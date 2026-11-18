"""시연: 학습된 DeepSDF·PINO 로 최적 형상을 찾고 FEM 으로 검증 → 결과 JSON·PNG·STL·요약 HTML (CPU 로도 동작)

python -m fp08.demo --run runs/main --data data --out results                      # 6그룹 × 시연 조건 전부
python -m fp08.demo --run runs/main --data data --out results --groups bike_pad80 --cond phone_mass_g=180,phone_angle_deg=10
옵션: --n-starts 10 --steps 300 --device cpu|cuda

결과 (out/)
  <그룹>_<조건>.json  : 상태(ok/fallback), FEM 판정값, 예측값, 시간
  <그룹>_<조건>.png   : 최적 형상 그림 (표면 다듬어 표시)
  <그룹>_<조건>.stl   : 최적 형상 STL (FEM 으로 검증한 칸 형상의 표면을 다듬은 것, 대칭 복원, 강체 대역 제외, mm)
  summary.html        : 전체 표
fallback = 대리 모델 후보가 전부 FEM 검증에 실패 (표시만 함. FEM 직접 최적화(경로 A, 팀 opt3d.py·ped.py)는 자동 연결 안 됨 → 수동)
"""
import os, sys, json, time, argparse, html
import numpy as np
import torch
from scipy import ndimage
from skimage import measure
from . import problems, design_opt, train_pino, loop

HERE = os.path.dirname(os.path.abspath(__file__))


def full_mesh(p, occ, smooth=True, up=2):
    """설계 재료 + 고정부품(강체 대역 제외) → 대칭 복원 → 다듬은 표면 (verts mm, faces)"""
    g = p.grid
    A = g.eshape((occ & (p.label == 0)) | (p.label == 1)).astype(float)
    if p.sym_axis is not None:
        ax = 2 - p.sym_axis
        A = np.concatenate([np.flip(A, ax), A], ax)
    A = np.pad(A, 2)
    if smooth:
        A = ndimage.zoom(ndimage.gaussian_filter(A, 0.7), up, order=1)
        v, f, _, _ = measure.marching_cubes(A, 0.5); v = v / up
    else:
        v, f, _, _ = measure.marching_cubes(A, 0.5)
    v = (v - 2) * g.h                                  # (z, y, x) mm
    o = g.origin.copy(); n = [g.nx, g.ny, g.nz]
    if p.sym_axis is not None:
        o[p.sym_axis] -= n[p.sym_axis] * g.h
    V = np.stack([v[:, 2] + o[0], v[:, 1] + o[1], v[:, 0] + o[2]], 1)
    return V, f


def write_stl(path, V, F):
    tri = V[F]
    nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    nrm /= (np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-12)
    rec = np.zeros(len(F), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')])
    rec['n'] = nrm; rec['v'] = tri
    with open(path, 'wb') as f:
        f.write(b'FormProof 08 optimized shape (mm)'.ljust(80, b' '))
        f.write(np.uint32(len(F)).tobytes()); f.write(rec.tobytes())


def render_png(path, p, occ, title):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    V, F = full_mesh(p, occ)
    fig = plt.figure(figsize=(6, 4.5)); ax = fig.add_subplot(111, projection='3d')
    ax.plot_trisurf(V[:, 0], V[:, 1], F, V[:, 2], color='#e8833a', lw=0, shade=True)
    span = V.max(0) - V.min(0); ax.set_box_aspect(span); ax.set_axis_off()
    view = (22, -58) if p.product == 'bike_mount' else (20, -40)
    ax.view_init(*view); ax.set_title(title, fontsize=10)
    plt.tight_layout(); plt.savefig(path, dpi=100, bbox_inches='tight'); plt.close(fig)


def tagof(group, cond):
    return group + '_' + '_'.join(f'{k}{v:g}' for k, v in sorted(cond.items()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', default='runs/main'); ap.add_argument('--data', default='data'); ap.add_argument('--out', default='results')
    ap.add_argument('--groups', default=None); ap.add_argument('--cond', default=None, help='예: phone_mass_g=180,phone_angle_deg=10')
    ap.add_argument('--n-starts', type=int, default=10); ap.add_argument('--steps', type=int, default=300)
    ap.add_argument('--device', default='cuda' if torch.cuda.is_available() else 'cpu')
    ap.add_argument('--pino-tag', default='pino')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    groups = a.groups.split(',') if a.groups else list(problems.GROUPS)
    gate = {}
    sf = os.path.join(a.run, 'state.json')
    if os.path.exists(sf):
        G = json.load(open(sf, encoding='utf-8')).get('gate', {})
        if G:
            gate = G[sorted(G)[-1]]                    # 마지막 관문 결과의 오차 → 최적화 여유
    rows, nets = [], {}
    for g in groups:
        p = problems.get(g)
        pr = problems.PRODUCT_OF[g]
        if pr not in nets:
            nets[pr] = train_pino.load(a.run, a.pino_tag, pr, a.device)[0]
        net = nets[pr]
        margins = {}
        m = gate.get(g, {}).get('metrics', {})
        for q, v in m.get('judge_abs_p90', {}).items():
            margins[q] = float(min(max(v, 0.02), 0.3))
        if 'freq_abs_p95' in m:
            margins['f_min'] = float(min(max(m['freq_abs_p95'], 0.02), 0.3))
        conds = [dict(kv.split('=') for kv in a.cond.split(','))] if a.cond else loop.DEMO[g]
        for cond in conds:
            cond = {k: float(v) for k, v in cond.items()}
            t0 = time.time()
            s, best = design_opt.optimize(g, cond, os.path.join(a.run, 'sdf', g, 'ckpt.pt'), net, a.data, margins=margins,
                                          n_starts=a.n_starts, steps=a.steps, device=a.device, out_dir=os.path.join(a.out, 'detail'))
            tag = tagof(g, cond)
            rec = dict(group=g, cond=cond, status=s['status'], sec=round(time.time() - t0, 1), margins=margins,
                       fem=(s['best'] or {}).get('fem'), pred=(s['best'] or {}).get('pred'))
            if best is not None:
                V, F = full_mesh(p, best); write_stl(os.path.join(a.out, tag + '.stl'), V, F)
                e = rec['fem']
                render_png(os.path.join(a.out, tag + '.png'), p, best, f"{g} {cond}\n{e['mass_g']:.0f} g · FEM 합격")
            json.dump(rec, open(os.path.join(a.out, tag + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
            rows.append(rec)
            print(f'[demo] {tag}: {rec["status"]} {rec["sec"]} s', flush=True)
    E = html.escape
    tr = ''.join(f'<tr><td>{E(r["group"])}</td><td>{E(json.dumps(r["cond"]))}</td><td>{"✅ ok" if r["status"] == "ok" else "⚠ fallback (FEM 검증 실패)"}</td>'
                 f'<td>{(r["fem"] or {}).get("mass_g", "-")}</td><td><code>{E(json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in (r["fem"] or {}).items() if k not in ("f", "pad_min_N")}, default=str))}</code></td>'
                 f'<td>{r["sec"]}</td><td>{"<img src=%s width=220>" % E(tagof(r["group"], r["cond"]) + ".png") if r["status"] == "ok" else ""}</td></tr>' for r in rows)
    open(os.path.join(a.out, 'summary.html'), 'w', encoding='utf-8').write(
        f'<!DOCTYPE html><html lang="ko"><meta charset="utf-8"><title>08 시연 결과</title><style>body{{font-family:sans-serif;margin:20px}}td,th{{border:1px solid #ddd;padding:4px 6px;font-size:13px}}table{{border-collapse:collapse}}</style>'
        f'<h2>08 시연 결과 — 대리 모델 최적화 + FEM 검증</h2><p>질량 g은 대칭 복원 전체(고정부품 포함). fallback = 대리 모델 후보가 모두 FEM 검증 실패 (자동 대체 없음).</p>'
        f'<table><tr><th>그룹</th><th>조건</th><th>상태</th><th>질량 g</th><th>FEM 판정값</th><th>시간 s</th><th>형상</th></tr>{tr}</table></html>')
    print(f'요약: {os.path.join(a.out, "summary.html")}')


if __name__ == '__main__':
    main()
