#!/bin/bash
# B: 남은 라벨링을 1 프로세스씩 순차 실행 (label2 1개 ≈ 3 GB, 2개 동시 실행은 8 GB 환경에서 OOM)
cd "$(dirname "$0")/../engine"
C="GRIP=2 NX=88 MSYS=0.311 MODE=label2"
env $C NS=80 SEED=1002 OUT=../data/shards_cpu/gen_s1002.npz python3 -u opt_int.py > ../data/shards_cpu/gen_s1002.log 2>&1
env $C SRC=../data/topopt_snapshots_half.npz OUT=../data/shards_cpu/snap_half.npz python3 -u opt_int.py > ../data/shards_cpu/snap_half.log 2>&1
echo "B done $(date)"; ls -la ../data/shards_cpu
