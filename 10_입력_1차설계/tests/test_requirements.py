"""User requirements -> physics conditions: '여름 땡볕에서 변형 없음', '화면 각도 최대한 자유롭게'."""
import math, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from formproof_input import angle, thermal, text_rules
from formproof_input import evidence as ev
from formproof_input.compile import Problem
from formproof_input.templates.bike_mount import build_spec
from formproof_input.templates.library import BY_ID


def test_text_detects_requirements():
    r = text_rules.parse("여름 땡볕에서 변형이 없도록 하고, 화면 각도 변환을 최대한 자유롭게")
    assert set(r["params"]["requirements"]) == {"sun_heat", "free_angle"}


def test_thermal_physics():
    s = ev.SUN
    tb = thermal.surface_temp(0.925, s["h_still"])
    tw = thermal.surface_temp(0.20, s["h_still"])
    t0 = thermal.surface_temp(0.0, s["h_still"])
    assert tb > tw > t0 and abs(tb - 76.9) < 0.2 and abs(tw - 48.5) < 0.2       # regression of the energy balance
    # more convection -> cooler, converging to the no-sun temperature
    assert thermal.surface_temp(0.925, 35.0) < tb
    hdt = ev.MATERIALS["PETG"]["hdt"]
    assert thermal.hdt_at(0.2, hdt)[0] == 74.0 and thermal.hdt_at(1.8, hdt)[0] == 68.0
    assert abs(thermal.hdt_at(1.125, hdt)[0] - 71.0) < 1e-9
    return dict(black=round(tb, 1), white=round(tw, 1), no_sun=round(t0, 1))


def test_tilt_vs_hand_calc():
    """Bar-only portrait tilt limit: code vs an independent 2-D calculation of the phone's back-face line."""
    s = build_spec(BY_ID["T01"]["params"], "T01")
    P = Problem(s)
    pc = angle.PoseChecker(P, np.zeros(len(P.label)), s)
    from scipy.spatial import cKDTree
    pc.tree = cKDTree(np.array([[1e9, 1e9, 1e9]]))
    code_max = pc.tilt_range(0, 3.0, lo=0)[1]
    ph, g = s["geometry"]["phone"], s["geometry"]
    jx, jz = ph["cog"][0], ph["cog"][1] - (ph["clamp_t"] + ph["D"] / 2)
    hand = 0
    for t in range(0, 91):
        th = math.radians(t)
        u = np.arange(-ph["H"] / 2, ph["H"] / 2 + 1e-9, 2.0)
        x = jx + u * math.cos(th) - ph["clamp_t"] * math.sin(th)
        z = jz + u * math.sin(th) + ph["clamp_t"] * math.cos(th)
        if (np.hypot(x, z) - g["ring_ro"]).min() < 3.0:        # phone spans the clamp width -> ring radius governs
            break
        hand = t
    assert code_max == hand, (code_max, hand)
    return dict(portrait_tilt_limit_deg=hand)


def test_requirements_are_handoff_only():
    """Requirements add conditions for the optimiser but never change the 1st design."""
    base = build_spec(BY_ID["T01"]["params"], "T01")
    req = build_spec(dict(BY_ID["T01"]["params"], requirements=["free_angle", "sun_heat"]), "T01")
    P0, P1 = Problem(base), Problem(req)
    assert np.array_equal(P0.label, P1.label)                                   # same roles
    assert np.array_equal(P0.initial_density(), P1.initial_density())           # same 1st design
    assert P0.keepout is None and P1.keepout is not None and P1.keepout.sum() > 0
    ids = {c["id"] for c in req["constraints"]}
    assert {"pose_clearance", "joint_stiffness", "joint_hold", "sun_heat"} <= ids
    from formproof_input.requirements import handoff_summary
    hs = {h["id"]: h for h in handoff_summary(req, P1)}
    assert set(hs) == {"free_angle", "sun_heat"}
    return dict(keepout_elements=int(P1.keepout.sum()), warnings=hs["free_angle"]["warnings"][:1])


if __name__ == "__main__":
    test_text_detects_requirements()
    print(test_thermal_physics())
    print(test_tilt_vs_hand_calc())
    print(test_requirements_are_handoff_only())
