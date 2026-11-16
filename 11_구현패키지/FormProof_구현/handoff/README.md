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
  - `J`: 병렬 수. 기본 = min(여유 메모리 GB ÷ 4.5, 빈 코어 ÷ 2). 빈 코어 = 허용 코어 − 1분 평균 부하. 시작할 때 예상 시간도 출력 FEM 1개당 메모리 약 4.1 GB (11-16 측정)
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
| s2 A | 형상 1개 FEM 약 30초 (2코어, 11-16 측정) × 5,245 ÷ J | 약 1.5시간 |
| s2 B | 판 패턴 1개 약 0.25초 | 몇 분 |
| s3 ~ s6 | GPU 학습 (08 경험상 각 수십 분). GPU 3장 이상이면 동시에 | 차례로 1 ~ 2시간 → 동시에 가장 긴 하나만큼 (미측정) |
| s7 · s8 | 후보 6개 × FEM | 수 분 |

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
