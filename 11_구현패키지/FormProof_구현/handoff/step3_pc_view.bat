@echo off
chcp 65001 > nul
set PYTHONUTF8=1
rem ==========================================================================================
rem [회사 PC] 3단계: 서버 결과 보기
rem   서버에서 받은 results_fp11.zip 을 이 패키지 폴더(FormProof_구현)에 두고 실행
rem   → runs\ 에 풀고 요약(runs\report.html)을 브라우저로 엶
rem ==========================================================================================
cd /d %~dp0\..
if not exist results_fp11.zip (
  echo results_fp11.zip 이 없음. 서버의 fp11\results_fp11.zip 을 %cd% 에 복사하세요.
  pause & exit /b 1
)
python -c "import zipfile;zipfile.ZipFile('results_fp11.zip').extractall('.');print('풀기 끝')" || (pause & exit /b 1)
rem 서버가 만든 요약(데이터 통계 포함)을 그대로 엶. 없을 때만 PC 에서 다시 만듦
if not exist runs\report.html python scripts\report_frame.py . > nul
start "" runs\report.html
echo 최적화 후보 형상: runs\latent\cand_*.npy   FEM 검증: runs\gate\frfint_cand_*.json
pause
