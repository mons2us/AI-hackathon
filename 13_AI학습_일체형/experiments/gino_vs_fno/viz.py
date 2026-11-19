"""검증 형상별 정밀 시뮬레이션(정답) · FNO · GINO 분포 지도 + 성능 산점도 → fig/*.png, viz.json
지도: 옆에서 본 모습(x–z 평면, y 방향 최댓값 투영). 응력 = log1p(von Mises) 재료 칸, 온도 상승 = 열 영역 칸. 행마다 같은 색 척도."""
import sys, os, json, numpy as np, torch
H = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [H, '/home/claude/input-spec/13_AI학습_일체형']
torch.set_num_threads(2)
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt; from matplotlib import font_manager as fm
fm.fontManager.addfont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'); plt.rcParams['font.family'] = 'Noto Sans CJK JP'
from ai.surrogate import Surrogate
from gino_data import load
from search_cmp import GinoPred
geo, D, tr, te, norm, Yn, T, V, ts, vs = load(); g = geo.g; TH = geo.thermal.ravel(); nz, ny, nx = g.nz, g.ny, g.nx
HAS_FNO = os.path.exists(H + '/fno_base.pt'); MODELS = (['fno'] if HAS_FNO else []) + ['gino']   # FNO 학습 전이면 GINO 만
fno = Surrogate(H + '/fno_base.pt', g, torch.device('cpu')) if HAS_FNO else None; gp = GinoPred(H + '/gino.pt')
m = np.load('/home/claude/input-spec/13_AI학습_일체형/data/grid_meta.npz'); h = float(m['h'])
ext = [m['xc'].min() - h / 2, m['xc'].max() + h / 2, m['zc'].min() - h / 2, m['zc'].max() + h / 2]
os.makedirs(H + '/fig', exist_ok=True)

def predict(i):
    F = geo.full(D['occ'][i]); fl = F.ravel() > 0.5
    with torch.no_grad():
        if HAS_FNO: o = fno.predict(torch.tensor(D['occ'][i][None])); yf = o['scalars'][0].numpy(); ff = o['fields'][0].reshape(2, -1).numpy()
        else: yf = np.full(7, np.nan); yf[0] = F.sum() * 0.02032; ff = np.full((2, len(fl)), np.nan)
        Ps, Ns = geo.surface(F); k = np.nonzero(fl | TH)[0]
        s, f = gp.net(torch.tensor(Ps), torch.tensor(Ns), torch.tensor(geo.latent), geo.latent_occ(torch.tensor(F)), torch.tensor(geo.cell.reshape(-1, 3)[k]))
        yg = gp.norm.decode_t(s[None])[0].numpy(); yg[0] = yf[0]
    fg = np.full((2, len(fl)), np.nan); fg[:, k] = f.numpy().T
    true = np.stack([T[i].ravel() / ts, V[i].ravel() / vs])
    return F, fl, dict(true=true, fno=ff, gino=fg), dict(true=D['lab'][i], fno=yf, gino=yg)

def proj(v, mask):
    a = np.where(mask, v, np.nan).reshape(nz, ny, nx)
    with np.errstate(all='ignore'): return np.nanmax(a, 1)        # (nz, nx)

# 대표 형상 6개: 정답 진동수 분위 + 데모 기준(95 Hz)에 가장 가까운 형상
f1 = D['lab'][te, 1]; order = te[np.argsort(f1)]
pick = [order[int(q * (len(order) - 1))] for q in (0.1, 0.3, 0.5, 0.7, 0.9)]
near = te[np.argmin(np.abs(f1 - 95))]
if near not in pick: pick.insert(3, near)
LBL = [('f1_hz', 1, 'Hz', '진동수'), ('phone_Tmax_rise_c', 3, '°C', '폰 온도'), ('touch_top_mm', 4, 'mm', '휨(위)'), ('shock_vm999_mpa', 6, 'MPa', '충격 응력')]
out = []
for n, i in enumerate(pick):
    F, fl, FLD, SC = predict(i)
    fig, ax = plt.subplots(2, 1 + len(MODELS), figsize=(3.5 * (1 + len(MODELS)), 4.6), constrained_layout=True, squeeze=False)
    for r, (ch, msk, ttl, cm) in enumerate([(1, fl, '응력 log(1+MPa)', 'magma'), (0, TH, '온도 상승', 'coolwarm')]):
        mps = [proj(FLD[k][ch] * (vs if ch else ts), msk) for k in ['true'] + MODELS]
        vmax = np.nanmax(mps[0]); vmin = np.nanmin(mps[0])
        for c, (mp, nm) in enumerate(zip(mps, ['정밀 시뮬레이션 (정답)'] + [x.upper() for x in MODELS])):
            a = ax[r, c]; sil = (F.reshape(nz, ny, nx).max(1) > 0.5).astype(float)
            a.imshow(np.where(sil > 0, 0.92, 1.0), origin='lower', extent=ext, cmap='gray', vmin=0, vmax=1)
            im = a.imshow(mp, origin='lower', extent=ext, cmap=cm, vmin=vmin, vmax=vmax)
            a.set_xticks([]); a.set_yticks([])
            a.set_title(nm if r == 0 else '', fontsize=10)
        fig.colorbar(im, ax=ax[r, :], shrink=0.8, label=ttl)
    fig.savefig(f'{H}/fig/shape_{n}.png', dpi=110); plt.close(fig)
    rel = {k: float(np.sqrt(np.nansum(((FLD[k][0] - FLD['true'][0]) * TH) ** 2)) / np.sqrt(np.nansum((FLD['true'][0] * TH) ** 2))) for k in MODELS}
    relv = {k: float(np.sqrt(np.nansum(((FLD[k][1] - FLD['true'][1]) * fl) ** 2)) / np.sqrt(np.nansum((FLD['true'][1] * fl) ** 2))) for k in MODELS}
    out.append(dict(idx=int(i), name=str(D['names'][i]), mass=float(F.sum() * 0.02032), img=f'fig/shape_{n}.png',
                    scalars={lab: {k: float(SC[k][j]) for k in ['true'] + MODELS} for lab, j, u, kr in LBL},
                    field_relL2_T={k: round(rel[k], 4) for k in rel}, field_relL2_vm={k: round(relv[k], 4) for k in relv}))
    print(n, out[-1]['name'], out[-1]['scalars']['f1_hz'], flush=True)
# 산점도 (검증 58개, 로그 축)
if not os.path.exists(H + '/pred_gino_test.npy'):
    np.save(H + '/pred_gino_test.npy', np.array([predict(i)[3]['gino'] for i in te]))
PG = np.load(H + '/pred_gino_test.npy'); PF = np.load(H + '/pred_fno_test.npy') if HAS_FNO else np.full_like(PG, np.nan); TT = D['lab'][te]
fig, ax = plt.subplots(1, 4, figsize=(13, 3.4), constrained_layout=True)
for a, (lab, j, u, kr) in zip(ax, LBL):
    t = TT[:, j]; lo, hi = max(np.nanmin([t.min(), np.nanmin(PF[:, j]), PG[:, j].min()]), 1e-3), np.nanmax([t.max(), np.nanmax(PF[:, j]), PG[:, j].max()])
    a.plot([lo, hi], [lo, hi], color='#888', lw=0.8); (a.scatter(t, PF[:, j], s=14, c='#7F77DD', label='FNO', alpha=0.8) if HAS_FNO else None); a.scatter(t, PG[:, j], s=14, c='#1D9E75', marker='^', label='GINO', alpha=0.8)
    a.set_xscale('log'); a.set_yscale('log'); a.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter()); a.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter()); a.set_title(f'{kr} ({u})', fontsize=10); a.set_xlabel('정밀 시뮬레이션 (정답)'); a.set_ylabel('AI 예측')
ax[0].legend(fontsize=8); fig.savefig(H + '/fig/scatter.png', dpi=110); plt.close(fig)
json.dump(out, open(H + '/viz.json', 'w'), ensure_ascii=False, indent=1)
