#!/bin/bash
# C: CPU 소규모 학습 → 잠재 탐색 → 후보 FEM 검증 (데이터 282개: 생성기 160 + 위상 최적화 이력 122)
set -e; cd "$(dirname "$0")/.."; mkdir -p runs_cpu/out; D='data/shards_cpu/*.npz'; M=data/grid_meta.npz
echo "sdf $(date)"; python3 -m ai.deepsdf train --meta $M --data "$D" --out runs_cpu/out/sdf.pt --steps ${SDF_STEPS:-4000} --bs 8 --npts 4096 --log_every 250
echo "fit $(date)"; python3 -m ai.deepsdf fit --meta $M --ckpt runs_cpu/out/sdf.pt --target data/reference/rbin_int35f95g2.npy --steps 800 || true
echo "cnn $(date)"; python3 -m ai.surrogate --meta $M --data "$D" --model cnn --out runs_cpu/out/cnn.pt --steps ${PHYS_STEPS:-3000} --bs 8 --log_every 250
echo "search $(date)"; python3 -m ai.latent_search --meta $M --sdf runs_cpu/out/sdf.pt --phys runs_cpu/out/cnn.pt --data "$D" --spec spec/bike_mount_targets.json --out runs_cpu/out/latent --k 3 --iters 150
echo "verify $(date)"
for f in runs_cpu/out/latent/cand_*.npy; do t=$(basename $f .npy); (cd engine && GRIP=2 NX=88 MSYS=0.311 MODE=eval RHO=../$f TAG=cpu_$t python3 opt_int.py | tail -1 > ../runs_cpu/out/eval_$t.txt); done
echo "C done $(date)"
