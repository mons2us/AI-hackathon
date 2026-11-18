"""'화면 각도 자유' 그룹 설명 그림 (11-14): 폰 기둥 높이를 왜 60 mm 로, 왜 '위에서 깎기' 형상을 추가하나.
사용: python experiments/free_angle_figure.py <10_입력_1차설계 폴더>   (기둥 22·110 mm 의 금지 공간을 그리려고 10 코드를 씀)"""
import os, sys, json
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
SRC = os.path.abspath(sys.argv[1]); sys.path.insert(0, SRC); sys.path.insert(0, ROOT)
from formproof_input.templates import bike_mount, library
from formproof_input.compile import Problem as P10
from fp08 import problems, shapes, datagen, labels
plt.rcParams['font.family'] = ['Noto Sans CJK KR', 'Noto Sans CJK JP', 'DejaVu Sans']; plt.rcParams['axes.unicode_minus'] = False
OUT = os.path.join(ROOT, 'docs', 'groups')


def keepout(post_h):
    pr = dict(library.BY_ID['T01']['params'], requirements=('free_angle',), post_h=post_h)
    return np.asarray(P10(bike_mount.build_spec(pr, 'T01')).keepout, bool)


def side(p, occ=None, ko=None):
    """옆모습(y 방향으로 겹쳐 봄): 0 빈곳 1 설계영역 2 금지공간 3 고정부품 4 재료 5 금지공간∩고정(충돌)"""
    g = p.grid; L = g.eshape(p.label)
    img = np.zeros((g.nz, g.nx), int)
    img[(L == 0).any(1)] = 1
    if ko is not None:
        img[g.eshape(ko).any(1)] = 2
    if occ is not None:
        img[g.eshape(occ).any(1)] = 4
    fx = ((L == 1) | (L == 3)).any(1)
    img[fx] = 3
    if ko is not None:
        img[(g.eshape(ko) & ((L == 1) | (L == 3))).any(1)] = 5
    return img


cmap = ListedColormap(['white', '#dfe7f2', '#f4b6b6', '#555555', '#e8833a', '#c0392b'])
def show(ax, p, img, title):
    g = p.grid
    ax.imshow(img, origin='lower', cmap=cmap, vmin=0, vmax=5, interpolation='nearest',
              extent=[g.origin[0], g.origin[0] + g.nx * g.h, g.origin[2], g.origin[2] + g.nz * g.h])
    ax.set_title(title, fontsize=10); ax.set_xlim(-26, 102); ax.set_ylim(-38, 142); ax.set_aspect('equal')
    ax.set_xlabel('앞 (x, mm)', fontsize=8); ax.set_ylabel('위 (z, mm)', fontsize=8); ax.tick_params(labelsize=7)


fig = plt.figure(figsize=(16, 10.5))
gs = fig.add_gridspec(2, 4, hspace=0.33, wspace=0.3)
for c, (ph, txt) in enumerate([(22.0, '기둥 22 mm (원래)\n폰 공간이 클램프·받침과 겹침(진빨강) → 불가능'),
                               (60.0, '기둥 60 mm (채택)\n폰 공간이 위로 올라감, 설계 영역의 12%만 막음'),
                               (110.0, '기둥 110 mm\n안 막지만 지렛대가 길어 다 채워도 56 Hz → 불가능')]):
    p = problems.BikeMount(80.0, 16.0, post_h=ph)
    show(fig.add_subplot(gs[0, c]), p, side(p, ko=keepout(ph)), f'①-{c + 1} {txt}')
ax = fig.add_subplot(gs[0, 3])
H = [40, 60, 80, 110]; F = [None, 101.2, 81.0, 56.3]
ax.plot([60, 80, 110], [101.2, 81.0, 56.3], 'o-', color='#e8833a', label='설계 영역 다 채움 (가장 튼튼한 경우)')
ax.axhline(91.2, color='#c0392b', ls='--', lw=1); ax.text(108, 93, '기준 91.2 Hz', color='#c0392b', fontsize=8, ha='right')
ax.axvspan(15, 50, color='#f4b6b6', alpha=.5); ax.text(32, 62, '폰 공간이\n고정부와 겹침\n(형상 불가)', ha='center', fontsize=8, color='#a33')
ax.set_xlim(15, 115); ax.set_ylim(40, 115); ax.set_xlabel('폰 기둥 높이 mm', fontsize=8); ax.set_ylabel('최저 진동수 Hz', fontsize=8)
ax.set_title('② 기둥 높이 고르기 (받침 80, FEM)\n낮으면 겹치고, 높으면 흔들림', fontsize=10); ax.legend(fontsize=7); ax.grid(alpha=.3); ax.tick_params(labelsize=7)

g = 'bike_pad80_free'; pf = problems.get(g); cv = shapes.Canvas(pf)
o, _ = shapes.make_shape(pf, g, 8, cv); ev = labels.fem_label(pf, o, pf.default_cond)['eval']
show(fig.add_subplot(gs[1, 0]), pf, side(pf, o, pf.keepout), f'③ 무작위 형상 예 (폰 공간을 돌아감)\n{ev["f_min"]:.0f} Hz · {ev["mass_g"]:.0f} g → 불합격')
seq, cond = datagen.topdown_seq(g, 1, cv)
pick = [0, 6, 9]
for c, k in enumerate(pick):
    i, o, m = seq[k]; ev = labels.fem_label(pf, o, cond)['eval']
    show(fig.add_subplot(gs[1, 1 + c]) if c < 2 else None, pf, side(pf, o, pf.keepout), '') if False else None
for c, k in enumerate(pick[:2]):
    i, o, m = seq[k]; ev = labels.fem_label(pf, o, cond)['eval']
    show(fig.add_subplot(gs[1, 1 + c]), pf, side(pf, o, pf.keepout),
         f'④ 위에서 깎기 {m["step"]}단계 (재료 {m["vf"]:.0%})\n{ev["f_min"]:.0f} Hz · {ev["mass_g"]:.0f} g → {"합격" if ev["pass"] else "불합격"}')
ax = fig.add_subplot(gs[1, 3])
d = json.load(open('/home/claude/run/td/free80.json'))
ax.scatter([r[1] for r in d['random']], [r[0] for r in d['random']], c='#888', s=22, label='무작위 형상 14개')
for k, (j, R) in enumerate(sorted(d['seqs'].items())):
    ax.plot([r[3] for r in R], [r[2] for r in R], '-o', ms=3.5, label=f'위에서 깎기 순서열 {j}')
ax.axhline(91.2, color='#c0392b', ls='--', lw=1)
ax.set_xlabel('질량 g (대칭 복원, 고정부품 포함)', fontsize=8); ax.set_ylabel('최저 진동수 Hz', fontsize=8); ax.set_xlim(0, 250); ax.set_ylim(0, 115)
ax.set_title('⑤ 무작위 형상은 기준 아래에 몰림\n위에서 깎기는 기준선을 가로지름', fontsize=10); ax.legend(fontsize=7, loc='lower right'); ax.grid(alpha=.3); ax.tick_params(labelsize=7)
fig.suptitle('화면 각도 자유 그룹 bike_pad80_free — 옆모습 · 분홍 = 폰이 360° 돌고 −30~+60° 기울며 지나가는 공간 · 회색 = 클램프·받침·기둥(고정) · 주황 = 재료', fontsize=11.5)
os.makedirs(OUT, exist_ok=True)
fn = os.path.join(OUT, 'free_angle_explain.png'); plt.savefig(fn, dpi=105, bbox_inches='tight'); print(fn)
