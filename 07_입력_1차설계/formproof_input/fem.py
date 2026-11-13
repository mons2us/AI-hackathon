"""Quick check of a voxel design against the spec's criteria (scipy only, no pypardiso).
Used to judge the 1st design before hand-off; the physics stage does the real optimisation.
Element formulation = the team's hex8 (03_자전거거치대/code_3D/fem3d.py)."""
import importlib.util
import os
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla
from scipy import ndimage

_FEM3D = os.path.join(os.path.dirname(__file__), "..", "..", "03_자전거거치대", "code_3D", "fem3d.py")
_spec = importlib.util.spec_from_file_location("team_fem3d", _FEM3D)
_team = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_team)
hex8_KB = _team.hex8_KB


def on_mask(P, dens):
    return P.solid | P.rigid | (P.design & (dens > 0.5))


def connected(P, on):
    """True if every active element is joined (face-adjacent) to an element touching a support."""
    nx, ny, nz = P.shape
    lab, n = ndimage.label(on.reshape(nz, ny, nx))
    sup = np.zeros(P.nn, bool)
    for s in P.supports.values():
        sup[s] = True
    touching = sup[P.enodes].any(1) & on
    seed = np.unique(lab.ravel()[touching])
    seed = seed[seed > 0]
    return bool(np.isin(lab.ravel()[on], seed).all()), int(n)


def _free(P, on, case):
    used = np.zeros(P.nn, bool)
    used[P.enodes[on].ravel()] = True
    fixed = [3 * n + d for s in P.supports.values() for n in s for d in range(3)]
    if P.sym_axis is not None and case in "SA":
        ax = P.sym_axis
        plane = np.where(used & (P.nijk[:, ax] == 0))[0]
        dofs = [ax] if case == "S" else [d for d in range(3) if d != ax]
        fixed += [3 * n + d for n in plane for d in dofs]
    dof = np.where(np.repeat(used, 3))[0]
    return np.setdiff1d(dof, np.array(fixed, int))


def evaluate(P, dens, n_modes=2):
    spec = P.spec
    mat = spec["material"]
    KE, C, B0, _ = hex8_KB(mat["E"], mat["nu"], P.h)
    on = on_mask(P, dens)
    edof = np.stack([3 * P.enodes, 3 * P.enodes + 1, 3 * P.enodes + 2], 2).reshape(len(on), 24)
    idx = np.where(on)[0]
    ke = P.k_scale[idx]
    K = sp.coo_matrix(((KE.ravel()[None, :] * ke[:, None]).ravel(),
                       (np.repeat(edof[idx], 24, 1).ravel(), np.tile(edof[idx], (1, 24)).ravel())),
                      shape=(3 * P.nn, 3 * P.nn)).tocsc()
    me = mat["rho"] * P.h ** 3 * P.m_scale * on
    mn = np.zeros(P.nn)
    np.add.at(mn, P.enodes.ravel(), np.repeat(me / 8, 8))
    mn += P.node_mass
    M = np.repeat(mn, 3)
    ok_struct, n_parts = connected(P, on)
    out = dict(mass_g=round(float(2 * (me * (~P.rigid)).sum() * 1e6), 1),
               elements=int(on.sum()), connected=ok_struct, parts=n_parts)
    excl = np.zeros(len(on), bool)
    for c in spec["constraints"]:
        for r in c.get("exclude_regions", []):
            excl |= P.region_masks[r]
    judge = on & ~P.rigid & ~excl
    freqs = []
    lu_cache = {}
    for case in ("S", "A"):
        fr = _free(P, on, case)
        A = K[fr][:, fr].tocsc()
        lu = sla.splu(A)
        lu_cache[case] = (fr, lu)
        op = sla.LinearOperator(A.shape, matvec=lu.solve, dtype=float)
        w = sla.eigsh(A, k=n_modes, M=sp.diags(M[fr]), sigma=0, OPinv=op, return_eigenvectors=False)
        freqs += [float(np.sqrt(abs(x)) / 2 / np.pi) for x in w]
    out["freqs_hz"] = sorted(round(f, 1) for f in freqs)
    out["f1_hz"] = out["freqs_hz"][0]
    for c in spec["load_cases"]:
        if c["type"] != "inertial":
            continue
        case = P.sym_case(c["dir"])
        fr, lu = lu_cache[case]
        F = P.load_vector(c, dens * on)
        u = np.zeros(3 * P.nn)
        u[fr] = lu.solve(F[fr])
        ue = u[edof]
        s = (C @ B0 @ ue.T).T
        vm = np.sqrt(0.5 * ((s[:, 0] - s[:, 1]) ** 2 + (s[:, 1] - s[:, 2]) ** 2 + (s[:, 2] - s[:, 0]) ** 2)
                     + 3 * (s[:, 3:] ** 2).sum(1))
        tip = P.mass_sets[c["applies_to"][0]][0]
        d = int(np.argmax(np.abs(c["dir"])))
        out[c["name"]] = dict(vm_max_mpa=round(float(vm[judge].max()), 1),
                              vm_p999_mpa=round(float(np.percentile(vm[judge], 99.9)), 1),
                              s_yy_tension_mpa=round(float(np.maximum(s[judge, 1], 0).max()), 1),
                              tip_disp_mm=round(float(np.abs(u[3 * tip + d]).mean()), 3))
    out["checks"] = judge_constraints(spec, out)
    out["pass"] = all(v["pass"] for v in out["checks"].values()) and ok_struct
    return out


def judge_constraints(spec, r):
    ck = {}
    for c in spec["constraints"]:
        if c["quantity"] == "natural_frequency_hz":
            v = r["f1_hz"]
        elif c["quantity"] == "von_mises_max_mpa":
            v = max(r[n]["vm_max_mpa"] for n in c["load_cases"])
        elif c["quantity"] == "layer_normal_tension_mpa":
            v = max(r[n]["s_yy_tension_mpa"] for n in c["load_cases"])
        else:
            continue                                   # min_feature: checked by the physics stage
        ok = v >= c["value"] if c["op"] == ">=" else v <= c["value"]
        ck[c["id"]] = dict(value=v, limit=f'{c["op"]} {c["value"]}', **{"pass": bool(ok)})
    return ck
