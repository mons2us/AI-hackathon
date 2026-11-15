"""Bicycle phone mount: template parameters -> design spec.

Frame (same as the team's opt3d.py): handlebar axis = y axis through (x=0, z=0),
x = forward (riding direction), z = up, y = across; symmetry plane y = Y_SYM, half model
on y >= Y_SYM. All template parameters are physical sizes in mm; the generator snaps
element-region bounds to grid lines so a bound never sits on an element centre.

DEFAULT reproduces opt3d.py (team v7 3D problem) element-for-element (tests/test_reproduce_opt3d.py);
the payload follows team v3 (rigid body with rotary inertia, opt3d_am.py RIGID=1 / verify_sys.py).
"""
import copy
import math
from .. import evidence as ev
from .. import look as LK

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
    arm="straight",       # 1st-design arm: straight | L | truss | low | stalk | under | riser | dogleg | step | vee
    knee_frac=0.4,        # 'dogleg' arm: knee position as a fraction of the reach
    stalk_base_z=-10.0,   # 'stalk' arm: height where the low arm meets the vertical stalk
    domain_z_min=None,    # extend the design space downward (mm); None = just below the bolt ears
    arm_t=6.0,            # arm thickness in the side view
    bolt_d=4.5,           # M4 clearance holes through the ears (axis x), team v7
    bolt_z=7.0,           # bolt axis height above the ear bottom
    bolt_dy=5.0,          # two bolts at y_sym +- bolt_dy
    mount_hole_d=8.0,     # phone-clamp fixing hole through the pad (assumed interface)
    phone="default",      # key in evidence.PHONES or 'default'
    phone_mass_kg=None,   # user-stated phone mass overrides the table
    payload_model="rigid",  # 'rigid' (team v3: phone+case+holder rigid body with rotary inertia) | 'point' (team v7)
    road="cobblestone",
    material="PETG",
    objective="min_mass",
    safety_factor=None,   # None -> evidence.FACTORS
    include_self_inertia=False,   # team v7 ignores bracket self-inertia in shock cases
    holder_plate_t=4.0, holder_jaw_t=4.0, holder_jaw_len=36.0, holder_lip=3.0, holder_lip_t=2.5,   # phone holder (CAD)
    phone_clamp_t=8.0,    # phone back face above the joint axis (clamp body), assumed
    colour="black",       # print colour -> solar absorptance (sun requirement)
    requirements=(),      # user requirement ids (formproof_input.requirements)
    angle_tilt=(-30.0, 60.0),   # free_angle: tilt range kept clear (deg, + = toward the rider)
    angle_margin=3.0,     # free_angle: clearance around the moving phone (mm)
    look=None,            # look template: dict(clamp, arm, section, joint, holder, tilt_deg) -> formproof_input.look
    look_arm_w=None, look_arm_t=None,   # look arm member size (None: look.ARM_W / ARM_T)
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


def _look_arm_prims(p, paths, yw_of):
    """Look arm (side paths of formproof_input.look) as thick segments; section -> width across the bar.
    rect: full section; trib / ibeam: flange segment(s) + narrow web; round: a tube (3D distance);
    taper: thickness and width shrink along the main path."""
    L = p["look"]
    sec = L.get("section") or LK.ARM_DEFAULT_SECTION[L["arm"]]
    w = p["look_arm_w"] or LK.ARM_W
    t = p["look_arm_t"] or LK.ARM_T
    prims, segs = [], []
    for k, pth in enumerate(paths):
        ww, tt = (w, t) if k == 0 else (w * 0.7, t * 0.75)
        n = len(pth) - 1
        for i in range(n):
            a, b = pth[i], pth[i + 1]
            if sec == "taper":
                f = (i + 0.5) / n
                ww_, tt_ = w + (0.65 * w - w) * f, t + (0.75 * t - t) * f
            else:
                ww_, tt_ = ww, tt
            P0, P1 = [round(a[0], 3), round(a[1], 3)], [round(b[0], 3), round(b[1], 3)]
            segs.append([P0, P1])
            if sec == "round":
                prims.append({"seg": dict(plane="xz", p0=P0, p1=P1, t=round(ww_, 3), round_y0=Y_SYM)})
            elif sec in ("trib", "ibeam"):
                # rib section as in mount_modules._section: full-width flange(s) + narrow web (side plane offsets
                # along the member normal n = (-dz, dx), the CAD's local +Y) -> same area as the CAD section
                f = min(2.6, tt_ / 3) if sec == "trib" else min(2.4, tt_ / 4)
                web = min(3.0, ww_ / 3)
                dx, dz = b[0] - a[0], b[1] - a[1]
                ln = math.hypot(dx, dz)
                n = (-dz / ln, dx / ln)
                offs = [tt_ / 2 - f / 2] + ([-(tt_ / 2 - f / 2)] if sec == "ibeam" else [])
                for o in offs:
                    prims.append({"seg": dict(plane="xz", p0=[round(P0[0] + o * n[0], 3), round(P0[1] + o * n[1], 3)],
                                              p1=[round(P1[0] + o * n[0], 3), round(P1[1] + o * n[1], 3)],
                                              t=round(f, 3), y=[None, yw_of(ww_)])})
                prims.append({"seg": dict(plane="xz", p0=P0, p1=P1, t=round(tt_, 3), y=[None, yw_of(web)])})
            else:
                prims.append({"seg": dict(plane="xz", p0=P0, p1=P1, t=round(tt_, 3), y=[None, yw_of(ww_)])})
    return prims, segs, sec


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
    tgt_pad = (xp + 2.0, zp + p["pad_t"] / 2)
    if style == "riser":                              # bar-top clamp: short vertical stub, pad centred over the bar
        return [(start, (0.0, zp + p["pad_t"] / 2))]
    if style == "dogleg":                             # gooseneck: rises diagonally to pad height, then runs forward
        knee = (xp * p["knee_frac"], zp + p["pad_t"] / 2)
        return [(start, knee), (knee, tgt_pad)]
    if style == "step":                               # out-front: forward at bar height from the ring front, then up to the pad
        s0 = (ro - p["arm_t"] / 2, 0.0)
        foot = (xp + p["pad_len"] / 2, 0.0)
        return [(s0, foot), (foot, (foot[0], zp + p["pad_t"] / 2))]
    if style == "vee":                                # two arms (ring top and ring front) meeting at the pad
        return [(start, tgt_pad), ((ro - p["arm_t"] / 2, 0.0), tgt_pad)]
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
    L = p["look"]
    if L:                                           # look template: clamp sizes from the clamp module, arm from its path
        L = dict(L)
        C = LK.CLAMP_SPEC[L["clamp"]]
        L.setdefault("section", LK.ARM_DEFAULT_SECTION[L["arm"]])
        L.setdefault("joint", LK.HOLDER_SPEC[L["holder"]]["joint"])
        L["section"] = L["section"] or LK.ARM_DEFAULT_SECTION[L["arm"]]
        L["joint"] = L["joint"] or LK.HOLDER_SPEC[L["holder"]]["joint"]
        p["look"] = L
        p["clamp_w"], p["ring_t"] = C["width"], C["ring_t"]
        p["arm"] = "look:" + L["arm"]
        p["post_x"] = (p["pad_len"] / 2 - p["post_w"] / 2, p["pad_len"] / 2 + p["post_w"] / 2)
        p["post_h"] = max(LK.JOINT_LEN[L["joint"]], 2 * h)
        p["payload_model"] = "rigid"
    R = p["bar_d"] / 2
    bore = R + p["bore_gap"]
    ro = bore + p["ring_t"]
    if L:
        look_paths, tip, _, _ = LK.arm_paths(L["arm"], ro, ro)
        p["pad_x0"] = round(tip[0] - p["pad_len"] / 2, 3)
        p["pad_z0"] = round(tip[1] - p["pad_t"] / 2, 3)
        # phone tilt toward the rider: the given one, else the largest that clears the ring and the arm (look.fit_tilt)
        dims_l = ev.PHONES[p["phone"]]["dims"] if p["phone"] in ev.PHONES else ev.PHONE_DEFAULT_DIMS
        base_l = (_snap(p["pad_x0"], 0.0, h) + _snap(p["pad_x0"] + p["pad_len"], 0.0, h)) / 2, _snap(p["pad_z0"] + p["pad_t"], 0.0, h)
        dep = LK.HOLDER_SPEC[L["holder"]]["depth"]
        if L.get("tilt_deg") is None:
            L["tilt_deg"], c_ring, c_arm = LK.fit_tilt(look_paths, ro, base_l, LK.JOINT_LEN[L["joint"]], dep, dims_l)
        else:
            c_ring, c_arm = LK.clearance(look_paths, ro, base_l, LK.JOINT_LEN[L["joint"]], dep, L["tilt_deg"], dims_l)
        L["clearance_mm"] = dict(ring=round(c_ring, 1), arm=round(c_arm, 1),
                                 ok=bool(c_ring >= LK.CLEAR_RING and c_arm >= LK.CLEAR_ARM))
    has_ears = not L or LK.CLAMP_SPEC[L["clamp"]]["ears"]
    saddle = L and LK.CLAMP_SPEC[L["clamp"]]["saddle"]
    yw = _snap(Y_SYM + p["clamp_w"] / 2, Y_SYM, p["h"], outward=1)        # y bounds on grid lines too
    ypost = _snap(Y_SYM + p["post_w"] / 2, Y_SYM, p["h"], outward=1)

    # grid origin on the frame: x lines on multiples of h, y lines from Y_SYM, z lines on multiples of h
    ear_top = _snap(-bore + 2.0, 0.0, h)
    ear_bot = _snap(ear_top - p["ear_len"], 0.0, h)
    x_min = _snap(-(ro + 2.0), 0.0, h, outward=-1)
    z_min = _snap(min(ear_bot if has_ears else 0.0, -ro) - 2.0, 0.0, h, outward=-1)
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
    x_max = max(pad_x1, _snap(ro + 2.0, 0.0, h, outward=1))      # pad over the bar (riser): keep the whole ring in the grid
    ny = int(round(p["design_w"] / 2 / h))
    nx = int(round((x_max - x_min) / h))
    nz = int(round((z_top - z_min) / h))
    sx = _snap(p["slit_w"] / 2, 0.0, h)
    ex0, ex1 = (_snap(v, 0.0, h) for v in p["ear_x"])
    cyl = lambda **kw: {"cyl": dict(axis="y", center=[0.0, 0.0], **kw)}
    box = lambda **kw: {"box": kw}

    regions = [
        dict(name="bore", role="void", shape=[cyl(r_max=bore)], why="핸들바가 지나가는 구멍"),
        *([dict(name="slit", role="void", shape=[box(x=[-sx, sx], z=[None, 0.0]), cyl(r_max=ro + 5.4)],
                why="클램프 조임용 절개")] if has_ears else []),
        *([dict(name="strap_band", role="void", shape=[cyl(r_min=bore, r_max=ro + 2.5, z=[None, 0.0])],
                why="고무 띠가 핸들 아래로 감기는 자리")] if saddle else []),
        dict(name="post", role="rigid", stiffness_scale=20.0, mass_scale=0.0,
             shape=[box(x=[post_x0, post_x1], z=[pad_z1, None], y=[None, ypost])],
             why="시판 폰 클램프(강체 가정, 질량은 point_masses에 포함)"),
        dict(name="holder", role="void", shape=[box(x=[_snap(pad_x0 - p["holder_gap"], 0.0, h), None], z=[pad_z1, None])],
             minus=["post"], why="폰이 놓이는 공간"),
        dict(name="above", role="void", shape=[box(z=[z_above, None])], minus=["post"],
             why="폰 뒤 공간은 받침판 위 일정 높이까지만 허용"),
        dict(name="contact", role="solid", shape=[cyl(r_min=bore, r_max=ro, y=[None, yw], **({"z": [0.0, None]} if saddle else {}))],
             why="핸들 위 반원 받침(지킬 곳)" if saddle else "핸들바 클램프 링(지킬 곳)"),
        *([dict(name="ears", role="solid",
                shape={"union": [[box(x=[ex0, ex1], z=[ear_bot, ear_top], y=[None, yw])],
                                 [box(x=[-ex1, -ex0], z=[ear_bot, ear_top], y=[None, yw])]]},
                why="M4 볼트 귀(지킬 곳)")] if has_ears else []),
        dict(name="pad", role="solid", shape=[box(x=[pad_x0, pad_x1], z=[pad_z0, pad_z1], y=[None, yw])],
             why="폰 클램프 받침판(지킬 곳)"),
    ]
    if L:
        arm, arm_segs, _ = _look_arm_prims(p, look_paths, lambda ww: _snap(Y_SYM + ww / 2, Y_SYM, h, outward=1))
    else:
        arm = [{"seg": dict(plane="xz", p0=list(a), p1=list(b), t=p["arm_t"], y=[None, yw])}
               for a, b in _arm_segments(p, ro)]
        arm_segs = [[list(a), list(b)] for a, b in _arm_segments(p, ro)]

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
        arm=dict(style=p["arm"], t=(p["look_arm_t"] or LK.ARM_T) if L else p["arm_t"], segments=arm_segs,
                 **(dict(paths=[[list(map(float, q)) for q in pth] for pth in look_paths]) if L else {})),
        clamp=L["clamp"] if L else "bolt",
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
    known = p["phone"] in ev.PHONES
    dims = ev.PHONES[p["phone"]]["dims"] if known else ev.PHONE_DEFAULT_DIMS
    PL = ev.PAYLOAD
    post_cx = (post_x0 + post_x1) / 2
    if p["payload_model"] == "point":                          # team v7: phone + 50 g clamp lumped on the post top
        if known:
            ph = ev.PHONES[p["phone"]]
            m_phone, phone_src, phone_name = ph["mass"], ph["source"], ph["name"]
        else:
            m_phone, phone_src, phone_name = ev.PHONE_DEFAULT_MASS, "team_v7", "기종 미지정(200 g 가정)"
        if p["phone_mass_kg"]:
            m_phone, phone_src, phone_name = p["phone_mass_kg"], "user", "사용자 입력 폰"
        m_phone_case, m_total = m_phone, m_phone + ev.PHONE_CLAMP_MASS
        pay_note = f"{phone_name} {m_phone*1e3:.0f} g + 폰 클램프 {ev.PHONE_CLAMP_MASS*1e3:.0f} g, 클램프 상단에 집중"
        pay_src = [phone_src, "assumed:clamp_50g"]
    else:                                                      # team v3: rigid payload with rotary inertia
        if p["phone_mass_kg"]:
            m_phone, phone_src, phone_name = p["phone_mass_kg"], "user", "사용자 입력 폰"
            m_phone_case = m_phone + PL["case_kg"]
        elif known:
            ph = ev.PHONES[p["phone"]]
            m_phone, phone_src, phone_name = ph["mass"], ph["source"], ph["name"]
            m_phone_case = m_phone + PL["case_kg"]
        else:
            m_phone, phone_src, phone_name = None, PL["source"], "기종 미지정(설계 범위 최대)"
            m_phone_case = PL["phone_case_max_kg"]
        m_total = m_phone_case + PL["holder_kg"]
        if known or p["phone_mass_kg"]:
            c = PL["case_margin_mm"]
            pbox = (dims[0] + 2 * c, dims[1] + 2 * c, dims[2] + c + p["holder_plate_t"])
        else:
            pbox = PL["box_default_mm"]
        pbox = tuple(round(v, 2) for v in pbox)
        pay_note = (f"{phone_name} " + (f"{m_phone*1e3:.0f} g + 케이스 {PL['case_kg']*1e3:.0f} g" if m_phone is not None
                    else f"+ 케이스 {PL['phone_case_max_kg']*1e3:.0f} g") + f" + 폰 홀더 {PL['holder_kg']*1e3:.0f} g = {m_total*1e3:.0f} g, "
                    f"강체(상자 {pbox[0]:g} × {pbox[1]:g} × {pbox[2]:g} mm, 회전 관성 포함)")
        pay_src = [phone_src, PL["source"]]
    look_pl = None
    if L:                                                      # holder + joint from the CAD (look_payload.json)
        entry = LK.payload_entry(L["holder"], L["joint"], L["tilt_deg"], dims)
        base = [(pad_x0 + pad_x1) / 2, Y_SYM, pad_z1]
        look_pl = LK.combine_payload(entry, base, m_phone_case)
        m_total = look_pl["mass_kg"]
        pay_note = (f"{phone_name} " + (f"{m_phone*1e3:.0f} g + 케이스 {PL['case_kg']*1e3:.0f} g" if m_phone is not None
                    else f"+ 케이스 {PL['phone_case_max_kg']*1e3:.0f} g") +
                    f" + {LK.HOLDER_SPEC[L['holder']]['name']}·{LK.JOINTS[L['joint']]} {look_pl['holder_kg']*1e3:.0f} g(CAD) = {m_total*1e3:.0f} g, "
                    f"강체(CAD에서 구한 무게중심·회전 관성, 기울기 {L['tilt_deg']:g}°)")
        pay_src = [phone_src, PL["source"], "cad:look"]
        th = math.radians(L["tilt_deg"])
        org = [base[0] - math.sin(th) * LK.HOLDER_SPEC[L["holder"]]["depth"], Y_SYM,
               base[2] + entry["joint_len"] + math.cos(th) * LK.HOLDER_SPEC[L["holder"]]["depth"]]
        geometry["look"] = dict(L, arm_w=p["look_arm_w"] or LK.ARM_W, arm_t=p["look_arm_t"] or LK.ARM_T,
                                joint_len=entry["joint_len"], base=base,
                                phone_center=[round(org[0] - math.sin(th) * dims[2] / 2, 3), Y_SYM,
                                              round(org[2] + math.cos(th) * dims[2] / 2, 3)])
    geometry["phone"] = dict(name=phone_name, H=dims[0], W=dims[1], D=dims[2], mass_kg=round(m_phone_case, 4),
                             cog=[post_cx, z_top], clamp_t=p["phone_clamp_t"],
                             dims_source=phone_src if known else "assumed")

    # phone holder (the part that grips the phone) — part of the product: stem on the pad, back plate, cross bar, two jaws.
    # Analysis keeps it as the rigid 'post' stand-in with the 50 g clamp mass (team v7); CAD / drawing carry the real shape.
    zb = z_top - dims[2] / 2                                   # phone back face
    geometry["holder"] = dict(
        stem=dict(x=[post_x0, post_x1], w=p["post_w"], z=[pad_z1, round(zb - p["holder_plate_t"], 3)]),
        plate=dict(x=[round((post_x0 + post_x1) / 2 - 0.34 * dims[0], 2), round((post_x0 + post_x1) / 2 + 0.34 * dims[0], 2)],
                   w=round(0.6 * dims[1], 2), z=[round(zb - p["holder_plate_t"], 3), round(zb, 3)]),
        bar=dict(x=[(post_x0 + post_x1) / 2 - p["holder_jaw_len"] / 2, (post_x0 + post_x1) / 2 + p["holder_jaw_len"] / 2],
                 w=round(dims[1] + 2 * p["holder_jaw_t"], 2), z=[round(zb - p["holder_plate_t"], 3), round(zb, 3)]),
        jaw=dict(t=p["holder_jaw_t"], z=[round(zb - p["holder_plate_t"], 3), round(zb + dims[2] + p["holder_lip_t"], 3)],
                 lip=p["holder_lip"], lip_t=p["holder_lip_t"], y_in=round(dims[1] / 2, 2)),
        phone_back_z=round(zb, 3), note="폰을 잡는 부분(받침 기둥·등판·가로대·양쪽 턱). 해석에서는 강체 기둥 + 탑재 하중의 홀더 몫으로 반영")

    payload = {"name": "phone_clamp", "mass_kg": round(m_total, 4),
               "nodes": [box(x=[post_x0, post_x1], y=[None, ypost], z=[z_top, None])],
               "source": pay_src, "note": pay_note}
    if look_pl:
        payload.update(model="rigid_body", cg=[round(v, 3) for v in look_pl["cg"]], box_mm=list(pbox),
                       inertia_kg_mm2=[[round(v, 3) for v in r] for r in look_pl["inertia"]],
                       parts=dict(phone_case_kg=round(m_phone_case, 4), holder_kg=round(look_pl["holder_kg"], 4),
                                  holder_parts_g=look_pl["parts"]),
                       attach="관절 기둥 윗면 절점에 최소제곱 강체 맞춤으로 연결(팀 verify_sys.py와 같은 방식)")
    elif p["payload_model"] != "point":
        cg = [post_cx, Y_SYM, round(z_top - PL["cg_below_post_top_mm"], 3)]
        Ix = m_total * (pbox[1] ** 2 + pbox[2] ** 2) / 12
        Iy = m_total * (pbox[0] ** 2 + pbox[2] ** 2) / 12
        Iz = m_total * (pbox[0] ** 2 + pbox[1] ** 2) / 12
        payload.update(model="rigid_body", cg=cg, box_mm=list(pbox), inertia_kg_mm2=[round(Ix, 3), round(Iy, 3), round(Iz, 3)],
                       parts=dict(phone_case_kg=round(m_phone_case, 4), holder_kg=PL["holder_kg"]),
                       attach="기둥 윗면 절점에 최소제곱 강체 맞춤으로 연결(팀 verify_sys.py와 같은 방식)")
    geometry["payload"] = dict(mass_kg=round(m_total, 4), cg=payload.get("cg", [post_cx, Y_SYM, z_top]),
                               box_mm=payload.get("box_mm"), model=p["payload_model"])

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
                      "nodes": [cyl(r_max=bore + 0.6, **({"z": [0.0, None]} if saddle else {}))],
                      **({"clamp": L["clamp"], "clamp_note": LK.CLAMP_SPEC[L["clamp"]]["support"]} if L else {}),
                      "assumption": "클램프 내면이 핸들바에 완전 고정(미끄럼·회전 없음)"}],
        "point_masses": [payload],
        "load_cases": [
            {"name": "road_vibration", "type": "modal", "modes_per_case": 2 if p["payload_model"] == "point" else 8,
             "excitation_hz": [road["f_lo"], road["f_hi"]], "source": road["source"],
             **({} if p["payload_model"] == "point" else
                dict(excitation_dirs=["z", "x"], damping_ratio=PL["damping_ratio"],
                     response="phone_clamp CG motion / handlebar motion"))},
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
            *([] if p["payload_model"] == "point" else [
                {"id": "transmissibility", "quantity": "transmissibility_band_max", "op": "<=", "value": round(tmax, 3),
                 "load_case": "road_vibration", "dirs": ["z", "x"],
                 "derivation": f"노면 {road['f_lo']}–{road['f_hi']} Hz에서 폰 무게중심 흔들림 / 핸들바 흔들림 최대값 ≤ {tmax:.2f}배 "
                               f"(위아래·앞뒤, 감쇠비 {PL['damping_ratio']:.0%}, 폰 강체 관성 포함)",
                 "source": [PL["source"], road["source"]]}]),
            {"id": "f1", "quantity": "natural_frequency_hz", "op": ">=", "value": round(f_min, 1),
             "load_case": "road_vibration",
             **({} if p["payload_model"] == "point" else {"reference": True}),
             "derivation": f"T_max={tmax:.3f} -> f1 >= {road['f_hi']} / sqrt(1-1/T_max)"
                           + ("" if p["payload_model"] == "point" else " (1자유도 근사 참고선, 판정은 transmissibility)"),
             "source": ["sdof", road["source"]]},
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
        "evidence": {k: ev.SOURCES[k] for k in sorted({mat["source"], road["source"], "sdof", "team_v7", phone_src, *pay_src}
                                                     & set(ev.SOURCES))},
        "assumptions": [
            "노면 진동은 바퀴 축 측정값을 핸들바에 그대로 적용(보수적)",
            "옆 충격 = 위아래 충격 크기",
            "48.5 g 충격을 정적 하중으로 환산",
            "클램프는 핸들바에 완전 고정, 시판 폰 클램프는 강체" if p["payload_model"] == "point"
            else "클램프는 핸들바에 완전 고정, 폰·케이스·폰 홀더는 한 덩어리 강체(해석 격자에서 홀더는 강체 기둥으로 대신)",
            f"폰 클램프 질량 {ev.PHONE_CLAMP_MASS*1e3:.0f} g" if p["payload_model"] == "point"
            else f"탑재 하중 {m_total*1e3:.0f} g: 케이스 {PL['case_kg']*1e3:.0f} g·폰 홀더 {PL['holder_kg']*1e3:.0f} g 여유(팀 v3), "
                 f"무게중심 기둥 윗면 − {PL['cg_below_post_top_mm']:g} mm, 감쇠비 {PL['damping_ratio']:.0%}",
            f"안전율 {sf}, 진동 증폭 허용 {tmax:.2f}배는 선택값",
        ] + ([f"요청한 노면('{p['road']}')은 측정 근거가 없어 자갈길 값으로 대체(보수적)"] if road_status == "fallback" else [])
          + ([f"외형 템플릿: {LK.CLAMP_SPEC[L['clamp']]['name']} · {LK.ARMS[L['arm']]} · {LK.SECTIONS[L['section']]} 단면 · "
               f"{LK.JOINTS[L['joint']]} · {LK.HOLDER_SPEC[L['holder']]['name']}. 지지: {LK.CLAMP_SPEC[L['clamp']]['support']}",
               "팔 단면(T·I자 리브)은 격자 2 mm로 근사: 날개 + 폭 4 mm 복부(CAD 단면적과 ±5 %)",
               "관절(볼·원판)은 강체 기둥으로 보고 조임 강성은 무시(실제보다 단단하게 계산됨)"]
             + (["회전 잠금 전용 케이스 무게는 일반 케이스 여유와 별도로 더함(보수적)"] if L["holder"] == "twist" else [])
             if L else [])
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
