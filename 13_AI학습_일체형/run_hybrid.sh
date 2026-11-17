#!/bin/bash
# AI 탐색 후보(al3_120: 89.4 g, 진동수 99 Hz)에서 출발하는 정밀 최적화(구조 최적화 + FEM) → 출력 형상 정밀 판정
cd "$(dirname "$0")/runs/hybrid"
C="GRIP=2 NX=88 MSYS=0.311 AM=1 TILT=35 FT=95 TLIM=21 DLIM=0.3"
env $C RF=5 ETAE=0.6 ITERS=${ITERS:-60} SCHED='{"0":4,"20":8,"40":16,"50":32}' START_RHO=start_al3_120.npy TAG=hyb python3 -u ../../engine/opt_int.py > opt.log 2>&1
env $C MODE=eval RHO=rprint_hyb.npy TAG=hyb python3 -u ../../engine/opt_int.py > eval.log 2>&1
echo done
