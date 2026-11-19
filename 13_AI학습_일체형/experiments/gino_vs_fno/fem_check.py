"""탐색 결과 형상을 팀 엔진(MODE=eval, GUI 정밀 시뮬레이션과 같은 설정)으로 판정. 저장소 캐시는 건드리지 않음.
사용: python3 fem_check.py gino [fno ...] → fem_<이름>.json"""
import sys, os, json, subprocess, tempfile, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, '/home/claude/input-spec/10_입력_1차설계')
from formproof_input import integral as I
for name in sys.argv[1:]:
    rho = np.load(f'{H}/search_{name}_rho.npy').astype(float).ravel()
    with tempfile.TemporaryDirectory() as td:
        rp = os.path.join(td, 'rho.npy'); np.save(rp, rho)
        env = dict(os.environ, **{k: v for k, v in I.ENGINE_ENV.items() if k in ('GRIP', 'NX', 'MSYS', 'TILT', 'DLIM', 'TLIM', 'FT')}, MODE='eval', RHO=rp, TAG='s', PYTHONUTF8='1')
        p = subprocess.run([sys.executable, I.ENGINE], cwd=td, env=env, capture_output=True, text=True)
        assert p.returncode == 0, p.stderr[-800:]
        r = json.load(open(os.path.join(td, 'frfint_s.json')))
    keep = dict(mass_g=r['mass_g'], f1=r['f'][0], Tmax=r['Tmax'], touch=r['touch_mm'], stress=r.get('shock_vm999', r.get('stress')), shake=max(r['fore']['peak'], r['vert']['peak']))
    json.dump(dict(raw=r, keep=keep), open(f'{H}/fem_{name}.json', 'w'), ensure_ascii=False, indent=1, default=float)
    print(name, keep, flush=True)
