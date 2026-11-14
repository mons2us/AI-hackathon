"""데이터 생성 — 형상(+SDF 점)과 FEM 정답을 묶음(shard) 단위로 만든다. 끊겨도 이어서 실행.

사용 예
  python -m fp08.datagen shapes --group bike_pad80 --n 5000 --workers 32 --out data
  python -m fp08.datagen fem    --group bike_pad80 --n 1000 --workers 32 --out data
  python -m fp08.datagen all    --n-shapes 5000 --n-fem 1000 --workers 32 --out data   # 6그룹 전부

저장 (그룹마다 data/<group>/)
  shapes_00000.npz : idx, occ(비트 압축), meta(json), sdf_xyz(float16), sdf(float16)
  fem_00000.npz    : idx, cond(json), U(float16, (n, C, NX, NY, NZ)), freq, eval(json), t
같은 (그룹, 번호)는 항상 같은 형상(시드 고정) → 서버에서 다시 만들어도 동일.
"""
import os, json, time, argparse
import numpy as np
from multiprocessing import get_context
from . import problems, shapes, labels

SHARD = 100
FEM_SPLIT = 4          # FEM 은 형상 묶음 하나를 4조각(25개)으로 나눠 병렬
_cache = {}


def _prob(group):
    if group not in _cache:
        p = problems.get(group)
        _cache[group] = (p, shapes.Canvas(p))
    return _cache[group]


def cond_of(p, group, idx):
    """형상마다 모델 입력 조건 1개 무작위 (설계 결정 5번). 기준값 0번 형상들은 기본 조건."""
    rng = np.random.default_rng(shapes.seed_of(group, idx) ^ 0x5eed)
    c = dict(p.default_cond)
    mi = p.conditions.get('model_input', {})
    for k, (lo, hi) in mi.items():
        c[k] = float(rng.uniform(lo, hi))
    return c


def cand_shard(args):
    """후보 형상 묶음: 형상 + 품질 지표만 (SDF 없음)"""
    group, s, out = args
    path = os.path.join(out, group, 'cand', f'cand_{s:05d}.npz')
    if os.path.exists(path):
        return path, 0.0
    t0 = time.time()
    p, cv = _prob(group)
    idx = np.arange(s * SHARD, (s + 1) * SHARD)
    occ, meta = [], []
    for i in idx:
        o, m = shapes.make_shape(p, group, int(i), cv)
        m.update(shapes.quality(cv, o))
        occ.append(np.packbits(o)); meta.append(m)
    tmp = path + '.tmp.npz'
    np.savez_compressed(tmp, idx=idx, occ=np.stack(occ), meta=json.dumps(meta))
    os.replace(tmp, path)
    return path, time.time() - t0


def select(group, out, n_keep, broken_frac=0.05, max_tips=2, rough_pct=90, log=print):
    """후보에서 n_keep 개 고르기 (설계 결정 3번 + 11-14 걸러내기). 결정적: 같은 후보면 항상 같은 선택.
    1) 생성 실패 제외  2) 끊긴 형상은 5%까지만  3) 허공 가지(골격 끝점) > max_tips 제외
    4) 울퉁불퉁 지표가 그룹 상위 (100-rough_pct)% 인 것 제외  5) 형식 비율(MIX) 맞춰 재료 비율이 고르게 퍼지도록 뽑기"""
    d = os.path.join(out, group, 'cand')
    fs = sorted(f for f in os.listdir(d) if f.endswith('.npz') and '.tmp' not in f)
    meta = []
    for f in fs:
        meta += json.loads(str(np.load(os.path.join(d, f))['meta']))
    M = {m['idx']: m for m in meta}
    reason = {}
    ok = [m for m in meta if not m.get('failed')]
    for m in meta:
        if m.get('failed'):
            reason[m['idx']] = 'failed'
    conn = [m for m in ok if m['connected']]
    broken = [m for m in ok if not m['connected']]
    r_cut = float(np.percentile([m['rough'] for m in conn], rough_pct))
    good = []
    for m in conn:
        if m['tips'] > max_tips:
            reason[m['idx']] = 'tips'
        elif m['rough'] > r_cut:
            reason[m['idx']] = 'rough'
        else:
            good.append(m)
    n_broken = min(len(broken), int(round(broken_frac * n_keep)))
    keep = [m['idx'] for m in sorted(broken, key=lambda m: m['idx'])[:n_broken]]
    for m in broken[n_broken:]:
        reason[m['idx']] = 'broken_over_quota'
    # 11-14: 형식 비율 자동 결정 = 형식별 "걸러지지 않고 남은 비율"에 비례 (최소 5%)
    fams = sorted({m['family'] for m in ok})
    tot = {f: sum(1 for m in conn if m['family'] == f) for f in fams}
    good_n = {f: sum(1 for m in good if m['family'] == f) for f in fams}
    rate = {f: good_n[f] / max(tot[f], 1) for f in fams}
    w = {f: max(rate[f], 1e-6) for f in fams}
    ws = sum(w.values()); w = {f: max(v / ws, 0.05) for f, v in w.items()}; ws = sum(w.values())
    mix = {f: v / ws for f, v in w.items()}
    need = n_keep - len(keep)
    byfam = {f: sorted([m for m in good if m['family'] == f], key=lambda m: (m['vf'], m['idx'])) for f in mix}
    quota = {f: int(round(need * w_)) for f, w_ in mix.items()}
    short = 0
    for f in mix:                                     # 모자라는 형식은 있는 만큼, 남는 몫은 다른 형식으로
        if quota[f] > len(byfam[f]):
            short += quota[f] - len(byfam[f]); quota[f] = len(byfam[f])
    for f in sorted(mix, key=lambda f: -len(byfam[f]) + quota[f]):
        add = min(short, len(byfam[f]) - quota[f]); quota[f] += add; short -= add
    diff = need - sum(quota.values())
    quota[max(mix, key=lambda f: len(byfam[f]) - quota[f])] += diff
    for f, q in quota.items():
        L = byfam[f]
        pick = np.unique(np.linspace(0, len(L) - 1, q).round().astype(int)) if q > 0 else []
        keep += [L[i]['idx'] for i in pick]
        for j, m in enumerate(L):
            if j not in set(pick):
                reason.setdefault(m['idx'], 'not_sampled')
    keep = sorted(keep)[:n_keep]
    rep = dict(group=group, n_cand=len(meta), n_keep=len(keep), rough_cut=r_cut, max_tips=max_tips,
               dropped={r: sum(1 for v in reason.values() if v == r) for r in set(reason.values())},
               family_keep={f: sum(1 for i in keep if M[i]['family'] == f) for f in mix},
               broken_keep=n_broken, keep_rate={f: round(v, 3) for f, v in rate.items()},
               mix_auto={f: round(v, 3) for f, v in mix.items()}, sym_axes=_prob(group)[1].sym_axes, keep=keep)
    with open(os.path.join(out, group, 'selection.json'), 'w') as f:
        json.dump(rep, f)
    with open(os.path.join(out, group, 'drop_reason.json'), 'w') as f:
        json.dump({str(k): v for k, v in reason.items()}, f)
    log(f'  [{group}] 후보 {len(meta)} → {len(keep)}개 선택, 제외 {rep["dropped"]}')
    return rep


def shapes_shard(args):
    group, s, out, n_pts = args
    path = os.path.join(out, group, f'shapes_{s:05d}.npz')
    if os.path.exists(path):
        return path, 0.0
    t0 = time.time()
    p, cv = _prob(group)
    sel = os.path.join(out, group, 'selection.json')
    if os.path.exists(sel):
        idx = np.array(json.load(open(sel))['keep'][s * SHARD:(s + 1) * SHARD])
    else:
        idx = np.arange(s * SHARD, (s + 1) * SHARD)
    occ, meta, X, S = [], [], [], []
    for i in idx:
        o, m = shapes.make_shape(p, group, int(i), cv)       # 시드 고정 → 후보 때와 같은 형상
        rng = np.random.default_rng(shapes.seed_of(group, int(i)) ^ 0xd5df)
        x, d = shapes.sample_sdf(p, o | cv.fixed, rng, n=n_pts)
        occ.append(np.packbits(o)); meta.append(m); X.append(x.astype(np.float16)); S.append(d.astype(np.float16))
    tmp = path + '.tmp.npz'
    np.savez_compressed(tmp, idx=idx, occ=np.stack(occ), meta=json.dumps(meta), sdf_xyz=np.stack(X), sdf=np.stack(S))
    os.replace(tmp, path)
    return path, time.time() - t0


ESO_BASE = 10_000_000     # ESO 로 다듬은 형상의 번호 = 원본 번호 + ESO_BASE


def eso_shard(args):
    """선택된 형상 묶음 s 에서 짝수 번째(절반)를 ESO 로 다듬어 새 형상으로 저장 (shapes_e#####.npz)"""
    group, s, out, n_pts = args
    path = os.path.join(out, group, f'shapes_e{s:05d}.npz')
    if os.path.exists(path):
        return path, 0.0
    from . import eso
    t0 = time.time()
    p, cv = _prob(group)
    z = np.load(os.path.join(out, group, f'shapes_{s:05d}.npz'))
    occ0 = np.unpackbits(z['occ'], axis=1)[:, :p.grid.ne].astype(bool)
    meta0 = json.loads(str(z['meta']))
    idx, occ, meta, X, S = [], [], [], [], []
    for k in range(0, len(z['idx']), 2):
        if not meta0[k].get('connected', True):
            continue
        o, lg = eso.eso_prune(p, cv, occ0[k])
        if k % 10 == 0:                         # 진행 표시 (묶음 하나가 끝나야 부모 로그가 찍혀서, 그 사이 멈춘 것처럼 보이지 않게)
            print(f'    [ESO {group} 묶음 {s}] {k + 2}/{len(z["idx"])} ({time.time() - t0:.0f}s)', flush=True)
        if (o ^ occ0[k]).sum() == 0:
            continue
        i = ESO_BASE + int(z['idx'][k])
        rng = np.random.default_rng(shapes.seed_of(group, i) ^ 0xd5df)
        x, d = shapes.sample_sdf(p, o | cv.fixed, rng, n=n_pts)
        m = dict(meta0[k], idx=i, parent=int(z['idx'][k]), eso=lg, vf=float(o.sum() / cv.design.sum()))
        idx.append(i); occ.append(np.packbits(o)); meta.append(m); X.append(x.astype(np.float16)); S.append(d.astype(np.float16))
    tmp = path + '.tmp.npz'
    np.savez_compressed(tmp, idx=np.array(idx), occ=np.stack(occ), meta=json.dumps(meta), sdf_xyz=np.stack(X), sdf=np.stack(S))
    os.replace(tmp, path)
    return path, time.time() - t0


def load_shapes(out, group):
    p, _ = _prob(group)
    d = os.path.join(out, group)
    fs = sorted(f for f in os.listdir(d) if f.startswith('shapes_') and f.endswith('.npz') and '.tmp' not in f)
    idx, occ, meta = [], [], []
    for f in fs:
        z = np.load(os.path.join(d, f))
        idx.append(z['idx']); occ.append(np.unpackbits(z['occ'], axis=1)[:, :p.grid.ne].astype(bool))
        meta += json.loads(str(z['meta']))
    return np.concatenate(idx), np.concatenate(occ), meta


def fem_one(group, idx, occ, cond=None):
    p, cv = _prob(group)
    cond = cond or cond_of(p, group, idx)
    r = labels.fem_label(p, occ, cond)
    U = labels.nodal_fields(p, r)
    fr = np.concatenate([r['freq'].get('S', []), r['freq'].get('A', [])]) if r['freq'] else np.zeros(0)
    return U, fr, r['eval'], cond, r['t']


def fem_shard(args):
    """FEM 정답 묶음. idx_list 를 주면 그 형상들(능동 학습), 아니면 s번째 묶음."""
    group, s, out, idx_list, occ_list, tag = args
    part = None
    if isinstance(s, tuple):
        s, part = s
    path = os.path.join(out, group, f'fem{tag}_{s:05d}' + ('' if part is None else f'_{part}') + '.npz')
    if os.path.exists(path):
        return path, 0.0
    t0 = time.time()
    p, cv = _prob(group)
    if occ_list is None:
        z = np.load(os.path.join(out, group, f'shapes_{s:05d}.npz'))
        idx_list = z['idx']
        occ_list = np.unpackbits(z['occ'], axis=1)[:, :p.grid.ne].astype(bool)
        meta = json.loads(str(z['meta']))
        if part is not None:
            sl = slice(part * SHARD // FEM_SPLIT, (part + 1) * SHARD // FEM_SPLIT)
            idx_list, occ_list, meta = idx_list[sl], occ_list[sl], meta[sl]
    else:
        meta = [{}] * len(idx_list)
    U, FR, EV, CD, T, ok = [], [], [], [], [], []
    for i, o, m in zip(idx_list, occ_list, meta):
        if m and not m.get('connected', True):
            ok.append(False); continue             # 끊긴 형상은 FEM 불가 → DeepSDF 전용
        try:
            u, fr, ev, cd, t = fem_one(group, int(i), o)
        except Exception as e:                      # FEM 실패도 기록
            ok.append(False); continue
        U.append(u.astype(np.float16)); FR.append(fr); EV.append(ev); CD.append(cd); T.append(t); ok.append(True)
    ok = np.array(ok)
    tmp = path + '.tmp.npz'
    np.savez_compressed(tmp, idx=np.asarray(idx_list)[ok], U=np.stack(U) if U else np.zeros(0),
                        freq=np.stack(FR) if FR and len(FR[0]) else np.zeros((len(U), 0)),
                        eval=json.dumps(EV), cond=json.dumps(CD), t=np.array(T),
                        occ=np.packbits(np.asarray(occ_list)[ok], axis=1))
    os.replace(tmp, path)
    return path, time.time() - t0


def run_pool(fn, tasks, workers, log=print):
    t0 = time.time()
    done = 0
    if workers <= 1:
        it = map(fn, tasks)
    else:
        # 작업자마다 1스레드 (MKL/pypardiso 가 코어 수만큼 스레드를 띄워 과부하되는 것 방지). spawn 이라 자식이 환경변수를 새로 읽음
        old = {k: os.environ.get(k) for k in ('MKL_NUM_THREADS', 'OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS')}
        for k in old:
            os.environ[k] = '1'
        pool = get_context('spawn').Pool(workers)
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        it = pool.imap_unordered(fn, tasks)
    for path, dt in it:
        done += 1
        if dt > 0:
            log(f'  {os.path.basename(os.path.dirname(path))}/{os.path.basename(path)} {dt:.1f}s ({done}/{len(tasks)}, 경과 {time.time()-t0:.0f}s)')
    if workers > 1:
        pool.close(); pool.join()


def make_shapes(group, n, out, workers, n_pts=4000, n_cand=None, eso=False, log=print):
    """n_cand 를 주면: 후보 n_cand 개 생성 → 걸러서 n 개 선택 → 선택된 것만 SDF 점 샘플"""
    os.makedirs(os.path.join(out, group), exist_ok=True)
    p, _ = _prob(group)
    p.save_npz(os.path.join(out, group, 'problem.npz'))
    with open(os.path.join(out, group, 'spec.json'), 'w') as f:
        json.dump(p.spec(), f, ensure_ascii=False, indent=1)
    if n_cand:
        os.makedirs(os.path.join(out, group, 'cand'), exist_ok=True)
        run_pool(cand_shard, [(group, s, out) for s in range((n_cand + SHARD - 1) // SHARD)], workers, log)
        if not os.path.exists(os.path.join(out, group, 'selection.json')):
            select(group, out, n, log=log)
    tasks = [(group, s, out, n_pts) for s in range((n + SHARD - 1) // SHARD)]
    run_pool(shapes_shard, tasks, workers, log)
    if eso:                                    # 11-14: 절반을 ESO 로 다듬어 추가 (형상 n → 약 1.5n)
        run_pool(eso_shard, tasks, workers, log)


def make_fem(group, n, out, workers, log=print):
    ns = (n + SHARD - 1) // SHARD
    tasks = [(group, (s, k), out, None, None, '') for s in range(ns) for k in range(FEM_SPLIT)]
    run_pool(fem_shard, tasks, workers, log)


def load_fem(out, group, tag=None):
    d = os.path.join(out, group)
    fs = sorted(f for f in os.listdir(d) if f.startswith('fem') and f.endswith('.npz') and '.tmp' not in f
                and (tag is None or f.startswith(f'fem{tag}_')))
    R = dict(idx=[], U=[], freq=[], eval=[], cond=[], occ=[])
    p, _ = _prob(group)
    for f in fs:
        z = np.load(os.path.join(d, f))
        if len(z['idx']) == 0:
            continue
        R['idx'].append(z['idx']); R['U'].append(z['U']); R['freq'].append(z['freq'])
        R['eval'] += json.loads(str(z['eval'])); R['cond'] += json.loads(str(z['cond']))
        R['occ'].append(np.unpackbits(z['occ'], axis=1)[:, :p.grid.ne].astype(bool))
    for k in ('idx', 'U', 'freq', 'occ'):
        R[k] = np.concatenate(R[k]) if R[k] else np.zeros(0)
    return R


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('what', choices=['shapes', 'fem', 'all'])
    ap.add_argument('--group', default=None)
    ap.add_argument('--n', type=int, default=100)
    ap.add_argument('--n-shapes', type=int, default=5000)
    ap.add_argument('--n-fem', type=int, default=1000)
    ap.add_argument('--n-cand', type=int, default=None, help='후보 형상 수 (주면 걸러서 n-shapes 개 선택)')
    ap.add_argument('--eso', action='store_true', help='선택된 형상의 절반을 ESO 로 다듬어 추가')
    ap.add_argument('--workers', type=int, default=os.cpu_count())
    ap.add_argument('--out', default='data')
    a = ap.parse_args()
    groups = [a.group] if a.group else list(problems.GROUPS)
    for gname in groups:
        if a.what in ('shapes', 'all'):
            make_shapes(gname, a.n if a.what == 'shapes' else a.n_shapes, a.out, a.workers, n_cand=a.n_cand, eso=a.eso)
        if a.what in ('fem', 'all'):
            make_fem(gname, a.n if a.what == 'fem' else a.n_fem, a.out, a.workers)
