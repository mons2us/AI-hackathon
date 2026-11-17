"""학습 모델로 AI 탐색 → 마지막 형상 정밀 계산(FEM) 검증. GUI 의 TorchBackend 를 그대로 쓰되, 모델 파일은 이 폴더(runs/)에서 읽는다.
GUI 폴더에는 아무것도 쓰지 않는다 (z0 캐시 · FEM 결과 모두 이 폴더 runs/ 아래, GUI 결과 DB 미사용)."""
import sys, os, json, time, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', '10_입력_1차설계'))
from formproof_input import integral as I
from formproof_input import inverse as V
from formproof_input.inverse.real import TorchBackend
iters = int(sys.argv[1]) if len(sys.argv) > 1 else 300
os.makedirs(os.path.join(H, 'runs/search/runs'), exist_ok=True)
import shutil
for f in ('sdf.pt', 'fno.pt'): shutil.copy(os.path.join(H, 'runs', f), os.path.join(H, 'runs/search/runs', f))
B = TorchBackend(os.path.join(H, 'runs/search/runs/sdf.pt'), os.path.join(H, 'runs/search/runs/fno.pt'), os.path.join(H, 'data/grid_meta.npz'))
sel = list(V.DEFAULT_SELECTIONS[0]); lim = V.limits(); t0 = time.time()
z0, fit = B.fit(V.start_shape(), steps=int(os.environ.get('FIT_STEPS', 600))); print(json.dumps(dict(fit=fit, t=round(time.time() - t0))), flush=True)
path = []
for fr in B.trace(z0, sel, lim, iters=iters, every=10):
    full = V.attached(fr['full']); p = fr['pred']
    path.append(dict(it=fr['it'], mass=round(float(full.sum()) * 0.02032, 2), **{k: (None if p.get(k) is None else round(float(p[k]), 3)) for k in ('f1', 'Tmax', 'touch', 'stress')}))
    print(json.dumps(path[-1]), flush=True); last = full
np.save(os.path.join(H, 'runs/search/final_full.npy'), last)
def fem_eval(rho, tag='ai_search'):   # GUI integral.evaluate 와 같은 엔진 · 설정, 단 GUI 캐시 파일에는 쓰지 않음
    import tempfile, subprocess
    with tempfile.TemporaryDirectory() as td:
        rp = os.path.join(td, 'rho.npy'); np.save(rp, np.asarray(rho, float).ravel())
        env = dict(os.environ, **{k: v for k, v in I.ENGINE_ENV.items() if k in ('GRIP', 'NX', 'MSYS', 'TILT', 'DLIM', 'TLIM', 'FT')}, MODE='eval', RHO=rp, TAG=tag, PYTHONUTF8='1')
        p = subprocess.run([sys.executable, I.ENGINE], cwd=td, env=env, capture_output=True, text=True, timeout=3600)
        if p.returncode: raise RuntimeError(p.stderr[-1500:])
        return json.load(open(os.path.join(td, f'frfint_{tag}.json'), encoding='utf-8'))
r = fem_eval(last.astype(float)); j = I.judge(r)
res = dict(selection=sel, limits={k: list(v) for k, v in lim.items()}, fit=fit, path=path, fem=dict(mass_g=r['mass_g'], pass_=j['pass_'],
           rows=[dict(key=x['key'], value=x['value'], ok=x.get('ok')) for x in j['rows']]), seconds=round(time.time() - t0))
json.dump(res, open(os.path.join(H, 'runs/search/result.json'), 'w'), ensure_ascii=False, indent=1, default=float)
print(json.dumps(res['fem'], ensure_ascii=False, default=float), flush=True)
