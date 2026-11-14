"""그룹별 문제 설정 그림 + 대표 무작위 형상(FEM 판정 포함) 그림 → docs/groups/*.png
python experiments/group_figures.py <data 폴더>   (datagen 결과가 있는 폴더)"""
import os, sys, json
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from skimage import measure
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
sys.path.insert(0, ROOT)
from fp08 import problems, shapes, datagen
for f in font_manager.findSystemFonts():
    if 'NotoSansCJK-Regular' in f or 'NotoSansCJK-Medium' in f:
        font_manager.fontManager.addfont(f)
plt.rcParams['font.family'] = 'Noto Sans CJK JP'
OUT = os.path.join(ROOT, 'docs', 'groups'); os.makedirs(OUT, exist_ok=True)
DATA = sys.argv[1] if len(sys.argv) > 1 else 'data'
FAM = {'A': 'A 직접 부재', 'B': 'B 트러스', 'Ctri': 'C 삼각 판', 'Cquad': 'C 사각 판', 'D': 'D 열린 껍데기'}
SMOOTH = [True]   # 그림 표면 다듬기 (데이터·FEM 은 칸 그대로)
VIEW = {'bike': (22, -58), 'tvfeet': (18, -35), 'tvped': (28, -55)}


def mirror(p, A):
    ax = 2 - p.sym_axis                      # eshape (z, y, x)
    return np.concatenate([np.flip(A, ax), A], ax)


def mesh(ax3, p, mask, color, alpha=1.0):
    g = p.grid
    A = mirror(p, g.eshape(mask)).astype(float)
    if A.sum() == 0:
        return
    A = np.pad(A, 2)
    if SMOOTH[0]:   # 표시만 다듬기: 칸 경계를 흐린 뒤(σ 0.7칸) 2배 촘촘히 보간해서 등위면 → 깍둑 모양 완화
        from scipy import ndimage
        A = ndimage.zoom(ndimage.gaussian_filter(A, 0.7), 2, order=1)
        v, f, _, _ = measure.marching_cubes(A, 0.5)
        v = v / 2.0
    else:
        v, f, _, _ = measure.marching_cubes(A, 0.5)
    v = (v - 2) * g.h                          # (z, y, x) mm, 원점 = 거울 복원 격자 시작
    o = g.origin.copy(); n = [g.nx, g.ny, g.nz]
    o[p.sym_axis] -= n[p.sym_axis] * g.h
    X, Y, Z = v[:, 2] + o[0], v[:, 1] + o[1], v[:, 0] + o[2]
    ax3.plot_trisurf(X, Y, f, Z, color=color, lw=0, alpha=alpha, shade=True)


def pts(p, idx):
    g = p.grid
    P = np.stack([g.nxc[idx], g.nyc[idx], g.nzc[idx]], 1)
    Q = P.copy(); a = p.sym_axis; c = g.origin[a]
    Q[:, a] = 2 * c - Q[:, a]
    return np.concatenate([P, Q])


def frame(ax3, p):
    g = p.grid
    lo = g.origin.copy(); hi = g.origin + np.array([g.nx, g.ny, g.nz]) * g.h
    lo[p.sym_axis] -= (hi - g.origin)[p.sym_axis]
    ax3.set_xlim(lo[0], hi[0]); ax3.set_ylim(lo[1], hi[1]); ax3.set_zlim(lo[2], hi[2])
    ax3.set_box_aspect(hi - lo)
    ax3.set_axis_off()


def product(k):
    return problems.PRODUCT_OF[k]


def setup_fig(k):
    p = problems.get(k); prod = product(k)
    fig = plt.figure(figsize=(7, 4.6)); ax3 = fig.add_subplot(111, projection='3d')
    mesh(ax3, p, p.label == 0, '#F0997B', 0.10)      # 설계 영역 (투명)
    mesh(ax3, p, p.label == 1, '#5F5E5A', 1.0)       # 고정부품
    mesh(ax3, p, p.label == 3, '#7F77DD', 1.0)       # 강체
    S = pts(p, p.supports); ax3.scatter(S[:, 0], S[:, 1], S[:, 2], s=2, c='#d9455f', depthshade=False)
    ln = p.mass_nodes if hasattr(p, 'mass_nodes') else p.load_nodes
    L = pts(p, ln); ax3.scatter(L[:, 0], L[:, 1], L[:, 2], s=6 if prod == 'bike' else 1, alpha=1 if prod == 'bike' else .25, c='#2f6fed', depthshade=False)
    frame(ax3, p); ax3.view_init(*VIEW[prod])
    fig.legend(handles=[plt.Line2D([], [], marker='s', ls='', color='#F0997B', alpha=.5, label='설계 영역(최적화가 채움)'),
                        plt.Line2D([], [], marker='s', ls='', color='#5F5E5A', label='고정부품(항상 재료)'),
                        plt.Line2D([], [], marker='s', ls='', color='#7F77DD', label='강체(폰 기둥·TV 블록)'),
                        plt.Line2D([], [], marker='o', ls='', color='#d9455f', label='지지(고정 절점)'),
                        plt.Line2D([], [], marker='o', ls='', color='#2f6fed', label='하중·질량 위치')],
               loc='lower center', ncol=3, fontsize=8, frameon=False)
    plt.subplots_adjust(0, 0.1, 1, 1)
    fig.savefig(os.path.join(OUT, f'{k}_setup.png'), dpi=110, bbox_inches='tight'); plt.close(fig)


def label_of(k, e):
    if 'f_min' in e:
        return f"{e['mass_g']:.0f} g · f_min {e['f_min']:.0f} Hz"
    return f"{e['mass_g']:.0f} g · 흔들림 {e['utop_fb']:.2f} mm"


def reps_fig(k):
    p = problems.get(k); prod = product(k); fixed = (p.label == 1) | (p.label == 3)
    R = datagen.load_fem(DATA, k)
    sidx, socc, smeta = datagen.load_shapes(DATA, k)
    meta = {int(i): m for i, m in zip(sidx, smeta)}
    rows = [(int(i), o, e, meta.get(int(i), {})) for i, o, e in zip(R['idx'], R['occ'], R['eval'])]
    picks = []
    for fam in ['A', 'B', 'Ctri', 'Cquad', 'D']:
        c = [r for r in rows if r[3].get('family') == fam and not r[3].get('reinforced')] or [r for r in rows if r[3].get('family') == fam]
        if not c:
            continue
        ok = sorted([r for r in c if r[2]['pass']], key=lambda r: r[2]['mass_g'])
        picks.append((FAM[fam], ok[0] if ok else sorted(c, key=lambda r: r[2]['mass_g'])[len(c) // 2]))
    E = sorted([r for r in rows if r[3].get('reinforced') and r[2]['pass']], key=lambda r: r[2]['mass_g'])
    if E:
        picks.append((FAM[E[0][3]['family']] + ' + E 보강', E[0]))
    passed = [r for r in rows if r[2]['pass']]
    used = {r[0] for _, r in picks}
    if passed and min(passed, key=lambda r: r[2]['mass_g'])[0] not in used:
        picks.append(('합격 중 가장 가벼운 것', min(passed, key=lambda r: r[2]['mass_g'])))
    fails = sorted([r for r in rows if not r[2]['pass']], key=lambda r: r[2]['mass_g'])
    if fails:
        picks.append(('불합격 예 (너무 약함)', fails[0]))
    picks = picks[:8]
    nc = 4; nr = (len(picks) + nc - 1) // nc
    fig = plt.figure(figsize=(4 * nc, 3.0 * nr))
    for j, (title, (i, o, e, m)) in enumerate(picks):
        ax3 = fig.add_subplot(nr, nc, j + 1, projection='3d')
        mesh(ax3, p, o & (p.label == 0), '#e8833a'); mesh(ax3, p, p.label == 1, '#5F5E5A'); mesh(ax3, p, p.label == 3, '#7F77DD')
        frame(ax3, p); ax3.view_init(*VIEW[prod])
        ax3.set_title(f"{title}\n{label_of(k, e)} · {'합격' if e['pass'] else '불합격'}", fontsize=13,
                      color='#0d7a5f' if e['pass'] else '#d9455f')
    plt.tight_layout()
    fig.savefig(os.path.join(OUT, f'{k}_shapes.png'), dpi=95, bbox_inches='tight'); plt.close(fig)
    return len(rows), sum(r[2]['pass'] for r in rows)


if __name__ == '__main__':
    st = {}
    for k in problems.GROUPS:
        setup_fig(k); st[k] = reps_fig(k); print(k, st[k], flush=True)
    json.dump(st, open(os.path.join(OUT, 'stats.json'), 'w'))
