#!/bin/bash
# A: 원본 재현 실행 종료 대기 → 생성기 형상 160개 라벨링 (2 프로세스)
cd "$(dirname "$0")/../engine"
while kill -0 7146 2>/dev/null; do sleep 30; done
echo "ref done $(date)"
C="GRIP=2 NX=88 MSYS=0.311 MODE=label2"
for s in 1001 1002; do env $C NS=80 SEED=$s OUT=../data/shards_cpu/gen_s$s.npz python3 -u opt_int.py > ../data/shards_cpu/gen_s$s.log 2>&1 & done
wait; echo "A done $(date)"; ls -la ../data/shards_cpu
