#!/bin/bash
# =====================================================================================================
# [GPU 서버] 4단계: 정확도 올리기 실험 — 기존 실행(BASE, 예: vcpu)은 그대로 두고 새 폴더에서 (11-16 추가)
#
#   (새 폴더 = 이 패키지 사본, 예: vimp)   cd vimp && BASE=../vcpu nohup bash handoff/step4_improve.sh > step4.out 2>&1 &
#   bash handoff/step4_improve.sh status
#
#   CPU 서버 → GPU 서버 (같은 공유 폴더):  [CPU] UNTIL=i2 BASE=../vcpu nohup bash handoff/step4_improve.sh > step4_cpu.out 2>&1 &
#                                          [GPU] 같은 폴더에서 BASE 를 같게 주고 UNTIL 없이 다시 실행 → i1 · i2 건너뛰고 i3 학습부터
#
#  i1 준비     BASE 의 학습 데이터 · 격자 연결(복사 안 함, 읽기만) + 열 연산자(thermal_ops.npz, PINO 용)
#  i2 데이터   추가 학습 데이터 NX 개(씨앗 3001~) + 공통 시험 셋 NT 개(씨앗 9001~, 어느 모델도 학습에 안 씀)   [CPU]
#              두 데이터 모두 충격 · 터치 변위 정답 저장(STORE_U=1, 구조 PINO 용)
#  i3 학습     형상 AI(SDF_STEPS) · CNN · FNO(큰 폭) · PINO(열 잔차) · PINO-S(열 + 구조 잔차) 를 GPU 에 나눠 동시에 [GPU]
#              물리 AI 는 모두 흔들림 · 층간 등 추가값 11개도 예측(--ext, 회귀)
#  i4 확인     새 형상 AI 표현력(기준 구조 복원 IoU)
#  i5 채점     물리 AI 전부(BASE 의 CNN · FNO 포함)를 같은 시험 셋으로
#  i6 최적화   조합마다 잠재 공간 최적화 (새 형상 AI × CNN / FNO / PINO, + BASE 조합)
#  i7 검증     모든 후보를 FEM 으로 다시 계산 (원래 방식, 최종 판정)
#  i8 선택     FEM 통과 · 가장 가벼운 조합 → runs/improve/report.md, best/ (scripts/compare_improve.py)
#
# 끊기면 같은 명령을 다시 실행 → 끝난 단계(runs/state/i*.done)와 끝난 묶음 · 모델은 건너뜀.
# 설정 (앞에 붙임):
#   BASE=../vcpu   기존 실행 폴더 (data/shards_frame, runs/{sdf,cnn,fno}.pt, runs/latent, runs/gate)
#   NX=5000 추가 데이터 · NT=600 시험 셋 · J 병렬 수(기본 자동, step2 와 같은 식) · NOX=1 이면 추가 데이터 없이
#   SDF_STEPS=60000 · PHYS_STEPS=40000 · FNO_W=32 · FNO_MODES="12 8 16" · WPHYS=0.1 (PINO 물리 손실 가중치)
#   WSTRUCT=0.1 (구조 물리 가중치) · DISP_MAX=2000 (변위 정답을 읽을 최대 형상 수, 형상당 메모리 약 1.7 MB)
#   SDF_HID=256 (형상 AI 폭) · GPUS=0,1,2,3 (기본 nvidia-smi 자동) · TINY=1 시험(작게)
# =====================================================================================================
set -e
cd "$(dirname "$0")/.."
ROOT=$(pwd); ST=runs/state; mkdir -p $ST runs/logs runs/improve
BASE=$(cd "${BASE:-../vcpu}" && pwd); M=data/grid_meta.npz; SPEC=spec/bike_mount_targets.json; COMMON="GRIP=2 NX=88 MSYS=0.311"
A=runs/improve; DX=data/shards_extra; DT=data/shards_test
if [ "${TINY:-0}" = "1" ]; then
  NXS=${NX:-2}; NT=${NT:-2}; SDF_STEPS=${SDF_STEPS:-60}; PHYS_STEPS=${PHYS_STEPS:-60}; FNO_W=${FNO_W:-8}; LK=1; LIT=5; J=${J:-1}
  SDF_X='--npts 1024 --bs 4 --log_every 20'; FIT_X='--steps 40 --npts 2048'; PHYS_X='--bs 4 --log_every 20 --phys_warm 10'
else
  NXS=${NX:-5000}; NT=${NT:-600}; SDF_STEPS=${SDF_STEPS:-60000}; PHYS_STEPS=${PHYS_STEPS:-40000}; FNO_W=${FNO_W:-32}; LK=${LK:-6}; LIT=${LIT:-300}
  SDF_X="--hid ${SDF_HID:-256}"; FIT_X=''; PHYS_X=''
fi
FNO_MODES=${FNO_MODES:-"12 8 16"}; WPHYS=${WPHYS:-0.1}; WSTRUCT=${WSTRUCT:-0.1}; DISP_MAX=${DISP_MAX:-2000}
say() { echo "[$(date '+%m-%d %H:%M:%S')] $*"; }
stage() { local name=$1 desc=$2; shift 2
  if [ -f $ST/$name.done ]; then say "건너뜀 (이미 끝남): $desc"; return; fi
  say "시작: $desc"; local t0=$(date +%s)
  if "$@" > runs/logs/$name.log 2>&1; then echo "$(date '+%F %T') $(( $(date +%s) - t0 ))s" > $ST/$name.done; say "끝: $desc ($(( $(date +%s) - t0 )) 초)"
  else say "실패: $desc — runs/logs/$name.log 마지막 30줄:"; tail -30 runs/logs/$name.log; exit 1; fi; }
if [ "$1" = "status" ]; then
  for s in i1_prep i2_data i3_train i4_sdf_fit i5_eval i6_search i7_gate i8_pick; do [ -f $ST/$s.done ] && echo "✔ $s  $(cat $ST/$s.done)" || echo "· $s"; done
  ls runs/*.pt 2>/dev/null; [ -f $A/report.md ] && tail -5 $A/report.md; exit 0; fi

# ---------- 병렬 수 J (step2 와 같은 식: min(메모리 GB ÷ 1.2, 빈 코어 ÷ 2), 컨테이너 몫 · 파일 캐시 반영)
if [ -z "$J" ]; then
read CPU IDLE MEM <<< $(python3 - <<'EOF'
import os
cpu = len(os.sched_getaffinity(0))
try:
    q, p = open('/sys/fs/cgroup/cpu.max').read().split(); quota = q != 'max'
    if quota: cpu = min(cpu, max(1, int(int(q) / int(p))))
except Exception: quota = False
idle = cpu if quota else max(1, int(cpu - os.getloadavg()[0]))
mem = int([l.split()[1] for l in open('/proc/meminfo') if l.startswith('MemAvailable')][0]) / 2**20
try:
    lim = open('/sys/fs/cgroup/memory.max').read().strip()
    if lim != 'max':
        cur = int(open('/sys/fs/cgroup/memory.current').read())
        try: cur -= int([l.split()[1] for l in open('/sys/fs/cgroup/memory.stat') if l.startswith('file ')][0])
        except Exception: pass
        mem = min(mem, (int(lim) - cur) / 2**30)
except Exception: pass
print(cpu, idle, int(mem))
EOF
)
  JA=$(( MEM * 10 / 12 )); JC=$(( IDLE / 2 )); J=$(( JA < JC ? JA : JC )); [ $J -lt 1 ] && J=1
fi
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
say "BASE=$BASE | J=$J | 추가 데이터 ${NXS} · 시험 셋 ${NT} | 형상 AI ${SDF_STEPS} · 물리 AI ${PHYS_STEPS} 스텝 | FNO 폭 ${FNO_W} 모드 ${FNO_MODES} | PINO 물리 가중치 ${WPHYS} | TINY=${TINY:-0}"

# ---------- i1 준비
prep() {
  [ -f $BASE/data/grid_meta.npz ] && [ -n "$(ls $BASE/data/shards_frame/*.npz 2>/dev/null)" ] || { echo "BASE 에 데이터 없음: $BASE"; exit 1; }
  mkdir -p data/shards_frame; cp $BASE/data/grid_meta.npz $M
  for f in $BASE/data/shards_frame/*.npz; do ln -sfr $f data/shards_frame/base_$(basename $f); done   # 상대 경로 (서버마다 공유 폴더 위치가 달라도 됨)
  (cd engine && env $COMMON MODE=thermops OUT=../data/thermal_ops.npz CHECK=1 python3 opt_int.py)
  (cd engine && env $COMMON MODE=structops OUT=../data/struct_ops.npz CHECK=1 python3 opt_int.py)
  ls data/shards_frame | wc -l | xargs echo "연결한 BASE 묶음:"
}
stage i1_prep "준비 (BASE 데이터 연결 · 열 연산자)" prep

# ---------- i2 데이터 (CPU)
gen() {   # gen 출력폴더 씨앗시작 개수 이름
  local out=$1 s0=$2 n=$3 nm=$4; mkdir -p $out; local per=$(( (n + J - 1) / J ))
  for s in $(seq 1 $J); do
    f=$out/${nm}_s$((s0+s)).npz; [ -f $f ] && continue
    (cd engine && env $COMMON MODE=label3 STORE_U=1 NS=$per SEED=$((s0+s)) OUT=../$f python3 -u opt_int.py > ../$out/${nm}_s$((s0+s)).log 2>&1) &
  done; wait
}
data() {
  gen $DT 9000 $NT test
  [ "${NOX:-0}" = "1" ] || gen $DX 3000 $NXS extra
  python3 - <<'EOF'
import glob, numpy as np
c = lambda p: sum(len(np.load(f)['occ']) for f in glob.glob(p))
n_t, n_x, n_b = c('data/shards_test/*.npz'), c('data/shards_extra/*.npz'), c('data/shards_frame/*.npz')
print('시험 셋', n_t, '| 추가', n_x, '| BASE', n_b); assert n_t > 0, '시험 셋 0개 — data/shards_test/*.log 확인'
EOF
  for f in $DX/*.npz; do [ -f "$f" ] && ln -sfr $f data/shards_frame/; done; true
}
stage i2_data "데이터: 시험 셋 ${NT} + 추가 ${NXS} (J=${J})" data
if [ "${UNTIL:-}" = "i2" ]; then say "데이터까지 끝 (UNTIL=i2). GPU 서버에서 이 폴더로 와서 BASE 를 같게 주고 UNTIL 없이 같은 명령 실행"; exit 0; fi
python3 -c "import torch" 2>/dev/null || { say "torch 없음 — 학습(i3~)은 GPU 서버에서. CPU 서버면 UNTIL=i2 로 실행"; exit 1; }
DA='data/shards_frame/*.npz'

# ---------- i3 학습 (GPU 동시)
pick_gpus() {
  if [ -n "$GPUS" ]; then echo "$GPUS" | tr ',' ' '; return; fi
  command -v nvidia-smi >/dev/null || return 0
  nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits 2>/dev/null | awk -F', *' -v m=${GPU_MIN_FREE_MB:-6000} '$2>=m{print $2, $1}' | sort -rn | awk '{printf "%s ", $2}'
}
G=($(pick_gpus)); NG=${#G[@]}
on() { local g=$1; shift; if [ -n "$g" ]; then CUDA_VISIBLE_DEVICES=$g "$@"; else "$@"; fi; }
gpu_of() { [ $NG -gt 0 ] && echo ${G[$(( $1 % NG ))]} || echo ""; }
train_one() {   # 이름 GPU 명령...
  local nm=$1 g=$2; shift 2; [ -f runs/$nm.pt ] && { echo "있음: runs/$nm.pt"; return 0; }
  on "$g" "$@" > runs/logs/train_$nm.log 2>&1 || { echo "실패: $nm — runs/logs/train_$nm.log"; tail -20 runs/logs/train_$nm.log; return 1; }
}
train_all() {
  echo "학습 GPU ${NG}장: ${G[*]:-없음} (5개 학습을 돌아가며 배정, GPU 4장이면 1번째 GPU 에 형상 AI + PINO-S)"
  train_one sdf  "$(gpu_of 0)" python3 -m ai.deepsdf train --meta $M --data "$DA" --out runs/sdf.pt --steps $SDF_STEPS $SDF_X & P0=$!
  train_one fno  "$(gpu_of 1)" python3 -m ai.surrogate --meta $M --data "$DA" --model fno  --out runs/fno.pt  --steps $PHYS_STEPS --ext --width $FNO_W --modes $FNO_MODES $PHYS_X & P1=$!
  train_one pino "$(gpu_of 2)" python3 -m ai.surrogate --meta $M --data "$DA" --model pino --out runs/pino.pt --steps $PHYS_STEPS --ext --width $FNO_W --modes $FNO_MODES --wphys $WPHYS --thermal_ops data/thermal_ops.npz $PHYS_X & P2=$!
  train_one cnn  "$(gpu_of 3)" python3 -m ai.surrogate --meta $M --data "$DA" --model cnn  --out runs/cnn.pt  --steps $PHYS_STEPS --ext $PHYS_X & P3=$!
  train_one pino_s "$(gpu_of 4)" python3 -m ai.surrogate --meta $M --data "$DA" --model pino --struct --out runs/pino_s.pt --steps $PHYS_STEPS --ext --width $FNO_W --modes $FNO_MODES \
      --wphys $WPHYS --thermal_ops data/thermal_ops.npz --wstruct $WSTRUCT --struct_ops data/struct_ops.npz --disp_max $DISP_MAX $PHYS_X & P4=$!
  F=0; for p in $P0 $P1 $P2 $P3 $P4; do wait $p || F=1; done; return $F
}
stage i3_train "학습: 형상 AI · FNO · PINO · CNN · PINO-S (GPU 동시) — 진행은 runs/logs/train_*.log" train_all

# ---------- i4 형상 AI 표현력
sdf_fit() {
  python3 - <<'EOF'
import numpy as np
m = np.load('data/grid_meta.npz'); d = np.load('data/topopt_snapshots.npz'); n = list(d['names'])
ne = int(m['nx']) * int(m['ny']) * int(m['nz']); i = n.index('snap_int35f95g2_119.npy')
np.save('runs/ref_int35f95g2.npy', np.unpackbits(d['r'], axis=1)[i, :ne].astype(np.float32))
EOF
  on "$(gpu_of 0)" python3 -m ai.deepsdf fit --meta $M --ckpt runs/sdf.pt --target runs/ref_int35f95g2.npy --save runs/ref_sdf_recon.npy $FIT_X | tail -1 > $A/sdf_fit.json
  cat $A/sdf_fit.json; [ -f $BASE/runs/sdf_fit.json ] && echo "BASE: $(cat $BASE/runs/sdf_fit.json)"; true
}
stage i4_sdf_fit "형상 AI 표현력 (기준 구조 복원 IoU, 통과 0.8)" sdf_fit

# ---------- i5 채점 (같은 시험 셋)
evalall() {
  on "$(gpu_of 1)" python3 scripts/eval_models.py --meta $M --test "$DT/*.npz" --out $A/eval.json \
    --model base_cnn=$BASE/runs/cnn.pt --model base_fno=$BASE/runs/fno.pt --model cnn=runs/cnn.pt --model fno=runs/fno.pt --model pino=runs/pino.pt --model pino_s=runs/pino_s.pt
}
stage i5_eval "물리 AI 채점 (BASE 포함, 같은 시험 셋)" evalall

# ---------- i6 최적화 (조합별) · i7 FEM 검증
COMBOS="new_cnn|runs/sdf.pt|runs/cnn.pt|cnn new_fno|runs/sdf.pt|runs/fno.pt|fno new_pino|runs/sdf.pt|runs/pino.pt|pino new_pino_s|runs/sdf.pt|runs/pino_s.pt|pino_s base_fno|$BASE/runs/sdf.pt|$BASE/runs/fno.pt|base_fno base_cnn|$BASE/runs/sdf.pt|$BASE/runs/cnn.pt|base_cnn"
search() {   # 동시에 최대 SPAR 개(기본 GPU 수, GPU 없으면 1) — 한꺼번에 띄우면 메모리 부족으로 죽음(11-16 시험). 실패한 조합은 한 번 더 혼자
  local SPAR=${SPAR:-$(( NG > 0 ? NG : 1 ))} i=0
  run1() { IFS='|' read nm sdf phys ev <<< "$1"; out=$A/latent_$nm
    [ -f $sdf ] && [ -f $phys ] || { echo "건너뜀 $nm (모델 없음)"; return 0; }
    [ -f $out/latent_search.json ] && return 0
    on "$(gpu_of $2)" python3 -m ai.latent_search --meta $M --sdf $sdf --phys $phys --data "$DA" --spec $SPEC --out $out --k $LK --iters $LIT > runs/logs/search_$nm.log 2>&1; }
  for c in $COMBOS; do run1 "$c" $i & i=$((i+1)); while [ $(jobs -r | wc -l) -ge $SPAR ]; do sleep 2; done; done; wait
  for c in $COMBOS; do IFS='|' read nm sdf phys ev <<< "$c"
    [ -f $sdf ] && [ -f $phys ] && [ ! -f $A/latent_$nm/latent_search.json ] && { echo "다시 (혼자): $nm"; run1 "$c" 0 || true; }
    [ -f $sdf ] && [ -f $phys ] && [ ! -f $A/latent_$nm/latent_search.json ] && { echo "최적화 실패: $nm — runs/logs/search_$nm.log"; tail -5 runs/logs/search_$nm.log; }
  done
  ls $A/latent_*/cand_*.npy | wc -l | xargs echo "후보 수:"
}
stage i6_search "최적화: 조합별 잠재 공간 탐색 (후보 ${LK}개씩)" search
gate() {
  for f in $A/latent_*/cand_*.npy; do
    nm=$(basename $(dirname $f)); nm=${nm#latent_}; t=$(basename $f .npy); g=$A/gate_$nm; mkdir -p $g
    [ -f $g/frfint_$t.json ] && continue
    (cd $g && env $COMMON MODE=eval RHO=$ROOT/$f TAG=$t python3 $ROOT/engine/opt_int.py > eval_$t.log 2>&1 || echo "FEM 실패 $f") &
    while [ $(jobs -r | wc -l) -ge $J ]; do sleep 2; done
  done; wait; ls $A/gate_*/frfint_*.json | wc -l | xargs echo "FEM 결과:"
}
stage i7_gate "FEM 검증 (모든 후보, 원래 방식)" gate

# ---------- i8 선택
pick() {
  args=(); for c in $COMBOS; do IFS='|' read nm sdf phys ev <<< "$c"; args+=(--combo "$nm|$sdf|$phys|$ev|$A/latent_$nm|$A/gate_$nm"); done
  python3 scripts/compare_improve.py --spec $SPEC --eval $A/eval.json --out $A --best best "${args[@]}"
}
rm -f $ST/i8_pick.done
stage i8_pick "비교 · 선택 → runs/improve/report.md, best/" pick
python3 - <<'EOF'
import glob, os, zipfile
fs = ['runs/improve/report.md', 'runs/improve/choice.json', 'runs/improve/eval.json', 'runs/improve/sdf_fit.json'] + glob.glob('best/*') \
     + glob.glob('runs/improve/latent_*/latent_search.json') + glob.glob('runs/improve/gate_*/frfint_*.json') + glob.glob('runs/logs/*.log') + glob.glob('runs/*.json')
with zipfile.ZipFile('results_improve.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for f in fs:
        if os.path.exists(f): z.write(f)
print('results_improve.zip', round(os.path.getsize('results_improve.zip') / 1e6, 1), 'MB')
EOF
say "전부 끝. runs/improve/report.md 확인, 고른 모델은 best/"
