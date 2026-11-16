"""PINO (물리 정보 신경 연산자) = FNO 구조 + 물리 식 잔차 손실 (11-16 추가)

무엇이 FNO 와 다른가
  - FNO 는 정답(FEM 값)만 맞추도록 학습한다 (데이터 손실).
  - PINO 는 여기에 "예측한 온도장이 열전도 방정식을 만족하는가" 를 손실로 더한다 (물리 손실).
    물리 식은 엔진(engine/opt_int.py thermal_T)과 **같은 FEM 연산자** K(r) T = q 를 그대로 쓴다
    (MODE=thermops 로 저장한 data/thermal_ops.npz). 정답 온도에서 잔차가 0 인 것을 확인함(상대값 8e-14, 11-16).

구조
  - FNO 몸통은 그대로. 온도는 절점 격자(nz+1, ny+1, nx+1)에 직접 예측(전치 합성곱 2×2×2) → 요소 온도 = 8개 절점 평균
    (학습 데이터의 요소 온도도 8개 절점 평균이라 정의가 같음). 충격 응력 분포 · 스칼라 7개 머리는 FNO 와 같음.
  - 물리 손실 = 야코비 전처리 잔차  ‖D⁻¹(K(r) T − q)‖² (온도 단위, 열 영역 절점)  — 정답이면 0.

구조 PINO (11-16 추가, struct=True)
  - 정적 구조 4개 하중(충격 위아래 · 앞뒤, 터치 위 · 아래)의 절점 변위 u 를 직접 예측(머리 12채널 = 4 하중 × 3 방향).
  - 물리 손실 = 야코비 전처리 잔차 ‖D⁻¹(K(r) u − f)‖² — 엔진과 같은 hex8 요소 강성 KE · 같은 하중 f (MODE=structops).
    FEM 정답(float64)에서 잔차 상대값 1e-11 ~ 1e-12 확인(11-16). float32 로 저장한 정답만 넣어도 약 1 % 남음(강성 행렬의 상쇄)
    → 잔차는 float64 로 계산.
  - 정답 변위가 없는 형상(예: 이전 데이터)도 물리 손실로 학습에 참여(PINO 의 장점). 변위 데이터 손실은 정답 있는 형상만.

한계 (확인된 것)
  - 물리 식은 열과 정적 구조(충격 · 터치)만. 1차 진동수 · 흔들림은 데이터로만 배움(회귀) → f1 정확도가 좋아진다는 보장은 없음.
  - 열 해석은 받침판 + 폰만 계산하므로 열 물리 손실은 그 영역(요소 10,500개, 절점 12,768개)에만 걸림.
"""
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
from .surrogate import FNO3D

class PINO(FNO3D):
    def __init__(self, n_out=7, width=24, modes=(10, 6, 16), layers=4, struct=False):
        super().__init__(n_out=n_out, width=width, modes=modes, layers=layers, n_field=2)
        self.node_T = nn.Sequential(nn.ConvTranspose3d(width, 32, 2), nn.GELU(), nn.Conv3d(32, 1, 1))   # 요소 격자 → 절점 격자
        self.struct = struct
        if struct: self.node_U = nn.Sequential(nn.ConvTranspose3d(width, 48, 2), nn.GELU(), nn.Conv3d(48, 12, 1))   # 4 하중 × 3 방향 변위(정규화)
    def forward_full(self, g, coords):
        h = self.lift(torch.cat([g, coords.expand(g.shape[0], -1, -1, -1, -1)], 1))
        for s, p in zip(self.spec, self.pw): h = F.gelu(s(h) + p(h))
        y = self.head(torch.cat([h.mean((2, 3, 4)), h.amax((2, 3, 4))], 1))
        Tn = self.node_T(h)                                        # (B, 1, nz+1, ny+1, nx+1), 정규화된 온도
        Te = F.avg_pool3d(Tn, 2, stride=1)                         # 요소 온도 = 8개 절점 평균
        fld = torch.cat([Te, self.proj(h)[:, 1:2]], 1)             # (온도, 응력 log1p) — FNO 와 같은 순서
        if self.struct:
            Un = self.node_U(h); B = Un.shape[0]                     # (B, 12, nz+1, ny+1, nx+1)
            Un = Un.view(B, 4, 3, -1).transpose(2, 3).reshape(B, 4, -1)   # (B, 4, 3·nn) — 자유도 순서 3n + d (엔진과 같음)
            return y, fld, Tn, Un
        return y, fld, Tn
    def forward(self, g, coords):
        o = self.forward_full(g, coords); return o[0], o[1]

class ThermalResidual(nn.Module):
    """K(r) T − q (엔진 thermal_T 와 같은 식), 배치 · 미분 가능. r = 요소 점유(0~1), T = 절점 온도(물리 단위)."""
    def __init__(self, path):
        super().__init__(); d = np.load(path); L = lambda k, t=torch.long: torch.as_tensor(np.asarray(d[k]), dtype=t)
        for k in ('the', 'en_the', 'ptop', 'pbot', 'pfront', 'en_ptop', 'en_pbot', 'en_pfront', 'thn'): self.register_buffer(k, L(k))
        self.register_buffer('phone_the', L('phone_the', torch.bool))
        for k in ('KTh', 'MFq', 'qv'): self.register_buffer(k, L(k, torch.float64))
        self.c = {k: float(d[k]) for k in ('K_PH', 'K_AIR', 'K_PETG', 'H_RIDE', 'H_FRONT')}; self.nn_ = int(d['nn'])
    def _scatter(self, B, nodes, vals):
        y = torch.zeros(B, self.nn_, dtype=vals.dtype, device=vals.device)
        return y.scatter_add_(1, nodes.reshape(1, -1).expand(B, -1), vals.reshape(B, -1))
    def forward(self, r, T):
        """r (B, ne) 요소 점유, T (B, nn) 절점 온도 → 야코비 전처리 잔차 (B, len(thn)) [온도 단위]"""
        r = r.double(); T = T.double(); B = r.shape[0]; c = self.c
        ke = torch.where(self.phone_the, torch.full_like(r[:, self.the], c['K_PH']), c['K_AIR'] + r[:, self.the] ** 3 * (c['K_PETG'] - c['K_AIR']))
        y = self._scatter(B, self.en_the, ke[..., None] * (T[:, self.en_the] @ self.KTh.T))
        d = self._scatter(B, self.en_the, ke[..., None] * torch.diagonal(self.KTh)[None, None])
        for els, nodes, hv in ((self.ptop, self.en_ptop, c['H_RIDE'] * (1 - r[:, self.ptop])), (self.pbot, self.en_pbot, c['H_RIDE'] * r[:, self.pbot]),
                               (self.pfront, self.en_pfront, torch.full_like(r[:, self.pfront], c['H_FRONT']))):
            y = y + self._scatter(B, nodes, hv[..., None] * (T[:, nodes] @ self.MFq.T))
            d = d + self._scatter(B, nodes, hv[..., None] * torch.diagonal(self.MFq)[None, None])
        return ((y - self.qv[None]) / d.clamp_min(1e-30))[:, self.thn]

class StructResidual(nn.Module):
    """정적 구조 K(r) u − f (엔진 analyse 와 같은 hex8 KE · 하중), 재료 칸만 (학습 데이터 정답 = 재료 칸만 조립과 같음).
    r = (B, ne) 요소 점유(0/1, 고정 부품 포함), U = (B, 3·nn) 한 하중의 변위(물리 단위 mm) → 야코비 전처리 잔차 [mm] 와 마스크"""
    def __init__(self, path):
        super().__init__(); d = np.load(path)
        self.register_buffer('KE', torch.as_tensor(d['KE'], dtype=torch.float64)); self.register_buffer('edof', torch.as_tensor(d['edof'].astype(np.int64)))
        self.register_buffer('ae', torch.as_tensor(np.where(d['active'])[0])); self.register_buffer('F', torch.as_tensor(d['F'], dtype=torch.float64))
        self.register_buffer('fixed', torch.as_tensor(d['fixed'].astype(bool))); self.ndof = int(d['nn']) * 3
    def forward(self, r, U, case):
        r = r[:, self.ae].double(); U = U.double(); B = r.shape[0]; ed = self.edof[self.ae]                     # (Na, 24)
        ye = (U[:, ed] @ self.KE.T) * r[..., None]; de = torch.diagonal(self.KE)[None, None] * r[..., None]
        idx = ed.reshape(1, -1).expand(B, -1)
        y = torch.zeros(B, self.ndof, dtype=torch.float64, device=U.device).scatter_add_(1, idx, ye.reshape(B, -1))
        dg = torch.zeros_like(y).scatter_add_(1, idx, de.reshape(B, -1))
        m = (dg > 0) & ~self.fixed[None]
        res = torch.where(m, (y - self.F[case][None]) / dg.clamp_min(1e-30), torch.zeros_like(y))
        return res, m
