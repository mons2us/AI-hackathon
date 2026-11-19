"""GINO 물리 AI 학습 — FNO 와 같은 389개 · 같은 분할(seed 0: 학습 331 / 검증 58) · 같은 손실 정의.
손실 = 성능 6개(무게 제외, 정규화) MSE + 분포 MSE(온도: 열 영역 칸, 응력: 재료 칸; FNO 와 같은 마스크 · 같은 척도 ts · vs).
한 단계 = 형상 1개(GINO 는 형상마다 점 배치가 달라 묶음 1), 표면 점 2048 · 출력 점 1024 무작위.
평가는 검증 형상 전체 점으로, FNO 와 같은 지표(성능 평균 |예측/정답 − 1|, 분포 상대 L2)."""
import sys, os, time, json, argparse, numpy as np, torch
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from gino_data import load
from gino_model import GinoSur
p = argparse.ArgumentParser(); p.add_argument('--steps', type=int, default=6000); p.add_argument('--lr', type=float, default=1e-3)
p.add_argument('--ns', type=int, default=2048); p.add_argument('--no', type=int, default=1024); p.add_argument('--r', type=float, default=0.045)
p.add_argument('--eval_every', type=int, default=2000); p.add_argument('--out', default=H + '/gino.pt'); p.add_argument('--threads', type=int, default=1)
p.add_argument('--data', default=None); p.add_argument('--test_names', default=None)
a = p.parse_args(); torch.set_num_threads(a.threads); torch.manual_seed(0)
import json as _j
geo, D, tr, te, norm, Yn, T, V, ts, vs = load(a.data, _j.load(open(a.test_names))) if a.data else load(); N = len(D['occ']); print('train', len(tr), 'test', len(te), flush=True)
TH = geo.thermal.ravel(); CELL = torch.tensor(geo.cell.reshape(-1, 3)); LAT = torch.tensor(geo.latent)
names = ['mass_g', 'f1_hz', 'f2_hz', 'phone_Tmax_rise_c', 'touch_top_mm', 'touch_bottom_mm', 'shock_vm999_mpa']
C = {}
def prep(i):
    if i in C: return C[i]
    F = geo.full(D['occ'][i]); P, Nn = geo.surface(F); fl = F.ravel() > 0.5
    k = np.nonzero(fl | TH)[0]
    tgt = np.stack([T[i].ravel()[k] / ts, V[i].ravel()[k] / vs], 1).astype(np.float32)
    msk = np.stack([TH[k], fl[k]], 1).astype(np.float32)
    C[i] = (torch.tensor(P), torch.tensor(Nn), geo.latent_occ(F), torch.tensor(k), torch.tensor(tgt), torch.tensor(msk)); return C[i]
net = GinoSur(rin=a.r, rout=a.r); w = torch.tensor([0.] + [1.] * 6); Y = torch.tensor(Yn)
opt = torch.optim.AdamW(net.parameters(), lr=a.lr, weight_decay=1e-4); sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, a.steps)
def evaluate(idx):
    net.eval(); P_, FE = [], []
    with torch.no_grad():
        for i in idx:
            Ps, Ns, lo, k, tgt, msk = prep(i); s, f = net(Ps, Ns, LAT, lo, CELL[k])
            P_.append(norm.decode_t(s[None])[0].numpy())
            FE.append((((f - tgt) * msk) ** 2).sum(0).sqrt() / ((tgt * msk) ** 2).sum(0).sqrt().clamp_min(1e-6))
    net.train(); P_ = np.array(P_); T_ = D['lab'][idx]; rel = np.nanmean(np.abs(P_ / np.maximum(np.abs(T_), 1e-6) - 1), 0)
    r = {f'relerr_{n}': float(v) for n, v in zip(names, rel) if n != 'mass_g'}; fe = torch.stack(FE).mean(0)
    r.update(field_relL2_T=float(fe[0]), field_relL2_vm=float(fe[1])); return r, P_
rng = np.random.default_rng(0); t0 = time.time(); log = []
for it in range(a.steps + 1):
    if it % a.eval_every == 0 and it > 0 or it == a.steps:
        r, _ = evaluate(te); r.update(it=it, t=round(time.time() - t0, 1)); log.append(r); print(json.dumps(r), flush=True)
    if it == a.steps: break
    i = int(rng.choice(tr)); Ps, Ns, lo, k, tgt, msk = prep(i)
    si = torch.as_tensor(rng.choice(len(Ps), min(a.ns, len(Ps)), replace=False)); oi = torch.as_tensor(rng.choice(len(k), min(a.no, len(k)), replace=False))
    s, f = net(Ps[si], Ns[si], LAT, lo, CELL[k[oi]])
    m = msk[oi]; loss = (((s - Y[i]) ** 2) * w).sum() / w.sum() + (((f - tgt[oi]) * m) ** 2).sum() / m.sum().clamp_min(1)
    opt.zero_grad(); loss.backward(); opt.step(); sch.step()
    if it % 200 == 0: print(json.dumps(dict(it=it, loss=round(float(loss), 4), t=round(time.time() - t0, 1))), flush=True)
torch.save(dict(kind='gino', state=net.state_dict(), norm=norm.state(), field_scale=[ts, vs], args=vars(a), final=log[-1], log=log,
                n_train=len(tr), n_test=len(te), params=sum(p.numel() for p in net.parameters())), a.out)
print('saved', a.out)
