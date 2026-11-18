"""물리 AI(FNO) 이어 학습: runs/fno.pt 에서 시작, 모든 샤드(능동 학습 샤드 가중 ×3 샘플링), 정규화 그대로. runs/fno.pt 를 덮지 않고 runs/fno_prev.pt 로 보관 후 저장."""
import sys, json, time, shutil, numpy as np, torch
from ai.data import Grid, load_shards, LabelNorm, device
from ai.surrogate import build
steps = int(sys.argv[1]) if len(sys.argv) > 1 else 400; torch.set_num_threads(2)
st = torch.load('runs/fno.pt', map_location='cpu', weights_only=False); dev = device(); grid = Grid('data/grid_meta.npz')
net = build(st['kind'], st['cfg']).to(dev); net.load_state_dict(st['state']); norm = LabelNorm(state=st['norm']); ts, vs = st['field_scale']
D = load_shards('data/shards/*.npz', grid, fields=True); N = len(D['occ']); Yn = norm.encode(D['lab'])
fin = torch.as_tensor(np.isfinite(Yn)); Y = torch.as_tensor(np.nan_to_num(Yn)); occ = torch.as_tensor(D['occ'])
Tf = torch.as_tensor(D['T']).view(N, 1, grid.nz, grid.ny, grid.nx); Vf = torch.log1p(torch.as_tensor(D['vm'])).view(N, 1, grid.nz, grid.ny, grid.nx)
tmask = torch.as_tensor(grid.thermal_region, dtype=torch.float32).view(1, 1, grid.nz, grid.ny, grid.nx); coords = grid.coords(dev)
w = np.array([3.0 if str(n).startswith('al') else 1.0 for n in D['names']]); w /= w.sum()
wl = torch.tensor([0.] + [1.] * 6); opt = torch.optim.AdamW(net.parameters(), lr=5e-4, weight_decay=1e-4); sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, steps)
rng = np.random.default_rng(1); t0 = time.time()
for it in range(steps):
    b = rng.choice(N, 8, p=w); g = grid.to_grid(occ[b]); yn, fl = net(g, coords)
    fb = fin[b]; loss = (((yn - Y[b]) ** 2) * wl * fb).sum() / fb.sum().clamp_min(1)
    tgt = torch.cat([Tf[b] / ts, Vf[b] / vs], 1); m = torch.cat([tmask.expand(len(b), -1, -1, -1, -1), g], 1); loss = loss + ((((fl - tgt) * m) ** 2).sum() / m.sum())
    opt.zero_grad(); loss.backward(); opt.step(); sch.step()
    if it % 100 == 0 or it == steps - 1: print(json.dumps(dict(it=it, loss=round(float(loss), 4), t=round(time.time() - t0))), flush=True)
shutil.copy('runs/fno.pt', 'runs/fno_prev.pt'); st['state'] = net.state_dict(); st['finetune'] = st.get('finetune', 0) + 1; st['n_train'] = N
torch.save(st, 'runs/fno.pt'); print('saved', N)
