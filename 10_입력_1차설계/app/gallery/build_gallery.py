"""Render the look variants (variants.py) for review: CAD (mount_modules) -> meshes -> three.js studio render -> PNG,
plus a gallery page.   python app/gallery/build_gallery.py [G01 G05 ...]  ->  app/gallery/out/"""
import base64
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
from formproof_input import mount_modules as M  # noqa: E402
from variants import PHONES, SCHEMES, V  # noqa: E402

OUT = os.path.join(HERE, "out")


def mesh_of(solids, tol=0.04, ang=0.15):
    vs, ts, off = [], [], 0
    for s in solids:
        v, t = s.tessellate(tol, ang)
        if not t:
            continue
        vs.append(np.array([[p.x, p.y, p.z] for p in v], np.float32))
        ts.append(np.array(t, np.uint32) + off)
        off += len(v)
    if not vs:
        return None
    v, t = np.concatenate(vs), np.concatenate(ts)
    return dict(pos=base64.b64encode(v.tobytes()).decode(), idx=base64.b64encode(t.astype(np.uint32).tobytes()).decode())


def build_variant(v):
    parts, info = M.build(dict(v, phone=PHONES[v["phone"]]))
    by_mat = {}
    for mat, sol, _ in parts:
        by_mat.setdefault(mat, []).append(sol)
    meshes = {mat: mesh_of(sols) for mat, sols in by_mat.items()}
    return dict(id=v["id"], scheme=SCHEMES[v["scheme"]], meshes={k: m for k, m in meshes.items() if m}, info=info)


def describe(v, info):
    return dict(id=v["id"], note=v["note"], clamp=M.CLAMPS[v["clamp"]]["name"], arm=M.ARMS[v["arm"]],
                section=M.SECTIONS[v["section"]], joint=M.JOINTS[v["joint"]], holder=M.HOLDERS[v["holder"]]["name"],
                support=M.CLAMPS[v["clamp"]]["support"], maps_to=info["maps_to"], mass_g=info["mass_g"],
                tilt_deg=info["tilt_deg"], phone=v["phone"])


def main(ids):
    os.makedirs(os.path.join(OUT, "mesh"), exist_ok=True)
    meta = []
    for v in V:
        if ids and v["id"] not in ids:
            continue
        d = build_variant(v)
        with open(os.path.join(OUT, "mesh", v["id"] + ".json"), "w") as f:
            json.dump(d, f)
        meta.append(describe(v, d["info"]))
        print(v["id"], d["info"]["mass_g"], flush=True)
    path = os.path.join(OUT, "variants.json")
    old = json.load(open(path)) if ids and os.path.exists(path) else []
    keep = {m["id"]: m for m in old}
    keep.update({m["id"]: m for m in meta})
    with open(path, "w", encoding="utf-8") as f:
        json.dump([keep[k] for k in sorted(keep)], f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
