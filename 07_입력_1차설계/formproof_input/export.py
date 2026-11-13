"""Hand-off files: 1st-design STL (full model, mirrored), side-view preview PNG."""
import numpy as np
from scipy import ndimage
from skimage import measure


def full_voxels(P, dens, include_rigid=False):
    """(nz, 2*ny, nx) bool of the full model, mirrored across the symmetry plane."""
    on = P.solid | (P.design & (dens > 0.5)) | (P.rigid & include_rigid)
    nx, ny, nz = P.shape
    v = on.reshape(nz, ny, nx)
    if P.sym_axis == 1:
        v = np.concatenate([v[:, ::-1, :], v], axis=1)
    return v


def write_stl(P, dens, path, smooth=0.6):
    v = full_voxels(P, dens).astype(np.float32)
    f = np.pad(v, 2)
    if smooth:
        f = ndimage.gaussian_filter(f, smooth)
    verts, faces, _, _ = measure.marching_cubes(f, 0.5, spacing=(P.h,) * 3)
    ny_full = v.shape[1]
    o = P.origin.copy()
    if P.sym_axis == 1:
        o[1] = P.origin[1] - ny_full // 2 * P.h
    verts = verts[:, ::-1] - 2 * P.h + P.h / 2 + o           # samples are voxel centres; (z,y,x) -> (x,y,z) mm
    # (z,y,x)->(x,y,z) is a reflection, which already flips skimage winding to outward normals
    tri = verts[faces].astype(np.float32)
    nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-12
    data = np.zeros(len(faces), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    data["n"], data["v"] = nrm, tri
    with open(path, "wb") as fo:
        fo.write(b"FormProof 1st design".ljust(80, b" "))
        fo.write(np.uint32(len(faces)).tobytes())
        fo.write(data.tobytes())
    vol = float(np.einsum("ij,ij->i", tri[:, 0], np.cross(tri[:, 1], tri[:, 2])).sum() / 6)
    return dict(triangles=int(len(faces)), volume_mm3=round(abs(vol), 1),
                bbox=[verts.min(0).round(1).tolist(), verts.max(0).round(1).tolist()])


def side_preview(P, dens, path, title=""):
    """Side view (x-z) of the analysis problem: design space / fixed parts / 1st design / supports."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    have = {f.name for f in font_manager.fontManager.ttflist}
    plt.rcParams["font.family"] = [f for f in ("Malgun Gothic", "AppleGothic", "NanumGothic", "Noto Sans CJK KR",
                                               "Noto Sans CJK JP", "DejaVu Sans") if f in have] or ["sans-serif"]
    nx, ny, nz = P.shape
    lab = P.label.reshape(nz, ny, nx)
    first = (P.design & (dens > 0.5)).reshape(nz, ny, nx).any(1)
    img = np.ones((nz, nx, 3))
    img[(lab == 0).any(1)] = (0.90, 0.93, 0.98)       # design space
    img[first] = (0.25, 0.45, 0.85)                   # 1st design
    img[(lab == 1).any(1)] = (0.35, 0.35, 0.35)       # keep (solid)
    img[(lab == 3).any(1)] = (0.85, 0.55, 0.15)       # phone clamp (rigid)
    ext = [P.origin[0], P.origin[0] + nx * P.h, P.origin[2], P.origin[2] + nz * P.h]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.imshow(img[::-1], extent=ext)
    sup = P.supports[next(iter(P.supports))]
    ax.plot(P.nodes[sup, 0], P.nodes[sup, 2], ".", ms=2, color="crimson", label="고정(핸들바)")
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=(0.90, 0.93, 0.98), label="설계 영역"), Patch(color=(0.25, 0.45, 0.85), label="1차 설계"),
                       Patch(color=(0.35, 0.35, 0.35), label="지킬 곳"), Patch(color=(0.85, 0.55, 0.15), label="폰 클램프(강체)"),
                       ax.lines[0]], loc="lower right", fontsize=7)
    ax.set_xlabel("x (앞) mm"), ax.set_ylabel("z (위) mm"), ax.set_title(title, fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
