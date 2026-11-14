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
3. **물리 상수·하중 조건·판정 기준**(`fp08/problems.py`의 재료값, 하중, 허용응력, `loop.py`의 `GATE`, `DEMO`)은 **사용자 확인 없이 바꾸지 말 것**. 07 담당(공동 작업자)과 맞춘 값입니다.
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
| `fp08/pack.py` | zip 묶기/풀기, `check`(데이터 개수), `report`(학습 결과 요약) |
| `docs/DeepSDF_study.html` | DeepSDF 공부 자료 (그림) |
| `RUN_MONDAY.md` | 서버 1대에서 전부 돌릴 때의 원래 계획서 |

6개 그룹: `bike_pad50`, `bike_pad80`, `bike_pad120` (자전거 거치대, 2 mm 격자) · `tvfeet_L300`, `tvfeet_L220` (TV 양발, 2.5 mm) · `tvped` (TV 중앙 스탠드, 5 mm). 제품 3개: `bike`, `tvfeet`, `tvped` (PINO 는 제품별).

---

## 5. 단계별 실행

### 준비 (회사 PC, 한 번)
1. 코드 받기: (가능하면) `git clone -b sosopapa https://github.com/mons2us/AI-hackathon.git` → `cd AI-hackathon/08_물리AI_최적형상`
   GitHub 접속이 막혀 있으면 `FormProof_08_code.zip` 을 풀어서 사용.
2. 파이썬 패키지: `pip install -r requirements.txt` (인터넷 없으면 파일 맨 위 주석의 오프라인 방법).
3. 확인: `python -m fp08.loop --help` 가 에러 없이 나오면 OK.

### ① [회사 PC] 데이터 생성 — 계획 B 일 때만
- 실행: `handoff\step1_pc_datagen.bat`
- 시간(추정): 형상 6그룹 수십 분 + FEM 6,000개 1~3시간 (8코어 기준, TV 그룹이 더 느림). **실측 아님.**
- 성공: 마지막 표에서 6그룹 모두 `형상 5000`, `FEM 1000` (ESO 열은 2,500 근처).
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
- 하는 일: (A면 형상·FEM 생성) → DeepSDF 6개(8층×256, 20,000스텝) → PINO 3개(30,000스텝) → 관문 → 불합격 그룹은 능동학습(200개 FEM 추가, 최대 3바퀴) → 시연.
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
| PINO (코드에 들어있음, `loop.py GATE`) | 변위장 상대 L2 평균 ≤ 0.10, 판정값 오차 p90 ≤ 5%, 응력 오차 p90 ≤ 15%, 진동수 ±5% 이내 ≥ 95% | 자동 판정 |
| DeepSDF | IoU_val ≥ 0.90, 표면 오차 ≤ 0.5칸 | **제안값, 사용자 미확정. 코드에서 자동 판정 안 함** → `pack report` 로 눈으로 확인 |
| 최종 시연 | `status: ok` (대리 모델 결과가 FEM 검증 합격). `fallback` = FEM 직접 최적화(경로 A)로 대신했다는 뜻 | 자동 |

DeepSDF IoU 가 0.90 에 못 미치면: 스텝을 늘려 이어서 학습 (ckpt 에서 이어짐, 크기 옵션은 꼭 같게):
`python -m fp08.train_sdf --group <그룹> --data data --out runs/main --steps 40000 --width 256 --depth 8 --n-eval 30 --device cuda:0`

그래도 안 되면 사용자에게 보고하고 지시를 받을 것.

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
| `ModuleNotFoundError: pypardiso` 경고 | ARM·인텔 MKL 없음 | 무시 가능. SuperLU 로 자동 대체 (느려짐, 결과 같음) |
| `GPU 가 안 보입니다` | CPU 판 torch / 드라이버 | `nvidia-smi`, `python -c "import torch;print(torch.cuda.is_available())"` |
| `CUDA out of memory` | 한 GPU 에 작업 너무 많음 | `step3` 의 `DEV="$DEV,$DEV,$DEV"` 를 `DEV="$DEV,$DEV"` 로, 또는 `--bs` 줄이기 |
| 학습이 중간에 죽음 | 세션 끊김 | `nohup` 으로 실행했는지 확인, 같은 명령 재실행 (이어짐) |
| 관문 계속 불합격 | 데이터 부족/학습 부족 | `pack report` 의 불합격 사유 확인 → 사용자 보고. 기준(GATE)을 낮추지 말 것 |
| 시연 `fallback` | 대리 모델 예측 ≠ FEM | 정상 동작(안전장치). 사유를 summary 에 그대로 보고 |
| `torch.load` 에러 `weights_only` | torch 버전 차이 | 코드가 `weights_only=False` 사용 중. torch ≥ 2.1 사용 |
| Windows 에서 한글 깨짐 | 콘솔 코드페이지 | bat 첫 줄 `chcp 65001` 유지 |

---

## 9. Git 커밋 예시

```
[08] DeepSDF 서버 학습 결과 반영

변경 포인트
- runs/main 요약을 docs/results_2026-11-16.md 에 추가 (IoU 그룹별 표)
- loop.py: --sdf-steps 기본 20000 → 30000 (IoU 0.90 미달 대응)
영향: 08 폴더만. 07 입력 스펙(formproof.spec/0.2-08) 변경 없음
```
- 체크포인트(`*.pt`)·데이터(`data/`)·zip 은 **커밋하지 말 것** (용량).
- push: `git push origin sosopapa`

---

## 10. 07(입력 스펙)과의 연결

- 07 은 사용자 입력을 스펙 JSON 으로 만듦. 08 은 `problems.py` 의 `Problem.spec()` 이 같은 형식(`schema: formproof.spec/0.2-08`)으로 문제를 내보냄.
- 시연 조건 `DEMO` (`loop.py`) 는 07 고정 시나리오와 맞춘 값 (거치대 휴대폰 200 g, TV 20.8 kg 등).
- 07 쪽 스펙이 바뀌면 08 을 고치기 전에 사용자에게 먼저 확인.
- 07 문서: https://github.com/mons2us/AI-hackathon/blob/feature/input-spec/07_%EC%9E%85%EB%A0%A5_1%EC%B0%A8%EC%84%A4%EA%B3%84/README.md

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
| fallback / 경로 A | 대리 모델이 실패하면 FEM 직접 최적화로 대신 |

참고문헌: Park et al., *DeepSDF*, CVPR 2019 · Li et al., *Fourier Neural Operator*, ICLR 2021 · Li et al., *Physics-Informed Neural Operator*, 2021 · Xie & Steven, *A simple evolutionary procedure for structural optimization*, Computers & Structures 1993.
