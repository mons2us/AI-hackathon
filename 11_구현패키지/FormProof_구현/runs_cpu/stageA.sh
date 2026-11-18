#!/bin/bash
# A: 앞선 무거운 계산 종료 대기 → 생성기 형상 160개 라벨링 (2 프로세스, 10개마다 중간 저장)
#    메모리 8 GB 기준: 라벨링 2개 동시 실행 중에는 렌더링 · 평가 등 다른 무거운 작업 금지 (OOM)
cd "$(dirname "$0")/../engine"
while pgrep -f "MODE=eval" >/dev/null || pgrep -x -f "python3 -u opt_int.py" >/dev/null; do sleep 20; done
echo "start $(date)"
C="GRIP=2 NX=88 MSYS=0.311 MODE=label2"
for s in 1001 1002; do env $C NS=80 SEED=$s OUT=../data/shards_cpu/gen_s$s.npz python3 -u opt_int.py > ../data/shards_cpu/gen_s$s.log 2>&1 & done
wait; echo "A done $(date)"; ls -la ../data/shards_cpu
