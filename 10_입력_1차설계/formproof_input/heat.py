"""Heat-map values on a CAD mesh: sample nodal fields of an analysis grid at mesh vertices, pack them for the viewer."""
import base64

import numpy as np


def nodal_from_elements(vals, enodes, nn, mask):
    """Element values -> node values (mean over the masked elements touching each node); returns values, valid."""
    s = np.zeros(nn)
    c = np.zeros(nn)
    idx = np.where(mask)[0]
    np.add.at(s, enodes[idx].ravel(), np.repeat(vals[idx], enodes.shape[1]))
    np.add.at(c, enodes[idx].ravel(), 1)
    return s / np.maximum(c, 1), c > 0


def sample_nodes(pts, node_vals, valid, origin, h, shape, margin=1.0):
    """Trilinear interpolation of node values (node index = (k*(ny+1)+j)*(nx+1)+i) using only valid nodes.
    pts in the grid frame; outside the grid (beyond margin) or no valid corner -> NaN."""
    nx, ny, nz = shape
    P = (np.asarray(pts, float) - np.asarray(origin, float)) / h
    out = np.full(len(P), np.nan)
    inside = np.all((P >= -margin / h) & (P <= np.array([nx, ny, nz]) + margin / h), axis=1)
    Q = np.clip(P, 0, np.array([nx, ny, nz]) - 1e-6)
    i0 = np.floor(Q).astype(int)
    f = Q - i0
    acc = np.zeros(len(P))
    wsum = np.zeros(len(P))
    vals = np.asarray(node_vals, float)
    ok = np.asarray(valid, bool)
    for dk in (0, 1):
        for dj in (0, 1):
            for di in (0, 1):
                ii, jj, kk = i0[:, 0] + di, i0[:, 1] + dj, i0[:, 2] + dk
                n = (kk * (ny + 1) + jj) * (nx + 1) + ii
                w = (f[:, 0] if di else 1 - f[:, 0]) * (f[:, 1] if dj else 1 - f[:, 1]) * (f[:, 2] if dk else 1 - f[:, 2])
                w = w * ok[n] + 1e-9 * ok[n]
                acc += w * vals[n]
                wsum += w
    good = inside & (wsum > 0)
    out[good] = acc[good] / wsum[good]
    return out


def pack(v, lo, hi):
    """uint8 per vertex: 0..254 = lo..hi (clipped), 255 = no data. base64 for the viewer."""
    v = np.asarray(v, float)
    q = np.full(len(v), 255, np.uint8)
    m = np.isfinite(v)
    lo, hi = float(f"{lo:.3g}"), float(f"{hi:.3g}")
    q[m] = np.clip(np.round((v[m] - lo) / (hi - lo) * 254), 0, 254).astype(np.uint8)
    r = lambda x: float(f"{x:.3g}")
    return dict(q=base64.b64encode(q.tobytes()).decode(), lo=r(lo), hi=r(hi))
