"""DeepSDF 복원 확인: 학습에 안 쓴 형상의 z 를 찾아(신경망 고정) 원본과 복원 형상을 나란히 그림 + IoU
python experiments/sdf_recon.py <data> <runs> <그룹> <출력 png> [개수]"""
import os, sys, json, numpy as np, torch, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..')); sys.path.insert(0, HERE)
import group_figures as G
from fp08 import problems, models, train_sdf, datagen, shapes
from skimage import measure
from scipy import ndimage


def recon_mesh(ax, p, model, z, up=2):
    """SDF 를 칸보다 촘촘히(up 배) 계산해서 표면 0 을 바로 그림 — 칸 모양 없이 신경망이 그린 그대로"""
    g = p.grid
    lo = g.origin.copy(); n = np.array([g.nx, g.ny, g.nz])
    xs = [lo[a] + (np.arange(n[a] * up) + 0.5) * g.h / up for a in range(3)]
    X, Y, Z = np.meshgrid(*xs, indexing='ij'); P = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1)
    with torch.no_grad():
        s = torch.cat([model(z, torch.tensor(P[i:i + 40000], dtype=torch.float32))[0] for i in range(0, len(P), 40000)]).numpy()
    S = s.reshape(X.shape)                                   # (x, y, z)
    a = p.sym_axis
    S = np.concatenate([np.flip(S, a), S], a)
    S = np.pad(S, 1, constant_values=S.max())
    v, f, _, _ = measure.marching_cubes(S, 0.0)
    v = (v - 1) * g.h / up
    o = lo.copy(); o[a] -= n[a] * g.h
    ax.plot_trisurf(v[:, 0] + o[0], v[:, 1] + o[1], f, v[:, 2] + o[2], color='#2f6fed', lw=0, shade=True)


if __name__ == '__main__':
    data, runs, group, out = sys.argv[1:5]; N = int(sys.argv[5]) if len(sys.argv) > 5 else 4
    torch.set_num_threads(1)
    p = problems.get(group)
    c = torch.load(os.path.join(runs, 'sdf', group, 'ckpt.pt'), map_location='cpu', weights_only=False)
    model, _ = models.load_sdf(os.path.join(runs, 'sdf', group, 'ckpt.pt'))
    idx, X, S, meta = train_sdf.load_group(data, group)
    _, occ, _ = datagen.load_shapes(data, group)
    tr, va = train_sdf.split(idx)
    vai = np.where(va)[0]
    fixed = (p.label == 1) | (p.label == 3)
    zv = train_sdf.infer_z(model, X[vai[:40]], S[vai[:40]], steps=300)
    ious = [train_sdf.grid_iou(p, model, zv[k:k + 1], occ[i] | fixed, 'cpu') for k, i in enumerate(vai[:40])]
    print(group, 'step', c['step'], '검증 형상 40개 IoU 평균 %.3f 중앙 %.3f 최소 %.3f' % (np.mean(ious), np.median(ious), np.min(ious)))
    order = np.argsort(ious)
    pick = [order[-1], order[len(order) // 2], order[len(order) // 4], order[0]][:N]
    lab = ['가장 잘 됨', '중간', '하위 25%', '가장 못 됨']
    fig = plt.figure(figsize=(9, 3.0 * len(pick)))
    for r, k in enumerate(pick):
        i = vai[k]
        ax = fig.add_subplot(len(pick), 2, 2 * r + 1, projection='3d')
        G.mesh(ax, p, occ[i] & (p.label == 0), '#e8833a'); G.mesh(ax, p, p.label == 1, '#5F5E5A'); G.mesh(ax, p, p.label == 3, '#7F77DD')
        G.frame(ax, p); ax.view_init(*G.VIEW[problems.PRODUCT_OF[group]]); ax.set_title(f'원본 #{int(idx[i])} ({lab[r]})', fontsize=10)
        ax = fig.add_subplot(len(pick), 2, 2 * r + 2, projection='3d')
        recon_mesh(ax, p, model, zv[k:k + 1])
        G.frame(ax, p); ax.view_init(*G.VIEW[problems.PRODUCT_OF[group]]); ax.set_title(f'DeepSDF 복원 · IoU {ious[k]:.2f}', fontsize=10)
    plt.tight_layout(); plt.savefig(out, dpi=80, bbox_inches='tight')
    json.dump(dict(group=group, step=int(c['step']), iou=[float(x) for x in ious]), open(out.replace('.png', '.json'), 'w', encoding='utf-8'))
