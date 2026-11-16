#!/bin/bash
# B: 위상 최적화 이력 123개(245개 중 짝수 번째) 라벨링 (2 프로세스)
cd "$(dirname "$0")/../engine"
C="GRIP=2 NX=88 MSYS=0.311 MODE=label2 SRC=../data/topopt_snapshots_half.npz"
env $C I0=0 I1=62 OUT=../data/shards_cpu/snap_0.npz python3 -u opt_int.py > ../data/shards_cpu/snap_0.log 2>&1 &
env $C I0=62 I1=123 OUT=../data/shards_cpu/snap_1.npz python3 -u opt_int.py > ../data/shards_cpu/snap_1.log 2>&1 &
wait; echo "B done $(date)"; ls -la ../data/shards_cpu
