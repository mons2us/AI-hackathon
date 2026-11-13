"""3D hex8 구조 격자 FEM.

요소 강성(hex8_KB)은 팀 코드 03_자전거거치대/code_3D/fem3d.py 와 동일한 식(2x2x2 가우스 적분)을 사용.
격자 번호 규칙도 팀 코드(opt3d.py)와 같음:
  요소 e = (k*ny + j)*nx + i,  절점 n = (k*NY + j)*NX + i,  NX = nx+1 ...
"""
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla

try:
    import pypardiso
    HAVE_PARDISO = True
except Exception:  # pragma: no cover
    HAVE_PARDISO = False

XI = np.array([[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
               [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]], float)


def hex8_KB(E, nu, h):
    """요소 강성 KE(24x24), 탄성 행렬 C(6x6), 중심 변형률 행렬 B0(6x24). 팀 fem3d.hex8_KB 와 동일."""
    C = E / ((1 + nu) * (1 - 2 * nu)) * np.array([
        [1 - nu, nu, nu, 0, 0, 0], [nu, 1 - nu, nu, 0, 0, 0], [nu, nu, 1 - nu, 0, 0, 0],
        [0, 0, 0, (1 - 2 * nu) / 2, 0, 0], [0, 0, 0, 0, (1 - 2 * nu) / 2, 0], [0, 0, 0, 0, 0, (1 - 2 * nu) / 2]])
    g = 1 / np.sqrt(3)
    K = np.zeros((24, 24))

    def B(p):
        dN = np.array([[XI[a, 0] * (1 + XI[a, 1] * p[1]) * (1 + XI[a, 2] * p[2]),
                        XI[a, 1] * (1 + XI[a, 0] * p[0]) * (1 + XI[a, 2] * p[2]),
                        XI[a, 2] * (1 + XI[a, 0] * p[0]) * (1 + XI[a, 1] * p[1])] for a in range(8)]) / 8 * (2 / h)
        Bm = np.zeros((6, 24))
        for a in range(8):
            x, y, z = dN[a]
            i = 3 * a
            Bm[0, i] = x; Bm[1, i + 1] = y; Bm[2, i + 2] = z
            Bm[3, i] = y; Bm[3, i + 1] = x
            Bm[4, i + 1] = z; Bm[4, i + 2] = y
            Bm[5, i] = z; Bm[5, i + 2] = x
        return Bm

    for a in (-g, g):
        for b in (-g, g):
            for c in (-g, g):
                Bm = B((a, b, c))
                K += Bm.T @ C @ Bm * (h / 2) ** 3
    return K, C, B((0, 0, 0))


class Grid:
    """구조 격자: 요소·절점 번호, 좌표, edof."""

    def __init__(self, shape, h, origin):
        self.nx, self.ny, self.nz = shape
        self.h = float(h)
        self.origin = np.asarray(origin, float)
        nx, ny, nz = shape
        self.NX, self.NY, self.NZ = nx + 1, ny + 1, nz + 1
        self.ne = nx * ny * nz
        self.nn = self.NX * self.NY * self.NZ
        k, j, i = np.meshgrid(np.arange(nz), np.arange(ny), np.arange(nx), indexing='ij')
        self.I, self.J, self.K = i.ravel(), j.ravel(), k.ravel()
        o = self.origin
        self.xc = o[0] + h * (self.I + 0.5)
        self.yc = o[1] + h * (self.J + 0.5)
        self.zc = o[2] + h * (self.K + 0.5)
        corner = ((XI + 1) / 2).astype(int)
        self.en = np.stack([self.nid(self.I + c[0], self.J + c[1], self.K + c[2]) for c in corner], 1)
        self.edof = np.stack([3 * self.en, 3 * self.en + 1, 3 * self.en + 2], 2).reshape(self.ne, 24)
        n = np.arange(self.nn)
        self.gi, self.gj, self.gk = n % self.NX, (n // self.NX) % self.NY, n // (self.NX * self.NY)
        self.nxc = o[0] + h * self.gi
        self.nyc = o[1] + h * self.gj
        self.nzc = o[2] + h * self.gk
        self._iK = None

    def nid(self, i, j, k):
        return (k * self.NY + j) * self.NX + i

    def eshape(self, a):
        """요소 배열 (ne,) → (nz, ny, nx)"""
        return np.asarray(a).reshape(self.nz, self.ny, self.nx)

    def iK_jK(self, idx):
        ed = self.edof[idx]
        return np.repeat(ed, 24, 1).ravel(), np.tile(ed, (1, 24)).ravel()


class Factor:
    """K_ff 분해 (pypardiso 있으면 사용, 없으면 SuperLU)."""

    def __init__(self, A):
        self.A = A.tocsr()
        if HAVE_PARDISO:
            self.ps = pypardiso.PyPardisoSolver()
            self.ps.factorize(self.A)
        else:
            self.lu = sla.splu(self.A.tocsc())

    def solve(self, b):
        if HAVE_PARDISO:
            return self.ps.solve(self.A, b)
        return self.lu.solve(b)

    def free(self):
        if HAVE_PARDISO:
            self.ps.free_memory(everything=True)


def assemble(grid, KE, kscale, active):
    idx = np.where(active)[0]
    iK, jK = grid.iK_jK(idx)
    v = (KE.ravel()[None, :] * kscale[idx][:, None]).ravel()
    n3 = 3 * grid.nn
    return sp.coo_matrix((v, (iK, jK)), shape=(n3, n3)).tocsr()


def lumped_mass(grid, elem_mass, node_mass):
    m = np.zeros(grid.nn)
    np.add.at(m, grid.en.ravel(), np.repeat(elem_mass / 8.0, 8))
    return m + node_mass


def solve_cases(grid, K, free_by_bc, F_by_bc, M_node=None, modes_by_bc=None):
    """대칭 조건(bc)마다 한 번 분해해서 여러 하중을 풀고, 필요하면 고유값도 같은 분해로 계산.

    free_by_bc : {'S': free dof idx, 'A': ...}
    F_by_bc    : {'S': (3nn, m) 하중 행렬, ...}
    modes_by_bc: {'S': k, 'A': k}  (M_node 필요)
    반환: U_by_bc {bc: (3nn, m)}, freq_by_bc {bc: (k,) Hz}, modes {bc: (3nn,k)}
    """
    U, FR, MV = {}, {}, {}
    n3 = 3 * grid.nn
    for bc, fr in free_by_bc.items():
        A = K[fr][:, fr]
        fac = Factor(A)
        Fm = F_by_bc.get(bc)
        if Fm is not None and Fm.shape[1] > 0:
            Ub = np.zeros((n3, Fm.shape[1]))
            for c in range(Fm.shape[1]):
                Ub[fr, c] = fac.solve(np.ascontiguousarray(Fm[fr, c]))
            U[bc] = Ub
        k = (modes_by_bc or {}).get(bc, 0)
        if k:
            Md = sp.diags(np.repeat(M_node, 3)[fr])
            OP = sla.LinearOperator(A.shape, matvec=lambda v: fac.solve(np.ascontiguousarray(v)), dtype=float)
            w, V = sla.eigsh(A, k=k, M=Md, sigma=0, OPinv=OP, tol=1e-8)
            order = np.argsort(w)
            w, V = w[order], V[:, order]
            FR[bc] = np.sqrt(np.maximum(w, 0)) / (2 * np.pi)
            Vf = np.zeros((n3, k)); Vf[fr] = V
            MV[bc] = Vf
        fac.free()
    return U, FR, MV


def element_stress(grid, C, B0, u):
    """요소 중심 응력 (ne, 6) — 단위 강성(실제 재료) 기준. u: (3nn,)"""
    ue = u[grid.edof]
    return (C @ B0 @ ue.T).T


def von_mises(s):
    return np.sqrt(0.5 * ((s[:, 0] - s[:, 1]) ** 2 + (s[:, 1] - s[:, 2]) ** 2 + (s[:, 2] - s[:, 0]) ** 2)
                   + 3 * (s[:, 3:] ** 2).sum(1))
