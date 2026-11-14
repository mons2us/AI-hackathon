@echo off
chcp 65001 > nul
set PYTHONUTF8=1
rem ===== [회사 PC, CPU] 4단계: 서버 결과로 시연 (최적 형상 찾기 + FEM 검증 + STL) =====
rem 준비: 서버의 results.zip 을 이 폴더(코드 최상위)에 둔다.
rem       data\ 폴더는 있으면 좋음(FEM 합격 형상에서 최적화 시작 = 더 빠르고 안정). 없어도 동작(무작위 시작).
cd /d %~dp0\..
if not exist runs\main\state.json python -m fp08.pack unpack results.zip runs
set OMP_NUM_THREADS=%NUMBER_OF_PROCESSORS%
python -m fp08.demo --run runs\main --data data --out results --device cpu
start results\summary.html
pause
