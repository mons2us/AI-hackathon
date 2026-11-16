@echo off
rem FormProof input stage GUI -> browser http://localhost:8765
chcp 65001 >nul
cd /d "%~dp0.."
set PYTHONUTF8=1
set "PYEXE=python"
if exist ".venv\Scripts\python.exe" set "PYEXE=.venv\Scripts\python.exe"
"%PYEXE%" app\server.py %*
pause
