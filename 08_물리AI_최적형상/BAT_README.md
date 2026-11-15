# bat / sh 실행 파일 안내 (FormProof 08)

> 2026-11-15 정리. **어디서(회사 PC / GPU 서버) 무엇을 하려는지**로 고르면 됩니다. 자세한 절차는 `HANDOFF.md`.
> 모든 파일은 끊겨도 **같은 파일을 다시 실행하면 이어서** 진행합니다 (끝난 묶음·단계는 건너뜀).

## 한눈에

| 파일 | 어디서 | 하는 일 | 걸리는 시간 (추정) | 결과 위치 |
|---|---|---|---|---|
| `handoff\step1_pc_datagen.bat` | 회사 PC (CPU) | **계획 B 전용.** 7그룹 형상 생성 + ESO + FEM 정답 (+ 위에서 깎기) | **매우 김 (하루 이상)** — Windows PC 는 FEM 이 느림 (11-14 실측: ESO 그룹당 6~7시간) | `data\`, `runs\pc\` |
| `handoff\step2_pack_upload.bat` | 회사 PC | 서버에 올릴 zip 만들기: 코드(`upload_code.zip`, 항상) + 데이터(`upload_data.zip`, `data\` 가 있을 때만) | 1분 이내 (데이터 있으면 수 분) | 코드 폴더의 `upload_*.zip` |
| `handoff\step3_server_train.bat` | GPU 서버 (**Windows**) | 데이터 생성(계획 A) → DeepSDF·PINO 학습(학습 방법 자동 선택) → 관문 → 능동학습 → 시연 → `results.zip` | 서버 사양에 따라 수 시간~ (미측정) | `data\`, `runs\main\`, `results.zip` |
| `handoff/step3_server_train.sh` | GPU 서버 (**Linux**) | 위와 같음 (Linux 판) | 위와 같음 | 위와 같음 |
| `handoff\step4_pc_demo.bat` | 회사 PC (CPU) | 서버 학습 결과(`results.zip`)로 시연: 최적 형상 찾기 → FEM 검증 → STL·`app.html` | 그룹당 수 분 | `results\` (`app.html`, `*.stl`, `*.json`, `*.png`) |
| `handoff\step4b_pc_demo_fem.bat` | 회사 PC (CPU) | **학습 모델 없이** 임시 시연: FEM 직접 최적화(경로 A) → 같은 화면(`app.html`) | 거치대 그룹당 2~3분, TV 10분 이상 | `results\` |
| `diag_eso.bat` | 회사 PC | Windows 에서 FEM 이 느린지 진단 (pypardiso vs SuperLU, 형상 3개) | 1분 | 화면 출력만. **`data\bike_pad50\` 이 있어야 동작** |
| `old_run_local_PC_ESO_사용안함.bat` | — | 예전 집 PC 실행 파일 (ESO 포함, 작업자 10개). **쓰지 마세요** — PC 에서 며칠 걸림. 기록용으로 이름만 바꿔 둠 | — | — |

## 계획별 순서

```
계획 A (권장, 서버에 CPU 코어가 많을 때)
  회사 PC: step2 (코드 zip 만)  ──업로드──▶  서버: step3 (A)  ──results.zip──▶  회사 PC: step4

계획 B (서버에서 FEM 이 안 될 때)
  회사 PC: step1 → step2 (코드 + 데이터 zip)  ──업로드──▶  서버: step3 B  ──results.zip──▶  회사 PC: step4

학습 결과가 아직 없을 때 화면만 먼저 보기
  회사 PC: step4b
```

## step3 (서버) 에서 바꿀 수 있는 숫자

실행 전에 지정하면 그 값으로 실행 (Windows `set 이름=값`, Linux `이름=값 bash ...`). 학습이 잘 안 됐을 때 키워서 다시 실행하면 **모자란 만큼만 추가**하고 이어서 학습합니다 (`HANDOFF.md` §6-1).

| 이름 | 기본 | 의미 |
|---|---|---|
| `N_SHAPES` | 5000 | 그룹당 형상 수 |
| `N_FEM` | 1000 | 그룹당 FEM 정답 수 (ESO 형상 정답은 이것의 약 절반이 추가) |
| `SDF_STEPS` | 20000 | DeepSDF 학습 스텝 |
| `PINO_STEPS` | 30000 | PINO 학습 스텝 |
| `SWEEP` | `--sweep --sweep-topk 1` | 학습 방법 후보 4개 중 최선 자동 선택. `--sweep-topk 2` 면 2등까지 끝까지 |

## 공통 주의

- **절전 끄기**: 오래 걸리는 파일은 PC 가 잠들면 멈춥니다 (11-14·15 두 번 멈춤). 설정 → 시스템 → 전원 → 절전 모드 "안 함"
- bat 파일은 줄끝이 **CRLF** 여야 합니다. 편집기로 고쳐 저장할 때 LF 로 바뀌면 `'THREADS'은(는) 내부 또는 외부 명령…` 같은 오류가 납니다 (VS Code 오른쪽 아래 LF → CRLF)
- 집 PC 의 `Downloads\FormProof_08_code\` 는 **이전 코드**로 데이터를 만드는 중인 별도 폴더입니다 (거치대에 D 형식 포함). 그 폴더의 `run_local_all.bat`(7그룹, ESO 없음)·`run_local_bike80.bat`(거치대 80만)은 그 폴더 전용
