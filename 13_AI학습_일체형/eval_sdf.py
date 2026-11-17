"""형상 AI 평가: 학습된 z 로 핵심 형상 복원 IoU + GUI 와 같은 방식(평균 z 에서 맞춤)으로 1차 설계 복원 IoU"""
import sys, json, numpy as np, torch, torch.nn.functional as F
from ai.data import Grid; from ai.deepsdf import ShapeAI, iou
ck = sys.argv[1] if len(sys.argv) > 1 else 'runs/sdf.pt'
torch.set_num_threads(1); g = Grid('data/grid_meta.npz'); S = ShapeAI(ck, g)
names = list(S.names); d = np.load('data/path_src.npz'); R = np.unpackbits(d['r'], axis=1)[:, :int(d['ne'])].astype(bool)
tgt = {n: R[i][g.didx].astype(np.float32) for i, n in enumerate(d['names'])}
out = {}
with torch.no_grad():
    for n in ['gui_base', 'path_0.000', 'path_0.250', 'path_0.500', 'path_0.750', 'path_1.000', 'gui_formproof', 'ref_rho_body_v3', 'ref_rbin_int35f95g2']:
        k = names.index(n); pr = S.decode(S.Z[k])[0].cpu().numpy(); out[n] = round(iou(pr, tgt[n]), 3)
print(json.dumps(dict(trained_z=out)), flush=True)
t = torch.as_tensor(tgt['gui_base']); z = S.Z.mean(0, keepdim=True).clone().requires_grad_(True); opt = torch.optim.Adam([z], lr=5e-3)
for it in range(int(sys.argv[2]) if len(sys.argv) > 2 else 600):
    idx = torch.randint(0, g.nd, (8192,)); lg = S.dec(z, S.P[idx])[0]
    loss = F.binary_cross_entropy_with_logits(lg, t[idx]) + 1e-4 * (z ** 2).mean(); opt.zero_grad(); loss.backward(); opt.step()
with torch.no_grad(): print(json.dumps(dict(gui_fit_base=round(iou(S.decode(z)[0].numpy(), t.numpy()), 3))))
