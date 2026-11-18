"""일체형(한 번에 출력, 핀 · 볼트 없음) 자전거 폰 거치대 → 3D 프린팅 파일 (11-18)

입력: opt_int.py GRIP=3 결과 밀도 (절반 격자 2 mm, 예: rprint_g3.npy / 보정본)
출력 (OUT 접두사):
  _phoneframe.stl : 폰 정렬 좌표 (opt_int 와 같은 x', y, z')
  _print.stl      : 출력 자세 — 폰 위쪽 끝이 베드(Z=0), 핸들바 클립이 맨 위 (BUILD=x-). 뱀부 스튜디오에 그대로 올림
  _views.png      : 세 방향 그림, _report.json : 무게 · 크기 · 0.5 mm 출력 검사
고정부는 격자(2 mm)가 아니라 수식으로 0.5 mm 해상도로 다시 그림 (opt_int.py GRIP=3 과 같은 치수):
  C자 스냅 클립: 핸들바 Ø31.8 (구멍 반지름 16.1), 두께 4.5, 폭 20, 감싸는 각 230°, 입구 방향 -120°(세계 아래), 구멍 위쪽 물방울(45°)
  탄성 옆 집게: 판 가장자리에서 세운 벽 두께 1.4 mm · 길이 60 mm (x' 40..100) + 폰 앞면 걸이 턱 1.5 mm (45° 들어가는 경사)
  아래 턱: 폰 쪽 면 45° 경사 / 위쪽 멈춤 벽: 폭 76, 두께 2 (베드에 닿는 면)
  케이블타이 귀: 클립 입구 양 끝, 홈 5.4 mm (4.8 mm 타이 1개로 입구를 오므려 조임 — 회전 · 빠짐 방지)
사용: python onepiece.py RHO.npy OUT_prefix
"""
import json, os, sys, numpy as np
from scipy import ndimage
from skimage import measure

H0 = 2.0; X0, Y0, Z0 = -24., 0., -36.; NX, NY, NZ = 88, 20, 37         # opt_int 격자 (절반)
R_IN, R_OUT, CLIPW = 16.1, 20.6, 10.0
CDIR, OPEN = np.radians(-120.), np.radians(65.)
ZB, XR, PL, YJ = 24., -10., 160., 38.
JAW_X = (40., 100.); JAW_T = 1.4; JAW_GAP = 0.4; LIP = 1.5; LIP_T = 2.0
RES = float(os.environ.get('RES', '0.5'))
TAB_DEG, TAB_HW, TAB_R = 14.0, 6.0, 29.0; SLOT_R0, SLOT_HW = 22.0, 2.7          # 케이블타이 귀 · 홈
RHO_PETG = 1.27e-3                                                      # g/mm3


def grid_coords():
    xs = np.arange(-34., 156. + 1e-6, RES); ys = np.arange(-44., 44. + 1e-6, RES); zs = np.arange(-40., 44. + 1e-6, RES)
    return xs, ys, zs


def analytic(X, Y, Z):
    """고정부(있어야 할 곳)와 비울 곳 — 0.5 mm 점에서 bool"""
    r = np.hypot(X, Z); th = np.arctan2(Z, X)
    dia = lambda rr: (X < -rr / np.sqrt(2)) & (np.abs(X) + np.abs(Z) < rr * np.sqrt(2))   # 원의 45° 접점 바깥만 뾰족
    bore = (r < R_IN) | dia(R_IN)
    mouth = (np.abs(np.angle(np.exp(1j * (th - CDIR)))) < OPEN) & (r < 30)
    al = X * np.cos(CDIR) + Z * np.sin(CDIR); pp = np.abs(-X * np.sin(CDIR) + Z * np.cos(CDIR))
    entry = (al > 0) & (pp < 15.1) & (r < 46)
    ay = np.abs(Y)
    clip = ((r < R_OUT) | dia(R_OUT)) & (ay < CLIPW)
    ledge = (X > -18) & (X < -9) & (Z > ZB - 1) & (Z < 21 - X) & (ay < 16)          # 1 mm 겹침: 격자 몸체와 틈 없이
    top = (X > 149) & (X < 152) & (Z > ZB - 1) & (Z < ZB + 14) & (ay < YJ)
    yw0, yw1 = YJ + JAW_GAP, YJ + JAW_GAP + JAW_T
    inx = (X > JAW_X[0]) & (X < JAW_X[1])
    wall = inx & (ay > yw0) & (ay < yw1) & (Z > ZB - 1) & (Z < ZB + 14 + JAW_GAP + LIP_T)
    lipz0 = ZB + 14 + JAW_GAP
    lip = inx & (ay > YJ - LIP) & (ay < yw1) & (Z > lipz0) & (Z < lipz0 + LIP_T) & (Z < lipz0 + 0.6 + (ay - (YJ - LIP)))   # 위쪽 45° 들어가는 경사
    phone = (X > XR) & (X < XR + PL) & (ay < YJ) & (Z > ZB + 6) & (Z < lipz0)
    # 케이블타이 귀 (11-18): 클립 입구 양 끝에 귀 + 홈. 타이를 귀 → 핸들바 아래 → 귀로 감아 조이면 입구가 오므라들며 핸들바를 조임
    # (볼트 클램프와 같은 원리, 출력물은 한 덩어리). 홈 단면 5.4 × 2~4.7 mm (폭 4.8 mm 타이), 바깥쪽 지붕은 45° 뾰족(브리지 없음)
    tab = np.zeros_like(X, bool); slot = np.zeros_like(X, bool)
    for a_k, sg in ((CDIR + OPEN, 1), (CDIR - OPEN, -1)):
        d = sg * np.angle(np.exp(1j * (th - a_k)))                       # 입구 끝에서 닫힌 쪽으로 잰 각도
        near = (d > -0.02) & (d < np.radians(TAB_DEG)) & (ay < TAB_HW)
        tab |= near & (r > R_OUT - 0.5) & (r < TAB_R)
        slot |= near & (r > SLOT_R0) & (r < SLOT_R0 + 1.0 + (SLOT_HW - ay)) & (ay < SLOT_HW)
    solid = clip | ledge | top | wall | lip | tab
    void = bore | mouth | entry | phone | slot
    return solid, void


def body_from_rho(rho, xs, ys, zs):
    """격자 밀도(절반) → 0.5 mm 점의 값 (거울로 펼침, 삼선형 보간)"""
    v = (np.asarray(rho, float).reshape(NZ, NY, NX) > 0.5).astype(np.float32)
    full = np.concatenate([v[:, ::-1], v], 1)                            # y: -40..40
    fz = (zs[:, None, None] - (Z0 + H0 / 2)) / H0; fy = (ys[None, :, None] - (-40 + H0 / 2)) / H0; fx = (xs[None, None, :] - (X0 + H0 / 2)) / H0
    FZ, FY, FX = np.broadcast_arrays(fz, fy, fx)
    return ndimage.map_coordinates(full, [FZ.ravel(), FY.ravel(), FX.ravel()], order=1, mode='constant').reshape(FZ.shape)


def _sup(P):
    Q = np.pad(P, 1); return Q[1:-1, 1:-1] | Q[:-2, 1:-1] | Q[2:, 1:-1] | Q[1:-1, :-2] | Q[1:-1, 2:]


def fine_fill(B, void):
    """0.5 mm 에서 떠 있는 칸 아래를 채움 (x- 방향, 위층부터). 2 mm 격자의 45° 계단을 매끈한 45° 로.
    받침은 [같은 자리 + 앞뒤좌우] 중 '아래층에서 가장 가까운 재료' 쪽으로 기울여 놓음 (곧은 기둥보다 가벼움).
    옆으로 갈 때는 같은 층 옆 칸도 채워 면으로 이음. 반환: (새 B, 추가 칸 수)"""
    L = np.moveaxis(B, 2, 0)[::-1].copy(); D = ~np.moveaxis(void, 2, 0)[::-1]
    k0 = np.where(L.any((1, 2)))[0][0]; add = 0
    sh = lambda A, dy, dz: np.roll(np.roll(A, dy, 0), dz, 1)
    offs = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))
    for j in range(len(L) - 1, k0, -1):
        o = L[j] & ~_sup(L[j - 1])
        if not o.any(): continue
        dist = ndimage.distance_transform_edt(~L[j - 1]) if L[j - 1].any() else np.full(L[j - 1].shape, 1e9)
        cost = []
        for dy, dz in offs:   # 후보 자리(현재 칸에서 dy,dz 만큼)의 거리; 못 쓰는 자리는 큰 값
            dd = sh(dist, -dy, -dz); ok = sh(D[j - 1], -dy, -dz) & (sh(D[j], -dy, -dz) if (dy, dz) != (0, 0) else True)
            cost.append(np.where(ok, dd + 0.3 * ((dy, dz) != (0, 0)), 1e12))
        cost = np.array(cost); best = cost.argmin(0); good = cost.min(0) < 1e11
        for q, (dy, dz) in enumerate(offs):
            sel = o & good & (best == q)
            if not sel.any(): continue
            c = sh(sel, dy, dz)
            add += int((c & ~L[j - 1]).sum()); L[j - 1] |= c
            if (dy, dz) != (0, 0): add += int((c & ~L[j]).sum()); L[j] |= c
    return np.moveaxis(L[::-1], 0, 2), add


def print_check(B):
    """B(z,y,x) bool 을 x- 방향(폰 위쪽 끝이 베드)으로 쌓을 때 떠 있는 칸 (0.5 mm, 45°, 브리지 없음)"""
    L = np.moveaxis(B, 2, 0)[::-1]; nzl = np.where(L.any((1, 2)))[0]; L = L[nzl[0]:]
    P = np.zeros_like(L); P[0] = L[0]
    for j in range(1, len(L)):
        Q = np.pad(P[j - 1], 1)
        P[j] = L[j] & (Q[1:-1, 1:-1] | Q[:-2, 1:-1] | Q[2:, 1:-1] | Q[1:-1, :-2] | Q[1:-1, 2:])
    need = L & ~P
    return int(need.sum()), float(need.sum() * RES ** 3 * RHO_PETG), len(L) * RES, float(L[0].sum() * RES * RES)


def write_stl(path, verts, faces, title):
    tri = verts[faces].astype(np.float64)
    if np.einsum('ij,ij->i', tri[:, 0], np.cross(tri[:, 1], tri[:, 2])).sum() < 0:   # 바깥쪽 법선이 되도록 감는 방향 맞춤
        faces = faces[:, [0, 2, 1]]; tri = verts[faces].astype(np.float64)
    tri = tri.astype(np.float32)
    nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]); nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-12
    data = np.zeros(len(faces), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); data['n'], data['v'] = nrm, tri
    with open(path, 'wb') as fo:
        fo.write(title.encode('ascii', 'replace')[:80].ljust(80, b' ')); fo.write(np.uint32(len(faces)).tobytes()); fo.write(data.tobytes())
    return float(abs(np.einsum('ij,ij->i', tri[:, 0], np.cross(tri[:, 1], tri[:, 2])).sum() / 6))


def main(rho_path, out):
    rho = np.load(rho_path).ravel()
    xs, ys, zs = grid_coords()
    Z, Y, X = np.meshgrid(zs, ys, xs, indexing='ij')
    solid, void = analytic(X, Y, Z)
    # 격자 고정부(클립 · 턱 · 벽 · 집게 뿌리)는 수식으로 다시 그리므로 격자 몸체에서는 설계 영역만 씀
    meta = np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'grid_meta_g3.npz'))
    design = meta['design'].astype(bool); body_rho = np.where(design, rho, 0.)
    band = meta['solid'].astype(bool) & (meta['zc'] < ZB + 4) & (meta['zc'] > ZB) & (meta['xc'] > 56) & (meta['xc'] < 74)   # 판 띠(고정, 격자 그대로)
    body_rho = np.where(band, 1.0, body_rho)
    F = body_from_rho(body_rho, xs, ys, zs)
    F = ndimage.gaussian_filter(F, 0.6)                                 # 격자 계단을 약간 매끈하게 (0.3 mm)
    B = ((F > 0.5) | solid) & ~void
    lab, n = ndimage.label(B); sizes = ndimage.sum(B, lab, range(1, n + 1)); B = lab == (1 + int(np.argmax(sizes)))   # 가장 큰 덩어리 하나
    n0, g0, _, _ = print_check(B)
    B, nadd = fine_fill(B, void)                                         # 0.5 mm 에서 마지막 보정 (계단 → 45°)
    nneed, gneed, height, bed = print_check(B)
    vol_mm3 = float(B.sum() * RES ** 3)
    verts, faces, _, _ = measure.marching_cubes(np.pad(B.astype(np.float32), 1), 0.5, spacing=(RES,) * 3)
    verts = verts - RES                                                  # pad 보정
    P = np.c_[verts[:, 2] + xs[0], verts[:, 1] + ys[0], verts[:, 0] + zs[0]]   # (x', y, z')
    faces_o = faces[:, ::-1]                                             # (z,y,x)->(x,y,z) 뒤집힘 보정
    v1 = write_stl(out + '_phoneframe.stl', P, faces_o, 'FormProof one-piece (phone frame)')
    xmax = P[:, 0].max(); Pp = np.c_[P[:, 1], P[:, 2], xmax - P[:, 0]]   # 출력 자세: Z = 폰 위쪽 끝에서 잰 높이
    Pp[:, 0] -= Pp[:, 0].min(); Pp[:, 1] -= Pp[:, 1].min()
    write_stl(out + '_print.stl', Pp, faces_o, 'FormProof one-piece (print pose)')
    rep = dict(mass_g=round(v1 * RHO_PETG, 1), voxel_mass_g=round(vol_mm3 * RHO_PETG, 1), size_print_mm=[round(float(v), 1) for v in Pp.max(0) - Pp.min(0)],
               print_height_mm=round(float(Pp[:, 2].max() - Pp[:, 2].min()), 1), bed_contact_mm2=round(bed, 0), overhang_before_fine_fill_g=round(g0, 2), fine_fill_added_g=round(nadd * RES ** 3 * RHO_PETG, 2),
               overhang_cells_0p5mm=nneed, overhang_g=round(gneed, 2),
               rule='45deg, no bridge, build x- (phone top on bed)', res_mm=RES, triangles=int(len(faces)), rho=os.path.basename(rho_path))
    json.dump(rep, open(out + '_report.json', 'w'), indent=1, ensure_ascii=False)
    try:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 3, figsize=(14, 4.6))
        ax[0].imshow(B.any(1), origin='lower', extent=[xs[0], xs[-1], zs[0], zs[-1]], cmap='Greys'); ax[0].set_title("side (x'-z')"); ax[0].set_xlabel("x' mm"); ax[0].set_ylabel("z' mm")
        ax[1].imshow(B.any(0), origin='lower', extent=[xs[0], xs[-1], ys[0], ys[-1]], cmap='Greys'); ax[1].set_title("plate view (x'-y)"); ax[1].set_xlabel("x' mm")
        ax[2].imshow(B.any(2), origin='lower', extent=[ys[0], ys[-1], zs[0], zs[-1]], cmap='Greys'); ax[2].set_title("end view (y-z')"); ax[2].set_xlabel('y mm')
        fig.suptitle(f"one-piece  {rep['mass_g']} g   print height {rep['print_height_mm']} mm   overhang(0.5 mm check) {rep['overhang_g']} g", fontsize=10)
        fig.tight_layout(); fig.savefig(out + '_views.png', dpi=100); plt.close(fig)
    except Exception as e: rep['views_error'] = str(e)
    print(json.dumps(rep, ensure_ascii=False)); return rep


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
