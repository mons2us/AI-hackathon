"""FNO vs GINO 예측 비교 — 같은 검증 58개, 같은 지표, 같은 코드로 계산.
성능: 평균 |예측/정답 − 1| (무게는 둘 다 정확식이라 제외) · 분포: 형상별 상대 L2 평균 (온도 = 열 영역 칸, 응력 = 재료 칸, log1p)
시간: 형상 1개 예측(CPU 1스레드), 검증 형상 10개 평균.
변형(v): 사용 python3 cmp_eval_v.py <태그> <fno.pt> <gino.pt> → cmp_eval_<태그>.json. 분포는 각 모델 자기 척도로 원래 단위 복원 후 비교(학습 데이터가 달라 척도가 다름)."""
import sys, os, json, time, numpy as np, torch
H = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [H, '/home/claude/input-spec/13_AI학습_일체형']
torch.set_num_threads(1)
from ai.surrogate import Surrogate
from gino_data import load
from search_cmp import GinoPred
geo, D, tr, te, norm, Yn, T, V, ts, vs = load(); g = geo.g; TH = geo.thermal.ravel()
names = ['f1_hz', 'f2_hz', 'phone_Tmax_rise_c', 'touch_top_mm', 'touch_bottom_mm', 'shock_vm999_mpa']
TAG, FP, GP = sys.argv[1], sys.argv[2], sys.argv[3]
fno = Surrogate(FP, g, torch.device('cpu')); gp = GinoPred(GP)
SC = {n: np.array(torch.load(f, map_location='cpu', weights_only=False)['field_scale'], float) for n, f in [('fno', FP), ('gino', GP)]}
res = {}; tim = {}
for name in ['fno', 'gino']:
    P, FE, tt = [], [], []
    for n, i in enumerate(te):
        occ = torch.tensor(D['occ'][i][None]); F = geo.full(D['occ'][i]); fl = F.ravel() > 0.5
        t0 = time.time()
        with torch.no_grad():
            if name == 'fno':
                o = fno.predict(occ); y = o['scalars'][0].numpy(); f = o['fields'][0].reshape(2, -1).T.numpy()
                k = np.arange(len(fl))
            else:
                full = torch.tensor(F); Ps, Ns = geo.surface(F); k = np.nonzero(fl | TH)[0]
                s, f = gp.net(torch.tensor(Ps), torch.tensor(Ns), torch.tensor(geo.latent), geo.latent_occ(full), torch.tensor(geo.cell.reshape(-1, 3)[k]))
                y = gp.norm.decode_t(s[None])[0].numpy(); f = f.numpy()
        if n < 10: tt.append(time.time() - t0)
        f = f * SC[name]; tgt = np.stack([T[i].ravel()[k], V[i].ravel()[k]], 1); m = np.stack([TH[k], fl[k]], 1).astype(float)
        FE.append(np.sqrt((((f - tgt) * m) ** 2).sum(0)) / np.maximum(np.sqrt(((tgt * m) ** 2).sum(0)), 1e-6)); P.append(y)
    P = np.array(P); Tt = D['lab'][te]; fe = np.mean(FE, 0); r = {}
    for j, n in enumerate(names, 1):
        p, t = P[:, j], Tt[:, j]; ar = np.abs(p / np.maximum(np.abs(t), 1e-6) - 1)
        lp, lt = np.log(np.maximum(p, 1e-6)), np.log(np.maximum(t, 1e-6))
        dz = (t >= 50) & (t <= 200) if n == 'f1_hz' else np.ones(len(t), bool)       # 진동수: 설계 구간 50~200 Hz 형상만 따로
        r[n] = dict(mape=round(float(ar.mean()), 4), median=round(float(np.median(ar)), 4),
                    relL2=round(float(np.linalg.norm(p - t) / np.linalg.norm(t)), 4),
                    r2=round(float(1 - ((p - t) ** 2).sum() / ((t - t.mean()) ** 2).sum()), 4),
                    r2_log=round(float(1 - ((lp - lt) ** 2).sum() / ((lt - lt.mean()) ** 2).sum()), 4))
        if n == 'f1_hz': r[n].update(mape_50_200=round(float(ar[dz].mean()), 4), n_50_200=int(dz.sum()))
    res[name] = dict(scalars=r, field_T=round(float(fe[0]), 4), field_vm=round(float(fe[1]), 4))
    np.save(f'{H}/pred_{name}_{TAG}_test.npy', P)
    tim[name] = round(float(np.mean(tt)), 3)
st = {n: torch.load(f, map_location='cpu', weights_only=False) for n, f in [('fno', FP), ('gino', GP)]}
info = dict(fno=dict(params=sum(v.numel() for v in st['fno']['state'].values()), train_s=st['fno']['final']['t'], steps=st['fno']['final']['it'], batch=16),
            gino=dict(params=st['gino']['params'], train_s=st['gino']['final']['t'], steps=st['gino']['final']['it'], batch=1))
out = dict(n_train=len(tr), n_test=len(te), relerr=res, predict_s_1thread=tim, info=info)
json.dump(out, open(H + f'/cmp_eval_{TAG}.json', 'w'), ensure_ascii=False, indent=1); print(json.dumps(out, ensure_ascii=False, indent=1))
