@echo off
chcp 65001 > nul
set PYTHONUTF8=1
rem ===== FormProof 08 - 내 PC 실행 (Windows, Anaconda) =====
rem 1) 형상 후보 12,000 -> 5,000 선택 + ESO 다듬기(절반 추가) + FEM 정답 1,000개 (6그룹)
rem 2) DeepSDF 학습: 거치대 80, 8층 x 256 (CPU 8코어)
rem 끊겨도 다시 실행하면 이어서 함. 결과: data\ , runs\local\ (report.html)
cd /d %~dp0
call "%USERPROFILE%\anaconda3\Scripts\activate.bat"
python -m pip install --quiet numpy scipy scikit-image matplotlib pypardiso torch
set OMP_NUM_THREADS=1
set MKL_NUM_THREADS=1
python -m fp08.loop --run runs\local --data data --stages shapes,fem --workers 10 --n-shapes 5000 --n-cand 12000 --eso --n-fem 1000
set OMP_NUM_THREADS=8
set MKL_NUM_THREADS=8
python -m fp08.train_sdf --group bike_pad80 --data data --out runs\local --steps 20000 --eval-every 2000 --width 256 --depth 8 --n-eval 30 --device cpu
echo.
echo 끝났습니다. runs\local\report.html 과 runs\local\sdf\bike_pad80\ 을 확인하세요.
pause
