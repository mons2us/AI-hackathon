# 11 일체형 · 서버 한 번에 돌리기 (step1 → step2 → step3)

```
[회사 PC] step1_pc_pack.bat   →  upload_fp11.zip (약 5 MB)  ──올림──▶
[GPU 서버] step2_server_all.sh  (데이터 → 형상 AI → 물리 AI → 최적화 → FEM 검증 → 묶기)
                                 →  results_fp11.zip  ──내려받음──▶
[회사 PC] step3_pc_view.bat   →  runs\report.html 이 열림
```

## 1. 회사 PC: 묶기
`handoff\step1_pc_pack.bat` 를 더블클릭. 시험부터 하려면 명령창에서 `handoff\step1_pc_pack.bat test` 로 실행 (패키지 확인 + 빠른 테스트, 약 2분).
- 묶음에 들어가는 것: 코드, `data/grid_meta.npz`, `data/topopt_snapshots.npz` (위상 최적화 기록 245개), `data/reference/` (기준 결과).
- 학습 데이터는 넣지 않음. 서버에서 새로 만듦.

## 2. GPU 서버: 한 번에 실행
```bash
unzip upload_fp11.zip && cd fp11
pip install -r requirements.txt -r requirements_gpu.txt   # 처음 한 번. torch 는 서버 CUDA 버전에 맞출 것
TINY=1 bash handoff/step2_server_all.sh                   # ① 시험: 데이터 몇 개 · 학습 수십 스텝 (GPU 서버 약 5분, CPU 2코어 약 15분)
rm -rf runs data/shards_frame data/shards_thermal         # ② 시험 결과 지우기 (꼭!)
nohup bash handoff/step2_server_all.sh > step2.out 2>&1 &  # ③ 본 실행 (SSH 끊겨도 계속 돎)
tail -f step2.out                                          # 진행 보기 (Ctrl+C 로 보기만 멈춤)
bash handoff/step2_server_all.sh status                    # 어느 단계까지 끝났는지
```

| 단계 | 하는 일 | 결과 |
|---|---|---|
| s0 | 환경 확인 (numpy · scipy · pypardiso · mmapy · torch · GPU) | |
| s1 | 격자 정보 | `data/grid_meta.npz` |
| s2 | **학습 데이터 (가장 오래 걸림)**. A: 프레임 생성기 형상 5,000개 + 위상 최적화 기록 245개를 FEM 으로 계산 (진동수 · 흔들림 · 터치 · 충격 · 층간 · 폰 온도). B: 받침판 패턴 20,000번 뽑아 열만 계산 | `data/shards_frame/`, `data/shards_thermal/` |
| s3 | 형상 AI (DeepSDF) 학습: 형상 → 숫자 32개(잠재 코드) → 형상 | `runs/sdf.pt` |
| s4 | 형상 AI 표현력 확인: 기준 구조를 다시 그려 겹침 비율(IoU) ≥ 0.8 인지 | `runs/sdf_fit.json` |
| s5 · s6 | 물리 AI 학습: CNN(기준선) · FNO. 형상 → 질량 · f1 · 폰 온도 · 터치 · 충격 예측 | `runs/cnn.pt`, `runs/fno.pt` |
| s7 | 최적화: 잠재 코드를 바꿔 가며 물리 AI 로 "기준 통과 + 가볍게" 찾기 (후보 6개) | `runs/latent/cand_*.npy` |
| s8 | FEM 검증 관문: 후보를 FEM 으로 다시 계산 (AI 예측을 그대로 믿지 않음) | `runs/gate/frfint_cand_*.json` |
| s9 | 요약 + 묶기 | `runs/report.html`, `results_fp11.zip` |

- **이어하기**: 서버가 끊기거나 실패하면 같은 명령을 다시 실행. 끝난 단계(`runs/state/*.done`)와 끝난 데이터 묶음은 건너뜀. 한 단계만 다시 하려면 `runs/state/s5_cnn.done` 같은 파일을 지우고 실행.
- **실패하면** 화면에 그 단계 기록(`runs/logs/<단계>.log`)의 마지막 30줄이 나옴. 데이터 단계는 `data/shards_frame/*.log` 도 확인. `Killed` 는 메모리 부족이니 `J` 를 줄여서 다시 실행.
- **설정** (명령 앞에 붙임. 예: `J=8 NA=2000 bash handoff/step2_server_all.sh`)
  - `J`: 병렬 수. 기본 = min(여유 메모리 GB ÷ 1.2, 빈 코어 ÷ 2). 빈 코어 = 허용 코어 − 1분 평균 부하. 시작할 때 예상 시간도 출력. FEM 1개당 메모리 약 0.94 GB (재료 칸만 조립, 11-16 측정)
  - `NA`: A 형상 수 (기본 5000). `NB`: B 뽑기 수 (기본 20000)
  - `SDF_STEPS` (기본 30000), `PHYS_STEPS` (기본 20000)
  - `GPUS=0,2,3`: 학습에 쓸 GPU 직접 지정. 안 주면 `nvidia-smi` 로 여유 메모리 `GPU_MIN_FREE_MB`(기본 6000) 이상인 GPU 를 여유 많은 순으로 자동 선택
  - `CPU_OK=1`: GPU 없이 강제 실행

### GPU 여러 장 (11-16 추가)
```
GPU 3장 이상:  GPU①  형상 AI 학습 → IoU 확인 ─┐
               GPU②  FNO 학습 ────────────────┼─▶ 최적화(s7, GPU①) → FEM 검증(CPU)
               GPU③  CNN 학습 ────────────────┘
GPU 2장: 형상 AI 한 장 + (CNN → FNO) 한 장      GPU 1장 이하: 차례로
```
- 세 학습은 서로의 결과를 쓰지 않아서 동시에 돌려도 결과가 같음. 학습 시간 = 셋의 합 → **가장 긴 하나**.
- 4번째 GPU 는 지금은 안 씀 (아직 맡길 학습이 없음. 열 모델 · 흔들림/층간 모델을 추가하면 거기에 씀).
- 한 학습을 GPU 여러 장에 나누는 방식(DDP)은 아님. 묶음 크기가 16 으로 작아서 효과가 불확실하고 코드 변경이 큼.
- 가장 오래 걸리는 s2 데이터 생성은 CPU(FEM) 작업이라 GPU 수와 상관없음.

### 걸리는 시간 (추정, 서버에서 확인 필요)
| 항목 | 근거 | 예: 128 GB · 64코어 (J=28) |
|---|---|---|
| s2 A | 형상 1개 약 3초 (재료 칸만 조립, 2코어 단독, 11-16 측정) × 5,245 ÷ J. 서버에서 동시에 많이 돌면 느려짐 → 로그 `dt` 로 확인 | 약 10분 |
| s2 B | 판 패턴 1개 약 0.25초 | 몇 분 |
| s3 ~ s6 | GPU 학습 (08 경험상 각 수십 분). GPU 3장 이상이면 동시에 | 차례로 1 ~ 2시간 → 동시에 가장 긴 하나만큼 (미측정) |
| s7 · s8 | 후보 6개 × FEM | 수 분 |

### 데이터 생성 속도: 재료 칸만 조립 (11-16 추가, `REDUCE=1` 기본)
- **문제**: 원래 방식은 형상과 상관없이 빈 칸까지 전부(자유도 약 17만) 조립 · 분해 → 형상 1개 약 29 s · 3.9 GB. 서버(J=100 동시)에서는 **약 250 s** 로 느려짐(11-16 실측, 메모리 대역폭 경쟁 추정) → 5,245개에 약 3.5시간.
- **해결**: 학습 데이터는 0/1 형상이므로 재료 칸 + 고정 부품만 조립(`engine/opt_int.py` `reduced_on`, `label_any`). 클램프와 이어지지 않은 조각은 계산에서 빼고(무게에는 포함), 폰 붙는 곳이 끊긴 형상은 원래 방식으로 계산.
- **확인** (`MODE=bench`, `MODE=label3 REDUCE=0/1`, 생성기 형상 3~4개, 2코어):

| | 원래 (REDUCE=0) | 재료 칸만 (REDUCE=1) |
|---|---|---|
| 형상 1개 (열 포함) | 28.5–29.1 s | 2.7–3.4 s |
| 최대 메모리 | 3.9 GB | 0.94 GB |
| 값 차이 | — | f2 최대 0.55 %, 나머지 7+11개 값 ≤ 0.2 %, 온도 · 형상 같음 |

- 최종 판정(s8 FEM 검증 관문 `MODE=eval`)은 **원래 방식 그대로** — 빠른 방식은 학습 데이터에만 사용.
- 원래 방식으로 되돌리려면 `REDUCE=0` (이때 J 를 메모리 ÷ 4.5 로 직접 줄일 것).

## 2a. 데이터는 CPU 서버, 학습은 GPU 서버 (11-16 추가, `UNTIL=s2`)
```bash
# [CPU 서버] fp11 폴더 (step1 묶음 그대로 풀고 requirements.txt 만 설치. torch 불필요)
nohup env UNTIL=s2 bash handoff/step2_server_all.sh > step2.out 2>&1 &   # s0 ~ s2 → data_fp11.zip
# [GPU 서버] fp11 폴더에 data_fp11.zip 복사 후
unzip -o data_fp11.zip && nohup bash handoff/step2_server_all.sh > step2.out 2>&1 &   # s1 · s2 건너뛰고 s3 학습부터
```
- `UNTIL=s2` 는 torch · GPU 검사를 하지 않고, s2 가 끝나면 `data_fp11.zip`(격자 정보 + 학습 데이터 묶음 + s1 · s2 완료 표시)을 만들고 끝남.
- GPU 서버는 완료 표시가 있으니 데이터를 다시 만들지 않음. s0 환경 확인(GPU 포함)만 GPU 서버에서 다시 함.
- 묶음 크기(추정): 구조 데이터 형상당 약 30 KB → 5,245개 약 0.2 GB, 열 데이터(B) 약 1 ~ 2 GB.
- GPU 서버에 이전 실행의 `data/shards_*` · `runs/` 가 남아 있으면 먼저 지울 것 (섞이지 않게).
- 11-16 시험 (이 작업 환경, TINY=1): CPU 쪽 `UNTIL=s2` → zip → 다른 폴더에서 풀고 실행 → s1 · s2 건너뜀, s3 ~ s9 통과.

## 2b. (선택) step2 와 같이 돌리는 추가 작업 — `step2b_extra.sh` (11-16 추가)
**step2 가 돌고 있어도 그대로 두고** 새 창에서 실행. 실행 중인 `step2_server_all.sh` · `scripts/gen_data_frame.sh` 파일은 덮어쓰지 말 것 (bash 는 실행 중에 파일을 이어서 읽음).
```bash
cd fp11          # step2 를 돌리는 그 폴더
# GitHub 에서 받은 handoff/step2b_extra.sh, scripts/eval_curve.py 두 파일만 이 폴더의 같은 위치에 복사 (새 파일이라 안전)
nohup bash handoff/step2b_extra.sh > step2b.out 2>&1 &
tail -f step2b.out
```
```
step2 :  s2 데이터(CPU) ──▶ s3·s5·s6 학습(GPU 3장) ──▶ s7·s8 ──▶ s9
step2b:     (기다림)    ──▶ ① 추가 데이터 5000(놀게 된 CPU)  ──────────▶ ③ FNO 약 1만(GPU 4번째) ─▶ ④ 채점 ─▶ ⑤
                            ② FNO 1000 · 2000 (GPU 4번째) ──┘
```
- 결과 `runs/curve/curve.md`: 데이터 1000 / 2000 / 5245 / 약 1만 개로 학습한 FNO 를 **같은 시험 셋**(추가 데이터 앞 4묶음 ≈ 600개, 어느 모델도 학습에 안 씀)으로 채점한 오차 표.
- 읽는 법: 5245 → 1만 에서 오차가 **아직 크게 줄면** 데이터가 모자란 것 → 1만 모델로 최적화를 다시 돌림 (아래). **거의 그대로면** 데이터 수는 충분.
- 1만 모델로 최적화 · FEM 검증 다시 하기 (step2 가 끝난 뒤):
```bash
python3 -m ai.latent_search --meta data/grid_meta.npz --sdf runs/sdf.pt --phys runs/curve/fno_big.pt --data 'data/shards_frame/*.npz' \
        --spec spec/bike_mount_targets.json --out runs/latent_big
mkdir -p runs/gate_big && cd runs/gate_big && for f in ../latent_big/cand_*.npy; do t=$(basename $f .npy); \
  GRIP=2 NX=88 MSYS=0.311 MODE=eval RHO=$(realpath $f) TAG=$t python3 ../../engine/opt_int.py | tail -1 & done; wait; cd ../..
```
- 시간(추정): ① 약 1시간 (CPU 몫 84 → JX=36), ② · ③ 은 GPU 1장에서 FNO 학습 3번 (1000 · 2000 은 동시에). step2 보다 1시간 안팎 늦게 끝날 것으로 봄 (미측정).
- 메모리: ① 36 × 0.94 GB ≈ 35 GB (재료 칸만 조립. 원래 방식 REDUCE=0 이면 36 × 4.1 GB ≈ 150 GB) + step2 학습. 720 GB 몫 안.
- 시간은 재료 칸만 조립으로 ① 이 약 1/10 로 줄 것으로 봄 (서버 미측정).
- 11-16 시험 (이 작업 환경, TINY=1): ①~⑤ 통과, 끊긴 뒤 이어하기 확인.

## 4. 정확도 올리기 실험 — `step4_improve.sh` (11-16 추가)
기존 실행 폴더(BASE, 예: `vcpu`)는 **읽기만** 하고 그대로 둔 채, 새 폴더에서 더 큰 설정으로 다시 학습 → 같은 시험 셋 · FEM 검증으로 비교 → 가장 좋은 조합을 자동으로 고름.
```bash
cp -r vcpu vimp && cd vimp && rm -rf runs data/shards_*         # 코드 사본 (또는 GitHub sosopapa 최신 패키지를 새로 풀기)
BASE=../vcpu nohup bash handoff/step4_improve.sh > step4.out 2>&1 &
# CPU 서버에서 데이터만 → GPU 서버에서 학습부터 (같은 공유 폴더, 11-16 추가):
#   [CPU] UNTIL=i2 BASE=../vcpu nohup bash handoff/step4_improve.sh > step4_cpu.out 2>&1 &   → '데이터까지 끝'
#   [GPU] BASE=../vcpu nohup bash handoff/step4_improve.sh > step4_gpu.out 2>&1 &            → i1 · i2 건너뛰고 i3 부터
#   데이터 연결은 상대 경로라 두 서버의 공유 폴더 위치가 달라도 됨. 단 BASE 는 두 번 다 같은 상대 경로로
bash handoff/step4_improve.sh status                              # 어디까지 끝났는지
cat runs/improve/report.md                                        # 끝나면: 비교표 · 선택
```

| 단계 | 하는 일 | 바뀐 점 (step2 대비) |
|---|---|---|
| i1 준비 | BASE 학습 데이터(5,269개) 연결, 열 연산자 저장 | 복사 안 함 (심볼릭 링크) |
| i2 데이터 | **추가 학습 데이터 5,000개**(씨앗 3001~) + **공통 시험 셋 600개**(씨앗 9001~), 둘 다 **충격 · 터치 변위 정답 포함** | 데이터 약 2배, 어느 모델도 안 본 시험 셋 |
| i3 학습 | GPU 4장에 동시: 형상 AI · FNO · **PINO(열)** · CNN · **PINO-S(열 + 구조)** | 스텝 2배(형상 AI 60,000 · 물리 AI 40,000), FNO 폭 24 → 32, 모드 (10,6,16) → (12,8,16), **모든 물리 AI 가 흔들림 · 층간 등 11개 추가 예측** |
| i4 확인 | 새 형상 AI 기준 구조 복원 IoU | |
| i5 채점 | BASE 의 CNN · FNO 와 새 CNN · FNO · PINO 를 **같은 시험 셋**으로 | 기준 근처(80–120 Hz) f1 오차 따로 |
| i6 최적화 | 조합 6개(새 형상 AI × 새 CNN/FNO/PINO/PINO-S, BASE 형상 AI × BASE FNO/CNN) 각각 후보 6개 | 반복 200 → 300, 추가값을 예측하는 모델은 **층간 응력 · 앞뒤 충격 · 아래 터치도 제약** |
| i7 검증 | 후보 36개 전부 FEM (원래 방식) | |
| i8 선택 | FEM 통과 → 가장 가벼움 → (0.5 g 이내면) 기준 근처 f1 오차 작은 쪽 | `runs/improve/report.md`, `best/` (sdf.pt · phys.pt · cand_best.npy · fem_best.json) |

- 설정(앞에 붙임): `WSTRUCT`(구조 물리 가중치 0.1) · `DISP_MAX`(변위 정답을 읽을 최대 형상 수 2000, 형상당 메모리 약 1.7 MB) · `NX`(추가 데이터, 기본 5000) · `NT`(시험 셋 600) · `NOX=1`(추가 데이터 없이) · `SDF_STEPS` · `PHYS_STEPS` · `FNO_W` · `FNO_MODES="12 8 16"` · `WPHYS`(PINO 물리 가중치 0.1) · `SDF_HID` · `GPUS` · `J`
- 시간(추정, 미측정): i2 약 10~15분(CPU, J 에 따라) · i3 가장 긴 형상 AI 약 40분~1시간(step2 의 2배 스텝) · i6 · i7 수십 분 이내.
- **keep 스크립트(GPU 유지용)를 같이 돌리지 말 것.** 11-16 step2 에서 같이 돌 때 형상 AI 학습이 멈춘 사례(CPU 사용 0, GPU 사용률은 keep 스크립트가 차지, 원인 추정: HAMi 사용량 제한).

### PINO (물리 정보 신경 연산자) — `ai/pino.py`
- **구조**: FNO 와 같은 몸통 + 온도를 절점 격자에 직접 예측하는 머리(요소 온도 = 8개 절점 평균, 학습 데이터 정의와 같음).
- **물리 손실**: 엔진 `thermal_T` 와 **같은 열전도 FEM 연산자**로 잔차 `K(r) T − q` (야코비 전처리, 온도 단위). 연산자는 `engine/opt_int.py MODE=thermops` 가 `data/thermal_ops.npz` 로 저장. FEM 정답 온도에서 잔차 상대값 **8 × 10⁻¹⁴** 확인(11-16) → 정답이면 0.
- 손실 = 데이터 손실(FNO 와 같음) + `WPHYS` × 물리 손실 (처음 2,000 스텝은 0 → 1 로 서서히).
- **PINO-S (`--struct`, 11-16 추가)**: 정적 구조 하중 4개(충격 위아래 · 앞뒤, 터치 위 · 아래)의 **절점 변위**를 직접 예측하고 엔진과 같은 hex8 강성으로 잔차 `K(r) u − f` 를 물리 손실로 씀(`engine/opt_int.py MODE=structops` → `data/struct_ops.npz`). FEM 정답(float64)에서 잔차 상대값 1e-11~1e-12 확인. float32 로 저장한 정답만 넣어도 약 1 % 남음(강성 행렬 상쇄) → 잔차는 float64 로 계산. 변위 정답은 하중별 최대값으로 나눠 float16 저장(`STORE_U=1`, 형상당 약 125 KB). **정답 변위가 없는 BASE 데이터도 물리 손실로 학습에 참여**, 변위 데이터 손실은 정답 있는 형상만.
- **흔들림(진동 응답)**: 모드 10개를 겹친 값이라 물리 손실 없이 **회귀(`--ext`)** 로만 학습 — 사용자 결정(11-16). 1차 진동수도 회귀.
- **한계**: PINO 물리 식은 **열 + 정적 구조(충격 · 터치)**. 진동수 · 흔들림은 데이터로만. f1 을 더 잘 맞힌다는 보장은 없음 — 그래서 FNO · CNN 과 같은 시험 셋 · FEM 검증으로 비교해서 고름. 열은 대류가 약해(받침판 · 폰) 잔차가 온도의 절대 수준보다 분포 모양을 주로 잡아 줌(추정).

## 5. 10 GUI(입력 단계 앱)에 학습 모델 붙이기 — `handoff/gui/carry_to_gui.py` (11-17 추가, 회사 PC · Windows)
새 GUI 를 ZIP 으로 받을 때마다 손으로 하던 일(모델 · 번역 결과 · 결과 DB 복사, Windows 버그 수정, 'DB 다 채움' 표시, 실행 파일)을 한 번에.
```
rem 1) 지금 쓰던 GUI 폴더 → 운반 폴더 (한 번)
"<기존>\.venv\Scripts\python.exe" carry_to_gui.py save  --gui "<기존>\10_입력_1차설계" --carry C:\work\fp_carry
rem 2) 새 GUI 폴더에 적용 (새로 받을 때마다)
"<기존>\.venv\Scripts\python.exe" carry_to_gui.py apply --gui "<새>\10_입력_1차설계"  --carry C:\work\fp_carry
rem 3) <새>\10_입력_1차설계\run_gui.bat 더블클릭  (run_gui.bat 20 → 찾아가기 20걸음, 기본 10)
```
- **cmd 에서 실행** (PowerShell 에서는 `set` 이 환경 설정이 안 되고, 따옴표 경로 실행에 `&` 가 필요). `run_gui.bat` 은 cmd 로 돎.
- `run_gui.bat` 은 **기존 .venv 의 python** 으로 GUI 를 띄움 → 새 폴더에서 `setup.bat`(PyTorch 재설치 · DB 채우기) 안 함. 기존 폴더는 지우지 말 것.
- 11-17 회사 PC 에서 겪은 문제와 대응
  - 뒤에서 결과 DB 를 채우는 작업(P01-opt)과 사용자 최적화 요청이 같이 멈춤(CPU 0 %) → 'DB 다 채움' 표시로 뒤 채우기를 끔.
  - `PermissionError … field_opt.npz` (WinError 32): `integral.fields()` 가 npz 를 닫지 않은 채 임시 폴더 삭제 → `with np.load(...)` 로 수정.
    **10 쪽 코드 버그 — 공동작업자에게 전달 필요** (feature/input-spec 은 우리가 push 하지 않음).
  - CPU 만 있는 PC 에서는 학습 모델 최적화가 매우 느림 (번역 1,500걸음이 1시간 넘게, 찾아가기 한 걸음 수십 초 추정) → 걸음 수를 줄이고(`FP11_ITERS`), 같은 기준으로 한 번 계산해 두면 다음부터 바로 재생.
- 이 작업 환경 확인 (11-17): 최신 feature/input-spec(6427773) 에 save → apply → 다시 apply. 복사 · 수정 · 표시 · 실행 파일 · 두 번째 적용 시 '이미 고쳐져 있음', 고친 integral.py 문법 OK. 회사 PC(Windows)에서 직접 실행은 미확인.

## 3. 회사 PC: 결과 보기
서버의 `fp11/results_fp11.zip` 을 회사 PC 의 `FormProof_구현` 폴더에 복사한 뒤 `handoff\step3_pc_view.bat` 를 더블클릭 → `runs\report.html` 이 열림.
- 결과 묶음에는 학습 데이터(수 GB)를 넣지 않음. 대신 서버에서 데이터 통계까지 넣어 만든 `runs/report.html` 이 들어 있고, step3 는 그것을 그대로 엶.
- 묶음 안: 요약, 학습된 모델(`*.pt`), 학습 기록(`*.json`), 최적화 후보(`cand_*.npy`), FEM 검증 결과, 단계별 기록(log). 11-16 시험 실행 기준 약 11 MB.

## 11-16 시험 실행 (이 작업 환경, CPU 2코어 · 메모리 7 GB, TINY=1)
- GPU 4장 흉내(nvidia-smi 대신 가짜 스크립트, 실제 계산은 CPU)로 동시 학습 확인: 여유 3 GB 인 GPU 는 빠지고 3장에 나눠 동시 시작, 끝난 뒤 최적화로 이어짐.
- s0 ~ s9 전부 통과. 중간에 끊긴 뒤 다시 실행했을 때 끝난 단계는 건너뛰는 것까지 확인.
- 시험이라 데이터가 4개뿐이어서 학습 결과 숫자(IoU 0.10, 오차 수백 %)는 의미 없음. 흐름이 끝까지 도는지만 본 것.

## 주의 (아직 안 된 것)
- 물리 AI 는 **값 맞추기(회귀)** 학습이고, 물리 식을 손실에 넣는 PINO 는 아님.
- s5 ~ s7 은 기존 11 패키지 학습 코드를 그대로 씀. 그래서 이번에 새로 만든 **흔들림 · 층간 값(lab_ext)** 과 **열 전용 데이터(B)** 는 데이터로 만들어만 두고 학습에는 아직 안 씀 → 다음 작업.
- 최적화(s7)는 형상 AI 잠재 공간 방식. 형상 생성기 변수로 직접 최적화하는 방식과의 비교도 다음 작업.
- s4 의 기준 구조는 학습에 포함된 형상이라, 처음 보는 형상을 얼마나 잘 그리는지 보는 시험은 아님.
