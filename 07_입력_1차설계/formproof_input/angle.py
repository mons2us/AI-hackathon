"""Requirement '화면 각도를 최대한 자유롭게' -> pose clearance + joint conditions.

Phone pose = in-plane rotation phi (0 = portrait, long side along x / riding direction) then tilt theta
about a y-axis through the joint (theta > 0: front edge up, screen turns toward the rider).
Checks: (1) the phone's back face clears the handlebar and the mount for every pose in the target range,
(2) the joint height that range needs and what that height costs in vibration / stress (re-analysed),
(3) joint stiffness so the phone's own rocking mode stays above the vibration limit,
(4) joint holding torque under the road shock."""
import math
import numpy as np
from scipy.spatial import cKDTree

TARGET = dict(tilt_deg=60.0, rotate_deg=360.0, clearance_mm=3.0)     # '최대한 자유롭게' (selected values)


def _rot(phi, theta):
    p, t = math.radians(phi), math.radians(theta)
    Rz = np.array([[math.cos(p), -math.sin(p), 0], [math.sin(p), math.cos(p), 0], [0, 0, 1]])
    Ry = np.array([[math.cos(t), 0, -math.sin(t)], [0, 1, 0], [math.sin(t), 0, math.cos(t)]])   # front up
    return Ry @ Rz


class PoseChecker:
    def __init__(self, P, dens, spec, lift=0.0, step=2.0):
        g = spec["geometry"]
        ph = g["phone"]
        self.g, self.ph = g, ph
        self.e = ph["clamp_t"] + ph["D"] / 2                       # joint axis -> phone CoG
        cx, cz = ph["cog"]
        self.J = np.array([cx, g["y_sym"], cz + lift - self.e])
        # mount occupancy (full model, phone-clamp stand-in excluded) as a point cloud
        on = P.solid | (P.design & (dens > 0.5))
        c = P.centres[on]
        mir = c.copy()
        mir[:, 1] = 2 * g["y_sym"] - mir[:, 1]
        self.tree = cKDTree(np.vstack([c, mir]))
        self.vox_r = P.h / 2 * math.sqrt(3)
        u = np.arange(-ph["H"] / 2, ph["H"] / 2 + 1e-9, step)
        v = np.arange(-ph["W"] / 2, ph["W"] / 2 + 1e-9, step)
        U, V = np.meshgrid(u, v)
        self.back = np.c_[U.ravel(), V.ravel(), np.full(U.size, ph["clamp_t"])]     # phone back face, joint frame

    def clearance(self, phi, theta):
        pts = self.back @ _rot(phi, theta).T + self.J
        x, y, z = pts.T
        r = np.hypot(x, z)
        in_clamp = np.abs(y - self.g["y_sym"]) <= self.g["width"] / 2
        bar = np.where(in_clamp, r - self.g["ring_ro"], r - self.g["bar_d"] / 2)      # bar runs the full width
        d_mount, _ = self.tree.query(pts)
        return float(min(bar.min(), (d_mount - self.vox_r).min()))

    def tilt_range(self, phi, cl, lo=-90, hi=90):
        up = 0
        for t in range(0, hi + 1):
            if self.clearance(phi, t) < cl:
                break
            up = t
        down = 0
        for t in range(0, lo - 1, -1):
            if self.clearance(phi, t) < cl:
                break
            down = t
        return down, up


def joint_requirements(spec, f_min, a_g, tilt_deg):
    ph = spec["geometry"]["phone"]
    m = ph["mass_kg"]
    e = (ph["clamp_t"] + ph["D"] / 2) / 1000
    out = {}
    for name, L in (("portrait", ph["H"]), ("landscape", ph["W"])):
        I_cg = m * ((L / 1000) ** 2 + (ph["D"] / 1000) ** 2) / 12
        for axis, off in (("joint_below_phone", e), ("axis_through_cog", 0.0)):
            I = I_cg + m * off ** 2
            out[f"{name}/{axis}"] = dict(I_kgm2=round(I, 7), k_req_Nm_per_rad=round((2 * math.pi * f_min) ** 2 * I, 1),
                                         hold_torque_Nm=round(m * a_g * 9.81 * off * math.sin(math.radians(tilt_deg)), 2))
    return out


def check(P, dens, spec, fem_eval=None, target=None, lifts=range(0, 81, 4)):
    """fem_eval(spec_params_override) -> evaluate() dict, used to re-analyse the mount at the needed joint height."""
    tg = dict(TARGET, **(target or {}))
    pc = PoseChecker(P, dens, spec)
    cl = tg["clearance_mm"]
    now = {"portrait": pc.tilt_range(0, cl), "landscape": pc.tilt_range(90, cl)}
    rot_ok_now = all(pc.clearance(phi, 0) >= cl for phi in range(0, 360, 15))
    need = None
    for lift in lifts:
        q = PoseChecker(P, dens, spec, lift=lift)
        ok_tilt = all(q.tilt_range(phi, cl, lo=0, hi=int(tg["tilt_deg"]))[1] >= tg["tilt_deg"] for phi in (0, 90))
        ok_rot = all(q.clearance(phi, t) >= cl for phi in range(0, 360, 15) for t in (0, tg["tilt_deg"] / 2, tg["tilt_deg"]))
        if ok_tilt and ok_rot:
            need = lift
            break
    cons = {c["id"]: c for c in spec["constraints"]}
    shock = next(c for c in spec["load_cases"] if c["name"] == "shock_vertical")
    joint = joint_requirements(spec, cons["f1"]["value"], shock["accel_g"], tg["tilt_deg"])
    trade = []
    if fem_eval is not None and need is not None:
        for lift in sorted({0, need // 2 // 2 * 2, need}):
            r = fem_eval(lift)
            trade.append(dict(lift_mm=lift, f1_hz=r["f1_hz"], stress_mpa=r["checks"]["stress"]["value"],
                              f1_ok=r["checks"]["f1"]["pass"], stress_ok=r["checks"]["stress"]["pass"]))
    ok = (now["portrait"][1] >= tg["tilt_deg"] and now["landscape"][1] >= tg["tilt_deg"] and rot_ok_now)
    return dict(requirement="free_angle", pass_=ok, target=tg,
                tilt_now={k: dict(down_deg=v[0], up_deg=v[1]) for k, v in now.items()}, rotate_360_now=rot_ok_now,
                joint_lift_needed_mm=need, joint=joint, tradeoff=trade,
                assumptions=["목표: 라이더 쪽 0–60° 기울기 + 360° 회전, 간격 3 mm (선택값)",
                             f"관절축은 폰 뒷면 아래 {spec['geometry']['phone']['clamp_t']:g} mm (클램프 두께 가정)",
                             "간섭 대상: 핸들바(클램프 폭 밖은 핸들 Ø, 안은 링 외경)와 거치대 본체. 스템·브레이크 레버는 미포함",
                             "관절 강성 요구 = 폰의 관절 회전 모드 ≥ 진동 기준, 폰+클램프를 강체 판으로 근사"])
