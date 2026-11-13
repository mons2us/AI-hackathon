"""fp08 — FormProof 08 단계: 제품군별 대리 모델(DeepSDF + PINO) 자동 생성과 최적 설계.

모듈
  fem       : 3D hex8 구조 격자 FEM (정적 다중 하중, 대칭 S/A, 고유진동수)
  problems  : 문제 정의 3종 (자전거 거치대, TV 양발형, TV 중앙형) — 07 problem.npz 형식 확장
  shapes    : 설계 범위 안 무작위 형상 생성 (A 부재, B 트러스, C 판, D 열린 껍데기, E 보강)
  labels    : 형상별 FEM 정답 계산
"""
