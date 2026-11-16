"""학습 곡선: 물리 AI 모델 여러 개를 같은 고정 시험 셋(학습에 안 쓴 추가 데이터 일부)으로 채점.

python3 scripts/eval_curve.py --meta data/grid_meta.npz --test 'runs/curve/test/*.npz' --out runs/curve \
        --model 1000=runs/curve/fno_1000.pt --model 5245=runs/fno.pt ...
출력: runs/curve/curve.json, runs/curve/curve.md (데이터 수별 상대 오차 표)
"""
import argparse, json, os, sys
import numpy as np, torch
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai.data import Grid, load_shards, LAB_NAMES
from ai.surrogate import Surrogate

p = argparse.ArgumentParser()
p.add_argument('--meta', required=True); p.add_argument('--test', required=True); p.add_argument('--out', required=True)
p.add_argument('--model', action='append', default=[], help='데이터수=체크포인트.pt')
a = p.parse_args()
grid = Grid(a.meta); D = load_shards(a.test, grid, fields=False); occ = D['occ']; T = D['lab']
print('시험 셋', len(T), '개')
res = []
for spec in a.model:
    n, ck = spec.split('=', 1)
    if not os.path.exists(ck):
        print('없음', ck); continue
    M = Surrogate(ck, grid); P = []
    with torch.no_grad():
        for i in range(0, len(occ), 16):
            P.append(M.predict(occ[i:i + 16])['scalars'].cpu().numpy())
    P = np.concatenate(P)
    rel = np.abs(P / np.maximum(np.abs(T), 1e-6) - 1)
    r = dict(n_data=int(n), ckpt=ck, n_test=len(T))
    for j, nm in enumerate(LAB_NAMES):
        if nm != 'mass_g':
            r[f'mean_{nm}'] = float(rel[:, j].mean()); r[f'median_{nm}'] = float(np.median(rel[:, j]))
    r['f1_within5pct'] = float((rel[:, 1] <= 0.05).mean())
    res.append(r); print(json.dumps(r), flush=True)
res.sort(key=lambda r: r['n_data'])
os.makedirs(a.out, exist_ok=True)
json.dump(res, open(os.path.join(a.out, 'curve.json'), 'w'), indent=1)
names = [n for n in LAB_NAMES if n != 'mass_g']
L = ['# 학습 곡선 (FNO, 같은 시험 셋 %d개, 상대 오차 중앙값)' % len(T), '',
     '| 데이터 수 | ' + ' | '.join(names) + ' | f1 ±5% 이내 |', '|' + '---|' * (len(names) + 2)]
for r in res:
    L.append(f"| {r['n_data']} | " + ' | '.join(f"{r['median_' + n] * 100:.1f}%" for n in names) + f" | {r['f1_within5pct'] * 100:.0f}% |")
L += ['', '읽는 법: 데이터가 늘 때 오차가 아직 크게 줄면 → 데이터를 더 만들면 좋아짐. 거의 그대로면 → 데이터 수는 충분, 모델·학습을 바꿔야 함.']
open(os.path.join(a.out, 'curve.md'), 'w', encoding='utf-8').write('\n'.join(L)); print('\n'.join(L))
