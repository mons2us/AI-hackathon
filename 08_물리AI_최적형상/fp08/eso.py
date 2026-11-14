"""ESO 방식 다듬기 (11-14 사용자 제안): FEM 으로 칸마다 변형 에너지를 구해, 힘을 거의 안 받는 칸을 지움.

참고: Y. M. Xie, G. P. Steven, "A simple evolutionary procedure for structural optimization," Computers & Structures 49 (1993).
- 판단 기준: 응력 대신 **변형 에너지 밀도**(기본 하중 경우들을 각각 전체 에너지로 나눠 합침).
  거치대는 기준이 진동수라 응력만 보면 진동에 중요한 칸을 지울 수 있음 → 충격 하중(위아래·옆) 에너지로 판단.
- 한 번에 재료 칸의 frac(기본 15%)만 지우고, 정리(한쪽 덩어리 삭제·다듬기·대칭)를 다시 함.
  고정부가 끊기면 그 회차는 취소하고 frac 를 절반으로 줄여 다시 시도.
- 원본은 그대로 두고, 다듬은 형상은 새 형상으로 추가 (다양성 유지).
"""
import numpy as np
from . import labels, shapes


def energy_density(p, occ, res):
    g = p.grid
    ks = p.kscale(occ.astype(float))
    E = np.zeros(g.ne)
    for u in res['U'].values():
        ue = u[g.edof]
        e = np.einsum('ei,ij,ej->e', ue, p.KE, ue) * ks
        E += e / (e.sum() + 1e-300)
    return E


def eso_prune(p, cv, occ, cond=None, frac=0.15, iters=2, min_vf=0.04):
    """반환: (다듬은 occ, 기록 dict). FEM 은 정적만(진동 없이) iters 번."""
    cond = cond or p.default_cond
    occ = occ.copy()
    log = []
    for it in range(iters):
        res = labels.fem_label(p, occ, cond, want_modes=False)
        E = energy_density(p, occ, res)
        m = np.where(occ & cv.design)[0]
        if len(m) == 0:
            break
        f = frac
        while f > 0.02:
            k = int(f * len(m))
            cut = m[np.argsort(E[m])[:k]]
            new = occ.copy(); new[cut] = False
            new = shapes.drop_dead_blobs(cv, new)
            new = shapes.smooth(cv, new)
            for a in cv.sym_axes:
                new = (new | np.flip(cv.g.eshape(new), a).ravel()) & cv.design
            new = shapes.fill_cavities(cv, new | cv.fixed) & cv.design
            new = shapes.drop_floating(cv, new)     # 11-14: 다듬기 뒤 떠 있는 작은 조각(진동수 0 Hz 원인) 삭제
            ok = shapes.connected_groups(cv, new | cv.fixed)[0] and new.sum() >= min_vf * cv.design.sum()
            if ok:
                break
            f /= 2
        if not ok:
            log.append(dict(it=it, stopped='connectivity'))
            break
        log.append(dict(it=it, removed=int(occ.sum() - new.sum()), frac=f))
        occ = new
    return occ, log
