"""간이 물리 최적화 (formproof_input.optimize): T01 1차 설계에서 짧게 돌려 동작 확인."""
import os, sys, tempfile
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from formproof_input import optimize, fem                      # noqa: E402
from formproof_input.pipeline import design                    # noqa: E402


def test_simple_optimizer():
    """T01, 12 반복: 목적 함수 감소 · 부피 = 목표 · 0/1 형상 연결 · 1차 설계보다 흔들림 · 응력 개선."""
    d = tempfile.mkdtemp()
    design("", None, None, "T01", d)
    m = optimize.run(d, iters=12, vol_frac=0.15, eval_every=6, render=False)
    h = m["history"]
    obj = [r["objective"] for r in h if "objective" in r]
    assert obj[-1] < 0.25 * obj[0], obj
    assert abs(h[-1]["volume_frac"] - 0.15) < 0.005, h[-1]["volume_frac"]
    ev, first = h[-1]["eval"], m["first_design"]
    assert ev["connected"] and ev["parts"] == 1, ev
    assert ev["shaking"] < first["shaking"] and ev["checks"]["stress"]["value"] < first["checks"]["stress"]["value"], (ev, first)
    for f in ("history.npz", "metrics.json", "final_design.npy", "final_density.npy"):
        assert os.path.isfile(os.path.join(d, "opt", f)), f
    fd = np.load(os.path.join(d, "opt", "final_design.npy"))
    assert fd.shape == np.load(os.path.join(d, "initial_design.npy")).shape       # 엔진 START_RHO 형식과 같음
    return f"{first['mass_g']} g · 흔들림 {first['shaking']} → {ev['mass_g']} g · {ev['shaking']} (반복 12, {m['seconds']} s)"
