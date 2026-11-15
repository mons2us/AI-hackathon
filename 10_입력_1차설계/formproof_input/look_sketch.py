"""Side-view sketches of the look templates, traced from their CAD (what a person would draw from the side).

  python -m formproof_input.look_sketch      -> templates/db/look_strokes.json (outline + centre lines, mm)

Outline: every module of the CAD (clamp, arm + pad, joint, holder, phone) is projected onto the side plane (x, z),
filled, and traced; a module hides what is behind it in a fixed drawing order (holder > phone > joint > arm > clamp),
so the strokes look like a line drawing, not an X-ray. The handlebar end (circle) is added like in the T templates.
Centre lines (skeleton): ring, clamp marks, arm paths, joint, phone centre line - the quick one-line version.
Both are stored in mm in the team frame (handlebar centre = origin), so sketch.Matcher renders them in its ring frame.
"""
import json
import math
import os

import numpy as np
from skimage import draw, measure

from . import look as LK

DB = os.path.join(os.path.dirname(__file__), "templates", "db", "look_strokes.json")
ORDER = ("clamp", "arm", "joint", "phone", "holder")      # later = in front
PX = 0.25                                                  # mm per raster pixel
_CACHE = None


def _project(solids, lo, shape):
    from PIL import Image, ImageDraw
    im = Image.new("1", (shape[1], shape[0]), 0)
    dr = ImageDraw.Draw(im)
    for sol in solids:
        verts, tris = sol.tessellate(0.15, 0.2)
        if not tris:
            continue
        v = np.array([[p.x, p.z] for p in verts])
        uv = np.c_[(v[:, 0] - lo[0]) / PX, (v[:, 1] - lo[1]) / PX].tolist()
        for a, b, d in tris:
            dr.polygon([tuple(uv[a]), tuple(uv[b]), tuple(uv[d])], fill=1, outline=1)
    return np.array(im, bool)          # row = z index (z up handled by the tracer: rows are z from lo)


def _trace(mask, lo, min_len=2.5):
    out = []
    pad = np.pad(mask, 1).astype(float)
    for c in measure.find_contours(pad, 0.5):
        c = measure.approximate_polygon(c, tolerance=1.2)
        xy = np.c_[(c[:, 1] - 1) * PX + lo[0], (c[:, 0] - 1) * PX + lo[1]]
        if len(xy) >= 2 and np.hypot(*np.diff(xy, axis=0).T).sum() >= min_len:
            out.append(np.round(xy, 2))
    return out


def look_strokes(spec):
    """CAD side-view outline (visible edges per module) + centre lines of a look spec."""
    from .cad import build_look
    _, parts = build_look(spec, with_holder=True, with_phone=True)
    groups = {k: [] for k in ORDER}
    for mat, sol, mod in parts:
        if mat == "screen":
            continue
        groups["arm" if mod == "arm" else mod].append(sol)
    bbs = [s.BoundingBox() for v in groups.values() for s in v]
    lo = np.array([min(b.xmin for b in bbs) - 3, min(b.zmin for b in bbs) - 3])
    hi = np.array([max(b.xmax for b in bbs) + 3, max(b.zmax for b in bbs) + 3])
    shape = (int((hi[1] - lo[1]) / PX) + 1, int((hi[0] - lo[0]) / PX) + 1)
    masks = {k: _project(v, lo, shape) for k, v in groups.items()}
    front = np.zeros(shape, bool)
    outline = []
    for k in reversed(ORDER):
        vis = masks[k] & ~front
        outline += [dict(part=k, mm=c.tolist()) for c in _trace(vis, lo)]
        front |= masks[k]
    g = spec["geometry"]
    a = np.linspace(0, 2 * np.pi, 49)
    outline.append(dict(part="bar", mm=np.round(np.c_[g["bar_d"] / 2 * np.cos(a), g["bar_d"] / 2 * np.sin(a)], 2).tolist()))
    return dict(outline=outline, skeleton=look_skeleton(spec), bbox=[lo.round(1).tolist(), hi.round(1).tolist()])


def look_skeleton(spec):
    g = spec["geometry"]
    L = g["look"]
    ri, ro = g["bore_r"], g["ring_ro"]
    rm = (ri + ro) / 2
    a = np.linspace(0, 2 * np.pi, 49)
    out = []
    if L["clamp"] == "strap":
        a0 = np.linspace(0, np.pi, 25)
        out.append(("ring", np.c_[rm * np.cos(a0), rm * np.sin(a0)]))
        a1 = np.linspace(np.pi, 2 * np.pi, 25)
        r1 = g["bar_d"] / 2 + 1.0
        out.append(("strap", np.c_[r1 * np.cos(a1), r1 * np.sin(a1)]))
    else:
        out.append(("ring", np.c_[rm * np.cos(a), rm * np.sin(a)]))
        if L["clamp"] == "bolt":
            xe = sum(g["ear_x"]) / 2
            out += [("ear", np.array([[s * xe, g["ear_z"][1]], [s * xe, g["ear_z"][0]]])) for s in (-1, 1)]
        else:                                                          # hinge: knob below the front
            k0 = np.array([ro * math.cos(math.radians(-36)), ro * math.sin(math.radians(-36))])
            out.append(("knob", np.array([k0, k0 + 10 * np.array([0.5, -0.866])])))
    out += [("arm", np.asarray(p, float)) for p in g["arm"]["paths"]]
    base = np.array([L["base"][0], L["base"][2]])
    th = math.radians(L["tilt_deg"])
    nrm = np.array([-math.sin(th), math.cos(th)])
    tan = np.array([math.cos(th), math.sin(th)])
    ph = g["phone"]
    from . import mount_modules as MM
    depth = MM.HOLDERS[L["holder"]]["fn"](ph["H"], ph["W"], ph["D"])[1]
    org = base + np.array([0, L["joint_len"]]) + nrm * depth
    out.append(("joint", np.array([base, base + np.array([0, L["joint_len"]])])))
    out.append(("holder", np.array([base + np.array([0, L["joint_len"]]), org])))
    c = org + nrm * ph["D"] / 2
    out.append(("phone", np.array([c - tan * ph["H"] / 2, c + tan * ph["H"] / 2])))
    return [dict(part=n, mm=np.round(s, 2).tolist()) for n, s in out]


def _one(t):
    from .templates import bike_mount
    sp = bike_mount.build_spec(t["params"], t["id"])
    return look_key(t["params"]["look"]), dict(look_strokes(sp), tilt_deg=sp["geometry"]["look"]["tilt_deg"], ids=[t["id"]])


def look_key(L):
    return "|".join(str(L.get(k)) for k in ("clamp", "arm", "section", "joint", "holder"))


def build(templates=None, force=False):
    from .templates import bike_mount
    from .templates.library import LOOKS
    templates = templates or LOOKS
    out = dict(load()) if os.path.exists(DB) else {}
    todo, seen = [], set()
    for t in templates:
        key = look_key(t["params"]["look"])
        if (force or key not in out) and key not in seen:
            todo.append(t)
            seen.add(key)
    from multiprocessing import Pool
    with Pool(max(1, os.cpu_count() or 1)) as pool:
        for k, (key, rec) in enumerate(pool.imap_unordered(_one, todo)):
            out[key] = rec
            print(f"{k + 1}/{len(todo)} {rec['ids'][0]}", flush=True)
            if k % 10 == 9:
                _save(out)
    for t in templates:
        ids = out[look_key(t["params"]["look"])].setdefault("ids", [])
        if t["id"] not in ids:
            ids.append(t["id"])
    _save(out)
    return out


def _save(out):
    global _CACHE
    tmp = DB + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(dict(frame="x 앞, z 위, 원점 = 핸들바 중심(mm). outline = CAD 측면 윤곽(보이는 선), skeleton = 중심선",
                       phone="기본 폰(160 × 76 × 8 mm)", templates=dict(sorted(out.items()))), f, ensure_ascii=False,
                  separators=(",", ":"))
    os.replace(tmp, DB)
    _CACHE = None


def load():
    global _CACHE
    if _CACHE is None:
        _CACHE = json.load(open(DB, encoding="utf-8"))["templates"] if os.path.exists(DB) else {}
    return _CACHE


def strokes_for(look, style="outline", phone=True):
    """Stored strokes of a look (params['look']) as (name, Nx2 mm array) pairs."""
    rec = load()[look_key(look)]
    out = [(s["part"], np.asarray(s["mm"], float)) for s in rec[style]]
    return [(n, s) for n, s in out if phone or n != "phone"]


if __name__ == "__main__":
    import sys
    build(force="--force" in sys.argv)
