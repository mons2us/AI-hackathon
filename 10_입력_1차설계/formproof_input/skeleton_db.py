"""Template skeleton database: the stored form used to compare a sketch / image with the templates.

  python -m formproof_input.skeleton_db          -> formproof_input/templates/db/skeletons.json, features.npz, sheet.png

skeletons.json  per template: structure kind, parameters, ring radius, centre-line polylines in mm and in
                ring units (ring centre = origin, ring outer radius = 1) -> scale-free, readable, editable
features.npz    per reference (template x outline/skeleton x with/without phone x ring/bbox frame):
                128x96 ink map (bit-packed), distance transform, 4x3x8 orientation histogram
                = exactly what sketch.Matcher compares against (chamfer both ways + histogram distance)
Matcher.load() reads features.npz, so matching never re-renders templates; the signature guards staleness."""
import hashlib
import json
import os

import numpy as np

from . import sketch
from .templates.library import TEMPLATES

DB = os.path.join(os.path.dirname(__file__), "templates", "db")


def signature(templates=TEMPLATES):
    blob = json.dumps([[t["id"], t["params"]] for t in templates], sort_keys=True) + f"{sketch.W}x{sketch.H}|{sketch.R_PX}|{list(sketch.C0)}"
    return hashlib.sha1(blob.encode()).hexdigest()[:16]


def skeleton_record(t):
    ro = sketch.ring_radius(t["params"])
    parts = sketch.template_skeleton(t["params"], phone=True)
    return dict(id=t["id"], name=t["name"], kind=t.get("kind", "arm"), desc=t["desc"], params=t["params"], ring_ro_mm=round(ro, 3),
                polylines=[dict(part=n, mm=np.round(s, 3).tolist(), ring_units=np.round(s / ro, 4).tolist()) for n, s in parts])


def build(templates=TEMPLATES, out=DB):
    os.makedirs(out, exist_ok=True)
    sig = signature(templates)
    with open(os.path.join(out, "skeletons.json"), "w", encoding="utf-8") as f:
        json.dump(dict(signature=sig, frame="x 앞, z 위, 원점 = 핸들바 중심. ring_units = mm / 클램프 링 바깥 반지름",
                       canvas=dict(W=sketch.W, H=sketch.H, ring_centre=list(sketch.C0), ring_radius_px=sketch.R_PX),
                       templates=[skeleton_record(t) for t in templates]), f, ensure_ascii=False, indent=1)
    refs = sketch.Matcher.build_refs(templates)
    arrays = dict(signature=np.array(sig), ids=np.array([t["id"] for t in templates]))
    for frame, lst in refs.items():
        arrays[f"{frame}_t"] = np.array([r["t"] for r in lst], np.int16)
        arrays[f"{frame}_phone"] = np.array([r["phone"] for r in lst], bool)
        arrays[f"{frame}_style"] = np.array([r["style"] for r in lst])
        arrays[f"{frame}_img"] = np.packbits(np.stack([r["img"] > 0.5 for r in lst]).reshape(len(lst), -1), axis=1)
        arrays[f"{frame}_dt"] = np.stack([r["dt"] for r in lst]).astype(np.float32)
        arrays[f"{frame}_hist"] = np.stack([r["hist"] for r in lst])
    np.savez_compressed(os.path.join(out, "features.npz"), **arrays)
    _sheet(templates, os.path.join(out, "sheet.png"))
    return sig


def load(templates=TEMPLATES, path=DB):
    """refs dict for sketch.Matcher, or None if the stored DB does not belong to these templates."""
    f = os.path.join(path, "features.npz")
    if not os.path.isfile(f):
        return None
    z = np.load(f)
    if str(z["signature"]) != signature(templates):
        return None
    refs = {}
    for frame in ("ring", "bbox"):
        img = np.unpackbits(z[f"{frame}_img"], axis=1)[:, :sketch.W * sketch.H].reshape(-1, sketch.H, sketch.W).astype(np.float32)
        refs[frame] = [dict(t=int(z[f"{frame}_t"][k]), phone=bool(z[f"{frame}_phone"][k]), style=str(z[f"{frame}_style"][k]),
                            img=img[k], dt=sketch._dt(img[k]), hist=z[f"{frame}_hist"][k]) for k in range(len(img))]
    return refs


def _sheet(templates, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    n = len(templates)
    cols = 6
    rows = -(-n // cols)
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 2.6, rows * 1.9))
    for ax in axes.ravel():
        ax.axis("off")
    col = dict(ring="#111", ear="#777", arm="#1f5fd0", pad="#d9822b", stem="#999", phone="#999")
    for ax, t in zip(axes.ravel(), templates):
        for s in sketch.template_strokes(t["params"], phone=False):
            ax.plot(s[:, 0], s[:, 1], color="#cfd6e0", lw=0.8)
        for name, s in sketch.template_skeleton(t["params"], phone=True):
            ax.plot(s[:, 0], s[:, 1], color=col[name], lw=2 if name in ("arm", "ring", "pad") else 1, solid_capstyle="round")
        ax.set_aspect("equal")
        ax.set_title(f"{t['id']} · {t.get('kind', 'arm')}", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


if __name__ == "__main__":
    print("signature", build(), "->", DB)
