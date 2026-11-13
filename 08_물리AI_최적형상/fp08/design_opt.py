"""최적화 (설계 결정 8번) — DeepSDF z 를 Adam 으로 갱신, 제약은 증강 라그랑지로 합침, 끝나면 FEM 검증.

목적: 질량 최소.  제약: 판정 기준(여유 = 품질 관문 실측 오차).
시작점 약 10개 동시: 학습 형상 중 예측상 가볍고 기준을 만족하는 것 + 무작위.
FEM 검증 실패 → 다음 후보 → 전부 실패면 'fallback' (FEM 직접 최적화로 넘김), 실패 형상은 재학습 데이터로 기록.
"""
import os, json, time
import numpy as np
import torch
from scipy import ndimage
from . import problems, models, train_pino, train_sdf, labels, fem, datagen, shapes


class Judge:
    """판정값을 torch 로 (미분 가능). 반환: [(이름, 값, 한계, 'le'|'ge')]"""

    def __init__(self, p, pt, cond):
        self.p, self.pt, self.cond = p, pt, cond
        g = p.grid
        dv = pt.edof.device
        self.C = torch.tensor(p.C, dtype=torch.float32, device=dv)
        self.B0 = torch.tensor(p.B0, dtype=torch.float32, device=dv)
        if p.product == 'tv_stand':
            n = p.load_nodes
            w = np.where(g.nxc[n] == 0.0, 0.5, 1.0); w = w / w.sum()
            self.n = torch.tensor(n, device=dv); self.w = torch.tensor(w, dtype=torch.float32, device=dv)
            self.cy = torch.tensor(g.nyc[n] - (w * g.nyc[n]).sum(), dtype=torch.float32, device=dv)
            self.cx = torch.tensor(g.nxc[n] - (w * g.nxc[n]).sum(), dtype=torch.float32, device=dv)
            self.L = p.loads(cond)
        else:
            rr = np.sqrt(g.xc ** 2 + g.zc ** 2)
            self.far = torch.tensor(rr > 19.0, device=dv)
        self.solid = torch.tensor(p.label == 1, device=dv)

    def stress(self, u):
        ue = u[self.pt.edof]
        s = (self.C @ self.B0 @ ue.T).T
        vm = torch.sqrt(0.5 * ((s[:, 0] - s[:, 1]) ** 2 + (s[:, 1] - s[:, 2]) ** 2 + (s[:, 2] - s[:, 0]) ** 2)
                        + 3 * (s[:, 3] ** 2 + s[:, 4] ** 2 + s[:, 5] ** 2) + 1e-12)
        return s, vm

    def tip(self, u, d, hor):
        n, w = self.n, self.w
        uz = u.reshape(-1, 3)[n, 2]
        den = (w * d * d).sum()
        th = -(uz * w * d).sum() / den if float(den) > 0 else 0.0
        return ((u.reshape(-1, 3)[n, hor] * w).sum() + th * self.p.lever).abs()   # 방향 무관 크기

    def __call__(self, out, occ):
        p = self.p
        on = self.solid | ((p_label0 := self.pt.design) & (occ > 0.5))
        J = []
        if p.product == 'bike_mount':
            f = torch.stack([out['f1'][0, 0], out['f2'][0, 0], out['f1'][0, 1], out['f2'][0, 1]])
            fmin = -torch.logsumexp(-f / 2.0, 0) * 2.0                       # 부드러운 최솟값 (KS)
            J.append(('f_min', fmin, 91.2, 'ge'))
            pk = p.conditions['formula']['peak_g']
            vms, syy = [], []
            ok = on & self.far
            for j in range(2):
                s, vm = self.stress(out['u'][0, j] * pk)
                vms.append(torch.quantile(vm[ok], 0.995)); syy.append(torch.quantile(torch.relu(s[ok, 1]), 0.995))
            J.append(('vm', torch.stack(vms).max(), 26.0, 'le'))
            J.append(('interlayer', torch.stack(syy).max(), 10.9, 'le'))
        else:
            names = self.pt.basis_names
            comb = {}
            for case, coef in self.L.items():
                comb[case] = sum(c * out['u'][0, names.index(b)] for b, c in coef.items() if b in names)
            n, w = self.n, self.w
            J.append(('sag', -(comb['gravity'].reshape(-1, 3)[n, 2] * w).sum(), 0.10, 'le'))
            J.append(('utop_fb', self.tip(comb['push_fb'], self.cy, 1), 1.0, 'le'))
            if 'Fx' in self.L['push_lat'] and p.name.startswith('tvfeet'):
                J.append(('sag_lat', -(comb['push_lat'].reshape(-1, 3)[n, 2] * w).sum(), 0.15, 'le'))
            else:
                J.append(('utop_lat', self.tip(comb['push_lat'], self.cx, 0), 1.0, 'le'))
            vm = torch.stack([torch.quantile(self.stress(u)[1][on], 0.995) for u in comb.values()]).max()
            J.append(('vm', vm, 184.0, 'le'))
        return J


def latent_occ(sdf, pt, z, P, tau):
    s = sdf(z, P)[0]
    occ = torch.zeros(pt.g.ne, device=z.device)
    occ = occ.index_put((pt.design.nonzero()[:, 0],), torch.sigmoid(-s / tau))
    return occ


def clean_binary(p, occ):
    """0/1 로 자르고 고정부와 이어진 덩어리만 남김. 반환 (occ_design, 모든 고정부 연결 여부)"""
    fixed = (p.label == 1) | (p.label == 3)
    full = (occ > 0.5) & (p.label == 0) | fixed
    lab, _ = ndimage.label(p.grid.eshape(full)); lab = lab.ravel()
    keep = set(np.unique(lab[fixed])) - {0}
    comps = [set(np.unique(lab[p.fixed_comp == c])) - {0} for c in range(1, p.n_fixed + 1)]
    ok = len(set.intersection(*comps)) > 0
    return np.isin(lab, list(keep)) & (p.label == 0), ok


def optimize(group, cond, sdf_ckpt, pino_net, data, margins=None, n_starts=10, steps=300, lr=2e-2, device='cpu',
             log=print, out_dir=None, verify=True):
    t0 = time.time()
    p = problems.get(group)
    pt = models.ProblemTensors(p, device)
    c = torch.load(sdf_ckpt, map_location=device, weights_only=False)
    sdf = models.DeepSDF(c['n'], c['lo'], c['hi']).to(device)
    sdf.load_state_dict(c['model']); sdf.eval()
    for q in sdf.parameters():
        q.requires_grad_(False)
    for q in pino_net.parameters():
        q.requires_grad_(False)
    margins = margins or {}
    judge = Judge(p, pt, cond)
    P = torch.tensor(np.stack([p.grid.xc, p.grid.yc, p.grid.zc], 1)[p.label == 0], dtype=torch.float32, device=device)
    tau = 0.5 * p.grid.h
    nm = torch.tensor(p.node_mass(cond), dtype=torch.float32, device=device)[None]
    m_fixed = float(p.emass(np.zeros(p.grid.ne)).sum())
    # 시작점: 학습 형상 z 중 FEM 정답상 합격 & 가벼운 것 우선, 나머지 무작위
    Z = c['model']['lat.weight'].to(device)
    starts = []
    try:
        R = datagen.load_fem(data, group)
        pos = {int(i): k for k, i in enumerate(c['idx'])}
        cand = sorted([(e['mass_g'], int(i)) for i, e in zip(R['idx'], R['eval']) if e['pass'] and int(i) in pos])
        starts = [pos[i] for _, i in cand[:n_starts // 2]]
    except Exception:
        pass
    rng = np.random.default_rng(0)
    while len(starts) < n_starts:
        starts.append(int(rng.integers(len(Z))))
    results = []
    for si, s0 in enumerate(starts):
        z = Z[s0].clone()[None].requires_grad_(True)
        opt = torch.optim.Adam([z], lr=lr)
        lam, mu = None, 10.0
        for it in range(steps):
            occ = latent_occ(sdf, pt, z, P, tau)
            out = pino_net(pt, occ[None], node_mass=nm)
            J = judge(out, occ)
            if lam is None:
                lam = torch.zeros(len(J), device=device)
            gs = []
            for name, v, lim, sense in J:
                mg = margins.get(name, 0.05)
                gs.append(1 - v / (lim * (1 + mg)) if sense == 'ge' else v / (lim * (1 - mg)) - 1)
            gv = torch.stack(gs)
            mass = (occ * pt.design.float()).sum() * p.me0
            m0 = float(pt.design.sum()) * p.me0 * 0.1
            obj = mass / m0
            al = (mu / 2) * (torch.relu(lam / mu + gv) ** 2 - (lam / mu) ** 2).sum()
            loss = obj + al + 1e-3 * z.pow(2).sum()
            opt.zero_grad(); loss.backward(); opt.step()
            if (it + 1) % 20 == 0:
                lam = torch.relu(lam + mu * gv.detach())
                mu = min(mu * 1.5, 1e4)
        occ = latent_occ(sdf, pt, z.detach(), P, tau).cpu().numpy()
        ob, conn = clean_binary(p, occ)
        pred = {n: float(v) for n, v, _, _ in J}
        rec = dict(start=int(s0), pred=pred, pred_mass_g=p.mass_g(ob), connected=bool(conn), z=z.detach().cpu().numpy()[0].tolist())
        results.append((ob, rec))
        log(f'  [opt {group}] 시작 {si}: 예측 {json.dumps({k: round(v, 3) for k, v in pred.items()})} 질량 {rec["pred_mass_g"]:.1f} g')
    # FEM 검증: 예측 질량 오름차순
    results.sort(key=lambda r: r[1]['pred_mass_g'])
    best, tried = None, []
    for ob, rec in results:
        if not rec['connected'] or not verify:
            tried.append(rec); continue
        r = labels.fem_label(p, ob, cond)
        rec['fem'] = r['eval']; rec['fem_t'] = r['t']
        tried.append(rec)
        log(f'  [opt {group}] FEM 검증 질량 {r["eval"]["mass_g"]:.1f} g 합격 {r["eval"]["pass"]}')
        if r['eval']['pass']:
            best = (ob, rec); break
    summary = dict(group=group, cond=cond, t=time.time() - t0, status='ok' if best else 'fallback',
                   best=best[1] if best else None, tried=tried)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        tag = f'{group}_' + '_'.join(f'{k}{v:g}' for k, v in sorted(cond.items()))
        with open(os.path.join(out_dir, f'opt_{tag}.json'), 'w') as f:
            json.dump(summary, f, ensure_ascii=False, indent=1, default=float)
        if best:
            np.save(os.path.join(out_dir, f'opt_{tag}.npy'), best[0])
        # 실패한 후보 형상은 재학습 데이터로 (능동 학습)
        fails = [ob for ob, rec in results if rec.get('fem') and not rec['fem']['pass']]
        if fails:
            np.save(os.path.join(out_dir, f'fail_{tag}.npy'), np.packbits(np.stack(fails), axis=1))
    return summary, (best[0] if best else None)
