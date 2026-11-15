"""경로 A — 학습 모델 없이 최적 형상 찾기: 수식 형상 생성 + FEM 직접 계산 (DeepSDF·PINO 학습 전 임시 시연 경로)

DeepSDF·PINO 가 학습되면 `fp08.demo`(대리 모델 경로)로 바꾸면 됩니다. 결과 파일 형식이 같아서 화면(fp08.app)은 그대로입니다.

python -m fp08.fem_opt --out results                                   # 시연 조건 전부 (loop.DEMO)
python -m fp08.fem_opt --out results --groups bike_pad80 --cond phone_mass_g=180,phone_angle_deg=10
옵션: --n 후보 수(기본 거치대 60, TV 30) --refine 다듬기 최대 횟수(기본 10) --workers CPU 작업자 수

순서
  1) 수식 형상 생성: shapes.make_shape (부재·트러스·판·껍데기 + 보강, 시드 고정 → 같은 번호는 항상 같은 형상)
  2) FEM 계산: 후보마다 정적 + 고유진동수 → 기준 판정 (problems.*.evaluate, 학습 데이터 만들 때와 같은 계산)
  3) 합격 후보 중 가벼운 3개 → FEM 다듬기: 힘을 거의 안 받는 칸 지우기(ESO, Xie & Steven 1993) → FEM 재판정,
     합격이면 계속, 불합격이면 지우는 양을 반으로 줄여 한 번 더, 그래도 불합격이면 멈춤
  (11-15) 모든 형상은 FEM 전에 '최소 두께'(격자 2~2.5 mm → 3칸, 5 mm → 2칸)로 굵게 + 홈 메우기,
     ESO 는 감도 필터(이웃 평균)로 지울 칸 선택 → 가는 목·날카로운 홈 방지. --raw 로 끄기
  4) 합격이 하나도 없으면: (어느 형상이든 값이 같은 기준 미달 항목이 있으면 = 형상으로 못 고침 → 표시하고 끝)
     기준에 가장 가까운 후보 3개를 한 칸씩 굵게(최대 3번) → FEM 재판정 → 합격하면 3) 다듬기
  5) 마무리 (11-15): 최소 두께 미만 칸(화면의 빨간 칸)을 채움 → FEM 재판정 (불합격이면 채우기 전 형상 유지)
  6) 가장 가벼운 합격 형상 → <tag>.json·.stl·.png + detail/opt_<tag>.json·.npy → app.html
결과: status ok(합격 형상 있음) / fallback(없음). 질량·판정값은 전부 FEM 값 (예측값 없음).
"""
import os, json, time, argparse
import numpy as np
from multiprocessing import get_context
from scipy import ndimage
from . import problems, labels, shapes, loop

SEED0 = 500000          # 학습 데이터(0~)와 겹치지 않는 형상 번호대
ROBUST = True           # 11-15: 최소 두께·홈 메우기·감도 필터 (--raw 로 끔 = 11-14 동작)


def violation(p, ev):
    """기준을 얼마나 넘었나 (0 = 합격 근처, 클수록 나쁨) — 굵게 할 후보 고르기용"""
    v = 0.0
    for c in p.criteria:
        k = c['id']
        if c['op'] not in ('<=', '>='):
            continue
        x = ev.get(k)
        if k == 'tip':
            t = [ev[q] for q in ('tip_margin_fb', 'tip_margin_lat') if q in ev]
            x = min(t) if t else None
        if x is None or not np.isfinite(x):
            v += 10; continue
        r = x / c['value']
        v += max(0.0, r - 1) if c['op'] == '<=' else max(0.0, 1 / max(r, 1e-6) - 1)
    return v


def shape_independent_fails(p, evals):
    """모든 후보에서 값이 같고(형상과 무관) 기준 미달인 항목 → 어떤 형상으로도 통과 불가 (예: TV 발 길이로 정해지는 넘어짐 여유)"""
    out = []
    for c in p.criteria:
        if c['op'] not in ('<=', '>=') or not evals:
            continue
        keys = ['tip_margin_fb', 'tip_margin_lat'] if c['id'] == 'tip' else [c['id']]
        for q in keys:
            v = [e[q] for e in evals if q in e]
            if len(v) < 2 or np.ptp(v) > 1e-9 * max(1.0, abs(v[0])):
                continue
            bad = v[0] > c['value'] if c['op'] == '<=' else v[0] < c['value']
            if bad:
                out.append(dict(id=c['id'], key=q, label=c['quantity'], op=c['op'], lim=c['value'], value=float(v[0]),
                                how=c.get('how', ''), src=c.get('source', '')))
    return out


def min_cells_of(p):
    """최소 부재 두께(칸). 격자 2~2.5 mm → 3칸(6~7.5 mm), 5 mm → 2칸(10 mm). 육면체 FEM 이 굽힘을 믿을 만하게 풀려면
    두께 방향 칸이 2~3개 이상 필요 (1칸 부재는 실제보다 단단하게 계산됨). 제안값 — min_feature 사용자 미확정"""
    return 3 if p.grid.h <= 2.5 else 2


def _mirror(p, A):
    """대칭 반쪽 → 전체 (모폴로지 연산이 대칭면을 '바깥'으로 착각하지 않게)"""
    if p.sym_axis is None:
        return A, None
    ax = 2 - p.sym_axis
    return np.concatenate([np.flip(A, ax), A], ax), (ax, A.shape[ax])


def _half(A, info):
    if info is None:
        return A
    ax, n = info
    return np.take(A, range(n, 2 * n), axis=ax)


def thin_cells(p, occ, k=None):
    """두께 k칸 미만인 재료 칸 (설계 공간 자체가 그만큼 얇은 곳은 제외). 반환: (ne,) bool"""
    k = k or min_cells_of(p)
    g = p.grid
    se = np.ones((k, k, k), bool)
    A, inf = _mirror(p, g.eshape(occ | (p.label == 1) | (p.label == 3)))
    D, _ = _mirror(p, g.eshape((p.label == 0) | (p.label == 1) | (p.label == 3)))
    room = ndimage.binary_opening(D, se)                       # 설계 공간이 k칸 두께를 허락하는 곳
    thin = A & ~ndimage.binary_opening(A, se) & room
    return _half(thin, inf).ravel() & occ & (p.label == 0)


def robustify(p, cv, occ, k=None, rounds=4):
    """얇은 부재는 굵게, 날카로운 홈은 메움 (설계 공간 안에서만). FEM 판정 전에 적용"""
    k = k or min_cells_of(p)
    if k <= 1:
        return occ
    g = p.grid
    st = ndimage.generate_binary_structure(3, 1)
    Dd, _ = _mirror(p, g.eshape(cv.design))
    for _ in range(rounds):
        A, inf = _mirror(p, g.eshape(occ | cv.fixed))
        A = A | (ndimage.binary_closing(A, st, iterations=1) & Dd)          # 홈·틈 메우기
        occ = _half(A, inf).ravel() & cv.design
        th = thin_cells(p, occ, k)
        if not th.any():
            break
        T, _ = _mirror(p, g.eshape(th))
        grow = ndimage.binary_dilation(T, np.ones((k, k, k), bool)) & Dd     # 얇은 곳 주변을 k칸 폭으로
        occ = occ | (_half(grow, inf).ravel() & cv.design)
    occ = shapes.fill_cavities(cv, occ | cv.fixed) & cv.design
    return shapes.drop_floating(cv, occ)


def open_close(p, cv, occ, k=None):
    """최소 크기 필터 (Sigmund 2007, 모폴로지 열림→닫힘): k칸보다 가는 부재는 없애고, 1칸짜리 홈·틈은 메움.
    다듬기(ESO) 뒤에 사용 — 굵게 채우는 robustify 와 달리 무게를 늘리지 않음. 끊기면 None"""
    k = k or min_cells_of(p)
    g = p.grid
    st = ndimage.generate_binary_structure(3, 1)
    A, inf = _mirror(p, g.eshape(occ | cv.fixed))
    D, _ = _mirror(p, g.eshape(cv.design))
    F, _ = _mirror(p, g.eshape(cv.fixed))
    room = ndimage.binary_opening(D | F, np.ones((k, k, k), bool))
    op = ndimage.binary_opening(A, np.ones((k, k, k), bool))
    A = (op | (A & ~room)) | F                   # 설계 공간 자체가 얇은 곳은 그대로
    A = A | (ndimage.binary_closing(A, st) & D)
    occ = _half(A, inf).ravel() & cv.design
    occ = shapes.fill_cavities(cv, occ | cv.fixed) & cv.design
    occ = shapes.drop_floating(cv, occ)
    return occ if shapes.connected_groups(cv, occ | cv.fixed)[0] else None


def fill_thin(p, cv, occ, k=None, rounds=6):
    """마무리: 최소 두께 미만 칸(화면의 빨간 칸) 주변을 k칸 폭으로 채움 (설계 공간 안에서만). 반환: (occ, 남은 칸 수)"""
    k = k or min_cells_of(p)
    g = p.grid
    Dd, _ = _mirror(p, g.eshape(cv.design))
    se = np.ones((k, k, k), bool)
    for _ in range(rounds):
        th = thin_cells(p, occ, k)
        if not th.any():
            break
        T, inf = _mirror(p, g.eshape(th))
        Dall, _ = _mirror(p, g.eshape(cv.design | cv.fixed | (p.label == 3)))
        ctr = ndimage.binary_dilation(T, se) & ndimage.binary_erosion(Dall, se)   # 그 칸을 덮으면서 설계 공간 안에 온전히 들어가는 k칸 상자들
        occ = occ | (_half(ndimage.binary_dilation(ctr, se) & Dd, inf).ravel() & cv.design)
        occ = shapes.fill_cavities(cv, occ | cv.fixed) & cv.design
    return occ, int(thin_cells(p, occ, k).sum())


def finalize(p, cv, occ, ev, cond, log=print):
    """빨간 칸 채움 → FEM 재판정. 합격이면 채운 형상, 불합격이면 원래 형상. 반환: (occ, ev, 기록)"""
    th0 = int(thin_cells(p, occ).sum())
    if th0 == 0:
        return occ, ev, dict(kind='fill', thin_before=0, thin_after=0, mass_before=ev['mass_g'], mass_after=ev['mass_g'], passed=True, applied=False)
    o2, left = fill_thin(p, cv, occ)
    e2 = _fem(p, o2, cond)
    rec = dict(kind='fill', thin_before=th0, thin_after=left, mass_before=ev['mass_g'], mass_after=e2['mass_g'],
               passed=bool(e2['pass']), applied=bool(e2['pass']))
    log(f'  얇은 곳 채움: {th0} → {left}칸, {ev["mass_g"]:.1f} → {e2["mass_g"]:.1f} g, 합격 {e2["pass"]}'
        + ('' if e2['pass'] else ' → 채우기 전 형상 유지'))
    return (o2, e2, rec) if e2['pass'] else (occ, ev, rec)


def _eval(args):
    """작업자: (그룹, 조건, 번호) → 수식 형상 + FEM 판정"""
    g, cond, idx = args
    p = problems.get(g)
    cv = shapes.Canvas(p)
    occ, meta = shapes.make_shape(p, g, idx, cv)
    rec = dict(idx=int(idx), family=meta.get('family'), connected=bool(meta.get('connected')))
    if not rec['connected']:
        return rec, None
    if ROBUST:
        occ = robustify(p, cv, occ)
        rec['connected'] = bool(shapes.connected_groups(cv, occ | cv.fixed)[0])
        if not rec['connected']:
            return rec, None
    r = labels.fem_label(p, occ, cond)
    rec.update(fem=r['eval'], fem_t=round(r['t'], 2))
    return rec, np.packbits(occ)


def _fem(p, occ, cond):
    return labels.fem_label(p, occ, cond)['eval']


def refine(p, cv, occ, ev, cond, steps=6, frac=0.10, log=print):
    """ESO 한 회씩 → FEM 재판정. 반환: (최종 occ, 최종 eval, 기록 [(질량, 합격)])"""
    from . import eso
    hist = []
    for it in range(steps):
        f, done = frac, False
        for _ in range(2):
            new, lg = eso.eso_prune(p, cv, occ, cond, frac=f, iters=1, filt=ROBUST)
            if ROBUST and not (lg and lg[-1].get('stopped')):
                oc = open_close(p, cv, new)
                if oc is None:                       # 가는 부재를 없애니 끊김 → 덜 지우고 다시
                    f /= 2; continue
                new = oc
            if new.sum() >= occ.sum() or (lg and lg[-1].get('stopped')):
                done = True; break
            e2 = _fem(p, new, cond)
            hist.append(dict(step=it + 1, frac=f, mass_g=e2['mass_g'], passed=bool(e2['pass'])))
            log(f'    다듬기 {it + 1}: {f * 100:.0f}% 지움 → {e2["mass_g"]:.1f} g, 합격 {e2["pass"]}')
            if e2['pass']:
                occ, ev = new, e2; break
            f /= 2
        else:
            done = True
        if done:
            break
    return occ, ev, hist


def thicken(p, cv, occ, cond, times=3, log=print):
    """한 칸씩 굵게 → FEM. 합격하면 반환"""
    hist = []
    for t in range(times):
        occ = ndimage.binary_dilation(p.grid.eshape(occ)).ravel() & cv.design
        if ROBUST:
            occ = robustify(p, cv, occ)
        ev = _fem(p, occ, cond)
        hist.append(dict(step=t + 1, mass_g=ev['mass_g'], passed=bool(ev['pass'])))
        log(f'    굵게 {t + 1}: {ev["mass_g"]:.1f} g, 합격 {ev["pass"]}')
        if ev['pass']:
            return occ, ev, hist
    return None, None, hist


def optimize(g, cond, n=None, refine_steps=6, workers=2, log=print, pool=None):
    t0 = time.time()
    p = problems.get(g)
    cv = shapes.Canvas(p)
    n = n or (60 if p.product == 'bike_mount' else 30)
    jobs = [(g, cond, SEED0 + i) for i in range(n)]
    log(f'[fem_opt] {g} {cond}: 수식 형상 {n}개 → FEM')
    out = pool.map(_eval, jobs, chunksize=1) if pool else [_eval(j) for j in jobs]
    tried, occs = [], {}
    for rec, bits in out:
        tried.append(rec)
        if bits is not None:
            occs[rec['idx']] = np.unpackbits(bits)[:p.grid.ne].astype(bool)
    ok = sorted([r for r in tried if r.get('fem') and r['fem']['pass']], key=lambda r: r['fem']['mass_g'])
    t_search = time.time() - t0
    log(f'  탐색: 합격 {len(ok)}/{len(tried)} ({t_search:.0f} s)')
    fixes = []
    infeasible = shape_independent_fails(p, [r['fem'] for r in tried if r.get('fem')])
    if infeasible:
        log(f'  형상과 무관하게 기준 미달: ' + ', '.join(f"{x['key']}={x['value']:.3f} (기준 {x['op']} {x['lim']})" for x in infeasible)
            + ' → 굵게 보정 생략')
    if not ok and not infeasible:                # 4) 굵게
        near = sorted([r for r in tried if r.get('fem')], key=lambda r: violation(p, r['fem']))[:3]
        for r in near:
            o2, e2, h = thicken(p, cv, occs[r['idx']], cond, log=log)
            fixes.append(dict(idx=r['idx'], kind='thicken', hist=h))
            if o2 is not None:
                occs[r['idx']] = o2; r2 = dict(r, fem=e2, thickened=len(h)); ok.append(r2)
        ok.sort(key=lambda r: r['fem']['mass_g'])
    best = None
    for r in ok[:3]:                             # 3) 다듬기
        log(f'  후보 {r["idx"]} ({r["family"]}) {r["fem"]["mass_g"]:.1f} g 다듬기')
        o2, e2, h = refine(p, cv, occs[r['idx']], r['fem'], cond, steps=refine_steps, log=log)
        fixes.append(dict(idx=r['idx'], kind='refine', start_mass_g=r['fem']['mass_g'], hist=h))
        if best is None or e2['mass_g'] < best[1]['mass_g']:
            best = (o2, e2, r['idx'], occs[r['idx']])
    if best is not None and ROBUST:              # 5) 마무리: 빨간 칸(최소 두께 미만) 채움 → FEM 재판정
        o3, e3, fr = finalize(p, cv, best[0], best[1], cond, log=log)
        fixes.append(dict(fr, idx=best[2]))
        best = (o3, e3, best[2], best[3])
    summ = dict(group=g, cond=cond, method='formula_fem', t=time.time() - t0, t_search=t_search, robust=ROBUST,
                min_cells=min_cells_of(p),
                status='ok' if best else 'fallback', n=n,
                tried=[dict(idx=r['idx'], family=r.get('family'), connected=r['connected'], pred_mass_g=None,
                            fem=None if not r.get('fem') else {k: v for k, v in r['fem'].items() if k != 'pad_min_N'})
                       for r in tried],
                fixes=fixes, infeasible=infeasible, best_idx=None if not best else best[2], best=None if not best else dict(fem=best[1]))
    return summ, (best[0] if best else None), (best[3] if best else None)


def main():
    from .demo import full_mesh, write_stl, render_png, tagof
    from . import app
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='results'); ap.add_argument('--groups', default=None)
    ap.add_argument('--cond', default=None, help='예: phone_mass_g=180,phone_angle_deg=10')
    ap.add_argument('--n', type=int, default=None); ap.add_argument('--refine', type=int, default=10)
    ap.add_argument('--workers', type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument('--raw', action='store_true', help='최소 두께·홈 메우기 끄기 (11-14 동작)'); ap.add_argument('--no-app', action='store_true'); ap.add_argument('--no-stress', action='store_true')
    ap.add_argument('--finalize-only', action='store_true', help='이미 만든 결과(--out)에 마무리(빨간 칸 채움)만 적용')
    a = ap.parse_args()
    if a.finalize_only:
        return finalize_results(a.out, not a.no_app, not a.no_stress)
    global ROBUST
    ROBUST = not a.raw
    os.makedirs(os.path.join(a.out, 'detail'), exist_ok=True)
    groups = a.groups.split(',') if a.groups else list(problems.GROUPS)
    pool = get_context('spawn').Pool(a.workers) if a.workers > 1 else None
    try:
        for g in groups:
            p = problems.get(g)
            conds = [dict(kv.split('=') for kv in a.cond.split(','))] if a.cond else loop.DEMO[g]
            for cond in conds:
                cond = {k: float(v) for k, v in cond.items()}
                s, best, start = optimize(g, cond, a.n, a.refine, a.workers, pool=pool)
                tag = tagof(g, cond)
                json.dump(s, open(os.path.join(a.out, 'detail', f'opt_{tag}.json'), 'w', encoding='utf-8'),
                          ensure_ascii=False, indent=1, default=float)
                fe = (s['best'] or {}).get('fem')
                rec = dict(group=g, cond=cond, method='formula_fem', status=s['status'], sec=round(s['t'], 1),
                           fem=fe, pred=None, margins={})
                if best is not None:
                    np.save(os.path.join(a.out, 'detail', f'opt_{tag}.npy'), best)
                    np.save(os.path.join(a.out, 'detail', f'start_{tag}.npy'), start)     # 다듬기 전 (화면 전·후 비교)
                    V, F = full_mesh(p, best); write_stl(os.path.join(a.out, tag + '.stl'), V, F)
                    render_png(os.path.join(a.out, tag + '.png'), p, best, f"{g} {cond}\n{fe['mass_g']:.0f} g · FEM 합격")
                json.dump(rec, open(os.path.join(a.out, tag + '.json'), 'w', encoding='utf-8'),
                          ensure_ascii=False, indent=1, default=float)
                print(f'[fem_opt] {tag}: {s["status"]} {rec["sec"]} s' + (f', {fe["mass_g"]:.1f} g' if fe else ''), flush=True)
    finally:
        if pool:
            pool.close()
    if not a.no_app:
        app.build(a.out, None, None, not a.no_stress)


def finalize_results(out, make_app=True, stress=True):
    """기존 결과 폴더에 마무리만 적용 (탐색·다듬기 다시 안 함)"""
    import glob
    from .demo import full_mesh, write_stl, render_png
    from . import app
    for jf in sorted(glob.glob(os.path.join(out, '*.json'))):
        rec = json.load(open(jf, encoding='utf-8'))
        if rec.get('status') != 'ok' or rec.get('method') != 'formula_fem':
            continue
        tag = os.path.basename(jf)[:-5]
        npf, dj = os.path.join(out, 'detail', f'opt_{tag}.npy'), os.path.join(out, 'detail', f'opt_{tag}.json')
        if not os.path.exists(npf):
            continue
        p, cond = problems.get(rec['group']), rec['cond']
        cv = shapes.Canvas(p)
        t0 = time.time()
        print(f'[fem_opt] {tag}: 마무리', flush=True)
        occ, ev, fr = finalize(p, cv, np.load(npf) > 0.5, rec['fem'], cond)
        d = json.load(open(dj, encoding='utf-8'))
        d['fixes'] = [x for x in d.get('fixes', []) if x.get('kind') != 'fill'] + [dict(fr, idx=d.get('best_idx'))]
        d['best'] = dict(fem=ev)
        json.dump(d, open(dj, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
        if fr['applied']:
            np.save(npf, occ)
            V, F = full_mesh(p, occ); write_stl(os.path.join(out, tag + '.stl'), V, F)
            render_png(os.path.join(out, tag + '.png'), p, occ, f"{rec['group']} {cond}\n{ev['mass_g']:.0f} g · FEM 합격")
            rec['fem'] = ev
        rec['sec'] = round(rec.get('sec', 0) + time.time() - t0, 1)
        json.dump(rec, open(jf, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    if make_app:
        app.build(out, None, None, stress)


if __name__ == '__main__':
    main()
