@echo off
chcp 65001 > nul
set PYTHONUTF8=1
rem ===== [회사 PC, CPU] 1단계: 학습 데이터 만들기 (계획 B: 서버에서 데이터 생성이 안 될 때만) =====
rem 형상 후보 12,000 -> 5,000 선택 + ESO 다듬기 + FEM 정답 1,000개 x 6그룹
rem 끊겨도 같은 파일을 다시 실행하면 이어서 함. 결과: data\
cd /d %~dp0\..
set OMP_NUM_THREADS=1
set MKL_NUM_THREADS=1
python -m fp08.loop --run runs\pc --data data --stages shapes,fem --workers %NUMBER_OF_PROCESSORS% --n-shapes 5000 --n-cand 12000 --eso --n-fem 1000
python -m fp08.pack check data
echo.
echo 위 표에서 6그룹 모두 형상 5000 / FEM 1000 이면 성공. 다음: handoff\step2_pack_upload.bat
pause
