"""Bicycle phone mount: template parameters -> design spec.

Frame (same as the team's opt3d.py): handlebar axis = y axis through (x=0, z=0),
x = forward (riding direction), z = up, y = across; symmetry plane y = Y_SYM, half model
on y >= Y_SYM. All template parameters are physical sizes in mm; the generator snaps
element-region bounds to grid lines so a bound never sits on an element centre.

DEFAULT reproduces opt3d.py (team v7 3D problem) element-for-element (tests/test_reproduce_opt3d.py).
"""
import copy
import math
from .. import evidence as ev

Y_SYM = 55.0          # team frame convention (inherited from the 2.5D model)

DEFAULT = dict(
    h=2.0,
    bar_d=31.8,           # handlebar diameter at the clamp
    bore_gap=0.2,         # radial clearance bar -> clamp bore
    ring_t=4.5,           # clamp ring wall
    clamp_w=20.0,         # ring / ear / pad / arm width (full, across y)
    slit_w=4.0,           # clamp split under the bar (physical voxel width)
    ear_x=(2.0, 8.0),     # bolt ears either side of the slit, |x| range
    ear_len=20.0,         # ears hang down this far from ear_top
    pad_x0=80.0, pad_len=20.0,      # phone pad (forward reach)
    pad_z0=16.0, pad_t=4.0,         # pad bottom height and thickness
    post_x=(6.0, 16.0),   # phone-clamp stand-in, measured from pad_x0
    post_w=12.0,          # full width of the post
    post_h=22.0,          # stand-in height above pad (phone COG lever)
    above_margin=4.0,     # design space allowed above pad top (behind the phone)
    holder_gap=2.0,       # keep this much clear in front of pad start above the pad
    design_w=40.0,        # full width of the design space
    arm="straight",       # initial (1st) design arm: straight | L | truss | low
    arm_t=6.0,            # arm thickness in the side view
    phone="default",      # key in evidence.PHONES or 'default'
    phone_mass_kg=None,   # user-stated phone mass overrides the table
    road="cobblestone",
    material="PETG",
    objective="min_mass",
    safety_factor=None,   # None -> evidence.FACTORS
    include_self_inertia=False,   # team v7 ignores bracket self-inertia in shock cases
)


def _snap(v, o, h, outward=0):
    t = (v - o) / h
    if abs(t - round(t)) < 1e-9:
        return o + h * round(t)
    if outward < 0:
        return o + h * math.floor(t)
    if outward > 0:
        return o + h * math.ceil(t)
    return o + h * round(t)


def _arm_segments(p, ro):
    """Initial-design arm in the xz side view as thick segments (p0, p1)."""
    xp, zp = p["pad_x0"], p["pad_z0"]
    start = (0.0, ro - p["arm_t"] / 2)               # top of the clamp ring
    style = p["arm"]
    if style == "straight":
        return [(start, (xp + 2.0, zp + p["pad_t"] / 2))]
    if style == "L":                                  # up, then forward
        corner = (0.0, zp + p["pad_t"] / 2)
        return [(start, corner), (corner, (xp + 2.0, zp + p["pad_t"] / 2))]
    if style == "truss":                              # straight arm + lower strut from ring front
        lower = (ro - p["arm_t"] / 2, 0.0)
        mid = (xp * 0.6, zp + p["pad_t"] / 2)
        return [(start, (xp + 2.0, zp + p["pad_t"] / 2)), (lower, mid)]
    if style == "low":                                # leaves the ring front, straight toward a low pad
        tgt = (xp + 2.0, zp + p["pad_t"] / 2)
        n = math.hypot(*tgt)
        s2 = ((ro - p["arm_t"] / 2) * tgt[0] / n, (ro - p["arm_t"] / 2) * tgt[1] / n)
        return [(s2, tgt)]
    raise ValueError(f"unknown arm style {style}")


def build_spec(params=None, template_id="custom", meta=None):
    p = copy.deepcopy(DEFAULT)
    p.update(params or {})
    h = p["h"]
    R = p["bar_d"] / 2
    bore = R + p["bore_gap"]
    ro = bore + p["ring_t"]
    yw = Y_SYM + p["clamp_w"] / 2
    ypost = Y_SYM + p["post_w"] / 2

    # grid origin on the frame: x lines on multiples of h, y lines from Y_SYM, z lines on multiples of h
    ear_top = _snap(-bore + 2.0, 0.0, h)
    ear_bot = _snap(ear_top - p["ear_len"], 0.0, h)
    x_min = _snap(-(ro + 2.0), 0.0, h, outward=-1)
    z_min = _snap(min(ear_bot, -ro) - 2.0, 0.0, h, outward=-1)
    pad_x0 = _snap(p["pad_x0"], 0.0, h)
    pad_x1 = _snap(p["pad_x0"] + p["pad_len"], 0.0, h)
    pad_z0 = _snap(p["pad_z0"], 0.0, h)
    pad_z1 = _snap(p["pad_z0"] + p["pad_t"], 0.0, h)
    post_x0 = _snap(pad_x0 + p["post_x"][0], 0.0, h)
    post_x1 = _snap(pad_x0 + p["post_x"][1], 0.0, h)
    z_above = max(pad_z1 + p["above_margin"], _snap(ro + 2.0, 0.0, h, outward=1))   # never cut the ring
    z_top = max(_snap(pad_z1 + p["post_h"], 0.0, h), z_above + 2 * h)
    x_max = pad_x1
    ny = int(round(p["design_w"] / 2 / h))
    nx = int(round((x_max - x_min) / h))
    nz = int(round((z_top - z_min) / h))
    sx = _snap(p["slit_w"] / 2, 0.0, h)
    ex0, ex1 = (_snap(v, 0.0, h) for v in p["ear_x"])
    cyl = lambda **kw: {"cyl": dict(axis="y", center=[0.0, 0.0], **kw)}
    box = lambda **kw: {"box": kw}

    regions = [
        dict(name="bore", role="void", shape=[cyl(r_max=bore)], why="핸들바가 지나가는 구멍"),
        dict(name="slit", role="void", shape=[box(x=[-sx, sx], z=[None, 0.0]), cyl(r_max=ro + 5.4)],
             why="클램프 조임용 절개"),
        dict(name="post", role="rigid", stiffness_scale=20.0, mass_scale=0.0,
             shape=[box(x=[post_x0, post_x1], z=[pad_z1, None], y=[None, ypost])],
             why="시판 폰 클램프(강체 가정, 질량은 point_masses에 포함)"),
        dict(name="holder", role="void", shape=[box(x=[pad_x0 - p["holder_gap"], None], z=[pad_z1, None])],
             minus=["post"], why="폰이 놓이는 공간"),
        dict(name="above", role="void", shape=[box(z=[z_above, None])], minus=["post"],
             why="폰 뒤 공간은 받침판 위 일정 높이까지만 허용"),
        dict(name="contact", role="solid", shape=[cyl(r_min=bore, r_max=ro, y=[None, yw])],
             why="핸들바 클램프 링(지킬 곳)"),
        dict(name="ears", role="solid",
             shape={"union": [[box(x=[ex0, ex1], z=[ear_bot, ear_top], y=[None, yw])],
                              [box(x=[-ex1, -ex0], z=[ear_bot, ear_top], y=[None, yw])]]},
             why="M4 볼트 귀(지킬 곳)"),
        dict(name="pad", role="solid", shape=[box(x=[pad_x0, pad_x1], z=[pad_z0, pad_z1], y=[None, yw])],
             why="폰 클램프 받침판(지킬 곳)"),
    ]
    arm = [{"seg": dict(plane="xz", p0=list(a), p1=list(b), t=p["arm_t"], y=[None, yw])}
           for a, b in _arm_segments(p, ro)]

    mat = ev.MATERIALS[p["material"]]
    road = ev.ROADS.get(p["road"])
    road_status = "cited"
    if road is None:
        road, road_status = ev.ROADS[ev.ROAD_FALLBACK], "fallback"
    sf = p["safety_factor"] or ev.FACTORS["safety_factor"]
    tmax = ev.FACTORS["t_max"]
    f_min = road["f_hi"] / math.sqrt(1.0 - 1.0 / tmax)
    if p["phone"] in ev.PHONES:
        ph = ev.PHONES[p["phone"]]
        m_phone, phone_src, phone_name = ph["mass"], ph["source"], ph["name"]
    else:
        m_phone, phone_src, phone_name = ev.PHONE_DEFAULT_MASS, "team_v7", "기종 미지정(200 g 가정)"
    if p["phone_mass_kg"]:
        m_phone, phone_src, phone_name = p["phone_mass_kg"], "user", "사용자 입력 폰"
    m_total = m_phone + ev.PHONE_CLAMP_MASS

    spec = {
        "schema": "formproof.spec/0.1",
        "product": "bike_phone_mount",
        "template": {"id": template_id, "params": p, **(meta or {})},
        "units": {"length": "mm", "mass": "t (kg in point_masses)", "force": "N", "stress": "MPa", "time": "s"},
        "grid": {"h": h, "origin": [x_min, Y_SYM, z_min], "shape": [nx, ny, nz],
                 "symmetry": {"axis": "y", "at": Y_SYM, "cases": ["S", "A"]}},
        "material": dict(name=p["material"], E=mat["E"], nu=mat["nu"], rho=mat["rho"],
                         yield_mpa=mat["yield_mpa"], interlayer_mpa=mat["interlayer_mpa"], source=mat["source"]),
        "regions": regions,
        "initial_design": {"name": "arm", "style": p["arm"], "shape": arm,
                           "why": "스케치의 팔 형상 = 1차 설계. 설계 영역 안에서만 유효"},
        "supports": [{"name": "handlebar", "type": "fixed", "dofs": "xyz",
                      "nodes": [cyl(r_max=bore + 0.6)],
                      "assumption": "클램프 내면이 핸들바에 완전 고정(미끄럼·회전 없음)"}],
        "point_masses": [{"name": "phone_clamp", "mass_kg": round(m_total, 4),
                          "nodes": [box(x=[post_x0, post_x1], y=[None, ypost], z=[z_top, None])],
                          "source": [phone_src, "assumed:clamp_50g"],
                          "note": f"{phone_name} {m_phone*1e3:.0f} g + 폰 클램프 {ev.PHONE_CLAMP_MASS*1e3:.0f} g, 클램프 상단에 집중"}],
        "load_cases": [
            {"name": "road_vibration", "type": "modal", "modes_per_case": 2,
             "excitation_hz": [road["f_lo"], road["f_hi"]], "source": road["source"]},
            {"name": "shock_vertical", "type": "inertial", "accel_g": road["peak_g"], "dir": [0, 0, -1],
             "applies_to": ["phone_clamp"], "include_self": p["include_self_inertia"], "source": road["source"]},
            {"name": "shock_lateral", "type": "inertial", "accel_g": road["peak_g"], "dir": [0, 1, 0],
             "applies_to": ["phone_clamp"], "include_self": p["include_self_inertia"],
             "source": "assumed:lateral_equals_vertical"},
        ],
        "objective": {"type": p["objective"]},
        "constraints": [
            {"id": "f1", "quantity": "natural_frequency_hz", "op": ">=", "value": round(f_min, 1),
             "load_case": "road_vibration",
             "derivation": f"T_max={tmax:.3f} -> f1 >= {road['f_hi']} / sqrt(1-1/T_max)", "source": ["sdof", road["source"]]},
            {"id": "stress", "quantity": "von_mises_max_mpa", "op": "<=", "value": round(mat["yield_mpa"] / sf, 1),
             "load_cases": ["shock_vertical", "shock_lateral"], "exclude_regions": ["contact"],
             "derivation": f"yield {mat['yield_mpa']} / SF {sf}", "source": [mat["source"], "assumed:sf"]},
            {"id": "interlayer", "quantity": "layer_normal_tension_mpa", "op": "<=",
             "value": round(mat["interlayer_mpa"] / sf, 1), "layer_normal": "y",
             "load_cases": ["shock_vertical", "shock_lateral"], "exclude_regions": ["contact"],
             "derivation": f"interlayer {mat['interlayer_mpa']} / SF {sf}, 옆으로 눕혀 출력(적층 방향 y)",
             "source": [mat["source"], "assumed:print_orientation"]},
            {"id": "min_feature", "quantity": "min_member_thickness_mm", "op": ">=",
             "value": ev.FACTORS["min_feature_mm"], "source": ["team_v7"]},
        ],
        "evidence": {k: ev.SOURCES[k] for k in sorted({mat["source"], road["source"], "sdof", "team_v7", phone_src} & set(ev.SOURCES))},
        "assumptions": [
            "노면 진동은 바퀴 축 측정값을 핸들바에 그대로 적용(보수적)",
            "옆 충격 = 위아래 충격 크기",
            "48.5 g 충격을 정적 하중으로 환산",
            "클램프는 핸들바에 완전 고정, 시판 폰 클램프는 강체",
            f"폰 클램프 질량 {ev.PHONE_CLAMP_MASS*1e3:.0f} g",
            f"안전율 {sf}, 진동 증폭 허용 {tmax:.2f}배는 선택값",
        ] + ([f"요청한 노면('{p['road']}')은 측정 근거가 없어 자갈길 값으로 대체(보수적)"] if road_status == "fallback" else [])
          + ([] if p["include_self_inertia"] else ["충격 하중에 거치대 자체 질량 관성 미포함(팀 v7과 동일) — 포함 권장"]),
    }
    return spec
