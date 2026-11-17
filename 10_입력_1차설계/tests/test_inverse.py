"""P01 물리 기반 최적화(역설계) — 경로 · 기준 선택 · 검증 관문 · 학습 모델 자리."""
import os
import py_compile
import sys
import tempfile
import zipfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from formproof_input import inverse as O               # noqa: E402
from formproof_input import integral as I               # noqa: E402


def test_path_reaches_verified_design():
    """1차 설계 → 최종 구조: 첫 프레임 = 1차 설계, 마지막 = FEM 으로 모든 기준 통과, 형상이 실제로 여러 번 바뀜."""
    O._BACKEND.clear()
    res = O.run(("f1", "Tmax", "touch", "interlayer", "shake"), use_cache=False)
    fr = res["frames"]
    assert fr[0]["sha"] == O._sha(O.attached(O.start_shape())), "첫 프레임이 1차 설계가 아님"
    assert abs(fr[0]["mass_g"] - 94.9) < 0.1 and fr[0]["pen"] > 10
    assert abs(fr[-1]["mass_g"] - 77.1) < 0.1 and fr[-1]["it"] == 500
    # AI 예측(대체 모델): 오르내리고, 목표에 가까운 항목은 마지막에 조금 모자람 → 정밀 계산(FEM)에서 충족
    lim = O.limits()
    miss = [k for k in ("Tmax", "shake") if O.violation(k, fr[-1]["pred"][k], lim) > 0]
    assert miss and fr[-1]["pen"] > 0, (fr[-1]["pred"], fr[-1]["pen"])
    ups = sum(1 for a, b in zip(fr, fr[1:]) if b["pred"]["f1"] < a["pred"]["f1"])
    assert ups >= 5, ups                                                       # 떨림 주파수가 중간에 내려가는 곳이 여러 번
    meshes = sum(f["mesh"] is not None for f in fr)
    assert meshes >= 20, meshes
    assert all(f["pred"]["f1"] is not None for f in fr)
    g = O.gate(res)
    assert g["pass_"], [r for r in g["rows"] if not r["ok"]]
    assert np.array_equal(O.final_shape(res), I.full_density(I.shape("formproof")) > 0.5)
    return (f"프레임 {len(fr)}개(반복 500) · 표면 {meshes}가지, 무게 {fr[0]['mass_g']} → {fr[-1]['mass_g']} g, AI 예측 미달 {miss} → "
            f"FEM 검증 f1 {g['rows'][0]['value']:.1f} Hz · 폰 {g['rows'][1]['value']:.1f} °C 통과, {res['seconds']} s")


def test_only_selected_targets_penalised():
    """고른 기준만 벌점: 1차 설계가 이미 지키는 충격 응력만 고르면 처음 벌점 0, 떨림 주파수만 고르면 그것만."""
    lim = O.limits()
    B = O.backend()
    y, _ = B.predict(0.0) if hasattr(B, "predict") else (None, None)
    p_stress = sum(O.violation(k, y[k], lim) for k in ("stress",))
    p_f1 = sum(O.violation(k, y[k], lim) for k in ("f1",))
    assert p_stress == 0 and abs(p_f1 - (95 - y["f1"]) / 95 * 10) < 1e-9
    try:
        O.run(())
        raise AssertionError("빈 선택이 통과함")
    except ValueError:
        pass
    return f"충격 응력만 0, 떨림 주파수만 {p_f1:.2f} (= (95 − {y['f1']:.1f}) / 95 × 10), 빈 선택은 거절"


def test_model_slot_fallback():
    """models/ 에 파일이 있어도 PyTorch 가 없거나 못 읽으면 대체 모델로 (이유를 남김). 학습 모델 코드는 문법 확인."""
    for f in ("real.py", "fp11/data.py", "fp11/deepsdf.py", "fp11/surrogate.py", "fp11/pino.py"):
        py_compile.compile(os.path.join(os.path.dirname(O.__file__), f), doraise=True)
    keep = O.MODELS
    with tempfile.TemporaryDirectory() as d:
        with zipfile.ZipFile(os.path.join(d, "results_fp11.zip"), "w") as z:
            z.writestr("runs/sdf.pt", b"not a checkpoint")
            z.writestr("runs/fno.pt", b"not a checkpoint")
            z.writestr("runs/report.md", "x")
        np.savez(os.path.join(d, "grid_meta.npz"), nx=88)
        try:
            O.MODELS = d
            O._BACKEND.clear()
            files = O.model_files()
            assert files and all(os.path.exists(f) for f in files[:2]), files
            B = O.backend()
            assert B.id.startswith("anchor") and B.reason, (B.id, B.reason)
            stamp = O.models_stamp()
        finally:
            O.MODELS = keep
            O._BACKEND.clear()
    assert stamp != "none" and O.models_stamp() == "none"
    return f"zip 풀기 OK, 대체 모델 사용 — 이유: {B.reason[:60]}"
