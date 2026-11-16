"""python -m formproof_input.inverse check       — 어느 모델로 도는지, 가중치 · 격자 읽기, 시작 형상 맞춤, 몇 회 시험
python -m formproof_input.inverse precompute  — 기본 선택(1차 설계 미충족 5개 · 전부)의 최적화 경로 + FEM 검증을 미리 계산"""
import sys
import time

from . import backend, limits, model_files, precompute, start_shape, KEYS


def check():
    files = model_files()
    print("모델 파일:", "있음 → " + " · ".join(files) if files else "없음 (models/results_fp11.zip · models/grid_meta.npz)")
    B = backend()
    print("사용 모델:", B.name, f"({B.id})", ("— " + B.reason) if B.reason else "")
    t = time.time()
    z0, fit = B.fit(start_shape())
    print(f"시작 형상 맞춤: 겹침 비율(IoU) {fit['fit_iou']} ({time.time() - t:.1f} s)", "— 0.8 미만이면 형상 AI 가 1차 설계를 잘 못 그림" if fit["fit_iou"] < 0.8 else "")
    t = time.time()
    fr = list(B.trace(z0, KEYS, limits(), iters=3, every=1))
    dt = (time.time() - t) / 4
    for f in fr:
        print(f"  반복 {f['it']}: 무게 {f['pred']['mass']:.1f} g · 벌점 {f['pen']:.2f} · " +
              " · ".join(f"{k} {v:.3g}" for k, v in f["pred"].items() if k != "mass" and v is not None))
    print(f"반복 1회 약 {dt:.2f} s → 기본 설정 전체 예상 {dt * (200 if B.id.startswith('fp11') else 120) / 60:.1f} 분 (precompute 하면 화면은 바로 재생)")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    check() if cmd == "check" else precompute()
