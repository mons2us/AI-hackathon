"""일체형 거치대 프레임 형상 생성기 (규칙 + 연속 변수) — gen_int.py 를 계열·변수로 정리·확장한 것

좌표: opt_int.py 와 같은 폰 정렬 좌표 (x' 폰 길이 방향, z' 받침판 법선, y 핸들바 축, 절반 모델 y >= 0), 2 mm 격자.
클램프 링 중심 (0, 0), 링 접촉부 반지름 16.1–20.6 mm. 받침판 z' 24–30.

몸체 = 막대(부재) 여러 개. 부재 = 측면 경로(점 2개 이상, 직선 또는 곡선) + 단면(종류, 두께 t, 반폭 w).
몸체가 이어야 할 곳(목표) — 폰 잡는 방식 GRIP 에 따라 위치가 다름 (opt_int.py 의 고정 부품과 같은 자리):
  mid : 판 가운데  (GRIP 0: 4면 판의 옆 턱 / 1·2: 스프링 집게 하우징)
  bot : 판 아래 끝 (GRIP 0: 받침 턱 / 1·2: 아래 걸이)
  top : 판 위 끝   (GRIP 0·1: 위쪽 받침점 / 2: 위쪽 슬라이드 레일)
계열(팔 구조) 7가지 — 아래 FAMILIES. 각 계열은 연속 변수(링에서 나오는 각도, 꺾이는 점, 단면 크기 등)를 가짐.

    rng = np.random.default_rng(0)
    occ, prm = sample(rng, meta, grip=2)               # 무작위 계열·변수
    occ, prm = sample(rng, meta, grip=2, family='truss')
    occ = build(prm, meta)                              # 같은 변수 -> 같은 형상 (재현·최적화용)

반환 occ: 설계 영역 요소의 점유 (len = 전체 요소 수, bool). 고정 부품(solid)은 포함 안 함 (opt_int 가 붙임).
prm: 계열·변수 사전 (JSON 저장 가능) — 형상 AI / 변수 최적화의 입력.
"""
import math
import numpy as np
from scipy import ndimage

RING_R = 19.0                          # 부재가 링에 붙는 반지름 (접촉부 16.1–20.6 가운데)
SECTIONS = ('rect', 'round', 'channel', 'ibeam')
SECTION_KO = {'rect': '사각', 'round': '둥근 관', 'channel': '양옆 벽(ㄷ자)', 'ibeam': 'I자'}
FAMILIES = {
    'straight': '곧은 팔: 링 → 판 가운데, 판 밑 보로 위 끝까지',
    'truss': '트러스: 위 팔 + 아래 사재 + 수직재',
    'vee': 'V자: 링 두 곳에서 나온 두 팔이 판 가운데에서 만남',
    'arch': '아치(구스넥): 링에서 위 끝까지 곡선 하나 + 짧은 기둥',
    'spine': '척추: 판 밑을 따라 긴 보 + 링에서 버팀대 여러 개',
    'yfork': 'Y자: 링에서 한 줄기가 나와 갈라짐',
    'plate': '판형: 판 밑을 넓은 띠로 받치고 링과 짧게 연결',
}
FAMILY_KO = {'straight': '곧은 팔', 'truss': '트러스', 'vee': 'V자', 'arch': '아치(구스넥)', 'spine': '척추',
             'yfork': 'Y자', 'plate': '판형'}


def targets(grip):
    """몸체가 닿아야 할 점 (x', z') — opt_int.py 고정 부품 아랫면 근처 (부재가 겹쳐 붙도록 1–2 mm 안쪽)"""
    if grip == 0:
        return dict(mid=(65.0, 25.0), bot=(-6.0, 25.0), top=(133.0, 25.0))
    if grip == 1:
        return dict(mid=(65.0, 19.0), bot=(-12.0, 25.0), top=(133.0, 25.0))
    return dict(mid=(65.0, 19.0), bot=(-12.0, 25.0), top=(126.0, 13.0))


def ring_pt(deg):
    a = math.radians(deg)
    return (RING_R * math.cos(a), RING_R * math.sin(a))


def _spline(ctrl, n=24):
    """Catmull-Rom (look.py 와 같은 방식) — 곡선 부재"""
    P = [np.asarray(p, float) for p in ctrl]
    P = [P[0] - (P[1] - P[0])] + P + [P[-1] + (P[-1] - P[-2])]
    out = []
    per = max(2, n // (len(ctrl) - 1))
    for i in range(1, len(P) - 2):
        for s in np.linspace(0, 1, per + 1)[:-1]:
            p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s ** 2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * s ** 3))
    out.append(P[-2])
    return [tuple(map(float, p)) for p in out]


def _lerp(a, b, s):
    return (a[0] + (b[0] - a[0]) * s, a[1] + (b[1] - a[1]) * s)


# ------------------------------------------------------------------ 계열별 규칙: 변수 -> 부재 목록
def _members(prm, T):
    """prm(계열·변수) -> 부재 [(경로 점들, 단면 배율)] (단면 배율: 주부재 1, 보조 부재 prm['sub'])"""
    f, v = prm['family'], prm['v']
    sub = prm['sub']
    M = []
    bot = (ring_pt(v['a_bot']), T['bot'])                         # 링 -> 아래 끝 (모든 계열 공통: 떠 있으면 안 됨)
    if f == 'straight':
        knee = (v['knee_x'], v['knee_z'])
        M += [([ring_pt(v['a_up']), knee, T['mid']], 1.0), ([T['mid'], T['top']], sub)]
    elif f == 'truss':
        lo = _lerp(T['mid'], T['top'], v['brace_s'])
        M += [([ring_pt(v['a_up']), T['mid']], 1.0), ([T['mid'], T['top']], 1.0),
              ([ring_pt(v['a_lo']), (v['low_x'], v['low_z']), lo], sub)]
        for k in range(int(v['n_vert'])):                           # 수직재: 위 보와 아래 사재 사이
            s = (k + 1) / (int(v['n_vert']) + 1)
            a = _lerp(T['mid'], lo, s)
            b = _lerp((v['low_x'], v['low_z']), lo, s)
            M.append(([a, b], sub * 0.8))
    elif f == 'vee':
        apex = (T['mid'][0] + v['apex_dx'], T['mid'][1] - v['apex_dz'])
        M += [([ring_pt(v['a_up']), apex], 1.0), ([ring_pt(v['a_lo']), apex], 1.0), ([apex, T['mid']], 1.0),
              ([apex, T['top']], sub)]
    elif f == 'arch':
        c1 = (v['c1_x'], v['c1_z'])
        c2 = (v['c2_x'], v['c2_z'])
        pth = _spline([ring_pt(v['a_up']), c1, c2, T['top']])
        M.append((pth, 1.0))
        near = min(pth, key=lambda p: (p[0] - T['mid'][0]) ** 2 + (p[1] - T['mid'][1]) ** 2)
        M.append(([near, T['mid']], sub))
    elif f == 'spine':
        z = v['spine_z']
        sp0, sp1 = (T['bot'][0] + 6, z), (T['top'][0], min(z, T['top'][1]) if T['top'][1] < 20 else z)
        M += [([sp0, (T['mid'][0], z), sp1], 1.0), ([(T['mid'][0], z), T['mid']], sub), ([sp1, T['top']], sub)]
        for k in range(int(v['n_strut'])):
            deg = v['a_up'] - k * v['strut_da']
            xs = sp0[0] + (sp1[0] - sp0[0]) * (0.15 + 0.6 * k / max(1, int(v['n_strut']) - 1 if int(v['n_strut']) > 1 else 1))
            M.append(([ring_pt(deg), (xs, z)], sub))
    elif f == 'yfork':
        node = (v['node_x'], v['node_z'])
        M += [([ring_pt(v['a_up']), node], 1.0), ([node, T['mid']], 1.0), ([node, T['top']], sub)]
    elif f == 'plate':
        z0 = v['band_z']
        M += [([(T['bot'][0] + 4, z0), T['top'] if T['top'][1] < 20 else (T['top'][0], z0)], 1.0),
              ([ring_pt(v['a_up']), (v['knee_x'], z0)], 1.0), ([(T['mid'][0], z0), T['mid']], sub)]
    else:
        raise ValueError(f)
    M.append(([bot[0], bot[1]], sub))
    for k in range(int(prm.get('n_web', 0))):                       # 보강 웹: 부재 두 개의 중간점끼리
        i, j, si, sj = prm['webs'][k]
        pi, pj = M[int(i) % len(M)][0], M[int(j) % len(M)][0]
        a = pi[min(len(pi) - 1, int(si * (len(pi) - 1)))] if len(pi) > 2 else _lerp(pi[0], pi[-1], si)
        b = pj[min(len(pj) - 1, int(sj * (len(pj) - 1)))] if len(pj) > 2 else _lerp(pj[0], pj[-1], sj)
        M.append(([a, b], sub * 0.7))
    return M


# ------------------------------------------------------------------ 계열별 변수 범위 (균일 샘플)
RANGES = {
    'common': dict(t=(5.0, 12.0), w=(5.0, 14.0), sub=(0.55, 1.0)),
    'straight': dict(a_up=(40, 100), a_bot=(90, 150), knee_x=(20, 50), knee_z=(5, 22)),
    'truss': dict(a_up=(40, 100), a_lo=(-50, 15), a_bot=(90, 150), low_x=(30, 70), low_z=(-25, 0),
                  brace_s=(0.3, 1.0), n_vert=(0, 3.99)),
    'vee': dict(a_up=(50, 100), a_lo=(-40, 20), a_bot=(90, 150), apex_dx=(-15, 10), apex_dz=(4, 18)),
    'arch': dict(a_up=(10, 80), a_bot=(90, 150), c1_x=(25, 55), c1_z=(-15, 15), c2_x=(70, 105), c2_z=(-5, 18)),
    'spine': dict(a_up=(40, 100), a_bot=(90, 150), spine_z=(14, 20), n_strut=(1, 3.99), strut_da=(25, 60)),
    'yfork': dict(a_up=(0, 80), a_bot=(90, 150), node_x=(30, 60), node_z=(-5, 15)),
    'plate': dict(a_up=(40, 100), a_bot=(90, 150), band_z=(17, 21), knee_x=(10, 40)),
}


def draw(rng, family=None, n_web_max=2):
    f = family or rng.choice(list(FAMILIES))
    v = {k: float(rng.uniform(*r)) for k, r in RANGES[f].items()}
    c = {k: float(rng.uniform(*r)) for k, r in RANGES['common'].items()}
    nw = int(rng.integers(0, n_web_max + 1))
    return dict(family=str(f), v=v, t=c['t'], w=c['w'], sub=c['sub'], section=str(rng.choice(SECTIONS)),
                n_web=nw, webs=[[int(rng.integers(0, 6)), int(rng.integers(0, 6)), float(rng.uniform(.2, .8)),
                                 float(rng.uniform(.2, .8))] for _ in range(nw)])


# ------------------------------------------------------------------ 격자로 (부재 = 경로를 따라 쓴 단면)
def _seg_dist(P, a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ab = b - a
    t = np.clip(((P - a) @ ab) / (ab @ ab + 1e-9), 0, 1)
    return np.linalg.norm(P - (a + t[:, None] * ab), axis=1)


def _member_mask(P, y, path, t, w, section):
    """측면 거리 d(경로까지), 핸들바축 y -> 단면 안쪽인가"""
    d = np.full(len(P), np.inf)
    for a, b in zip(path[:-1], path[1:]):
        d = np.minimum(d, _seg_dist(P, a, b))
    if section == 'rect':
        return (d <= t / 2) & (y <= w)
    if section == 'round':                                         # 지름 = 2w 기준 관 (t 는 무시하지 않고 최소 두께)
        r = max(t, w) / 2 + w / 2
        return np.sqrt(d ** 2 + y ** 2) <= r * 0.75
    if section == 'channel':                                       # 양옆 벽 + 바닥: 가운데 비움 (gen_int 'side')
        wall = max(4.0, w * 0.4)
        return (d <= t / 2) & (y <= w) & ((y >= w - wall) | (d >= t / 2 - 3.0))
    if section == 'ibeam':                                         # 위아래 날개 + 가는 복부
        fl = max(2.5, t * 0.3)
        web = max(3.0, w * 0.35)
        return (d <= t / 2) & (y <= w) & ((d >= t / 2 - fl) | (y <= web))
    raise ValueError(section)


def build(prm, meta, grip=None):
    """변수 -> 점유 (설계 영역 안, 링·고정 부품과 이어진 덩어리만). meta: opt_int MODE=meta 의 npz 또는 dict"""
    xc, yc, zc = meta['xc'], meta['yc'], meta['zc']
    design, solid = meta['design'].astype(bool), meta['solid'].astype(bool)
    grip = prm.get('grip', grip)
    T = targets(grip)
    P = np.c_[xc, zc]
    occ = np.zeros(len(xc), bool)
    for path, scale in _members(prm, T):
        occ |= _member_mask(P, yc, path, prm['t'] * (scale ** 0.5), prm['w'] * scale, prm['section'])
    occ &= design
    nz, ny, nx = int(meta['nz']), int(meta['ny']), int(meta['nx'])
    lab, n = ndimage.label((occ | solid).reshape(nz, ny, nx))
    lab = lab.ravel()
    rr = np.sqrt(xc ** 2 + zc ** 2)
    contact = solid & (rr >= 16.1) & (rr < 20.6)
    keep = np.unique(lab[contact & (lab > 0)])
    occ &= np.isin(lab, keep)
    return occ


def check(occ, meta, grip):
    """유효성: 링과 세 목표(가운데·아래·위 고정 부품)가 한 덩어리로 이어졌는가 + 최소 두께(1칸짜리 막대 없음)"""
    xc, yc, zc = meta['xc'], meta['yc'], meta['zc']
    solid = meta['solid'].astype(bool)
    nz, ny, nx = int(meta['nz']), int(meta['ny']), int(meta['nx'])
    lab, _ = ndimage.label((occ | solid).reshape(nz, ny, nx))
    lab = lab.ravel()
    rr = np.sqrt(xc ** 2 + zc ** 2)
    ring = lab[solid & (rr >= 16.1) & (rr < 20.6) & (lab > 0)]
    if not len(ring):
        return False, 'ring'
    L = np.bincount(ring).argmax()
    T = targets(grip)
    for k, (tx, tz) in T.items():
        near = solid & (np.abs(xc - tx) < 12) & (np.abs(zc - tz) < 8)
        if near.any() and not (lab[near] == L).any():
            return False, k
    return True, 'ok'


def sample(rng, meta, grip=2, family=None, tries=20):
    """유효한 형상 하나 (변수 다시 뽑기 최대 tries 번)"""
    for _ in range(tries):
        prm = draw(rng, family)
        prm['grip'] = int(grip)
        occ = build(prm, meta)
        ok, why = check(occ, meta, grip)
        if ok and occ.sum() >= 30:
            return occ, prm
    return None, prm
