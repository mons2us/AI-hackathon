"""데모 제품 시나리오 (TV 스탠드 · AI 글래스) — 해석 · 인식 · 파이프라인 검증.  python tests/test_products.py"""
import glob
import math
import os
import sys
import tempfile
import zlib
import base64

import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from formproof_input import pipeline  # noqa: E402
from formproof_input.products import glasses as G  # noqa: E402
from formproof_input.products import tv_stand as TV  # noqa: E402
from formproof_input.products.voxfem import VoxModel  # noqa: E402
from formproof_input.sketch import draw_image, perturb  # noqa: E402


def test_voxfem_cantilever():
    """복셀 FEM: 외팔보 100×10×10 mm, 끝 100 N → 처짐 PL³/3EI, 뿌리 응력 6PL/bh² (±5 % / ±20 %)."""
    L, b, E, P = 100.0, 10.0, 200000.0, 100.0
    occ = np.ones((10, 10, 100), bool)
    V = VoxModel(occ, (0, 0, 0), 1.0, E, 0.3)
    xyz = V.node_xyz
    fixed = np.where(xyz[:, 0] <= 1e-6)[0]
    tip = np.where(xyz[:, 0] >= L - 1e-6)[0]
    F = V.rigid_load(tip, xyz[tip].mean(0), (0, 0, -P))
    u = V.solve(fixed, F)
    d = -float(np.mean(u[3 * tip + 2]))
    d_th = P * L ** 3 / (3 * E * b ** 4 / 12)
    assert abs(d / d_th - 1) < 0.05, (d, d_th)
    vm = V.von_mises(u)
    root = vm[V.el_xyz[:, 0] < 3].max()
    s_th = 6 * P * L / b ** 3
    assert abs(root / s_th - 1) < 0.2, (root, s_th)
    return f"처짐 {d:.3f} / 이론 {d_th:.3f} mm, 뿌리 응력 {root:.2f} / {s_th:.2f} MPa"


def test_tv_tip_hand_calc():
    """넘어짐 각 = atan(무게중심 → 지지면 가장자리 거리 / 무게중심 높이) 손계산과 같음."""
    tv = TV.tv_spec(55)
    info = dict(foot=[(-200, -150), (200, -150), (200, 150), (-200, 150)], tv_box=dict(center=[0, 0, 900], size=[tv["W"], 60, tv["H"]]))
    r = TV.tip_checks(tv, info, mass_stand_kg=0.0)
    assert abs(r["tip_deg"] - math.degrees(math.atan2(150, 900))) < 0.05, r
    Fh = 0.13 * tv["mass_kg"] * 9.81
    h = 900 + tv["H"] / 2
    assert abs(r["push_margin"] - (tv["mass_kg"] * 9.81 * 150) / (Fh * h)) < 0.01, r
    return f"넘어짐 각 {r['tip_deg']}° = atan(150/900), 수평력 여유 {r['push_margin']}"


def test_tv_conditions_iec():
    """IEC 62368-1 수치: 13 % (≤ 250 N) 수평력, 50 % (≤ 100 N) 하향력, 10° 기울임."""
    for size in (55, 85):
        tv = TV.tv_spec(size)
        c = {x["key"]: x for x in TV.conditions(tv, "TV01", "steel", "거실장 위")}
        W = tv["mass_kg"] * 9.81
        assert f"{min(0.13 * W, 250):.0f} N" in c["push"]["value"] and f"{min(0.5 * W, 100):.0f} N" in c["down"]["value"]
        assert "10°" in c["tilt"]["value"]
    assert TV.tv_spec(55)["mass_kg"] == 17.7
    return "55형 23 N · 87 N, 85형 수평력 · 하향력 상한 적용"


def test_tv_sketch_match():
    """정면 스케치: 정형 4/4 + 합성 손그림 (TV 있음/없음, ±8° 기울임) 40장 중 ≥ 95 %, 예시 손그림 4/4.
    알려진 혼동: TV가 그림 대부분을 차지하고 받침이 아주 작으면 TV01 ↔ TV02."""
    ok = n = 0
    rng = np.random.default_rng(7)
    for t in TV.TEMPLATES:
        for k in range(11):
            st = TV.front_strokes(t["id"], with_tv=(k % 2 == 0))
            if k:
                st = perturb(st, rng, 1.0, drop=())
            m = TV.match(draw_image(st, px=480))
            ok += m["candidates"][0]["id"] == t["id"]
            n += 1
    assert ok >= 0.95 * n, (ok, n)
    for f in sorted(glob.glob(os.path.join(HERE, "examples", "hand", "hand_TV*.png"))):
        g = pipeline.decode_image(open(f, "rb").read())
        assert TV.match(g)["candidates"][0]["id"] == os.path.basename(f)[5:9], f
    return f"{ok}/{n} + 예시 손그림 4장"


def test_tv_designs():
    """4개 템플릿: 한 몸(바닥 접지) · 판정 전부 충족 · 결과 파일."""
    out = []
    for t in TV.TEMPLATES:
        with tempfile.TemporaryDirectory() as d:
            rep = TV.design("55인치", template=t["id"], out=d)
            assert rep["judge"]["pass_"], (t["id"], rep["judge"])
            for f in ("design_1st.step", "design_1st.stl", "design_1st_drawing.pdf", "spec.json", "report.json", "handoff.zip"):
                assert os.path.exists(os.path.join(d, f)), f
        out.append(f"{t['id']} {rep['extra']['tip']['tip_deg']}°")
    return ", ".join(out)


def _truth(style):
    S = G.STYLES[style]
    return 50.0, S["h"] * 50.0 / S["w"]


def test_glasses_photo_analysis():
    """합성 제품 사진 (2 형상 × 투명/어두운 렌즈 × 기울임 ±3°): 렌즈 폭 · 높이 ±4 %, 형상 분류, 브리지 ±2 mm."""
    worst = 0.0
    for style in ("slim_oval", "cat_eye"):
        w0, h0 = _truth(style)
        br0 = 18.0 * 50.0 / G.STYLES[style]["w"]
        for dark in (False, True):
            for tilt in (-3.0, 0.0, 3.0):
                an = G.analyze_photo(G.render_photo(style, seed=int(tilt + 5), dark_lens=dark, tilt_deg=tilt))
                assert an is not None, (style, dark, tilt)
                e = max(abs(an["lens_w"] / w0 - 1), abs(an["lens_h"] / h0 - 1))
                worst = max(worst, e)
                assert e < 0.04, (style, dark, tilt, an["lens_w"], an["lens_h"])
                assert an["style"] == style, (style, dark, tilt, an["features"])
                assert abs(an["bridge"] - br0) < 2.0 or dark, (style, an["bridge"], br0)
    return f"12장 모두 인식, 치수 오차 최대 {worst * 100:.1f} %"


def test_glasses_no_false_positive():
    """자전거 거치대 예시 그림 (손그림 · 정형 · 발표 스케치) 은 안경으로 잡지 않음."""
    from PIL import Image
    fs = [f for f in glob.glob(os.path.join(HERE, "examples", "**", "*.png"), recursive=True)]
    bad = [f for f in fs if G.is_glasses_image(np.asarray(Image.open(f).convert("L"), float) / 255.0)]
    assert not bad, bad[:5]
    return f"{len(fs)}장 중 0장"


def test_glasses_design():
    """무게 · 클램프 힘(문헌 범위) · 응력 · 온도 판정, 클램프 힘 = 강성 × 벌림, 온도 = P/(hA)."""
    with tempfile.TemporaryDirectory() as d:
        rep = G.design("", image=G.render_photo("slim_oval"), out=d)
    fe, th = rep["extra"]["fem"], rep["extra"]["thermal"]
    assert rep["judge"]["pass_"], rep["judge"]
    assert abs(fe["clamp_N"] - fe["k_N_per_mm"] * G.SPREAD_EACH) < 0.01
    assert abs(th["dT"] - G.SOC_W / (G.H_CONV * th["area_cm2"] * 1e-4)) < 0.2
    assert 35 <= rep["extra"]["mass"]["total_g"] <= 50
    return f"{rep['extra']['mass']['total_g']} g, 클램프 {fe['clamp_N']} N, 다리 {th['T']} °C"


def test_routing_and_heat_payload():
    """제품 선택: 지정 · 템플릿 번호 · 문장 단어 · 안경 사진. 큰 격자 분포는 zlib 압축 → 풀면 절점 수와 같음."""
    R = pipeline.route_product
    assert R("55인치 TV 스탠드") == "tv" and R("젠틀몬스터 안경") == "glasses" and R("자갈길에서 안 흔들리게") == "bike"
    assert R(template="TV03") == "tv" and R(template="T01") == "bike" and R(product="glasses") == "glasses"
    assert R(image=G.render_photo("cat_eye") / 255.0) == "glasses"
    with tempfile.TemporaryDirectory() as d:
        rep = pipeline.design("55인치", template="TV02", out=d, with_mesh=True)
    nx, ny, nz = rep["heat"]["grid"]["nodes"]
    f = rep["heat"]["fields"]["stress"]
    raw = zlib.decompress(base64.b64decode(f["qz"])) if "qz" in f else base64.b64decode(f["q"])
    assert len(raw) == nx * ny * nz
    return f"TV02 분포 {nx}×{ny}×{nz} 절점"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            print(name, fn())
