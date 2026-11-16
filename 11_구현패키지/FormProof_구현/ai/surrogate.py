"""물리 AI (대리 모델): 형상 → 성능.  CNN(스칼라만) 과 FNO(스칼라 + 분포) 두 가지.

사용 (GPU 권장):
  python -m ai.surrogate --meta data/grid_meta.npz --data 'data/shards/*.npz' --model fno --out runs/fno.pt
출력: 체크포인트(.pt) + 검증 지표(.json). 지표: 스칼라별 평균 상대오차, 분포 상대 L2.
인터페이스(에이전트 · 잠재 탐색이 쓰는 것):  predict(occ_d) -> dict(scalars=(B,7) 원래 단위, fields=(B,2,nz,ny,nx) 또는 None)
"""
import argparse, json, time, numpy as np, torch, torch.nn as nn, torch.nn.functional as F
from .data import Grid, load_shards, LabelNorm, split, device, LAB_NAMES

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
    dev = device(); grid = Grid(a.meta); FLD = a.model in ('fno', 'pino'); D = load_shards(a.data, grid, fields=FLD)
    N = len(D['occ']); tr, te = split(N, seed=a.seed); norm = LabelNorm(D['lab'][tr]); Yn = norm.encode(D['lab'])
    cfg = dict(width=a.width, modes=tuple(a.modes)) if FLD else {}
    net = build(a.model, cfg).to(dev); coords = grid.coords(dev)
    if a.model == 'pino':   # 물리 손실: 엔진과 같은 열전도 FEM 연산자 (ai/pino.py)
        from .pino import ThermalResidual; TR = ThermalResidual(a.thermal_ops).to(dev); NN = (grid.nz + 1, grid.ny + 1, grid.nx + 1)
    opt = torch.optim.AdamW(net.parameters(), lr=a.lr, weight_decay=1e-4); sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, a.steps)
    occ = torch.as_tensor(D['occ']); Y = torch.as_tensor(Yn); w_lab = torch.tensor([0.] + [1.] * 6)   # 무게는 정확식이 있어 학습 제외
    if FLD:
        Tf = torch.as_tensor(D['T']).view(N, 1, grid.nz, grid.ny, grid.nx); Vf = torch.log1p(torch.as_tensor(D['vm'])).view(N, 1, grid.nz, grid.ny, grid.nx)
        tmask = torch.as_tensor(grid.thermal_region, dtype=torch.float32).view(1, 1, grid.nz, grid.ny, grid.nx)
        ts, vs = Tf[tr].std() + 1e-6, Vf[tr].std() + 1e-6
    rng = np.random.default_rng(a.seed); t0 = time.time(); log = []
    def evaluate(idx):
        net.eval(); P = []; FE = []; PR = []
        with torch.no_grad():
            for i in range(0, len(idx), a.bs):
                b = idx[i:i + a.bs]; g = grid.to_grid(occ[b].to(dev)); yn, fl = net(g, coords)
                if a.model == 'pino': PR.append(TR(g.flatten(1), net.forward_full(g, coords)[2].flatten(1) * ts).abs().mean(1).cpu())
                P.append(norm.decode_t(yn).cpu())
                if fl is not None:
                    tgt = torch.cat([Tf[b] / ts, Vf[b] / vs], 1).to(dev); m = torch.cat([tmask.to(dev).expand(len(b), -1, -1, -1, -1), g], 1)
                    FE.append((((fl - tgt) * m) ** 2).sum((2, 3, 4)).sqrt() / ((tgt * m) ** 2).sum((2, 3, 4)).sqrt().clamp_min(1e-6))
        net.train(); P = torch.cat(P).numpy(); T_ = D['lab'][idx]
        rel = np.abs(P / np.maximum(np.abs(T_), 1e-6) - 1).mean(0)
        r = {f'relerr_{n}': float(v) for n, v in zip(LAB_NAMES, rel) if n != 'mass_g'}
        if FE: fe = torch.cat(FE).mean(0).cpu().numpy(); r.update(field_relL2_T=float(fe[0]), field_relL2_vm=float(fe[1]))
        if PR: r['phys_residual_T'] = float(torch.cat(PR).mean())   # 열전도 잔차 평균 (°C, 정답이면 0)
        return r
    for it in range(a.steps):
        b = rng.choice(tr, min(a.bs, len(tr))); g = grid.to_grid(occ[b].to(dev))
        if a.model == 'pino': yn, fl, Tn = net.forward_full(g, coords)
        else: yn, fl = net(g, coords)
        loss = ((yn - Y[b].to(dev)) ** 2 * w_lab.to(dev)).mean()
        if fl is not None:
            tgt = torch.cat([Tf[b] / ts, Vf[b] / vs], 1).to(dev); m = torch.cat([tmask.to(dev).expand(len(b), -1, -1, -1, -1), g], 1)
            loss = loss + a.wfield * (((fl - tgt) * m) ** 2).sum() / m.sum()
        if a.model == 'pino' and a.wphys > 0:   # 물리 손실 (온도 정규화 단위). 처음 warm 스텝 동안 0 → wphys 로 키움
            res = TR(g.flatten(1), Tn.flatten(1) * ts) / ts; loss = loss + a.wphys * min(1.0, it / max(a.phys_warm, 1)) * (res ** 2).mean().float()
        opt.zero_grad(); loss.backward(); opt.step(); sch.step()
        if it % a.log_every == 0 or it == a.steps - 1:
            r = dict(it=it, loss=float(loss), t=round(time.time() - t0, 1), **evaluate(te)); log.append(r); print(json.dumps(r), flush=True)
    st = dict(kind=a.model, cfg=cfg, state=net.state_dict(), norm=norm.state(), field_scale=[float(ts), float(vs)] if FLD else None,
              n_train=len(tr), n_test=len(te), final=log[-1])
    torch.save(st, a.out); json.dump(dict(final=log[-1], log=log), open(a.out.replace('.pt', '.json'), 'w'), indent=1); print('saved', a.out)

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--meta', required=True); p.add_argument('--data', required=True)
    p.add_argument('--model', choices=['cnn', 'fno', 'pino'], default='fno'); p.add_argument('--out', required=True)
    p.add_argument('--steps', type=int, default=20000); p.add_argument('--bs', type=int, default=16); p.add_argument('--lr', type=float, default=1e-3)
    p.add_argument('--width', type=int, default=24); p.add_argument('--modes', type=int, nargs=3, default=[10, 6, 16]); p.add_argument('--wfield', type=float, default=1.0)
    p.add_argument('--thermal_ops', default='data/thermal_ops.npz'); p.add_argument('--wphys', type=float, default=0.1); p.add_argument('--phys_warm', type=int, default=2000)
    p.add_argument('--seed', type=int, default=0); p.add_argument('--log_every', type=int, default=500)
    train(p.parse_args())
