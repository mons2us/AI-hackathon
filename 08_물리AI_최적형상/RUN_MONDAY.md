# 월요일 실행 안내 — 08 물리 AI 자동 루프

> 코드: `sosopapa` 브랜치 `08_물리AI_최적형상/fp08/`. 모든 명령은 `08_물리AI_최적형상/` 폴더에서 실행.
> 숫자 중 **실측**은 주말 리허설(Claude 작업 환경, CPU 2코어)에서 잰 값, **추정**은 그 값으로 계산한 값.

## 0. 설치 (두 서버 공통)

```bash
git clone -b sosopapa https://github.com/mons2us/AI-hackathon.git && cd AI-hackathon/08_물리AI_최적형상
pip install numpy scipy scikit-image pypardiso torch    # GPU 서버는 CUDA 버전 torch
python -m fp08.problems                                  # 6개 그룹 격자·칸 수 출력되면 정상
```

## 1. 걸리는 시간 (실측 → 추정)

| 작업 | 실측 (CPU 1코어당) | 월요일 규모 | 추정 |
|---|---|---|---|
| 무작위 형상 + SDF 점 4,000개 | 100개 묶음 2~4 s | 그룹당 5,000 × 6 = 3만 | 약 15분·코어 → 32코어 1분 미만 |
| FEM 정답 (정적 + 진동) | 형상 1개 1.1~1.7 s | 그룹당 1,000 × 6 = 6,000 | 약 2.5시간·코어 → 32코어 약 5분 |
| DeepSDF | 0.2 s/스텝 (CPU 1스레드, 32형상×1024점) | 그룹당 2만 스텝 | GPU 실측 필요 |
| PINO | 약 1.8 s/스텝 (CPU 1스레드, 폭 16, 배치 4+2) | 제품당 3만 스텝 | GPU 실측 필요 |

→ **FEM이 예상(7.5 s)보다 5배 빨라서 CPU 서버 부담이 작음.** GPU 서버 CPU 코어가 16개 이상이면 GPU 서버 하나로 전부 가능.
→ 여유가 있으면 FEM 정답 수를 늘리는 것이 정확도에 가장 확실함 (`--n-fem 3000` 등, 결정 필요).

## 2. CPU 서버 — 데이터 (약 10~20분 추정)

```bash
python -m fp08.loop --run runs/main --data data --stages shapes,fem --workers $(nproc) \
       --n-shapes 5000 --n-fem 1000
# 진행: runs/main/report.html, runs/main/loop.log, data/<그룹>/spec.json
rsync -a data/ <GPU서버>:<경로>/08_물리AI_최적형상/data/      # 서버 간 SSH 전송 (사내망)
```
- 끊겨도 같은 명령을 다시 실행하면 만든 묶음은 건너뛰고 이어서 함.
- 같은 (그룹, 번호)는 항상 같은 형상(시드 고정) → 전송이 막히면 GPU 서버에서 같은 명령으로 다시 만들어도 동일.

## 3. GPU 서버 — 학습·관문·능동 학습·시연 (A100 × 8)

```bash
# (1) 본 루프: GPU 0~2 — DeepSDF 6개 → PINO 3개 → 관문 → 능동 학습(최대 3바퀴) → 시연 최적화 + FEM 검증
nohup python -m fp08.loop --run runs/main --data data --stages sdf,pino,gate,al,demo \
      --devices cuda:0,cuda:1,cuda:2 --workers $(nproc) \
      --sdf-steps 20000 --pino-steps 30000 --deadline "2026-11-17 07:00" > runs/main.out 2>&1 &

# (2) 비교 실험 (발표 부록): GPU 3~5 = FNO(물리 손실 없음), GPU 6 = 레일리 대신 직접 회귀
for i in 0 1 2; do pr=(bike tvfeet tvped); \
  nohup python -m fp08.train_pino --product ${pr[$i]} --data data --out runs/main --tag fno --no-physics \
        --steps 30000 --device cuda:$((3+i)) > runs/fno_${pr[$i]}.out 2>&1 & done
nohup python -m fp08.train_pino --product bike --data data --out runs/main --tag direct --freq direct \
      --steps 30000 --device cuda:6 > runs/direct_bike.out 2>&1 &
# GPU 7 = 예비 (FEM 정답을 늘리거나 실패한 작업 재실행)
```

## 4. 확인할 파일

| 파일 | 내용 |
|---|---|
| `runs/main/report.html` | 품질 관문 결과·시연 최적화 결과·단계 완료 시각 (1분마다 새로고침) |
| `runs/main/state.json` | 같은 내용 (기계용). 끊기면 이 파일 기준으로 이어서 |
| `runs/main/sdf/<그룹>/ckpt.pt`, `runs/main/pino/<제품>/ckpt.pt` | 모델 체크포인트 (+ 학습 기록 `hist`) |
| `runs/main/demo/opt_*.json / .npy` | 시연 조건 최적 형상과 FEM 검증 값 |
| `runs/main/*.log` | 작업별 로그 |

## 5. 문제가 생기면

| 증상 | 조치 |
|---|---|
| 관문 불합격이 계속됨 | 시연은 FEM 직접 최적화 결과로 (팀 `opt3d.py` / `ped.py`). `--n-fem` 늘려 재실행 |
| DeepSDF IoU 낮음 (리허설 1,500스텝 0.6) | 스텝 늘리기, 폭 256 시도 (아래 "알려진 위험") |
| GPU 메모리 부족 | `train_pino --bs 2`, `--width 16` |
| 중간에 멈춤 | 같은 명령 다시 실행 (체크포인트에서 이어짐) |

## 6. 알려진 위험 (주말 리허설에서 확인)

- DeepSDF 4층×128은 얇은 부재(반지름 2~6 mm)를 표현하기에 작을 수 있음 → GPU에서 IoU 확인 후 필요하면 폭·층 증가
- TV 양발형 L220 그룹은 해석식 넘어짐 여유 0.89 → 어떤 형상도 합격 불가 (발끝 길이 재결정 필요)
- TV 앞뒤 밀기 때 뒤쪽 패드 반력이 음수(들림)인 형상이 대부분 → 현재 "경고"로만 기록
