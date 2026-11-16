#!/bin/bash
# GPU 학습 (형상 AI → 물리 AI → 잠재 탐색 → 검증 관문). 데이터: data/shards/*.npz
set -e; cd "$(dirname "$0")/.."; mkdir -p runs; D='data/shards/*.npz'; M=data/grid_meta.npz
python3 -m ai.deepsdf train --meta $M --data "$D" --out runs/sdf.pt --steps ${SDF_STEPS:-30000}
python3 -m ai.deepsdf fit   --meta $M --ckpt runs/sdf.pt --target data/reference/rbin_int35f95g2.npy      # 통과 기준 IoU ≥ 0.8
python3 -m ai.surrogate --meta $M --data "$D" --model cnn --out runs/cnn.pt --steps ${PHYS_STEPS:-20000}   # 기준선
python3 -m ai.surrogate --meta $M --data "$D" --model fno --out runs/fno.pt --steps ${PHYS_STEPS:-20000}
python3 -m ai.latent_search --meta $M --sdf runs/sdf.pt --phys runs/fno.pt --data "$D" --spec spec/bike_mount_targets.json --out runs/latent
# 검증 관문: 후보를 FEM 으로 다시 계산 (CPU)
for f in runs/latent/cand_*.npy; do t=$(basename $f .npy); (cd engine && GRIP=2 NX=88 MSYS=0.311 MODE=eval RHO=../$f TAG=$t python3 opt_int.py | tail -1); done
