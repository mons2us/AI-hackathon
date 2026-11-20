"""아키텍처 지도 v3 그림: 같은 검증 형상 하나를 각 아키텍처가 '어떻게 보는지' 실제 데이터로 그림 → fig/arch_*.png
형상 = 검증 58개 중 첫 형상(te[0]), 정답 분포 = 팀 정밀 시뮬레이션. Transolver 조각 · 확산 등 학습 안 한 모델은 '개념 예시'로 표기."""
import sys, os, json, numpy as np, torch
H = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [H, '/home/claude/input-spec/13_AI학습_일체형']
torch.set_num_threads(2)
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt; from matplotlib import font_manager as fm
fm.fontManager.addfont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'); plt.rcParams['font.family'] = 'Noto Sans CJK JP'; plt.rcParams['axes.unicode_minus'] = False
from gino_data import load
from ai.surrogate import Surrogate
geo, D, tr, te, norm, Yn, T, V, ts, vs = load(); g = geo.g; nz, ny, nx = g.nz, g.ny, g.nx
I = int(te[0]); F = geo.full(D['occ'][I]); fl = F > 0.5; TH = geo.thermal
FIX = g.solid.reshape(nz, ny, nx).astype(bool)
OUT = H + '/fig'; DPI = 150
BLUE, GRAY, TEAL, PUR, ORG = '#2F6FA8', '#B9C0C9', '#1D7F69', '#6A60C9', '#C27C0E'
def save(fig, n): fig.savefig(f'{OUT}/arch_{n}.png', dpi=DPI, bbox_inches='tight', facecolor='white'); plt.close(fig); print(n)
def ax3(fig, pos=111):
    a = fig.add_subplot(pos, projection='3d'); a.set_box_aspect((nx, ny * 2, nz)); a.view_init(22, -62); a.set_axis_off(); return a

# 1) 복셀 입력 (FNO · 3D U-Net): 대칭 반쪽 → 전체로 펼쳐 보여줌
full = np.concatenate([fl[:, ::-1, :], fl], 1); fixf = np.concatenate([FIX[:, ::-1, :], FIX], 1)
vox = full.transpose(2, 1, 0)                                  # (x, y, z)
col = np.empty(vox.shape, object); col[:] = BLUE; col[fixf.transpose(2, 1, 0) & vox] = GRAY
fig = plt.figure(figsize=(7, 3.6)); a = ax3(fig); a.voxels(vox, facecolors=col, edgecolor=(0, 0, 0, .08), linewidth=.2)
a.set_title(f'복셀 격자 {nx}×{ny * 2}×{nz} (칸 2 mm) — 파랑 = 설계 영역 재료 · 회색 = 고정 부품', fontsize=10); save(fig, 'voxel')

# 2) FNO 개념: 옆모습(앞뒤 방향 투영) 점유에 같은 모드 수(z 8 · x 12)만 남김
occ = fl.any(1).astype(float); Fk = np.fft.rfft2(occ); mz, mx = 8, 12; M = np.zeros_like(Fk)
M[:mz, :mx] = Fk[:mz, :mx]; M[-mz:, :mx] = Fk[-mz:, :mx]; low = np.fft.irfft2(M, s=occ.shape); j = int(np.argmax(fl.sum((0, 2))))
fig, ax = plt.subplots(1, 3, figsize=(12, 2.4))
ax[0].imshow(occ, origin='lower', cmap='Greys', interpolation='nearest'); ax[0].set_title('입력: 점유 0/1 (옆모습)', fontsize=10)
ax[1].imshow(np.log1p(np.abs(np.fft.fftshift(np.fft.fft2(occ)))), origin='lower', cmap='magma', aspect='auto'); ax[1].add_patch(plt.Rectangle((nx / 2 - mx, nz / 2 - mz), 2 * mx, 2 * mz, fill=False, ec='cyan', lw=1.5)); ax[1].set_title('푸리에 스펙트럼 · 하늘색 = 남기는 저주파', fontsize=10)
ax[2].imshow(low, origin='lower', cmap='Greys', interpolation='bilinear'); ax[2].set_title('저주파만 남긴 모습 = 전역 경로가 보는 형상', fontsize=10)
for x in ax: x.set_xticks([]); x.set_yticks([])
save(fig, 'fno_modes')

# 3) GINO: 표면 점 + 법선, 잠재 격자, 한 잠재 노드의 반경 이웃
P, Nn = geo.surface(F); rng = np.random.default_rng(0); si = rng.choice(len(P), 2048, replace=False); Ps = P[si]
L = geo.latent.reshape(-1, 3); r = 0.045
c = L[np.argmin(np.linalg.norm(L - Ps[np.argmin(np.abs(Ps[:, 0] - np.median(Ps[:, 0])) + np.abs(Ps[:, 2] - Ps[:, 2].max()))], axis=1))]
nb = np.linalg.norm(Ps - c, axis=1) < r * 2
fig = plt.figure(figsize=(11, 3.8))
a = fig.add_subplot(121, projection='3d'); a.set_box_aspect((2, 0.45, 0.85)); a.view_init(20, -62); a.set_axis_off()
a.scatter(Ps[:, 0], Ps[:, 1], Ps[:, 2], c=(Nn[si] + 1) / 2, s=2); a.set_title(f'표면 점 2,048개 (색 = 바깥 법선 방향)\n전체 표면 점 {len(P):,}개에서 무작위', fontsize=10)
b = fig.add_subplot(122, projection='3d'); b.set_box_aspect((2, 0.45, 0.85)); b.view_init(20, -62); b.set_axis_off()
b.scatter(L[::2, 0], L[::2, 1], L[::2, 2], s=2, c=PUR, alpha=.35); b.scatter(Ps[~nb, 0], Ps[~nb, 1], Ps[~nb, 2], s=1.2, c=GRAY)
b.scatter(Ps[nb, 0], Ps[nb, 1], Ps[nb, 2], s=22, c=ORG, depthshade=False); b.scatter(*c, s=160, c='#E0245E', marker='*', depthshade=False)
b.set_title('보라 = 잠재 격자 44×10×19 노드 · 주황 = 한 노드(★)가 모으는 이웃 표면 점', fontsize=10)
save(fig, 'gino_points')

# 4) 정답 분포 (온도 · 응력) 3D 점 — Transolver 조각 개념 예시: 정답 [온도, log 응력, 위치]로 k-평균 8조각
k = np.nonzero(fl.ravel() | TH.ravel())[0]; xyz = geo.cell.reshape(-1, 3)[k]
Tv = T[I].ravel()[k]; Vv = V[I].ravel()[k]
Z = np.c_[(Tv - Tv.mean()) / Tv.std(), (Vv - Vv.mean()) / (Vv.std() + 1e-9), xyz / xyz.std(0) * .5]
from numpy.random import default_rng
cent = Z[default_rng(1).choice(len(Z), 8, replace=False)]
for _ in range(30):
    lab = np.argmin(((Z[:, None] - cent[None]) ** 2).sum(-1), 1); cent = np.array([Z[lab == q].mean(0) if (lab == q).any() else cent[q] for q in range(8)])
sub = rng.choice(len(k), min(9000, len(k)), replace=False)
fig = plt.figure(figsize=(11, 3.6))
for pi, (v, cm, tt) in enumerate([(Tv, 'coolwarm', '정답 온도 상승'), (lab, 'tab10', '개념 예시: 비슷한 물리 상태끼리 8조각')]):
    a = fig.add_subplot(1, 2, pi + 1, projection='3d'); a.set_box_aspect((2, 0.45, 0.85)); a.view_init(20, -62); a.set_axis_off()
    a.scatter(xyz[sub, 0], xyz[sub, 1], xyz[sub, 2], c=v[sub], cmap=cm, s=1.5); a.set_title(tt, fontsize=10)
save(fig, 'trans_slices')

# 5) MeshGraphNet: 가운데 단면 칸 그래프 + 한 노드에서 메시지 3 · 15 단계 도달 범위
j = int(np.argmax(fl.sum((0, 2)))); sl = fl[:, j, :]; idx = -np.ones(sl.shape, int); pts = np.argwhere(sl); idx[tuple(pts.T)] = np.arange(len(pts))
from collections import deque
st = pts[np.argmin(np.abs(pts[:, 1] - nx * 0.45) + np.abs(pts[:, 0] - pts[:, 0].max()))]
dist = -np.ones(len(pts), int); dist[idx[tuple(st)]] = 0; dq = deque([tuple(st)])
while dq:
    z_, x_ = dq.popleft()
    for dz, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        q = (z_ + dz, x_ + dx)
        if 0 <= q[0] < nz and 0 <= q[1] < nx and idx[q] >= 0 and dist[idx[q]] < 0: dist[idx[q]] = dist[idx[(z_, x_)]] + 1; dq.append(q)
fig, ax = plt.subplots(1, 2, figsize=(11, 2.9))
for a, hop in zip(ax, (3, 15)):
    for (z_, x_) in pts[::1]:
        for dz, dx in ((1, 0), (0, 1)):
            q = (z_ + dz, x_ + dx)
            if q[0] < nz and q[1] < nx and idx[q] >= 0: a.plot([x_, q[1]], [z_, q[0]], color='#D5DAE0', lw=.4, zorder=1)
    reach = (dist >= 0) & (dist <= hop)
    a.scatter(pts[~reach, 1], pts[~reach, 0], s=3, c=GRAY, zorder=2); a.scatter(pts[reach, 1], pts[reach, 0], s=4, c=TEAL, zorder=3)
    a.scatter(st[1], st[0], s=60, c=ORG, marker='*', zorder=4); a.set_aspect('equal'); a.set_xticks([]); a.set_yticks([])
    a.set_title(f'메시지 전달 {hop}회 뒤 정보가 닿는 칸 (초록) — 전체 {len(pts)}칸 중 {int(reach.sum())}', fontsize=10)
save(fig, 'mgn_hops')

# 6) DoMINO 개념: 질의점 주변 k-NN(7) 이웃 + 크기 다른 두 영역
q = Ps[np.argmax(Ps[:, 0])]; d = np.linalg.norm(Ps - q, axis=1); kn = np.argsort(d)[:7]
fig, ax = plt.subplots(1, 2, figsize=(11, 3.4))
ax[0].scatter(Ps[:, 0], Ps[:, 2], s=1, c=GRAY); ax[0].scatter(*q[[0, 2]], s=120, c=TEAL, marker='*'); ax[0].add_patch(plt.Rectangle((q[0] - .12, q[2] - .12), .24, .24, fill=False, ec=PUR, lw=1.2)); ax[0].set_title('표면 점 (옆모습) · 보라 = 확대 영역', fontsize=10)
w = np.abs(Ps[:, 0] - q[0]) < .12; w &= np.abs(Ps[:, 2] - q[2]) < .12
ax[1].scatter(Ps[w, 0], Ps[w, 2], s=10, c=GRAY); ax[1].scatter(Ps[kn, 0], Ps[kn, 2], s=40, c=ORG); ax[1].scatter(*q[[0, 2]], s=200, c=TEAL, marker='*')
for hs, cc in ((.04, ORG), (.1, PUR)): ax[1].add_patch(plt.Rectangle((q[0] - hs, q[2] - hs), 2 * hs, 2 * hs, fill=False, ec=cc, lw=1.2, ls='--'))
ax[1].set_title('확대: 주황 = 가장 가까운 7개 이웃 · 점선 = 크기 다른 두 영역 (개념)', fontsize=10)
for x in ax: x.set_aspect('equal'); x.set_xticks([]); x.set_yticks([])
save(fig, 'domino_knn')

# 7) 출력: 정답 vs FNO 온도 · 응력 + 라플라시안 (PINO 방식 물리 손실이 보는 곳, 개념)
fno = Surrogate(H + '/fno_base.pt', g, torch.device('cpu'))
with torch.no_grad(): o = fno.predict(torch.tensor(D['occ'][I][None]))
ff = o['fields'][0].reshape(2, nz, ny, nx).numpy(); Tp = ff[0] * ts; Tt = T[I]
def lap(u, m):
    Lp = np.zeros_like(u); mm = m.copy()
    for ax_ in range(3):
        Lp += np.roll(u, 1, ax_) + np.roll(u, -1, ax_) - 2 * u
        mm &= np.roll(m, 1, ax_) & np.roll(m, -1, ax_)
    return np.where(mm, Lp, np.nan)
zs = np.where(TH.any((1, 2)))[0]; zc = int(zs[len(zs) // 2])
Lt, Lpp = lap(Tt, TH), lap(Tp, TH); vm = np.nanpercentile(np.abs(Lt), 98)
fig, ax = plt.subplots(2, 2, figsize=(11, 3.4))
for a, im, tt, cm, lim in [(ax[0, 0], np.where(TH, Tt, np.nan)[zc], '정답 온도 (열 영역 한 층, 위에서 봄)', 'coolwarm', None), (ax[0, 1], np.where(TH, Tp, np.nan)[zc], 'FNO 예측 온도', 'coolwarm', None),
                           (ax[1, 0], Lt[zc], '정답의 라플라시안 ∇²T', 'RdBu_r', vm), (ax[1, 1], Lpp[zc], 'FNO 예측의 라플라시안 ∇²T', 'RdBu_r', vm)]:
    kw = dict(vmin=-lim, vmax=lim) if lim else dict(vmin=np.nanmin(Tt[zc][TH[zc]]), vmax=np.nanmax(Tt[zc][TH[zc]]))
    a.imshow(im, origin='lower', cmap=cm, aspect='auto', interpolation='nearest', **kw); a.set_title(tt, fontsize=10); a.set_xticks([]); a.set_yticks([])
fig.tight_layout(); save(fig, 'pino_lap')

# 8) 능동학습 5회: AI 진동수 vs 정밀 (경로 31개씩) — 탐색이 속는 모습
fig, ax = plt.subplots(1, 5, figsize=(13, 2.9), sharey=True)
for r, a in zip(range(1, 6), ax):
    p = json.load(open(f'/home/claude/input-spec/13_AI학습_일체형/data/al/r{r}_pred_vs_fem.json'))
    x = [c['fem_f1'] for c in p]; y = [c['pred_f1'] for c in p]; it = np.arange(len(p))
    sc = a.scatter(x, y, c=it, cmap='viridis', s=14); a.plot([0, 220], [0, 220], color='#888', lw=.8); a.axhline(95, color='#C8453B', lw=.7, ls=':'); a.axvline(95, color='#C8453B', lw=.7, ls=':')
    a.set_xlim(0, 220); a.set_ylim(0, 220); a.set_title(f'{r}회차', fontsize=10); a.set_xlabel('정밀 진동수 (Hz)', fontsize=9)
ax[0].set_ylabel('AI 진동수 (Hz)', fontsize=9); cb = fig.colorbar(sc, ax=ax, fraction=.015); cb.set_label('탐색 반복 (×10)', fontsize=8)
save(fig, 'al_rounds')
