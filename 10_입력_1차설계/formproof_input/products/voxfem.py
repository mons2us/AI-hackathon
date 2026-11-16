"""Small voxel FEM for the demo products (TV stand, AR glasses): CAD mesh -> voxels -> linear static solve ->
von Mises / displacement node fields for the viewer's heat maps (same packing as the bike mount).

hex8 element = fem.hex8_KB (team 3D code). Loads are rigid-body distributions over node sets (least squares, like
the team's phone payload), supports = fixed node sets."""
import numpy as np
import scipy.sparse as sp

from ..fem import hex8_KB
from ..heat import grid_info, pack_nodes


def voxelize(mesh, h, pad=1):
    """Watertight trimesh -> occupancy (nz, ny, nx) of element centres inside (layer slices, even-odd), grid origin."""
    import manifold3d as mf
    from matplotlib.path import Path
    lo = mesh.bounds[0] - pad * h
    hi = mesh.bounds[1] + pad * h
    n = np.ceil((hi - lo) / h).astype(int)
    xs, ys, zs = (lo[a] + h * (np.arange(n[a]) + 0.5) for a in range(3))
    A = mf.Manifold(mf.Mesh(vert_properties=np.asarray(mesh.vertices, np.float32), tri_verts=np.asarray(mesh.faces, np.uint32)))
    X, Y = np.meshgrid(xs, ys)
    pts = np.c_[X.ravel(), Y.ravel()]
    occ = np.zeros((n[2], n[1], n[0]), bool)
    for k, z in enumerate(zs):
        w = np.zeros(len(pts), int)
        for poly in A.slice(float(z)).to_polygons():
            P = np.asarray(poly)
            if len(P) < 3:
                continue
            bb = (pts[:, 0] >= P[:, 0].min()) & (pts[:, 0] <= P[:, 0].max()) & (pts[:, 1] >= P[:, 1].min()) & (pts[:, 1] <= P[:, 1].max())
            if bb.any():
                w[bb] += Path(P).contains_points(pts[bb])
        occ[k] = ((w % 2) == 1).reshape(n[1], n[0])
    return occ, lo


class VoxModel:
    """Nodes are numbered compactly (only nodes of solid voxels carry dofs); `node_xyz`, `used`, loads, displacements
    and node fields are all in that compact numbering. The full bounding-box grid is used only for the viewer texture
    (`heat`), so memory scales with the part, not with its bounding box (a 1.5 m TV stand is mostly air)."""

    def __init__(self, occ, origin, h, E, nu):
        self.occ, self.origin, self.h = occ, np.asarray(origin, float), float(h)
        nz, ny, nx = occ.shape
        self.shape = (nx, ny, nz)
        self.NX, self.NY, self.NZ = nx + 1, ny + 1, nz + 1
        self.n_grid = self.NX * self.NY * self.NZ
        k, j, i = np.nonzero(occ)
        self.el = np.c_[i, j, k].astype(np.int32)
        self.ne = len(self.el)
        nid = lambda a, b, c: ((c * self.NY + b) * self.NX + a).astype(np.int64)
        corners = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]
        en_grid = np.stack([nid(i + a, j + b, k + c) for a, b, c in corners], 1)
        self.gid, inv = np.unique(en_grid, return_inverse=True)            # compact node -> grid node
        self.en = inv.reshape(en_grid.shape).astype(np.int32)
        self.nn = len(self.gid)
        self.KE, self.C, self.B0, _ = hex8_KB(E, nu, h)
        self.edof = np.stack([3 * self.en, 3 * self.en + 1, 3 * self.en + 2], 2).reshape(self.ne, 24).astype(np.int32)
        self.used = np.ones(self.nn, bool)
        g = self.gid
        self.node_xyz = self.origin + h * np.c_[g % self.NX, (g // self.NX) % self.NY, g // (self.NX * self.NY)]
        self.el_xyz = self.origin + h * (self.el + 0.5)

    def stiffness(self):
        if getattr(self, "_K", None) is None:
            rows = np.repeat(self.edof, 24, 1).ravel()
            cols = np.tile(self.edof, (1, 24)).ravel()
            self._K = sp.csr_matrix((np.tile(self.KE.ravel(), self.ne), (rows, cols)), shape=(3 * self.nn, 3 * self.nn))
            del rows, cols
        return self._K

    def solve(self, fixed_nodes, F):
        """Linear static: fixed node indices (all dofs), F (3*nn,). Returns u (3*nn,)."""
        K = self.stiffness()
        fixed_nodes = np.asarray(fixed_nodes, np.int64)
        fd = np.r_[3 * fixed_nodes, 3 * fixed_nodes + 1, 3 * fixed_nodes + 2]
        free = np.setdiff1d(np.arange(3 * self.nn), fd)
        A = K[free][:, free].tocsr()
        u = np.zeros(3 * self.nn)
        try:
            import pypardiso
            solver = pypardiso.PyPardisoSolver()
            try:
                u[free] = solver.solve(A, F[free])
            finally:
                solver.free_memory(everything=True)              # MKL keeps the factors otherwise
        except Exception:                                   # pragma: no cover - no MKL
            from scipy.sparse.linalg import spsolve
            u[free] = spsolve(A.tocsc(), F[free])
        return u

    def von_mises(self, u):
        s = (self.C @ self.B0 @ u[self.edof].T).T
        return np.sqrt(0.5 * ((s[:, 0] - s[:, 1]) ** 2 + (s[:, 1] - s[:, 2]) ** 2 + (s[:, 2] - s[:, 0]) ** 2)
                       + 3 * (s[:, 3:] ** 2).sum(1))

    def rigid_load(self, nodes, point, F, M=(0.0, 0.0, 0.0)):
        """Force F and moment M about `point`, spread over `nodes` as a rigid body (least squares)."""
        P = self.node_xyz[nodes] - np.asarray(point, float)
        T = np.zeros((3 * len(nodes), 6))
        for q, (x, y, z) in enumerate(P):
            T[3 * q:3 * q + 3, :3] = np.eye(3)
            T[3 * q:3 * q + 3, 3:] = [[0, z, -y], [-z, 0, x], [y, -x, 0]]
        f = np.linalg.pinv(T).T @ np.r_[F, M]
        out = np.zeros(3 * self.nn)
        for q, n in enumerate(nodes):
            out[3 * n:3 * n + 3] = f[3 * q:3 * q + 3]
        return out

    def rigid_fit(self, u, nodes, point):
        """Translation + rotation of a node set (least squares) -> displacement of `point` far away."""
        P = self.node_xyz[nodes] - np.asarray(point, float)
        T = np.zeros((3 * len(nodes), 6))
        for q, (x, y, z) in enumerate(P):
            T[3 * q:3 * q + 3, :3] = np.eye(3)
            T[3 * q:3 * q + 3, 3:] = [[0, z, -y], [-z, 0, x], [y, -x, 0]]
        d = np.c_[u[3 * nodes], u[3 * nodes + 1], u[3 * nodes + 2]].ravel()
        sol = np.linalg.lstsq(T, d, rcond=None)[0]
        return sol[:3], sol[3:]

    def nodal(self, vals):
        s = np.zeros(self.nn)
        c = np.zeros(self.nn)
        np.add.at(s, self.en.ravel(), np.repeat(vals, 8))
        np.add.at(c, self.en.ravel(), 1)
        return s / np.maximum(c, 1), c > 0

    def heat(self, fields):
        """fields: {key: (compact node values, lo, hi, name, unit, note)} -> viewer payload on the full grid (no mirror)."""
        out = {}
        valid = np.zeros(self.n_grid, bool)
        valid[self.gid] = True
        for k, (v, lo, hi, name, unit, note) in fields.items():
            full = np.zeros(self.n_grid)
            full[self.gid] = v
            out[k] = dict(pack_nodes(full, valid, lo, hi), name=name, unit=unit, note=note)
        return dict(grid=grid_info(self.origin, self.h, self.shape, 0.0, ysym=0.0, yoff=0.0, mirror=False), fields=out)


def pick_h(mesh, target=35000, lo=0.8, hi=12.0):
    """Voxel size so the part has about `target` elements."""
    return float(np.clip((abs(mesh.volume) / target) ** (1 / 3), lo, hi))
