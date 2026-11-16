"""TV 스탠드 (LG 스탠바이미형 이동식) — 스케치 → 템플릿 → 1차 설계(CAD · 도면) + 물리 조건 + 간이 판정 (데모 시나리오).

구조 (LG StanbyME 27ART10 과 같은 방식): 바퀴 5개가 숨은 둥근 받침 + 가운데 수직 기둥 + 기둥을 타는 높이 조절 캐리지
+ 짧은 팔 + 회전 헤드(화면 뒤 장착판). 기둥은 화면 **뒤**에 있고 화면 위로 나오지 않는다 (CAD 에서 화면과 겹침 0 을 검사).

좌표 (mm): x = 화면 폭 방향, y = 앞뒤 (앞 = −y, 시청자 쪽), z = 위, 바닥 z = 0, 기둥 축 = (0, 0).
템플릿: TV01 가로 · TV02 세로(화면 회전). 화면 높이는 스케치 비율에서 읽어 스탠바이미 조절 범위로 제한.
물리 조건: IEC 62368-1 8.6 안정성 (10° 기울임, 무게 13 % 수평력 ≤ 250 N, 50 % 하향력 ≤ 100 N, 1.5 m 이하),
자중 + 수평력 응력 ≤ 항복/1.5, 화면 윗단 흔들림 ≤ 1 mm(가정), 바퀴 하나 하중 ≤ 200 N(가정).
"""
import math
import os
import re
import tempfile
import time

import numpy as np

from .. import progress
from ..sketch import Matcher, ink_points

SOURCES = {
    "stanbyme": dict(title="LG StanbyME 27ART10AKPL 사양: 화면 621 × 361 × 29.9 mm · 4.8 kg, 스탠드 포함 621 × 1077 × 397 mm · 17.5 kg, 받침 397 × 397",
                     url="https://www.lg.com/sg/tvs/lg-27art10akpl"),
    "stanbyme_us": dict(title="LG US 사양: 스탠드 포함 높이 49.8\"(최대) / 41.9\"(최소), 받침 폭 15.6\"",
                        url="https://www.lg.com/us/lifestyle-products/lg-27art10akpl-lifestyle-screen"),
    "wheels": dict(title="B&H: 받침에 숨은 바퀴 5개 + 기둥에 조절 팔로 화면 장착, 배터리 내장",
                   url="https://www.bhphotovideo.com/c/product/1770964-REG"),
    "iec62368": dict(title="IEC 62368-1 ed.3 8.6 안정성 시험 (10° 기울임, 13 % 수평력 ≤ 250 N, 50 % 하향력 ≤ 100 N, 1.5 m 이하)",
                     url="https://www.mail-archive.com/emc-pstc@listserv.ieee.org/msg76504.html"),
}
MAT = dict(name="강 (받침판 · 기둥 강관 SS275)", E=205000.0, nu=0.3, rho=7.85e-3, yield_mpa=275.0)
MATERIALS = {"steel": MAT}
SF = 1.5
TOP_DEFLECTION_MM = 1.0          # 가정 (팀 TV 스탠드 사례와 같은 값)
CASTER_LIMIT_N = 200.0           # 가정: 소형 캐스터 정격 약 20 kg
REF27 = dict(W=621.0, H=361.0, D=29.9, mass=4.8, stand_mass=17.5 - 4.8, base_d=397.0,
             top_min=1064.0, top_max=1265.0)     # 41.9" / 49.8" (LG US) -> 가로 화면 윗단 높이 범위
VOXEL = 4.0


def tv_spec(size_in=27):
    """화면 크기 → 치수 · 무게. 27형 = 스탠바이미 실측(LG), 다른 크기는 대각 비례 가정(무게 ∝ 크기²)."""
    s = size_in / 27.0
    src = "근거: LG StanbyME 27형 사양" if size_in == 27 else f"가정: 27형 스탠바이미에서 대각 비례 — {size_in}형 실제 사양 확인 필요"
    return dict(size_in=size_in, W=round(REF27["W"] * s, 1), H=round(REF27["H"] * s, 1), D=REF27["D"],
                mass_kg=round(REF27["mass"] * s ** 2, 1), source=src)


TEMPLATES = [
    dict(id="TV01", name="이동식 스탠드 · 가로", desc="둥근 받침(바퀴 5) + 수직 기둥 + 높이 조절 캐리지 · 회전 헤드, 화면 가로", orient="landscape"),
    dict(id="TV02", name="이동식 스탠드 · 세로", desc="같은 스탠드, 화면을 90° 돌려 세로로 (헤드 회전)", orient="portrait"),
]
BY_ID = {t["id"]: t for t in TEMPLATES}


# ------------------------------------------------------------------ geometry
FIRST = dict(base_d=300.0, caster_frac=0.40, pole_d=28.0)   # 1차 설계 = 스케치 비율 그대로 (작은 받침 · 가는 기둥) -> 최적화 대상
LEVELS = ("low", "mid", "high")                            # 템플릿 높이 3단 (스탠바이미 조절 범위 최소 · 가운데 · 최대)
LEVEL_WORD = {"low": "낮게", "mid": "", "high": "높게"}
LEVEL_NAME = {"low": "낮게", "mid": "가운데", "high": "높게"}


def stand_dims(tv):
    k = max(tv["size_in"] / 27.0, 1.0) ** 0.6           # 큰 화면은 받침 · 기둥을 키움 (가정)
    return dict(base_d=FIRST["base_d"] * k, plate_t=8.0, plate_z=22.0, hub_d=130.0 * k, hub_h=40.0,
                caster_r=FIRST["caster_frac"] * FIRST["base_d"] * k, wheel_d=36.0, wheel_w=16.0,
                pole_d=FIRST["pole_d"] * k, pole_t=4.0, sleeve_d=50.0 * k, sleeve_h=130.0, arm=(60.0, 40.0, 40.0), plate=(120.0, 8.0, 120.0))


def level_zc(tv, orient, level):
    lo, hi = center_range(tv, orient)
    return {"low": lo, "mid": (lo + hi) / 2, "high": hi}[level]


def snap_level(tv, orient, zc):
    """임의 높이 -> 가장 가까운 템플릿 높이 단."""
    return min(LEVELS, key=lambda lv: abs(level_zc(tv, orient, lv) - zc))


def screen_box(tv, orient):
    W, H = (tv["W"], tv["H"]) if orient == "landscape" else (tv["H"], tv["W"])
    return W, H, tv["D"]


def center_range(tv, orient):
    """화면 중심 높이 조절 범위: 스탠바이미 가로 화면 윗단 1064–1265 mm → 캐리지(=화면 중심) 범위, 세로도 같은 캐리지 범위."""
    s = tv["size_in"] / 27.0
    lo = REF27["top_min"] - REF27["H"] / 2
    hi = REF27["top_max"] - REF27["H"] / 2
    if s > 1:                                             # 큰 화면: 받침 위 여유를 유지하도록 위로
        lo, hi = lo + (tv["H"] - REF27["H"]) / 2, hi + (tv["H"] - REF27["H"]) / 2
    W, H, _ = screen_box(tv, orient)
    lo = max(lo, H / 2 + 200.0)
    return lo, max(hi, lo)


def layout(tid, tv, zc=None):
    orient = BY_ID[tid]["orient"]
    g = stand_dims(tv)
    lo, hi = center_range(tv, orient)
    zc = float(np.clip(zc if zc is not None else (lo + hi) / 2, lo, hi))
    W, H, D = screen_box(tv, orient)
    back = -(g["sleeve_d"] / 2 + g["arm"][1] + g["plate"][1])          # 화면 뒷면 y
    tv_c = np.array([0.0, back - D / 2, zc])
    return dict(g=g, orient=orient, zc=zc, z_range=(lo, hi), back=back, tv_center=tv_c, tv_size=(W, D, H))


def build(tid, tv, zc=None):
    """CadQuery stand (one solid) + screen box (context) + caster contact polygon + mount node selector."""
    import cadquery as cq
    L = layout(tid, tv, zc)
    g, zc, back = L["g"], L["zc"], L["back"]
    W, D, H = L["tv_size"]
    cyl = lambda d, h, x, y, z: cq.Workplane("XY").circle(d / 2).extrude(h).translate((x, y, z))
    box = lambda dx, dy, dz, x, y, z: cq.Workplane().box(dx, dy, dz).translate((x, y, z))
    parts = []
    # 받침: 둥근 판 + 가운데 허브 (기둥 소켓)
    parts.append(cyl(g["base_d"], g["plate_t"], 0, 0, g["plate_z"]).edges(">Z").fillet(3))
    zt = g["plate_z"] + g["plate_t"]
    parts.append(cq.Workplane("XY").circle(g["hub_d"] / 2).circle(g["hub_d"] / 2 - 4).extrude(g["hub_h"]).translate((0, 0, zt)))   # 허브 덮개 (벽 4)
    parts.append(cq.Workplane("XY").circle(g["hub_d"] / 2).circle(g["pole_d"] / 2 - 1).extrude(4).translate((0, 0, zt + g["hub_h"] - 4)))
    parts.append(cq.Workplane("XY").circle(g["pole_d"] / 2 + 6).circle(g["pole_d"] / 2 - 1).extrude(g["hub_h"]).translate((0, 0, zt)))  # 기둥 소켓
    # 바퀴 5개 (앞쪽에 하나: 앞으로 넘어짐에 유리), 바퀴 축 = 접선 방향
    feet = []
    for k in range(5):
        a = -math.pi / 2 + 2 * math.pi * k / 5
        cx, cy = g["caster_r"] * math.cos(a), g["caster_r"] * math.sin(a)
        feet.append((cx, cy))
        tdir = (-math.sin(a), math.cos(a))
        wheel = (cq.Workplane("YZ").circle(g["wheel_d"] / 2).extrude(g["wheel_w"] / 2, both=True)
                 .rotate((0, 0, 0), (0, 0, 1), math.degrees(math.atan2(tdir[1], tdir[0])))
                 .translate((cx, cy, g["wheel_d"] / 2)))
        fork = box(26, 26, g["plate_z"] - g["wheel_d"] / 2 + 2, cx, cy, (g["plate_z"] + g["wheel_d"] / 2) / 2 + 1)
        parts += [wheel, fork]
    # 기둥 (강관): 받침 위 → 캐리지 위끝 (화면 윗단보다 낮게, 화면 뒤)
    z_top = zc + g["sleeve_h"] / 2 + 15.0
    parts.append(cq.Workplane("XY").circle(g["pole_d"] / 2).circle(g["pole_d"] / 2 - g["pole_t"]).extrude(z_top - zt + 5).translate((0, 0, zt - 5)))
    parts.append(cyl(g["pole_d"], 6, 0, 0, z_top - 6))                                   # 기둥 마개
    # 캐리지 (기둥을 감싸는 슬리브) + 팔 + 회전 헤드 장착판
    parts.append(cq.Workplane("XY").circle(g["sleeve_d"] / 2).circle(g["pole_d"] / 2).extrude(g["sleeve_h"]).translate((0, 0, zc - g["sleeve_h"] / 2)))
    aw, al, ah = g["arm"]
    parts.append(box(aw, al + 6, ah, 0, -g["sleeve_d"] / 2 - al / 2 + 3, zc))
    pw, pt, ph = g["plate"]
    parts.append(box(pw, pt, ph, 0, back + pt / 2, zc))
    body = parts[0]
    for p in parts[1:]:
        body = body.union(p)
    tv_solid = box(W, D, H, 0, L["tv_center"][1], zc)
    inter = body.intersect(tv_solid)
    clash = sum(s.Volume() for s in inter.vals()) if inter.vals() else 0.0
    if clash > 1.0:                                  # 스탠드가 화면을 뚫으면 설계 오류
        raise ValueError(f"{tid}: stand intersects the screen ({clash:.0f} mm³)")
    floating = [so for so in body.val().Solids() if so.BoundingBox().zmin > 0.5]
    if floating:
        raise ValueError(f"{tid}: {len(floating)} part(s) do not reach the floor")
    info = dict(layout=L, foot=feet, clash_mm3=round(clash, 2),
                mount=dict(y=back, z=zc, w=pw, h=ph),
                tv_box=dict(center=L["tv_center"].tolist(), size=[W, D, H]))
    return body, info


def front_strokes(tid, tv=None, with_tv=True, zc=None):
    """정면 스케치 (x, z mm): 화면 + 화면 아래로 보이는 기둥 + 둥근 받침(정면에선 납작한 띠) + 바퀴."""
    tv = tv or tv_spec(27)
    L = layout(tid, tv, zc)
    g = L["g"]
    W, D, H = L["tv_size"]
    zc = L["zc"]
    rect = lambda x0, x1, z0, z1: np.array([[x0, z0], [x1, z0], [x1, z1], [x0, z1], [x0, z0]], float)
    zt = g["plate_z"] + g["plate_t"]
    S = []
    if with_tv:
        S.append(rect(-W / 2, W / 2, zc - H / 2, zc + H / 2))
    pole_top = zc - H / 2 if with_tv else zc + g["sleeve_h"] / 2
    S.append(rect(-g["pole_d"] / 2, g["pole_d"] / 2, zt + g["hub_h"], pole_top))
    if not with_tv:
        S.append(rect(-g["sleeve_d"] / 2, g["sleeve_d"] / 2, zc - g["sleeve_h"] / 2, zc + g["sleeve_h"] / 2))
    r = g["base_d"] / 2
    S.append(rect(-r, r, g["plate_z"], zt))
    S.append(rect(-g["hub_d"] / 2, g["hub_d"] / 2, zt, zt + g["hub_h"]))
    a = np.linspace(0, 2 * np.pi, 25)
    for x in (-0.95 * g["caster_r"], -0.59 * g["caster_r"], 0.0, 0.59 * g["caster_r"], 0.95 * g["caster_r"]):
        S.append(np.c_[x + g["wheel_d"] / 2 * np.cos(a), g["wheel_d"] / 2 + g["wheel_d"] / 2 * np.sin(a)])
    return S


# ------------------------------------------------------------------ sketch matching (정면, 윤곽 상자 기준) + 높이 읽기
_MATCHER = None


class _FrontMatcher(Matcher):
    """Front-view stand sketches: no handlebar ring -> bounding-box frame only; references with and without the screen."""
    RING_MIN_SCORE = 9.0
    ROTATIONS = (0,)

    @staticmethod
    def build_refs(templates):
        from ..sketch import _feat, bbox_map, strokes_to_points
        refs = {"ring": [], "bbox": []}
        for i, t in enumerate(templates):
            for with_tv in (True, False):
                for zc in (None, 900.0, 1070.0):
                    pts = strokes_to_points(front_strokes(t["params"]["tv"], with_tv=with_tv, zc=zc), 6.0)
                    refs["bbox"].append(dict(t=i, phone=with_tv, style="outline", zc=zc, **_feat(bbox_map(pts))))
        return refs

    def match_points(self, pts, k=3):
        from ..sketch import _chamfer
        _, _, queries = self.query_maps(pts)
        best = {}
        for (mir, _), q in queries:
            for r in self.refs["bbox"]:
                s = 0.5 * (_chamfer(q["img"], r["dt"]) + _chamfer(r["img"], q["dt"])) + self.w_hist * float(np.linalg.norm(q["hist"] - r["hist"]))
                if r["t"] not in best or s < best[r["t"]][0]:
                    best[r["t"]] = (s, r["phone"])
        ranked = sorted((s, i, w) for i, (s, w) in best.items())
        s0 = ranked[0][0]
        res = [dict(id=self.templates[i]["id"], name=self.templates[i]["name"], score=round(s, 3), with_screen=bool(w),
                    confidence=round(math.exp(-(s - s0) / 0.5), 3)) for s, i, w in ranked[:k]]
        return dict(frame="bbox", ring_score=0.0, candidates=res)


def matcher():
    global _MATCHER
    if _MATCHER is None:
        _MATCHER = _FrontMatcher([dict(id=t["id"], name=t["name"], params=dict(tv=t["id"])) for t in TEMPLATES])
    return _MATCHER


def match(gray):
    pts = ink_points(gray)
    if len(pts) < 20:
        return None
    m = matcher().match_points(pts, k=len(TEMPLATES))
    m["source"] = "스케치"
    return m


def height_from_sketch(gray, tid, tv, with_screen=True):
    """스케치 윤곽 상자 비율 → 화면 중심 높이 (mm). 가로: 상자 폭 = 화면 폭, 세로: 상자 폭 = max(화면 폭, 받침 지름)."""
    if not with_screen:
        return None
    pts = ink_points(gray)
    w, h = np.ptp(pts[:, 0]), np.ptp(pts[:, 1])
    orient = BY_ID[tid]["orient"]
    W, H, _ = screen_box(tv, orient)
    ref_w = max(W, stand_dims(tv)["base_d"])
    top = h * ref_w / max(w, 1e-9)
    return float(top - H / 2)


# ------------------------------------------------------------------ physics
def conditions(tv, tid, total_kg):
    Wn = total_kg * 9.81
    Fh = min(0.13 * Wn, 250.0)
    Fd = min(0.5 * Wn, 100.0)
    return [
        dict(key="mass", name="화면 무게", value=f"{tv['mass_kg']} kg ({tv['size_in']}형)", source=tv["source"]),
        dict(key="total", name="제품 전체 무게 (화면 + 스탠드)", value=f"{total_kg:.1f} kg = {Wn:.0f} N",
             source="스탠드 = CAD (강) · 참고: 스탠바이미 스탠드 12.7 kg (17.5 − 4.8)"),
        dict(key="tilt", name="안정성 ① 기울임 시험", value="모든 방향 10° 기울여도 넘어지지 않음 (바퀴 5개 접지점 기준)", source="IEC 62368-1 8.6 (근거) — 세 대안 시험 중 하나"),
        dict(key="push", name="안정성 ③ 힘 시험 (대안)", value=f"수평 13 % = {Fh:.0f} N (≤ 250 N) · 하향 50 % = {Fd:.0f} N (≤ 100 N), 1.5 m 이하", source="IEC 62368-1 8.6 (근거) — EU 판매 시 모든 대안 권장"),
        dict(key="stress", name="응력", value=f"자중 + 수평력에서 ≤ 항복 {MAT['yield_mpa']:.0f} ÷ {SF} = {MAT['yield_mpa'] / SF:.0f} MPa", source=f"{MAT['name']} 일반값 · 안전율 1.5 (가정)"),
        dict(key="defl", name="화면 윗단 흔들림", value=f"수평력에서 ≤ {TOP_DEFLECTION_MM} mm", source="가정 (팀 TV 스탠드 사례와 같은 값)"),
        dict(key="caster", name="바퀴 하나 하중", value=f"자중 + 수평력에서 ≤ {CASTER_LIMIT_N:.0f} N", source="가정 (소형 캐스터 정격 약 20 kg)"),
        dict(key="move", name="이동", value="바퀴 5개로 굴려 이동 · 화면 회전(가로/세로) · 높이 조절", source="근거: LG 스탠바이미 사양"),
    ]


def _edges(foot):
    P = np.asarray(foot, float)
    c = P.mean(0)
    o = np.argsort(np.arctan2(P[:, 1] - c[1], P[:, 0] - c[0]))
    P = P[o]
    out = []
    for a, b in zip(P, np.roll(P, -1, 0)):
        e = b - a
        n = np.array([e[1], -e[0]]) / np.linalg.norm(e)        # outward for counter-clockwise order
        out.append((a, n))
    return out


def tip_checks(tv, info, mass_stand_kg, stand_cg=None):
    """정역학: 접지 다각형(바퀴) · 전체 무게중심 → 넘어짐 각, 수평력 · 하향력 넘어짐 여유, 바퀴 하중 (강체 받침, 같은 강성 바퀴)."""
    m_tv = tv["mass_kg"]
    c_tv = np.asarray(info["tv_box"]["center"], float)
    W_, D_, H_ = info["tv_box"]["size"]
    c_st = np.asarray(stand_cg if stand_cg is not None else [0.0, 0.0, 0.0], float)
    m = m_tv + mass_stand_kg
    cg = (m_tv * c_tv + mass_stand_kg * c_st) / m
    Wn = m * 9.81
    edges = _edges(info["foot"])
    d = [-(np.dot(cg[:2] - a, n)) for a, n in edges]                 # >0 = inside
    dmin = max(min(d), 0.0)
    tip_deg = math.degrees(math.atan2(dmin, cg[2]))
    Fh = min(0.13 * Wn, 250.0)
    h = min(c_tv[2] + H_ / 2, 1500.0)
    push = min((Wn * di) / (Fh * h) for di in d) if Fh > 0 else 99.0
    Fd = min(0.5 * Wn, 100.0)
    p_front = np.array([c_tv[0], c_tv[1] - D_ / 2])                  # 화면 앞 윗모서리 (가운데)
    down = 99.0
    for (a, n), di in zip(edges, d):
        dp = -(np.dot(p_front - a, n))
        if dp < 0:
            down = min(down, (Wn * di) / (Fd * -dp))
    # 바퀴 하중: 자중 + 수평력(화면 윗단, 앞→뒤 · 뒤→앞 · 옆) — 강체 받침 위 같은 스프링 (최소 노름)
    P = np.asarray(info["foot"], float)
    A = np.vstack([np.ones(len(P)), P[:, 0], P[:, 1]])
    worst = 0.0
    for fx, fy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        Mx = Wn * cg[1] - Fh * fy * h                          # Σ R y = W y_cg − F_y h
        My = Wn * cg[0] - Fh * fx * h
        R = A.T @ np.linalg.solve(A @ A.T, np.array([Wn, My, Mx]))
        worst = max(worst, float(R.max()))
    return dict(cg=cg.round(1).tolist(), d_min_mm=round(float(dmin), 1), tip_deg=round(float(tip_deg), 1),
                push_margin=round(float(push), 2), push_N=round(float(Fh), 1), push_h_mm=round(float(h), 1),
                down_N=round(float(Fd), 1), down_margin=round(float(down), 2), caster_max_N=round(worst, 1), total_kg=round(m, 2))


def fem_checks(body, info, tv, total_kg, h=VOXEL):
    """복셀 FEM: 바퀴 바닥 고정, 화면 무게 + 수평력 13 % (앞뒤, 화면 윗단) — 화면은 강체로 장착판에 분배."""
    import trimesh
    import cadquery as cq
    from .voxfem import VoxModel, voxelize
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "s.stl")
        cq.exporters.export(body, p, tolerance=0.3)
        mesh = trimesh.load(p)
    from .voxfem import pick_h
    h = max(h, pick_h(mesh, target=35000, lo=VOXEL, hi=8.0))         # 큰 화면(큰 스탠드)도 메모리 ≤ 약 2.5 GB
    progress.step("복셀 격자 만들기", f"{h:.1f} mm")
    occ, o = voxelize(mesh, h, sym_x=True)
    V = VoxModel(occ, o, h, MAT["E"], MAT["nu"])
    xyz = V.node_xyz
    fixed = np.where(xyz[:, 2] <= mesh.bounds[0][2] + h * 0.6)[0]
    mt = info["mount"]
    sel = (np.abs(xyz[:, 1] - mt["y"]) <= h * 0.6) & (np.abs(xyz[:, 0]) <= mt["w"] / 2) & (np.abs(xyz[:, 2] - mt["z"]) <= mt["h"] / 2)
    load_nodes = np.where(sel)[0]
    c = np.asarray(info["tv_box"]["center"])
    Wtv = tv["mass_kg"] * 9.81
    Fh = min(0.13 * total_kg * 9.81, 250.0)
    top = np.array([0.0, c[1], min(c[2] + info["tv_box"]["size"][2] / 2, 1500.0)])
    F = V.rigid_load(load_nodes, c, (0.0, 0.0, -Wtv))
    F += V.rigid_load(load_nodes, c, (0.0, Fh, 0.0), np.cross(top - c, [0.0, Fh, 0.0]))
    t0 = time.time()
    u = V.solve(fixed, F, label=f"FEM 풀이 — 화면 무게 + 수평력 ({V.ne:,} 요소)")
    progress.step("응력 · 변위 분포")
    vm = V.von_mises(u)
    tr, rot = V.rigid_fit(u, load_nodes, top)
    nv, _ = V.nodal(vm)
    vm_max = float(np.percentile(nv, 99.5))          # 격자 계단 모서리 특이점 제외 (상위 0.5 % 절점)
    nv = np.minimum(nv, vm_max)
    un = np.linalg.norm(u.reshape(-1, 3), axis=1)
    lim = MAT["yield_mpa"] / SF
    heat = V.heat({
        "stress": (nv, 0.0, max(vm_max, 1e-3), "응력 (화면 무게 + 수평력 13 %, von Mises)", "MPa", f"빨강 = 이 설계 최대 근처 (허용 {lim:.0f} MPa)"),
        "disp": (un, 0.0, max(float(np.percentile(un, 99.5)), 1e-3), "변위 (화면 무게 + 수평력)", "mm", "자동 척도"),
    })
    return dict(h=round(h, 2), elements=int(V.ne), vm_max=round(vm_max, 2), top_defl=round(float(np.linalg.norm(tr)), 3),
                solve_s=round(time.time() - t0, 1), heat=heat, stress_limit=round(lim, 1))


# ------------------------------------------------------------------ pipeline
def parse_size(text):
    m = re.search(r"(\d{2})\s*(인치|형|inch|\")", text or "")
    return int(m.group(1)) if m else 27


def keyword_template(text):
    return "TV02" if re.search(r"세로|회전|portrait", text or "", re.I) else "TV01"


def parse_height(text):
    t = text or ""
    m = re.search(r"(?:화면\s*)?(?:중심\s*)?높이\s*(\d{3,4})", t)
    if m:
        return float(m.group(1))
    if re.search(r"낮게|소파|좌식", t):
        return 0.0                       # -> 범위 최소
    if re.search(r"높게|서서|주방|식탁", t):
        return 1e4                       # -> 범위 최대
    return None


def design(text="", sketch=None, out="out", with_mesh=False, template=None):
    """템플릿(가로/세로 × 높이 3단) 결과 DB 에서 바로 (처음 한 번만 계산). 스케치 · 문장은 템플릿과 높이 단을 고르는 데 쓴다."""
    import json
    from .. import memo
    t0 = time.time()
    tv = tv_spec(parse_size(text))
    match = None
    zc_req = parse_height(text)
    zc_how = "문장" if zc_req is not None else None
    from .. import demo_inputs
    demo = demo_inputs.match("tv", sketch) if (sketch is not None and not template) else None
    if demo:                                             # 등록된 데모 스케치 (말 + 스케치) → 정해 둔 템플릿 · 높이
        progress.step("정면 스케치 → 등록된 데모 스케치 (그림 지문)")
        tid, how = demo["template"], "데모 스케치 (그림 지문)"
        zc_req, zc_how = None, None
    elif template:
        tid, how = template, "지정"
    elif sketch is not None:
        progress.step("정면 스케치 → 템플릿 비교 · 높이 읽기")
        match = match_sketch(sketch)
        tid, how = (match["candidates"][0]["id"], "스케치 매칭") if match else (keyword_template(text), "텍스트")
    else:
        tid, how = keyword_template(text), "텍스트"
    if zc_req is None and sketch is not None and not demo:
        top = match["candidates"][0] if match else {}
        zc_req = height_from_sketch(sketch, tid, tv, top.get("with_screen", True))
        zc_how = "스케치 비율" if zc_req is not None else None
    orient = BY_ID[tid]["orient"]
    level = demo["level"] if demo else snap_level(tv, orient, zc_req) if zc_req is not None else "mid"
    k = memo.key("tv", tid, tv["size_in"], level, FIRST)
    rep = memo.get(k, out) if with_mesh else None
    if rep is None:
        os.makedirs(out, exist_ok=True)
        before = os.listdir(out)
        rep = _design(tv, tid, level_zc(tv, orient, level), out, with_mesh)
        if with_mesh:
            rep = memo.put(k, out, memo.new_files(out, before), rep)
    else:
        progress.step("템플릿 결과 DB에서 1차 설계 · 성능 불러오기", f"{tid} · 높이 {LEVEL_NAME[level]}")
    zc_t = rep["extra"]["zc"]
    read = (f"{zc_how} {zc_req:.0f} mm → 템플릿 높이 '{LEVEL_NAME[level]}' {zc_t:.0f} mm" if zc_how and zc_req is not None
            else f"데모 스케치 → 템플릿 높이 '{LEVEL_NAME[level]}' {zc_t:.0f} mm" if demo
            else f"템플릿 높이 '{LEVEL_NAME[level]}' {zc_t:.0f} mm (기본)")
    rep["template"].update(chosen_by=how, match=match, level=level)
    rep["design_vars"] = [[a, read] if a == "화면 중심 높이" else [a, b] for a, b in rep["design_vars"]]
    rep["extra"]["height_read"] = read
    rep["extra"]["sketch_note"] = demo["note"] if demo else ""
    rep["seconds"] = round(time.time() - t0, 2)
    with open(os.path.join(out, "report.json"), "w", encoding="utf-8") as f:
        json.dump({k_: v for k_, v in rep.items() if k_ not in ("mesh", "heat", "aux")}, f, ensure_ascii=False, indent=1)
    return rep


def _design(tv, tid, zc_req, out, with_mesh):
    """실제 계산 (템플릿 DB 가 비었을 때만)."""
    import cadquery as cq
    from .common import base_report, finish
    t0 = time.time()
    os.makedirs(out, exist_ok=True)
    how, match, zc_how = "템플릿", None, None
    T = BY_ID[tid]
    progress.step("CAD (받침 · 바퀴 · 기둥 · 헤드) · 화면 겹침 검사")
    body, info = build(tid, tv, zc_req)
    L = info["layout"]
    lo, hi = L["z_range"]
    clipped = False
    cq.exporters.export(body, os.path.join(out, "design_1st.step"), exportType="STEP")
    cq.exporters.export(body, os.path.join(out, "design_1st.stl"), tolerance=0.3)
    sol = body.val()
    mass_stand = sol.Volume() * MAT["rho"] * 1e-3
    cgv = sol.Center()
    progress.step("넘어짐 · 바퀴 하중 (정역학)")
    tip = tip_checks(tv, info, mass_stand, [cgv.x, cgv.y, cgv.z])
    total = tip["total_kg"]
    fem = fem_checks(body, info, tv, total)
    lim = MAT["yield_mpa"] / SF
    rows = [
        dict(key="tilt", name="넘어짐 각 (무게중심 ↔ 바퀴 다각형 가장자리)", value=tip["tip_deg"], unit="°", op=">=", limit=10.0, source="IEC 62368-1 8.6 10° 기울임"),
        dict(key="push", name=f"힘 시험: 수평력 {tip['push_N']:.0f} N 넘어짐 여유 (참고)", value=tip["push_margin"], unit="배", op=">=", limit=1.0,
             source="IEC 62368-1 8.6 대안 시험 (기울임과 동등) — EU 판매 시 모두 권장", ref=True),
        dict(key="down", name=f"힘 시험: 하향력 {tip['down_N']:.0f} N 넘어짐 여유 (참고)", value=min(tip["down_margin"], 99.0), unit="배", op=">=", limit=1.0,
             source="IEC 62368-1 8.6 대안 시험 — 화면 앞 윗모서리", ref=True),
        dict(key="stress", name="최대 응력 (화면 무게 + 수평력, FEM)", value=fem["vm_max"], unit="MPa", op="<=", limit=round(lim, 1), source=f"{MAT['name']} 항복 ÷ 1.5"),
        dict(key="defl", name="화면 윗단 흔들림 (수평력, FEM)", value=fem["top_defl"], unit="mm", op="<=", limit=TOP_DEFLECTION_MM, source="가정 (팀 TV 스탠드 사례)"),
        dict(key="caster", name="바퀴 하나 최대 하중 (정역학)", value=tip["caster_max_N"], unit="N", op="<=", limit=CASTER_LIMIT_N, source="가정 (캐스터 정격)"),
    ]
    for r in rows:
        r["ok"] = bool(r["value"] >= r["limit"] if r["op"] == ">=" else r["value"] <= r["limit"])
    progress.step("도면 · 결과 파일")
    drawing(body, info, tv, T, os.path.join(out, "design_1st_drawing.png"), os.path.join(out, "design_1st_drawing.pdf"), mass_stand)
    sketch_png(tid, tv, os.path.join(out, "side_view.png"), L["zc"])
    g = L["g"]
    W_, D_, H_ = L["tv_size"]
    zc_note = f"{L['zc']:.0f} mm (조절 범위 {lo:.0f}–{hi:.0f})"
    rep = base_report(
        product="TV 스탠드", tid=tid, tname=T["name"], tdesc=T["desc"], chosen_by=how, match=match, rows=rows,
        conditions=conditions(tv, tid, total),
        summary=[["제품", "이동식 TV 스탠드 (스탠바이미형)"], ["화면", f"{tv['size_in']}형 · {tv['mass_kg']} kg · {'가로' if T['orient'] == 'landscape' else '세로'}"],
                 ["이동", "바퀴 5개 · 높이 조절 · 회전"], ["재료", MAT["name"]], ["안정성 기준", "IEC 62368-1 8.6"], ["안전율", SF]],
        design_vars=[["형식", f"{tid} {T['name']}"], ["화면 (폭 × 높이)", f"{W_:.0f} × {H_:.0f} mm"], ["화면 중심 높이", zc_note],
                     ["받침", f"Ø{g['base_d']:.0f} mm 판 {g['plate_t']:.0f} mm + 허브 Ø{g['hub_d']:.0f} (스탠바이미 Ø397)"],
                     ["바퀴", f"5개 · Ø{g['wheel_d']:.0f} · 원주 반지름 {g['caster_r']:.0f} mm (앞쪽 1개)"],
                     ["기둥", f"강관 Ø{g['pole_d']:.0f} × {g['pole_t']:.0f} mm, 화면 뒤 {abs(L['back']):.0f} mm"],
                     ["캐리지 · 팔 · 헤드", f"슬리브 Ø{g['sleeve_d']:.0f} × {g['sleeve_h']:.0f}, 팔 {g['arm'][1]:.0f} mm, 장착판 {g['plate'][0]:.0f} × {g['plate'][2]:.0f}"],
                     ["스탠드 무게 (CAD)", f"{mass_stand:.1f} kg (참고: 스탠바이미 12.7 kg)"], ["전체 무게중심 높이", f"{tip['cg'][2]:.0f} mm"],
                     ["화면과 겹침", f"{info['clash_mm3']:.0f} mm³ (기둥 · 헤드는 화면 뒤)"], ["해석 격자", f"{fem['h']} mm · {fem['elements']:,} 요소"]],
        assumptions=[tv["source"], f"1차 설계 = 스케치 비율 그대로: 받침 Ø{g['base_d']:.0f} · 바퀴 원 반지름 {g['caster_r']:.0f} · 기둥 Ø{g['pole_d']:.0f} — 미충족 항목은 다음 단계(물리 최적화)에서 맞춤",
                     "스탠드 전체 강 (받침판 · 강관 · 캐리지), 배터리 · 스피커 등 내장품은 넣지 않음 (넣으면 더 안정)",
                     "바퀴 바닥 고정 (잠금 상태), 화면은 강체로 보고 장착판에 하중 분배",
                     "최대 응력 = 절점 응력 상위 0.5 % 제외값 (복셀 계단 모서리의 가짜 응력 집중 제외)",
                     f"화면 윗단 흔들림 ≤ {TOP_DEFLECTION_MM} mm, 바퀴 정격 {CASTER_LIMIT_N:.0f} N 은 가정",
                     "높이 조절 범위 = 스탠바이미 전체 높이 41.9–49.8\" 에서 계산", "데모용 1차 설계 — 최적화 단계로 넘기지 않음"],
        sources=[SOURCES["stanbyme"], SOURCES["stanbyme_us"], SOURCES["wheels"], SOURCES["iec62368"]],
        cad=dict(mass_g=round(mass_stand * 1e3, 1), material=MAT["name"]),
        extra=dict(tip=tip, fem={k: v for k, v in fem.items() if k != "heat"}, tv=tv, zc=L["zc"], z_range=[lo, hi]),
        seconds=time.time() - t0)
    finish(rep, out)
    if with_mesh:
        from .common import mesh_b64
        rep["mesh"] = mesh_b64(body)
        rep["heat"] = fem["heat"]
        rep["aux"] = [dict(kind="box", center=info["tv_box"]["center"], size=info["tv_box"]["size"], color="#1b1f24", opacity=1.0, label="화면")]
        rep["scene"] = dict(floor_z=0.0, up="z", color="#c9ccd0")
    return rep


def match_sketch(gray):
    return match(gray)


# ------------------------------------------------------------------ images
def sketch_png(tid, tv, path, zc=None):
    from ..mplkr import pyplot
    plt = pyplot()                                  # 한글 글꼴
    fig, ax = plt.subplots(figsize=(4.6, 6))
    for s in front_strokes(tid, tv, zc=zc):
        ax.plot(s[:, 0], s[:, 1], c="#222", lw=1.6)
    ax.axhline(0, c="#888", lw=1)
    ax.set_aspect("equal")
    ax.set_title(f"{tid} {BY_ID[tid]['name']} — 정면 (1차 설계 윤곽, mm)", fontsize=10)
    ax.grid(alpha=.25)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def drawing(body, info, tv, T, png, pdf, mass_kg):
    from ..mplkr import pyplot
    plt = pyplot()                                  # 한글 글꼴
    from matplotlib.collections import PolyCollection
    verts, tris = body.val().tessellate(0.5, 0.5)
    V = np.array([[p.x, p.y, p.z] for p in verts])
    F = np.array(tris)
    c = np.asarray(info["tv_box"]["center"])
    W, D, H = info["tv_box"]["size"]
    fig, ax = plt.subplots(1, 3, figsize=(16, 7), gridspec_kw=dict(width_ratios=[1.1, 1.0, 0.9]))
    views = ((0, 2, "정면", (W, H)), (1, 2, "옆 (앞 = 왼쪽)", (D, H)), (0, 1, "위 (앞 = 아래)", (W, D)))
    for a, (i, j, ttl, (sw, sh)) in zip(ax, views):
        a.add_collection(PolyCollection(V[F][:, :, [i, j]], fc="#b9c2c9", ec="none", rasterized=True))
        a.add_patch(plt.Rectangle((c[i] - sw / 2, c[j] - sh / 2), sw, sh, fill=False, ls="--", ec="#555"))
        if j == 2:
            a.axhline(0, c="#888", lw=1)
        a.set_aspect("equal")
        a.autoscale()
        a.grid(alpha=.25)
        a.set_title(ttl, fontsize=10)
    for fx, fy in info["foot"]:
        ax[2].plot(fx, fy, "o", c="#e4572e", ms=5)
    P = np.asarray(info["foot"])
    o = np.argsort(np.arctan2(P[:, 1], P[:, 0]))
    Q = np.vstack([P[o], P[o][:1]])
    ax[2].plot(Q[:, 0], Q[:, 1], c="#e4572e", lw=.8, ls=":")
    ax[2].text(0, P[:, 1].min() - 40, "빨강 = 바퀴 접지 (넘어짐 다각형)", ha="center", fontsize=8, color="#e4572e")
    ax[0].text(c[0], c[2], f"화면 {tv['size_in']}형\n{tv['mass_kg']} kg", ha="center", va="center", color="#555")
    fig.suptitle(f"TV 스탠드 (이동식) — 1차 설계 {T['id']} {T['name']} · {MAT['name']} · 스탠드 {mass_kg:.1f} kg · 단위 mm", fontsize=12)
    fig.savefig(png, dpi=170, bbox_inches="tight")             # 메인 창에 크게 띄워도 글자 선명하게
    fig.savefig(pdf, bbox_inches="tight")
    plt.close(fig)
