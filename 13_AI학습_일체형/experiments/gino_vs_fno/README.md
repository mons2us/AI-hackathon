# GINO vs FNO 물리 AI 비교 실험 (2026-11-19 ~ 20)

같은 형상 AI(DeepSDF, 숫자 16개)에 물리 AI 만 FNO / GINO 로 바꿔 비교. 검증 58개 형상은 고정(`results/test_names.json`).

| 판 | 내용 | 페이지 |
|---|---|---|
| v1 | GINO 단독 검증 (389개) | `pages/gino_report.html` |
| v2 | FNO 같은 분할 재학습 + AI 탐색 → 정밀 판정 | `pages/gino_report_v2.html` |
| v3 | 데이터 389 → 734 재학습 비교 | `pages/gino_report_v3.html` |

## 결과 요약 (v3)
- 탐색 형상 4개(FNO/GINO × 389/734) 모두 정밀 판정 불합격. 공통 원인 = 진동수 과대평가 (AI 94~103 Hz → 정밀 2~40 Hz).
- 734개 학습: 충격 응력 · 온도 · 휨(아래) 지표는 좋아졌으나 진동수 · 분포 오차는 나빠짐. 학습 단계 수는 389개 때와 같음(형상당 학습 횟수 약 절반) — 원인 분리는 확인 필요.

## 파일
- 학습: `train_fno_ckpt.py`(중간 저장 · 이어 학습), `train_gino.py`, `train_gino_ck.py`, `gino_data.py`, `gino_model.py`
- 평가: `cmp_eval.py`(389, v2), `cmp_eval_v.py <태그> <fno.pt> <gino.pt>`(각 모델 자기 척도로 분포 복원)
- 탐색: `search_cmp.py` (`TAG=734` 환경변수로 734 모델), 판정: `fem_check.py` (팀 엔진 MODE=eval)
- 그림 · 페이지: `viz.py`, `fig_v3.py`, `page.py`, `page_v2.py`, `page_v3.py`
- `results/nan_*` = 무게 출력 decode 넘침(NaN 기울기)으로 무효가 된 첫 FNO 탐색. 보존만 하고 결과로 쓰지 않음.

## 주의
- 학습된 모델(.pt, 9~35 MB)은 저장소에 넣지 않음. 스크립트의 경로 일부는 실험한 세션의 임시 폴더(`.../scratchpad/gino`) 기준 — 다시 돌리려면 경로 수정 필요.
- 머신 2코어 · 8 GB: 학습 중 정밀 시뮬레이션 동시 실행 금지(메모리 부족).

## 종합 · 문헌 (2026-11-20)
- `pages/lit_review_v1.html`: 대리모델 역설계 문헌 조사 (출처 11건)
- `pages/summary_v1.html`: 팀 능동학습 5회 · 하이브리드 시연 · GINO/FNO 비교 · 문헌 종합. v2·v3 의 "GUI FNO 80.1 g 합격" 문구 정정 포함 (시연 합격 형상은 하이브리드 결과).
- `pages/arch_review_v1.html`: 물리 AI 아키텍처 지도 (신경 연산자 · 트랜스포머 · 그래프 · 물리 정보 계열, NVIDIA PhysicsNeMo 모델 · 예제)
- `pages/arch_review_v2.html`: 아키텍처 지도 v2 — 8단계 프레임워크별 적용 자리(클릭) · 단계×방법 표 · 아키텍처 14개 구조 그림
- `pages/arch_review_v3.html`: 아키텍처 지도 v3 — 우리 형상을 각 구조가 보는 방식(복셀 · 푸리에 모드 · 표면 점 · 그래프 전달 범위 등)과 정밀 시뮬레이션 · AI 분포 · 능동학습 그림 추가 (`viz_arch.py`)
- `pages/cad_cae_ai_framework_v1.html`: CAD·CAE 와 물리 AI 통합 프레임워크 v1 — 기존 흐름 비교, BLU(CAD에서 해석까지 v12 · 3단계)와 FormProof 를 같은 계층(A~E + 신뢰도 · 재학습)으로
- `pages/cad_cae_ai_framework_v2.html`: 통합 프레임워크 v2 — 공통 뼈대 + 제품별 교체 부품, 제품 · 영역별 현황, 파라메트릭 CAD 재출력 설명
- `pages/physics_ai_framework_v3.html`: 통합 v3 — 기존 CAD·CAE 단계 매칭 · 입력~출력 파라메트릭 구간 · 모든 제품 공통 뼈대 · 아키텍처 지도 한 페이지 (`build_v3.py`)
