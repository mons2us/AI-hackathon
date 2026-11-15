"""Look modules of the bike phone mount without CAD: names, arm side paths, clamp sizes and the rigid payload table.

clamp x arm (side path) x cross-section x joint x phone holder.  The CAD for each module is in mount_modules
(CadQuery); this file is what the analysis (templates/bike_mount, look=...) and the browser engine need, so a spec can
be built without CadQuery.  The holder + joint + phone payload (mass, CG, inertia) comes from the CAD, precomputed in
templates/db/look_payload.json (python -m formproof_input.look --build).
"""
import json
import math
import os

import numpy as np

CLAMP_SPEC = {   # width / ring_t: the analysis uses the same values (clamp_w, ring_t)
    "bolt": dict(name="볼트 링 클램프", width=20.0, ring_t=4.5, ears=True, saddle=None,
                 support="볼트 2개로 조인 링, 링 안쪽 전체 고정"),
    "hinge": dict(name="경첩 퀵 클램프", width=16.0, ring_t=4.5, ears=False, saddle=None,
                  support="경첩 + 손나사로 닫는 링, 링 안쪽 전체 고정(경첩·손나사 귀는 해석에서 생략)"),
    "strap": dict(name="고무 스트랩", width=26.0, ring_t=5.5, ears=False, saddle=(0.0, 180.0),
                  support="반원 받침이 핸들 위에 얹히고 고무 띠가 감쌈. 받침 안쪽(위쪽 반원)만 고정, 띠 강성 무시"),
}
HOLDER_SPEC = {   # depth = joint top -> phone back (mm, = mount_modules holder fn); joint = default joint
    "side_clamp": dict(depth=17.0, name="양옆 스프링 집게", joint="ball"),
    "x_grip": dict(depth=10.0, name="X자 네 모서리 집게", joint="ball"),
    "silicone": dict(depth=8.0, name="실리콘 모서리 감싸기", joint="fixed"),
    "magsafe": dict(depth=14.0, name="자석 원판", joint="disc"),
    "twist": dict(depth=10.0, name="회전 잠금(전용 케이스)", joint="fixed"),
    "hooks": dict(depth=8.0, name="아래 갈고리 + 위 스프링 고리", joint="disc"),
}
JOINTS = {"ball": "볼 조인트", "disc": "회전 원판", "fixed": "고정"}
JOINT_LEN = {"ball": 9.0, "disc": 7.0, "fixed": 3.0}
ARM_W, ARM_T = 16.0, 8.0          # main member: width across the bar (y), thickness in the side view; round: diameter ARM_W


TILTS = (20.0, 15.0, 10.0, 5.0, 0.0)   # phone tilt toward the rider (deg); the largest that clears is used
CLEAR_RING, CLEAR_ARM = 3.0, 4.0       # mm: phone side outline vs clamp ring / vs the arm away from the joint


def default_tilt(arm):
    """Nominal tilt (no geometry): kept for the CAD gallery; templates use fit_tilt."""
    return 20.0


def phone_outline(base, joint_len, depth, tilt, dims, n=41):
    """Side-view points of the phone (x, z) for joint base (x, z), holder depth and tilt."""
    th = math.radians(tilt)
    nrm = np.array([-math.sin(th), math.cos(th)])
    tan = np.array([math.cos(th), math.sin(th)])
    org = np.asarray(base, float) + np.array([0.0, joint_len]) + nrm * depth
    H, _, D = dims
    return np.array([org + tan * a + nrm * b for a in np.linspace(-H / 2, H / 2, n) for b in (0.0, D / 2, D)])


def clearance(paths, ring_ro, base, joint_len, depth, tilt, dims):
    """(ring clearance, arm clearance) in mm of the phone in the side view."""
    P = phone_outline(base, joint_len, depth, tilt, dims)
    d_ring = float(np.hypot(P[:, 0], P[:, 1]).min() - ring_ro)
    pts = []
    for pth in paths:                                          # arm centre line, densified, away from the joint
        q = np.asarray(pth, float)
        for a, b in zip(q[:-1], q[1:]):
            for s in np.linspace(0, 1, 9):
                pts.append(a + (b - a) * s)
    pts = np.array(pts)
    pts = pts[np.hypot(*(pts - np.asarray(base, float)).T) > 20.0]
    d_arm = 99.0 if not len(pts) else float(np.sqrt(((P[:, None, :] - pts[None]) ** 2).sum(-1)).min() - ARM_T / 2)
    return d_ring, d_arm


def fit_tilt(paths, ring_ro, base, joint_len, depth, dims):
    """Largest tilt in TILTS whose phone clears the clamp ring and the arm; 0 if none does (flagged by the caller)."""
    for t in TILTS:
        r, a = clearance(paths, ring_ro, base, joint_len, depth, t, dims)
        if r >= CLEAR_RING and a >= CLEAR_ARM:
            return t, r, a
    r, a = clearance(paths, ring_ro, base, joint_len, depth, 0.0, dims)
    return 0.0, r, a


# ------------------------------------------------------------------ arms (side paths in the xz plane)
def _spline(ctrl, n=14):
    """Catmull-Rom through control points (xz)."""
    P = [np.asarray(p, float) for p in ctrl]
    P = [P[0] - (P[1] - P[0])] + P + [P[-1] + (P[-1] - P[-2])]
    out = []
    for i in range(1, len(P) - 2):
        for s in np.linspace(0, 1, n // (len(ctrl) - 1) + 1)[:-1]:
            p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s ** 2 + (-p0 + 3 * p1 - 3 * p2 + p3) * s ** 3))
    out.append(P[-2])
    return [tuple(p) for p in out]


def arm_paths(style, top, front):
    """Lists of point paths (xz, mm); the last point of the first path is where the joint / holder sits.
    `maps_to` = existing analysis arm style (bike_mount)."""
    t0 = (0.0, top - 2.0)
    f0 = (front - 2.0, 0.0)
    if style == "riser":
        return [[t0, (0.0, 30.0)]], (0.0, 30.0), (0, 1), "riser"
    if style == "tall_riser":
        return [[t0, (0.0, 52.0)]], (0.0, 52.0), (0, 1), "riser"
    if style == "angled":
        return [[t0, (52.0, 44.0)]], (52.0, 44.0), (0.76, 0.65), "straight"
    if style == "gooseneck":
        p = _spline([t0, (6.0, 34.0), (26.0, 52.0), (58.0, 56.0)])
        return [p], p[-1], (1, 0.1), "dogleg"
    if style == "long_gooseneck":
        p = _spline([t0, (10.0, 40.0), (40.0, 62.0), (90.0, 60.0)], n=18)
        return [p], p[-1], (1, 0), "dogleg"
    if style == "out_front":          # forward at bar height, then up so the phone clears the bar
        return [[f0, (70.0, -2.0), (82.0, 14.0)]], (82.0, 14.0), (0.6, 0.8), "step"
    if style == "out_front_long":
        return [[f0, (96.0, -3.0), (108.0, 14.0)]], (108.0, 14.0), (0.6, 0.8), "step"
    if style == "L":
        return [[t0, (0.0, 40.0), (50.0, 40.0)]], (50.0, 40.0), (1, 0), "L"
    if style == "truss":
        top_ = [t0, (16.0, 34.0), (64.0, 34.0)]
        brace = [(front * 0.85, top * 0.45), (44.0, 34.0)]
        return [top_, brace], (64.0, 34.0), (1, 0), "truss"
    if style == "vee":
        tip = (62.0, 38.0)
        return [[t0, tip], [(front - 2.0, 3.0), tip]], tip, (0.85, 0.5), "vee"
    raise ValueError(style)


ARMS = {
    "riser": "핸들 위 짧은 기둥", "tall_riser": "핸들 위 높은 기둥", "angled": "비스듬한 곧은 팔",
    "gooseneck": "구스넥(곡선)", "long_gooseneck": "긴 구스넥", "out_front": "아웃프론트",
    "out_front_long": "긴 아웃프론트", "L": "L자 팔", "truss": "트러스(아래 보강대)", "vee": "V자 두 팔",
}
ARM_DEFAULT_SECTION = {"riser": "rect", "tall_riser": "rect", "angled": "rect", "gooseneck": "round",
                       "long_gooseneck": "round", "out_front": "trib", "out_front_long": "trib", "L": "round",
                       "truss": "ibeam", "vee": "round"}
SECTIONS = {"rect": "모서리 둥근 사각", "round": "둥근 관", "trib": "T자 리브", "ibeam": "I자 리브", "taper": "끝으로 가늘어짐"}




# ------------------------------------------------------------------ rigid payload table (from the CAD)
DB = os.path.join(os.path.dirname(__file__), "templates", "db", "look_payload.json")
_TABLE = None


def payload_key(holder, joint, tilt, dims):
    return f"{holder}|{joint}|{float(tilt):g}|" + "x".join(f"{float(v):g}" for v in dims)


def _table():
    global _TABLE
    if _TABLE is None:
        _TABLE = json.load(open(DB, encoding="utf-8")) if os.path.exists(DB) else {}
    return _TABLE


def payload_entry(holder, joint, tilt, dims):
    """Holder + joint parts (mass kg, CG mm, inertia kg mm^2 about own CG) and the phone shape (CG, inertia per kg),
    relative to the joint base (pad top centre).  From the table, else computed with CadQuery and cached."""
    k = payload_key(holder, joint, tilt, dims)
    t = _table()
    if k not in t:
        from . import mount_modules as MM                      # CadQuery only when the table misses
        t[k] = MM.payload_entry(holder, joint, tilt, dims)
    return t[k]


def combine_payload(entry, base, phone_case_kg):
    """Rigid payload = holder + joint parts + phone (incl. case) as one body. base = joint base point (x, y, z)."""
    items = [(e["m"], np.asarray(e["cg"], float), np.asarray(e["I"], float)) for e in entry["parts"]]
    ph = entry["phone"]
    items.append((phone_case_kg, np.asarray(ph["cg"], float), np.asarray(ph["I_per_kg"], float) * phone_case_kg))
    m = sum(i[0] for i in items)
    cg = sum(i[0] * i[1] for i in items) / m
    J = np.zeros((3, 3))
    for mi, ci, Ii in items:
        d = ci - cg
        J += Ii + mi * ((d @ d) * np.eye(3) - np.outer(d, d))
    holder_kg = sum(e["m"] for e in entry["parts"])
    return dict(mass_kg=m, cg=(cg + np.asarray(base, float)).tolist(), inertia=J.tolist(), holder_kg=holder_kg,
                phone_case_kg=phone_case_kg, parts={e["module"] + ":" + e["mat"]: round(e["m"] * 1e3, 1) for e in entry["parts"]})


def build_table(phones):
    """All holder x joint x tilt x phone combinations (CadQuery)."""
    from . import mount_modules as MM
    out = {}
    tilts = TILTS
    for hk in HOLDER_SPEC:
        for jk in JOINTS:
            for tl in tilts:
                for dims in phones:
                    out[payload_key(hk, jk, tl, dims)] = MM.payload_entry(hk, jk, tl, dims)
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    with open(DB, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    return out


if __name__ == "__main__":
    import sys
    from . import evidence as ev
    if "--build" in sys.argv:
        t = build_table([ev.PHONE_DEFAULT_DIMS] + [v["dims"] for v in ev.PHONES.values()])
        print(len(t), "entries ->", DB)
