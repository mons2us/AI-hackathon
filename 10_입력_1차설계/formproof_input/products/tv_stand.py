"""TV 스탠드 — 스케치 → 템플릿 → 1차 설계(CAD · 도면) + 물리 조건 + 간이 판정 (데모 시나리오).

좌표 (mm): x = TV 폭 방향(좌우), y = 앞뒤(앞 = −y, 시청자 쪽), z = 위, 바닥 z = 0.
템플릿 4종 (TV 스탠드로 흔히 쓰는 구조):
  TV01 센터 받침형 — 판형 받침 + 짧은 기둥 + VESA 브래킷 (TV 아래 중앙)
  TV02 양발형      — TV 아래 양끝 두 발 (판 다리), 화면 하단 프레임에 체결
  TV03 이젤형      — 앞다리 2 + 뒷다리 1 삼각대, 앞다리에 VESA 판
  TV04 바닥 스탠드  — 무거운 판 받침 + 높은 기둥 + VESA 브래킷 (시청 높이)
물리 조건: IEC 62368-1 안정성(10° 기울임 / 무게 13 % 수평력 ≤ 250 N, 1.5 m 이하에 가함 · 50 % 하향력 ≤ 100 N),
자중 · 수평력에서 응력 ≤ 항복/1.5, TV 윗단 흔들림 ≤ 1 mm(가정). 판정: 넘어짐 = 정역학 계산, 응력 · 처짐 = 복셀 FEM.
"""
import base64
import math
import os
import tempfile
import time

import numpy as np

from ..sketch import Matcher, draw_image, ink_points, perturb  # noqa: F401

SOURCES = {
    "iec62368": dict(title="IEC 62368-1 ed.3 8.6 안정성 시험 (10° 기울임, 13 % 수평력 ≤ 250 N, 50 % 하향력 ≤ 100 N, 1.5 m 이하)",
                     url="https://www.mail-archive.com/emc-pstc@listserv.ieee.org/msg76504.html"),
    "samsung55": dict(title="Samsung 55\" UHD (CU7000) 사양: 1230.5 × 707.2 × 59.9 mm, 13.9 kg(스탠드 제외), VESA 200×200",
                      url="https://shop.prog-it.net/samsung-55cu7000-55in-uhd-3840x2160/cat-p/c/p1004365763/l_en"),
    "samsung55_qn90b": dict(title="Samsung QE55QN90B: 스탠드 제외 17.7 kg, VESA 200×200",
                            url="https://productsupport.johnlewis.com/customer/device/Samsung/QE55QN90BATXXU"),
}
MATERIALS = {
    "steel": dict(name="강판 · 강관 (SS275)", E=205000.0, nu=0.3, rho=7.85e-3, yield_mpa=275.0),
    "al": dict(name="알루미늄 6061-T6", E=69000.0, nu=0.33, rho=2.70e-3, yield_mpa=240.0),
    "wood": dict(name="너도밤나무 집성목 (각재)", E=12000.0, nu=0.3, rho=0.72e-3, yield_mpa=40.0),
}
VOXEL = {"TV01": 5.0, "TV02": 3.0, "TV03": 7.0, "TV04": 5.0}      # 부재 두께가 격자 2칸 이상 되게
SF = 1.5
TOP_DEFLECTION_MM = 1.0          # 가정 (팀 TV 스탠드 사례와 같은 값)


def tv_spec(size_in=55):
    """TV 크기 → 패널 치수 · 무게 · VESA. 55형 = 근거(삼성 사양, 무거운 쪽 17.7 kg), 다른 크기는 대각 비례 가정."""
    s = size_in / 55.0
    W, H, D = 1230.5 * s, 707.2 * s, 60.0
    m = 17.7 * s ** 2
    vesa = (200, 200) if size_in <= 55 else (300, 300) if size_in <= 65 else (400, 300)
    src = "근거: 삼성 55형 사양" if size_in == 55 else f"가정: 55형 사양에서 대각 비례(무게 ∝ 크기²) — {size_in}형 실제 사양 확인 필요"
    return dict(size_in=size_in, W=round(W, 1), H=round(H, 1), D=D, mass_kg=round(m, 1), vesa=vesa, source=src)


TEMPLATES = [
    dict(id="TV01", name="센터 받침형", desc="판형 받침 + 짧은 기둥 + VESA 브래킷 (거실장 위)", material="steel", place="거실장 위"),
    dict(id="TV02", name="양발형", desc="TV 아래 양끝 두 발(판 다리), 화면 하단에 체결 (기본 제공 다리)", material="al", place="거실장 위"),
    dict(id="TV03", name="이젤형", desc="앞다리 2 + 뒷다리 1 삼각대(원목 각재), 앞다리에 VESA 판 (바닥)", material="wood", place="바닥"),
    dict(id="TV04", name="바닥 스탠드", desc="H자 받침 + 높은 각관 기둥 + VESA 브래킷 (바닥, 시청 높이)", material="steel", place="바닥"),
]
BY_ID = {t["id"]: t for t in TEMPLATES}


# ------------------------------------------------------------------ geometry
def layout(tid, tv):
    """Template + TV -> dimensions of the stand, TV placement, floor contact polygon, load points."""
    W, H, D = tv["W"], tv["H"], tv["D"]
    vx, vz = tv["vesa"]
    if tid == "TV01":
        g = dict(base=(min(0.37 * W, 450.0), 280.0, 8.0), neck=(80.0, 40.0, 4.0), gap=60.0, bracket=(vx + 60, vz + 40, 5.0))
        tv_bottom = g["base"][2] + g["gap"]
        tv_y = 30.0
    elif tid == "TV02":
        g = dict(foot_x=0.5 * W - 0.12 * W, foot_len=260.0, foot_t=12.0, foot_h=90.0, slot=18.0)
        tv_bottom = g["foot_h"] - 25.0
        tv_y = 0.0
    elif tid == "TV03":
        g = dict(leg=(50.0, 35.0), spread=0.55 * W, rear=700.0, vesa_plate=(vx + 80, vz + 60, 18.0))
        tv_bottom = 650.0
        tv_y = -40.0
    else:
        g = dict(base=(560.0, 600.0, 12.0), foot_w=70.0, pole=(60.0, 60.0, 4.0), bracket=(vx + 60, vz + 40, 5.0))
        tv_bottom = 1050.0 - H / 2
        tv_y = 30.0
    tv_c = np.array([0.0, tv_y - D / 2 - 5.0, tv_bottom + H / 2])
    return dict(g=g, tv_center=tv_c, tv_bottom=tv_bottom)


def _tube(w, d, wall, height, base):
    """Vertical rectangular tube, bottom centre at `base`."""
    import cadquery as cq
    x, y, z = base
    return (cq.Workplane("XY").rect(w, d).rect(w - 2 * wall, d - 2 * wall).extrude(height).translate((x, y, z)))


def _bar(p0, p1, w, t):
    """Rectangular bar between two points (CadQuery)."""
    import cadquery as cq
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    d = p1 - p0
    L = float(np.linalg.norm(d))
    n = d / L
    x = np.cross(n, [0.0, 0.0, 1.0])
    if np.linalg.norm(x) < 1e-6:
        x = np.array([1.0, 0.0, 0.0])
    x = x / np.linalg.norm(x)
    pl = cq.Plane(origin=cq.Vector(*p0), xDir=cq.Vector(*x), normal=cq.Vector(*n))
    return cq.Workplane(pl).rect(w, t).extrude(L)


def build(tid, tv):
    """CadQuery parts (stand only) + TV panel box (context) + contact polygon + load node selectors."""
    import cadquery as cq
    L = layout(tid, tv)
    g, c = L["g"], L["tv_center"]
    W, H, D = tv["W"], tv["H"], tv["D"]
    box = lambda dx, dy, dz, x, y, z: cq.Workplane().box(dx, dy, dz).translate((x, y, z))
    back = c[1] + D / 2                                 # TV back face y
    vz0 = c[2]                                          # VESA centre height (TV centre)
    parts = []
    if tid == "TV01":
        bx, by, bt = g["base"]
        parts.append(box(bx, by, bt, 0, 40, bt / 2).edges("|Z").fillet(20))
        top = vz0 + 0.15 * H
        nx_, ny_, nw = g["neck"]
        parts.append(_tube(nx_, ny_, nw, top - bt, (0, back + ny_ / 2 + 8, bt)))
        bw, bh, btk = g["bracket"]
        parts.append(box(bw, btk, bh, 0, back + btk / 2, vz0))
        parts.append(box(nx_, 10, 60, 0, back + btk + 4, top - 30))          # bracket -> neck tab
        foot = [(-bx / 2, 40 - by / 2), (bx / 2, 40 - by / 2), (bx / 2, 40 + by / 2), (-bx / 2, 40 + by / 2)]
        mount = dict(kind="vesa", y=back, z=vz0, w=bw, h=bh)
    elif tid == "TV02":
        fx, fl, ft, fh, sl = g["foot_x"], g["foot_len"], g["foot_t"], g["foot_h"], g["slot"]
        for s in (-1, 1):
            prof = (cq.Workplane("YZ").polyline([(-fl / 2, 0), (fl / 2, 0), (fl / 2 - 30, 14), (sl / 2 + 4, fh - 10), (sl / 2 + 4, fh),
                                                 (-sl / 2 - 4, fh), (-sl / 2 - 4, fh - 10), (-fl / 2 + 30, 14)]).close()
                    .extrude(ft / 2, both=True).translate((s * fx, c[1], 0)))
            prof = prof.cut(box(ft + 2, D + 1, 40, s * fx, c[1], L["tv_bottom"] + 20))
            parts.append(prof)
        foot = [(-fx - ft / 2, c[1] - fl / 2), (fx + ft / 2, c[1] - fl / 2), (fx + ft / 2, c[1] + fl / 2), (-fx - ft / 2, c[1] + fl / 2)]
        mount = dict(kind="slots", z=L["tv_bottom"], xs=(-fx, fx), w=ft, y=c[1])
    elif tid == "TV03":
        lw, lt = g["leg"]
        sp, rear = g["spread"], g["rear"]
        apex = np.array([0.0, back + 40, vz0 + 0.5 * H + 150])
        feet_f = [np.array([-sp / 2, back - 300, 0.0]), np.array([sp / 2, back - 300, 0.0])]
        foot_r = np.array([0.0, back + rear, 0.0])
        for f in feet_f + [foot_r]:
            parts.append(_bar(f, apex, lw, lt))
        pw, ph, pt = g["vesa_plate"]
        parts.append(box(pw, pt, ph, 0, back + pt / 2, vz0))
        f_at = lambda f, z: f + (apex - f) * (z / apex[2])
        for zc in (vz0 - ph / 2 + 20, vz0 + ph / 2 - 20):       # cross bars at the bottom and top of the VESA plate
            a, b = f_at(feet_f[0], zc), f_at(feet_f[1], zc)
            parts.append(_bar(a - [20, 0, 0], b + [20, 0, 0], 30, 30))         # cross bar through both front legs
            y0, y1 = min(a[1], back) - 15, back + pt                             # plate -> cross bar web
            parts.append(box(pw * 0.6, y1 - y0, 40, 0, (y0 + y1) / 2, zc))
        r0 = f_at(foot_r, 300)                                   # spreader: front legs -> rear leg
        m0 = (f_at(feet_f[0], 300) + f_at(feet_f[1], 300)) / 2
        parts.append(_bar(m0, r0, 30, 20))
        parts.append(_bar(f_at(feet_f[0], 300), f_at(feet_f[1], 300), 30, 20))
        foot = [(f[0], f[1]) for f in feet_f] + [(foot_r[0], foot_r[1])]
        mount = dict(kind="vesa", y=back, z=vz0, w=pw, h=ph)
    else:
        bx, by, bt = g["base"]
        fw = g["foot_w"]
        px, py, pw_ = g["pole"]
        yc = back + 60                                           # pole centre line (behind the TV)
        for sx in (-1, 1):                                       # H base: two front-back feet + cross bar
            parts.append(box(fw, by, bt, sx * (bx / 2 - fw / 2), yc - 40, bt / 2))
        parts.append(box(bx, fw, bt, 0, yc, bt / 2))
        top = vz0 + 0.3 * H
        parts.append(_tube(px, py, pw_, top - bt, (0, yc, bt)))
        bw, bh, btk = g["bracket"]
        parts.append(box(bw, btk, bh, 0, back + btk / 2, vz0))
        parts.append(box(px + 20, yc - back - py / 2 - btk + 2, 80, 0, back + btk + (yc - back - py / 2 - btk) / 2, vz0))   # bracket -> pole
        foot = [(-bx / 2, yc - 40 - by / 2), (bx / 2, yc - 40 - by / 2), (bx / 2, yc - 40 + by / 2), (-bx / 2, yc - 40 + by / 2)]
        mount = dict(kind="vesa", y=back, z=vz0, w=bw, h=bh)
    body = parts[0]
    for p in parts[1:]:
        body = body.union(p)
    floating = [i for i, so in enumerate(body.val().Solids()) if so.BoundingBox().zmin > 0.5]
    if floating:                                         # every separate part must stand on the floor, or the FEM is singular
        raise ValueError(f"{tid}: {len(floating)} part(s) do not reach the floor")
    tv_box = dict(center=c.tolist(), size=[W, D, H])
    return body, dict(layout=L, foot=foot, mount=mount, tv_box=tv_box)


def front_strokes(tid, tv=None, with_tv=True):
    """대략 정면 스케치 (x, z mm): TV 화면 + 스탠드 윤곽 — 템플릿 매칭 참조."""
    tv = tv or tv_spec(55)
    L = layout(tid, tv)
    W, H = tv["W"], tv["H"]
    c, g = L["tv_center"], L["g"]
    rect = lambda x0, x1, z0, z1: np.array([[x0, z0], [x1, z0], [x1, z1], [x0, z1], [x0, z0]], float)
    S = [rect(-W / 2, W / 2, c[2] - H / 2, c[2] + H / 2)] if with_tv else []
    if tid == "TV01":
        bx = g["base"][0]
        S += [rect(-bx / 2, bx / 2, 0, g["base"][2] + 4), rect(-g["neck"][0] / 2, g["neck"][0] / 2, g["base"][2], c[2] - H / 2)]
    elif tid == "TV02":
        for s in (-1, 1):
            x = s * g["foot_x"]
            S.append(np.array([[x - 50, 0], [x + 50, 0], [x + 8, g["foot_h"]], [x - 8, g["foot_h"]], [x - 50, 0]]))
    elif tid == "TV03":
        top = c[2] + H / 2 + 150
        sp = g["spread"]
        S += [np.array([[-sp / 2, 0], [0, top]]), np.array([[sp / 2, 0], [0, top]]), np.array([[-sp / 4, 260], [sp / 4, 260]])]
    else:
        bx = g["base"][0]
        S += [rect(-bx / 2, bx / 2, 0, g["base"][2] + 6), rect(-g["pole"][0] / 2, g["pole"][0] / 2, g["base"][2], c[2] + 0.3 * H),
              rect(-bx / 2, -bx / 2 + g["foot_w"], 0, 40), rect(bx / 2 - g["foot_w"], bx / 2, 0, 40)]
    return S


# ------------------------------------------------------------------ sketch matching (정면 스케치, 윤곽 상자 기준)
_MATCHER = None


class _FrontMatcher(Matcher):
    """Front-view TV stand sketches: no handlebar ring, so only the bounding-box frame; references with and
    without the TV outline (people often draw only the stand)."""
    RING_MIN_SCORE = 9.0
    ROTATIONS = (0,)

    @staticmethod
    def build_refs(templates):
        from ..sketch import _feat, bbox_map, strokes_to_points
        refs = {"ring": [], "bbox": []}
        for i, t in enumerate(templates):
            for with_tv in (True, False):
                st = front_strokes(t["params"]["tv"], with_tv=with_tv)
                pts = strokes_to_points(st, 8.0)
                refs["bbox"].append(dict(t=i, phone=with_tv, style="outline", **_feat(bbox_map(pts))))
        return refs


def matcher():
    global _MATCHER
    if _MATCHER is None:
        tpls = [dict(id=t["id"], name=t["name"], params=dict(tv=t["id"])) for t in TEMPLATES]
        _MATCHER = _FrontMatcher(tpls)
    return _MATCHER


def tv_strokes(params, phone=True):
    return front_strokes(params["tv"])


def match(gray):
    """정면 스케치 → 템플릿 후보 (TV 화면 + 스탠드 모양, 윤곽 상자 기준 chamfer)."""
    M = matcher()
    pts = ink_points(gray)
    if len(pts) < 20:
        return None
    m = M.match_points(pts, k=len(TEMPLATES))
    m["source"] = "스케치"
    return m


# ------------------------------------------------------------------ physics
def conditions(tv, tid, mat, place):
    m = tv["mass_kg"]
    Wn = m * 9.81
    Fh = min(0.13 * Wn, 250.0)
    Fd = min(0.5 * Wn, 100.0)
    return [
        dict(key="mass", name="TV 무게 (정하중)", value=f"{m} kg = {Wn:.0f} N", source=tv["source"]),
        dict(key="tilt", name="기울임 안정성", value="10° 기울여도 넘어지지 않음", source="IEC 62368-1 8.6 (근거)"),
        dict(key="push", name="수평력", value=f"무게의 13 % = {Fh:.0f} N (≤ 250 N), 1.5 m 이하 가장 불리한 위치(TV 윗단)", source="IEC 62368-1 8.6 (근거)"),
        dict(key="down", name="하향력", value=f"무게의 50 % = {Fd:.0f} N (≤ 100 N)", source="IEC 62368-1 8.6 (근거)"),
        dict(key="stress", name="응력", value=f"자중 + 수평력에서 ≤ 항복 {MATERIALS[mat]['yield_mpa']:.0f} ÷ {SF} = {MATERIALS[mat]['yield_mpa'] / SF:.0f} MPa",
             source=f"{MATERIALS[mat]['name']} 일반값 · 안전율 1.5 (가정)"),
        dict(key="defl", name="TV 윗단 흔들림", value=f"수평력에서 ≤ {TOP_DEFLECTION_MM} mm", source="가정 (팀 TV 스탠드 사례와 같은 값)"),
        dict(key="place", name="설치", value=place, source="템플릿"),
    ]


def tip_checks(tv, info, mass_stand_kg):
    """정역학: 지지 다각형 · 무게중심 → 넘어짐 각, 수평력 넘어짐 여유."""
    from matplotlib.path import Path
    foot = np.asarray(info["foot"], float)
    hull = foot if len(foot) == 3 else foot
    m_tv = tv["mass_kg"]
    c_tv = np.asarray(info["tv_box"]["center"])
    c_st = np.array([0.0, float(np.mean(foot[:, 1])), 0.15 * c_tv[2]])      # stand CG (low; approximation)
    m = m_tv + mass_stand_kg
    cg = (m_tv * c_tv + mass_stand_kg * c_st) / m
    # distance from CG projection to each edge of the support polygon (front / back / sides)
    P = np.vstack([hull, hull[:1]])
    d_edges = []
    for a, b in zip(P[:-1], P[1:]):
        e = b - a
        nrm = np.array([e[1], -e[0]]) / np.linalg.norm(e)
        d_edges.append(abs(np.dot(cg[:2] - a, nrm)))
    inside = Path(hull).contains_point(cg[:2])
    dmin = min(d_edges) if inside else 0.0
    tip_deg = math.degrees(math.atan2(dmin, cg[2]))
    Wn = m * 9.81
    Fh = min(0.13 * m_tv * 9.81, 250.0)
    h = min(c_tv[2] + info["tv_box"]["size"][2] / 2, 1500.0)
    margin = (Wn * dmin) / (Fh * h) if Fh > 0 else 99
    return dict(cg=cg.round(1).tolist(), d_min_mm=round(float(dmin), 1), tip_deg=round(float(tip_deg), 1), push_margin=round(float(margin), 2),
                push_N=round(Fh, 1), push_h_mm=round(h, 1), total_kg=round(m, 2))


def fem_checks(body, info, tv, mat, h=None):
    """Voxel FEM: floor contact fixed, TV weight + 13 % horizontal force (front-back) applied as a rigid TV."""
    import trimesh
    import cadquery as cq
    from .voxfem import VoxModel, pick_h, voxelize
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "s.stl")
        cq.exporters.export(body, p, tolerance=0.3)
        mesh = trimesh.load(p)
    h = h or pick_h(mesh, target=30000, lo=3.0, hi=12.0)
    occ, o = voxelize(mesh, h)
    M = MATERIALS[mat]
    V = VoxModel(occ, o, h, M["E"], M["nu"])
    xyz = V.node_xyz
    fixed = np.where(V.used & (xyz[:, 2] <= o[2] + h * 1.01 + 0.5))[0]
    fixed = fixed[xyz[fixed, 2] <= mesh.bounds[0][2] + h * 0.6]
    mt = info["mount"]
    if mt["kind"] == "vesa":
        sel = V.used & (np.abs(xyz[:, 1] - mt["y"]) <= h * 0.6) & (np.abs(xyz[:, 0]) <= mt["w"] / 2) & (np.abs(xyz[:, 2] - mt["z"]) <= mt["h"] / 2)
        if sel.sum() < 4:
            sel = V.used & (xyz[:, 1] <= mt["y"] + 2 * h) & (np.abs(xyz[:, 2] - mt["z"]) <= mt["h"] / 2)
    else:
        sel = V.used & (xyz[:, 2] >= mt["z"] - h) & np.any([np.abs(xyz[:, 0] - x) <= mt["w"] for x in mt["xs"]], axis=0)
    load_nodes = np.where(sel)[0]
    c = np.asarray(info["tv_box"]["center"])
    Wn = tv["mass_kg"] * 9.81
    Fh = min(0.13 * Wn, 250.0)
    top = np.array([0.0, c[1], min(c[2] + info["tv_box"]["size"][2] / 2, 1500.0)])
    F = V.rigid_load(load_nodes, c, (0.0, 0.0, -Wn))
    F += V.rigid_load(load_nodes, c, (0.0, Fh, 0.0), np.cross(top - c, [0.0, Fh, 0.0]))
    t0 = time.time()
    u = V.solve(fixed, F)
    vm = V.von_mises(u)
    tr, rot = V.rigid_fit(u, load_nodes, top)
    top_defl = float(np.linalg.norm(tr))
    nv, _ = V.nodal(vm)
    vm_max = float(np.percentile(nv, 99.5))          # 격자 계단 모서리 특이점 제외 (상위 0.5 % 절점)
    nv = np.minimum(nv, vm_max)
    un = np.linalg.norm(u.reshape(-1, 3), axis=1)
    lim = M["yield_mpa"] / SF
    heat = V.heat({
        "stress": (nv, 0.0, max(vm_max, 1e-3), "응력 (TV 무게 + 수평력 13 %, von Mises)", "MPa",
                   f"빨강 = 이 설계 최대 근처 (허용 {lim:.0f} MPa)"),
        "disp": (un, 0.0, max(float(np.percentile(un[V.used], 99.5)), 1e-3), "변위 (TV 무게 + 수평력)", "mm", "자동 척도"),
    })
    return dict(h=round(h, 2), elements=int(V.ne), vm_max=round(vm_max, 2), top_defl=round(top_defl, 3),
                solve_s=round(time.time() - t0, 1), heat=heat, stress_limit=round(lim, 1))


# ------------------------------------------------------------------ pipeline
def parse_size(text):
    import re
    m = re.search(r"(\d{2})\s*(인치|형|inch|\")", text or "")
    return int(m.group(1)) if m else 55


def design(text="", sketch=None, out="out", with_mesh=False, template=None):
    import cadquery as cq
    from .common import base_report, finish
    t0 = time.time()
    os.makedirs(out, exist_ok=True)
    tv = tv_spec(parse_size(text))
    match = None
    if template:
        tid, how = template, "지정"
    elif sketch is not None:
        match = match_sketch(sketch)
        tid, how = (match["candidates"][0]["id"], "스케치 매칭") if match else ("TV01", "기본")
    else:
        tid, how = keyword_template(text), "텍스트"
    T = BY_ID[tid]
    body, info = build(tid, tv)
    mat = T["material"]
    cq.exporters.export(body, os.path.join(out, "design_1st.step"), exportType="STEP")
    cq.exporters.export(body, os.path.join(out, "design_1st.stl"), tolerance=0.3)
    vol = body.val().Volume()
    mass_stand = vol * MATERIALS[mat]["rho"] * 1e-3
    tip = tip_checks(tv, info, mass_stand)
    fem = fem_checks(body, info, tv, mat, VOXEL[tid])
    lim = MATERIALS[mat]["yield_mpa"] / SF
    rows = [
        dict(key="tilt", name="넘어짐 각 (무게중심 ↔ 지지면 가장자리)", value=tip["tip_deg"], unit="°", op=">=", limit=10.0, source="IEC 62368-1 8.6 10° 기울임"),
        dict(key="push", name=f"수평력 {tip['push_N']:.0f} N 넘어짐 여유 (복원/전도 모멘트)", value=tip["push_margin"], unit="배", op=">=", limit=1.0,
             source="IEC 62368-1 8.6 13 % 수평력"),
        dict(key="stress", name="최대 응력 (자중 + 수평력, FEM)", value=fem["vm_max"], unit="MPa", op="<=", limit=round(lim, 1),
             source=f"{MATERIALS[mat]['name']} 항복 ÷ 1.5"),
        dict(key="defl", name="TV 윗단 흔들림 (수평력, FEM)", value=fem["top_defl"], unit="mm", op="<=", limit=TOP_DEFLECTION_MM,
             source="가정 (팀 TV 스탠드 사례)"),
    ]
    for r in rows:
        r["ok"] = bool(r["value"] >= r["limit"] if r["op"] == ">=" else r["value"] <= r["limit"])
    drawing(body, info, tv, T, os.path.join(out, "design_1st_drawing.png"), os.path.join(out, "design_1st_drawing.pdf"), mass_stand)
    sketch_png(tid, tv, os.path.join(out, "side_view.png"))
    rep = base_report(
        product="TV 스탠드", tid=tid, tname=T["name"], tdesc=T["desc"], chosen_by=how, match=match, rows=rows,
        conditions=conditions(tv, tid, mat, T["place"]),
        summary=[["제품", "TV 스탠드"], ["TV", f"{tv['size_in']}형 · {tv['mass_kg']} kg · VESA {tv['vesa'][0]}×{tv['vesa'][1]}"],
                 ["설치", T["place"]], ["재료", MATERIALS[mat]["name"]], ["안정성 기준", "IEC 62368-1 8.6"], ["안전율", SF]],
        design_vars=[["형식", f"{tid} {T['name']}"], ["TV 크기", f"{tv['W']:.0f} × {tv['H']:.0f} mm"],
                     ["TV 아래 높이", f"{info['layout']['tv_bottom']:.0f} mm"], ["지지면 (발 사이)", f"{np.ptp(np.asarray(info['foot'])[:, 0]):.0f} × {np.ptp(np.asarray(info['foot'])[:, 1]):.0f} mm"],
                     ["무게중심 높이", f"{tip['cg'][2]:.0f} mm"], ["스탠드 무게", f"{mass_stand:.2f} kg"], ["해석 격자", f"{fem['h']} mm · {fem['elements']:,} 요소"]],
        assumptions=[tv["source"], "스탠드 무게중심은 지지면 위 낮은 곳으로 근사 (넘어짐 계산은 TV가 지배)",
                     "바닥 접촉면 완전 고정, TV는 강체로 보고 VESA 판 · 받침 슬롯에 하중 분배",
                     "최대 응력 = 절점 응력 상위 0.5 % 제외값 (복셀 계단 모서리의 가짜 응력 집중 제외)",
                     f"TV 윗단 흔들림 ≤ {TOP_DEFLECTION_MM} mm 는 가정 (팀 TV 스탠드 사례)", "데모용 1차 설계 — 최적화 단계로 넘기지 않음"],
        sources=[SOURCES["iec62368"], SOURCES["samsung55"], SOURCES["samsung55_qn90b"]],
        cad=dict(mass_g=round(mass_stand * 1e3, 1), material=MATERIALS[mat]["name"]), extra=dict(tip=tip, fem={k: v for k, v in fem.items() if k != "heat"}, tv=tv),
        seconds=time.time() - t0)
    finish(rep, out)
    if with_mesh:
        from .common import mesh_b64
        rep["mesh"] = mesh_b64(body)
        rep["heat"] = fem["heat"]
        rep["aux"] = [dict(kind="box", center=info["tv_box"]["center"], size=info["tv_box"]["size"], color="#1b1f24", opacity=1.0, label="TV")]
        rep["scene"] = dict(floor_z=0.0, up="z", color={"steel": "#8b959e", "al": "#b9c2c9", "wood": "#c49a63"}[mat])
    return rep


def keyword_template(text):
    import re
    t = text or ""
    if re.search(r"이젤|삼각", t):
        return "TV03"
    if re.search(r"바닥|높게|이동|스탠드형", t):
        return "TV04"
    if re.search(r"양발|다리 두|두 다리|양쪽 다리", t):
        return "TV02"
    return "TV01"


def match_sketch(gray):
    return match(gray)


# ------------------------------------------------------------------ images
def sketch_png(tid, tv, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 4.2))
    for s in front_strokes(tid, tv):
        ax.plot(s[:, 0], s[:, 1], c="#222", lw=1.6)
    ax.axhline(0, c="#888", lw=1)
    ax.set_aspect("equal")
    ax.set_title(f"{tid} {BY_ID[tid]['name']} — 정면 (1차 설계 윤곽, mm)", fontsize=10)
    ax.grid(alpha=.25)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def drawing(body, info, tv, T, png, pdf, mass_kg):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    verts, tris = body.val().tessellate(0.5, 0.5)
    V = np.array([[p.x, p.y, p.z] for p in verts])
    F = np.array(tris)
    c, (W, D, H) = np.asarray(info["tv_box"]["center"]), info["tv_box"]["size"]
    fig, ax = plt.subplots(1, 2, figsize=(14, 6))
    for a, (i, j, ttl) in zip(ax, ((0, 2, "정면"), (1, 2, "옆 (앞 = 왼쪽)"))):
        a.add_collection(PolyCollection(V[F][:, :, [i, j]], fc="#c9d6df", ec="none"))
        lo, hi = c[[i, j]] - np.array([[W, D][i] / 2 if i == 0 else D / 2, H / 2]), c[[i, j]] + np.array([[W, D][i] / 2 if i == 0 else D / 2, H / 2])
        a.add_patch(plt.Rectangle(lo, *(hi - lo), fill=False, ls="--", ec="#555"))
        a.axhline(0, c="#888", lw=1)
        a.set_aspect("equal")
        a.autoscale()
        a.grid(alpha=.25)
        a.set_title(ttl, fontsize=10)
    ax[0].text(c[0], c[2], f"TV {tv['size_in']}형\n{tv['mass_kg']} kg", ha="center", va="center", color="#555")
    fig.suptitle(f"TV 스탠드 — 1차 설계 {T['id']} {T['name']} · {MATERIALS[T['material']]['name']} · 스탠드 {mass_kg:.2f} kg · 단위 mm", fontsize=12)
    fig.savefig(png, dpi=120, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    plt.close(fig)
