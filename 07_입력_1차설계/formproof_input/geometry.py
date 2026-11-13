"""Primitive shapes for design-spec regions and node selectors.

Element regions use OPEN bounds (lo < c < hi) evaluated at element centres.
Node selectors use CLOSED bounds (lo <= c <= hi) evaluated at node coordinates.
The spec validator rejects element-region bounds that coincide with an element
centre, so open/closed never changes the result for elements.
"""
import numpy as np

AXES = {"x": 0, "y": 1, "z": 2}


def _cyl_r(pts, prim):
    """Radial distance from a cylinder axis. prim['axis'] in x/y/z, prim['center'] = the
    other two coordinates in (x,y,z) order with the axis removed."""
    a = AXES[prim["axis"]]
    others = [i for i in range(3) if i != a]
    c = prim.get("center", [0.0, 0.0])
    return np.sqrt((pts[:, others[0]] - c[0]) ** 2 + (pts[:, others[1]] - c[1]) ** 2)


def eval_prim(prim, pts, closed):
    """Return bool mask of points inside one primitive."""
    (kind, p), = prim.items()
    m = np.ones(len(pts), bool)
    lt = (lambda a, b: a <= b) if closed else (lambda a, b: a < b)
    if kind == "box":
        for ax, rng in p.items():
            if rng is None:
                continue
            v = pts[:, AXES[ax]]
            lo, hi = rng
            if lo is not None:
                m &= lt(lo, v)
            if hi is not None:
                m &= lt(v, hi)
        return m
    if kind == "cyl":
        r = _cyl_r(pts, p)
        if p.get("r_min") is not None:
            m &= r >= p["r_min"]          # matches opt3d (rr>=16.1)
        if p.get("r_max") is not None:
            m &= lt(r, p["r_max"]) if not closed else (r <= p["r_max"])
        for ax in ("x", "y", "z"):         # optional axial / planar limits on a cylinder
            if p.get(ax) is not None:
                m &= eval_prim({"box": {ax: p[ax]}}, pts, closed)
        return m
    if kind == "seg":
        # thick line segment in a plane, e.g. {"plane":"xz","p0":[x,z],"p1":[x,z],"t":6,"y":[lo,hi]}
        dist = eval_seg_dist(p, pts)
        m &= (dist <= p["t"] / 2) if closed else (dist < p["t"] / 2)
        for ax in ("x", "y", "z"):
            if p.get(ax) is not None:
                m &= eval_prim({"box": {ax: p[ax]}}, pts, closed)
        return m
    raise ValueError(f"unknown primitive '{kind}'")


def eval_seg_dist(p, pts):
    """Distance from points to a segment drawn in plane p['plane'] (e.g. 'xz')."""
    a, b = (AXES[c] for c in p["plane"])
    p0, p1 = np.asarray(p["p0"], float), np.asarray(p["p1"], float)
    q = np.c_[pts[:, a], pts[:, b]]
    d = p1 - p0
    s = np.clip(((q - p0) @ d) / max(d @ d, 1e-12), 0.0, 1.0)
    return np.linalg.norm(q - (p0 + s[:, None] * d), axis=1)


def eval_shape(shape, pts, closed=False):
    """shape = {'union': [[prim, prim, ...], ...]}  (OR of ANDs)  or a plain list of prims (AND)."""
    members = shape["union"] if isinstance(shape, dict) else [shape]
    out = np.zeros(len(pts), bool)
    for conj in members:
        m = np.ones(len(pts), bool)
        for prim in conj:
            m &= eval_prim(prim, pts, closed)
        out |= m
    return out


def element_bounds(shape):
    """Yield (axis_index, value, kind) for every scalar bound in a shape (for tie checks)."""
    members = shape["union"] if isinstance(shape, dict) else [shape]
    for conj in members:
        for prim in conj:
            (kind, p), = prim.items()
            if kind == "box":
                for ax, rng in p.items():
                    if rng is None:
                        continue
                    for v in rng:
                        if v is not None:
                            yield ("plane", AXES[ax], v, None)
            elif kind == "seg":
                for ax in ("x", "y", "z"):
                    if p.get(ax) is not None:
                        for v in p[ax]:
                            if v is not None:
                                yield ("plane", AXES[ax], v, None)
            elif kind == "cyl":
                for key in ("r_min", "r_max"):
                    if p.get(key) is not None:
                        yield ("radius", None, p[key], p)
                for ax in ("x", "y", "z"):
                    if p.get(ax) is not None:
                        for v in p[ax]:
                            if v is not None:
                                yield ("plane", AXES[ax], v, None)
