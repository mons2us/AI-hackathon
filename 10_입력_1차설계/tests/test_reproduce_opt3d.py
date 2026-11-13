"""The default bike-mount template must reproduce the team's hard-coded opt3d.py problem exactly:
element roles, fixed nodes, symmetry-plane nodes and the phone tip-mass distribution."""
import os, sys, types
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from formproof_input.compile import Problem
from formproof_input.templates.bike_mount import build_spec

OPT3D = os.path.join(ROOT, "..", "03_자전거거치대", "code_3D")


def opt3d_reference():
    """Run opt3d.py up to (not including) the stiffness assembly, with solver modules stubbed."""
    for m in ("mmapy", "pyamg", "pypardiso"):
        sys.modules.setdefault(m, types.ModuleType(m))
    sys.path.insert(0, OPT3D)
    src = open(os.path.join(OPT3D, "opt3d.py"), encoding="utf-8").read()
    head = src.split("iK=np.repeat")[0]
    ns = {}
    cwd = os.getcwd()
    try:
        os.chdir(OPT3D)
        exec(compile(head, "opt3d_head", "exec"), ns)
    finally:
        os.chdir(cwd)
    return ns


def test_reproduce():
    ref = opt3d_reference()
    P = Problem(build_spec())
    assert P.shape == (ref["nx"], ref["ny"], ref["nz"])
    assert np.allclose(P.origin, [ref["x0"], ref["y0"], ref["z0"]])
    for mine, theirs in ((P.design, "design"), (P.solid, "solid"), (P.void, "void"), (P.rigid, "post")):
        assert np.array_equal(mine, ref[theirs]), theirs
    assert np.array_equal(P.used, ref["used"])
    assert np.array_equal(np.sort(P.supports["handlebar"]), np.sort(ref["fixn"]))
    assert np.array_equal(np.sort(P.sym_plane), np.sort(ref["plane"]))
    assert np.allclose(P.node_mass, ref["tipm"], rtol=0, atol=1e-15)
    # adapter exposes the same names the optimiser header defines
    from formproof_input.adapter import opt3d_namespace
    ns = opt3d_namespace(build_spec())
    for name in ("design", "solid", "void", "post", "active", "used", "edof", "nxc", "nzc", "xc", "zc"):
        assert np.array_equal(ns[name], ref[name]), name
    for name in ("fixn", "plane", "topn"):
        assert np.array_equal(np.sort(ns[name]), np.sort(ref[name])), name
    assert np.allclose(ns["tipm"], ref["tipm"], atol=1e-15) and abs(ns["MP"] - ref["MP"]) < 1e-12
    assert abs(ns["FT"] - ref["FT"]) < 1e-9 and ns["E"] == ref["E"] and ns["rho"] == ref["rho"]
    return dict(design=int(P.design.sum()), solid=int(P.solid.sum()), void=int(P.void.sum()),
                rigid=int(P.rigid.sum()), fixed_nodes=len(P.supports["handlebar"]),
                tip_nodes=len(P.mass_sets["phone_clamp"][0]))


if __name__ == "__main__":
    print("opt3d.py reproduced:", test_reproduce())
