@echo off
rem FormProof input stage - Windows setup (run once). Needs internet (PyPI), no admin rights.
chcp 65001 >nul
setlocal
cd /d "%~dp0.."
set PYTHONUTF8=1

rem 1) find Python 3.11-3.13 (py launcher first, then python on PATH)
set "PY="
for %%V in (3.12 3.11 3.13) do (
  if not defined PY (
    py -%%V -c "import sys" >nul 2>&1 && set "PY=py -%%V"
  )
)
if not defined PY (
  python -c "import sys; assert (3,11) <= sys.version_info[:2] <= (3,13)" >nul 2>&1 && set "PY=python"
)
if not defined PY (
  echo [ERROR] Python 3.11-3.13 not found. Install Python 3.12 64-bit from https://www.python.org/downloads/windows/
  echo         and tick "Add python.exe to PATH", then run this again.
  pause
  exit /b 1
)
echo Python: %PY%

rem 2) virtual environment .venv (installs only inside this folder)
if not exist ".venv\Scripts\python.exe" %PY% -m venv .venv
if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] could not create .venv
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r app\requirements.txt
if errorlevel 1 (
  echo [ERROR] pip install failed. Behind a company proxy try: set HTTPS_PROXY=http://proxy:port
  pause
  exit /b 1
)

rem 3) check
".venv\Scripts\python.exe" -c "import cadquery, pypardiso, manifold3d, mmapy, skimage, ezdxf; print('setup OK')"

rem 3b) P01 physics optimization model (optional): models\results_fp11.zip + models\grid_meta.npz -> PyTorch CPU + check
if exist "models\results_fp11.zip" if exist "models\grid_meta.npz" (
  echo Trained model found in models\ - installing PyTorch CPU (once, about 200 MB^)...
  ".venv\Scripts\python.exe" -c "import torch" >nul 2>&1 || ".venv\Scripts\python.exe" -m pip install torch --index-url https://download.pytorch.org/whl/cpu
  ".venv\Scripts\python.exe" -m formproof_input.inverse check
)

rem 4) template result DB (1st designs are templates: compute once, then every run loads in < 4 s) - about 3 min
echo Building template result DB (once, about 3 min; with the trained model the P01 optimization paths take longer)...
".venv\Scripts\python.exe" -m formproof_input.memo
echo.
echo Done. Start the GUI with app\start.bat
pause
