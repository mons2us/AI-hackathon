@echo off
chcp 65001 > nul
set PYTHONUTF8=1
rem ===== [회사 PC] 2단계: 서버에 올릴 zip 만들기 =====
rem upload_code.zip : 코드 (항상)      upload_data.zip : data\ 폴더 (계획 B 일 때만, 수 GB 가능)
cd /d %~dp0\..
python -m fp08.pack code upload_code.zip
if exist data\ python -m fp08.pack data data upload_data.zip
echo.
echo 서버에 upload_code.zip (와 upload_data.zip) 를 올리고 handoff\step3_server_train.sh 를 실행하세요.
pause
