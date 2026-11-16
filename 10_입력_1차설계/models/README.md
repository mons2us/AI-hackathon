# 학습 모델 넣는 곳 (P01 물리 기반 최적화)

GPU 서버 step2 결과 두 파일을 **이 폴더에 이름 그대로** 넣는다.

```
10_입력_1차설계/models/results_fp11.zip    ← step2_server_all.sh 가 만든 묶음 (안의 runs/sdf.pt · runs/fno.pt 를 씀)
10_입력_1차설계/models/grid_meta.npz       ← 같은 서버의 data/grid_meta.npz
```

그다음 `app\setup.bat` 을 한 번 실행 (PyTorch CPU 설치 → 모델 확인 → 기본 최적화 경로 미리 계산). 끝.
- 처음 쓸 때 zip 에서 `runs/sdf.pt`(형상 AI) · `runs/fno.pt`(물리 AI) 를 `models/fp11/runs/` 로 풀어 둔다 (zip 이 바뀌면 다시 풂).
- 확인만: `.venv\Scripts\python -m formproof_input.inverse check` → 어느 모델로 도는지, 1차 설계를 형상 AI 로 다시 그린 겹침 비율(IoU),
  반복 1회 시간.
- 두 파일이 없거나 PyTorch 가 없거나 격자가 P01 과 다르면, 자동으로 대체 모델(1차 설계 → 최종 최적 구조 형상 경로 + 실제 FEM 값)로 돈다.
- 이 폴더의 zip · npz · pt 는 git 에 올라가지 않는다(.gitignore).
