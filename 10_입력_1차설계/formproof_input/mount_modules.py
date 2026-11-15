"""Bike phone mount = clamp x arm (side path + cross-section) x joint x phone holder.

CAD-only module library for the look of the product (CadQuery). Frame = team frame: handlebar axis = y through
(x=0, z=0), x forward, z up, mount centred at y = Y0. Each part carries a material key so a renderer can colour it.

The analysis side keeps its own simplifications (bike_mount.build_spec): the arm side path maps to an existing
arm style, the holder becomes the rigid payload (mass / CG / box from this CAD), the clamp becomes the support.
"""
import math

import cadquery as cq
import numpy as np

Y0 = 55.0
BAR_D = 31.8
RING_RI = BAR_D / 2 + 0.2


# ------------------------------------------------------------------ primitives
def _plane(p0, d):
    d = np.asarray(d, float)
    d = d / np.linalg.norm(d)
    x = np.array([0.0, 1.0, 0.0])
    if abs(x @ d) > 0.9:
        x = np.array([1.0, 0.0, 0.0])
    x = x - (x @ d) * d
    x /= np.linalg.norm(x)
    return cq.Plane(origin=tuple(map(float, p0)), xDir=tuple(map(float, x)), normal=tuple(map(float, d)))


def _xz(p):
    return np.array([p[0], Y0, p[1]], float) if len(p) == 2 else np.asarray(p, float)


def _section(sec, w, t):
    """Cross-section in local XY (X = across the bar, Y = in the bending plane), extruded along local Z."""
    wp = cq.Workplane("XY")
    if sec == "round":
        return wp.circle(w / 2)
    if sec == "rect":
        return wp.rect(w, t)
    if sec == "trib":                                   # T: flange on top, web below
        f, web = min(2.6, t / 3), min(3.0, w / 3)
        pts = [(-w / 2, t / 2), (w / 2, t / 2), (w / 2, t / 2 - f), (web / 2, t / 2 - f), (web / 2, -t / 2),
               (-web / 2, -t / 2), (-web / 2, t / 2 - f), (-w / 2, t / 2 - f)]
        return wp.polyline(pts).close()
    if sec == "ibeam":
        f, web = min(2.4, t / 4), min(3.0, w / 3)
        pts = [(-w / 2, t / 2), (w / 2, t / 2), (w / 2, t / 2 - f), (web / 2, t / 2 - f), (web / 2, -t / 2 + f),
               (w / 2, -t / 2 + f), (w / 2, -t / 2), (-w / 2, -t / 2), (-w / 2, -t / 2 + f), (-web / 2, -t / 2 + f),
               (-web / 2, t / 2 - f), (-w / 2, t / 2 - f)]
        return wp.polyline(pts).close()
    raise ValueError(sec)


def member(p0, p1, sec="rect", w=16.0, t=7.0, w1=None, t1=None, fillet=1.2):
    """Straight member p0 -> p1 with a cross-section; w1/t1 taper the far end (rect / round only)."""
    p0, p1 = _xz(p0), _xz(p1)
    L = float(np.linalg.norm(p1 - p0))
    if w1 is not None or t1 is not None:
        w1 = w if w1 is None else w1
        t1 = t if t1 is None else t1
        if sec == "round":
            s = cq.Solid.makeCone(w / 2, w1 / 2, L)
        else:
            s = (cq.Workplane("XY").rect(w, t).workplane(offset=L).rect(w1, t1).loft()).val()
    else:
        s = _section(sec, w, t).extrude(L)
        if sec == "rect" and fillet:
            try:
                s = s.edges("|Z").fillet(min(fillet, t / 2.2, w / 2.2))
            except Exception:
                pass
        s = s.val()
    return s.moved(cq.Location(_plane(p0, p1 - p0)))


def knuckle(p, sec, w, t):
    """Rounded joint between two members of a path (sphere for tubes, a short cylinder across the bar otherwise)."""
    p = _xz(p)
    if sec == "round":
        return cq.Solid.makeSphere(w / 2, cq.Vector(*p))
    return cq.Solid.makeCylinder(t / 2, w, cq.Vector(p[0], p[1] - w / 2, p[2]), cq.Vector(0, 1, 0))


def path_solid(pts, sec, w, t, taper=None):
    parts = []
    n = len(pts) - 1
    for i in range(n):
        if taper:
            a, b = i / n, (i + 1) / n
            wa, wb = w + (taper[0] - w) * a, w + (taper[0] - w) * b
            ta, tb = t + (taper[1] - t) * a, t + (taper[1] - t) * b
            parts.append(member(pts[i], pts[i + 1], sec, wa, ta, wb, tb))
            if 0 < i:
                parts.append(knuckle(pts[i], sec, wa, ta))
        else:
            parts.append(member(pts[i], pts[i + 1], sec, w, t))
            if 0 < i:
                parts.append(knuckle(pts[i], sec, w, t))
    return union(parts)


def union(parts):
    parts = [p for p in parts if p is not None]
    out = parts[0]
    for p in parts[1:]:
        out = out.fuse(p)
    try:
        return out.clean()
    except Exception:
        return out


def box(x, y, z, fillet=0.0):
    s = cq.Workplane("XY").box(x[1] - x[0], y[1] - y[0], z[1] - z[0], centered=False).translate((x[0], y[0], z[0]))
    if fillet:
        try:
            s = s.edges().fillet(fillet)
        except Exception:
            pass
    return s.val()


def cyl(r, h, base, axis=(0, 0, 1)):
    return cq.Solid.makeCylinder(r, h, cq.Vector(*base), cq.Vector(*axis))


def annulus_y(ri, ro, w, a0=0.0, a1=360.0, yc=Y0):
    """Ring around the bar axis (y), optionally a sector between angles a0..a1 (deg, from +x toward +z)."""
    ring = cq.Workplane("XZ", origin=(0, yc + w / 2, 0)).circle(ro).circle(ri).extrude(w)
    if a1 - a0 < 359.9:
        R = ro + 5
        pts = [(0, 0)] + [(R * math.cos(math.radians(a)), R * math.sin(math.radians(a)))
                          for a in np.linspace(a0, a1, 24)]
        wedge = cq.Workplane("XZ", origin=(0, yc + w / 2 + 1, 0)).polyline(pts).close().extrude(w + 2)
        ring = ring.intersect(wedge)
    return ring.val()


def at_angle(r, a):
    return np.array([r * math.cos(math.radians(a)), Y0, r * math.sin(math.radians(a))])


# ------------------------------------------------------------------ clamps (on the bar)
def clamp_bolt(w=20.0, t=5.0):
    ro = RING_RI + t
    ring = cq.Workplane("XZ", origin=(0, Y0 + w / 2, 0)).circle(ro).circle(RING_RI).extrude(w)
    try:
        ring = ring.edges().fillet(1.0)
    except Exception:
        pass
    ears = [box([s * 1.5 if s > 0 else -7.5, 7.5 if s > 0 else -1.5], [Y0 - w / 2, Y0 + w / 2], [-RING_RI - 20, -RING_RI + 2], 1.2)
            for s in (1, -1)]
    body = union([ring.val()] + ears)
    body = body.cut(box([-1.2, 1.2], [Y0 - w, Y0 + w], [-60, -RING_RI + 3]))
    bolts = [cyl(3.4, 3.6, (7.4, Y0 + dy, -RING_RI - 11), (1, 0, 0)) for dy in (-5, 5)]
    nuts = [cyl(3.6, 3.0, (-10.4, Y0 + dy, -RING_RI - 11), (1, 0, 0)) for dy in (-5, 5)]
    return dict(parts=[("primary", body), ("metal", union(bolts)), ("metal", union(nuts))], ro=ro, top=ro, front=ro)


def clamp_hinge(w=16.0, t=4.5):
    ro = RING_RI + t
    ring = annulus_y(RING_RI, ro, w, -25.0, 230.0)
    k = at_angle(ro + 1.5, 205)
    knuckle_ = cyl(4.3, w, (k[0], Y0 - w / 2, k[2]), (0, 1, 0))
    k2 = at_angle(ro + 1.0, 238)
    lower = annulus_y(RING_RI, ro, w, 232.0, 312.0)
    pin = cyl(1.6, w + 3, (k[0], Y0 - w / 2 - 1.5, k[2]), (0, 1, 0))
    lug_a, lug_b = at_angle(ro + 4, -22), at_angle(ro + 4, -50)
    lugs = [box([p[0] - 4, p[0] + 4], [Y0 - w / 2, Y0 + w / 2], [p[2] - 3, p[2] + 3], 1.0) for p in (lug_a, lug_b)]
    knob_c = at_angle(ro + 11, -36)
    knob = cyl(6.5, 7.0, (knob_c[0] + 3.5, Y0, knob_c[2] - 2), (-0.5, 0, -0.866))
    screw = cyl(1.8, 16.0, tuple(lug_a + np.array([0, 0, 2])), (-0.5, 0, -0.866))
    return dict(parts=[("primary", union([ring, knuckle_] + lugs[:1])), ("primary", union([lower] + lugs[1:])),
                       ("metal", pin), ("metal", screw), ("accent", knob)], ro=ro, top=ro, front=ro)


def clamp_strap(w=26.0, t=5.5):
    ro = RING_RI + t
    saddle = annulus_y(RING_RI, ro, w, 10.0, 170.0)
    try:
        saddle = cq.Workplane().add(saddle).edges().fillet(1.2).val()
    except Exception:
        pass
    strap = annulus_y(BAR_D / 2 - 0.05, BAR_D / 2 + 1.8, 12.0, 168.0, 372.0)
    hook = cyl(2.6, 14.0, tuple(at_angle(ro + 1.0, 12) + np.array([0, -7, 0])), (0, 1, 0))
    tab = box([ro - 1, ro + 6], [Y0 - 6, Y0 + 6], [-2.5, 1.5], 0.8)
    return dict(parts=[("primary", union([saddle, hook])), ("rubber", union([strap, tab]))], ro=ro, top=ro, front=ro * 0.95)


CLAMPS = {
    "bolt": dict(name="볼트 링 클램프", fn=clamp_bolt, support="볼트 2개로 조인 링, 완전 고정"),
    "hinge": dict(name="경첩 퀵 클램프", fn=clamp_hinge, support="경첩 + 손나사, 완전 고정(조임력 가정)"),
    "strap": dict(name="고무 스트랩", fn=clamp_strap, support="반원 받침 + 고무 띠, 탄성 지지(강성 가정 필요)"),
}


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
    if style == "out_front":
        return [[f0, (78.0, -3.0), (84.0, 4.0)]], (84.0, 4.0), (0.6, 0.8), "step"
    if style == "out_front_long":
        return [[f0, (104.0, -4.0), (110.0, 4.0)]], (110.0, 4.0), (0.6, 0.8), "step"
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
SECTIONS = {"rect": "모서리 둥근 사각", "round": "둥근 관", "trib": "T자 리브", "ibeam": "I자 리브", "taper": "끝으로 가늘어짐"}


# ------------------------------------------------------------------ joints (between arm end and holder back)
def joint(kind, p, d):
    """Returns (parts, length along the holder normal) at arm end p (3D)."""
    p = np.asarray(p, float)
    if kind == "ball":
        return [("metal", cq.Solid.makeSphere(6.5, cq.Vector(*(p + np.array([0, 0, 4]))))),
                ("primary", cyl(8.5, 5.0, tuple(p - np.array([0, 0, 1.5]))))], 9.0
    if kind == "disc":
        return [("secondary", cyl(13.0, 4.0, tuple(p))), ("metal", cyl(4.5, 3.0, tuple(p + np.array([0, 0, 4]))))], 7.0
    return [("primary", cyl(9.0, 3.0, tuple(p)))], 3.0


JOINTS = {"ball": "볼 조인트", "disc": "회전 원판", "fixed": "고정"}


# ------------------------------------------------------------------ holders (phone frame: phone back at z=0, long side x)
def holder_side_clamp(H, W, D):
    body = box([-24, 24], [-W * 0.28, W * 0.28], [-13, -2], 3.0)
    rails = [box([-15, 15], sorted([0, s * (W / 2 + 3)]), [-9, -3], 1.4) for s in (1, -1)]
    jaws, lips, pads = [], [], []
    for s in (1, -1):
        y0, y1 = sorted([s * (W / 2 + 0.6), s * (W / 2 + 5)])
        jaws.append(box([-16, 16], [y0, y1], [-9, D + 3.2], 1.4))
        l0, l1 = sorted([s * (W / 2 - 2.4), s * (W / 2 + 5)])
        lips.append(box([-16, 16], [l0, l1], [D + 0.4, D + 3.2], 1.0))
        p0, p1 = sorted([s * (W / 2), s * (W / 2 + 0.7)])
        pads.append(box([-14, 14], [p0, p1], [0.2, D], 0))
    boss = cyl(9.0, 4.0, (0, 0, -17))
    return [("primary", union([body, boss] + rails)), ("secondary", union(jaws + lips)), ("rubber", union(pads))], 17.0


def holder_x_grip(H, W, D):
    hub = cyl(15.0, 8.0, (0, 0, -10))
    cap = cyl(10.0, 2.5, (0, 0, -2.5))
    arms, cups = [], []
    for sx in (1, -1):
        for sy in (1, -1):
            c = np.array([sx * (H / 2 - 4.0), sy * (W / 2 - 3.0), 0.0])
            arms.append(member((0, 0, -6), (c[0] * 0.97, c[1] * 0.97, -6), "round", 5.0, 5.0))
            cup = cyl(7.0, D + 8.0, (c[0], c[1], -6.0))
            ph = box([-H / 2, H / 2], [-W / 2, W / 2], [0, D], 0)
            cups.append(cup.cut(ph))
    return [("primary", union([hub, cap])), ("metal", union(arms)), ("rubber", union(cups))], 10.0


def holder_silicone(H, W, D):
    tray = (cq.Workplane("XY").box(H * 0.9, W + 6, 3.0).translate((0, 0, -1.5)).edges("|Z").fillet(11).val())
    ph = cq.Workplane("XY").box(H, W, D).translate((0, 0, D / 2)).edges("|Z").fillet(9).val()
    corners = []
    for sx in (1, -1):
        for sy in (1, -1):
            b = (cq.Workplane("XY").box(26, 24, D + 5).translate((sx * (H / 2 - 9), sy * (W / 2 - 8), (D + 5) / 2 - 3))
                 .edges("|Z").fillet(7).val())
            corners.append(b)
    sil = union([tray] + corners).cut(ph.translate(cq.Vector(0, 0, 0)))
    window = (cq.Workplane("XY").box(H * 0.9 - 40, W - 18, 20).translate((0, 0, D + 4)).val())
    sil = sil.cut(window)
    base = union([cyl(16.0, 5.0, (0, 0, -8)), box([-30, 30], [-10, 10], [-6, -3], 1.0)])
    return [("rubber_col", sil), ("primary", base)], 8.0


def holder_magsafe(H, W, D):
    puck = cq.Workplane("XY").circle(29).extrude(8).translate((0, 0, -8)).edges(">Z").fillet(2.0).val()
    ring = cq.Workplane("XY").circle(26).circle(22.5).extrude(0.6).translate((0, 0, -0.4)).val()
    neck = cyl(11.0, 6.0, (0, 0, -14))
    return [("secondary", puck), ("metal", ring), ("primary", neck)], 14.0


def holder_twist(H, W, D):
    puck = cyl(20.0, 7.0, (0, 0, -10))
    tabs = [box([-5, 5], sorted([s * 14, s * 22]), [-3.5, 0.0], 0.6) for s in (1, -1)] + \
           [box(sorted([s * 14, s * 22]), [-5, 5], [-3.5, 0.0], 0.6) for s in (1, -1)]
    lever = box([-28, -18], [-4, 4], [-9, -4], 1.2)
    adapter = cyl(21.0, 2.5, (0, 0, -2.5))
    case = (cq.Workplane("XY").box(H + 2.4, W + 2.4, D + 1.2).translate((0, 0, (D + 1.2) / 2 - 1.2)).edges("|Z").fillet(10).val())
    phone = cq.Workplane("XY").box(H, W, D).translate((0, 0, D / 2)).edges("|Z").fillet(9).val()
    case = case.cut(phone.translate(cq.Vector(0, 0, 0.6)))
    return [("primary", union([puck] + tabs)), ("accent", lever), ("case", union([adapter, case]))], 10.0


def holder_hooks(H, W, D):
    plate = (cq.Workplane("XY").box(H * 0.55, W * 0.72, 4.0).translate((0, 0, -2.0)).edges("|Z").fillet(8).val())
    hooks = []
    for sy in (1, -1):
        y = sy * W * 0.26
        hooks += [box([-H / 2 - 4, -H / 2], [y - 7, y + 7], [-4, D + 3], 1.2),
                  box([-H / 2 - 4, -H / 2 + 3], [y - 7, y + 7], [D, D + 3], 1.0),
                  box([-H / 2 - 2, -H * 0.27], [y - 5, y + 5], [-4, -1], 1.0)]
    top = [box([H * 0.25, H / 2 + 4], [-7, 7], [-4.5, -1.5], 1.0), box([H / 2, H / 2 + 4], [-7, 7], [-4.5, D + 3], 1.2),
           box([H / 2 - 3, H / 2 + 4], [-7, 7], [D, D + 3], 1.0)]
    pads = [box([-H / 2 + 0.1, -H / 2 + 0.8], [sy * W * 0.26 - 6, sy * W * 0.26 + 6], [0.3, D], 0) for sy in (1, -1)]
    boss = cyl(10.0, 4.0, (0, 0, -8))
    return [("primary", union([plate, boss] + hooks)), ("secondary", union(top)), ("rubber", union(pads))], 8.0


HOLDERS = {
    "side_clamp": dict(name="양옆 스프링 집게", fn=holder_side_clamp),
    "x_grip": dict(name="X자 네 모서리 집게", fn=holder_x_grip),
    "silicone": dict(name="실리콘 모서리 감싸기", fn=holder_silicone),
    "magsafe": dict(name="자석 원판", fn=holder_magsafe),
    "twist": dict(name="회전 잠금(전용 케이스)", fn=holder_twist),
    "hooks": dict(name="아래 갈고리 + 위 스프링 고리", fn=holder_hooks),
}


def phone_solid(H, W, D):
    body = cq.Workplane("XY").box(H, W, D).translate((0, 0, D / 2)).edges("|Z").fillet(9)
    try:
        body = body.edges("not |Z").fillet(1.6)
    except Exception:
        pass
    screen = cq.Workplane("XY").box(H - 4, W - 4, 0.3).translate((0, 0, D)).edges("|Z").fillet(7).val()
    return [("phone", body.val()), ("screen", screen)]


# ------------------------------------------------------------------ assembly
def build(cfg):
    """cfg: clamp, arm, section, holder, joint, tilt_deg, phone (H, W, D), arm_w, arm_t -> [(material, solid, module)], info."""
    H, W, D = cfg.get("phone", (162.8, 77.6, 8.2))
    c = CLAMPS[cfg["clamp"]]["fn"]()
    parts = [(m, sol, "clamp") for m, sol in c["parts"]]
    paths, tip, tdir, maps_to = arm_paths(cfg["arm"], c["top"], c["front"])
    sec = cfg.get("section", "rect")
    w, t = cfg.get("arm_w", 16.0), cfg.get("arm_t", 8.0)
    arm = []
    for k, pth in enumerate(paths):
        if sec == "taper":
            arm.append(path_solid(pth, "rect", w, t, taper=(w * 0.65, t * 0.75)))
        else:
            ww, tt = (w, t) if k == 0 else (w * 0.7, t * 0.75)
            arm.append(path_solid(pth, sec, ww, tt))
    parts.append(("primary", union(arm), "arm"))
    tip3 = _xz(tip)
    jparts, jlen = joint(cfg.get("joint", "fixed"), tip3, tdir)
    parts += [(m, sol, "joint") for m, sol in jparts]
    default_tilt = 8.0 if cfg["arm"].startswith("out_front") else 20.0
    th = math.radians(cfg.get("tilt_deg", default_tilt))
    hparts, depth = HOLDERS[cfg["holder"]]["fn"](H, W, D)
    nrm = np.array([-math.sin(th), 0.0, math.cos(th)])
    origin = tip3 + np.array([0, 0, jlen]) + nrm * depth
    loc = cq.Location(cq.Vector(*origin), cq.Vector(0, 1, 0), -math.degrees(th))
    for mat, sol in hparts:
        parts.append((mat, sol.moved(loc), "holder"))
    if cfg.get("with_phone", True):
        for mat, sol in phone_solid(H, W, D):
            parts.append((mat, sol.moved(loc), "phone"))
    rho = 1.27e-3                                                     # PETG g/mm^3 (printed parts only)
    printed = ("primary", "secondary", "accent")
    mass = {m: round(sum(sol.Volume() for mt, sol, mod in parts if mod in m_ and mt in printed) * rho, 1)
            for m, m_ in (("body", ("clamp", "arm", "joint")), ("holder", ("holder",)))}
    info = dict(maps_to=maps_to, tip=[round(float(v), 1) for v in tip3], phone_origin=[round(float(v), 1) for v in origin],
                tilt_deg=round(math.degrees(th), 1), mass_g=mass)
    return parts, info
