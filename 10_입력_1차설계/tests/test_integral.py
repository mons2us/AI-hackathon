"""P01 일체형 (발표 사례) — 발표 · 팀 구현 패키지와 같은 형상 · 설계 · 물리 조건인지.

  python tests/test_integral.py            (캐시된 팀 엔진 결과 사용, 약 1분)
  RUN_ENGINE=1 python tests/test_integral.py   (팀 엔진으로 처음 설계를 다시 계산, +1분)
"""
import json
import os
import subprocess
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from formproof_input import integral as I  # noqa: E402

REF = os.path.join(I.PKG, "data", "reference")
SLIDE = {   # 발표초안 v83 7 · 10 · 22쪽 숫자 (무게 g, 1차 Hz, 최대 흔들림 배, 폰 온도 °C)
    "base": (94.9, 30.5, 5.58, 32.57), "llm_A": (87.7, 150.6, 1.37, 22.64), "llm_B": (79.8, 109.6, 2.95, 20.55),
    "llm_C": (80.0, 89.7, 6.57, 20.56), "formproof": (77.1, 153.9, 1.39, 20.7), "formproof_body": (93.9, 168.0, 1.27, 20.77)}
VERDICT = {"base": False, "llm_A": False, "llm_B": False, "llm_C": False, "formproof": True, "formproof_body": True}


def _opt_int_sets():
    """opt_int.py (GRIP=2) 의 집합 식을 그대로 다시 계산 (요소 중심 좌표)."""
    c, _ = I.grid_centres()
    xc, yc, zc = c.T
    t = np.radians(35)
    Xw, Zw, rr = xc * np.cos(t) - zc * np.sin(t), xc * np.sin(t) + zc * np.cos(t), np.sqrt(xc ** 2 + zc ** 2)
    XR, PL, ZB = -10., 150., 24.
    bore = rr < 16.1
    slit = (np.abs(Xw) <= 1) & (Zw < 0) & (rr < 26)
    foot = (xc > XR) & (xc < XR + PL)
    xl = xc - XR
    plate = foot & (zc > ZB) & (zc < ZB + 6)
    phone = foot & (zc > ZB + 6) & (zc < ZB + 14)
    ledge = plate & (xl < 8) & (yc < 16)
    toppad = plate & (xl > 136) & (yc < 16)
    hous = (xc > 55) & (xc < 75) & (zc > 18) & (zc < 30)
    chan = (xc > 60) & (xc < 70) & (zc > 20) & (zc < 28) & (yc > 5)
    slot = (xc > 63) & (xc < 67) & (zc > 27) & (zc < 30) & (yc > 26)
    hook = (xc > -14) & (xc < -10) & (yc < 15) & (zc > ZB)
    jaw = hous & ~chan & ~slot
    void = bore | slit | phone | (((zc > ZB) & ~plate) & ~hook) | chan | slot
    rail = (xc > 102) & (xc < 150) & (yc < 10) & (zc > 12) & (zc < 30)
    rch = (xc > 104) & (yc < 5) & (zc > 14) & (zc < 22) & (xc < 151)
    rsl = (xc > 128) & (xc < 151) & (yc < 2.2) & (zc > 21) & (zc < 30)
    rail = rail & ((zc < 24) | rsl)
    rs = rail & ~(rch | rsl)
    void = (void & ~rs) | (rail & ~rs)
    attach = ((jaw & (zc > 28)) | ledge | toppad | (hook & (zc > ZB + 6)) | (rail & (zc > 28))) & ~void
    src = phone & (zc < ZB + 8) & (xl > 100) & (xl < 125) & (yc < 10)
    return dict(attach=attach, heat_src=src)


def test_grid_same_as_team():
    """설계 · 고정 · 빈 영역, 판 · 폰 층 = 팀 data/grid_meta.npz (요소 하나까지), 연결 요소 · 발열 요소 = opt_int 식."""
    M = I.masks()
    g = np.load(os.path.join(I.PKG, "data", "grid_meta.npz"))
    for k in ("solid", "void", "design", "plate", "phone"):
        assert (M[k] == g[k].astype(bool)).all(), k
    assert (np.where(M["design"])[0] == g["didx"]).all()
    o = _opt_int_sets()
    for k in ("attach", "heat_src"):
        assert (M[k] == o[k]).all(), k
    return f"설계 {M['design'].sum():,} · 고정 {M['solid'].sum():,} · 빈 {M['void'].sum():,} 요소 일치"


def test_first_design_is_presentation_base():
    """1차 설계 = 발표 '처음 설계 (판 + 기둥)' = mkbase_int.py 식(88 격자)."""
    r = I.base_design()
    c, _ = I.grid_centres()
    x, y, z = c.T
    want = (((y < 10) & (z > 20) & (z < 28) & (x > 0) & (x < 140)) | ((x > -10) & (x < 140) & (z > 28) & (z < 30))).astype(float)
    assert (r == want).all() and int(r.sum()) == 2900
    return "2,900 요소 (보 20×8 + 판 2 mm)"


def test_conditions_same_as_team_spec():
    """말 + 스케치 → 설계 명세 = 팀 spec/bike_mount_spec.json, 판정 기준 = spec/bike_mount_targets.json."""
    team = json.load(open(os.path.join(I.PKG, "spec", "bike_mount_spec.json"), encoding="utf-8"))
    mine = I.condition_spec()
    for sec in ("geometry", "objectives", "constraints"):
        for k, v in team[sec].items():
            assert mine[sec][k]["value"] == v["value"], (sec, k, mine[sec][k]["value"], v["value"])
            assert mine[sec][k]["source"] == v["source"], (sec, k, mine[sec][k]["source"], v["source"])
    assert mine["questions_to_user"] == team["questions_to_user"]
    tg = json.load(open(os.path.join(I.PKG, "spec", "bike_mount_targets.json"), encoding="utf-8"))
    mt = I.targets()
    assert all(mt[k] == tg[k] for k in mt) and set(mt) == {k for k in tg if not k.startswith("_")}
    return f"명세 {sum(len(team[s]) for s in ('geometry', 'objectives', 'constraints'))}개 항목 · 판정 기준 5개 일치"


def test_comparison_shapes_same_as_team():
    """10쪽 LLM 단독 A · B · C = llm2rho.py 출력과 같은 격자, FormProof = 최적화 기록 120회."""
    with tempfile.TemporaryDirectory() as td:
        for n, sid in ((1, "llm_A"), (2, "llm_B"), (3, "llm_C")):
            o = os.path.join(td, f"L{n}.npy")
            subprocess.run([sys.executable, os.path.join(I.LLM_DIR, "llm2rho.py"), os.path.join(I.LLM_DIR, f"L{n}.md"), o],
                           check=True, capture_output=True)
            assert (np.load(o) == I.shape(sid)).all(), sid
    return "LLM A·B·C 격자 일치"


def test_numbers_same_as_presentation():
    """같은 팀 엔진(캐시)으로 계산한 수치 = 발표 7 · 10 · 22쪽, 판정도 같음."""
    out = []
    for sid, (m, f1, sh, T) in SLIDE.items():
        r = I.evaluate(I.full_density(I.shape(sid)), tag=sid)
        j = I.judge(r)
        tf = 1.0 if sid == "formproof" else 0.05      # 저장소에는 0/1 로 묶은 기록만 있음(발표 값은 연속 밀도) -> 153.3 vs 153.9 Hz
        assert abs(r["mass_g"] - m) <= 0.05 and abs(r["f"][0] - f1) <= tf, (sid, r["mass_g"], r["f"][0])
        assert abs(j["shake"] - sh) <= 0.02 and abs(r["Tmax"] - T) <= 0.05, (sid, j["shake"], r["Tmax"])
        assert j["pass_"] == VERDICT[sid], (sid, j["fails"])
        out.append(f"{sid} {r['mass_g']} g {r['f'][0]} Hz {j['shake']}배")
    for sid, ref in (("base", "frfint_base35g3.json"), ("formproof_body", "frfint_body_v3.json")):
        e = json.load(open(os.path.join(REF, ref)))
        r = I.evaluate(I.full_density(I.shape(sid)), tag=sid)
        assert r["f"][:4] == e["f"][:4] and r["Tmax"] == e["Tmax"] and r["shock"] == e["shock"], sid
    return " · ".join(out)


def test_engine_reruns_same(force=None):
    """RUN_ENGINE=1: 처음 설계를 팀 엔진으로 다시 계산해 기준 결과(frfint_base35g3.json)와 비교."""
    if not (force or os.environ.get("RUN_ENGINE") == "1"):
        return "건너뜀 (RUN_ENGINE=1)"
    r = I.evaluate(I.full_density(I.base_design()), tag="rerun", use_cache=False)
    e = json.load(open(os.path.join(REF, "frfint_base35g3.json")))
    assert r["f"] == e["f"] and r["mass_g"] == e["mass_g"] and r["Tmax"] == e["Tmax"] and r["vert"]["T"] == e["vert"]["T"]
    return "다시 계산 = 기준 결과"


def test_routing():
    """발표 문장 · 발표 입력 스케치(화면 비율 · 크기 바뀌어도)는 P01, 다른 입력은 아님."""
    from skimage import io, transform
    assert I.is_presentation_text(I.PRESENTATION_TEXT) and I.is_presentation_text("일체형으로 해줘")
    assert not I.is_presentation_text("자갈길에서도 폰이 안 흔들리게, 최대한 가볍게. 갤럭시 S25 울트라, 3D 프린터로 뽑을 거야")
    g = io.imread(I.DEMO_SKETCHES[0])[..., :3].mean(-1) / 255
    c = np.ones((600, 800))
    h = int(800 * g.shape[0] / g.shape[1])
    c[(600 - h) // 2:(600 - h) // 2 + h] = transform.resize(g, (h, 800), anti_aliasing=True)
    assert I.matches_presentation_sketch(g) and I.matches_presentation_sketch(c)
    ex = os.path.join(I.INPUT_ROOT, "examples", "hand")
    others = [f for f in sorted(os.listdir(ex)) if f.endswith(".png")][:40]
    assert not any(I.matches_presentation_sketch(io.imread(os.path.join(ex, f)) / 255.0) for f in others)
    return f"발표 문장 · 스케치 → P01, 다른 예시 {len(others)}장 → 아님"


def test_pipeline_outputs():
    """pipeline.design(발표 문장) → P01 명세 · 1차 설계 · STL(출력 몸체) · STEP · 도면 · 넘길 파일."""
    from formproof_input import pipeline
    with tempfile.TemporaryDirectory() as td:
        rep = pipeline.design(I.PRESENTATION_TEXT, out=td)
        assert rep["kind"] == "integral" and rep["template"]["id"] == "P01"
        for f in I.HANDOFF + ["handoff.zip", "side_view.png", "design_1st_drawing.png"]:
            assert os.path.exists(os.path.join(td, f)), f
        assert abs(rep["cad"]["mass_g"] - 86.5) < 1.0, rep["cad"]           # 팀 build_body 절차 = 86.5 g
        assert rep["engine_result"]["f"][0] == 30.5 and not rep["judge"]["pass_"]
        assert [r["id"] for r in rep["compare"]] == [s[0] for s in I.SHAPES]
    return f"출력 몸체 {rep['cad']['mass_g']} g · STEP {rep['cad']['step_mass_g']} g · 판정 미달(처음 설계)"


if __name__ == "__main__":
    for fn in (test_grid_same_as_team, test_first_design_is_presentation_base, test_conditions_same_as_team_spec,
               test_comparison_shapes_same_as_team, test_numbers_same_as_presentation, test_routing, test_pipeline_outputs,
               test_engine_reruns_same):
        print(fn.__name__, fn())
