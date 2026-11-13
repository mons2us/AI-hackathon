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
    arm="straight",       # initial (1st) design arm: straight | L | truss | low | stalk | under
    stalk_base_z=-10.0,   # 'stalk' arm: height where the low arm meets the vertical stalk
    domain_z_min=None,    # extend the design space downward (mm); None = just below the bolt ears
    arm_t=6.0,            # arm thickness in the side view
    bolt_d=4.5,           # M4 clearance holes through the ears (axis x), team v7
    bolt_z=7.0,           # bolt axis height above the ear bottom
    bolt_dy=5.0,          # two bolts at y_sym +- bolt_dy
    mount_hole_d=8.0,     # phone-clamp fixing hole through the pad (assumed interface)
    phone="default",      # key in evidence.PHONES or 'default'
    phone_mass_kg=None,   # user-stated phone mass overrides the table
    road="cobblestone",
    material="PETG",
    objective="min_mass",
    safety_factor=None,   # None -> evidence.FACTORS
    include_self_inertia=False,   # team v7 ignores bracket self-inertia in shock cases
    phone_clamp_t=8.0,    # phone back face above the joint axis (clamp body), assumed
    colour="black",       # print colour -> solar absorptance (sun requirement)
    requirements=(),      # user requirement ids (formproof_input.requirements)
    angle_tilt=(-30.0, 60.0),   # free_angle: tilt range kept clear (deg, + = toward the rider)
    angle_margin=3.0,     # free_angle: clearance around the moving phone (mm)
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
    """Initial-design arm in the xz side view as thick segments (p0, p1).
    Axis-aligned segments are shifted so their faces lie on grid lines; otherwise a 6 mm bar on a 2 mm grid
    voxelises as 4 or 8 mm and the analysed design differs from the CAD (seen as +15-20 % mass on L arms)."""
    segs = _arm_segments_raw(p, ro)
    h, t = p["h"], p["arm_t"]
    on_grid = lambda c: math.floor((c - t / 2) / h + 1e-9) * h + t / 2
    out = []
    for (x0, z0), (x1, z1) in segs:
        if abs(x1 - x0) < 1e-9:
            x0 = x1 = on_grid(x0)
        if abs(z1 - z0) < 1e-9:
            z0 = z1 = on_grid(z0)
        out.append(((x0, z0), (x1, z1)))
    # keep consecutive segments joined: the joint takes x from a vertical leg and z from a horizontal leg
    for k in range(1, len(out)):
        if math.dist(segs[k][0], segs[k - 1][1]) < 1e-9:
            (px, pz), (qx, qz) = out[k - 1][1], out[k][0]
            vert = lambda sg: abs(sg[0][0] - sg[1][0]) < 1e-9
            horz = lambda sg: abs(sg[0][1] - sg[1][1]) < 1e-9
            jx = px if vert(out[k - 1]) else qx if vert(out[k]) else px
            jz = qz if horz(out[k]) else pz if horz(out[k - 1]) else pz
            out[k - 1] = (out[k - 1][0], (jx, jz))
            out[k] = ((jx, jz), out[k][1])
    return out


def _arm_segments_raw(p, ro):
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
    if style == "stalk":                              # under the phone: low arm to a vertical stalk below the joint
        xc = xp + p["pad_len"] / 2
        zb = p["stalk_base_z"]
        n = math.hypot(xc, zb)
        s2 = ((ro - p["arm_t"] / 2) * xc / n, (ro - p["arm_t"] / 2) * zb / n)
        return [(s2, (xc, zb)), ((xc, zb), (xc, zp + p["pad_t"] / 2))]
    if style == "under":                              # down from the ring, forward under the phone's space, up a stalk
        xc = xp + p["pad_len"] / 2
        zb = p["stalk_base_z"]
        a = math.radians(-60.0)
        s0 = ((ro - p["arm_t"] / 2) * math.cos(a), (ro - p["arm_t"] / 2) * math.sin(a))
        return [(s0, (s0[0], zb)), ((s0[0], zb), (xc, zb)), ((xc, zb), (xc, zp + p["pad_t"] / 2))]
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
    yw = _snap(Y_SYM + p["clamp_w"] / 2, Y_SYM, p["h"], outward=1)        # y bounds on grid lines too
    ypost = _snap(Y_SYM + p["post_w"] / 2, Y_SYM, p["h"], outward=1)

    # grid origin on the frame: x lines on multiples of h, y lines from Y_SYM, z lines on multiples of h
    ear_top = _snap(-bore + 2.0, 0.0, h)
    ear_bot = _snap(ear_top - p["ear_len"], 0.0, h)
    x_min = _snap(-(ro + 2.0), 0.0, h, outward=-1)
    z_min = _snap(min(ear_bot, -ro) - 2.0, 0.0, h, outward=-1)
    if p["domain_z_min"] is not None:
        z_min = min(z_min, _snap(p["domain_z_min"], 0.0, h, outward=-1))
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
        dict(name="holder", role="void", shape=[box(x=[_snap(pad_x0 - p["holder_gap"], 0.0, h), None], z=[pad_z1, None])],
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

    dims_pre = ev.PHONES[p["phone"]]["dims"] if p["phone"] in ev.PHONES else ev.PHONE_DEFAULT_DIMS
    # resolved CAD geometry (mm, same snapped values the analysis grid uses) — single source for STEP / drawing
    geometry = dict(
        frame="x 앞(진행 방향), z 위, y 핸들바 축. 핸들바 중심 (x=0, z=0), 대칭면 y=%.1f" % Y_SYM,
        y_sym=Y_SYM, bar_d=p["bar_d"], bore_r=round(bore, 3), ring_ro=round(ro, 3), width=p["clamp_w"],
        slit_half=sx, slit_r=round(ro + 5.4, 3), ear_x=[ex0, ex1], ear_z=[ear_bot, ear_top],
        bolts=dict(d=p["bolt_d"], z=ear_bot + p["bolt_z"], y=[Y_SYM - p["bolt_dy"], Y_SYM + p["bolt_dy"]],
                   x_span=[-ex1 - 2.0, ex1 + 2.0]),
        pad=dict(x=[pad_x0, pad_x1], z=[pad_z0, pad_z1]),
        mount_hole=dict(d=p["mount_hole_d"], x=(pad_x0 + pad_x1) / 2, y=Y_SYM),
        arm=dict(style=p["arm"], t=p["arm_t"], segments=[[list(a), list(b)] for a, b in _arm_segments(p, ro)]),
        clip=dict(holder_x=_snap(pad_x0 - p["holder_gap"], 0.0, h), holder_z=pad_z1, z_above=z_above),
        holes_in_analysis=False,
    )

    if "free_angle" in p["requirements"]:
        e_j = p["phone_clamp_t"] + (dims_pre[2] / 2)
        regions.append(dict(
            name="phone_sweep", role="keepout", minus=["post"],
            shape=[{"phone_sweep": dict(joint=[(post_x0 + post_x1) / 2, Y_SYM, z_top - e_j], H=dims_pre[0], W=dims_pre[1],
                                        D=dims_pre[2], clamp_t=p["phone_clamp_t"], margin=p["angle_margin"],
                                        tilt_lo=p["angle_tilt"][0], tilt_hi=p["angle_tilt"][1], rot_deg=360.0, rot_step=15.0,
                                        tilt_step=4.0)}],
            why="요구 '화면 각도 자유롭게': 폰이 360° 회전·기울기 범위에서 지나가는 공간. 최적화 단계에서 비울 곳"))

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
    dims = ev.PHONES[p["phone"]]["dims"] if p["phone"] in ev.PHONES else ev.PHONE_DEFAULT_DIMS
    geometry["phone"] = dict(name=phone_name, H=dims[0], W=dims[1], D=dims[2], mass_kg=round(m_total, 4),
                             cog=[(post_x0 + post_x1) / 2, z_top], clamp_t=p["phone_clamp_t"],
                             dims_source=phone_src if p["phone"] in ev.PHONES else "assumed")

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
        "geometry": geometry,
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
        "finish": {"colour": p["colour"]},
        "requirements": list(p["requirements"]),
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
    _add_requirement_conditions(spec, p, f_min, road)
    return spec


def _add_requirement_conditions(spec, p, f_min, road):
    """Constraints that user requirements add (formproof_input.requirements); values derived here, judged later."""
    req = set(p["requirements"])
    ph = spec["geometry"]["phone"]
    if "free_angle" in req:
        m = ph["mass_kg"]
        e = (ph["clamp_t"] + ph["D"] / 2) / 1000
        lo, hi = p["angle_tilt"]
        I_p = m * ((ph["H"] / 1000) ** 2 + (ph["D"] / 1000) ** 2) / 12 + m * e ** 2      # portrait pitch about joint
        k_req = (2 * math.pi * f_min) ** 2 * I_p
        torque = m * road["peak_g"] * 9.81 * e * math.sin(math.radians(max(abs(lo), abs(hi))))
        spec["constraints"] += [
            {"id": "pose_clearance", "quantity": "phone_clearance_mm", "op": ">=", "value": p["angle_margin"],
             "poses": {"rotate_deg": 360, "tilt_deg": [lo, hi]}, "keep_out_region": "phone_sweep",
             "requirement": "free_angle", "source": ["assumed:target_range"]},
            {"id": "joint_stiffness", "quantity": "joint_rot_stiffness_Nm_per_rad", "op": ">=", "value": round(k_req, 1),
             "derivation": f"(2π·{f_min})² × I_joint, I_joint = m(H²+D²)/12 + m·e² = {I_p:.2e} kg·m² (세로, 관절이 폰 뒤 {e*1000:.0f} mm)",
             "requirement": "free_angle", "source": ["sdof"]},
            {"id": "joint_hold", "quantity": "joint_hold_torque_Nm", "op": ">=", "value": round(torque, 2),
             "derivation": f"m·{road['peak_g']} g·e·sin{max(abs(lo), abs(hi)):.0f}°; 관절축이 폰 무게중심을 지나면 0",
             "requirement": "free_angle", "source": [road["source"]]},
        ]
        spec["assumptions"].append(f"각도 자유: 360° 회전 + 기울기 {lo:+.0f}~{hi:+.0f}°, 간격 {p['angle_margin']:g} mm (목표 선택값)")
    if "sun_heat" in req:
        mat = ev.MATERIALS[p["material"]]
        spec["constraints"].append(
            {"id": "sun_heat", "quantity": "parked_surface_temp_c", "op": "<=",
             "value": f"HDT(σ_1g) − {ev.SUN['margin_k']:.0f}", "hdt_table": mat["hdt"], "colour": p["colour"],
             "derivation": "햇빛 아래 주차 표면온도(에너지 평형) ≤ 정하중(폰 무게) 응력에서의 열변형온도 − 여유",
             "requirement": "sun_heat", "source": [mat["source"], "energy_balance", ev.ABSORPTANCE_SOURCE]})
        spec["evidence"].update({k: ev.SOURCES[k] for k in ("energy_balance", ev.ABSORPTANCE_SOURCE, "prusa_asa_blog")})
