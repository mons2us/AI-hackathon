"""FNO 학습 — ai.surrogate.train 그대로, 검증 분할만 고정(389개 분할의 58개 이름). 사용: python3 train_fno_fixed.py <샤드 패턴> <출력> [단계]"""
import sys, json, argparse, numpy as np
sys.path.insert(0, '/home/claude/input-spec/13_AI학습_일체형')
import ai.surrogate as S
from ai.data import Grid, load_shards
pat, out = sys.argv[1], sys.argv[2]; steps = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
G = '/tmp/claude-0/-home-claude/e964ed80-ee1b-5f91-abd3-3081682a3ad7/scratchpad/gino'
meta = '/home/claude/input-spec/13_AI학습_일체형/data/grid_meta.npz'
nm = [str(x) for x in load_shards(pat, Grid(meta), fields=False)['names']]; test = json.load(open(G + '/test_names.json'))
te = np.array([nm.index(t) for t in test]); tr = np.setdiff1d(np.arange(len(nm)), te)
S.split = lambda n, seed=0, test_frac=0.15: (tr, te)          # 분할만 바꿈
print('train', len(tr), 'test', len(te), flush=True)
a = argparse.Namespace(meta=meta, data=pat, model='fno', out=out, steps=steps, bs=16, lr=1e-3, width=12, modes=[8, 5, 12], wfield=1.0,
                       thermal_ops='data/thermal_ops.npz', wphys=0.1, phys_warm=2000, ext=False, wext=1.0, struct=False, struct_ops='data/struct_ops.npz',
                       wstruct=0.1, wdisp=1.0, disp_max=2000, seed=0, log_every=500)
S.train(a)
