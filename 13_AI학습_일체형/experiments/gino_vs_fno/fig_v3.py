"""v3 그림: (1) 탐색 경로 — AI 예측 진동수 · 무게 vs 반복, 끝점에 정밀 결과 (2) 탐색 형상 옆모습 4개 + 초기 설계"""
import json, os, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
H = os.path.dirname(os.path.abspath(__file__))
for f in ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc']:
    if os.path.exists(f): fm.fontManager.addfont(f); plt.rcParams['font.family'] = fm.FontProperties(fname=f).get_name()
plt.rcParams['axes.unicode_minus'] = False
import sys; sys.path.insert(0, '/home/claude/input-spec/13_AI학습_일체형'); from ai.data import Grid
g = Grid('/home/claude/input-spec/13_AI학습_일체형/data/grid_meta.npz')
R = [('gino', 'GINO · 389', '#1D7F69', '-'), ('gino734', 'GINO · 734', '#1D7F69', '--'), ('fno', 'FNO · 389', '#6A60C9', '-'), ('fno734', 'FNO · 734', '#6A60C9', '--')]
fig, ax = plt.subplots(1, 2, figsize=(11, 3.8), dpi=150)
for n, lab, c, ls in R:
    t = json.load(open(f'{H}/search_{n}.json'))['trace']; fe = json.load(open(f'{H}/fem_{n}.json'))['keep']
    it = [r['it'] for r in t]
    ax[0].plot(it, [r['f1'] for r in t], ls, color=c, label=lab, lw=1.6); ax[0].plot([300], [fe['f1']], 'o' if ls == '-' else 's', color=c, ms=7, mfc='white' if ls == '--' else c)
    ax[1].plot(it, [r['mass'] for r in t], ls, color=c, label=lab, lw=1.6)
ax[0].axhline(95, color='#C8453B', lw=1, ls=':'); ax[0].text(5, 98, '기준 95 Hz', color='#C8453B', fontsize=9)
ax[0].set_yscale('log'); ax[0].set_xlabel('탐색 반복'); ax[0].set_ylabel('진동수 1차 (Hz, 로그)'); ax[0].set_title('AI 가 본 진동수 (선) · 끝 형상 정밀 결과 (점)', fontsize=10)
ax[1].set_xlabel('탐색 반복'); ax[1].set_ylabel('무게 (g)'); ax[1].set_title('무게 (0.5 기준 형상)', fontsize=10); ax[1].legend(fontsize=8, frameon=False)
for a in ax: a.grid(alpha=.25); a.spines[['top', 'right']].set_visible(False)
plt.tight_layout(); plt.savefig(f'{H}/fig/search_v3.png'); plt.close()
# 옆모습: 칸 0/1 → y 방향 합(두께), z 위
nz, ny, nx = g.nz, g.ny, g.nx
z0 = g.solid.copy().astype(float)
import torch; sys.path.insert(0, '/home/claude/input-spec/10_입력_1차설계')
from formproof_input.inverse.fp11.deepsdf import ShapeAI
M = '/home/claude/input-spec/10_입력_1차설계/models/fp11'; S = ShapeAI(M + '/runs/sdf.pt', g)
o = S.decode(torch.tensor(np.load(M + '/z0_3a61befe66c5_1500.npy').reshape(1, -1), dtype=torch.float32), sharp=2.0)
z0[g.didx] = (o.detach().numpy()[0] > 0.5)
items = [('초기 설계', z0, '94.9 g')] + [(lab, np.load(f'{H}/search_{n}_rho.npy').astype(float), f"{json.load(open(f'{H}/fem_{n}.json'))['keep']['mass_g']:.1f} g") for n, lab, _, _ in R]
from matplotlib.colors import ListedColormap
fixed = g.solid.reshape(nz, ny, nx).astype(bool); D = np.zeros(nz * ny * nx, bool); D[g.didx] = True; D = D.reshape(nz, ny, nx)
cm = ListedColormap(['#FFFFFF', '#C9CED6', '#1F6F8B'])
fig, ax = plt.subplots(3, 2, figsize=(10, 5.4), dpi=150); ax = ax.ravel()
for a, (lab, r, m) in zip(ax, items):
    v = r.reshape(nz, ny, nx) > 0.5
    img = np.where((v & D).any(1), 2, np.where((v & ~D).any(1), 1, 0))     # 옆에서 봤을 때 설계 영역 재료 = 파랑, 고정 부품 = 회색
    a.imshow(img, origin='lower', cmap=cm, vmin=0, vmax=2, aspect='equal', interpolation='nearest'); a.set_xticks([]); a.set_yticks([])
    a.set_title(f'{lab} · {m}', fontsize=10, loc='left')
    for s_ in a.spines.values(): s_.set_color('#D9DEE5')
ax[-1].axis('off'); ax[-1].text(0.02, 0.6, '옆에서 본 모습 (앞뒤 방향으로 하나라도 재료가 있으면 칠함)\n파랑 = 형상 AI 가 만든 재료 · 회색 = 고정 부품', fontsize=9, transform=ax[-1].transAxes, va='top')
plt.tight_layout(); plt.savefig(f'{H}/fig/shapes_v3.png'); plt.close(); print('ok')
