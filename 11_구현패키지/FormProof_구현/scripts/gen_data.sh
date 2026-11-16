#!/bin/bash
# 학습 데이터 생성 (CPU, FEM). 프로세스 하나가 메모리 약 2 GB · 형상 1개 약 25초(2코어 기준).
# 사용: scripts/gen_data.sh <병렬 수> <프로세스당 생성기 형상 수>     예) scripts/gen_data.sh 8 250   → 생성기 2,000개
#   + 위상 최적화 기록 245개는 SNAP=1 로 함께 라벨링
set -e; cd "$(dirname "$0")/../engine"; mkdir -p ../data/shards
J=${1:-4}; NS=${2:-50}; COMMON="GRIP=2 NX=88 MSYS=0.311 MODE=label2"
for s in $(seq 1 $J); do
  env $COMMON NS=$NS SEED=$((1000+s)) OUT=../data/shards/gen_s$((1000+s)).npz python3 -u opt_int.py > ../data/shards/gen_s$((1000+s)).log 2>&1 &
done
if [ "${SNAP:-1}" = "1" ]; then
  N=$(python3 -c "import numpy as np;print(len(np.load('../data/topopt_snapshots.npz')['names']))"); STEP=$(( (N+J-1)/J ))
  wait
  for s in $(seq 0 $((J-1))); do
    env $COMMON SRC=../data/topopt_snapshots.npz I0=$((s*STEP)) I1=$(((s+1)*STEP)) OUT=../data/shards/snap_$s.npz python3 -u opt_int.py > ../data/shards/snap_$s.log 2>&1 &
  done
fi
wait; echo "done: $(ls ../data/shards/*.npz | wc -l) 샤드"
