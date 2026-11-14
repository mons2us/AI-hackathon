#!/usr/bin/env bash
# ===== [GPU 서버] 3단계: 학습 (DeepSDF 6개 + PINO 3개 + 관문 + 능동학습 + 시연) =====
# 사용:  mkdir fp08run && cd fp08run && unzip ../upload_code.zip && bash handoff/step3_server_train.sh [A|B]
#   A (기본) : 데이터도 서버에서 만듦 (서버 CPU 코어가 많을 때. 회사 PC 에서 만들 필요 없음)
#   B        : 회사 PC 에서 만든 upload_data.zip 을 이 폴더에 두고 실행
# 끊기면 같은 명령을 다시 실행 → runs/main/state.json 보고 끝난 단계는 건너뜀
set -e
cd "$(dirname "$0")/.."
PLAN=${1:-A}
python - <<'P'
import torch, os
print('torch', torch.__version__, '| GPU', torch.cuda.device_count(), [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())], '| CPU', os.cpu_count())
P
NG=$(python -c "import torch;print(torch.cuda.device_count())")
if [ "$NG" = "0" ]; then echo "GPU 가 안 보입니다 (nvidia-smi, CUDA판 torch 확인). 중단."; exit 1; fi
DEV=$(python -c "print(','.join(f'cuda:{i}' for i in range($NG)))")
# GPU 가 1~2장이면 한 장에 여러 작업을 동시에 (DeepSDF 는 작아서 같이 돌려도 됨)
if [ "$NG" -lt 3 ]; then DEV="$DEV,$DEV,$DEV"; fi
echo "장치: $DEV"
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
if [ "$PLAN" = "B" ]; then
  [ -d data ] || python -m fp08.pack unpack upload_data.zip .
  STAGES=sdf,pino,gate,al,demo
else
  STAGES=shapes,fem,sdf,pino,gate,al,demo
fi
python -m fp08.loop --run runs/main --data data --stages $STAGES --devices "$DEV" --workers $(nproc) \
  --n-shapes 5000 --n-cand 12000 --eso --n-fem 1000 \
  --sdf-steps 20000 --sdf-width 256 --sdf-depth 8 --pino-steps 30000 \
  --al-n 200 --max-rounds 3 2>&1 | tee -a runs_main.out
python -m fp08.pack check data
python -m fp08.pack runs runs/main results.zip
echo "끝. results.zip 을 회사 PC 로 내려받아 handoff\\step4_pc_demo.bat 실행"
