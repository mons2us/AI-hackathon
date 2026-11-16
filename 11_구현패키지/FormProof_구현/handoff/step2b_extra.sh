#!/bin/bash
# =====================================================================================================
# [GPU 서버] 2b단계 (선택): step2 와 '같이' 돌리는 추가 작업 — step2 는 멈추거나 고치지 않음
#
#   cd fp11 && nohup bash handoff/step2b_extra.sh > step2b.out 2>&1 &
#   tail -f step2b.out
#
# 하는 일
#   ① step2 의 데이터 생성(s2)이 끝나길 기다림 → GPU 학습 중 놀게 되는 CPU 로 추가 데이터 NX개(기본 5000, 시드 3001~)
#      → data/shards_frame_extra/   (앞 HOLD 묶음(기본 4)은 '고정 시험 셋'으로 따로 둠, 학습에 안 씀)
#   ② step2 가 GPU 3장을 잡은 뒤 남는 GPU 1장에서 학습 곡선용 FNO: 데이터 1000 · 2000 개 (동시에)
#   ③ 추가 데이터가 끝나면 같은 GPU 에서 FNO 를 약 1만 개(본 데이터 + 추가 데이터 − 시험 셋)로 학습
#   ④ 1000 / 2000 / 5245(step2 의 fno.pt) / 약 1만 을 같은 시험 셋으로 채점 → runs/curve/curve.md
#   ⑤ results_curve.zip (회사 PC 로 내려받기)
# 이어하기: 같은 명령을 다시 실행 (끝난 묶음 · 끝난 모델은 건너뜀)
#
# 설정: JX (추가 데이터 병렬 수, 기본 = (CPU 몫 − 12) ÷ 2), NX (기본 5000), HOLD (기본 4), GPU (직접 지정, 기본 자동),
#       CURVE="1000 2000", PHYS_STEPS (기본 20000, step2 와 같아야 비교가 공정), TINY=1 (시험)
# =====================================================================================================
set -e
cd "$(dirname "$0")/.."
ROOT=$(pwd); C=runs/curve; X=data/shards_frame_extra; mkdir -p $C/logs $X
M=data/grid_meta.npz; COMMON="GRIP=2 NX=88 MSYS=0.311"
if [ "${TINY:-0}" = "1" ]; then NXS=${NX:-4}; HOLD=${HOLD:-1}; CURVE=${CURVE:-"2 3"}; PHYS_STEPS=${PHYS_STEPS:-60}; JX=${JX:-2}; PX='--bs 4 --width 8 --log_every 20'
else NXS=${NX:-5000}; HOLD=${HOLD:-4}; CURVE=${CURVE:-"1000 2000"}; PHYS_STEPS=${PHYS_STEPS:-20000}; PX=''; fi
say() { echo "[$(date '+%m-%d %H:%M:%S')] $*"; }
CPU=$(python3 -c "
import os; c=len(os.sched_getaffinity(0))
try:
    q,p=open('/sys/fs/cgroup/cpu.max').read().split()
    if q!='max': c=min(c,int(int(q)/int(p)))
except Exception: pass
print(c)")
JX=${JX:-$(( (CPU - 12) / 2 ))}; [ $JX -lt 1 ] && JX=1
export OMP_NUM_THREADS=${THREADS:-2} MKL_NUM_THREADS=${THREADS:-2}
say "CPU 몫 $CPU → 추가 데이터 병렬 JX=$JX · NX=$NXS (시험 셋 묶음 $HOLD) · 학습 곡선 $CURVE · FNO $PHYS_STEPS 스텝"

# ---------- ① 추가 데이터 (CPU) — step2 의 s2 가 끝난 뒤 시작
say "step2 데이터 생성(s2) 끝나길 기다림"; until [ -f runs/state/s2_data.done ]; do sleep 30; done
gen_extra() {
  per=$(( (NXS + JX - 1) / JX ))
  for s in $(seq 1 $JX); do
    f=$X/frame_s$((3000+s)).npz; [ -f $f ] && continue
    (cd engine && env $COMMON MODE=label3 NS=$per SEED=$((3000+s)) OUT=../$f python3 -u opt_int.py > ../$X/frame_s$((3000+s)).log 2>&1) &
  done; wait
  python3 -c "
import glob,numpy as np; n=sum(len(np.load(f)['occ']) for f in glob.glob('$X/*.npz')); print('추가 데이터',n); assert n>0"
}
say "시작 ① 추가 데이터 $NXS 개 (약 $(( NXS * 60 / (JX * 2) / 60 ))분 추정)"; gen_extra > $C/logs/extra.log 2>&1 &
PG=$!

# ---------- GPU 고르기: step2 가 학습을 시작해 GPU 를 잡은 뒤, 여유 메모리 가장 많은 1장
say "step2 학습 시작 기다림"; until [ -f runs/logs/s6_fno.log ] || [ -f runs/state/s6_fno.done ]; do sleep 20; done; sleep 90
if [ -z "$GPU" ] && command -v nvidia-smi >/dev/null; then
  GPU=$(nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits | sort -t, -k2 -rn | head -1 | cut -d, -f1)
fi
on() { if [ -n "$GPU" ]; then CUDA_VISIBLE_DEVICES=$GPU "$@"; else "$@"; fi; }
say "학습 곡선 GPU: ${GPU:-없음(CPU)}"

# ---------- ② 학습 곡선: 본 데이터에서 N개만 골라 FNO (기록 245개는 항상 포함, 나머지는 생성기 묶음 앞에서부터)
subset() {   # subset N → $C/sub_N/*.npz (필요한 만큼 잘라서 새 묶음으로 저장)
  python3 - "$1" <<'EOF'
import glob, os, sys, numpy as np
N = int(sys.argv[1]); out = f'runs/curve/sub_{N}'; os.makedirs(out, exist_ok=True)
fs = sorted(glob.glob('data/shards_frame/snap_*.npz')) + sorted(glob.glob('data/shards_frame/frame_*.npz')); left = N
for f in fs:
    if left <= 0: break
    d = dict(np.load(f, allow_pickle=True)); n = len(d['occ']); k = min(n, left); left -= k
    per = [key for key, v in d.items() if not key.endswith('_names') and getattr(v, 'ndim', 0) >= 1 and len(v) == n]
    for key in per: d[key] = d[key][:k]
    np.savez(os.path.join(out, os.path.basename(f)), **d)
print('부분 데이터', N - left, '개 →', out)
EOF
}
pids=()
for n in $CURVE; do
  [ -f $C/fno_$n.pt ] && continue
  ( subset $n && on python3 -m ai.surrogate --meta $M --data "$C/sub_$n/*.npz" --model fno --out $C/fno_$n.pt --steps $PHYS_STEPS $PX ) > $C/logs/fno_$n.log 2>&1 &
  pids+=($!); say "시작 ② FNO 데이터 $n 개"
done
for p in "${pids[@]}"; do wait $p || { say "실패: 학습 곡선 FNO — $C/logs/fno_*.log"; exit 1; }; done
say "끝 ② 학습 곡선 FNO"

# ---------- ③ 약 1만 개 FNO (추가 데이터 끝난 뒤)
wait $PG || { say "실패: 추가 데이터 — $C/logs/extra.log, $X/*.log"; exit 1; }; say "끝 ① 추가 데이터"
mkdir -p $C/test $C/big
ls $X/frame_s*.npz | sort -V | head -$HOLD | while read f; do ln -sf $ROOT/$f $C/test/; done
ls $X/frame_s*.npz | sort -V | tail -n +$((HOLD+1)) | while read f; do ln -sf $ROOT/$f $C/big/; done
for f in data/shards_frame/*.npz; do ln -sf $ROOT/$f $C/big/; done
NBIG=$(python3 -c "import glob,numpy as np;print(sum(len(np.load(f)['occ']) for f in glob.glob('$C/big/*.npz')))")
if [ ! -f $C/fno_big.pt ]; then
  say "시작 ③ FNO 데이터 $NBIG 개"
  on python3 -m ai.surrogate --meta $M --data "$C/big/*.npz" --model fno --out $C/fno_big.pt --steps $PHYS_STEPS $PX > $C/logs/fno_big.log 2>&1 \
    || { say "실패 ③ — $C/logs/fno_big.log"; tail -30 $C/logs/fno_big.log; exit 1; }
fi
say "끝 ③"

# ---------- ④ 채점 (step2 의 fno.pt 가 아직이면 기다림)
say "step2 FNO(s6) 끝나길 기다림"; until [ -f runs/state/s6_fno.done ]; do sleep 30; done
NMAIN=$(python3 -c "import glob,numpy as np;print(sum(len(np.load(f)['occ']) for f in glob.glob('data/shards_frame/*.npz')))")
ARGS=""; for n in $CURVE; do ARGS="$ARGS --model $n=$C/fno_$n.pt"; done
on python3 scripts/eval_curve.py --meta $M --test "$C/test/*.npz" --out $C $ARGS --model $NMAIN=runs/fno.pt --model $NBIG=$C/fno_big.pt | tee $C/logs/eval.log | tail -12

# ---------- ⑤ 묶기
python3 -c "
import glob,os,zipfile
z=zipfile.ZipFile('results_curve.zip','w',zipfile.ZIP_DEFLATED)
for f in sorted(set(['$C/curve.md','$C/curve.json','$C/fno_big.pt']+glob.glob('$C/fno_*.json')+glob.glob('$C/logs/*.log'))):
    if os.path.exists(f): z.write(f)
z.close(); print('results_curve.zip', round(os.path.getsize('results_curve.zip')/1e6,1),'MB')"
say "전부 끝. runs/curve/curve.md 확인. 1만 개 모델이 더 좋으면 handoff/README.md '2b' 의 명령으로 최적화를 다시 돌릴 수 있음"
