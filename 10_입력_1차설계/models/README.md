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

## 하이브리드 경로 (hybrid_p01.json.gz)

기본 선택(1차 설계에서 미충족 5개: 진동수 · 폰 온도 · 휨 · 층간 · 흔들림)으로 최적화를 누르면 이 경로를 재생한다.

1. **① AI 탐색** — 형상 AI × 물리 AI, 300회 (GUI `TorchBackend.trace` 그대로)
2. **후보 선택** — 탐색 형상 31개를 정밀 계산(FEM) → 진동수 · 휨 · 충격 기준 통과 형상 중 가장 가벼운 것 (탐색 120회째, 89.4 g)
3. **② 정밀 최적화** — 그 후보에서 구조 최적화 + FEM (진동수 목표 95 Hz 60회 → 흔들림 대응 150 Hz 40회)
4. **③ 최종 검증** — 검증 관문(gate)이 최종 형상을 팀 엔진 FEM 으로 다시 판정

최종 형상 정밀 판정 (13_AI학습_일체형/runs/hybrid/frfint_hyb2.json): 89.2 g · 진동수 153 Hz · 폰 온도 상승 20.93 °C · 휨 0.04 mm ·
충격 3.2 MPa · 층간 2.7 MPa · 흔들림 1.36배 — 전 기준 통과.

다른 기준을 고르면 학습 모델로 바로 탐색하고(CPU 에서 수 분), 마지막 형상을 FEM 으로 판정한다. `FP_OPT_HYBRID=0` 이면 하이브리드 경로를 쓰지 않는다.
다시 만들기: `python3 13_AI학습_일체형/make_hybrid_pack.py <runs/hybrid 폴더>`.
