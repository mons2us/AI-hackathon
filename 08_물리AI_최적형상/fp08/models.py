"""모델 — DeepSDF(형상 ↔ z) 와 PINO(형상 → 변위장·진동수).

DeepSDF  : 자동 디코더. [z(32), x(3)] → 부호 거리. 그룹마다 1개.
PINO     : 3D FNO. 입력 = 절점 격자 위 (재료 밀도, 고정부, 강체, 지지점, 대칭면, 질량 지도, 좌표)
           출력 = 기본 하중별 변위장. 크기는 "모양(정규화) × 크기(로그 스케일 머리)"로 분리.
           하드 경계조건: 지지점·대칭면 조건은 출력에 마스크를 곱해서 정확히 0.
           물리 손실: 행렬 없이 요소 강성으로 K·u 를 계산 → 에너지 Π = ½uᵀKu − fᵀu (정답 없는 형상도 학습).
진동수 머리: 첫 모드 = 예측 정적 변위로 레일리 몫 f_R × 학습 보정비 c, 두 번째 모드 = 직접 회귀.
"""
import math
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from . import fem

PI2 = 2 * math.pi


# ============================================================================ DeepSDF
class DeepSDF(nn.Module):
    """width·depth: MLP 크기, nfreq: 좌표에 사인·코사인 특징(Fourier features) 개수(0이면 끔) — 11-14 비교 실험용"""

    def __init__(self, n_shapes, lo, hi, zdim=32, width=128, depth=4, nfreq=0):
        super().__init__()
        self.lat = nn.Embedding(n_shapes, zdim)
        nn.init.normal_(self.lat.weight, 0, 0.01)
        self.register_buffer('lo', torch.tensor(lo, dtype=torch.float32))
        self.register_buffer('hi', torch.tensor(hi, dtype=torch.float32))
        self.nfreq = nfreq
        layers, d = [], zdim + 3 + 6 * nfreq
        for i in range(depth):
            layers += [nn.Linear(d, width), nn.Softplus(beta=50)]
            d = width
        self.net = nn.Sequential(*layers, nn.Linear(d, 1))
        self.zdim = zdim
        self.cfg = dict(zdim=zdim, width=width, depth=depth, nfreq=nfreq)

    def norm(self, x):
        return 2 * (x - self.lo) / (self.hi - self.lo) - 1

    def encode(self, xn):
        if not self.nfreq:
            return xn
        f = (2.0 ** torch.arange(self.nfreq, device=xn.device, dtype=xn.dtype)) * math.pi   # 1, 2, 4, … 배 주파수
        a = xn[..., None] * f                                                           # (..., 3, nfreq)
        return torch.cat([xn, torch.sin(a).flatten(-2), torch.cos(a).flatten(-2)], -1)

    def forward(self, z, x):
        """z (B, zdim) 또는 (zdim,), x (B, N, 3) mm → (B, N) mm"""
        if z.dim() == 1:
            z = z[None]
        if x.dim() == 2:
            x = x[None].expand(z.shape[0], -1, -1)
        zz = z[:, None, :].expand(-1, x.shape[1], -1)
        scale = float((self.hi - self.lo).max()) / 2
        return self.net(torch.cat([zz, self.encode(self.norm(x))], -1))[..., 0] * scale


def load_sdf(ckpt, device='cpu'):
    """체크포인트에서 DeepSDF 복원 (크기 설정 포함)"""
    c = torch.load(ckpt, map_location=device, weights_only=False)
    m = DeepSDF(c['n'], c['lo'], c['hi'], **c.get('cfg', {})).to(device)
    m.load_state_dict(c['model']); m.eval()
    return m, c


# ============================================================================ 문제별 고정 텐서
class ProblemTensors:
    """FEM 격자 정보를 torch 버퍼로 (그룹마다 1개). 물리 손실·레일리 몫·입력 지도 생성에 사용."""

    def __init__(self, p, device='cpu'):
        g = p.grid
        self.p, self.g = p, g
        dv = device
        t = lambda a, dt=torch.float32: torch.as_tensor(np.asarray(a), dtype=dt, device=dv)
        self.edof = t(g.edof, torch.long)
        self.KE = t(p.KE, torch.float64)   # float32 는 강체 이동에서 에너지 오차 수 % → 물리 계산은 float64
        self.label = t(p.label, torch.long)
        self.design = self.label == 0
        self.me0 = float(p.me0)
        self.shape_n = (g.NX, g.NY, g.NZ)
        self.shape_e = (g.nx, g.ny, g.nz)
        nn_ = g.nn
        # 기본 하중 (단위)과 자유도 마스크 (기본 하중마다 bc 에 따라)
        B = p.basis(p.default_cond)
        self.basis_names = [b[0] for b in B]
        self.basis_bc = [b[1] for b in B]
        self.F = t(np.stack([b[2] for b in B]))                # (nb, 3nn)
        masks = []
        for _, bc, _ in B:
            m = np.zeros(3 * nn_, np.float32)
            m[p.free[bc]] = 1
            masks.append(m)
        self.free = t(np.stack(masks))                          # (nb, 3nn)
        # 입력 지도 (절점)
        def node_map(a):
            return t(np.asarray(a, np.float32).reshape(g.NZ, g.NY, g.NX).transpose(2, 1, 0))
        sup = np.zeros(nn_); sup[p.supports] = 1
        pl = np.zeros(nn_); pl[p.plane] = 1
        nm = p.node_mass(p.default_cond)
        if hasattr(p, 'load_nodes'):
            nm = np.zeros(nn_); nm[p.load_nodes] = 1
        xs = [(g.nxc - g.nxc.min()) / 100.0, (g.nyc - g.nyc.min()) / 100.0, (g.nzc - g.nzc.min()) / 100.0]
        self.static_maps = torch.stack([node_map(sup), node_map(pl), node_map(nm / (nm.max() + 1e-30))]
                                       + [node_map(x) for x in xs])          # (6, NX, NY, NZ)
        fixed_e = ((p.label == 1)).astype(np.float32)
        rigid_e = (p.label == 3).astype(np.float32)
        self.fixed_e = t(fixed_e); self.rigid_e = t(rigid_e)
        self.k_rigid = float(p.k_rigid)

    # 요소 (ne,) → (nx,ny,nz) 격자
    def e3(self, a):
        g = self.g
        return a.reshape(*a.shape[:-1], g.nz, g.ny, g.nx).transpose(-1, -3)

    def n_flat(self, a):
        """(..., NX, NY, NZ) → (..., nn) 절점 번호 순서"""
        return a.transpose(-1, -3).reshape(*a.shape[:-3], -1)

    def elem_to_node(self, e):
        """(B, ne) → (B, 1, NX, NY, NZ): 절점 주변 8칸 평균"""
        x = self.e3(e)[:, None]
        x = F.pad(x, (1, 1, 1, 1, 1, 1))
        return F.avg_pool3d(x, 2, stride=1)

    def full_occ(self, occ_design):
        """설계 칸 점유(0~1) + 라벨 덮어쓰기(설계 결정: 빈 곳 0, 고정·강체 1)"""
        d = self.design.float()
        return occ_design * d + self.fixed_e + self.rigid_e

    def kscale(self, occ_design, p=3.0, emin=1e-9):
        d = self.design.float()
        return (emin + (1 - emin) * occ_design.clamp(0, 1) ** p) * d + self.fixed_e + self.k_rigid * self.rigid_e

    def inputs(self, occ_design, extra=None):
        """(B, ne) → (B, Cin, NX, NY, NZ)"""
        B = occ_design.shape[0]
        maps = [self.elem_to_node(self.full_occ(occ_design)), self.elem_to_node(self.fixed_e.expand(B, -1)),
                self.elem_to_node(self.rigid_e.expand(B, -1)), self.static_maps[None].expand(B, -1, -1, -1, -1)]
        if extra is not None:
            maps.append(extra)
        return torch.cat(maps, 1)

    # ---- 물리
    def Ku(self, ks, u):
        """ks (B, ne), u (B, 3nn) → K·u (B, 3nn) 행렬 없이"""
        dt = u.dtype
        u = u.double()
        ue = u[:, self.edof]                                      # (B, ne, 24)
        fe = torch.einsum('bei,ij->bej', ue, self.KE) * ks.double()[..., None]
        return torch.zeros_like(u).index_add_(1, self.edof.reshape(-1), fe.reshape(u.shape[0], -1))  # float64 반환

    def energy(self, ks, u, f):
        """Π = ½uᵀKu − fᵀu, 정규화: |fᵀu| 로 나눔 (정답이면 −0.5)"""
        Ku = self.Ku(ks, u)
        u = u.double(); f = f.double()
        uKu = (u * Ku).sum(1)
        fu = (f * u).sum(1)
        return ((0.5 * uKu - fu) / (fu.detach().abs() + 1e-30)).float(), Ku

    def residual(self, ks, u, f, free):
        """야코비(대각) 전처리 잔차 — ‖D⁻¹(Ku − f)‖ / ‖u‖ (자유도만). 정답이면 0, 변위 단위라 크기가 안정적.
        에너지 Π 는 무작위 출력에서 값이 수천 배로 커져 데이터 손실을 덮어버려서(리허설 실측) 이것을 기본 물리 손실로 씀."""
        Ku = self.Ku(ks, u)
        dg = torch.zeros_like(Ku).index_add_(1, self.edof.reshape(-1),
                                              (ks.double()[..., None] * torch.diagonal(self.KE)[None, None]).reshape(ks.shape[0], -1))
        solid = (dg > 1e-6 * dg.amax(1, keepdim=True)).double()     # 빈 칸만 닿은 절점(EMIN 행)은 제외
        r = (Ku - f.double()) / (dg + 1e-30) * free * solid
        shape_err = r.norm(dim=1) / (u.double().norm(dim=1) + 1e-30)
        # 크기 오차: 정답이면 uᵀKu = fᵀu → log 비 = 0 (야코비 잔차는 크기 오차에 둔감해서 추가)
        ud = u.double()
        scale_err = torch.log(((ud * Ku).sum(1).clamp_min(1e-30)) / ((f.double() * ud).sum(1).abs() + 1e-30)).abs()
        return (shape_err + scale_err).float()

    def mass_nodes(self, occ_design, node_mass):
        d = self.design.float()
        em = (occ_design * d + self.fixed_e) * self.me0
        m = torch.zeros(occ_design.shape[0], self.g.nn, device=em.device)
        m.index_add_(1, torch.as_tensor(self.g.en, device=em.device).reshape(-1),
                     (em[..., None] / 8).expand(-1, -1, 8).reshape(em.shape[0], -1))
        return m + node_mass


# ============================================================================ FNO
class SpectralConv3d(nn.Module):
    def __init__(self, cin, cout, modes):
        super().__init__()
        self.m = modes
        s = 1 / (cin * cout)
        self.w = nn.ParameterList([nn.Parameter(s * torch.randn(cin, cout, *modes, dtype=torch.cfloat)) for _ in range(4)])

    def forward(self, x):
        B, C, X, Y, Z = x.shape
        m1, m2, m3 = min(self.m[0], X // 2), min(self.m[1], Y // 2), min(self.m[2], Z // 2 + 1)
        xf = torch.fft.rfftn(x, dim=(-3, -2, -1))
        out = torch.zeros(B, self.w[0].shape[1], X, Y, Z // 2 + 1, dtype=torch.cfloat, device=x.device)
        mul = lambda a, w: torch.einsum('bixyz,ioxyz->boxyz', a, w[:, :, :a.shape[2], :a.shape[3], :a.shape[4]])
        out[:, :, :m1, :m2, :m3] = mul(xf[:, :, :m1, :m2, :m3], self.w[0])
        out[:, :, -m1:, :m2, :m3] = mul(xf[:, :, -m1:, :m2, :m3], self.w[1])
        out[:, :, :m1, -m2:, :m3] = mul(xf[:, :, :m1, -m2:, :m3], self.w[2])
        out[:, :, -m1:, -m2:, :m3] = mul(xf[:, :, -m1:, -m2:, :m3], self.w[3])
        return torch.fft.irfftn(out, s=(X, Y, Z), dim=(-3, -2, -1))


class FNO3d(nn.Module):
    def __init__(self, cin, cout, width=24, layers=4, modes=(8, 8, 8), pad=4):
        super().__init__()
        self.pad = pad
        self.lift = nn.Conv3d(cin, width, 1)
        self.spec = nn.ModuleList([SpectralConv3d(width, width, modes) for _ in range(layers)])
        self.loc = nn.ModuleList([nn.Conv3d(width, width, 3, padding=1) for _ in range(layers)])
        self.proj = nn.Sequential(nn.Conv3d(width, 64, 1), nn.GELU(), nn.Conv3d(64, cout, 1))

    def forward(self, x, return_feat=False):
        X, Y, Z = x.shape[-3:]
        h = self.lift(x)
        p = self.pad
        h = F.pad(h, (0, p, 0, p, 0, p))
        for i, (s, l) in enumerate(zip(self.spec, self.loc)):
            h2 = s(h) + l(h)
            h = F.gelu(h2) if i < len(self.spec) - 1 else h2
        h = h[..., :X, :Y, :Z]
        out = self.proj(h)
        return (out, h) if return_feat else out


class PINO(nn.Module):
    """제품마다 1개. 그룹(격자 크기)이 달라도 같은 가중치."""

    def __init__(self, n_basis, n_freq_pairs=0, width=24, layers=4, modes=(8, 8, 8), cin=9):
        super().__init__()
        self.nb = n_basis
        self.fno = FNO3d(cin, 3 * n_basis, width, layers, modes)
        self.scale_head = nn.Sequential(nn.Linear(3 * width + 2, 64), nn.GELU(), nn.Linear(64, n_basis))
        self.nf = n_freq_pairs                    # 진동 모드 쌍(S, A)마다 [첫 모드 보정비, 두 번째 모드 비율]
        if n_freq_pairs:
            self.freq_head = nn.Sequential(nn.Linear(2 * width + 2 + n_freq_pairs, 64), nn.GELU(),
                                           nn.Linear(64, 2 * n_freq_pairs))
        self.register_buffer('u_ref', torch.ones(n_basis))   # 크기 기준 (학습 데이터 중앙값)
        self.freq_mode = 'rayleigh'                            # 'direct' = 레일리 없이 직접 회귀 (비교 실험)

    def forward(self, pt, occ_design, node_mass=None, want_freq=True):
        x = pt.inputs(occ_design)
        y, feat = self.fno(x, return_feat=True)
        B = y.shape[0]
        vf = occ_design[:, pt.design].mean(1, keepdim=True)
        wl = pt.static_maps[2][None, None]                                 # 하중(질량) 절점 지도
        at_load = (feat * wl).sum((2, 3, 4)) / (wl.sum() + 1e-12)         # 하중점 특징 = 처짐 크기와 직결
        pooled = torch.cat([feat.mean((2, 3, 4)), feat.amax((2, 3, 4)), vf, torch.log(vf + 1e-3)], 1)
        logs = self.scale_head(torch.cat([pooled, at_load], 1))                                    # (B, nb) 크기(로그)
        shape = y.reshape(B, self.nb, 3, *y.shape[2:])                   # (B, nb, 3, NX, NY, NZ)
        u = pt.n_flat(shape).permute(0, 1, 3, 2).reshape(B, self.nb, -1)  # (B, nb, 3nn) 절점·xyz 순
        # 재료가 하나도 안 닿은 절점은 FEM 에서 변위 0 (정답의 약 87%) → 마스크로 강제 (리허설: 학습 속도 개선 목적)
        solid = (8 * pt.n_flat(pt.elem_to_node(pt.full_occ(occ_design))[:, 0])).clamp(0, 1)   # (B, nn)
        u = u * solid.repeat_interleave(3, dim=1)[:, None]
        un = u * pt.free[None]
        un = un / (un.pow(2).mean(-1, keepdim=True).sqrt() + 1e-12)        # 모양 (rms 1)
        u = un * (torch.exp(logs) * self.u_ref)[..., None]
        out = dict(u=u, un=un, logs=logs)
        if self.nf and want_freq and node_mass is not None:
            out.update(self.freq(pt, occ_design, node_mass, u, pooled))
        return out

    def freq(self, pt, occ_design, node_mass, u, pooled):
        """첫 모드 = 레일리 몫 × 보정비 c,  두 번째 = 첫 모드 × 비율 (둘 다 학습)."""
        if self.freq_mode == 'direct':
            B = pooled.shape[0]
            h = self.freq_head(torch.cat([pooled, torch.zeros(B, self.nf, device=pooled.device)], 1))
            f1 = torch.exp(h[:, :self.nf] + 4.0)
            return dict(fR=f1.detach(), c=torch.ones_like(f1), f1=f1, f2=f1 * (1.0 + F.softplus(h[:, self.nf:] + 1.0)))
        m = pt.mass_nodes(occ_design, node_mass)                 # (B, nn)
        ks = pt.kscale(occ_design)
        fR = []
        for j in range(self.nf):                                  # 기본 하중 j = 모드 쌍 j 의 정적 변위 (예: 위아래 → S)
            uj = u[:, j]
            Ku = pt.Ku(ks, uj)
            uKu = (uj.double() * Ku).sum(1)
            uMu = (uj.double().reshape(uj.shape[0], -1, 3).pow(2).sum(-1) * m.double()).sum(1)
            fR.append((torch.sqrt(uKu.clamp_min(1e-30) / uMu.clamp_min(1e-30)) / PI2).float())
        fR = torch.stack(fR, 1)                                    # (B, nf)
        h = self.freq_head(torch.cat([pooled, torch.log(fR + 1)], 1))
        c = 0.5 + 0.5 * torch.sigmoid(h[:, :self.nf] + 2.0)        # 보정비 0.5~1 (레일리는 항상 위쪽 값)
        r2 = 1.0 + F.softplus(h[:, self.nf:] + 1.0)                 # 두 번째 / 첫 번째 > 1
        f1 = fR * c
        return dict(fR=fR, c=c, f1=f1, f2=f1 * r2)
