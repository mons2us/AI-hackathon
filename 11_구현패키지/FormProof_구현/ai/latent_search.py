"""잠재 공간 역설계: 형상 AI(z → 형상) × 물리 AI(형상 → 성능), 미분으로 '가볍고 기준을 지키는' 형상을 찾는다.

  최소화  무게(정확식)  +  벌점 Σ max(0, 위반)^2
  제약    f1 ≥ FT,  폰 온도 상승 ≤ TLIM,  터치 처짐 ≤ DLIM,  충격 응력 ≤ SLIM   (설계 명세 JSON 에서 읽음)
  시작점  학습 데이터 중 기준을 지키는 가장 가벼운 형상들의 z

3D 프린팅(11-18): 탐색 중 '아래가 빈 칸' 벌점(--wp, ai/printable.py) + 후보 저장 전 45° 보정(engine/printability.py).
출력: 후보마다 엔진 형식 밀도 파일(cand_k.npy, 요소 배열, 고정 부품 포함) → 검증 관문에서 FEM 재계산:
  cd engine && GRIP=2 NX=88 MSYS=0.311 MODE=eval RHO=../runs/cand_0.npy TAG=cand0 python3 opt_int.py
사용:
  python -m ai.latent_search --meta data/grid_meta.npz --sdf runs/sdf.pt --phys runs/fno.pt --data 'data/shards/*.npz' --spec spec/bike_mount_targets.json --out runs/
"""
import argparse, json, os, sys, numpy as np, torch
from .data import Grid, load_shards, G_PER_CELL
from .deepsdf import ShapeAI
from .surrogate import Surrogate
from .printable import PrintPenalty
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'engine'))
import printability as _pr   # 11-18: 3D 프린터(FDM) 45° 규칙 — 탐색 중 벌점(--wp) + 후보 저장 전 보정(make_self_supporting)


def finalize(r, a, info):
    """후보(엔진 형식 0/1)를 출력 가능하게 보정하고 결과 정보에 기록. --no_print_fix 이면 검사만"""
    pm = _pr.load_meta(a.meta); before, _ = _pr.check(r, pm, fixed_ok=True)
    if not a.no_print_fix:
        r2, added, trimmed = _pr.make_self_supporting(r, pm)
        r = np.where(pm['design'], r2, r)
    else: added = trimmed = 0
    after, _ = _pr.check(r, pm, fixed_ok=True)
    info['print'] = dict(need_before=before['need_support_in_design'], need_after=after['need_support_in_design'],
                         added_cells=int(added), added_g=round(added * G_PER_CELL, 2), trimmed_cells=int(trimmed))
    return r

def penx(y, tg):
    """물리 AI 가 추가값(--ext, 18개 출력)도 예측하면: 층간 응력(위아래 · 앞뒤) ≤ 한도, 터치 아래 · 충격 앞뒤도 같이 제약. 아니면 0"""
    if y.shape[-1] <= 7: return 0.
    IL = tg.get('shock_interlayer_max_mpa', 1e9); SL = tg['shock_vm_max_mpa']; DL = tg['touch_max_mm']
    return (torch.relu(y[16] - IL) / IL * 10 + torch.relu(y[17] - IL) / IL * 10 + torch.relu(y[15] - SL) / SL * 10 + torch.relu(y[5] - DL) / DL * 10)

def main(a):
    grid = Grid(a.meta); S = ShapeAI(a.sdf, grid); M = Surrogate(a.phys, grid, S.dev); tg = json.load(open(a.spec))
    FT, TL, DL, SL = tg['f1_min_hz'], tg['phone_Tmax_rise_max_c'], tg['touch_max_mm'], tg['shock_vm_max_mpa']
    D = load_shards(a.data, grid, fields=False); lab = D['lab']
    name2z = {n: i for i, n in enumerate(S.names)}
    known = np.array([n in name2z for n in D['names']])   # 이 형상 AI 가 학습한 형상만 출발점으로 (다른 데이터로 학습한 형상 AI 와 섞어 쓸 때)
    ok = (lab[:, 1] >= FT) & (lab[:, 3] <= TL) & (lab[:, 4] <= DL) & (lab[:, 6] <= SL) & known
    pool = np.where(ok)[0] if ok.any() else np.where(known)[0][np.argsort(-lab[known, 1])][:a.k]
    starts = pool[np.argsort(lab[pool, 0])][:a.k]
    os.makedirs(a.out, exist_ok=True); res = []; PP = PrintPenalty(grid, a.meta)
    for k, s in enumerate(starts):
        z = S.Z[name2z[D['names'][s]]].clone().to(S.dev)[None].requires_grad_(True); opt = torch.optim.Adam([z], lr=a.lr)
        for it in range(a.iters):
            o = S.decode(z, sharp=2.0); y = M.predict(o)['scalars'][0]
            pen = torch.relu(FT - y[1]) / FT * 10 + torch.relu(y[3] - TL) / TL * 10 + torch.relu(y[4] - DL) / DL * 10 + torch.relu(y[6] - SL) / SL * 10 + penx(y, tg)
            loss = y[0] + a.w * pen ** 2 + 1e-3 * (z ** 2).sum() + a.wp * G_PER_CELL * PP(o)[0]   # 아래가 빈 칸 1개 = 무게 wp 배
            opt.zero_grad(); loss.backward(); opt.step()
        with torch.no_grad(): o = S.decode(z, sharp=2.0); y = M.predict(o)['scalars'][0].cpu().numpy()
        r = np.where(grid.design, 0.0, grid.solid.astype(float)); r[grid.didx] = (o[0].cpu().numpy() > 0.5).astype(float)
        info = dict(start=str(D['names'][s]), start_mass=float(lab[s, 0]), pred=dict(zip(['mass_g', 'f1_hz', 'f2_hz', 'Tmax', 'touch_top', 'touch_bot', 'shock_vm'], map(float, y))))
        r = finalize(r, a, info)   # 예측값(pred)은 보정 전 형상 기준 → FEM 검증 관문이 보정 후 형상으로 다시 판정
        f = os.path.join(a.out, f'cand_{k}.npy'); np.save(f, r)
        res.append(dict(cand=f, **info))
        print(json.dumps(res[-1]), flush=True)
    json.dump(res, open(os.path.join(a.out, 'latent_search.json'), 'w'), indent=1)

def trace_run(a):
    """시연용 (11-16 추가): 주어진 시작 형상(--start_rho, 예: 처음 설계)에 z 를 맞춘 뒤 같은 목적 · 벌점으로 최적화하며
    --trace_every 회마다 z · 예측값을 저장 → scripts/demo_trace.py 가 프레임(형상 + 분포)으로 그림.
    출력: <out>/trace.npz (Z, it, pred, pen, fit_iou), <out>/cand_trace.npy (마지막 형상, 엔진 형식) → FEM 검증"""
    import torch.nn.functional as F
    from .deepsdf import iou
    grid = Grid(a.meta); S = ShapeAI(a.sdf, grid); M = Surrogate(a.phys, grid, S.dev); tg = json.load(open(a.spec))
    FT, TL, DL, SL = tg['f1_min_hz'], tg['phone_Tmax_rise_max_c'], tg['touch_max_mm'], tg['shock_vm_max_mpa']
    r0 = np.load(a.start_rho).ravel(); tgt = torch.as_tensor((r0[grid.didx] > 0.5).astype(np.float32), device=S.dev)
    z = S.Z.mean(0, keepdim=True).clone().to(S.dev).requires_grad_(True); opt = torch.optim.Adam([z], lr=5e-3)
    for it in range(a.fit_steps):   # 1) 시작 형상에 z 맞추기 (디코더 고정, deepsdf fit 과 같은 방식)
        idx = torch.randint(0, grid.nd, (16384,), device=S.dev); lg = S.dec(z, S.P[idx])[0]
        loss = F.binary_cross_entropy_with_logits(lg, tgt[idx]) + 1e-4 * (z ** 2).mean(); opt.zero_grad(); loss.backward(); opt.step()
    with torch.no_grad(): fit_iou = iou(S.decode(z)[0].cpu().numpy(), tgt.cpu().numpy())
    print(json.dumps(dict(fit_iou=round(fit_iou, 3), note='시작 형상을 형상 AI 로 다시 그린 겹침 비율')), flush=True)
    z = z.detach().clone().requires_grad_(True); opt = torch.optim.Adam([z], lr=a.lr); Zs, its, preds, pens = [], [], [], []; PP = PrintPenalty(grid, a.meta)
    for it in range(a.iters + 1):   # 2) 최적화 (main 과 같은 목적 · 벌점)
        o = S.decode(z, sharp=2.0); y = M.predict(o)['scalars'][0]
        pen = torch.relu(FT - y[1]) / FT * 10 + torch.relu(y[3] - TL) / TL * 10 + torch.relu(y[4] - DL) / DL * 10 + torch.relu(y[6] - SL) / SL * 10 + penx(y, tg)
        if it % a.trace_every == 0 or it == a.iters:
            Zs.append(z.detach().cpu().numpy()[0].copy()); its.append(it); preds.append(y.detach().cpu().numpy()); pens.append(float(pen))
        if it == a.iters: break
        loss = y[0] + a.w * pen ** 2 + 1e-3 * (z ** 2).sum() + a.wp * G_PER_CELL * PP(o)[0]; opt.zero_grad(); loss.backward(); opt.step()
    os.makedirs(a.out, exist_ok=True)
    np.savez(os.path.join(a.out, 'trace.npz'), Z=np.array(Zs), it=np.array(its), pred=np.array(preds), pen=np.array(pens), fit_iou=fit_iou,
             start_rho=a.start_rho, targets=json.dumps(tg))
    with torch.no_grad(): o = S.decode(torch.as_tensor(Zs[-1], device=S.dev), sharp=2.0)
    r = np.where(grid.design, 0.0, grid.solid.astype(float)); r[grid.didx] = (o[0].cpu().numpy() > 0.5).astype(float)
    info = {}; r = finalize(r, a, info)
    np.save(os.path.join(a.out, 'cand_trace.npy'), r)
    print(json.dumps(dict(frames=len(Zs), print=info['print'], last_pred=dict(zip(['mass_g', 'f1_hz', 'f2_hz', 'Tmax', 'touch_top', 'touch_bot', 'shock_vm'], map(float, preds[-1]))))), flush=True)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    for k in ['meta', 'sdf', 'phys', 'spec', 'out']: p.add_argument('--' + k, required=True)
    p.add_argument('--data', default=None, help='학습 데이터 샤드 (기본 모드에서 필수)')
    p.add_argument('--k', type=int, default=6); p.add_argument('--iters', type=int, default=200); p.add_argument('--lr', type=float, default=0.02); p.add_argument('--w', type=float, default=3.0)
    p.add_argument('--start_rho', default=None, help='시연용: 이 형상(엔진 요소 배열 .npy)에서 출발해 경로 기록 (trace_run)')
    p.add_argument('--wp', type=float, default=5.0, help='3D 프린팅 벌점: 아래가 빈 칸 1개를 그 무게의 몇 배로 칠지 (0 = 끔)')
    p.add_argument('--no_print_fix', action='store_true', help='후보 저장 전 45° 보정을 하지 않음 (검사 결과만 기록)')
    p.add_argument('--trace_every', type=int, default=5); p.add_argument('--fit_steps', type=int, default=1500)
    a = p.parse_args()
    if a.start_rho: trace_run(a)
    else:
        assert a.data, '--data 필요'; main(a)
