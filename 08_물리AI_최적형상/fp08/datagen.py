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


def shapes_shard(args):
    group, s, out, n_pts = args
    path = os.path.join(out, group, f'shapes_{s:05d}.npz')
    if os.path.exists(path):
        return path, 0.0
    t0 = time.time()
    p, cv = _prob(group)
    idx = np.arange(s * SHARD, (s + 1) * SHARD)
    occ, meta, X, S = [], [], [], []
    for i in idx:
        o, m = shapes.make_shape(p, group, int(i), cv)
        rng = np.random.default_rng(shapes.seed_of(group, int(i)) ^ 0xd5df)
        x, d = shapes.sample_sdf(p, o | cv.fixed, rng, n=n_pts)
        occ.append(np.packbits(o)); meta.append(m); X.append(x.astype(np.float16)); S.append(d.astype(np.float16))
    tmp = path + '.tmp.npz'
    np.savez_compressed(tmp, idx=idx, occ=np.stack(occ), meta=json.dumps(meta), sdf_xyz=np.stack(X), sdf=np.stack(S))
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


def make_shapes(group, n, out, workers, n_pts=4000, log=print):
    os.makedirs(os.path.join(out, group), exist_ok=True)
    p, _ = _prob(group)
    p.save_npz(os.path.join(out, group, 'problem.npz'))
    with open(os.path.join(out, group, 'spec.json'), 'w') as f:
        json.dump(p.spec(), f, ensure_ascii=False, indent=1)
    tasks = [(group, s, out, n_pts) for s in range((n + SHARD - 1) // SHARD)]
    run_pool(shapes_shard, tasks, workers, log)


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
    ap.add_argument('--workers', type=int, default=os.cpu_count())
    ap.add_argument('--out', default='data')
    a = ap.parse_args()
    groups = [a.group] if a.group else list(problems.GROUPS)
    for gname in groups:
        if a.what in ('shapes', 'all'):
            make_shapes(gname, a.n if a.what == 'shapes' else a.n_shapes, a.out, a.workers)
        if a.what in ('fem', 'all'):
            make_fem(gname, a.n if a.what == 'fem' else a.n_fem, a.out, a.workers)
