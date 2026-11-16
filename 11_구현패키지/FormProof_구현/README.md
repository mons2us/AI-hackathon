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
| `engine/` | `opt_int.py` 위상 최적화 · FEM(진동 · 충격 · 터치) · 열, 학습 데이터 생성, 평가. `gen_int.py` 형상 생성기. **`gen_frame.py` 프레임 형상 생성기(계열 7 × 연속 변수, 11-16 추가)** | ② · ③ |
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

기준 결과(해커톤 최종): `scripts/run_reference.sh` — 설정은 `FT=95 TLIM=21 DLIM=0.3 ITERS=120 RF=8 ETAE=0.7 SCHED={0:1,20:2,40:4,60:8,80:16,100:32}`.

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
- 해커톤 최종 형상(`data/reference/rbin_int35f95g2.npy`)을 만든 실행과 지금 코드는 고정 부품 정의가 조금 달라 첫 반복 무게가 다르다(559.4 → 550.9 g). 지금 코드 기준 재현값은 `scripts/run_reference.sh` 결과를 기준으로 삼는다.
- 층간 강도 한계 10.9 MPa, 폰 발열 4 W, 감쇠비 3 %, 터치 5 N 은 가정값 — 근거 DB 에 출처 확정 필요.
- `pypardiso` 는 x86_64 전용. 다른 CPU 는 `scipy.sparse.linalg.splu` 로 교체.
- 학습 코드의 성능(오차 · IoU)은 GPU 학습으로 확인해야 한다. 이 패키지에서는 CPU 소규모로 끝까지 도는 것만 확인했다.

## 7. 프레임 형상 생성기 `engine/gen_frame.py` (11-16 추가, sosopapa)
- 목적: 형상 생성기 → FEM 종류별 정답 → 물리 AI(PINO) → 최적 설계, 이어서 형상 AI(DeepSDF 등)와 비교. 형상이 덩어리가 아니라 **제품 같은 프레임**이 되도록 규칙 + 연속 변수로 만듦
- 계열 7: 곧은 팔 · 트러스 · V자 · 아치(구스넥) · 척추 · Y자 · 판형. 단면 4: 사각 · 둥근 관 · 양옆 벽(ㄷ자) · I자. 두께 t 5–12 mm, 반폭 w 5–14 mm, 보조 부재 배율, 보강 웹 0–2
- 폰 잡는 방식 `GRIP` 0/1/2 마다 몸체가 이을 곳(판 가운데 · 아래 끝 · 위 끝)을 바꿈. 유효성: 링과 세 곳이 한 덩어리
- 변수 사전(`prm`)으로 같은 형상 재현 가능(`build`) → 변수 최적화 · 형상 AI 비교에 사용
- 확인 (CPU 2코어): 98개 생성 2 s, 7계열 모두 유효. FEM(`MODE=label2`) 형상당 약 22 s. GRIP 2 계열별 1개: f1 12–97 Hz(트러스 97 Hz 만 ≥ 95), 터치 0.09–6.1 mm, 충격 응력 4–44 MPa
- 열: 열 해석 영역이 받침판 + 폰뿐이라 판 아래 몸체(팔)는 폰 온도에 영향 없음(처음 7개 모두 20.654 °C) → **받침판 채움 패턴 변수 추가**: 판 없음 · 꽉 찬 판 · 리브 · 구멍 · 테두리+십자 · 띠 × 층 1–3 × 크기
- 같은 트러스 몸체 + 판 패턴 11가지 FEM (GRIP 2): 폰 온도 상승 20.7–37.5 °C, 질량 67–142 g, f1 39–48 Hz, 터치 0.34–0.59 mm
  - 판이 많을수록 터치·f1 은 좋아지지만 **온도는 나빠짐**(PETG 0.2 W/mK 가 단열재처럼 폰 뒷면 공기 냉각을 막음): 판 없음 20.7 °C, 꽉 찬 판 1층 37.5 °C(기준 21 초과), 3층 24.5 °C → 열 · 강성 맞교환이 생겨 학습 · 최적화 의미 있음
- 클램프: 볼트 링 하나로 고정 (opt_int.py 와 같음)
- 미리보기: `engine/gen_frame_preview.png` (계열 7 × 7개)
