"""User requirement library: words -> physics conditions -> spec changes -> checks.

Each entry says which phrases trigger it, what it means physically, what it adds to the spec
(load cases / constraints / keep-out regions / finish), how the 1st design is adapted to it,
and which check judges the 1st design. Unknown requirements are returned as questions."""
import math
import re

import numpy as np

from . import angle, thermal
from .compile import Problem
from .fem import evaluate, connected
from .geometry import eval_shape
from .templates.bike_mount import build_spec

LIBRARY = {
    "sun_heat": dict(
        name="여름 땡볕에서 변형 없음",
        triggers=r"땡볕|햇빛|햇볕|직사광선|여름|뙤약볕|더위|뜨거운\s*날|고온",
        physics="주차 중 햇빛에 달궈진 부품 온도 ≤ 재료 열변형온도(자기 정하중 응력에서) − 여유",
        adds="마감 색(흡수율), 열 판정. 불충족 시 색 → 재료 순으로 대안 제시",
    ),
    "free_angle": dict(
        name="화면 각도 최대한 자유롭게",
        triggers=r"각도|기울|틸트|돌려|회전|가로\s*(로|모드)?|세로\s*(로|모드)?|자유롭게\s*(조절|돌)",
        physics="폰이 360° 회전 + 기울기 범위에서 핸들·거치대와 부딪히지 않음, 관절이 진동 기준 이상 강성·충격 유지 토크 보유",
        adds="폰이 지나가는 공간을 '비울 곳'으로 추가, 관절 위치(높이·도달 거리) 선택, 관절 강성·유지 토크 요구",
    ),
}


def detect(text):
    return [k for k, v in LIBRARY.items() if re.search(v["triggers"], text or "")]


# ---------------------------------------------------------------- free_angle: adapt the 1st design
def _bar_clear(spec, lift, margin):
    """Do all poses clear the handlebar (mount body ignored) with the joint raised by `lift`?"""
    P = Problem(spec)
    pc = angle.PoseChecker(P, np.zeros(len(P.label)), spec, lift=lift)
    from scipy.spatial import cKDTree
    pc.tree = cKDTree(np.array([[1e9, 1e9, 1e9]]))
    lo, hi = spec_tilt(spec)
    return all(pc.clearance(phi, t) >= margin for phi in range(0, 360, 15) for t in np.arange(lo, hi + 1e-9, 4.0))


def spec_tilt(spec):
    return spec["template"]["params"]["angle_tilt"]


def _arm_in_sweep(P, spec):
    arm = eval_shape({"union": [[s] for s in spec["initial_design"]["shape"]]}, P.centres)
    return int((arm & P.region_masks["phone_sweep"]).sum())


def adapt_free_angle(params, tid, reach_steps=(0.0, 20.0, 40.0), lift_max=60.0, tilt=None):
    """Choose joint lift / reach and an arm that stays out of the phone's swept space; keep the stiffest."""
    p0 = dict(params)
    p0["requirements"] = sorted(set(p0.get("requirements", [])) | {"free_angle"})
    p0.setdefault("domain_z_min", -110.0)         # room for an arm that passes under the phone's swept space
    if tilt is not None:
        p0["angle_tilt"] = tilt
    cands = []
    for dr in reach_steps:
        p = dict(p0, pad_x0=p0.get("pad_x0", 80.0) + dr)
        base_post = p.get("post_h", 22.0)
        lift = None
        for L in np.arange(0.0, lift_max + 1e-9, 4.0):
            if _bar_clear(build_spec(dict(p, post_h=base_post + L), tid), 0.0, p.get("angle_margin", 3.0)):
                lift = float(L)
                break
        if lift is None:
            cands.append(dict(reach_add=dr, lift=None, ok=False, why="핸들바와 간섭(지지대 높이 한계)"))
            continue
        p["post_h"] = base_post + lift
        # keep the original arm if it already avoids the sweep, else route a stalk under the joint
        s = build_spec(p, tid)
        P = Problem(s)
        chosen = None
        if _arm_in_sweep(P, s) == 0 and connected(P, P.solid | (P.design & (P.initial_density() > 0.5)))[0]:
            chosen = (p, s, P)
        else:
            found = []
            for style in ("stalk", "under"):                 # each: highest base that clears the swept space
                for zb in np.arange(p["pad_z0"] - 6.0, p["domain_z_min"] + 6.0, -4.0):
                    q = dict(p, arm=style, stalk_base_z=float(zb))
                    s = build_spec(q, tid)
                    P = Problem(s)
                    on = P.solid | (P.design & (P.initial_density() > 0.5))
                    if _arm_in_sweep(P, s) == 0 and connected(P, on)[0]:
                        found.append((zb, (q, s, P)))
                        break
            if found:
                chosen = max(found, key=lambda f: f[0])[1]          # shortest stalk
        if chosen is None:
            cands.append(dict(reach_add=dr, lift=lift, ok=False, why="팔 경로 없음"))
            continue
        q, s, P = chosen
        r = evaluate(P, P.initial_density())
        cands.append(dict(reach_add=dr, lift=lift, ok=True, arm=q.get("arm"), stalk_base_z=q.get("stalk_base_z"),
                          f1_hz=r["f1_hz"], stress_mpa=r["checks"]["stress"]["value"], mass_g=r["mass_g"],
                          potential_f1_hz=design_potential(q, tid), params=q))
    ok = [c for c in cands if c["ok"]]
    # choose by what the optimiser can reach (design space potential), not by the thin sketch arm
    best = max(ok, key=lambda c: (c["potential_f1_hz"], c["f1_hz"])) if ok else None
    table = [{k: v for k, v in c.items() if k != "params"} for c in cands]
    return (best["params"] if best else p0), table


def design_potential(params, tid, h=4.0):
    """1st natural frequency with the whole design space filled (4 mm grid): an indicator of whether the
    optimiser can still reach the vibration limit once the requirement's keep-out space is removed."""
    s = build_spec(dict(params, h=h), tid)
    P = Problem(s)
    return evaluate(P, np.ones(len(P.label)))["f1_hz"]


def run_checks(spec, P, dens, fem_result):
    out = {}
    req = spec.get("requirements", [])
    if "sun_heat" in req:
        out["sun_heat"] = thermal.check(spec, fem_result)
    if "free_angle" in req:
        out["free_angle"] = angle.check(P, dens, spec, fem_eval=None)
    return out
