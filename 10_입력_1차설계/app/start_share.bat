@echo off
rem FormProof GUI - share on the company network: other PCs open http://<this PC IP>:8765 (no source code needed there)
chcp 65001 >nul
cd /d "%~dp0.."
set PYTHONUTF8=1
set "PYEXE=python"
if exist ".venv\Scripts\python.exe" set "PYEXE=.venv\Scripts\python.exe"
rem Windows firewall: allow inbound TCP 8765 (works only when run as administrator; otherwise Windows asks once - choose Allow)
netsh advfirewall firewall show rule name="FormProof 8765" >nul 2>&1 || netsh advfirewall firewall add rule name="FormProof 8765" dir=in action=allow protocol=TCP localport=8765 >nul 2>&1
"%PYEXE%" app\server.py --share %*
pause
