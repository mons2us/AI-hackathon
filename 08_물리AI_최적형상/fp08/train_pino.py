"""PINO 학습 (제품마다 1개) — 정답 있는 형상(데이터+물리 손실) + 정답 없는 형상(물리 손실만).

python -m fp08.train_pino --product bike --data data --out runs --steps 30000 --device cuda:0
python -m fp08.train_pino --product bike --no-physics --tag fno ...      # FNO 비교(물리 손실 없음)
python -m fp08.train_pino --product bike --freq direct --tag direct ...  # 레일리 대신 직접 회귀 비교
"""
import os, json, time, argparse
import numpy as np
import torch
from . import problems, datagen, models, train_sdf

PRODUCTS = {'bike': ['bike_pad50', 'bike_pad80', 'bike_pad120'],
            'tvfeet': ['tvfeet_L300', 'tvfeet_L220'],
            'tvped': ['tvped']}
MODES = {'bike': (12, 5, 10), 'tvfeet': (4, 16, 12), 'tvped': (10, 12, 6)}
FREQ_PAIRS = {'bike': 2, 'tvfeet': 0, 'tvped': 0}


class GroupData:
    def __init__(self, group, data, device):
        self.group = group
        self.p = p = problems.get(group)
        self.pt = models.ProblemTensors(p, device)
        self.device = device
        R = datagen.load_fem(data, group)
        self.idx = R['idx']; self.U = R['U']; self.freq = R['freq']; self.eval = R['eval']; self.cond = R['cond']
        self.occ = R['occ']
        tr, va, te = train_sdf.split3(self.idx)
        self.tr, self.va, self.te = np.where(tr)[0], np.where(va)[0], np.where(te)[0]
        # 정답 없는 형상 (물리 손실 전용)
        sidx, socc, smeta = datagen.load_shapes(data, group)
        lab = set(self.idx.tolist())
        keep = [k for k, (i, m) in enumerate(zip(sidx, smeta)) if int(i) not in lab and m.get('connected', True)]
        self.u_idx, self.u_occ = sidx[keep], socc[keep]
        self.u_cond = [datagen.cond_of(p, group, int(i)) for i in self.u_idx]

    def batch_inputs(self, occ, conds):
        p, dv = self.p, self.device
        occ_t = torch.tensor(np.asarray(occ, np.float32), device=dv)
        nm = torch.tensor(np.stack([p.node_mass(c) for c in conds]), dtype=torch.float32, device=dv)
        Fb = torch.tensor(np.stack([np.stack([b[2] for b in p.basis(c)]) for c in conds]), dtype=torch.float32, device=dv)
        return occ_t, nm, Fb

    def target_u(self, k):
        U = torch.tensor(self.U[k].astype(np.float32), device=self.device)       # (B, C, NX, NY, NZ)
        B, nb = U.shape[0], U.shape[1] // 3
        return self.pt.n_flat(U.reshape(B, nb, 3, *U.shape[2:])).permute(0, 1, 3, 2).reshape(B, nb, -1)


def u_reference(gds):
    rms = []
    for gd in gds:
        if len(gd.tr):
            u = gd.target_u(gd.tr[:64])
            rms.append(u.pow(2).mean(-1).sqrt().cpu().numpy())
    return np.median(np.concatenate(rms), 0)


def predict(net, gd, occ, conds, with_grad=False):
    occ_t, nm, Fb = gd.batch_inputs(occ, conds)
    with torch.set_grad_enabled(with_grad):
        return net(gd.pt, occ_t, node_mass=nm), occ_t, nm, Fb


def to_res(gd, out, b, occ):
    """모델 출력 → problems.evaluate 가 받는 형식"""
    U = {n: out['u'][b, j].double().cpu().numpy() for j, n in enumerate(gd.pt.basis_names)}
    fr = {}
    if 'f1' in out:
        f1, f2 = out['f1'][b].cpu().numpy(), out['f2'][b].cpu().numpy()
        fr = {'S': np.array([f1[0], f2[0]]), 'A': np.array([f1[1], f2[1]])}
    return dict(U=U, freq=fr, occ=np.asarray(occ, float))


def validate(net, gd, ks=None, max_n=200):
    """검증 지표: 변위장 상대 L2, 진동수 오차, 판정값 오차"""
    ks = gd.va if ks is None else ks
    ks = ks[:max_n]
    rel, fe, je = [], [], {}
    for s in range(0, len(ks), 4):
        k = ks[s:s + 4]
        out, *_ = predict(net, gd, gd.occ[k], [gd.cond[i] for i in k])
        ut = gd.target_u(k)
        rel.append(((out['u'] - ut).norm(dim=-1) / (ut.norm(dim=-1) + 1e-30)).cpu().numpy())
        if 'f1' in out:
            fp = torch.stack([out['f1'][:, 0], out['f2'][:, 0], out['f1'][:, 1], out['f2'][:, 1]], 1).cpu().numpy()
            fe.append(fp / gd.freq[k] - 1)
        for b, i in enumerate(k):
            ev = gd.p.evaluate(to_res(gd, out, b, gd.occ[i]), gd.cond[i])
            for q, v in ev.items():
                if isinstance(v, float) and q in gd.eval[i] and abs(gd.eval[i][q]) > 1e-12:
                    je.setdefault(q, []).append(v / gd.eval[i][q] - 1)
    rel = np.concatenate(rel) if rel else np.zeros((0, 1))
    m = dict(n=int(len(ks)), relL2_mean=float(rel.mean()) if rel.size else None,
             relL2_p90=float(np.percentile(rel, 90)) if rel.size else None)
    if fe:
        fe = np.concatenate(fe)
        m['freq_within5_frac'] = float((np.abs(fe) <= 0.05).mean())
        m['freq_abs_p95'] = float(np.percentile(np.abs(fe), 95))
    m['judge_abs_p90'] = {q: float(np.percentile(np.abs(v), 90)) for q, v in je.items()}
    return m


def train(product, data, out, steps=30000, bs=4, bs_u=2, lr=1e-3, device='cpu', physics=True, freq_mode='rayleigh',
          tag='pino', width=24, time_limit=None, log=print, eval_every=1000, w_phys=0.1, groups=None, modes_scale=1.0,
          stop_at=None):
    """stop_at: 학습률 일정은 steps 기준, stop_at 스텝에서 멈춤 (sweep 1차 거르기). 이어하기는 저장된 설정(cfg)을 따름"""
    t0 = time.time()
    gds = [GroupData(g, data, device) for g in PRODUCTS[product] if not groups or g in groups]   # groups: 일부 그룹만(시험용)
    nb = len(gds[0].pt.basis_names)
    nfp = FREQ_PAIRS[product]
    od = os.path.join(out, tag, product); os.makedirs(od, exist_ok=True)
    ck = os.path.join(od, 'ckpt.pt')
    if os.path.exists(ck):                          # 이어하기: 저장된 설정으로 (sweep 으로 고른 설정이 능동학습 재학습에도 유지됨)
        cf = torch.load(ck, map_location='cpu', weights_only=False)['cfg']
        width, physics, freq_mode = cf['width'], cf['physics'], cf['freq_mode']
        w_phys, lr, modes = cf.get('w_phys', w_phys), cf.get('lr', lr), tuple(cf['modes'])
    else:
        modes = tuple(max(2, int(round(m * modes_scale))) for m in MODES[product])
    net = models.PINO(nb, n_freq_pairs=nfp, width=width, modes=modes, cin=9).to(device)
    net.freq_mode = freq_mode
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    step, hist = 0, []
    if os.path.exists(ck):
        c = torch.load(ck, map_location=device, weights_only=False)
        net.load_state_dict(c['model']); opt.load_state_dict(c['opt']); step, hist = c['step'], c['hist']
        log(f'[{tag} {product}] 이어하기 step {step}')
    else:
        net.u_ref.copy_(torch.tensor(u_reference(gds), dtype=torch.float32))
    w = np.array([len(gd.tr) for gd in gds], float); w /= w.sum()
    rng = np.random.default_rng(step)
    end = min(steps, stop_at) if stop_at else steps
    while step < end:
        gd = gds[rng.choice(len(gds), p=w)]
        k = rng.choice(gd.tr, min(bs, len(gd.tr)), replace=False)
        out, occ_t, nm, Fb = predict(net, gd, gd.occ[k], [gd.cond[i] for i in k], with_grad=True)
        ut = gd.target_u(k)
        # 모양과 크기를 따로 학습: 상대 L2 하나로 묶으면 모양이 틀린 초기에 크기를 0으로 줄이는 쪽으로
        # 붕괴함(리허설에서 log 크기 −60 까지 떨어짐) → 모양 손실(정규화 L2) + 크기 손실(log rms)
        trms = ut.pow(2).mean(-1).sqrt() + 1e-30
        l_shape = (out['un'] - ut / trms[..., None]).pow(2).mean(-1).sqrt().mean()
        l_scale = (out['logs'] - torch.log(trms / net.u_ref)).abs().mean()
        l_data = l_shape + l_scale
        loss = l_data
        rec = dict(shape=float(l_shape.detach()), scale=float(l_scale.detach()))
        if nfp:
            ft = torch.tensor(gd.freq[k], dtype=torch.float32, device=device)
            fp = torch.stack([out['f1'][:, 0], out['f2'][:, 0], out['f1'][:, 1], out['f2'][:, 1]], 1)
            l_f = (torch.log(fp) - torch.log(ft)).abs().mean()
            loss = loss + l_f; rec['freq'] = float(l_f)
        if physics:
            ks_ = gd.pt.kscale(occ_t)
            lp = torch.stack([gd.pt.residual(ks_, out['u'][:, j], Fb[:, j], gd.pt.free[j]) for j in range(nb)]).mean()
            if len(gd.u_idx) and bs_u:
                ku = rng.choice(len(gd.u_idx), min(bs_u, len(gd.u_idx)), replace=False)
                ou, ocu, nmu, Fu = predict(net, gd, gd.u_occ[ku], [gd.u_cond[i] for i in ku], with_grad=True)
                ksu = gd.pt.kscale(ocu)
                lp = lp + torch.stack([gd.pt.residual(ksu, ou['u'][:, j], Fu[:, j], gd.pt.free[j]) for j in range(nb)]).mean()
            loss = loss + w_phys * lp; rec['phys'] = float(lp)
        for gp in opt.param_groups:
            gp['lr'] = lr * 0.5 ** (step / (steps / 4))
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(net.parameters(), 1.0)
        opt.step(); step += 1
        if step % eval_every == 0 or step == end:
            net.eval()
            vm = {gd.group: validate(net, gd) for gd in gds}
            net.train()
            h = dict(step=step, t=round(time.time() - t0, 1), train=rec, val=vm)
            hist.append(h)
            log(f'[{tag} {product}] {json.dumps(h, ensure_ascii=False)}', flush=True) if log is print else log(f'[{tag} {product}] {json.dumps(h, ensure_ascii=False)}')
            torch.save(dict(model=net.state_dict(), opt=opt.state_dict(), step=step, hist=hist,
                            cfg=dict(product=product, nb=nb, nfp=nfp, width=width, modes=list(modes),
                                     physics=physics, freq_mode=freq_mode, w_phys=w_phys, lr=lr)), ck + '.tmp')
            os.replace(ck + '.tmp', ck)
        if time_limit and time.time() > time_limit:
            log(f'[{tag} {product}] 시간 한도 도달 step {step}')
            break
    return net, hist


def load(out, tag, product, device='cpu'):
    c = torch.load(os.path.join(out, tag, product, 'ckpt.pt'), map_location=device, weights_only=False)
    cf = c['cfg']
    net = models.PINO(cf['nb'], n_freq_pairs=cf['nfp'], width=cf['width'], modes=tuple(cf['modes']), cin=9).to(device)
    net.load_state_dict(c['model']); net.freq_mode = cf.get('freq_mode', 'rayleigh'); net.eval()
    return net, c


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--product', required=True, choices=list(PRODUCTS))
    ap.add_argument('--data', default='data'); ap.add_argument('--out', default='runs')
    ap.add_argument('--steps', type=int, default=30000); ap.add_argument('--bs', type=int, default=4)
    ap.add_argument('--width', type=int, default=24)
    ap.add_argument('--no-physics', action='store_true'); ap.add_argument('--freq', default='rayleigh', choices=['rayleigh', 'direct'])
    ap.add_argument('--tag', default='pino')
    ap.add_argument('--device', default='cuda' if torch.cuda.is_available() else 'cpu')
    ap.add_argument('--eval-every', type=int, default=1000)
    ap.add_argument('--groups', default=None, help='쉼표로 구분, 일부 그룹만 학습(시험용)')
    ap.add_argument('--lr', type=float, default=1e-3); ap.add_argument('--w-phys', type=float, default=0.1)
    ap.add_argument('--modes-scale', type=float, default=1.0); ap.add_argument('--stop-at', type=int, default=None)
    a = ap.parse_args()
    train(a.product, a.data, a.out, a.steps, a.bs, device=a.device, physics=not a.no_physics, freq_mode=a.freq,
          tag=a.tag, width=a.width, eval_every=a.eval_every, groups=a.groups.split(',') if a.groups else None,
          lr=a.lr, w_phys=a.w_phys, modes_scale=a.modes_scale, stop_at=a.stop_at)
