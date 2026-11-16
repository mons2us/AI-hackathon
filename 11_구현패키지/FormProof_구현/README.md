# FormProof 구현 패키지

말 · 스케치 요청 → **① 설계 명세(물리 조건)** → **② 역설계(형상 AI × 물리 AI → 위상 최적화)** → CAD 결합 → **③ 검증 관문(출력 형상 재계산)** → 제작 파일.
해커톤 사례(일체형 자전거 폰 거치대)를 그대로 재현하고, 이어서 구현할 수 있게 정리한 패키지다. 원리 · 설계 결정 · 실패 기록 · 과제 분담은 **구현 가이드(HTML)** 를 본다.

## 1. 시작하기 (CPU, 10분)
```bash
pip install -r requirements.txt            # 계산 엔진
pip install -r requirements_gpu.txt        # 학습 (GPU 장비)
pytest -q tests                            # 빠른 테스트 (격자 · 데이터 생성 1개 · 학습 코드 동작)
RUN_SLOW=1 pytest -q tests                 # 기준 결과와 숫자 비교 (FEM 재계산, 약 10분)
```

## 2. 폴더
| 폴더 | 내용 | 프레임워크 단계 |
|---|---|---|
| `spec/` | 설계 명세 형식(schema), 거치대 명세 예시, 판정 기준(targets), 근거 DB | ① |
| `agent/` | LLM 교체 인터페이스, 조건 생성기, 단계 실행기(검증 실패 시 재설계 루프) | 에이전트 · ① |
| `engine/` | `opt_int.py` 위상 최적화 · FEM(진동 · 충격 · 터치) · 열, 학습 데이터 생성, 평가. `gen_int.py` 형상 생성기 | ② · ③ |
| `ai/` | `deepsdf.py` 형상 AI, `surrogate.py` 물리 AI(CNN · FNO), `latent_search.py` 잠재 공간 역설계 (PyTorch, GPU). `reference_jax/` 해커톤 원본(분리형) | ② |
| `cad/` | 고정 부품(`parts.py`), 최적화 형상 + 부품 결합 → 출력 STL(`build_body.py`), STL → 계산 격자(`vox.py`) | CAD 결합 |
| `drawing/` | 부품도 · 조립도 | 제작 파일 |
| `data/` | 격자 정보, 위상 최적화 기록 245개, 기준 결과(`reference/`) | — |
| `scripts/` | 데이터 생성 · GPU 학습 · 기준 결과 재현 | — |
| `tests/` | 기준값 회귀 테스트 | — |

## 3. 엔진 실행 (환경 변수로 설정)
공통: `GRIP=2 NX=88 MSYS=0.311` (폰 4면 고정 부품 포함 · 2 mm 격자 88×20×37 · 폰 + 고정 부품 311 g)

| MODE | 하는 일 | 주요 변수 | 출력 |
|---|---|---|---|
| (기본) `opt` | 위상 최적화: 무게 최소, f1..f4 ≥ FT, 폰 온도 ≤ TLIM, 터치 ≤ DLIM, 출력(적층) 필터 | `FT TLIM DLIM ITERS SCHED RF ETAE TAG START_RHO` | `rprint_TAG.npy`, `snap_TAG_*.npy`, 로그(json 줄) |
| `eval` | 형상 평가: 진동 전달(10–100 Hz) · 고유진동수 · 충격 응력 · 층간 · 터치 · 온도 · 무게 | `RHO TAG` | `frfint_TAG.json` |
| `field` | 분포: 흔들림 RMS · 충격 응력 · 온도 · 1차 모드 | `RHO TAG FF` | `field_TAG.npz` |
| `meta` | 학습 코드용 격자 정보 | `OUT` | `grid_meta.npz` |
| `label2` | 학습 데이터: 형상 → 스칼라 7개 + 분포 2개 | `NS SEED` 또는 `SRC(I0,I1)` · `OUT` | 샤드 `.npz` |

기준 결과(해커톤 최종): `scripts/run_reference.sh` — 설정은 `FT=95 TLIM=21 DLIM=0.3 ITERS=120 RF=5 ETAE=0.6 SCHED={0:1,20:2,40:4,60:8,80:16,100:32}` (MSYS 기본값). 결과는 실패 사례: 최적화 값은 80.0 g · f1 94.7 Hz였지만 중간 밀도가 강성을 대신해, 0.5로 자른 실제 형상은 끊겨 있고 재계산 f1 25.9 Hz로 불합격(아래 '알려진 차이'). 검증 관문에 연결성 · 중간 밀도 비율 판정을 추가함.

## 4. 학습 (GPU)
```bash
scripts/gen_data.sh 8 250      # CPU 8프로세스 × 250 = 생성기 2,000개 + 위상 최적화 기록 245개 (메모리 프로세스당 약 2 GB)
scripts/train_gpu.sh           # DeepSDF → (통과 기준) 최종 구조 복원 IoU ≥ 0.8 → CNN · FNO → 잠재 탐색 → FEM 검증
```
- **형상 생성기 ≠ 형상 AI**: 생성기는 학습용 형상을 규칙으로 만드는 프로그램, DeepSDF 는 그 형상들을 잠재 변수로 배우는 신경망(미분 가능).
- 생성기 형상만으로는 최종 구조를 표현 못 함(가장 가까운 IoU 0.14) → 위상 최적화 기록을 반드시 함께 학습.
- 물리 AI 인터페이스 `Surrogate.predict(occ) -> scalars, fields` 는 고정. 모델(CNN · FNO · 이후 GINO)은 바꿔 끼운다.

## 5. 에이전트
```bash
LLM_KIND=openai LLM_BASE_URL=http://<사내 LLM> LLM_MODEL=<모델> python3 agent/condition_generator.py "울퉁불퉁한 길에서도 안 흔들리게, 가볍게. 3D 프린터로" "핸들바 스템 옆, 35°"
python3 agent/pipeline.py --spec spec/bike_mount_targets.json --run runs/r1      # 최적화 → CAD → 재격자화 → 검증 관문 (불합격 시 목표 조여 재설계)
```

## 6. 알려진 한계 · 확인 필요
- 해커톤 최종 형상(`data/reference/rbin_int35f95g2.npy`)을 만든 실행과 지금 코드는 고정 부품 정의가 조금 달라 첫 반복 무게가 다르다(559.4 → 550.9 g). RF=8 · ETAE=0.7 설정은 118.4 g · f1 43.3 Hz(IoU 0.565)로 발산했고, RF=5 · ETAE=0.6은 최적화 값 80.0 g · 94.7 Hz였으나 중간 밀도 요소 2,614개가 남아 실제 형상(0.5 기준)은 끊기고 재계산 f1 25.9 Hz · 터치 1.54 mm로 불합격했다. 원본 형상이 필요하면 `data/reference/` 파일을 그대로 쓴다.
- 층간 강도 한계 10.9 MPa, 폰 발열 4 W, 감쇠비 3 %, 터치 5 N 은 가정값 — 근거 DB 에 출처 확정 필요.
- `pypardiso` 는 x86_64 전용. 다른 CPU 는 `scipy.sparse.linalg.splu` 로 교체.
- 학습 코드의 성능(오차 · IoU)은 GPU 학습으로 확인해야 한다. 이 패키지에서는 CPU 소규모로 끝까지 도는 것만 확인했다.

## GPU 인계 (2026-11-16)
- 학습 데이터 준비 완료: `data/shards/` — 생성기 형상 160개(gen_s1001 · gen_s1002) + 위상 최적화 이력 122개(snap_half), 형상당 스칼라 7개 + 온도 · 응력 분포. 같은 FEM 엔진(label2)으로 계산.
- 바로 실행: `bash scripts/train_gpu.sh` (형상 AI → 물리 AI(CNN 기준선 · FNO) → 잠재 탐색 → 검증 관문).
- CPU 시험 결과(참고): DeepSDF 2,000회(CPU 2코어 약 1.8시간)에서 학습 형상 재구성 IoU 0.50 — 합격 기준 0.8 미달, 실행 시간 제한으로 중단. `runs_cpu/stageC.log` 참조.
- 데이터 확대가 필요하면 `scripts/gen_data.sh` 로 생성기 형상을 추가(목표 2,000개). label2 프로세스 1개 ≈ 3 GB 메모리.
- DeepSDF 학습은 1,000회마다 중간 저장.
