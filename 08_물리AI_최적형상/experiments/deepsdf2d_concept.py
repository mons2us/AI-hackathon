"""Tiny 2D DeepSDF (auto-decoder) on circle<->square family, CPU only.
Shape family: blend t in [0,1] (circle->square) x scale s in [0.6,1.0].
"""
import time, math, torch, torch.nn as nn
torch.manual_seed(0); torch.set_num_threads(2)

def sdf(p, t, s):
    c = p.norm(dim=-1) - 0.6 * s
    q = p.abs() - 0.5 * s
    sq = q.clamp(min=0).norm(dim=-1) + q.max(dim=-1).values.clamp(max=0)
    return (1 - t) * c + t * sq

def make_shapes(n_t, n_s):
    ts = torch.linspace(0, 1, n_t); ss = torch.linspace(0.6, 1.0, n_s)
    return [(float(t), float(s)) for t in ts for s in ss]

def samples(t, s, n=2000):
    u = torch.rand(n // 2, 2) * 2 - 1                      # uniform in box
    ang = torch.rand(n // 2) * 2 * math.pi                 # near surface
    r = torch.linspace(0, 1, 1)
    near = torch.stack([ang.cos(), ang.sin()], -1) * (0.55 * s) + 0.05 * torch.randn(n // 2, 2)
    p = torch.cat([u, near]); return p, sdf(p, torch.tensor(t), torch.tensor(s))

class Dec(nn.Module):
    def __init__(s, zd=8, h=128):
        super().__init__()
        s.net = nn.Sequential(nn.Linear(zd + 2, h), nn.ReLU(), nn.Linear(h, h), nn.ReLU(),
                              nn.Linear(h, h), nn.ReLU(), nn.Linear(h, 1))
    def forward(s, z, p): return s.net(torch.cat([z, p], -1)).squeeze(-1)

CL = 0.1
train = make_shapes(10, 10)                                 # 100 shapes
data = [samples(t, s) for t, s in train]
P = torch.stack([d[0] for d in data]); S = torch.stack([d[1] for d in data])
N, M = P.shape[:2]
dec = Dec(); Z = nn.Embedding(N, 8); nn.init.normal_(Z.weight, 0, 0.01)
opt = torch.optim.Adam([{'params': dec.parameters(), 'lr': 1e-3}, {'params': Z.parameters(), 'lr': 1e-2}])

t0 = time.time(); ep = 0
for ep in range(1, 401):
    idx = torch.randperm(N)
    for b in idx.split(20):
        z = Z(b)[:, None, :].expand(-1, M, -1)
        pred = dec(z, P[b])
        loss = (pred.clamp(-CL, CL) - S[b].clamp(-CL, CL)).abs().mean() + 1e-4 * Z(b).pow(2).sum(-1).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    if ep % 100 == 0: print(f"epoch {ep} loss {loss.item():.4f}  {time.time()-t0:.0f}s", flush=True)
train_time = time.time() - t0

# --- evaluate: IoU on a 128x128 grid
g = torch.linspace(-1, 1, 128); G = torch.stack(torch.meshgrid(g, g, indexing='xy'), -1).reshape(-1, 2)
def iou(a, b): return ((a < 0) & (b < 0)).sum().item() / max(((a < 0) | (b < 0)).sum().item(), 1)

with torch.no_grad():
    tr_iou = sum(iou(dec(Z.weight[i].expand(len(G), -1), G), sdf(G, torch.tensor(t), torch.tensor(s)))
                 for i, (t, s) in enumerate(train)) / N

# unseen shapes: fit latent only (DeepSDF inference), decoder frozen
test = [(0.27, 0.73), (0.61, 0.88), (0.93, 0.65), (0.45, 0.97)]
res = []
for t, s in test:
    p, d = samples(t, s, 1000)
    z = torch.zeros(1, 8, requires_grad=True); o = torch.optim.Adam([z], 5e-2)
    for _ in range(300):
        l = (dec(z.expand(len(p), -1), p).clamp(-CL, CL) - d.clamp(-CL, CL)).abs().mean() + 1e-4 * z.pow(2).sum()
        o.zero_grad(); l.backward(); o.step()
    with torch.no_grad(): res.append(iou(dec(z.expand(len(G), -1), G), sdf(G, torch.tensor(t), torch.tensor(s))))

print(f"\nshapes={N}, params={sum(p.numel() for p in dec.parameters())}, CPU threads=2")
print(f"train time: {train_time:.0f} s ({ep} epochs)")
print(f"train IoU: {tr_iou:.3f}")
print("unseen IoU:", [round(r, 3) for r in res])
