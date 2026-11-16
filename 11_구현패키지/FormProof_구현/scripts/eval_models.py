"""물리 AI 여러 개(CNN · FNO · PINO, 이전 실행 포함)를 **같은 시험 셋**(어느 모델도 학습에 안 쓴 데이터)으로 채점 (11-16 추가)

  python3 scripts/eval_models.py --meta data/grid_meta.npz --test 'data/shards_test/*.npz' --out runs/improve/eval.json \
      --model base_fno=../vcpu/runs/fno.pt --model fno_big=runs/fno.pt --model pino=runs/pino.pt
지표: 항목별 상대오차 평균 · 중앙값, f1 은 기준 근처(80–120 Hz)만 따로, f1 ±5% 이내 비율, 분포 상대 L2(FNO · PINO)
"""
import argparse, json, os, sys, numpy as np, torch
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai.data import Grid, load_shards, LAB_NAMES, EXT_NAMES
from ai.surrogate import Surrogate

p = argparse.ArgumentParser()
p.add_argument('--meta', required=True); p.add_argument('--test', required=True); p.add_argument('--out', required=True)
p.add_argument('--model', action='append', default=[], help='이름=체크포인트.pt'); p.add_argument('--bs', type=int, default=8)
a = p.parse_args()
grid = Grid(a.meta); D = load_shards(a.test, grid, fields=True, ext=True); occ, Y = D['occ'], np.concatenate([D['lab'], D['ext']], 1); N = len(Y)
tm = torch.as_tensor(grid.thermal_region, dtype=torch.float32).view(1, grid.nz, grid.ny, grid.nx)
band = (Y[:, 1] >= 80) & (Y[:, 1] <= 120); print('시험 셋', N, '개 (f1 80–120 Hz:', int(band.sum()), '개)', flush=True)
res = []
for spec in a.model:
    name, ck = spec.split('=', 1)
    if not os.path.exists(ck): print('없음:', name, ck); continue
    st = torch.load(ck, map_location='cpu', weights_only=False); M = Surrogate(ck, grid); P = []; FT, FV = [], []
    with torch.no_grad():
        for i in range(0, N, a.bs):
            o = M.predict(occ[i:i + a.bs]); P.append(o['scalars'].cpu().numpy())
            if o['fields'] is not None and st.get('field_scale'):
                ts, vs = st['field_scale']; f = o['fields'].cpu()
                g = grid.to_grid(torch.as_tensor(occ[i:i + a.bs]))[:, 0]
                T = torch.as_tensor(D['T'][i:i + a.bs]).view(-1, grid.nz, grid.ny, grid.nx); V = torch.log1p(torch.as_tensor(D['vm'][i:i + a.bs])).view(-1, grid.nz, grid.ny, grid.nx)
                l2 = lambda pr, tg, m: (((pr - tg) * m) ** 2).sum((1, 2, 3)).sqrt() / ((tg * m) ** 2).sum((1, 2, 3)).sqrt().clamp_min(1e-6)
                FT.append(l2(f[:, 0] * ts, T, tm)); FV.append(l2(f[:, 1] * vs, V, g))
    P = np.concatenate(P); k = P.shape[1]; rel = np.abs(P / np.maximum(np.abs(Y[:, :k]), 1e-6) - 1)
    r = dict(name=name, ckpt=ck, kind=st['kind'], n_train=st.get('n_train'), n_test=N)
    for j, nm in enumerate((LAB_NAMES + EXT_NAMES)[:k]):
        if nm != 'mass_g': r[f'mean_{nm}'] = float(np.nanmean(rel[:, j])); r[f'median_{nm}'] = float(np.nanmedian(rel[:, j]))
    r['f1_band_mean'] = float(rel[band, 1].mean()) if band.any() else None; r['f1_within5pct'] = float((rel[:, 1] <= 0.05).mean())
    if FT: r['field_L2_T'] = float(torch.cat(FT).mean()); r['field_L2_vm_log'] = float(torch.cat(FV).mean())
    res.append(r); print(json.dumps(r, ensure_ascii=False), flush=True)
os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True); json.dump(res, open(a.out, 'w'), indent=1, ensure_ascii=False)
