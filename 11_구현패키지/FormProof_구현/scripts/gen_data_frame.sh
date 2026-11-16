#!/bin/bash
# 프레임 생성기(gen_frame) 학습 데이터 — 서버 CPU. 11-16 추가 (기존 gen_data.sh 는 그대로)
#
#   A 구조+열 정답 (MODE=label3): 생성기 형상 NA 개 + 위상 최적화 기록 245개
#       lab(7열, 기존 ai/ 코드와 같은 순서) + lab_ext(11열: f3 f4, 흔들림 위아래·앞뒤 대역 최대/80Hz 최대/RMS,
#       충격 앞뒤, 층간 위아래·앞뒤) + 분포 T·vm + 생성 변수 prm
#       형상당 약 26–30 s (2스레드, 11-16 측정), 프로세스당 메모리 약 4.1 GB (11-16 측정. README 의 '약 2 GB' 보다 큼)
#   B 열 전용 (MODE=tlabel): 받침판 패턴 NB 번 뽑기 (격자 위 중복은 건너뜀, 약 1/3) → 폰 온도장
#       패턴당 약 0.37 s (11-16 측정)
#
# 사용:  scripts/gen_data_frame.sh [병렬 수 J] [A 형상 수 NA] [B 뽑기 수 NB]
#   병렬 수 J ≤ 메모리(GB) ÷ 4.5 그리고 ≤ 코어 수 ÷ 2.  넘으면 프로세스가 메모리 부족으로 죽음(Killed, 결과 없음)
#   예)  scripts/gen_data_frame.sh 28 5000 20000     # 메모리 128 GB · 64코어 기준
#   시간(추정): A ≈ (NA+245) × 28 s / J  → J=28 이면 약 90분 / B ≈ NB × 0.67 × 0.37 s / J → 약 3분
#   SNAP=0 이면 위상 최적화 기록 245개 생략 (SNAP_N=k 면 앞 k개만), ONLY=A|B 로 한쪽만, THREADS=스레드 수(기본 2)
set -e; cd "$(dirname "$0")/../engine"
J=${1:-4}; NA=${2:-5000}; NB=${3:-20000}
OUTA=../data/shards_frame; OUTB=../data/shards_thermal; mkdir -p $OUTA $OUTB
export OMP_NUM_THREADS=${THREADS:-2} MKL_NUM_THREADS=${THREADS:-2}
COMMON="GRIP=2 NX=88 MSYS=0.311"
env $COMMON MODE=meta OUT=../data/grid_meta.npz python3 opt_int.py > /dev/null
per=$(( (NA + J - 1) / J )); perb=$(( (NB + J - 1) / J ))
echo "A: $J × $per = $((J*per)) 형상 (+ 위상 최적화 기록) → $OUTA"
echo "B: $J × $perb = $((J*perb)) 판 패턴 뽑기 → $OUTB"
if [ "${ONLY:-A}" != "B" ]; then
  for s in $(seq 1 $J); do
    env $COMMON MODE=label3 NS=$per SEED=$((2000+s)) OUT=$OUTA/frame_s$((2000+s)).npz \
      python3 -u opt_int.py > $OUTA/frame_s$((2000+s)).log 2>&1 &
  done
  wait
  if [ "${SNAP:-1}" = "1" ]; then
    N=$(python3 -c "import numpy as np;print(len(np.load('../data/topopt_snapshots.npz')['names']))")
    [ -n "$SNAP_N" ] && [ "$SNAP_N" -lt "$N" ] && N=$SNAP_N          # 시험용: 기록 일부만
    STEP=$(( (N+J-1)/J ))
    for s in $(seq 0 $((J-1))); do
      [ $((s*STEP)) -ge $N ] && break
      env $COMMON MODE=label3 SRC=../data/topopt_snapshots.npz I0=$((s*STEP)) I1=$(((s+1)*STEP)) OUT=$OUTA/snap_$s.npz \
        python3 -u opt_int.py > $OUTA/snap_$s.log 2>&1 &
    done
    wait
  fi
fi
if [ "${ONLY:-A}" != "A" ] || [ -z "${ONLY}" ]; then
  for s in $(seq 1 $J); do
    env $COMMON MODE=tlabel NS=$perb SEED=$((5000+s)) OUT=$OUTB/plate_s$((5000+s)).npz \
      python3 -u opt_int.py > $OUTB/plate_s$((5000+s)).log 2>&1 &
  done
  wait
fi
python3 - <<'EOF'
import glob, numpy as np
a = sorted(glob.glob('../data/shards_frame/*.npz')); b = sorted(glob.glob('../data/shards_thermal/*.npz'))
na = sum(len(np.load(f)['occ']) for f in a); nb = sum(len(np.load(f)['Tmax']) for f in b)
print(f'완료: A {na}개 ({len(a)} 샤드), B {nb}개 판 패턴 ({len(b)} 샤드). 실패는 *.log 의 "fail" 줄 확인')
EOF
