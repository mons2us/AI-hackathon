"""Rigid-body payload (team v3): our half model (symmetry cases S + A, weighted rigid fit) must give the same
natural frequencies and transmissibility as the team's full model (03_자전거거치대/opt3d_am.py RIGID=1 mass matrix,
verify_sys.py frf formula) on the same 1st design."""
import os, sys, types
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from formproof_input.compile import Problem
from formproof_input.fem import evaluate
from formproof_input.templates.bike_mount import build_spec

TEAM = os.path.join(ROOT, "..", "03_자전거거치대")


def team_full_model():
    """opt3d_am.py header (RIGID=1, MSYS 0.350) up to the optimisation loop; solver modules stubbed."""
    for m in ("mmapy", "pypardiso"):
        try:                                             # 설치돼 있으면 진짜 모듈 (빈 껍데기가 뒤 시험의 pypardiso 를 가리지 않게)
            __import__(m)
        except ImportError:
            sys.modules.setdefault(m, types.ModuleType(m))
    sys.path.insert(0, os.path.join(TEAM, "code_3D"))
    src = open(os.path.join(TEAM, "opt3d_am.py"), encoding="utf-8").read()
    head = src.split("def interp(r):")[0]
    env = dict(os.environ)
    os.environ.update(RIGID="1", MSYS="0.350", CGZ="36.5", BOX="165,80,15", XP="90")
    ns = {}
    try:
        exec(compile(head, "opt3d_am_head", "exec"), ns)
    finally:
        os.environ.clear()
        os.environ.update(env)
    return ns


def full_eigs(ns, dens_full, k=8):
    on = ns["active"] & (ns["solid"] | ns["post"] | (ns["design"] & (dens_full > 0.5)))
    ke = np.where(ns["post"], 20.0, 1.0)
    idx = np.where(on)[0]
    edof, KE = ns["edof"], ns["KE"]
    K = sp.coo_matrix(((KE.ravel()[None, :] * ke[idx][:, None]).ravel(),
                       (np.repeat(edof[idx], 24, 1).ravel(), np.tile(edof[idx], (1, 24)).ravel())),
                      shape=(3 * ns["nn"], 3 * ns["nn"])).tocsr()
    mel = np.where(on & ~ns["post"], 1.0, 0.0)
    mn = np.zeros(ns["nn"])
    np.add.at(mn, ns["en"].ravel(), np.repeat(mel * ns["me0"] / 8, 8))
    used = np.zeros(ns["nn"], bool)
    used[ns["en"][on].ravel()] = True
    fixed = np.r_[3 * ns["fixn"], 3 * ns["fixn"] + 1, 3 * ns["fixn"] + 2]
    free = np.setdiff1d(np.where(np.repeat(used, 3))[0], fixed)
    M = (sp.diags(np.repeat(mn, 3)) + ns["MA"]).tocsr()[free][:, free].tocsc()
    A = K[free][:, free].tocsc()
    lu = sla.splu(A)
    w, V = sla.eigsh(A, k=k, M=M, sigma=0, OPinv=sla.LinearOperator(A.shape, matvec=lu.solve), tol=1e-10)
    o = np.argsort(w)
    w, V = w[o], V[:, o]
    # verify_sys.frf: phone CG motion / base motion, z direction, damping 3 %
    full = np.zeros((3 * ns["nn"], k))
    full[free] = V
    r = np.zeros(3 * ns["nn"])
    r[2::3] = 1.0
    gam = V.T @ (M @ r[free])
    cgz = ns["Tp"][2] @ full[ns["dd"]]
    f = np.round(np.arange(5.0, 100.0 + 1e-9, 0.5), 1)
    om, wn = 2 * np.pi * f, np.sqrt(w)
    H = 1 + np.sum((cgz * gam)[None] * om[:, None] ** 2 / (wn ** 2 - om[:, None] ** 2 + 2j * 0.03 * wn * om[:, None]), 1)
    band = (f >= 34.6) & (f <= 45.6)
    return wn / 2 / np.pi, float(np.abs(H)[band].max())


def test_rigid_payload_matches_team_full_model():
    spec = build_spec()                                    # DEFAULT: phone not specified -> 350 g, box 165 x 80 x 15
    P = Problem(spec)
    pm = spec["point_masses"][0]
    assert pm["model"] == "rigid_body" and abs(pm["mass_kg"] - 0.350) < 1e-12 and pm["cg"] == [91.0, 55.0, 36.5]
    dens = P.initial_density()
    mine = evaluate(P, dens)
    ns = team_full_model()
    nx, ny, nz = P.shape
    half = dens.reshape(nz, ny, nx)
    full = np.concatenate([half[:, ::-1, :], half], axis=1).ravel()
    f_team, T_team = full_eigs(ns, full)
    f_mine = np.array(mine["freqs_hz"][:4])
    assert np.abs(f_mine - f_team[:4]).max() <= 0.051, (f_mine, f_team[:4])       # ours are rounded to 0.1 Hz
    T_mine = mine["frf"]["z"]["Tmax_band"]
    assert abs(T_mine - T_team) / T_team < 5e-3, (T_mine, T_team)
    return dict(f_mine=f_mine.tolist(), f_team=np.round(f_team[:4], 1).tolist(), T_band_z=[T_mine, round(T_team, 3)])


def test_payload_load_resultant():
    """Inertial load of the rigid payload: the half model carries half the force in the components its symmetry
    case keeps (S: x, z; A: y); the other components cancel with the mirror half."""
    spec = build_spec()
    P = Problem(spec)
    rp = P.rigid_payloads["phone_clamp"]
    for c in spec["load_cases"]:
        if c["type"] != "inertial":
            continue
        F = P.load_vector(dict(c, include_self=False)).reshape(-1, 3)
        expect = 0.5 * rp["mass_t"] * c["accel_g"] * 9810.0 * np.asarray(c["dir"], float)
        keep = [1] if P.sym_case(c["dir"]) == "A" else [0, 2]
        assert np.allclose(F.sum(0)[keep], expect[keep], rtol=1e-9, atol=1e-9), (c["name"], F.sum(0), expect)


if __name__ == "__main__":
    print(test_rigid_payload_matches_team_full_model())
    test_payload_load_resultant()
    print("load resultant ok")
