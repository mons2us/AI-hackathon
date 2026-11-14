"""설계 범위 안 무작위 형상 생성기 (설계 결정 3번) + DeepSDF 학습용 점 샘플.

형식 A 직접 부재 / B 트러스(나무형 포함) / C 판 + 부재(삼각·사다리꼴·직사각) / D 열린 껍데기
+ E 보강(지지봉·리브 0~4개, 약 절반 확률).
규칙: 설계 칸 안에서만 재료, 고정부 전부 연결(약 5%는 일부러 끊긴 형상), 최소 두께 2칸(반지름 ≥ 1칸),
재료 비율 5~50%, 갇힌 빈 공간 메움(대칭면은 거울로 보고 판단). 같은 (그룹, 번호) → 항상 같은 형상(시드 고정).
"""
import zlib
import numpy as np
from scipy import ndimage, sparse
from scipy.sparse import csgraph

MIX = {'bike': [('B', .35), ('Ctri', .25), ('A', .15), ('D', .15), ('Cquad', .10)],
       'tv': [('A', .25), ('B', .30), ('Ctri', .175), ('Cquad', .175), ('D', .10)]}   # 11-14: D 25→10% (사용자 결정)
MIX_UNIFORM = [('A', .2), ('B', .2), ('Ctri', .2), ('Cquad', .2), ('D', .2)]


def auto_sym_axes(p):
    """문제(라벨: 설계·고정·빈 곳·강체)를 각 축으로 뒤집어 똑같으면 그 축은 대칭 → 형상도 대칭으로 만듦.
    절반 모델의 대칭면 축은 이미 거울 복원되므로 제외. 반환: eshape (z, y, x) 축 번호 목록.
    (spec 의 conditions 에 'free_asymmetry': True 가 있으면 끔 — 사용자가 비대칭을 원할 때)"""
    if p.conditions.get('free_asymmetry'):
        return []
    L = p.grid.eshape(p.label)
    skip = None if p.sym_axis is None else 2 - p.sym_axis
    return [a for a in range(3) if a != skip and np.array_equal(L, np.flip(L, a))]


def seed_of(group, idx):
    return zlib.crc32(f'{group}:{idx}'.encode()) & 0x7fffffff


# ---------------------------------------------------------------- 기본 도형(요소 중심 P 에 대해 bool)
def seg_dist(P, a, b):
    ab = b - a
    t = np.clip(((P - a) @ ab) / max(ab @ ab, 1e-12), 0, 1)
    return np.linalg.norm(P - (a + t[:, None] * ab), axis=1)


def capsule(P, a, b, r):
    return seg_dist(P, a, b) <= r


def bar(cv, a, b, r):
    """막대 a→b. 금지 공간이 있고 곧은 막대가 그곳을 지나면 돌아가는 경로를 따라 그림 (없으면 capsule 과 같음)"""
    if cv.avoid is None:
        return capsule(cv.P, a, b, r)
    n = max(2, int(np.linalg.norm(b - a) / (cv.h / 2)) + 1)
    pts = a[None] + np.linspace(0, 1, n)[:, None] * (b - a)[None]
    if not cv.avoid[cv.cell_of(pts)].any():
        return capsule(cv.P, a, b, r)
    way = cv.route(a, b)
    if way is None:
        return capsule(cv.P, a, b, r)
    m = np.zeros(len(cv.P), bool)
    for p0, p1 in zip(way[:-1], way[1:]):
        m |= capsule(cv.P, p0, p1, r)
    return m


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
        self.sym_axes = auto_sym_axes(p)          # 11-14: 라벨이 뒤집어도 같은 축 = 형상도 대칭으로 생성
        self.mix = MIX_UNIFORM                    # 11-14: 후보는 모든 형식을 같은 비율로, 선택 단계에서 자동 조정
        # 11-14: 금지 공간(keepout, 예: 폰이 회전하며 지나가는 공간)이 있으면 막대를 그 공간을 돌아가게 그림.
        # 금지 공간이 없는 그룹은 예전과 똑같은 형상(같은 시드 → 같은 형상) 유지
        ko = getattr(p, 'keepout', None)
        self.avoid = ko if ko is not None and ko.any() else None
        self._graph = None

    def cell_of(self, X):
        """좌표(…,3) → 요소 번호 (격자 밖은 가장자리로)"""
        g = self.g
        q = np.floor((np.asarray(X) - g.origin) / g.h).astype(int)
        i = np.clip(q[..., 0], 0, g.nx - 1); j = np.clip(q[..., 1], 0, g.ny - 1); k = np.clip(q[..., 2], 0, g.nz - 1)
        return (k * g.ny + j) * g.nx + i

    def _build_graph(self):
        """설계+고정 칸 그래프 (6이웃). 금지 공간 가장자리에서 멀수록 싸게 → 경로가 금지 공간에서 떨어져 지나감"""
        g = self.g
        ok = self.design | self.fixed
        d = ndimage.distance_transform_edt(g.eshape(ok)).ravel() * g.h        # 막힌 칸까지 거리 [mm]
        cost = 1.0 + 3.0 * np.exp(-d / (2 * g.h))
        idx = np.arange(g.ne).reshape(g.nz, g.ny, g.nx)
        okg = g.eshape(ok)
        rows, cols, w = [], [], []
        for ax in range(3):
            a = [slice(None)] * 3; b = [slice(None)] * 3
            a[ax] = slice(0, -1); b[ax] = slice(1, None)
            m = okg[tuple(a)] & okg[tuple(b)]
            i0, i1 = idx[tuple(a)][m], idx[tuple(b)][m]
            ww = 0.5 * (cost[i0] + cost[i1])
            rows += [i0, i1]; cols += [i1, i0]; w += [ww, ww]
        self._graph = sparse.csr_matrix((np.concatenate(w), (np.concatenate(rows), np.concatenate(cols))), shape=(g.ne, g.ne))
        self._ok = ok

    def route(self, a, b):
        """a→b 를 금지 공간을 피해 잇는 경유점 목록 (설계+고정 칸만 지나는 최단 경로를 4칸마다 끊음). 길 없으면 None"""
        if self._graph is None:
            self._build_graph()
        ia, ib = int(self.cell_of(a)), int(self.cell_of(b))
        okidx = np.where(self._ok)[0]
        if not self._ok[ia]:
            ia = int(okidx[np.argmin(np.linalg.norm(self.P[okidx] - a, axis=1))])
        if not self._ok[ib]:
            ib = int(okidx[np.argmin(np.linalg.norm(self.P[okidx] - b, axis=1))])
        dist, pred = csgraph.dijkstra(self._graph, indices=ia, return_predecessors=True)
        if not np.isfinite(dist[ib]):
            return None
        path = [ib]
        while path[-1] != ia:
            path.append(int(pred[path[-1]]))
        path = path[::-1]
        keep = path[::4] + ([path[-1]] if (len(path) - 1) % 4 else [])
        return [a] + [self.P[c] for c in keep[1:-1]] + [b]

    def rand_anchor(self, rng, c):
        return self.P[rng.choice(self.anchor[c])]

    def rand_design_pt(self, rng):
        return self.Pd[rng.integers(len(self.Pd))]


_TS = [1.0]     # 형상마다 두께 배율 (얇은 것~굵은 것 고르게 → 기준 근처 형상도 포함)


def _radius(rng, h, lo=1.0, hi=3.0):
    return h * rng.uniform(lo, hi) * _TS[0]


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
                m |= bar(cv, a, mid, r) | bar(cv, mid, b, r)
            else:
                m |= bar(cv, a, b, r)
    return m


def gen_B(cv, rng):
    """트러스: 무작위 경유점(1~4개)을 거치는 나무형 + 삼각 보강선.
    (11-14 수정) 고정부와 연결되지 않은 사슬 끝 경유점은 버림 → 끝이 허공에 뜬 가지가 생기지 않음"""
    P, h = cv.P, cv.h
    m = np.zeros(len(P), bool)
    hubs = [cv.rand_design_pt(rng) for _ in range(rng.integers(1, 5))]
    links, has_anchor, nodes = [], [False] * len(hubs), []
    for c in range(len(cv.anchor)):
        for _ in range(rng.integers(1, 3)):
            a = cv.rand_anchor(rng, c)
            j = int(np.argmin([np.linalg.norm(a - q) for q in hubs])) if rng.random() < .7 else int(rng.integers(len(hubs)))
            links.append((a, j)); has_anchor[j] = True; nodes.append(a)
    lo, hi = 0, len(hubs) - 1
    while lo < hi and not has_anchor[lo]:
        lo += 1
    while hi > lo and not has_anchor[hi]:
        hi -= 1
    for a, j in links:
        m |= bar(cv, a, hubs[j], _radius(rng, h))
    for i in range(lo + 1, hi + 1):
        m |= bar(cv, hubs[i - 1], hubs[i], _radius(rng, h))
    nodes += [hubs[i] for i in range(lo, hi + 1) if has_anchor[i] or lo < i < hi]
    for _ in range(rng.integers(0, 4)):            # 대각 보강선 (양 끝 모두 기존 마디)
        a, b = nodes[rng.integers(len(nodes))], nodes[rng.integers(len(nodes))]
        if np.linalg.norm(a - b) > 3 * h:
            m |= bar(cv, a, b, _radius(rng, h, 1.0, 2.0))
    return m


def gen_C(cv, rng, kind):
    """판 + 부재: 고정부 사이를 삼각형/사각형 판으로 덮고, 남은 연결은 막대"""
    P, h = cv.P, cv.h
    m = np.zeros(len(P), bool)
    t = h * rng.uniform(2.0, 4.0) * _TS[0]
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
                # (11-14 수정) 막대의 다른 끝은 판 위의 점 → 끝이 허공에 뜬 막대가 생기지 않음
                idx = np.where(m)[0]
                b = P[rng.choice(idx)] if len(idx) else cv.rand_anchor(rng, (c + 1) % nf)
                m |= bar(cv, cv.rand_anchor(rng, c), b, _radius(rng, h))
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
            m = m | bar(cv, a, q, _radius(rng, h, 1.0, 2.5))
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
            m |= bar(cv, a, b, _radius(rng, h, 1.0, 2.0))
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
            m = m | bar(cv, sa[i], sb[j], _radius(rng, h, 1.0, 2.0))
            main = main | cs
    full = (m & cv.design) | cv.fixed
    ok, lab = connected_groups(cv, full)
    if ok:
        keep = set(np.unique(lab[cv.fixed])) - {0}
        full = np.isin(lab, list(keep))
    return full & cv.design, ok


# ---------------------------------------------------------------- 군더더기 정리 (2026-11-14 추가)
CLEAN = [True]      # False 로 두면 정리 전(이전 버전) 형상


def drop_dead_blobs(cv, occ):
    """고정부 두 곳 이상과 닿지 않는 설계 덩어리 삭제 (한 곳에만 붙은 덩어리 = 힘을 안 받는 군더더기)"""
    g, p = cv.g, cv.p
    lab, n = ndimage.label(g.eshape(occ & cv.design))
    lab = lab.ravel()
    keep = np.zeros_like(occ)
    for c in range(1, n + 1):
        m = lab == c
        near = ndimage.binary_dilation(g.eshape(m)).ravel()
        touch = set(np.unique(p.fixed_comp[near & cv.fixed])) - {0}
        if len(touch) >= 2:
            keep |= m
    return keep


def drop_floating(cv, occ):
    """고정부와 붙지 않은 조각 삭제 (FEM 에서 0 Hz 가짜 모드를 만듦)"""
    lab, n = ndimage.label(cv.g.eshape(occ | cv.fixed))
    lab = lab.ravel()
    keep = set(np.unique(lab[cv.fixed])) - {0}
    return occ & np.isin(lab, list(keep))


def smooth(cv, occ, sigma=0.6):
    """칸 단위 울퉁불퉁함을 한 번 다듬음 (가우시안 → 0.5 자르기). 연결이 끊기면 다듬기 전으로"""
    g = cv.g
    A = g.eshape(((occ & cv.design) | cv.fixed).astype(float))
    S = ndimage.gaussian_filter(A, sigma) > 0.5
    out = S.ravel() & cv.design
    if connected_groups(cv, out | cv.fixed)[0] and out.sum() > 0.5 * occ.sum():
        return out
    return occ


def clean_shape(cv, occ):
    occ = drop_dead_blobs(cv, occ)
    occ = smooth(cv, occ)
    occ = drop_dead_blobs(cv, occ)
    return fill_cavities(cv, occ | cv.fixed) & cv.design


def make_shape(p, group, idx, cv=None, max_try=12):
    """반환: occ_design (ne,) bool, meta dict"""
    cv = cv or Canvas(p)
    rng = np.random.default_rng(seed_of(group, idx))
    fams, w = zip(*cv.mix)
    for attempt in range(max_try):
        fam = fams[rng.choice(len(fams), p=np.array(w) / sum(w))]
        _TS[0] = float(rng.uniform(1.0, 2.2))
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
        for a in cv.sym_axes:
            m = m | np.flip(cv.g.eshape(m), a).ravel()
        m &= cv.design
        want_broken = rng.random() < 0.05
        if want_broken:
            occ, ok = m, connected_groups(cv, m | cv.fixed)[0]
        else:
            occ, ok = repair(cv, rng, m)
        occ = fill_cavities(cv, occ | cv.fixed) & cv.design
        if CLEAN[0] and not want_broken:
            occ = clean_shape(cv, occ)
        for a in cv.sym_axes:       # 연결 보정·정리 뒤에도 대칭 유지 (보정 막대가 한쪽에만 생기는 것 방지)
            occ = (occ | np.flip(cv.g.eshape(occ), a).ravel()) & cv.design
        vf = occ.sum() / cv.design.sum()
        if 0.05 <= vf <= 0.50 and (ok or want_broken):
            return occ, dict(group=group, idx=int(idx), family=fam, reinforced=bool(reinf), vf=float(vf), tscale=_TS[0],
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


# ---------------------------------------------------------------- 품질 지표 (걸러내기용, FEM 불필요)
def quality(cv, occ):
    """tips: 고정부에서 먼 골격 끝점 수(허공에 뜬 가지), rough: 표면 칸면 수 / 부피^(2/3) (울퉁불퉁·얇은 판 정도),
    ncomp: 설계 재료 덩어리 수, vf: 재료 비율"""
    from skimage.morphology import skeletonize
    g = cv.g
    A = g.eshape((occ & cv.design) | cv.fixed)
    sk = skeletonize(A).astype(bool)
    k = np.ones((3, 3, 3), np.int16); k[1, 1, 1] = 0
    nb = ndimage.convolve(sk.astype(np.int16), k, mode='constant')
    far = ~ndimage.binary_dilation(g.eshape(cv.fixed), iterations=3)
    tips = int((sk & (nb == 1) & far).sum())
    D = g.eshape(occ & cv.design)
    faces = sum(int(np.abs(np.diff(D.astype(np.int8), axis=a)).sum()) for a in range(3))
    vol = max(int(D.sum()), 1)
    ncomp = ndimage.label(D)[1]
    return dict(tips=tips, rough=float(faces / vol ** (2 / 3)), ncomp=int(ncomp), vf=float(D.sum() / cv.design.sum()))
