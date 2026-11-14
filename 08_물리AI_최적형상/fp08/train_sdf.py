"""DeepSDF 학습 (그룹마다 1개) — 체크포인트·이어하기·시간 한도.

python -m fp08.train_sdf --group bike_pad80 --data data --out runs --steps 20000 --device cuda
검증: 학습에 안 쓴 10% 형상의 z 를 디코더 고정 상태로 찾아서(200 스텝) 격자 IoU 측정.
"""
import os, json, time, argparse
import numpy as np
import torch
from . import problems, datagen, models, shapes


def load_group(data, group):
    d = os.path.join(data, group)
    fs = sorted(f for f in os.listdir(d) if f.startswith('shapes_') and f.endswith('.npz') and '.tmp' not in f)
    X, S, idx, meta = [], [], [], []
    for f in fs:
        z = np.load(os.path.join(d, f))
        X.append(z['sdf_xyz']); S.append(z['sdf']); idx.append(z['idx']); meta += json.loads(str(z['meta']))
    return np.concatenate(idx), np.concatenate(X).astype(np.float32), np.concatenate(S).astype(np.float32), meta


def split(idx, frac=0.1):
    """번호로 결정되는 고정 분할 (다시 실행해도 같음)"""
    h = np.array([shapes.seed_of('split', int(i)) % 1000 for i in idx])
    return h >= frac * 1000, h < frac * 1000


def grid_iou(p, model, z, occ_full, device):
    g = p.grid
    P = torch.tensor(np.stack([g.xc, g.yc, g.zc], 1), dtype=torch.float32, device=device)
    with torch.no_grad():
        s = torch.cat([model(z, P[i:i + 20000])[0] for i in range(0, len(P), 20000)]).cpu().numpy()
    reg = p.label == 0
    a, b = (s < 0) & reg, occ_full & reg
    return float((a & b).sum() / max((a | b).sum(), 1))


def infer_z(model, X, S, steps=200, lr=5e-3, device='cpu', n0=None):
    """디코더 고정, z 만 최적화 (새 형상 → z)"""
    z = torch.zeros(len(X), model.zdim, device=device, requires_grad=True)
    opt = torch.optim.Adam([z], lr=lr)
    Xt, St = torch.tensor(X, device=device), torch.tensor(S, device=device)
    for _ in range(steps):
        sel = torch.randint(0, Xt.shape[1], (1024,), device=device)
        pred = model(z, Xt[:, sel])
        loss = (pred - St[:, sel]).abs().mean() + 1e-4 * z.pow(2).sum(1).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    return z.detach()


def train(group, data, out, steps=20000, bs=32, npts=1024, lr=5e-4, device='cpu', time_limit=None, log=print,
          eval_every=2000, width=128, depth=4, nfreq=0, subset=None, tag='sdf', n_eval=8):
    t0 = time.time()
    p = problems.get(group)
    idx, X, S, meta = load_group(data, group)
    if subset:                                     # 비교 실험: 앞에서부터 subset 개만
        idx, X, S, meta = idx[:subset], X[:subset], S[:subset], meta[:subset]
    tr, va = split(idx)
    od = os.path.join(out, tag, group); os.makedirs(od, exist_ok=True)
    ck = os.path.join(od, 'ckpt.pt')
    g = p.grid
    reg = p.label != 2
    lo = np.array([g.xc[reg].min(), g.yc[reg].min(), g.zc[reg].min()]) - g.h
    hi = np.array([g.xc[reg].max(), g.yc[reg].max(), g.zc[reg].max()]) + g.h
    model = models.DeepSDF(len(idx), lo, hi, width=width, depth=depth, nfreq=nfreq).to(device)
    opt = torch.optim.Adam([{'params': model.net.parameters(), 'lr': lr},
                            {'params': model.lat.parameters(), 'lr': lr * 2}])
    step, hist = 0, []
    if os.path.exists(ck):
        c = torch.load(ck, map_location=device, weights_only=False)
        if c['n'] == len(idx):
            model.load_state_dict(c['model']); opt.load_state_dict(c['opt']); step, hist = c['step'], c['hist']
            log(f'[sdf {group}] 이어하기 step {step}')
    Xt = torch.tensor(X, device=device); St = torch.tensor(S, device=device)
    tri = torch.tensor(np.where(tr)[0], device=device)
    sched = lambda s: 0.5 ** (s / (steps / 3))
    while step < steps:
        b = tri[torch.randint(0, len(tri), (bs,), device=device)]
        sel = torch.randint(0, Xt.shape[1], (bs, npts), device=device)
        x = torch.gather(Xt[b], 1, sel[..., None].expand(-1, -1, 3))
        s = torch.gather(St[b], 1, sel)
        pred = model(model.lat(b), x)
        loss = (pred - s).abs().mean() + 1e-4 * model.lat(b).pow(2).sum(1).mean()
        for gp, base in zip(opt.param_groups, [lr, 2 * lr]):
            gp['lr'] = base * sched(step)
        opt.zero_grad(); loss.backward(); opt.step()
        step += 1
        if step % eval_every == 0 or step == steps:
            rec = dict(step=step, loss=float(loss), t=time.time() - t0)
            # 학습 형상 IoU (z 저장값) / 검증 형상 IoU (z 추론)
            p_occ = datagen.load_shapes(data, group)[1]
            fixed = (p.label == 1) | (p.label == 3)
            tri_np = np.where(tr)[0][:8]; vai = np.where(va)[0][:n_eval]
            rec['iou_train'] = float(np.mean([grid_iou(p, model, model.lat.weight[i:i + 1].detach(), p_occ[i] | fixed, device) for i in tri_np]))
            if len(vai):
                zv = infer_z(model, X[vai], S[vai], device=device)
                rec['iou_val'] = float(np.mean([grid_iou(p, model, zv[k:k + 1], p_occ[i] | fixed, device) for k, i in enumerate(vai)]))
                with torch.no_grad():                       # 표면 근처 점의 거리 오차 (mm): |예측 s − 정답 s|, 정답 |s| < 1칸 인 점
                    xs = torch.tensor(X[vai][:, :2000], device=device); ss = torch.tensor(S[vai][:, :2000], device=device)
                    pr = model(zv, xs); msk = ss.abs() < p.grid.h
                    rec['surf_err_mm'] = float((pr - ss).abs()[msk].mean())
            hist.append(rec)
            log(f'[{tag} {group}] {json.dumps(rec)}', flush=True) if log is print else log(f'[{tag} {group}] {json.dumps(rec)}')
            torch.save(dict(model=model.state_dict(), opt=opt.state_dict(), step=step, hist=hist, n=len(idx),
                            idx=idx, lo=lo, hi=hi, cfg=model.cfg), ck + '.tmp')
            os.replace(ck + '.tmp', ck)
        if time_limit and time.time() > time_limit:
            log(f'[sdf {group}] 시간 한도 도달 step {step}')
            break
    return model, hist


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--group', required=True)
    ap.add_argument('--data', default='data'); ap.add_argument('--out', default='runs')
    ap.add_argument('--steps', type=int, default=20000); ap.add_argument('--bs', type=int, default=32)
    ap.add_argument('--device', default='cuda' if torch.cuda.is_available() else 'cpu')
    ap.add_argument('--eval-every', type=int, default=2000)
    ap.add_argument('--width', type=int, default=128); ap.add_argument('--depth', type=int, default=4)
    ap.add_argument('--nfreq', type=int, default=0); ap.add_argument('--subset', type=int, default=None)
    ap.add_argument('--npts', type=int, default=1024); ap.add_argument('--tag', default='sdf'); ap.add_argument('--n-eval', type=int, default=8)
    a = ap.parse_args()
    train(a.group, a.data, a.out, a.steps, a.bs, npts=a.npts, device=a.device, eval_every=a.eval_every, width=a.width,
          depth=a.depth, nfreq=a.nfreq, subset=a.subset, tag=a.tag, n_eval=a.n_eval)
