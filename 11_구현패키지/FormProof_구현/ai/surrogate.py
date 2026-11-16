"""물리 AI (대리 모델): 형상 → 성능.  CNN(스칼라만) 과 FNO(스칼라 + 분포) 두 가지.

사용 (GPU 권장):
  python -m ai.surrogate --meta data/grid_meta.npz --data 'data/shards/*.npz' --model fno --out runs/fno.pt
출력: 체크포인트(.pt) + 검증 지표(.json). 지표: 스칼라별 평균 상대오차, 분포 상대 L2.
인터페이스(에이전트 · 잠재 탐색이 쓰는 것):  predict(occ_d) -> dict(scalars=(B,7) 원래 단위, fields=(B,2,nz,ny,nx) 또는 None)
"""
import argparse, json, time, numpy as np, torch, torch.nn as nn, torch.nn.functional as F
from .data import Grid, load_shards, LabelNorm, split, device, LAB_NAMES, LOG_LABS, EXT_NAMES

class CNN3D(nn.Module):
    """해커톤에서 쓴 구조와 같은 계열: 3D 합성곱 4층(스트라이드 2) → 평균·최대 풀링 → MLP."""
    def __init__(self, n_out=7, ch=(16, 32, 64, 96)):
        super().__init__(); L = []; c0 = 1
        for c in ch: L += [nn.Conv3d(c0, c, 3, 2, 1), nn.GELU()]; c0 = c
        self.f = nn.Sequential(*L); self.head = nn.Sequential(nn.Linear(2 * c0, 128), nn.GELU(), nn.Linear(128, n_out))
    def forward(self, g, coords=None):
        h = self.f(g); h = torch.cat([h.mean((2, 3, 4)), h.amax((2, 3, 4))], 1); return self.head(h), None

class SpectralConv3d(nn.Module):
    def __init__(self, cin, cout, m1, m2, m3):
        super().__init__(); self.m = (m1, m2, m3); s = 1 / (cin * cout)
        self.w = nn.ParameterList([nn.Parameter(s * torch.randn(cin, cout, m1, m2, m3, dtype=torch.cfloat)) for _ in range(4)])
    def forward(self, x):
        B, C, D, H, W = x.shape; m1, m2, m3 = self.m
        X = torch.fft.rfftn(x, dim=(-3, -2, -1)); out = torch.zeros(B, self.w[0].shape[1], D, H, W // 2 + 1, dtype=torch.cfloat, device=x.device)
        mul = lambda a, w: torch.einsum('bixyz,ioxyz->boxyz', a, w)
        out[:, :, :m1, :m2, :m3] = mul(X[:, :, :m1, :m2, :m3], self.w[0]); out[:, :, -m1:, :m2, :m3] = mul(X[:, :, -m1:, :m2, :m3], self.w[1])
        out[:, :, :m1, -m2:, :m3] = mul(X[:, :, :m1, -m2:, :m3], self.w[2]); out[:, :, -m1:, -m2:, :m3] = mul(X[:, :, -m1:, -m2:, :m3], self.w[3])
        return torch.fft.irfftn(out, s=(D, H, W), dim=(-3, -2, -1))

class FNO3D(nn.Module):
    """푸리에 신경 연산자: 입력 = 점유 + 좌표 3채널, 출력 = 분포 2채널(온도 상승, 충격 응력 log1p) + 스칼라 7개."""
    def __init__(self, n_out=7, width=24, modes=(10, 6, 16), layers=4, n_field=2):
        super().__init__(); self.lift = nn.Conv3d(4, width, 1)
        self.spec = nn.ModuleList([SpectralConv3d(width, width, *modes) for _ in range(layers)])
        self.pw = nn.ModuleList([nn.Conv3d(width, width, 1) for _ in range(layers)])
        self.proj = nn.Sequential(nn.Conv3d(width, 64, 1), nn.GELU(), nn.Conv3d(64, n_field, 1))
        self.head = nn.Sequential(nn.Linear(2 * width, 128), nn.GELU(), nn.Linear(128, n_out))
    def forward(self, g, coords):
        h = self.lift(torch.cat([g, coords.expand(g.shape[0], -1, -1, -1, -1)], 1))
        for s, p in zip(self.spec, self.pw): h = F.gelu(s(h) + p(h))
        return self.head(torch.cat([h.mean((2, 3, 4)), h.amax((2, 3, 4))], 1)), self.proj(h)

def build(kind, cfg):
    if kind == 'pino':
        from .pino import PINO; return PINO(**cfg)
    return FNO3D(**cfg) if kind == 'fno' else CNN3D(**cfg)

class Surrogate:
    """학습된 물리 AI 를 감싼 공통 인터페이스. 모델 종류(CNN/FNO/이후 GINO)를 바꿔도 호출 방식은 같다."""
    def __init__(self, ckpt, grid, dev=None):
        st = torch.load(ckpt, map_location='cpu', weights_only=False); self.kind = st['kind']; self.grid = grid; self.dev = dev or device()
        self.net = build(self.kind, st['cfg']).to(self.dev); self.net.load_state_dict(st['state']); self.net.eval()
        self.norm = LabelNorm(state=st['norm']); self.coords = grid.coords(self.dev)
    def predict(self, occ_d):
        """occ_d: (B, nd) torch(미분 가능) 또는 numpy. 반환 scalars 는 원래 단위 (mass 는 정확식으로 대체)."""
        occ_d = torch.as_tensor(occ_d, dtype=torch.float32, device=self.dev)
        yn, fld = self.net(self.grid.to_grid(occ_d), self.coords); y = self.norm.decode_t(yn)
        y = torch.cat([self.grid.mass_g(occ_d)[:, None], y[:, 1:]], 1)
        return dict(scalars=y, fields=fld)

def train(a):
    """물리 AI 학습. 추가(11-16): --ext (흔들림 · 층간 등 11개도 출력, 회귀), --model pino [--struct] (열 / 구조 물리 손실)"""
    dev = device(); grid = Grid(a.meta); FLD = a.model in ('fno', 'pino'); ST = a.model == 'pino' and a.struct
    D = load_shards(a.data, grid, fields=FLD, ext=a.ext, disp=a.disp_max if ST else 0)
    names = [n for n in LAB_NAMES] + (EXT_NAMES if a.ext else [])
    LAB = np.concatenate([D['lab'], D['ext']], 1) if a.ext else D['lab']; nout = LAB.shape[1]
    log_idx = list(LOG_LABS) + (list(range(len(LAB_NAMES), nout)) if a.ext else [])
    N = len(D['occ']); tr, te = split(N, seed=a.seed); norm = LabelNorm(LAB[tr], log_idx=log_idx); Yn = norm.encode(LAB)
    fin = torch.as_tensor(np.isfinite(Yn)); Y = torch.as_tensor(np.nan_to_num(Yn))
    cfg = dict(n_out=nout)
    if FLD: cfg.update(width=a.width, modes=tuple(a.modes))
    if ST: cfg['struct'] = True
    net = build(a.model, cfg).to(dev); coords = grid.coords(dev)
    if a.model == 'pino':   # 물리 손실: 엔진과 같은 FEM 연산자 (ai/pino.py)
        from .pino import ThermalResidual; TR = ThermalResidual(a.thermal_ops).to(dev)
    if ST:
        from .pino import StructResidual; SR = StructResidual(a.struct_ops).to(dev)
        has_u = np.full(N, -1); has_u[D.get('U_idx', np.zeros(0, int))] = np.arange(len(D.get('U_idx', [])))
        Ut = torch.as_tensor(D['U']) if 'U' in D else None; Usc = torch.as_tensor(D['U_scale']) if 'U' in D else None
        us = torch.as_tensor(np.median(D['U_scale'], 0) if 'U' in D else np.ones(4), dtype=torch.float32)   # 하중별 변위 크기 (정규화)
        print(json.dumps(dict(struct=True, n_with_U=int((has_u >= 0).sum()), n_all=N, u_scale_mm=[round(float(v), 5) for v in us])), flush=True)
    opt = torch.optim.AdamW(net.parameters(), lr=a.lr, weight_decay=1e-4); sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, a.steps)
    occ = torch.as_tensor(D['occ']); w_lab = torch.tensor([0.] + [1.] * 6 + [a.wext] * (nout - 7))   # 무게는 정확식이 있어 학습 제외
    if FLD:
        Tf = torch.as_tensor(D['T']).view(N, 1, grid.nz, grid.ny, grid.nx); Vf = torch.log1p(torch.as_tensor(D['vm'])).view(N, 1, grid.nz, grid.ny, grid.nx)
        tmask = torch.as_tensor(grid.thermal_region, dtype=torch.float32).view(1, 1, grid.nz, grid.ny, grid.nx)
        ts, vs = Tf[tr].std() + 1e-6, Vf[tr].std() + 1e-6
    def u_true(b):   # 정답 변위 (B, 4, 3nn) 물리 단위, 없는 형상은 None
        k = has_u[b]; ok = k >= 0
        if not ok.any(): return None, ok
        u = Ut[k[ok]].float().view(int(ok.sum()), 4, 3, -1).transpose(2, 3).reshape(int(ok.sum()), 4, -1) * Usc[k[ok]][..., None]
        return u, ok
    def struct_losses(g, Un, b):   # (데이터 손실, 물리 손실, 잔차 크기) — 물리 손실은 모든 형상, 데이터 손실은 정답 있는 형상만
        U = Un * us.to(Un.device)[None, :, None]; r = g.flatten(1); lp = 0.; rr = []
        for c in range(4):
            res, m = SR(r, U[:, c], c); lp = lp + ((res / us[c]) ** 2).sum() / m.sum().clamp_min(1); rr.append((res.abs().sum(1) / m.sum(1).clamp_min(1)).float())
        ut, ok = u_true(b); ld = torch.zeros((), device=Un.device)
        if ut is not None:
            ut = ut.to(Un.device); pu = U[torch.as_tensor(ok, device=Un.device)]
            ld = (((pu - ut) ** 2).sum(-1) / (ut ** 2).sum(-1).clamp_min(1e-30)).mean()
        return ld, lp / 4, torch.stack(rr, 1)
    rng = np.random.default_rng(a.seed); t0 = time.time(); log = []
    def evaluate(idx):
        net.eval(); P = []; FE = []; PR = []; SRr = []; UE = []
        with torch.no_grad():
            for i in range(0, len(idx), a.bs):
                b = idx[i:i + a.bs]; g = grid.to_grid(occ[b].to(dev)); o = net.forward_full(g, coords) if a.model == 'pino' else net(g, coords)
                yn, fl = o[0], o[1]
                if a.model == 'pino': PR.append(TR(g.flatten(1), o[2].flatten(1) * ts).abs().mean(1).cpu())
                if ST:
                    ld, _, rr = struct_losses(g, o[3], b); SRr.append(rr.cpu())
                    if has_u[b].max() >= 0: UE.append(float(ld))
                P.append(norm.decode_t(yn).cpu())
                if fl is not None:
                    tgt = torch.cat([Tf[b] / ts, Vf[b] / vs], 1).to(dev); m = torch.cat([tmask.to(dev).expand(len(b), -1, -1, -1, -1), g], 1)
                    FE.append((((fl - tgt) * m) ** 2).sum((2, 3, 4)).sqrt() / ((tgt * m) ** 2).sum((2, 3, 4)).sqrt().clamp_min(1e-6))
        net.train(); P = torch.cat(P).numpy(); T_ = LAB[idx]
        rel = np.nanmean(np.abs(P / np.maximum(np.abs(T_), 1e-6) - 1), 0)
        r = {f'relerr_{n}': float(v) for n, v in zip(names, rel) if n != 'mass_g'}
        if FE: fe = torch.cat(FE).mean(0).cpu().numpy(); r.update(field_relL2_T=float(fe[0]), field_relL2_vm=float(fe[1]))
        if PR: r['phys_residual_T'] = float(torch.cat(PR).mean())   # 열전도 잔차 평균 (°C, 정답이면 0)
        if SRr: r['phys_residual_u_mm'] = [float(v) for v in torch.cat(SRr).mean(0)]   # 구조 잔차 평균 (하중 4개, mm)
        if UE: r['disp_relL2sq'] = float(np.mean(UE))   # 변위 상대 오차 제곱 (정답 있는 형상)
        return r
    for it in range(a.steps):
        b = rng.choice(tr, min(a.bs, len(tr))); g = grid.to_grid(occ[b].to(dev))
        o = net.forward_full(g, coords) if a.model == 'pino' else net(g, coords); yn, fl = o[0], o[1]
        fb = fin[b].to(dev); loss = (((yn - Y[b].to(dev)) ** 2) * w_lab.to(dev) * fb).sum() / fb.sum().clamp_min(1)
        if fl is not None:
            tgt = torch.cat([Tf[b] / ts, Vf[b] / vs], 1).to(dev); m = torch.cat([tmask.to(dev).expand(len(b), -1, -1, -1, -1), g], 1)
            loss = loss + a.wfield * (((fl - tgt) * m) ** 2).sum() / m.sum()
        ramp = min(1.0, it / max(a.phys_warm, 1))
        if a.model == 'pino' and a.wphys > 0:   # 열 물리 손실 (온도 정규화 단위). 처음 warm 스텝 동안 0 → wphys 로 키움
            res = TR(g.flatten(1), o[2].flatten(1) * ts) / ts; loss = loss + a.wphys * ramp * (res ** 2).mean().float()
        if ST:   # 구조: 변위 데이터 손실 + 물리 손실
            ld, lp, _ = struct_losses(g, o[3], b); loss = loss + a.wdisp * ld + a.wstruct * ramp * lp.float()
        opt.zero_grad(); loss.backward(); opt.step(); sch.step()
        if it % a.log_every == 0 or it == a.steps - 1:
            r = dict(it=it, loss=float(loss.detach()), t=round(time.time() - t0, 1), **evaluate(te)); log.append(r); print(json.dumps(r), flush=True)
    st = dict(kind=a.model, cfg=cfg, state=net.state_dict(), norm=norm.state(), field_scale=[float(ts), float(vs)] if FLD else None,
              names=names, u_scale=[float(v) for v in us] if ST else None, n_train=len(tr), n_test=len(te), final=log[-1])
    torch.save(st, a.out); json.dump(dict(final=log[-1], log=log), open(a.out.replace('.pt', '.json'), 'w'), indent=1); print('saved', a.out)

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--meta', required=True); p.add_argument('--data', required=True)
    p.add_argument('--model', choices=['cnn', 'fno', 'pino'], default='fno'); p.add_argument('--out', required=True)
    p.add_argument('--steps', type=int, default=20000); p.add_argument('--bs', type=int, default=16); p.add_argument('--lr', type=float, default=1e-3)
    p.add_argument('--width', type=int, default=24); p.add_argument('--modes', type=int, nargs=3, default=[10, 6, 16]); p.add_argument('--wfield', type=float, default=1.0)
    p.add_argument('--thermal_ops', default='data/thermal_ops.npz'); p.add_argument('--wphys', type=float, default=0.1); p.add_argument('--phys_warm', type=int, default=2000)
    p.add_argument('--ext', action='store_true', help='흔들림 · 층간 등 추가값 11개도 학습 (lab_ext)'); p.add_argument('--wext', type=float, default=1.0)
    p.add_argument('--struct', action='store_true', help='pino: 정적 구조(충격 · 터치) 변위 머리 + 구조 물리 손실'); p.add_argument('--struct_ops', default='data/struct_ops.npz')
    p.add_argument('--wstruct', type=float, default=0.1); p.add_argument('--wdisp', type=float, default=1.0); p.add_argument('--disp_max', type=int, default=2000, help='변위 정답을 읽을 최대 형상 수 (메모리)')
    p.add_argument('--seed', type=int, default=0); p.add_argument('--log_every', type=int, default=500)
    train(p.parse_args())
