"""ESO 다듬기 시험: 선택된 형상 N개 → 원본 vs 다듬은 형상의 질량·판정값 + 그림
python experiments/eso_compare.py <data> <그룹> <출력 png> [N]"""
import os, sys, json, time, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..')); sys.path.insert(0, HERE)
import group_figures as G
from fp08 import problems, shapes, datagen, labels, eso

if __name__ == '__main__':
    data, group, out = sys.argv[1:4]; N = int(sys.argv[4]) if len(sys.argv) > 4 else 20
    p = problems.get(group); cv = shapes.Canvas(p)
    idx, occ, meta = datagen.load_shapes(data, group)
    rows = []; t0 = time.time()
    for k in range(N):
        o = occ[k]
        if not meta[k].get('connected', True):
            continue
        a = labels.fem_label(p, o)['eval']
        o2, lg = eso.eso_prune(p, cv, o)
        b = labels.fem_label(p, o2)['eval']
        rows.append(dict(idx=int(idx[k]), fam=meta[k]['family'], before=a, after=b, log=lg, o=o, o2=o2))
    dt = (time.time() - t0) / max(len(rows), 1)
    key = 'f_min' if 'f_min' in rows[0]['before'] else 'utop_fb'
    S = dict(group=group, n=len(rows), sec_per_shape=dt,
             mass_change=float(np.median([r['after']['mass_g'] / r['before']['mass_g'] - 1 for r in rows])),
             key=key, key_change=float(np.median([r['after'][key] / r['before'][key] - 1 for r in rows])),
             pass_before=sum(r['before']['pass'] for r in rows), pass_after=sum(r['after']['pass'] for r in rows),
             eff_before=None)
    print(json.dumps(S, ensure_ascii=False))
    pick = sorted(rows, key=lambda r: r['after']['mass_g'] / r['before']['mass_g'])[:4]
    fig = plt.figure(figsize=(9, 3.0 * len(pick)))
    fmt = lambda e: f"{e['mass_g']:.0f} g · " + (f"f_min {e['f_min']:.0f} Hz" if key == 'f_min' else f"흔들림 {e['utop_fb']:.2f} mm") + (' · 합격' if e['pass'] else ' · 불합격')
    for r_, r in enumerate(pick):
        for c, (o, e, lab) in enumerate([(r['o'], r['before'], '원본'), (r['o2'], r['after'], 'ESO 다듬음')]):
            ax = fig.add_subplot(len(pick), 2, 2 * r_ + c + 1, projection='3d')
            G.mesh(ax, p, o & (p.label == 0), '#e8833a')
            if c == 1:
                G.mesh(ax, p, r['o'] & ~r['o2'] & (p.label == 0), '#2f6fed', 0.25)
            G.mesh(ax, p, p.label == 1, '#5F5E5A'); G.mesh(ax, p, p.label == 3, '#7F77DD')
            G.frame(ax, p); ax.view_init(*G.VIEW[problems.PRODUCT_OF[group]])
            ax.set_title(f"{lab} #{r['idx']} {G.FAM[r['fam']]}\n{fmt(e)}", fontsize=10, color='#0d7a5f' if e['pass'] else '#d9455f')
    plt.tight_layout(); plt.savefig(out, dpi=80, bbox_inches='tight')
    json.dump(dict(S, rows=[dict(idx=r['idx'], fam=r['fam'], before=r['before'], after=r['after'], log=r['log']) for r in rows]),
              open(out.replace('.png', '.json'), 'w'), ensure_ascii=False, default=float)
