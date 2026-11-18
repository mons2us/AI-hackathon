#!/bin/bash
# 일체형(한 번에 출력, 핀 · 볼트 없음) 자전거 폰 거치대: 위상 최적화 → 출력 보정 → FEM 판정 → STL (11-18)
#   출력 방향 BUILD=x- (세움: 폰 위쪽 끝이 베드, 핸들바 클립이 맨 위), 45° · 브리지 없음
#   2코어 약 50분 (최적화 120회). 결과: runs/onepiece_* (STL · 그림 · 판정 JSON)
set -e; cd "$(dirname "$0")/../engine"
export GRIP=3 BUILD=x- NX=88 MSYS=0.311 AM=1 RF=8 ETAE=0.7 TILT=35 FT=95 TLIM=21 DLIM=0.3 ITERS=${ITERS:-120} SCHED='{"0":1,"20":2,"40":4,"60":8,"80":16,"100":32}'
[ -f rprint_g3.npy ] && [ "$SKIP_OPT" = "1" ] || TAG=g3 python3 -u opt_int.py > g3_opt.log 2>&1
mkdir -p ../runs
python3 - <<'EOF'
import numpy as np, printability as pr, json
pm = pr.load_meta('../data/grid_meta_g3.npz'); d = pm['design'].astype(bool); s = pm['solid'].astype(bool)
r = np.load('rprint_g3.npy').ravel(); r = np.where(d, (r > 0.5).astype(float), s.astype(float))   # 0/1 (필터 통과 형상)
before, _ = pr.check(r, pm)
r2, added, trimmed = pr.make_self_supporting(r, pm, fixed_ok=False)                               # 고정부(클립 등)까지 받침
r2 = np.where(d, r2, s.astype(float)); after, _ = pr.check(r2, pm)
np.save('../runs/onepiece_rho.npy', r2)
print(json.dumps(dict(need_before=before['need_support'], added_cells=int(added), added_g=round(added * 0.0203, 2), trimmed=int(trimmed), need_after=after['need_support'])))
EOF
MODE=eval RHO=../runs/onepiece_rho.npy TAG=onepiece python3 opt_int.py | tail -1
cp frfint_onepiece.json ../runs/onepiece_eval.json
cd ../cad && python3 onepiece.py ../runs/onepiece_rho.npy ../runs/onepiece
mkdir -p ../results_onepiece && cp ../runs/onepiece_print.stl ../runs/onepiece_eval.json ../runs/onepiece_report.json ../runs/onepiece_views.png ../results_onepiece/   # git 에 올리는 결과 (runs/ 는 .gitignore)
