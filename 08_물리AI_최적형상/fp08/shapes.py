"""설계 범위 안 무작위 형상 생성기 (설계 결정 3번) + DeepSDF 학습용 점 샘플.

형식 A 직접 부재 / B 트러스(나무형 포함) / C 판 + 부재(삼각·사다리꼴·직사각) / D 열린 껍데기
+ E 보강(지지봉·리브 0~4개, 약 절반 확률).
규칙: 설계 칸 안에서만 재료, 고정부 전부 연결(약 5%는 일부러 끊긴 형상), 최소 두께 2칸(반지름 ≥ 1칸),
재료 비율 5~50%, 갇힌 빈 공간 메움(대칭면은 거울로 보고 판단). 같은 (그룹, 번호) → 항상 같은 형상(시드 고정).
"""
import zlib
import numpy as np
from scipy import ndimage

MIX = {'bike': [('B', .35), ('Ctri', .25), ('A', .15), ('D', .15), ('Cquad', .10)],
       'tv': [('A', .25), ('B', .25), ('Ctri', .125), ('Cquad', .125), ('D', .25)]}


def seed_of(group, idx):
    return zlib.crc32(f'{group}:{idx}'.encode()) & 0x7fffffff


# ---------------------------------------------------------------- 기본 도형(요소 중심 P 에 대해 bool)
def seg_dist(P, a, b):
    ab = b - a
    t = np.clip(((P - a) @ ab) / max(ab @ ab, 1e-12), 0, 1)
    return np.linalg.norm(P - (a + t[:, None] * ab), axis=1)


def capsule(P, a, b, r):
    return seg_dist(P, a, b) <= r


def tri_plate(P, a, b, c, t):
    n = np.cross(b - a, c - a); A2 = np.linalg.norm(n)
    if A2 < 1e-9:
        return np.zeros(len(P), bool)
    n = n / A2
    d = (P - a) @ n
    Q = P - d[:, None] * n
    def side(p, q):
        return (np.cross(q - p, Q - p) @ n) >= -0.5 * t
    inside = side(a, b) & side(b, c) & side(c, a)
    return inside & (np.abs(d) <= t / 2)


# ---------------------------------------------------------------- 문제에서 필요한 기하 정보
class Canvas:
    def __init__(self, p):
        self.p = p
        g = p.grid
        self.g = g
        self.P = np.stack([g.xc, g.yc, g.zc], 1)
        self.design = p.label == 0
        self.fixed = (p.label == 1) | (p.label == 3)
        self.dshape = g.eshape(self.design)
        # 고정부 덩어리별로 설계 칸과 맞닿은 칸 = 연결 후보점
        near = ndimage.binary_dilation(g.eshape(self.design)).ravel()
        self.anchor = []
        for c in range(1, p.n_fixed + 1):
            m = (p.fixed_comp == c) & near
            if not m.any():
                m = p.fixed_comp == c
            self.anchor.append(np.where(m)[0])
        self.Pd = self.P[self.design]
        lo, hi = self.Pd.min(0), self.Pd.max(0)
        self.lo, self.hi = lo, hi
        self.h = g.h
        self.product = 'bike' if p.product == 'bike_mount' else 'tv'

    def rand_anchor(self, rng, c):
        return self.P[rng.choice(self.anchor[c])]

    def rand_design_pt(self, rng):
        return self.Pd[rng.integers(len(self.Pd))]


def _radius(rng, h, lo=1.0, hi=3.0):
    return h * rng.uniform(lo, hi)


def gen_A(cv, rng):
    """직접 부재: 고정부 덩어리를 서로 곧은 막대로 잇기 (가끔 중간 꺾임 1번)"""
    P, h = cv.P, cv.h
    m = np.zeros(len(P), bool)
    nf = len(cv.anchor)
    pairs = [(i, j) for i in range(nf) for j in range(i + 1, nf)]
    rng.shuffle(pairs)
    n_bar = rng.integers(1, 3)
    for i, j in pairs[:max(nf - 1, 1)] + pairs[:0]:
        for _ in range(n_bar):
            a, b = cv.rand_anchor(rng, i), cv.rand_anchor(rng, j)
            r = _radius(rng, h)
            if rng.random() < 0.3:
                mid = (a + b) / 2 + rng.normal(0, 0.15, 3) * (cv.hi - cv.lo)
                m |= capsule(P, a, mid, r) | capsule(P, mid, b, r)
            else:
                m |= capsule(P, a, b, r)
    return m


def gen_B(cv, rng):
    """트러스: 무작위 경유점(1~4개)을 거치는 나무형 + 삼각 보강선"""
    P, h = cv.P, cv.h
    m = np.zeros(len(P), bool)
    hubs = [cv.rand_design_pt(rng) for _ in range(rng.integers(1, 5))]
    nodes = list(hubs)
    for c in range(len(cv.anchor)):
        for _ in range(rng.integers(1, 3)):
            a = cv.rand_anchor(rng, c)
            hb = hubs[int(np.argmin([np.linalg.norm(a - q) for q in hubs]))] if rng.random() < .7 else hubs[rng.integers(len(hubs))]
            m |= capsule(P, a, hb, _radius(rng, h))
            nodes.append(a)
    for i in range(1, len(hubs)):
        m |= capsule(P, hubs[i - 1], hubs[i], _radius(rng, h))
    for _ in range(rng.integers(0, 4)):            # 대각 보강선
        a, b = nodes[rng.integers(len(nodes))], nodes[rng.integers(len(nodes))]
        if np.linalg.norm(a - b) > 3 * h:
            m |= capsule(P, a, b, _radius(rng, h, 1.0, 2.0))
    return m


def gen_C(cv, rng, kind):
    """판 + 부재: 고정부 사이를 삼각형/사각형 판으로 덮고, 남은 연결은 막대"""
    P, h = cv.P, cv.h
    m = np.zeros(len(P), bool)
    t = h * rng.uniform(2.0, 4.0)
    nf = len(cv.anchor)
    for _ in range(rng.integers(1, 3)):
        pts = [cv.rand_anchor(rng, c) for c in range(nf)]
        while len(pts) < 3:
            pts.append(cv.rand_design_pt(rng))
        if kind == 'Ctri':
            a, b, c = pts[0], pts[1], pts[2] if nf >= 3 else cv.rand_design_pt(rng)
            m |= tri_plate(P, a, b, c, t)
        else:
            a, b = pts[0], pts[1]
            off = rng.normal(0, 0.25, 3) * (cv.hi - cv.lo)
            c, d = b + off * rng.uniform(.5, 1.5), a + off      # 직사각/사다리꼴
            m |= tri_plate(P, a, b, c, t) | tri_plate(P, a, c, d, t)
    if nf >= 2:
        for c in range(nf):
            if rng.random() < .5:
                m |= capsule(P, cv.rand_anchor(rng, c), cv.rand_design_pt(rng), _radius(rng, h))
    return m


def gen_D(cv, rng):
    """열린 껍데기: 매끈한 덩어리의 표면 2~3칸 두께만 남기고 평면으로 한쪽을 잘라 엶 → 고정부와 막대로 연결"""
    P, h = cv.P, cv.h
    span = cv.hi - cv.lo
    k = rng.integers(2, 6)
    C = cv.lo + rng.random((k, 3)) * span
    S = (0.15 + 0.25 * rng.random(k))[:, None] * span[None, :]
    f = np.zeros(len(P))
    for c, s in zip(C, S):
        f += np.exp(-0.5 * (((P - c) / s) ** 2).sum(1))
    solid = f > rng.uniform(0.35, 0.7) * f.max()
    sh = cv.g.eshape(solid)
    th = int(rng.integers(2, 4))
    shell = (sh & ~ndimage.binary_erosion(sh, iterations=th)).ravel()
    nrm = rng.normal(size=3); nrm /= np.linalg.norm(nrm)
    c0 = P[solid].mean(0) if solid.any() else C[0]
    shell &= ((P - c0) @ nrm) < rng.uniform(0, 0.4) * np.abs(span @ nrm)   # 한쪽 잘라 엶
    m = shell
    for c in range(len(cv.anchor)):
        a = cv.rand_anchor(rng, c)
        if m.any():
            q = P[m][np.argmin(np.linalg.norm(P[m] - a, axis=1))]
            m = m | capsule(P, a, q, _radius(rng, h, 1.0, 2.5))
    return m


def gen_E(cv, rng, base):
    """보강: 지지봉·리브 0~4개 (기존 재료 점 ↔ 다른 재료 점/고정부)"""
    P, h = cv.P, cv.h
    m = base.copy()
    idx = np.where(base & cv.design)[0]
    if len(idx) < 2:
        return m
    for _ in range(rng.integers(1, 5)):
        a = P[rng.choice(idx)]
        b = cv.rand_anchor(rng, rng.integers(len(cv.anchor))) if rng.random() < .5 else P[rng.choice(idx)]
        if np.linalg.norm(a - b) > 3 * h:
            m |= capsule(P, a, b, _radius(rng, h, 1.0, 2.0))
    return m


# ---------------------------------------------------------------- 후처리
def fill_cavities(cv, occ_full):
    """갇힌 빈 공간 메움. 대칭면 쪽은 거울로 붙여서 판단 (대칭면에 닿은 빈 곳이 바깥으로 오인되지 않게)."""
    g, p = cv.g, cv.p
    A = g.eshape(occ_full)
    ax = p.sym_axis
    if ax is not None:
        A2 = np.concatenate([np.flip(A, ax), A], ax)
        F = ndimage.binary_fill_holes(A2)
        n = A.shape[ax]
        F = np.take(F, range(n, 2 * n), axis=ax)
    else:
        F = ndimage.binary_fill_holes(A)
    return F.ravel()


def connected_groups(cv, occ_full):
    lab, n = ndimage.label(cv.g.eshape(occ_full))
    lab = lab.ravel()
    ids = [set(np.unique(lab[cv.p.fixed_comp == c])) - {0} for c in range(1, cv.p.n_fixed + 1)]
    common = set.intersection(*ids) if ids else set()
    return len(common) > 0, lab


def repair(cv, rng, m):
    """끊긴 덩어리를 가장 가까운 점끼리 막대로 잇고, 고정부와 안 이어진 떠다니는 조각은 지움"""
    P, h = cv.P, cv.h
    for _ in range(6):
        full = (m & cv.design) | cv.fixed
        ok, lab = connected_groups(cv, full)
        if ok:
            break
        comps = [set(np.unique(lab[cv.p.fixed_comp == c])) - {0} for c in range(1, cv.p.n_fixed + 1)]
        main = comps[0]
        for cs in comps[1:]:
            if cs & main:
                continue
            A = P[np.isin(lab, list(main))]; B = P[np.isin(lab, list(cs))]
            sa = A[rng.choice(len(A), min(400, len(A)), replace=False)]
            sb = B[rng.choice(len(B), min(400, len(B)), replace=False)]
            d = np.linalg.norm(sa[:, None] - sb[None], axis=2)
            i, j = np.unravel_index(np.argmin(d), d.shape)
            m = m | capsule(P, sa[i], sb[j], _radius(rng, h, 1.0, 2.0))
            main = main | cs
    full = (m & cv.design) | cv.fixed
    ok, lab = connected_groups(cv, full)
    if ok:
        keep = set(np.unique(lab[cv.fixed])) - {0}
        full = np.isin(lab, list(keep))
    return full & cv.design, ok


def make_shape(p, group, idx, cv=None, max_try=12):
    """반환: occ_design (ne,) bool, meta dict"""
    cv = cv or Canvas(p)
    rng = np.random.default_rng(seed_of(group, idx))
    fams, w = zip(*MIX[cv.product])
    for attempt in range(max_try):
        fam = fams[rng.choice(len(fams), p=np.array(w) / sum(w))]
        if fam == 'A':
            m = gen_A(cv, rng)
        elif fam == 'B':
            m = gen_B(cv, rng)
        elif fam in ('Ctri', 'Cquad'):
            m = gen_C(cv, rng, fam)
        else:
            m = gen_D(cv, rng)
        reinf = rng.random() < 0.5
        if reinf:
            m = gen_E(cv, rng, m)
        m &= cv.design
        want_broken = rng.random() < 0.05
        if want_broken:
            occ, ok = m, connected_groups(cv, m | cv.fixed)[0]
        else:
            occ, ok = repair(cv, rng, m)
        occ = fill_cavities(cv, occ | cv.fixed) & cv.design
        vf = occ.sum() / cv.design.sum()
        if 0.05 <= vf <= 0.50 and (ok or want_broken):
            return occ, dict(group=group, idx=int(idx), family=fam, reinforced=bool(reinf), vf=float(vf),
                             connected=bool(connected_groups(cv, occ | cv.fixed)[0]), attempt=attempt)
    return occ, dict(group=group, idx=int(idx), family=fam, reinforced=bool(reinf), vf=float(vf),
                     connected=bool(ok), attempt=max_try, failed=True)


# ---------------------------------------------------------------- SDF (DeepSDF 정답)
def sdf_grid(p, occ_full):
    """요소 중심 격자의 부호 거리 [mm] (안쪽 음수). EDT 기반, 반 칸 보정."""
    g = p.grid
    A = g.eshape(occ_full)
    h = g.h
    out = ndimage.distance_transform_edt(~A) * h
    inn = ndimage.distance_transform_edt(A) * h
    return np.where(A, -(inn - h / 2), out - h / 2)


def sample_sdf(p, occ_full, rng, n=4000, delta=None, near_frac=0.85):
    """표면 근처 위주로 n점 샘플 → (n,3) 좌표[mm], (n,) SDF[mm], ±delta 로 자름."""
    g = p.grid
    h = g.h
    delta = delta or 4 * h
    S = sdf_grid(p, occ_full)
    region = (p.label != 2)
    Sm = S.ravel()
    near = np.where(region & (np.abs(Sm) <= 2 * h))[0]
    allr = np.where(region)[0]
    nn = int(n * near_frac)
    pick = np.concatenate([rng.choice(near, nn, replace=len(near) < nn) if len(near) else rng.choice(allr, nn),
                           rng.choice(allr, n - nn)])
    P = np.stack([g.xc[pick], g.yc[pick], g.zc[pick]], 1) + rng.uniform(-h / 2, h / 2, (n, 3))
    q = (P - g.origin) / h - 0.5                        # 요소 중심 격자 좌표
    shp = S.shape  # (nz, ny, nx) 또는 eshape 규약
    val = ndimage.map_coordinates(S, _coords_for(g, q), order=1, mode='nearest')
    return P.astype(np.float32), np.clip(val, -delta, delta).astype(np.float32)


def _coords_for(g, q):
    """eshape 축 순서에 맞춘 좌표 배열"""
    test = g.eshape(np.arange(g.ne))
    # eshape 가 (nz, ny, nx) 이면 [k, j, i] 순서
    if test.shape == (g.nz, g.ny, g.nx):
        return np.stack([q[:, 2], q[:, 1], q[:, 0]])
    return np.stack([q[:, 0], q[:, 1], q[:, 2]])
