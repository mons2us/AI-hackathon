"""후보 선택 + 후보 근처 정밀 최적화 v2 (기존 run_hybrid.sh 는 그대로 둠).
(1) 능동 학습 회차 r<n> 의 후보(10회마다 형상) FEM 결과에서 기준 통과 · 가장 가벼운 형상 선택
(2) 그 형상에서 구조 최적화 + FEM: 경계 선명하게 시작(START_LO/HI 0.02/0.98, 투영 β 16→32), 한 번에 바뀌는 폭 MOVE 작게
(3) 결과 FEM 판정(eval: 진동수 · 흔들림 · 온도 · 휨) + 후보 대비 겹침(IoU)
사용: python3 refine_v2.py <회차> [진동수 목표 Hz 150] [반복 60] [MOVE 0.03]"""
import sys, os, json, subprocess, time, numpy as np
H = os.path.dirname(os.path.abspath(__file__))
rn = int(sys.argv[1]); FT = sys.argv[2] if len(sys.argv) > 2 else '150'; IT = sys.argv[3] if len(sys.argv) > 3 else '60'; MV = sys.argv[4] if len(sys.argv) > 4 else '0.03'
C = json.load(open(f'{H}/data/al/r{rn}_pred_vs_fem.json'))
ok = lambda c, ft: c['fem_f1'] >= ft and c['fem_touch'] <= 0.3 and c['fem_stress'] <= 10.9
d = np.load(f'{H}/data/al/r{rn}_src.npz'); names = [str(n) for n in d['names']]
R = np.unpackbits(d['r'], axis=1)[:, :int(d['ne'])].astype(bool)
for c in C:
    c.setdefault('mass', round(float(R[names.index(c['name'])].sum()) * 0.02032, 2))
P = [c for c in C if ok(c, float(FT))] or [c for c in C if ok(c, 95.0)]
pick = min(P, key=lambda c: c['mass']); print(json.dumps(dict(passed=len(P), pick=pick)), flush=True)
cand = R[names.index(pick['name'])]
W = f'{H}/runs/refine_r{rn}'; os.makedirs(W, exist_ok=True); np.save(f'{W}/start.npy', cand.astype(np.float32))
TAG = f'r{rn}'; base = dict(os.environ, GRIP='2', NX='88', MSYS='0.311', AM='1', TILT='35', FT=FT, TLIM='21', DLIM='0.3')
t0 = time.time()
subprocess.run([sys.executable, '-u', f'{H}/engine/opt_int.py'], cwd=W, check=True, stdout=open(f'{W}/opt.log', 'w'), stderr=subprocess.STDOUT,
               env=dict(base, RF='5', ETAE='0.6', ITERS=IT, SCHED='{"0":16,"20":32}', START_RHO=f'{W}/start.npy', START_LO='0.02', START_HI='0.98', MOVE=MV, TAG=TAG))
subprocess.run([sys.executable, '-u', f'{H}/engine/opt_int.py'], cwd=W, check=True, stdout=open(f'{W}/eval.log', 'w'), stderr=subprocess.STDOUT,
               env=dict(base, MODE='eval', RHO=f'rprint_{TAG}.npy', TAG=TAG))
fin = np.load(f'{W}/rprint_{TAG}.npy').ravel() > 0.5
iou = float((fin & cand).sum() / max(1, (fin | cand).sum()))
ev = json.load(open(f'{W}/frfint_{TAG}.json'))
print(json.dumps(dict(iou_cand_final=round(iou, 3), removed=int((cand & ~fin).sum()), added=int((~cand & fin).sum()), eval=dict(mass_g=ev['mass_g'], f=ev['f'][:3], shake=max(ev['fore']['peak'], ev['vert']['peak']), Tmax=ev['Tmax'], touch=ev['touch_mm'], shock=ev['shock']), t=round(time.time() - t0)), default=str)[:2000], flush=True)
