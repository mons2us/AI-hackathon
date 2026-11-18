@echo off
chcp 65001 > nul
set PYTHONUTF8=1
rem ===== [GPU 서버, Windows] 3단계: 데이터 생성 + 학습 + 관문 + 능동학습 + 시연 (step3_server_train.sh 의 Windows 판) =====
rem 사용: 코드 폴더에서  handoff\step3_server_train.bat        (계획 A: 데이터도 서버에서 생성)
rem       handoff\step3_server_train.bat B                    (계획 B: upload_data.zip 을 코드 폴더에 두고)
rem 반영 (2026-11-15): 7그룹(화면 각도 자유 포함), ESO 형상 + 정답, 위에서 깎기 형상 + 정답, 학습 방법 자동 선택(sweep),
rem       D 열린 껍데기: 거치대 0%, TV 5%(두께 3~4칸, 앞뒤 같은 방향으로 열림)
rem 끊기면 같은 파일을 다시 실행 → runs\main\state.json 보고 끝난 단계는 건너뜀
rem 숫자 바꾸기(학습이 잘 안 될 때, HANDOFF.md 6-1): 실행 전에  set N_FEM=2000  처럼 지정
cd /d %~dp0\..
set PLAN=%1
if "%PLAN%"=="" set PLAN=A
if not defined N_SHAPES set N_SHAPES=5000
if not defined N_FEM set N_FEM=1000
if not defined SDF_STEPS set SDF_STEPS=20000
if not defined PINO_STEPS set PINO_STEPS=30000
if not defined SWEEP set SWEEP=--sweep --sweep-topk 1
if not defined WORKERS set WORKERS=%NUMBER_OF_PROCESSORS%
if %WORKERS% GTR 64 set WORKERS=64
python -c "import torch,os;print('torch',torch.__version__,'GPU',torch.cuda.device_count(),[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())],'CPU',os.cpu_count())"
set DEV=
for /f "delims=" %%i in ('python -m fp08.pack devices') do set DEV=%%i
if "%DEV%"=="" (
  echo GPU 가 안 보입니다. nvidia-smi 와 CUDA 판 torch 를 확인하세요. 중단.
  pause
  exit /b 1
)
echo 장치: %DEV%
set OMP_NUM_THREADS=1
set MKL_NUM_THREADS=1
if /i "%PLAN%"=="B" (
  if not exist data\ python -m fp08.pack unpack upload_data.zip .
  set STAGES=sdf,pino,gate,al,demo
) else (
  set STAGES=shapes,fem,sdf,pino,gate,al,demo
)
python -m fp08.loop --run runs\main --data data --stages %STAGES% --devices "%DEV%" --workers %WORKERS% %SWEEP% ^
  --n-shapes %N_SHAPES% --n-cand 12000 --eso --topdown 100 --n-fem %N_FEM% ^
  --sdf-steps %SDF_STEPS% --sdf-width 256 --sdf-depth 8 --pino-steps %PINO_STEPS% ^
  --al-n 200 --max-rounds 3
python -m fp08.pack check data
python -m fp08.pack report runs\main
python -m fp08.pack runs runs\main results.zip
echo.
echo 끝. results.zip 을 회사 PC 로 내려받아 handoff\step4_pc_demo.bat 실행
pause
