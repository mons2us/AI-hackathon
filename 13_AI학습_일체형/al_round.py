"""능동 학습 1회: (1) 현재 모델로 AI 탐색(GUI TorchBackend.trace 그대로) → 중간 형상 저장 (2) 엔진 label2 로 정답 계산
(3) 물리 AI(FNO) 이어 학습. 사용: python3 al_round.py <회차> [탐색 반복 300] [추가 학습 스텝 400]. GUI 폴더에는 쓰지 않음."""
import sys, os, json, time, shutil, subprocess, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', '10_입력_1차설계'))
rn = int(sys.argv[1]); iters = int(sys.argv[2]) if len(sys.argv) > 2 else 300; ft_steps = int(sys.argv[3]) if len(sys.argv) > 3 else 400
from formproof_input import inverse as V
from formproof_input.inverse.real import TorchBackend
W = os.path.join(H, 'runs', 'search', 'runs'); os.makedirs(W, exist_ok=True)
for f in ('sdf.pt', 'fno.pt'): shutil.copy(os.path.join(H, 'runs', f), os.path.join(W, f))
B = TorchBackend(os.path.join(W, 'sdf.pt'), os.path.join(W, 'fno.pt'), os.path.join(H, 'data/grid_meta.npz'))
sel = list(V.DEFAULT_SELECTIONS[0]); lim = V.limits(); t0 = time.time()
z0, fit = B.fit(V.start_shape(), steps=600)
R, N, P = [], [], []
for fr in B.trace(z0, sel, lim, iters=iters, every=10):
    full = V.attached(fr['full']); p = fr['pred']; R.append(full); N.append(f'al{rn}_{fr["it"]:03d}')
    P.append(dict(it=fr['it'], mass=round(float(full.sum()) * 0.02032, 2), **{k: (None if p.get(k) is None else round(float(p[k]), 3)) for k in ('f1', 'Tmax', 'touch', 'stress')}))
print(json.dumps(dict(round=rn, step='search', last=P[-1], t=round(time.time() - t0))), flush=True)
os.makedirs(os.path.join(H, 'data/al'), exist_ok=True); R = np.array(R, bool)
src = os.path.join(H, f'data/al/r{rn}_src.npz'); np.savez(src, r=np.packbits(R, axis=1), names=np.array(N), ne=R.shape[1])
json.dump(P, open(os.path.join(H, f'data/al/r{rn}_pred.json'), 'w'), indent=1)
env = dict(os.environ, GRIP='2', NX='88', MSYS='0.311', MODE='label2', SRC=src, OUT=os.path.join(H, f'data/shards/al_r{rn}.npz'))
subprocess.run([sys.executable, '-u', 'opt_int.py'], cwd=os.path.join(H, 'engine'), env=env, check=True,
               stdout=open(os.path.join(H, f'runs/label_al{rn}.log'), 'w'), stderr=subprocess.STDOUT)
d = np.load(os.path.join(H, f'data/shards/al_r{rn}.npz')); lab = d['lab']
cmp = [dict(name=str(n), pred_f1=P[i]['f1'], fem_f1=round(float(l[1]), 1), pred_touch=P[i]['touch'], fem_touch=round(float(max(l[4], l[5])), 3),
            pred_stress=P[i]['stress'], fem_stress=round(float(l[6]), 1), fem_T=round(float(l[3]), 2)) for i, (n, l) in enumerate(zip(d['names'], lab))]
json.dump(cmp, open(os.path.join(H, f'data/al/r{rn}_pred_vs_fem.json'), 'w'), indent=1)
print(json.dumps(dict(round=rn, step='label', n=len(lab), last=cmp[-1], t=round(time.time() - t0))), flush=True)
subprocess.run([sys.executable, '-u', 'finetune.py', str(ft_steps)], cwd=H, check=True,
               stdout=open(os.path.join(H, f'runs/finetune_r{rn}.log'), 'w'), stderr=subprocess.STDOUT)
print(json.dumps(dict(round=rn, step='finetune', t=round(time.time() - t0))), flush=True)
