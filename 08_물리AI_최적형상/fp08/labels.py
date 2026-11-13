"""FEM 정답 라벨 — 형상 하나(0/1 칸)를 넣으면 기본 하중별 변위·고유진동수·판정값을 돌려준다.

설계 결정 4번: 형상마다 대칭 조건(S/A)별로 강성행렬을 한 번만 분해해서 기본 하중 전부 + 고유값을 같은 분해로 푼다.
속도를 위해 0/1 형상은 재료 칸 + 고정부만 조립한다(빈 설계 칸은 아예 뺌 → 행렬이 작아짐).
"""
import time
import numpy as np
from . import fem


def fem_label(p, occ, cond=None, want_modes=True, keep_K=False):
    """p: Problem, occ: (ne,) 0/1 설계 칸 채움. 반환 dict(U{basis:(3nn,)}, freq{bc:[Hz]}, occ, eval, t)."""
    t0 = time.time()
    g = p.grid
    cond = cond or p.default_cond
    occ = np.asarray(occ, float)
    on = (p.label == 1) | (p.label == 3) | ((p.label == 0) & (occ > 0.5))
    occb = (occ > 0.5).astype(float)
    ks = p.kscale(occb)
    K = fem.assemble(g, p.KE, ks, on)
    used = np.zeros(g.nn, bool); used[g.en[on].ravel()] = True
    dof_used = np.repeat(used, 3)
    free = {bc: f[dof_used[f]] for bc, f in p.free.items()}
    B = p.basis(cond)
    F_by = {}
    names = {}
    for name, bc, f in B:
        F_by.setdefault(bc, []).append(f); names.setdefault(bc, []).append(name)
    F_by = {bc: np.stack(v, 1) for bc, v in F_by.items()}
    M = None
    modes = None
    if want_modes and p.modes:
        em = p.emass(occb) * on
        M = fem.lumped_mass(g, em, p.node_mass(cond))
        modes = p.modes
    U, FR, _ = fem.solve_cases(g, K, free, F_by, M_node=M, modes_by_bc=modes)
    Ud = {}
    for bc, nm in names.items():
        for j, n in enumerate(nm):
            Ud[n] = U[bc][:, j]
    res = dict(U=Ud, freq={bc: np.asarray(v) for bc, v in (FR or {}).items()}, occ=occb, _K=K)
    res['eval'] = p.evaluate(res, cond)
    res['t'] = time.time() - t0
    if not keep_K:
        res.pop('_K')
    return res


def nodal_fields(p, res):
    """학습용 출력: 기본 하중별 절점 변위 (C, NX, NY, NZ) float32 — C = 3 × 기본 하중 수"""
    g = p.grid
    out = []
    for name, _, _ in p.basis(p.default_cond):
        u = res['U'][name].reshape(g.NZ, g.NY, g.NX, 3)
        out.append(np.moveaxis(u, -1, 0).transpose(0, 3, 2, 1))   # (3, NX, NY, NZ)
    return np.concatenate(out, 0).astype(np.float32)
