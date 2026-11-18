"""ESO 속도 진단: 같은 형상 3개를 다듬는 시간 (pypardiso / SuperLU 는 FP08_NO_PARDISO 환경변수로 선택)"""
import time, numpy as np
from fp08 import datagen, eso, fem
print('pypardiso 사용:', fem.HAVE_PARDISO, flush=True)
p, cv = datagen._prob('bike_pad50')
z = np.load('data/bike_pad50/shapes_00000.npz')
occ = np.unpackbits(z['occ'], axis=1)[:, :p.grid.ne].astype(bool)
for k in (0, 2, 4):
    t = time.time(); eso.eso_prune(p, cv, occ[k])
    print(f'  형상 {k}: {time.time() - t:.1f} 초', flush=True)
