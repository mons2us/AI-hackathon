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
    """넘어짐 각 = atan(무게중심 → 접지 다각형 가장자리 거리 / 무게중심 높이), 수평력 여유 = W·d / (F·h) 손계산."""
    tv = TV.tv_spec(27)
    info = dict(foot=[(-200, -150), (200, -150), (200, 150), (-200, 150)], tv_box=dict(center=[0, 0, 900], size=[tv["W"], 30, tv["H"]]))
    r = TV.tip_checks(tv, info, mass_stand_kg=0.0)
    assert abs(r["tip_deg"] - math.degrees(math.atan2(150, 900))) < 0.05, r
    W = tv["mass_kg"] * 9.81
    h = 900 + tv["H"] / 2
    assert abs(r["push_margin"] - (W * 150) / (0.13 * W * h)) < 0.01, r
    assert abs(r["caster_max_N"] - (W / 4 + 0.13 * W * h / (2 * 2 * 150))) < 0.5, r      # 4 바퀴, 앞뒤 수평력
    return f"넘어짐 각 {r['tip_deg']}° = atan(150/900), 수평력 여유 {r['push_margin']}, 바퀴 {r['caster_max_N']} N"


def test_tv_conditions_iec():
    """IEC 62368-1 수치: 전체 무게의 13 % (≤ 250 N) 수평력, 50 % (≤ 100 N) 하향력, 10° 기울임 · 스탠바이미 27형 실측값."""
    tv = TV.tv_spec(27)
    assert (tv["W"], tv["H"], tv["mass_kg"]) == (621.0, 361.0, 4.8)
    for total in (17.5, 250.0):
        c = {x["key"]: x for x in TV.conditions(tv, "TV01", total)}
        W = total * 9.81
        assert f"{min(0.13 * W, 250):.0f} N" in c["push"]["value"] and f"{min(0.5 * W, 100):.0f} N" in c["push"]["value"]
        assert "10°" in c["tilt"]["value"]
    return "17.5 kg: 22 N · 86 N, 250 kg: 상한 250 N · 100 N"


def test_tv_no_clash():
    """스탠드(기둥 · 캐리지 · 헤드)는 화면 뒤 — 화면과 겹침 0 (가로 · 세로 × 높이 최소/최대 × 27 · 43형)."""
    out = []
    for size in (27, 43):
        tv = TV.tv_spec(size)
        for t in TV.TEMPLATES:
            lo, hi = TV.center_range(tv, t["orient"])
            for zc in (lo, hi):
                _, info = TV.build(t["id"], tv, zc)
                assert info["clash_mm3"] <= 1.0, (size, t["id"], zc, info["clash_mm3"])
                assert info["layout"]["back"] < 0
        out.append(f"{size}형")
    return "겹침 0 mm³ — " + ", ".join(out)


def test_tv_sketch_match():
    """정면 스케치 (화면 있음): 정형 + 합성 손그림(±8° 기울임 · 축척) 가로/세로 32/32, 높이 읽기 정형 ±15 mm, 예시 손그림."""
    ok = n = 0
    rng = np.random.default_rng(7)
    tv = TV.tv_spec(27)
    worst_clean = 0.0
    for t in TV.TEMPLATES:
        for k in range(16):
            zc = (884, 950, 1020, 1084)[k % 4]
            st = TV.front_strokes(t["id"], zc=zc)
            if k:
                st = perturb(st, rng, 1.0, drop=())
            img = draw_image(st, px=480)
            m = TV.match(img)
            ok += m["candidates"][0]["id"] == t["id"]
            n += 1
            if k == 0:
                worst_clean = max(worst_clean, abs(TV.height_from_sketch(img, t["id"], tv) - zc))
    assert ok == n, (ok, n)
    assert worst_clean < 15, worst_clean
    for f in sorted(glob.glob(os.path.join(HERE, "examples", "hand", "hand_TV*.png"))):
        g = pipeline.decode_image(open(f, "rb").read())
        assert TV.match(g)["candidates"][0]["id"] == os.path.basename(f)[5:9], f
    return f"{ok}/{n}, 높이 오차(정형) ≤ {worst_clean:.0f} mm + 예시 손그림"


def test_tv_designs():
    """가로 · 세로 1차 설계: 판정(기울임 · 응력 · 흔들림 · 바퀴) 충족, 힘 시험은 참고 행, 결과 파일."""
    out = []
    for t in TV.TEMPLATES:
        with tempfile.TemporaryDirectory() as d:
            rep = TV.design("", template=t["id"], out=d, with_mesh=True)
            ok = {r["key"]: r["ok"] for r in rep["judge"]["rows"]}
            # 1차 설계 = 스케치 비율 그대로 (작은 받침 · 가는 기둥) -> 넘어짐 · 흔들림 미충족 (최적화 대상), 응력 · 바퀴는 충족
            assert not rep["judge"]["pass_"] and not ok["tilt"] and not ok["defl"] and ok["stress"] and ok["caster"], (t["id"], ok)
            assert all(r.get("ref") for r in rep["judge"]["rows"] if r["key"] in ("push", "down"))
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
    """공식 제품 사진 → 'gm' 템플릿 1차 설계: 무게 · 피부 온도 · 클램프 힘(너무 조임) 미충족(통 아세테이트 굵은 뿔테 · 방열 시트 없음), 응력 충족.
    클램프 힘 = 강성 × 벌림, 온도 = P / (h · 둘레 · (SoC 길이 + 2/m)), m = √(hP/kA) (핀 이론) 손계산."""
    import math as M
    photo = pipeline.decode_image(open(os.path.join(HERE, "examples", "glasses", "젠틀몬스터_구글_삼성_AI글래스.jpg"), "rb").read())
    with tempfile.TemporaryDirectory() as d:
        rep = G.design("", image=photo, out=d, with_mesh=True)
    assert rep["template"]["id"] == "AG-gm" and rep["template"]["chosen_by"] == "공식 제품 사진 → 템플릿"
    fe, th = rep["extra"]["fem"], rep["extra"]["thermal"]
    ok = {r["key"]: r["ok"] for r in rep["judge"]["rows"]}
    assert not ok["mass"] and not ok["skin"] and not ok["clamp_hi"] and ok["clamp_lo"] and ok["clamp_vm"] and ok["bridge_vm"], ok
    assert abs(fe["clamp_N"] - fe["k_N_per_mm"] * G.SPREAD_EACH) < 0.01
    t = G.STYLES["gm"]["temple"]
    per, ac = 2 * (t["h40"] + t["t"]) * 1e-3, t["h40"] * t["t"] * 1e-6       # 다리 앞쪽 부품실 단면 (높이 14.5 × 두께 5.5)
    m = M.sqrt(G.H_CONV * per / (G.K_FRAME * ac))
    dT = G.SOC_W / (G.H_CONV * per * (G.SOC_LEN * 1e-3 + 2 / m))
    assert abs(th["dT"] - dT) < 0.1, (th, dT)
    return f"{rep['extra']['mass']['total_g']} g, 클램프 {fe['clamp_N']} N, 다리 {th['T']} °C (손계산 ΔT {dT:.1f} K)"


def test_glasses_heat_symmetric():
    """착용 벌림 · 브리지 누름(둘 다 좌우 대칭 하중)의 응력 · 변위 분포가 좌우 대칭이고, CAD 표면에 값이 다 있음 (끊김 없음)."""
    with tempfile.TemporaryDirectory() as d:
        rep = G.design("", out=d, with_mesh=True, style="gm")
    g = rep["heat"]["grid"]
    nx, ny, nz = g["nodes"]
    assert abs(g["origin"][0] + (nx - 1) * g["h"] / 2) < 1e-6          # 격자가 x = 0 에 대칭
    res = {}
    for k in ("clamp_stress", "clamp_disp", "bridge_stress", "bridge_disp"):
        f = rep["heat"]["fields"][k]
        q = np.frombuffer(zlib.decompress(base64.b64decode(f["qz"])) if "qz" in f else base64.b64decode(f["q"]), np.uint8)
        q = q.reshape(nz, ny, nx).astype(float)
        both = (q != 255) & (q[:, :, ::-1] != 255)
        assert ((q != 255) == (q[:, :, ::-1] != 255)).mean() > 0.999                   # 값 있는 자리 대칭
        d = np.abs(q - q[:, :, ::-1])[both] / 254
        res[k] = (float(np.percentile(d, 99)), float(d.max()))
    # 변위는 전체가 대칭, 응력은 99 % 절점이 대칭 (나머지는 오른쪽 카메라 Ø6 · 왼쪽 LED Ø2 처럼 실제로 좌우가 다른 앞면 장식 둘레)
    for c in ("clamp", "bridge"):
        assert res[c + "_disp"][1] < 0.02 and res[c + "_stress"][0] < 0.08, res
    # 화면에 그리는 CAD 표면 꼭짓점마다 값이 있음 (브라우저와 같은 삼선형 보간 · 가중치 > 0.03)
    from scipy.ndimage import map_coordinates
    V = np.frombuffer(base64.b64decode(rep["mesh"]["pos"]), np.float32).reshape(-1, 3).astype(float)
    c = (V - np.array(g["origin"])) / g["h"]
    w = map_coordinates((q != 255).astype(float), [c[:, 2], c[:, 1], c[:, 0]], order=1, mode="nearest")
    assert (w > 0.03).mean() > 0.999, (w > 0.03).mean()
    return (f"착용 벌림 · 브리지 누름: 변위 좌우 차 최대 {max(res['clamp_disp'][1], res['bridge_disp'][1]) * 100:.1f} %, "
            f"응력 좌우 차 99 % 절점 ≤ {max(res['clamp_stress'][0], res['bridge_stress'][0]) * 100:.1f} % (색 척도 대비, 카메라 · LED 둘레 제외), "
            f"표면 꼭짓점 {len(V):,}개 모두 값 있음")


def test_routing_and_heat_payload():
    """제품 선택: 지정 · 템플릿 번호 · 문장 단어 · 안경 사진. 큰 격자 분포는 zlib 압축 → 풀면 절점 수와 같음."""
    R = pipeline.route_product
    assert R("27인치 TV 스탠드") == "tv" and R("젠틀몬스터 안경") == "glasses" and R("자갈길에서 안 흔들리게") == "bike"
    assert R(template="TV03") == "tv" and R(template="T01") == "bike" and R(product="glasses") == "glasses"
    assert R(image=G.render_photo("cat_eye") / 255.0) == "glasses"
    with tempfile.TemporaryDirectory() as d:
        rep = pipeline.design("", template="TV02", out=d, with_mesh=True)
    nx, ny, nz = rep["heat"]["grid"]["nodes"]
    f = rep["heat"]["fields"]["stress"]
    raw = zlib.decompress(base64.b64decode(f["qz"])) if "qz" in f else base64.b64decode(f["q"])
    assert len(raw) == nx * ny * nz
    return f"TV02 분포 {nx}×{ny}×{nz} 절점"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            print(name, fn())


def test_template_db_speed():
    """템플릿 결과 DB: 두 번째부터는 계산 없이 불러옴 — 시나리오마다 4 s 이내 (여기서는 1.5 s 이내로 확인)."""
    import time
    from formproof_input import integral
    photo = pipeline.decode_image(open(os.path.join(HERE, "examples", "glasses", "젠틀몬스터_구글_삼성_AI글래스.jpg"), "rb").read())
    sk = pipeline.decode_image(open(os.path.join(HERE, "examples", "hand", "hand_TV01.png"), "rb").read())
    cases = [("P01", lambda d: pipeline.design(integral.PRESENTATION_TEXT, out=d, with_mesh=True)),
             ("TV", lambda d: pipeline.design("", sk, None, out=d, with_mesh=True, product="tv")),
             ("AI 글래스", lambda d: pipeline.design("", None, photo, out=d, with_mesh=True, product="glasses")),
             ("T01", lambda d: pipeline.design("", template="T01", out=d, with_mesh=True, product="bike"))]
    out = []
    for name, fn in cases:
        with tempfile.TemporaryDirectory() as d:
            fn(d)                                            # 처음 (DB 가 비었으면 계산 · 저장)
        with tempfile.TemporaryDirectory() as d:
            t = time.time()
            rep = fn(d)
            s = time.time() - t
            assert os.path.exists(os.path.join(d, "design_1st.step")) and rep.get("mesh"), name
        assert s < 1.5, (name, s)
        out.append(f"{name} {s:.2f} s")
    return ", ".join(out)
