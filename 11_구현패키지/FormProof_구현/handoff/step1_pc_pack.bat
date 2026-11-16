@echo off
chcp 65001 > nul
set PYTHONUTF8=1
rem ==========================================================================================
rem [회사 PC] 1단계: 서버에 올릴 묶음 만들기  →  upload_fp11.zip  (약 5 MB)
rem   코드 + 격자 정보 + 위상 최적화 기록 245개 + 기준 결과. 학습 데이터는 서버에서 새로 만듦.
rem   선택: "step1_pc_pack.bat test" 로 실행하면 묶기 전에 패키지 확인 + 빠른 테스트 (약 2분)
rem ==========================================================================================
cd /d %~dp0\..
if /i "%1"=="test" (
  echo [시험] 패키지 확인 + 빠른 테스트 (pytest)
  python -c "import numpy,scipy,pypardiso,mmapy; print('패키지 OK')" || goto :fail
  python -m pytest -q tests || goto :fail
)
python -c "import zipfile,os,glob;skip=('data/shards','runs','upload_fp11.zip','results_fp11.zip','__pycache__','.pytest_cache');fs=[f.replace(os.sep,'/') for f in glob.glob('**/*',recursive=True) if os.path.isfile(f)];fs=[f for f in fs if not any(f.startswith(s) or ('/'+s) in f for s in skip)];z=zipfile.ZipFile('upload_fp11.zip','w',zipfile.ZIP_DEFLATED);[z.write(f,'fp11/'+f) for f in fs];z.close();print(len(fs),'개 파일 →','upload_fp11.zip',round(os.path.getsize('upload_fp11.zip')/1e6,1),'MB')" || goto :fail
echo.
echo 다음: upload_fp11.zip 을 서버에 올리고 서버에서
echo    unzip upload_fp11.zip ^&^& cd fp11
echo    pip install -r requirements.txt -r requirements_gpu.txt      (처음 한 번)
echo    TINY=1 bash handoff/step2_server_all.sh                      (시험, 약 10분)
echo    rm -rf runs data/shards_frame data/shards_thermal            (시험 결과 지우기)
echo    nohup bash handoff/step2_server_all.sh ^> step2.out 2^>^&1 ^&   (본 실행)
pause
exit /b 0
:fail
echo 실패 — 위 메시지 확인
pause
exit /b 1
