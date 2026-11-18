"""능동 학습 1회 v2: 모델 폴더 · 목표 조건을 인자로 받음 (기존 al_round.py 는 그대로 둠).
(1) AI 탐색 (GUI TorchBackend.trace 그대로) → 10회마다 형상 (2) 엔진 label2 로 정답(FEM) 계산 → 예측 대비 비교 저장
(3) 물리 AI 이어 학습은 따로 (finetune.py).
사용: python3 al_round_v2.py <회차> <모델 폴더(runs/sdf.pt · fno.pt 있는 곳)> [탐색 반복 300] [진동수 목표 Hz, 기본 150 = 흔들림 대리 목표]"""
import sys, os, json, time, subprocess, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', '10_입력_1차설계'))
rn = int(sys.argv[1]); MD = sys.argv[2]; iters = int(sys.argv[3]) if len(sys.argv) > 3 else 300; ft = float(sys.argv[4]) if len(sys.argv) > 4 else 150.0
from formproof_input import inverse as V
from formproof_input.inverse.real import TorchBackend
B = TorchBackend(os.path.join(MD, 'runs', 'sdf.pt'), os.path.join(MD, 'runs', 'fno.pt'), os.path.join(H, 'data/grid_meta.npz'))
sel = list(V.DEFAULT_SELECTIONS[0]); lim = V.limits(); lim['f1'] = ('>=', ft); lim['Tmax'] = ('<=', 21.0); t0 = time.time()
z0, fit = B.fit(V.start_shape(), steps=600)
R, N, P = [], [], []
for fr in B.trace(z0, sel, lim, iters=iters, every=10):
    full = V.attached(fr['full']); p = fr['pred']; R.append(full); N.append(f'al{rn}_{fr["it"]:03d}')
    P.append(dict(it=fr['it'], mass=round(float(full.sum()) * 0.02032, 2), **{k: (None if p.get(k) is None else round(float(p[k]), 3)) for k in ('f1', 'Tmax', 'touch', 'stress')}))
    print(json.dumps(dict(t=round(time.time() - t0), **P[-1])), flush=True)
os.makedirs(os.path.join(H, 'data/al'), exist_ok=True); R = np.array(R, bool)
src = os.path.join(H, f'data/al/r{rn}_src.npz'); np.savez(src, r=np.packbits(R, axis=1), names=np.array(N), ne=R.shape[1])
json.dump(dict(sel=sel, lim={k: list(v) for k, v in lim.items()}, model=MD, pred=P), open(os.path.join(H, f'data/al/r{rn}_pred.json'), 'w'), indent=1)
env = dict(os.environ, GRIP='2', NX='88', MSYS='0.311', MODE='label2', SRC=src, OUT=os.path.join(H, f'data/shards/al_r{rn}.npz'))
subprocess.run([sys.executable, '-u', 'opt_int.py'], cwd=os.path.join(H, 'engine'), env=env, check=True,
               stdout=open(os.path.join(H, f'runs/label_al{rn}.log'), 'w'), stderr=subprocess.STDOUT)
d = np.load(os.path.join(H, f'data/shards/al_r{rn}.npz')); lab = d['lab']
cmp = [dict(name=str(n), mass=P[i]['mass'], pred_f1=P[i]['f1'], fem_f1=round(float(l[1]), 1), pred_touch=P[i]['touch'], fem_touch=round(float(max(l[4], l[5])), 3),
            pred_stress=P[i]['stress'], fem_stress=round(float(l[6]), 1), pred_T=P[i]['Tmax'], fem_T=round(float(l[3]), 2)) for i, (n, l) in enumerate(zip(d['names'], lab))]
json.dump(cmp, open(os.path.join(H, f'data/al/r{rn}_pred_vs_fem.json'), 'w'), indent=1)
e = [abs(c['pred_f1'] - c['fem_f1']) / c['fem_f1'] for c in cmp]
print(json.dumps(dict(round=rn, step='label', n=len(lab), f1_err_mean=round(100 * float(np.mean(e)), 1), f1_err_max=round(100 * float(np.max(e)), 1), t=round(time.time() - t0))), flush=True)
