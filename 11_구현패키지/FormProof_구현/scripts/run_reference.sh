#!/bin/bash
# 기준 결과 재현: 일체형 위상 최적화(120회, 2코어 약 70분) → 출력 몸체 → 재격자화 → 검증
set -e; cd "$(dirname "$0")/../engine"
export GRIP=2 NX=88 MSYS=0.311 AM=1 RF=8 ETAE=0.7 TILT=35 FT=95 TLIM=21 DLIM=0.3 ITERS=120 SCHED='{"0":1,"20":2,"40":4,"60":8,"80":16,"100":32}'
TAG=ref python3 -u opt_int.py > ref_opt.log 2>&1
cd ../cad && python3 parts.py 76 > /dev/null && python3 build_body.py ref ../runs/ref_body && python3 vox.py ../runs/ref_body_phoneframe.stl ../runs/ref_rho.npy 88
cd ../engine && MODE=eval RHO=../runs/ref_rho.npy TAG=ref_body python3 opt_int.py | tail -1
