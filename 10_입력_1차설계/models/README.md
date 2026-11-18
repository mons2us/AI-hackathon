# 학습 모델 (P01 물리 기반 최적화)

이 폴더의 세 파일은 git 에 함께 올라가 있다 (`13_AI학습_일체형` 에서 CPU 로 학습 · 검증한 결과).

```
results_fp11.zip    runs/sdf.pt (형상 AI · DeepSDF, 잠재 16 · 폭 128) + runs/fno.pt (물리 AI · FNO, 폭 12, 능동 학습 2회 후)
grid_meta.npz       P01 격자 (88 × 20 × 37, 2 mm)
hybrid_p01.json.gz  하이브리드 최적화 경로 (아래)
```

- 처음 쓸 때 zip 에서 `runs/sdf.pt` · `runs/fno.pt` 를 `models/fp11/runs/` 로 풀어 둔다 (zip 이 바뀌면 다시 풂). `models/fp11/` 는 git 에 안 올림.
- 확인: `python -m formproof_input.inverse check` → 어느 모델로 도는지, 1차 설계를 형상 AI 로 다시 그린 겹침 비율(IoU 0.997).
- PyTorch 가 없거나 파일이 없으면 자동으로 대체 모델(anchor)로 돈다.

## 지금 쓰는 경로: hybrid_p01_v4.json.gz (결선 데모 v28 과 같음)

`inverse.hybrid_pack()` 은 v4 > v3 > e2 > v1 순으로 있는 파일을 쓴다. v4 = v3 와 경로 · 수치 같음, 화면 문구에서 FEM 표기만 뺌.

1. **① AI 탐색** — 형상 AI × 물리 AI 300회 (능동 학습 3회차 al3)
2. **후보 선택** — 탐색 형상 31개 정밀 계산 → 기준(진동수 ≥ 95 Hz · 휨 ≤ 0.3 mm · 충격 ≤ 10.9 MPa) 통과 11개 중 진동수가 가장 높은 al3_020 (171.2 Hz)
3. **② 정밀 최적화** — 그 후보에서 발표 최종 형상(int35f95g2)과 같은 조건 120회 (`13_AI학습_일체형/runs/ppt_from_al3_020`)
4. **③ 최종 검증** — 검증 관문이 최종 형상을 팀 엔진으로 다시 판정 (결과는 `formproof_input/templates/db/integral_eval.json` · `integral_fields.npz` 에 커밋되어 있어 엔진 없이 바로 나옴)

GUI 결과(2026-11-19 새로 받은 저장소에서 확인): 94.9 → 80.1 g (−15.6 %) · 152.4 Hz · 20.87 °C · 0.038 mm · 3.6 MPa · 흔들림 1.41배 — 5/5 충족.

**재생 조건**: 고른 항목 중 물리 AI 가 예측하는 항목(떨림 주파수 · 폰 온도 · 휨 · 충격)이 {떨림 주파수, 폰 온도, 휨} 과 정확히 같고, 학습 모델(PyTorch + results_fp11.zip)로 돌 때. 흔들림 · 층간은 넣든 빼든 같음.
그 밖의 선택(예: 충격 추가, 휨 빼기)이나 PyTorch 가 없으면 경로 재생이 아니라 그 자리에서 탐색한다 (CPU 수 분 이상, 결과 형상 다름).
다시 만들기: `python3 13_AI학습_일체형/make_hybrid_pack_v3.py` (출력 v4).

## (이전) 하이브리드 경로 v1 (hybrid_p01.json.gz)

기본 선택(1차 설계에서 미충족 5개: 진동수 · 폰 온도 · 휨 · 층간 · 흔들림)으로 최적화를 누르면 이 경로를 재생한다.

1. **① AI 탐색** — 형상 AI × 물리 AI, 300회 (GUI `TorchBackend.trace` 그대로)
2. **후보 선택** — 탐색 형상 31개를 정밀 계산(FEM) → 진동수 · 휨 · 충격 기준 통과 형상 중 가장 가벼운 것 (탐색 120회째, 89.4 g)
3. **② 정밀 최적화** — 그 후보에서 구조 최적화 + FEM (진동수 목표 95 Hz 60회 → 흔들림 대응 150 Hz 40회)
4. **③ 최종 검증** — 검증 관문(gate)이 최종 형상을 팀 엔진 FEM 으로 다시 판정

최종 형상 정밀 판정 (13_AI학습_일체형/runs/hybrid/frfint_hyb2.json): 89.2 g · 진동수 153 Hz · 폰 온도 상승 20.93 °C · 휨 0.04 mm ·
충격 3.2 MPa · 층간 2.7 MPa · 흔들림 1.36배 — 전 기준 통과.

다른 기준을 고르면 학습 모델로 바로 탐색하고(CPU 에서 수 분), 마지막 형상을 FEM 으로 판정한다. `FP_OPT_HYBRID=0` 이면 하이브리드 경로를 쓰지 않는다.
다시 만들기: `python3 13_AI학습_일체형/make_hybrid_pack.py <runs/hybrid 폴더>`.
