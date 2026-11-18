"""FDM(층층이 쌓는 3D 프린터, 예: 뱀부랩) 출력 가능성 검사 · 보정 — opt_int.py 의 출력 필터와 같은 규칙

규칙 (opt_int.py am_forward 와 같음):
  * 출력 방향: 폰 닿는 받침판 윗면(z' = 30)을 베드에 두고 -z' 방향으로 쌓음. 층 0 = 요소 k = KTOP(=32), 층 n = k = KTOP - n
  * 한 칸(2 mm)이 출력되려면 바로 아래층의 [같은 자리 + 앞뒤좌우 4칸] 중 하나에 재료가 있어야 함
    → 한 층(2 mm)마다 옆으로 최대 1칸(2 mm) = 오버행 45° (FDM 일반 기준, 서포트 없이 출력되는 각도)
  * y = 0 은 대칭면(절반 모델) → 거울로 이웃을 봄

검사 결과
  * overhang : 아래가 비어 있는 칸 (그 층에서 바로 새로 떠 있는 칸)
  * bridge   : overhang 중 같은 층 같은 줄(x 또는 y)로 양쪽 끝이 받쳐진 칸이 BRIDGE_MM 이내 → 브리지로 출력 가능
  * need_support : bridge 로도 안 되는 overhang + 그 위로 이어 쌓인 칸 (서포트 없으면 출력 실패)
보정 (make_self_supporting): need_support 칸 아래로 45° 받침(원뿔 모양)을 채워 베드 또는 기존 재료까지 이어 줌
  → 재료가 늘어나므로 보정 뒤에는 opt_int.py MODE=eval 로 다시 판정해야 함

    import printability as pr
    meta = pr.load_meta('../data/grid_meta.npz')
    rep = pr.check(rho, meta)                 # rho: 전체 요소(65120) 밀도 또는 0/1
    rho2, add = pr.make_self_supporting(rho, meta)

명령줄:  python printability.py 형상.npy [형상2.npy ...]   (npz 묶음은 packbits 'occ' 또는 키 이름 지정 key=...)
근거: Langelaar (2017) "An additive manufacturing filter for topology optimization of print-ready designs",
      Struct. Multidisc. Optim. 55(3), 871–883. 45° 기준: Bambu Lab Wiki "Overhang" (45° 넘으면 서포트 권장)
      https://wiki.bambulab.com/en/filament-acc/filament/print-quality/overhang
"""
import json, os, sys
import numpy as np

H = 2.0                    # 격자 (mm)
BRIDGE_MM = float(os.environ.get('BRIDGE_MM', '0'))    # 브리지(양쪽이 받쳐진 수평 구간) 허용 길이. 0 = 브리지 없음(가장 보수적, 11-18 사용자 요청) — 모든 면이 45° 이내
ZB = 24.0                  # 받침판 아랫면 z' (opt_int.py 와 같음)


def load_meta(path):
    d = np.load(path)
    m = {k: d[k] for k in d.files}
    m['nx'], m['ny'], m['nz'] = int(m['nx']), int(m['ny']), int(m['nz'])
    m['ktop'] = int((ZB + 6 - float(m['origin'][2])) / H) - 1
    return m


def meta_from(gm):
    """opt_int._gen_meta() / gen_frame 이 쓰는 dict(xc, yc, zc, design, solid, nx, ny, nz) -> 이 모듈의 meta
    (void 가 없으면 = 설계 영역도 고정 부품도 아닌 곳, opt_int 의 design = ~(void | solid) 와 같음)"""
    if 'ktop' in gm and 'void' in gm: return gm
    m = dict(gm); m['nx'], m['ny'], m['nz'] = int(gm['nx']), int(gm['ny']), int(gm['nz'])
    d, s_ = np.asarray(gm['design'], bool), np.asarray(gm['solid'], bool)
    m['design'], m['solid'] = d, s_
    m['void'] = np.asarray(gm['void'], bool) if 'void' in gm else ~(d | s_)
    zc = np.asarray(gm['zc'], float); z0 = float(zc.min()) - H / 2
    m['ktop'] = int((ZB + 6 - z0) / H) - 1
    return m


def _occ(rho, meta):
    r = np.asarray(rho, float).ravel()
    occ = (r > 0.5) | meta['solid'].astype(bool)
    occ &= ~meta['void'].astype(bool)
    return occ


def layers(occ, meta):
    """(층, y, x) bool, 층 0 = 베드 쪽"""
    v = occ.reshape(meta['nz'], meta['ny'], meta['nx'])
    return v[meta['ktop']::-1].copy(), v[meta['ktop'] + 1:].any()


def support(L):
    """L(이전 층)이 받쳐 주는 칸: 같은 자리 + 앞뒤좌우, y=0 은 거울"""
    P = np.pad(L, 1)
    P[0, 1:-1] = L[0]                       # y=-1 = y=0 의 거울
    return P[1:-1, 1:-1] | P[:-2, 1:-1] | P[2:, 1:-1] | P[1:-1, :-2] | P[1:-1, 2:]


def _bridgeable(over, sup_cells, nb):
    """over 칸 중 같은 줄로 양쪽이 받쳐진 구간 길이 <= nb 칸"""
    ok = np.zeros_like(over)
    for axis in (0, 1):
        A = np.moveaxis(over, axis, 0); S = np.moveaxis(sup_cells, axis, 0); O = np.moveaxis(ok, axis, 0)
        for line in range(A.shape[1]):
            a = A[:, line]; s = S[:, line]; n = len(a); i = 0
            while i < n:
                if not a[i]: i += 1; continue
                j = i
                while j < n and a[j]: j += 1
                left = i > 0 and s[i - 1]
                right = j < n and s[j]
                if axis == 0 and i == 0:        # y 방향: y=0 대칭면 너머는 거울 → 반대쪽 끝도 같은 거리
                    left = right; length = 2 * (j - i)
                else:
                    length = j - i
                if left and right and length <= nb: O[i:j, line] = True
                i = j
    return ok


def _fixed(meta):
    return meta['solid'].astype(bool) & ~meta['void'].astype(bool)


def check(rho, meta, bridge_mm=BRIDGE_MM, fixed_ok=False):
    """fixed_ok=True: 고정 부품(클램프 링 · 집게 하우징 · 레일 · 걸이)은 출력된 것으로 봄 (opt_int.py 출력 필터와 같은 가정)
    → 설계 영역(몸체 팔 · 받침판)만의 출력 가능성. False: 고정 부품까지 포함한 실제 몸체 전체"""
    occ = _occ(rho, meta)
    X, below_bed = layers(occ, meta)
    F, _ = layers(_fixed(meta), meta)
    nb = int(round(bridge_mm / H))
    P = np.zeros_like(X); P[0] = X[0]
    over = np.zeros_like(X); bridge = np.zeros_like(X)
    for j in range(1, X.shape[0]):
        s = support(P[j - 1])
        o = X[j] & ~s
        if fixed_ok: o &= ~F[j]
        b = _bridgeable(o, X[j] & ~o, nb) if o.any() else np.zeros_like(o)
        over[j] = o; bridge[j] = b
        P[j] = X[j] & (s | b | (F[j] if fixed_ok else False))
    need = X & ~P
    mass_g = lambda c: float(c.sum() * H ** 3 * 1.27e-3 * 2)          # PETG 1.27 g/cm3, 양쪽(대칭) 합
    rep = dict(cells=int(X.sum()), overhang=int(over.sum()), bridge=int(bridge.sum()),
               need_support=int(need.sum()), need_support_g=round(mass_g(need), 2), total_g=round(mass_g(X), 1),
               need_support_pct=round(100 * need.sum() / max(X.sum(), 1), 2), bed_contact_mm2=int(X[0].sum() * H * H * 2),
               below_bed=bool(below_bed), printable=bool(need.sum() == 0 and not below_bed),
               worst_layers=[int(j) for j in np.argsort(-need.sum((1, 2)))[:5] if need[j].any()])
    rep['need_support_in_fixed_parts'] = int((need & F).sum())        # 고정 부품(클램프 링 · 집게 · 레일) 자체
    rep['need_support_in_design'] = int((need & ~F).sum())
    return rep, dict(X=X, P=P, over=over, bridge=bridge, need=need)


def _fill_pass(X, D, F, nb, fixed_ok):
    ny, nx = X.shape[1:]; added = 0; stuck = []
    off = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))
    for j in range(X.shape[0] - 1, 0, -1):
        s = support(X[j - 1]); o = X[j] & ~s
        if fixed_ok: o &= ~F[j]
        if not o.any(): continue
        o &= ~_bridgeable(o, X[j] & ~o, nb)
        s2 = support(X[j - 2]).astype(int) if j >= 2 else np.ones((ny, nx), int)
        for y, x in zip(*np.where(o)):
            best = None
            for dy, dx in off:
                yy, xx = y + dy, x + dx
                if yy == -1: yy = 0                                   # 대칭면 거울
                if 0 <= yy < ny and 0 <= xx < nx and D[j - 1, yy, xx]:
                    sc = s2[yy, xx] * 10 + 5 * (dy == 0 and dx == 0)
                    if best is None or sc > best[0]: best = (sc, yy, xx)
            if best is None: stuck.append((j, y, x)); continue
            yy, xx = best[1], best[2]
            if (yy, xx) != (y, x):                                    # 옆 칸으로 내려갈 때: 같은 층 옆 칸도 채워 면으로 이어지게
                if not D[j, yy, xx]: stuck.append((j, y, x)); continue   # (모서리로만 닿으면 FEM 에서 경첩처럼 약함)
                if not X[j, yy, xx]: X[j, yy, xx] = True; added += 1
            if not X[j - 1, yy, xx]: X[j - 1, yy, xx] = True; added += 1
    return added, stuck


def make_self_supporting(rho, meta, bridge_mm=BRIDGE_MM, fixed_ok=True, passes=6):
    """떠 있는 칸 아래에 받침 칸을 채워 45° 규칙을 만족시킴 (설계 영역 안에서만, 비울 곳 · 고정 부품은 그대로)
    위층(베드에서 먼 쪽)부터 내려오며: 아래층 [같은 자리 + 앞뒤좌우] 가 비어 있으면 그중 '그 아래층에 받침이 가장 많은 자리' 하나를 채움
    → 받침이 기존 재료 쪽으로 45° 로 기울며 합쳐짐(곧은 기둥보다 가벼움).
    아래가 '비울 곳'(받침판 바깥 z' > 24 등)이라 채울 수 없는 칸은 깎아 내고 다시 채움 (보통 형상당 0–2 칸).
    반환: (0/1 밀도(설계 영역), 추가 칸 수, 깎은 칸 수)"""
    design = meta['design'].astype(bool)
    occ = _occ(rho, meta)
    nz, ny, nx, kt = meta['nz'], meta['ny'], meta['nx'], meta['ktop']
    X, _ = layers(occ, meta); D, _ = layers(design, meta); F, _ = layers(_fixed(meta), meta)
    nb = int(round(bridge_mm / H)); added = 0; trimmed = 0
    for _ in range(passes):
        a, stuck = _fill_pass(X, D, F, nb, fixed_ok); added += a
        if not stuck: break
        for j, y, x in stuck:
            if D[j, y, x] and X[j, y, x]: X[j, y, x] = False; trimmed += 1
    v = occ.reshape(nz, ny, nx).copy(); v[kt::-1] = X; out = v.reshape(-1) & (design | meta['solid'].astype(bool))
    return np.where(design, out, 0.).astype(float), added, trimmed


def _unpack(a, meta):
    """packbits 한 줄 -> 전체 요소 밀도. 전체(65120) 또는 설계 영역만(didx, label3 학습 데이터) 둘 다"""
    ne = meta['nx'] * meta['ny'] * meta['nz']; di = meta['didx']; b = np.unpackbits(a)
    if len(b) >= ne and len(b) - ne < 8: return b[:ne].astype(float)
    r = np.zeros(ne); r[di] = b[:len(di)]; return r


def _load_many(path, meta, key=None, limit=None):
    if path.endswith('.npy'):
        return [(os.path.basename(path), np.load(path).ravel())]
    d = np.load(path, allow_pickle=False); out = []; ne = meta['nx'] * meta['ny'] * meta['nz']
    keys = [key] if key else d.files
    for k in keys:
        a = d[k]
        if a.dtype == np.uint8 and a.ndim == 1: out.append((k, _unpack(a, meta)))
        elif a.dtype == np.uint8 and a.ndim == 2:
            for q in range(len(a) if limit is None else min(limit, len(a))): out.append(('%s[%d]' % (k, q), _unpack(a[q], meta)))
        elif a.ndim == 1 and a.size == ne: out.append((k, a.astype(float)))
    return out


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    meta = load_meta(os.environ.get('META', os.path.join(here, '..', 'data', 'grid_meta.npz')))
    for p in sys.argv[1:]:
        key = None
        if '::' in p: p, key = p.split('::')
        for nm, r in _load_many(p, meta, key, int(os.environ['LIMIT']) if os.environ.get('LIMIT') else None):
            rep, _ = check(r, meta, fixed_ok=os.environ.get('FIXED_OK') == '1')
            print(json.dumps(dict(name=nm, **rep), ensure_ascii=False))
