"""형상 AI: DeepSDF 방식 auto-decoder (잠재 벡터 z + 좌표 → 점유 확률).

  - 형상마다 잠재 벡터 z(기본 32차원)를 두고, 디코더와 z 를 함께 학습한다 (DeepSDF, Park et al. 2019 방식).
  - SDF 대신 2 mm 격자 점유(0/1)를 목표로 한다 → 손실은 BCE.
  - 학습 데이터 = 생성기 형상 + 위상 최적화 기록(스냅샷). 생성기만으로는 최종 구조를 표현하지 못한다(IoU 0.14).

사용:
  python -m ai.deepsdf train --meta data/grid_meta.npz --data 'data/shards/*.npz' --out runs/sdf.pt
  python -m ai.deepsdf fit   --meta data/grid_meta.npz --ckpt runs/sdf.pt --target data/reference/rbin_int35f95g2.npy
     → 처음 보는 형상에 z 를 맞춰 복원 IoU 를 잰다. 통과 기준: 최종 구조 IoU ≥ 0.8
인터페이스: ShapeAI.decode(z) -> (B, nd) 점유 확률 (미분 가능)
"""
import argparse, json, time, numpy as np, torch, torch.nn as nn, torch.nn.functional as F
from .data import Grid, load_shards, device

def penc(p, nf):
    f = (2.0 ** torch.arange(nf, device=p.device)) * np.pi; a = p[..., None] * f
    return torch.cat([p, torch.sin(a).flatten(-2), torch.cos(a).flatten(-2)], -1)

class Decoder(nn.Module):
    """8층 MLP, 4층에서 입력을 다시 붙이는 skip (DeepSDF 원 구조)."""
    def __init__(self, ld=32, nf=6, hid=256):
        super().__init__(); self.ld, self.nf = ld, nf; din = ld + 3 + 6 * nf
        self.l1 = nn.ModuleList([nn.Linear(din, hid)] + [nn.Linear(hid, hid) for _ in range(3)])
        self.l2 = nn.ModuleList([nn.Linear(hid + din, hid)] + [nn.Linear(hid, hid) for _ in range(2)]); self.out = nn.Linear(hid, 1)
    def forward(self, z, p):   # z (B, ld), p (M, 3) → logits (B, M)
        B, M = z.shape[0], p.shape[0]; x = torch.cat([z[:, None].expand(B, M, -1), penc(p, self.nf)[None].expand(B, M, -1)], -1); h = x
        for l in self.l1: h = F.softplus(l(h), beta=100)
        h = torch.cat([h, x], -1)
        for l in self.l2: h = F.softplus(l(h), beta=100)
        return self.out(h)[..., 0]

class ShapeAI:
    def __init__(self, ckpt, grid, dev=None):
        st = torch.load(ckpt, map_location='cpu', weights_only=False); self.dev = dev or device(); self.grid = grid
        self.dec = Decoder(**st['cfg']).to(self.dev); self.dec.load_state_dict(st['state']); self.dec.eval()
        self.Z = torch.as_tensor(st['z']); self.names = st.get('names'); self.P = torch.as_tensor(grid.pts, device=self.dev)
    def decode(self, z, sharp=1.0, chunk=20000):
        z = torch.as_tensor(z, dtype=torch.float32, device=self.dev); z = z[None] if z.dim() == 1 else z
        return torch.cat([torch.sigmoid(sharp * self.dec(z, self.P[i:i + chunk])) for i in range(0, len(self.P), chunk)], 1)

def iou(a, b): a, b = a > 0.5, b > 0.5; return float((a & b).sum() / max((a | b).sum(), 1))

def train(a):
    dev = device(); grid = Grid(a.meta); D = load_shards(a.data, grid, fields=False); occ = torch.as_tensor(D['occ']); N = len(occ)
    dec = Decoder(a.ld, a.nf, a.hid).to(dev); Z = nn.Embedding(N, a.ld).to(dev); nn.init.normal_(Z.weight, 0, 0.01)
    opt = torch.optim.Adam([{'params': dec.parameters(), 'lr': a.lr}, {'params': Z.parameters(), 'lr': a.lr_z}]); sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, a.steps)
    P = torch.as_tensor(grid.pts, device=dev); rng = np.random.default_rng(0); t0 = time.time()
    for it in range(a.steps):
        idx = rng.integers(0, N, a.bs); y = occ[idx].to(dev)
        # 점 샘플: 재료 점과 빈 점을 반반 (얇은 부재가 사라지지 않게)
        pos = torch.multinomial(y + 1e-6, a.npts // 2, replacement=True); neg = torch.multinomial((1 - y) + 1e-6, a.npts // 2, replacement=True)
        pidx = torch.cat([pos, neg], 1); yt = torch.gather(y, 1, pidx)
        z = Z(torch.as_tensor(idx, device=dev)); lg = torch.stack([dec(z[b:b + 1], P[pidx[b]])[0] for b in range(len(idx))])
        loss = F.binary_cross_entropy_with_logits(lg, yt) + a.wz * (z ** 2).mean()
        opt.zero_grad(); loss.backward(); opt.step(); sch.step()
        if it and it % 1000 == 0:   # 중간 저장 (실행 시간 제한 · 중단 대비)
            torch.save(dict(cfg=dict(ld=a.ld, nf=a.nf, hid=a.hid), state=dec.state_dict(), z=Z.weight.detach().cpu().numpy(), names=list(D['names'])), a.out)
        if it % a.log_every == 0 or it == a.steps - 1:
            with torch.no_grad():
                k = rng.choice(N, min(16, N), replace=False); pr = torch.cat([torch.sigmoid(dec(Z(torch.as_tensor(k, device=dev)), P[i:i + 20000])) for i in range(0, len(P), 20000)], 1).cpu()
                mi = float(np.mean([iou(pr[j].numpy(), occ[k[j]].numpy()) for j in range(len(k))]))
            print(json.dumps(dict(it=it, loss=float(loss), train_IoU=round(mi, 3), t=round(time.time() - t0, 1))), flush=True)
    torch.save(dict(cfg=dict(ld=a.ld, nf=a.nf, hid=a.hid), state=dec.state_dict(), z=Z.weight.detach().cpu().numpy(), names=list(D['names'])), a.out); print('saved', a.out)

def fit(a):
    """처음 보는 형상에 z 만 맞춘다 (디코더 고정). 표현력 확인용."""
    grid = Grid(a.meta); S = ShapeAI(a.ckpt, grid); r = np.load(a.target).ravel(); tgt = torch.as_tensor((r[grid.didx] > 0.5).astype(np.float32), device=S.dev)
    z = S.Z.mean(0, keepdim=True).clone().to(S.dev).requires_grad_(True); opt = torch.optim.Adam([z], lr=a.lr)
    for it in range(a.steps):
        idx = torch.randint(0, grid.nd, (a.npts,), device=S.dev); lg = S.dec(z, S.P[idx])[0]
        loss = F.binary_cross_entropy_with_logits(lg, tgt[idx]) + 1e-4 * (z ** 2).mean(); opt.zero_grad(); loss.backward(); opt.step()
    with torch.no_grad(): pr = S.decode(z)[0].cpu().numpy()
    res = dict(target=a.target, IoU=iou(pr, tgt.cpu().numpy()), pass_criterion=0.8); res['pass'] = res['IoU'] >= 0.8
    print(json.dumps(res)); np.save(a.target.replace('.npy', '_sdf_recon.npy') if not a.save else a.save, pr)

if __name__ == '__main__':
    p = argparse.ArgumentParser(); sp = p.add_subparsers(dest='cmd', required=True)
    t = sp.add_parser('train'); t.add_argument('--meta', required=True); t.add_argument('--data', required=True); t.add_argument('--out', required=True)
    t.add_argument('--ld', type=int, default=32); t.add_argument('--nf', type=int, default=6); t.add_argument('--hid', type=int, default=256)
    t.add_argument('--steps', type=int, default=30000); t.add_argument('--bs', type=int, default=16); t.add_argument('--npts', type=int, default=8192)
    t.add_argument('--lr', type=float, default=5e-4); t.add_argument('--lr_z', type=float, default=1e-3); t.add_argument('--wz', type=float, default=1e-4); t.add_argument('--log_every', type=int, default=500)
    f = sp.add_parser('fit'); f.add_argument('--meta', required=True); f.add_argument('--ckpt', required=True); f.add_argument('--target', required=True)
    f.add_argument('--steps', type=int, default=2000); f.add_argument('--npts', type=int, default=16384); f.add_argument('--lr', type=float, default=5e-3); f.add_argument('--save', default=None)
    a = p.parse_args(); train(a) if a.cmd == 'train' else fit(a)
