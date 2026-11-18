"""출력 조건 학습 데이터: 기존 학습 형상(모든 샤드)에 출력 필터(45° 돌출, 팀 엔진과 같은 식)를 적용 → 바뀐 형상만 FEM(엔진 label2)으로 정답 계산.
물리 AI 가 '출력 가능한 형상'의 성능을 배우게 하는 데이터. 40개씩 나눠 data/shards/print_cNN.npz 로 저장(중간에 멈춰도 끝난 묶음은 남음).
사용: python3 make_print_data.py [최소 제거 칸 20] [시작 묶음 0]"""
import sys, os, glob, subprocess, json, time, numpy as np, torch
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', '10_입력_1차설계'))
from formproof_input import inverse as V
MIN = int(sys.argv[1]) if len(sys.argv) > 1 else 20; C0 = int(sys.argv[2]) if len(sys.argv) > 2 else 0
B = V.backend(); g = B.grid
src = os.path.join(H, 'data/al/print_src.npz')
if not os.path.exists(src):
    R, N = [], []
    for f in sorted(glob.glob(os.path.join(H, 'data/shards/*.npz'))):
        if os.path.basename(f).startswith('print_'): continue
        d = np.load(f); occ = np.unpackbits(d['occ'], axis=1)[:, :g.nd].astype(bool); names = list(d['names'])
        for o, nm in zip(occ, names):
            fo = B.am_filter(torch.as_tensor(o.astype(np.float32)).unsqueeze(0))[0].numpy() > 0.5
            if int((o & ~fo).sum()) > MIN:
                full = g.solid.copy(); full[g.didx] = fo; R.append(full); N.append('pr_' + str(nm))
    R = np.array(R, bool); np.savez(src, r=np.packbits(R, axis=1), names=np.array(N), ne=R.shape[1])
    print(json.dumps(dict(step='filter', n=len(N))), flush=True)
n = len(np.load(src)['names']); t0 = time.time()
for c in range(C0, (n + 39) // 40):
    out = os.path.join(H, f'data/shards/print_c{c:02d}.npz')
    if os.path.exists(out): continue
    env = dict(os.environ, GRIP='2', NX='88', MSYS='0.311', MODE='label2', SRC=src, I0=str(40 * c), I1=str(min(n, 40 * c + 40)), OUT=out)
    subprocess.run([sys.executable, '-u', 'opt_int.py'], cwd=os.path.join(H, 'engine'), env=env, check=True,
                   stdout=open(os.path.join(H, f'runs/label_print_c{c:02d}.log'), 'w'), stderr=subprocess.STDOUT)
    print(json.dumps(dict(step='label', chunk=c, of=(n + 39) // 40, t=round(time.time() - t0))), flush=True)
