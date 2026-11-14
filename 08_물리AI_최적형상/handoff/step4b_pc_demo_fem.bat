@echo off
chcp 65001 > nul
set PYTHONUTF8=1
rem ===== [회사 PC, CPU] 4단계(임시): 학습 모델 없이 시연 — 수식 형상 생성 + FEM 직접 최적화 =====
rem DeepSDF·PINO 학습 전에 쓰는 경로. 학습이 끝나면 step4_pc_demo.bat (대리 모델 경로)로 바꿈. 화면(app.html)은 같음.
rem 결과: results\app.html (통합 시연 화면), results\<그룹>_<조건>.stl/.json/.png
rem 시간(추정, 미측정): 거치대 그룹당 약 2~3분, TV 그룹은 FEM 이 느려 그룹당 10분 이상 (CPU 코어 수에 따라 다름)
rem 한 그룹만: python -m fp08.fem_opt --out results --groups bike_pad80
cd /d %~dp0\..
set OMP_NUM_THREADS=1
rem TV 그룹은 FEM 메모리가 커서 작업자 1개 (메모리 7 GB 환경에서 2개면 작업자가 죽고 멈춤, 11-15 확인)
if "%~1"=="" (
  python -m fp08.fem_opt --out results --groups bike_pad50,bike_pad80,bike_pad120,bike_pad80_free --no-app
  python -m fp08.fem_opt --out results --groups tvped,tvfeet_L300,tvfeet_L220 --workers 1
) else (
  python -m fp08.fem_opt --out results %*
)
start results\app.html
pause
