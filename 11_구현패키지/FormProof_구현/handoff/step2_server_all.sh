#!/bin/bash
# =====================================================================================================
# [GPU 서버] 2단계: 데이터 생성 → 형상 AI → 물리 AI → 최적화 → FEM 검증 → 결과 묶기 (한 번에, 이어하기 가능)
#
#   cd fp11 && nohup bash handoff/step2_server_all.sh > step2.out 2>&1 &
#   tail -f step2.out                         # 진행 보기
#   bash handoff/step2_server_all.sh status   # 어느 단계까지 끝났는지
#
# 끊기면 같은 명령을 다시 실행 → 끝난 단계(runs/state/*.done)와 끝난 데이터 묶음은 건너뜀.
# 단계를 다시 하려면 runs/state/<단계>.done 을 지우고 실행.
#
# 설정 (환경 변수, 앞에 붙여 실행. 예: NA=2000 bash handoff/step2_server_all.sh)
#   J           데이터 생성 병렬 수. 기본 = min(메모리 GB ÷ 4.5, 코어 수 ÷ 2)  (프로세스당 메모리 약 4.1 GB, 11-16 측정)
#   NA          A 구조 데이터: 프레임 생성기 형상 수 (기본 5000) + 위상 최적화 기록 245개
#   NB          B 열 데이터: 받침판 패턴 뽑기 수 (기본 20000, 중복 약 1/3 은 건너뜀)
#   SDF_STEPS   형상 AI 학습 스텝 (기본 30000)     PHYS_STEPS  물리 AI 학습 스텝 (기본 20000)
#   TINY=1      시험 실행 (데이터 몇 개 · 학습 수십 스텝, CPU 가능, 약 10분) — 처음에 한 번 돌려 볼 것
# =====================================================================================================
set -e
cd "$(dirname "$0")/.."
ROOT=$(pwd); ST=runs/state; mkdir -p $ST runs/logs
M=data/grid_meta.npz; DA='data/shards_frame/*.npz'; SPEC=spec/bike_mount_targets.json
export OMP_NUM_THREADS=${THREADS:-2} MKL_NUM_THREADS=${THREADS:-2}
COMMON="GRIP=2 NX=88 MSYS=0.311"

MEM=$(awk '/MemAvailable/{print int($2/1048576)}' /proc/meminfo); CPU=$(nproc)
JA=$(( MEM * 10 / 45 )); JC=$(( CPU / 2 )); JD=$(( JA < JC ? JA : JC )); [ $JD -lt 1 ] && JD=1
J=${J:-$JD}
if [ "${TINY:-0}" = "1" ]; then
  NA=${NA:-2}; NB=${NB:-40}; SNAP_N=${SNAP_N:-2}; SDF_STEPS=${SDF_STEPS:-60}; PHYS_STEPS=${PHYS_STEPS:-60}; LK=1; LIT=5; J=1
  SDF_X='--npts 1024 --bs 4 --log_every 20'; FIT_X='--steps 40 --npts 2048'; PHYS_X='--bs 4 --width 8 --log_every 20'
else
  NA=${NA:-5000}; NB=${NB:-20000}; SDF_STEPS=${SDF_STEPS:-30000}; PHYS_STEPS=${PHYS_STEPS:-20000}; LK=${LK:-6}; LIT=${LIT:-200}
fi
export SNAP_N

say() { echo "[$(date '+%m-%d %H:%M:%S')] $*"; }
stage() {   # stage 이름 설명 명령...
  local name=$1 desc=$2; shift 2
  if [ -f $ST/$name.done ]; then say "건너뜀 (이미 끝남): $desc"; return; fi
  say "시작: $desc"; local t0=$(date +%s)
  if "$@" > runs/logs/$name.log 2>&1; then
    echo "$(date '+%F %T') $(( $(date +%s) - t0 ))s" > $ST/$name.done; say "끝: $desc ($(( $(date +%s) - t0 )) 초)"
  else
    say "실패: $desc — runs/logs/$name.log 마지막 30줄:"; tail -30 runs/logs/$name.log; exit 1
  fi
}

if [ "$1" = "status" ]; then
  for s in s0_check s1_meta s2_data s3_sdf s4_sdf_fit s5_cnn s6_fno s7_latent s8_gate s9_pack; do
    [ -f $ST/$s.done ] && echo "✔ $s  $(cat $ST/$s.done)" || echo "· $s"; done
  ls data/shards_frame/*.npz 2>/dev/null | wc -l | xargs echo "A 묶음 파일:"; ls data/shards_thermal/*.npz 2>/dev/null | wc -l | xargs echo "B 묶음 파일:"
  exit 0
fi

say "설정: 메모리 여유 ${MEM} GB · 코어 ${CPU} → 병렬 J=${J} | A ${NA}개(+기록) · B ${NB}번 | 형상 AI ${SDF_STEPS} · 물리 AI ${PHYS_STEPS} 스텝 | TINY=${TINY:-0}"

check() {
  python3 - <<'EOF'
import importlib, sys
bad = []
for m in ('numpy', 'scipy', 'pypardiso', 'mmapy', 'torch'):
    try: importlib.import_module(m)
    except Exception as e: bad.append(f'{m}: {e}')
if bad: print('패키지 없음:', *bad, sep='\n  '); sys.exit(1)
import torch; print('torch', torch.__version__, 'GPU', torch.cuda.is_available(), torch.cuda.device_count())
EOF
  if [ "${TINY:-0}" != "1" ]; then
    python3 -c "import torch,sys; sys.exit(0 if torch.cuda.is_available() else 1)" || { echo 'GPU 가 안 보임 (TINY=1 이 아니면 학습이 매우 느림). 강제로 하려면 CPU_OK=1'; [ "${CPU_OK:-0}" = "1" ]; }
  fi
}
stage s0_check "환경 확인 (numpy · scipy · pypardiso · mmapy · torch · GPU)" check

stage s1_meta "격자 정보 (grid_meta.npz)" bash -c "cd engine && env $COMMON MODE=meta OUT=../$M python3 opt_int.py"

data() {
  SNAP_N=$SNAP_N bash scripts/gen_data_frame.sh $J $NA $NB
  python3 -c "
import glob,numpy as np
n=sum(len(np.load(f)['occ']) for f in glob.glob('data/shards_frame/*.npz')); print('A',n)
assert n>0, 'A 데이터 0개 — data/shards_frame/*.log 확인 (Killed 면 J 를 줄일 것)'"
}
stage s2_data "학습 데이터 A(구조+열 ${NA}+기록) · B(열 ${NB}) — 오래 걸림 (J=${J})" data

stage s3_sdf "형상 AI (DeepSDF) 학습 ${SDF_STEPS} 스텝" \
  python3 -m ai.deepsdf train --meta $M --data "$DA" --out runs/sdf.pt --steps $SDF_STEPS $SDF_X

sdf_fit() {   # 기준 구조 = 위상 최적화 기록 int35f95g2 마지막(119) — 원래 파일(rbin_int35f95g2.npy)은 저장소에 없음(.gitignore *.npy)
  python3 - <<'EOF'
import numpy as np
m = np.load('data/grid_meta.npz'); d = np.load('data/topopt_snapshots.npz'); n = list(d['names'])
ne = int(m['nx']) * int(m['ny']) * int(m['nz']); i = n.index('snap_int35f95g2_119.npy')
r = np.unpackbits(d['r'], axis=1)[i, :ne].astype(np.float32); np.save('runs/ref_int35f95g2.npy', r); print('기준 구조', n[i], int(r.sum()))
EOF
  python3 -m ai.deepsdf fit --meta $M --ckpt runs/sdf.pt --target runs/ref_int35f95g2.npy --save runs/ref_sdf_recon.npy $FIT_X | tee /dev/stderr | tail -1 > runs/sdf_fit.json
}
stage s4_sdf_fit "형상 AI 표현력 확인 (기준 구조 복원 IoU, 통과 0.8)" sdf_fit

stage s5_cnn "물리 AI 기준선 CNN ${PHYS_STEPS} 스텝" \
  python3 -m ai.surrogate --meta $M --data "$DA" --model cnn --out runs/cnn.pt --steps $PHYS_STEPS $PHYS_X
stage s6_fno "물리 AI FNO (값 + 온도·응력 분포) ${PHYS_STEPS} 스텝" \
  python3 -m ai.surrogate --meta $M --data "$DA" --model fno --out runs/fno.pt --steps $PHYS_STEPS $PHYS_X

stage s7_latent "최적화: 형상 AI 잠재 공간 × 물리 AI (후보 ${LK}개)" \
  python3 -m ai.latent_search --meta $M --sdf runs/sdf.pt --phys runs/fno.pt --data "$DA" --spec $SPEC --out runs/latent --k $LK --iters $LIT

gate() {    # 후보를 FEM 으로 다시 계산 (물리 AI 예측을 믿지 않고 확인)
  mkdir -p runs/gate
  for f in runs/latent/cand_*.npy; do
    t=$(basename $f .npy); [ -f runs/gate/frfint_$t.json ] && continue
    (cd runs/gate && env $COMMON MODE=eval RHO=$ROOT/$f TAG=$t python3 $ROOT/engine/opt_int.py | tail -1) &
    while [ $(jobs -r | wc -l) -ge $J ]; do sleep 2; done
  done; wait
}
stage s8_gate "FEM 검증 관문 (후보 재계산)" gate

pack() {
  python3 scripts/report_frame.py "$ROOT"
  python3 - <<'EOF'
import glob, os, zipfile
keep = ['runs/report.md', 'runs/report.html', 'runs/sdf_fit.json', 'runs/cnn.json', 'runs/fno.json', 'runs/latent/latent_search.json',
        'runs/sdf.pt', 'runs/cnn.pt', 'runs/fno.pt', 'runs/ref_sdf_recon.npy'] + glob.glob('runs/latent/cand_*.npy') + glob.glob('runs/gate/*.json') \
       + glob.glob('runs/logs/*.log') + glob.glob('runs/state/*') + glob.glob('data/shards_frame/*.log')
with zipfile.ZipFile('results_fp11.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for f in keep:
        if os.path.exists(f): z.write(f)
print('results_fp11.zip', round(os.path.getsize('results_fp11.zip') / 1e6, 1), 'MB  (학습 데이터 묶음은 크기 때문에 뺌: data/shards_*)')
EOF
}
rm -f $ST/s9_pack.done      # 요약·묶기는 매번 다시
stage s9_pack "요약(runs/report.html) + 결과 묶기(results_fp11.zip)" pack
say "전부 끝. results_fp11.zip 을 회사 PC 로 내려받아 handoff\\step3_pc_view.bat"
