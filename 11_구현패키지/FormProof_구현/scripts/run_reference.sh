#!/bin/bash
# 기준 실행(현재 코드): 일체형 위상 최적화(120회, 2코어 약 60분) → 출력 몸체 → 재격자화 → 검증
# 주의: 원본 최종 형상(data/reference/rbin_int35f95g2.npy)의 정확 재현은 불가 — 원본 실행 뒤 고정 부품 정의가 바뀜.
#   2026-11-16 실행(RF=5 ETAE=0.6, MSYS 기본값): 80.0 g · f1 94.7 Hz · 폰 온도 20.83 °C · 터치 0.11 mm, 원본과 IoU 0.69
#   (원본 77.9 g · 95.0 Hz). 그러나 이 결과는 실패: 0/1로 수렴하지 않아 중간 밀도 요소 2,614개(설계 요소 806개의 3.2배)가 강성을 대신함.
#   0.5 기준으로 자른 실제 형상은 끊겨 있고 재계산 시 f1 25.9 Hz · 터치 1.54 mm로 불합격 (원본은 중간 밀도 비율 0.22).
#   → 원본 형상이 필요하면 data/reference/rbin_int35f95g2.npy 를 쓴다. 재현 설정 탐색은 '할 일' 참조.
set -e; cd "$(dirname "$0")/../engine"
export GRIP=2 NX=88 AM=1 RF=5 ETAE=0.6 TILT=35 FT=95 TLIM=21 DLIM=0.3 ITERS=120 SCHED='{"0":1,"20":2,"40":4,"60":8,"80":16,"100":32}'
TAG=ref python3 -u opt_int.py > ref_opt.log 2>&1
cd ../cad && python3 parts.py 76 > /dev/null && python3 build_body.py ref ../runs/ref_body && python3 vox.py ../runs/ref_body_phoneframe.stl ../runs/ref_rho.npy 88
cd ../engine && MODE=eval RHO=../runs/ref_rho.npy TAG=ref_body python3 opt_int.py | tail -1
