"""Side-view sketch -> template (track 1, CPU only, no learned weights).

The clamp ring around the handlebar is drawn in every side-view sketch, so it is used as the
reference object: the query is translated / scaled / mirrored so that the ring has a fixed centre
and radius, then compared with each template rendered in the same frame
(chamfer distance both ways + orientation histogram). If no ring is found (e.g. a photo),
a bounding-box fit is used instead and the result is flagged as low confidence.
"""
import math
import numpy as np
from scipy import ndimage
from skimage.morphology import skeletonize
from skimage.transform import hough_circle, hough_circle_peaks

from .templates.bike_mount import DEFAULT, _arm_segments
from . import evidence as ev

W, H = 128, 96            # comparison canvas (x right, y up)
C0 = np.array([26.0, 40.0])   # ring centre on the canvas
R_PX = 8.0                # ring outer radius on the canvas
PAD = 6


# ------------------------------------------------------------------ template -> strokes (mm)
def _circle(r, cx=0.0, cz=0.0, n=48):
    a = np.linspace(0, 2 * np.pi, n + 1)
    return np.c_[cx + r * np.cos(a), cz + r * np.sin(a)]


def _rect(x0, x1, z0, z1):
    return np.array([[x0, z0], [x1, z0], [x1, z1], [x0, z1], [x0, z0]], float)


def _thick_seg(p0, p1, t):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    d = p1 - p0
    n = np.array([-d[1], d[0]]) / max(np.linalg.norm(d), 1e-9) * t / 2
    return np.array([p0 + n, p1 + n, p1 - n, p0 - n, p0 + n])


def ring_radius(params):
    p = dict(DEFAULT)
    p.update(params)
    return p["bar_d"] / 2 + p["bore_gap"] + p["ring_t"]


def template_strokes(params, phone=True):
    """Side-view outline of the 1st design (+ phone) in mm; stroke 0 = ring, 1 = bar, 2 = ears."""
    p = dict(DEFAULT)
    p.update(params)
    R = p["bar_d"] / 2
    bore = R + p["bore_gap"]
    ro = bore + p["ring_t"]
    ear_top, ear_bot = -bore + 2.0, -bore + 2.0 - p["ear_len"]
    strokes = [_circle(ro), _circle(R), _rect(-p["ear_x"][1], p["ear_x"][1], ear_bot, ear_top)]
    strokes += [_thick_seg(a, b, p["arm_t"]) for a, b in _arm_segments(p, ro)]
    x0, x1 = p["pad_x0"], p["pad_x0"] + p["pad_len"]
    z0, z1 = p["pad_z0"], p["pad_z0"] + p["pad_t"]
    strokes.append(_rect(x0, x1, z0, z1))
    if phone:
        L = ev.PHONES.get(p["phone"], {}).get("dims", (160.0,))[0]
        xc = (x0 + x1) / 2
        strokes.append(_rect(xc - L / 2, xc + L / 2, z1 + 8.0, z1 + 17.0))       # phone in the clamp
        strokes.append(_rect(xc - 6, xc + 6, z1, z1 + 8.0))                     # clamp stem
    return strokes


# ------------------------------------------------------------------ geometry helpers
def _resample(poly, step):
    poly = np.asarray(poly, float)
    seg = np.diff(poly, axis=0)
    L = np.r_[0, np.cumsum(np.hypot(seg[:, 0], seg[:, 1]))]
    if L[-1] < 1e-9:
        return poly[:1]
    s = np.linspace(0, L[-1], max(int(L[-1] / step) + 2, 2))
    return np.c_[np.interp(s, L, poly[:, 0]), np.interp(s, L, poly[:, 1])]


def _plot(u, w, h, width=1):
    img = np.zeros((h, w), bool)
    c = np.round(u[:, 0]).astype(int)
    r = np.round(h - 1 - u[:, 1]).astype(int)
    ok = (c >= 0) & (c < w) & (r >= 0) & (r < h)
    img[r[ok], c[ok]] = True
    if width > 1:
        img = ndimage.binary_dilation(img, iterations=width // 2)
    return img


def strokes_to_points(strokes, step):
    return np.vstack([_resample(s, step) for s in strokes])


def canonical_map(pts, centre, radius, mirror=False, width=2):
    """Points (y-up) -> canvas with the ring at C0 / R_PX."""
    u = (pts - centre) / radius * R_PX
    if mirror:
        u[:, 0] = -u[:, 0]
    return _plot(u + C0, W, H, width).astype(np.float32)


def bbox_map(pts, width=2):
    lo, hi = pts.min(0), pts.max(0)
    span = np.maximum(hi - lo, 1e-9)
    s = min((W - 2 * PAD) / span[0], (H - 2 * PAD) / span[1])
    off = np.array([(W - s * span[0]) / 2, (H - s * span[1]) / 2])
    return _plot((pts - lo) * s + off, W, H, width).astype(np.float32)


# ------------------------------------------------------------------ user image -> points + ring
def ink_points(gray, photo=False):
    g = np.asarray(gray, float)
    if g.ndim == 3:
        g = g[..., :3].mean(-1)
    if g.max() > 1.5:
        g = g / 255.0
    if photo:
        from skimage import feature
        ink = feature.canny(g, sigma=2.0)
    else:
        ink = g < 0.5
    lab, n = ndimage.label(ink)                                     # drop specks
    if n:
        size = ndimage.sum(ink, lab, np.arange(1, n + 1))
        ink = np.isin(lab, np.where(size >= 6)[0] + 1)
    rr, cc = np.nonzero(ink)
    if len(rr) < 10:
        raise ValueError("no strokes found in the image")
    return np.c_[cc, g.shape[0] - 1 - rr].astype(float)


def find_ring(pts):
    """Hough circle on a 256-wide working raster. Returns (centre, radius, score) in point units."""
    lo, hi = pts.min(0), pts.max(0)
    span = max(np.ptp(pts[:, 0]), np.ptp(pts[:, 1]), 1e-9)
    s = 240.0 / span
    w, h = int(np.ptp(pts[:, 0]) * s) + 17, int(np.ptp(pts[:, 1]) * s) + 17
    img = _plot((pts - lo) * s + 8, w, h, 1)
    img = ndimage.binary_dilation(skeletonize(ndimage.binary_closing(img, iterations=2)), iterations=1)
    radii = np.arange(6, 60)
    acc = hough_circle(img, radii)
    a, cx, cy, rad = hough_circle_peaks(acc, radii, total_num_peaks=20, min_xdistance=3, min_ydistance=3)
    if len(a) == 0:
        return None
    # accumulator is normalised by circumference = fraction of the circle that is inked.
    # Small circles fit any corner, so rank by inked arc length among well-closed circles;
    # this also prefers the outer clamp ring over the bar circle drawn inside it.
    frac = np.asarray(a, float)
    arc = frac * rad * np.where(frac >= 0.55, 1.0, 0.0)
    if arc.max() <= 0:
        arc = frac * rad
    best = int(np.argmax(arc))
    centre = (np.array([cx[best], h - 1 - cy[best]], float) - 8) / s + lo
    r = rad[best] / s
    # refine: algebraic (Kasa) circle fit to ink points in a narrowing annulus around the Hough circle
    for band in (0.15, 0.08):
        d = np.hypot(*(pts - centre).T)
        q = pts[np.abs(d - r) <= band * r]
        if len(q) < 12:
            break
        A = np.c_[2 * q, np.ones(len(q))]
        sol, *_ = np.linalg.lstsq(A, (q ** 2).sum(1), rcond=None)
        centre, r = sol[:2], float(np.sqrt(sol[2] + sol[:2] @ sol[:2]))
    return centre, r, float(frac[best])


# ------------------------------------------------------------------ features & matcher
def _dt(img):
    return ndimage.distance_transform_edt(img < 0.5)


def _orient_hist(img, gx=4, gy=3, bins=8):
    b = ndimage.gaussian_filter(img, 1.0)
    sx, sy = ndimage.sobel(b, 1), ndimage.sobel(b, 0)
    mag = np.hypot(sx, sy)
    k = np.minimum(((np.arctan2(sy, sx) % np.pi) / np.pi * bins).astype(int), bins - 1)
    hist = np.zeros((gy, gx, bins))
    ys = np.minimum(np.arange(H) * gy // H, gy - 1)
    xs = np.minimum(np.arange(W) * gx // W, gx - 1)
    np.add.at(hist, (ys[:, None].repeat(W, 1), xs[None, :].repeat(H, 0), k), mag)
    return (hist / (np.linalg.norm(hist) + 1e-9)).ravel()


def _feat(img):
    return dict(img=img, dt=_dt(img), hist=_orient_hist(img))


def _chamfer(a, dt_b, trim=0.9):
    d = np.sort(dt_b[a > 0.5])
    return float(d[: max(1, int(len(d) * trim))].mean()) if len(d) else 1e3


class Matcher:
    RING_MIN_SCORE = 0.45          # fraction of the ring circumference that must be inked

    ROTATIONS = (-8, -4, 0, 4, 8)  # hand sketches are rarely level; search small tilts about the ring

    def __init__(self, templates, w_hist=2.0):
        self.templates = templates
        self.w_hist = w_hist           # tuned on synthetic sketches (README: matcher accuracy)
        self.refs = {"ring": [], "bbox": []}
        for i, t in enumerate(templates):
            ro = ring_radius(t["params"])
            for ph in (False, True):
                pts = strokes_to_points(template_strokes(t["params"], phone=ph), ro / 20)
                self.refs["ring"].append(dict(t=i, phone=ph, **_feat(canonical_map(pts, np.zeros(2), ro))))
                self.refs["bbox"].append(dict(t=i, phone=ph, **_feat(bbox_map(pts))))

    def query_maps(self, pts):
        """Candidate query canvases: ring frame (both mirrors) if a ring is found, else bbox frame."""
        ring = find_ring(pts)
        if ring is not None and ring[2] >= self.RING_MIN_SCORE:
            c, r, sc = ring
            maps = []
            for a in self.ROTATIONS:
                th = math.radians(a)
                rot = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
                pr = (pts - c) @ rot.T + c
                maps += [((m, a), _feat(canonical_map(pr, c, r, mirror=m))) for m in (False, True)]
            return "ring", sc, maps
        q = bbox_map(pts)
        return "bbox", (ring[2] if ring else 0.0), [((False, 0), _feat(q)), ((True, 0), _feat(q[:, ::-1].copy()))]

    def match_points(self, pts, k=3):
        frame, ring_score, queries = self.query_maps(pts)
        best = {}
        for (mir, _), q in queries:
            for r in self.refs[frame]:
                s = 0.5 * (_chamfer(q["img"], r["dt"]) + _chamfer(r["img"], q["dt"])) \
                    + self.w_hist * float(np.linalg.norm(q["hist"] - r["hist"]))
                if r["t"] not in best or s < best[r["t"]][0]:
                    best[r["t"]] = (s, mir)
        ranked = sorted((s, i, m) for i, (s, m) in best.items())
        s0 = ranked[0][0]
        res = [dict(id=self.templates[i]["id"], name=self.templates[i]["name"], score=round(s, 3), mirrored=m,
                    confidence=round(math.exp(-(s - s0) / 0.5), 3)) for s, i, m in ranked[:k]]
        return dict(frame=frame, ring_score=round(ring_score, 2), candidates=res)

    def match_image(self, gray, photo=False, k=3):
        return self.match_points(ink_points(gray, photo), k)


# ------------------------------------------------------------------ synthetic hand-drawn sketches
def perturb(strokes, rng, strength=1.0, drop=(1, 2)):
    """Hand-drawn look: wobble, per-stroke offset, global rotation / anisotropic scale, omitted details."""
    ang = math.radians(rng.uniform(-8, 8) * strength)
    rot = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
    sc = 1 + rng.uniform(-0.08, 0.08, 2) * strength
    span = np.ptp(np.vstack(strokes), 0).max()
    out = []
    for k, poly in enumerate(strokes):
        if k in drop and rng.random() < 0.4 * strength:
            continue
        q = _resample(poly, span / 150)
        n = len(q)
        wob = ndimage.gaussian_filter1d(rng.normal(0, 1, (n, 2)), sigma=max(n / 12, 1), axis=0, mode="nearest")
        wob = wob / (np.abs(wob).max() + 1e-9) * span * 0.012 * strength
        out.append(q + wob + rng.normal(0, span * 0.01 * strength, 2))
    c = np.vstack(out).mean(0)
    return [((q - c) * sc) @ rot.T + c for q in out]


def draw_image(strokes, px=480, mirror=False, line=3):
    """Render strokes as a 'scanned' sketch image (white paper, dark ink) of arbitrary size."""
    pts = np.vstack(strokes)
    lo = pts.min(0)
    s = (px - 40) / max(np.ptp(pts[:, 0]), np.ptp(pts[:, 1]))
    w, h = int(np.ptp(pts[:, 0]) * s) + 40, int(np.ptp(pts[:, 1]) * s) + 40
    img = np.zeros((h, w), bool)
    for poly in strokes:
        u = (_resample(poly, 0.5 / s) - lo) * s + 20
        img |= _plot(u, w, h, line)
    if mirror:
        img = img[:, ::-1]
    return np.where(img, 0.1, 0.95)
