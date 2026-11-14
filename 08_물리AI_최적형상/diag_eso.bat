@echo off
chcp 65001 > nul
set PYTHONUTF8=1
cd /d "%~dp0"
call "%USERPROFILE%\anaconda3\Scripts\activate.bat"
set OMP_NUM_THREADS=1
set MKL_NUM_THREADS=1
echo [1] pypardiso
python diag_eso.py
echo [2] SuperLU
set FP08_NO_PARDISO=1
python diag_eso.py
echo.
echo Done. Please capture this window.
pause
