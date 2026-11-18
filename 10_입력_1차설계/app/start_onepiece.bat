@echo off
rem 11-18 sosopapa: 일체형(한 번에 출력, 핀/볼트 없음) 모드로 GUI 실행 -> http://localhost:8765
rem 물리 기반 최적화 = 일체형 위상 최적화 기록 재생(models/onepiece_p01.json.gz) + 팀 엔진 GRIP=3 판정 + 출력 자세 STL
chcp 65001 >nul
cd /d "%~dp0.."
set PYTHONUTF8=1
set FP_ONEPIECE=1
set "PYEXE=python"
if exist ".venv\Scripts\python.exe" set "PYEXE=.venv\Scripts\python.exe"
"%PYEXE%" app\server.py %*
pause
