"""기준값 회귀 테스트. 코드를 바꾼 뒤 결과가 같은지 확인한다.
  빠른 테스트: pytest -q tests            (약 2분)
  느린 테스트: RUN_SLOW=1 pytest -q tests (FEM 재계산 포함, 약 10분)
기준값 출처: data/reference/frfint_*.json (해커톤 최종 자료의 숫자와 같은 계산)
"""
import json, os, subprocess, sys, numpy as np, pytest
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ENG = os.path.join(R, 'engine')
ENV = dict(os.environ, GRIP='2', NX='88', MSYS='0.311')
slow = pytest.mark.skipif(os.environ.get('RUN_SLOW') != '1', reason='RUN_SLOW=1 일 때만')

def run_engine(**kw):
    p = subprocess.run([sys.executable, 'opt_int.py'], cwd=ENG, env=dict(ENV, **kw), capture_output=True, text=True, timeout=1800)
    assert p.returncode == 0, p.stdout[-2000:] + p.stderr[-2000:]; return p.stdout

def test_grid_meta():
    m = np.load(os.path.join(R, 'data/grid_meta.npz')); assert (int(m['nx']), int(m['ny']), int(m['nz'])) == (88, 20, 37)
    assert len(m['didx']) == 50101 and int(m['solid'].sum()) == 2477

def test_label2_one_sample(tmp_path):
    out = tmp_path / 'g.npz'; run_engine(MODE='label2', NS='1', SEED='1', OUT=str(out)); d = np.load(out)
    assert d['lab'].shape == (1, 7) and d['T'].shape == (1, 65120)
    assert abs(d['lab'][0, 0] - 73.315) < 0.05 and abs(d['lab'][0, 1] - 33.609) < 0.1     # 생성기 SEED=1 첫 형상: 무게 · 1차 진동수

@slow
@pytest.mark.parametrize('rho,ref', [('rho_body_v3.npy', 'frfint_body_v3.json'), ('rbase_int88.npy', 'frfint_base35g3.json')])
def test_eval_matches_reference(rho, ref, tmp_path):
    tag = 'test_' + rho.split('.')[0]; run_engine(MODE='eval', RHO=os.path.join(R, 'data/reference', rho), TAG=tag)
    got = json.load(open(os.path.join(ENG, f'frfint_{tag}.json'))); exp = json.load(open(os.path.join(R, 'data/reference', ref)))
    for k, g, e, tol in [('mass_g', got['mass_g'], exp['mass_g'], 0.01), ('f1', got['f'][0], exp['f'][0], 0.01), ('Tmax', got['Tmax'], exp['Tmax'], 0.01),
                         ('peak_vert', got['vert']['peak'], exp['vert']['peak'], 0.03), ('vm_vert', got['shock']['vert']['vm999'], exp['shock']['vert']['vm999'], 0.03)]:
        assert abs(g - e) <= tol * max(abs(e), 1e-6) + 0.05, f'{k}: {g} vs 기준 {e}'

def test_ai_smoke(tmp_path):
    """학습 코드가 끝까지 도는지 (CPU, 몇 단계). 성능은 보지 않는다."""
    pytest.importorskip('torch'); shards = os.path.join(R, 'tests/data/*.npz'); M = os.path.join(R, 'data/grid_meta.npz')
    def py(*a): p = subprocess.run([sys.executable, '-m', *a], cwd=R, capture_output=True, text=True, timeout=1800); assert p.returncode == 0, p.stderr[-2000:]
    py('ai.surrogate', '--meta', M, '--data', shards, '--model', 'fno', '--out', str(tmp_path / 'f.pt'), '--steps', '3', '--bs', '2', '--log_every', '2')
    py('ai.surrogate', '--meta', M, '--data', shards, '--model', 'cnn', '--out', str(tmp_path / 'c.pt'), '--steps', '3', '--bs', '2', '--log_every', '2')
    py('ai.deepsdf', 'train', '--meta', M, '--data', shards, '--out', str(tmp_path / 's.pt'), '--steps', '5', '--bs', '2', '--npts', '512', '--hid', '32', '--log_every', '4')
    py('ai.latent_search', '--meta', M, '--sdf', str(tmp_path / 's.pt'), '--phys', str(tmp_path / 'f.pt'), '--data', shards, '--spec', os.path.join(R, 'spec/bike_mount_targets.json'), '--out', str(tmp_path / 'ls'), '--k', '1', '--iters', '2')
    assert (tmp_path / 'ls' / 'cand_0.npy').exists()
