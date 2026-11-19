"""FNO 학습 (ai.surrogate.train 의 fno 경로와 같은 손실 · 설정) + 중간 저장 · 이어 학습.
작업 하나가 2시간에 끊기므로 --budget 초가 지나면 저장하고 종료 → 다시 실행하면 이어서.
검증 분할은 389개 때 정한 58개 이름으로 고정.
사용: python3 train_fno_ckpt.py <샤드 패턴> <출력.pt> [--steps 2000] [--budget 6000]"""
import sys, os, json, time, argparse, numpy as np, torch
sys.path.insert(0, '/home/claude/input-spec/13_AI학습_일체형')
from ai.surrogate import build, LAB_NAMES, LOG_LABS
from ai.data import Grid, load_shards, LabelNorm
p = argparse.ArgumentParser(); p.add_argument('data'); p.add_argument('out'); p.add_argument('--steps', type=int, default=2000)
p.add_argument('--budget', type=float, default=6000); p.add_argument('--ck_every', type=int, default=100); p.add_argument('--log_every', type=int, default=500)
a = p.parse_args(); torch.set_num_threads(int(os.environ.get('THREADS', 2)))
G = os.path.dirname(os.path.abspath(__file__)); meta = '/home/claude/input-spec/13_AI학습_일체형/data/grid_meta.npz'
grid = Grid(meta); D = load_shards(a.data, grid, fields=True); N = len(D['occ'])
nm = [str(x) for x in D['names']]; te = np.array([nm.index(t) for t in json.load(open(G + '/test_names.json'))]); tr = np.setdiff1d(np.arange(N), te)
print('train', len(tr), 'test', len(te), flush=True)
LAB = D['lab']; norm = LabelNorm(LAB[tr], log_idx=list(LOG_LABS)); Yn = norm.encode(LAB)
fin = torch.as_tensor(np.isfinite(Yn)); Y = torch.as_tensor(np.nan_to_num(Yn))
cfg = dict(n_out=7, width=12, modes=(8, 5, 12)); torch.manual_seed(0); net = build('fno', cfg); coords = grid.coords(torch.device('cpu'))
opt = torch.optim.AdamW(net.parameters(), lr=1e-3, weight_decay=1e-4); sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, a.steps)
occ = torch.as_tensor(D['occ']); w_lab = torch.tensor([0.] + [1.] * 6)
Tf = torch.as_tensor(D['T']).view(N, 1, grid.nz, grid.ny, grid.nx); Vf = torch.log1p(torch.as_tensor(D['vm'])).view(N, 1, grid.nz, grid.ny, grid.nx)
tmask = torch.as_tensor(grid.thermal_region, dtype=torch.float32).view(1, 1, grid.nz, grid.ny, grid.nx)
ts, vs = Tf[tr].std() + 1e-6, Vf[tr].std() + 1e-6
rng = np.random.default_rng(0); log = []; it0 = 0; CK = a.out + '.ckpt'
if os.path.exists(CK):
    c = torch.load(CK, weights_only=False); net.load_state_dict(c['net']); opt.load_state_dict(c['opt']); sch.load_state_dict(c['sch'])
    rng.bit_generator.state = c['rng']; torch.set_rng_state(c['trng']); log = c['log']; it0 = c['it']; print('resume', it0, flush=True)
def evaluate(idx):
    net.eval(); P = []; FE = []
    with torch.no_grad():
        for i in range(0, len(idx), 16):
            b = idx[i:i + 16]; g = grid.to_grid(occ[b]); yn, fl = net(g, coords)[:2]; P.append(norm.decode_t(yn))
            tgt = torch.cat([Tf[b] / ts, Vf[b] / vs], 1); m = torch.cat([tmask.expand(len(b), -1, -1, -1, -1), g], 1)
            FE.append((((fl - tgt) * m) ** 2).sum((2, 3, 4)).sqrt() / ((tgt * m) ** 2).sum((2, 3, 4)).sqrt().clamp_min(1e-6))
    net.train(); P = torch.cat(P).numpy(); rel = np.nanmean(np.abs(P / np.maximum(np.abs(LAB[idx]), 1e-6) - 1), 0)
    r = {f'relerr_{n}': float(v) for n, v in zip(LAB_NAMES, rel) if n != 'mass_g'}; fe = torch.cat(FE).mean(0).numpy()
    r.update(field_relL2_T=float(fe[0]), field_relL2_vm=float(fe[1])); return r
def save_ck(it):
    torch.save(dict(net=net.state_dict(), opt=opt.state_dict(), sch=sch.state_dict(), rng=rng.bit_generator.state, trng=torch.get_rng_state(), log=log, it=it), CK + '.tmp')
    os.replace(CK + '.tmp', CK)
t0 = time.time()
for it in range(it0, a.steps):
    b = rng.choice(tr, 16); g = grid.to_grid(occ[b]); yn, fl = net(g, coords)[:2]
    fb = fin[b]; loss = (((yn - Y[b]) ** 2) * w_lab * fb).sum() / fb.sum().clamp_min(1)
    tgt = torch.cat([Tf[b] / ts, Vf[b] / vs], 1); m = torch.cat([tmask.expand(len(b), -1, -1, -1, -1), g], 1)
    loss = loss + (((fl - tgt) * m) ** 2).sum() / m.sum()
    opt.zero_grad(); loss.backward(); opt.step(); sch.step()
    if it % a.log_every == 0 or it == a.steps - 1:
        r = dict(it=it, loss=float(loss.detach()), t=round(time.time() - t0, 1), **evaluate(te)); log.append(r); print(json.dumps(r), flush=True)
    if (it + 1) % a.ck_every == 0:
        save_ck(it + 1); print(json.dumps(dict(ck=it + 1, t=round(time.time() - t0, 1))), flush=True)
        if time.time() - t0 > a.budget and it + 1 < a.steps: print('budget stop', it + 1, flush=True); sys.exit(0)
st = dict(kind='fno', cfg=cfg, state=net.state_dict(), norm=norm.state(), field_scale=[float(ts), float(vs)], names=list(LAB_NAMES), u_scale=None,
          n_train=len(tr), n_test=len(te), final=log[-1])
torch.save(st, a.out); json.dump(dict(final=log[-1], log=log), open(a.out.replace('.pt', '.json'), 'w'), indent=1); print('saved', a.out, flush=True)
