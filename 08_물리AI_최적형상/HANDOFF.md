# HANDOFF — 08 물리AI 최적형상: 회사 PC + GPU 서버 작업 지시서

> **Cline(또는 다른 LLM)에게**: 이 파일 하나만 읽으면 작업을 이어갈 수 있도록 썼습니다.
> 순서대로 읽고, **§2 규칙**을 꼭 지키세요. 모르는 것은 추측하지 말고 사용자에게 물어보세요.
> 작성: 2026-11-14 (Claude). 담당: 소소파파 (08 물리 엔진/물리 AI). 브랜치: **sosopapa** 만 사용.

---

## 0. 한 줄 요약

**설계 공간 안의 무작위 형상 → FEM 정답 → DeepSDF(형상 압축, 그룹 6개)·PINO(물리 예측, 제품 3개) 학습 → 품질 관문 → 잠재벡터 z 최적화 → FEM 검증 → 최적 형상(STL)**
코드는 다 있고 **CPU 리허설로 끝까지 도는 것까지 확인**했습니다. 남은 일은 **GPU 서버에서 본 학습**과 **결과 확인·시연**입니다.

---

## 1. 작업 환경 (내일 조건)

| 기계 | 할 수 있는 것 | 못 하는 것 |
|---|---|---|
| **회사 PC** (Windows, GPU 없음) | Cline 사용, 코드 수정, zip 만들기/풀기, 시연(`fp08.demo`, CPU 로 그룹당 수 분), 결과 보기 | GPU 학습, Claude 사용 |
| **GPU 서버** | 학습 (`step3_server_train.sh`), CPU 코어가 많으면 데이터 생성까지 | Cline 없음(가정). 인터넷 없을 수 있음 |

```
 [회사 PC]                                   [GPU 서버]
  ① (계획 B) 데이터 생성 step1  ─┐
  ② zip 만들기 step2 ────────────┼─ 업로드 ─▶ ③ 학습 step3 (A: 데이터부터 / B: 학습부터)
                                 │                │  results.zip
  ④ 시연 step4  ◀── 다운로드 ─────┴────────────────┘
     (최적화+FEM 검증+STL+summary.html)
```

- **계획 A (권장)**: 서버 CPU 코어가 많으면(≥16) 데이터 생성도 서버에서. 회사 PC 는 코드 zip 만 올림 → 업로드 용량 0.1 MB.
- **계획 B**: 서버에서 FEM 이 안 되면(패키지·CPU 부족) 회사 PC 에서 `step1` 로 데이터를 만들어 `upload_data.zip`(수 GB 가능)을 올림.
- 데이터는 **시드 고정**(`shapes.seed_of(group, idx)`) → 어디서 만들어도 같은 형상. 그래서 데이터를 옮기는 대신 **다시 만들어도 됩니다.**

---

## 2. 규칙 (꼭 지킬 것)

1. Git push 는 **`sosopapa` 브랜치에만**. main·다른 사람 브랜치 금지.
2. 커밋 메시지에 **변경 포인트**를 목록으로 (무엇을/왜/영향 범위). 예시는 §9.
3. **물리 상수·하중 조건·판정 기준**(`fp08/problems.py`의 재료값, 하중, 허용응력, `loop.py`의 `GATE`, `DEMO`)은 **사용자 확인 없이 바꾸지 말 것**. 10 담당(공동 작업자)과 맞춘 값입니다.
4. 확인 안 된 수치를 사실처럼 쓰지 말 것. 이 문서의 시간은 대부분 **추정**이라고 표시했습니다.
5. 학습이 끊겨도 **같은 명령을 다시 실행**하면 `runs/main/state.json`·`ckpt.pt` 로 이어집니다. 폴더를 지우고 처음부터 하지 말 것.
6. 실패하면 **로그 마지막 30줄**(`runs/main/*.log`, `runs_main.out`)을 먼저 읽고 §8 표를 보고 대응.

---

## 3. 현재 상태 (2026-11-14 기준, 사실만)

| 항목 | 상태 | 근거 |
|---|---|---|
| 6개 그룹 문제 정의 | ✅ | `fp08/problems.py` `GROUPS` |
| 형상 생성: 후보 12,000 → 거름 → 5,000/그룹 | ✅ CPU 확인 | `data3/<그룹>/selection.json` (예: bike_pad80 거친 것 1,075·끝 뾰족 261 제외) |
| ESO 다듬기(약한 칸 15% × 2회 삭제) | ✅ 20개 시험: 질량 중앙값 −20%, 최저 진동수 −4% | `docs/groups/eso_*` |
| FEM 정답 생성 | ✅ 거치대 80 1,000개 (CPU 2코어 약 14분) | `dg1k.log` |
| DeepSDF | ⚠ CPU 6,000 스텝까지만: IoU_val 0.76 (bike_pad80), 0.73 (tvped). **목표 미달** | `sdf1/` |
| DeepSDF 크기 비교 (1,000형상, 3,000스텝) | 8층×256 > 4층×128, 푸리에 특징은 오히려 나쁨 → **8×256 채택, 푸리에 미사용** | §아래 표 |
| PINO | ⚠ CPU 시험 학습만 (값 의미 없음). 본 학습 필요 | `train_pino.py` |
| 시연 파이프라인 (최적화→FEM 검증→STL→summary.html) | ✅ 시험 모델로 끝까지 동작 확인 (bike_pad80, 42초) | `fp08/demo.py` |

DeepSDF 크기 비교 (bike_pad80, 형상 1,000개, 3,000스텝, CPU):

| 모델 | IoU | 표면 오차 |
|---|---|---|
| 4층×128 | 0.70 | 0.72 mm |
| **8층×256** | **0.73** | **0.63 mm** |
| 4층×128 + 푸리에 | 0.63 | 0.69 mm |
| 8층×256 + 푸리에 | 0.65 | 0.69 mm |

→ 전부 아직 오르는 중이었음 = **더 오래 학습(20,000 스텝 이상)이 핵심.** GPU 에서 해결할 부분.

---

## 4. 파일 지도 (`08_물리AI_최적형상/`)

| 경로 | 역할 |
|---|---|
| `HANDOFF.md` | **이 문서** |
| `handoff/step1_pc_datagen.bat` | [회사 PC] 데이터 생성 (계획 B) |
| `handoff/step2_pack_upload.bat` | [회사 PC] 업로드용 zip |
| `handoff/step3_server_train.sh` | [서버] 학습 전체 (GPU 자동 감지) |
| `handoff/step4_pc_demo.bat` | [회사 PC] 결과 풀기 + 시연 |
| `requirements.txt` | 패키지 목록 (오프라인 설치 방법 포함) |
| `fp08/problems.py` | 6개 그룹: 격자·고정부품·하중·판정 기준 (**함부로 수정 금지**) |
| `fp08/fem.py` | 3D 육면체 FEM (정적 + 고유진동수) |
| `fp08/shapes.py` | 무작위 형상 생성기 (가족 A~E, 자동 대칭, 정리) |
| `fp08/eso.py` | ESO: 변형에너지 낮은 칸 삭제 |
| `fp08/datagen.py` | 후보 생성→선택→ESO→FEM 정답 저장 |
| `fp08/models.py` | DeepSDF, PINO(FNO3d) |
| `fp08/train_sdf.py` / `train_pino.py` | 학습 |
| `fp08/loop.py` | 전체 흐름 자동화 (단계·관문·능동학습·시연, `state.json`·`report.html`) |
| `fp08/design_opt.py` | z 최적화 (증강 라그랑주 + Adam) + FEM 검증 |
| `fp08/demo.py` | 시연: JSON·PNG·STL·summary.html |
| `fp08/sweep.py` | 학습 방법 후보·점수 계산·선택 (후보는 여기만 고치면 됨) |
| `diag_eso.bat` / `diag_eso.py` | Windows 에서 ESO·FEM 속도 진단 |
| `fp08/pack.py` | zip 묶기/풀기, `check`(데이터 개수), `report`(학습 결과 요약) |
| `docs/DeepSDF_study.html` | DeepSDF 공부 자료 (그림) |
| `RUN_MONDAY.md` | 서버 1대에서 전부 돌릴 때의 원래 계획서 |

6개 그룹: `bike_pad50`, `bike_pad80`, `bike_pad120` (자전거 거치대, 2 mm 격자) · `tvfeet_L300`, `tvfeet_L220` (TV 양발, 2.5 mm) · `tvped` (TV 중앙 스탠드, 5 mm). 제품 3개: `bike`, `tvfeet`, `tvped` (PINO 는 제품별).

---

## 5. 단계별 실행

### 준비 (회사 PC, 한 번)
1. 코드 받기 (회사 PC 는 GitHub 접속 가능 확인됨, 2026-11-14): `git clone -b sosopapa https://github.com/mons2us/AI-hackathon.git` → `cd AI-hackathon/08_물리AI_최적형상`
   이미 받아 둔 경우 `git pull origin sosopapa`. **GitHub 이 기준**이며, 다운로드 폴더의 zip·md 사본은 예비용(옛날 판일 수 있음).
   bat 파일은 `.gitattributes` 로 CRLF 줄끝이 유지됨 → cmd 에서 그대로 실행. (LF 로 바뀌면 `'THREADS'은(는) 내부 또는 외부 명령…` 같은 오류가 남)
2. 파이썬 패키지: `pip install -r requirements.txt` (인터넷 없으면 파일 맨 위 주석의 오프라인 방법).
3. 확인: `python -m fp08.loop --help` 가 에러 없이 나오면 OK.

### ① [회사 PC] 데이터 생성 — 계획 B 일 때만
- 실행: `handoff\step1_pc_datagen.bat`
- 시간(추정): 형상 6그룹 수십 분 + FEM 6,000개 1~3시간 (8코어 기준, TV 그룹이 더 느림). **실측 아님.**
- 성공: 마지막 표에서 6그룹 모두 `형상 5000`, `FEM 1000` 근처 (ESO 열 2,500 근처, ESO FEM 열 500 근처. 끊긴 형상·FEM 실패는 빠져서 조금 적을 수 있음).
- 끊기면: 그냥 다시 실행.

### ② [회사 PC] 업로드 파일 만들기
- 실행: `handoff\step2_pack_upload.bat` → `upload_code.zip` (+ 계획 B 면 `upload_data.zip`)
- 서버로 업로드 (회사 규정에 맞는 방법으로).

### ③ [GPU 서버] 학습
```bash
mkdir fp08run && cd fp08run && unzip ../upload_code.zip
pip install -r requirements.txt            # CUDA 판 torch 는 서버에 이미 있는 것 사용 권장
nohup bash handoff/step3_server_train.sh A > train.out 2>&1 &   # 계획 B 면 A 대신 B (upload_data.zip 을 같은 폴더에)
tail -f train.out                           # 진행 보기
python -m fp08.pack report runs/main        # 중간 결과 요약 (언제든)
```
- 하는 일: (A면 형상·FEM 생성) → **학습 방법 고르기(sweep)** → DeepSDF 6개(20,000스텝) → PINO 3개(30,000스텝) → 관문 → 불합격 그룹은 능동학습(200개 FEM 추가, 최대 3바퀴) → 시연.
- **sweep (기본 켜짐)**: `fp08/sweep.py` 의 후보 4개(DeepSDF: 8×256 / 8×512 / 표면점 2048 / z 64차원, PINO: 폭 24 / 폭 32 / 물리가중 0.3 / 푸리에 모드 1.5배)를 20% 스텝만 학습 → **검증 셋** 점수 1등만 끝까지 → `runs/main/sdf|pino/` 로 복사. GPU 시간 약 1.6배(추정). 끄려면 `SWEEP= bash handoff/step3_server_train.sh A`
- 데이터 분할(형상 번호로 고정): 학습 80% / 검증 10%(학습 중 확인·sweep 선택) / **시험 10%(관문·최종 보고 전용, 고르는 데 안 씀)**
- GPU 가 1~2장이어도 동작 (한 장에 작업 여러 개 동시 실행).
- 시간(추정, 미측정): DeepSDF 그룹당 GPU 수십 분, PINO 제품당 수 시간. **처음 10분 동안 `runs/main/sdf_*.log` 의 step 속도를 보고 전체 시간을 다시 계산할 것.**
- 끝나면 `results.zip` 생성 → 회사 PC 로 다운로드.
- 시간이 모자라면: `--sdf-steps 10000 --pino-steps 15000` 으로 줄이거나, `loop.py` 의 `--deadline "YYYY-MM-DD HH:MM"` 옵션 (마감 3시간 전 능동학습 중단).

### ④ [회사 PC] 시연
- `results.zip` 을 코드 최상위 폴더에 두고 `handoff\step4_pc_demo.bat`
- 결과: `results\summary.html` (표 + 그림), `results\<그룹>_<조건>.stl` (CAD/3D 뷰어로 열기), `.json` (FEM 판정값).
- 특정 조건만: `python -m fp08.demo --run runs\main --data data --out results --groups bike_pad80 --cond phone_mass_g=180,phone_angle_deg=10`
- 그룹당 CPU 수 분 (시험: bike_pad80 시작점 2개·30스텝에 42초. 기본값 10개·300스텝은 더 오래).

---

## 6. 성공 판단 기준

| 대상 | 기준 | 상태 |
|---|---|---|
| PINO (코드에 들어있음, `loop.py GATE`, **시험 셋**으로 판정) | 변위장 상대 L2 평균 ≤ 0.10, 판정값 오차 p90 ≤ 5%, 응력 오차 p90 ≤ 15%, 진동수 ±5% 이내 ≥ 95% | 자동 판정 |
| DeepSDF | 시험 셋 IoU ≥ 0.90, 표면 오차 ≤ 0.5칸 (`state.json` 의 `sdf_test`, `report.html`) | **제안값, 사용자 미확정. 코드에서 자동 판정 안 함** → `pack report` 로 눈으로 확인 |
| 최종 시연 | `status: ok` (대리 모델 결과가 FEM 검증 합격). `fallback` = 후보가 전부 FEM 검증에 떨어졌다는 **표시만** 함 — FEM 직접 최적화(경로 A)를 자동으로 돌리지는 않음(미구현). 그 경우 팀 `opt3d.py`·`ped.py` 결과를 수동으로 사용 | 자동 판정 |

DeepSDF IoU 가 0.90 에 못 미치면: 스텝을 늘려 이어서 학습 (ckpt 에서 이어짐, 크기 옵션은 꼭 같게):
`python -m fp08.train_sdf --group <그룹> --data data --out runs/main --steps 40000 --width 256 --depth 8 --n-eval 30 --device cuda:0`

그래도 안 되면 사용자에게 보고하고 지시를 받을 것.

### 6-1. 학습이 잘 안 됐을 때 — 대응 사다리 (1번 대응: 학습을 개선)

`python -m fp08.pack report runs/main` 맨 아래 **"권장 조치"** 가 아래 표에서 무엇을 할지 알려 줍니다(규칙 기반, 참고용).
모든 조치는 **숫자만 키워 같은 스크립트를 다시 실행**하면 됩니다. 이미 만든 데이터·모델은 버리지 않고 모자란 만큼만 추가하고 이어서 학습합니다.

```
 DeepSDF 시험 IoU < 0.90 ?                     PINO 관문 불합격 ?
   │ 아직 오르는 중 → S1 더 오래                  │ P1 능동학습 (자동, 최대 3바퀴)
   │ 멈춤          → S2 큰 모델 (sweep)          │ P2 FEM 정답 늘리기 (+ESO 정답)
   │ 그래도 미달   → S3 시연 FEM 검증으로 판단    │ P3 형상 늘리기
   ▼                                             ▼ 그래도 불합격 → 2번 대응(FEM 직접 최적화, 별도 준비)
```

| 단계 | 언제 | 실행 (서버) | 추가 비용 (추정) | 왜 효과가 있나 |
|---|---|---|---|---|
| **S1** DeepSDF 더 오래 | IoU 가 마지막 평가까지 오르는 중 | `SDF_STEPS=40000 bash handoff/step3_server_train.sh A` | 학습 시간 2배 | 11-14 비교에서 모든 설정이 아직 오르는 중이었음 |
| **S2** DeepSDF 큰 모델 | IoU 가 멈춤 | sweep 후보에 8×512, z 64차원이 이미 있음. 2등까지 끝까지: `SWEEP="--sweep --sweep-topk 2"` | 약 1.5배 | 형상 7,500개를 32차원·256폭으로 다 못 담을 수 있음 |
| **S3** 그대로 진행 | S1·S2 후에도 0.90 미달 | 시연(`demo`) 결과가 `ok` 인지 확인 | 없음 | 최종 형상은 DeepSDF 가 **만든** 형상을 FEM 으로 직접 검증하므로, 복원이 완벽하지 않아도 결과는 틀리지 않음(표현 가능한 형상의 폭만 줄어듦) |
| **P1** 능동학습 | 관문 불합격 | 자동 (틀리는 형상 100 + 최적화 후보 100 개에 FEM 정답 추가 → 재학습, 최대 3바퀴) | 바퀴당 FEM 200개/그룹 + 학습 1/3 | 틀리는 곳·최적화가 가는 곳에 정답 집중 |
| **P2** FEM 정답 늘리기 | P1 후에도 불합격 | `N_FEM=2000 bash handoff/step3_server_train.sh A` (3000 까지) | FEM 1,000개 + ESO 500개 ≈ 그룹당 40분·코어(형상당 약 1.5 s, TV 는 더 김) + PINO 학습 1/3 | PINO 는 정답 수에 가장 민감 (리허설: 100개 과적합, 1,000개에서 모양 오차 16%) |
| **P3** 형상 늘리기 | P2 후에도 불합격 | `N_SHAPES=8000 bash handoff/step3_server_train.sh A` (후보 여유상 약 10,000 까지) | 형상·ESO 생성 + DeepSDF 다시 학습(이전 모델 이어받음) | 정답 없는 형상의 물리 손실 데이터와 z 공간 범위가 넓어짐 |

주의
- **형상 수를 늘린다고 DeepSDF IoU 가 오르지는 않습니다.** 같은 크기 모델이 더 많은 형상을 외워야 해서 오히려 어려워집니다. DeepSDF 는 S1·S2 로, 형상 늘리기(P3)는 PINO·최적화 범위를 위한 것.
- ESO 정답: `--eso` 가 켜져 있으면 FEM 정답 형상의 절반에 대해 **깎은 뒤 형상의 정답**도 만듭니다(`femeso_*.npz`, 조건은 부모와 동일). N_FEM 을 늘리면 같이 늘어남.
- 계획 B(데이터를 회사 PC 에서 생성)면 P2·P3 는 회사 PC 에서 `step1` 을 숫자 키워 다시 실행 → 데이터 다시 업로드.
- 관문 기준(`GATE`)을 낮추는 것은 대응이 아닙니다. 사용자 결정 사항.

---

## 7. 아직 사용자가 정하지 않은 것 (임의로 정하지 말 것)

- DeepSDF 관문 기준 (§6 제안값 확정 여부)
- TV 발 높이 (120 mm 또는 더 낮게), 두 번째 발 길이 (260 / 340 mm)
- TV 패드 들림(uplift) 처리 방식
- FEM 정답 개수 (지금 1,000/그룹)

---

## 8. 문제 해결

| 증상 | 원인 | 대응 |
|---|---|---|
| `ModuleNotFoundError: pypardiso` 경고 | ARM·인텔 MKL 없음 | 무시 가능. SuperLU 로 자동 대체 (결과 같음) |
| `GPU 가 안 보입니다` | CPU 판 torch / 드라이버 | `nvidia-smi`, `python -c "import torch;print(torch.cuda.is_available())"` |
| `CUDA out of memory` | 한 GPU 에 작업 너무 많음 | `step3` 의 `DEV="$DEV,$DEV,$DEV"` 를 `DEV="$DEV,$DEV"` 로, 또는 `--bs` 줄이기 |
| 학습이 중간에 죽음 | 세션 끊김 | `nohup` 으로 실행했는지 확인, 같은 명령 재실행 (이어짐) |
| 관문 계속 불합격 | 데이터 부족/학습 부족 | `pack report` 의 불합격 사유 확인 → 사용자 보고. 기준(GATE)을 낮추지 말 것 |
| 시연 `fallback` | 대리 모델 후보가 전부 FEM 검증 실패 | 표시만 됨(자동 대체 없음). §6-1 사다리로 모델 개선 또는 팀 FEM 직접 최적화 결과를 수동 사용. summary 에 그대로 보고 |
| `torch.load` 에러 `weights_only` | torch 버전 차이 | 코드가 `weights_only=False` 사용 중. torch ≥ 2.1 사용 |
| Windows 에서 한글 깨짐 | 콘솔 코드페이지 | bat 첫 줄 `chcp 65001` 유지 |
| bat 실행 시 `'cho'`, `'THREADS'` 등 조각난 명령 오류 | bat 줄끝이 LF | 편집기에서 CRLF 로 저장 (VS Code 오른쪽 아래 LF→CRLF) |
| Windows 에서 ESO·FEM 이 매우 느림 (작업자 CPU 2~3%) | **Windows 의 pypardiso 가 SuperLU 보다 20~40배 느림** (11-14 실측: 형상당 17~43 s vs 0.6~2.7 s) | 코드가 Windows 에서는 자동으로 SuperLU 사용 (`fp08/fem.py`). 강제: `FP08_NO_PARDISO=1` / `FP08_PARDISO=1`. 확인: `diag_eso.bat` |

---

## 9. Git 커밋 예시

```
[08] DeepSDF 서버 학습 결과 반영

변경 포인트
- runs/main 요약을 docs/results_2026-11-16.md 에 추가 (IoU 그룹별 표)
- loop.py: --sdf-steps 기본 20000 → 30000 (IoU 0.90 미달 대응)
영향: 08 폴더만. 10 입력 스펙(formproof.spec/0.2-08) 변경 없음
```
- 체크포인트(`*.pt`)·데이터(`data/`)·zip 은 **커밋하지 말 것** (용량).
- push: `git push origin sosopapa`

---

## 10. 10(입력 스펙)과의 연결

- 10 은 사용자 입력을 스펙 JSON 으로 만듦. 08 은 `problems.py` 의 `Problem.spec()` 이 같은 형식(`schema: formproof.spec/0.2-08`)으로 문제를 내보냄.
- 시연 조건 `DEMO` (`loop.py`) 는 10 고정 시나리오와 맞춘 값 (거치대 휴대폰 200 g, TV 20.8 kg 등).
- 10 쪽 스펙이 바뀌면 08 을 고치기 전에 사용자에게 먼저 확인.
- 입력 단계 폴더는 `10_입력_1차설계` (예전 이름 `07_입력_1차설계`). 템플릿 22종 중 08 이 처리 가능한 것은 **T01·T02·T03·T07·T08·T17** (받침 50·80·120 mm, 높이 16 mm). 이 6종은 요소 라벨이 08 과 완전히 일치함(11-14 확인).
- 08 이 아직 다루지 않는 입력 요구: `free_angle`(`keepout` 마스크·관절 제약), `sun_heat`, `min_feature` 5 mm. 시연에서 쓸지는 미정(README §11 요청 18~23).
- 10 문서: https://github.com/mons2us/AI-hackathon/blob/feature/input-spec/10_%EC%9E%85%EB%A0%A5_1%EC%B0%A8%EC%84%A4%EA%B3%84/README.md

---

## 11. 용어

| 용어 | 뜻 |
|---|---|
| SDF `s` | 어떤 점에서 형상 표면까지의 거리 (안쪽 음수) |
| `z` | 형상 하나의 32차원 번호표(잠재벡터). 학습 중 θ 와 같이 학습됨 |
| DeepSDF | `s = f_θ(z, x)` 인 MLP. 형상을 z 로 압축 |
| IoU | 원래 재료 칸 A 와 모델이 s<0 이라 한 칸 B 의 겹침 = \|A∩B\| / \|A∪B\| |
| PINO | 형상 → 변위장·진동수 예측 신경망 (FNO + 물리 잔차 손실) |
| ESO | 힘이 거의 안 가는 칸을 지우는 고전 기법 (Xie & Steven 1993) |
| 관문(gate) | 대리 모델을 믿어도 되는지 검사. 불합격이면 능동학습 |
| 능동학습 | 모델이 틀리는 형상만 골라 FEM 정답을 더 만들어 재학습 |
| fallback / 경로 A | 대리 모델 결과가 FEM 검증에 실패한 상태 / FEM 직접 최적화(팀 코드, 자동 연결은 아직 없음) |

참고문헌: Park et al., *DeepSDF*, CVPR 2019 · Li et al., *Fourier Neural Operator*, ICLR 2021 · Li et al., *Physics-Informed Neural Operator*, 2021 · Xie & Steven, *A simple evolutionary procedure for structural optimization*, Computers & Structures 1993.
