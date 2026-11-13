"""Design spec (JSON) -> voxel analysis problem for the physics stage.

Element / node numbering follows the team's optimisers (opt3d.py, tvopt.py):
  element e = (k*ny + j)*nx + i,  node n = (k*(ny+1) + j)*(nx+1) + i,
  element centre = origin + h*(i,j,k) + h/2.
"""
import json
import numpy as np
from .geometry import eval_shape, element_bounds, _cyl_r

LABEL = {"design": 0, "solid": 1, "void": 2, "rigid": 3}
PRECEDENCE = ["void", "rigid", "solid"]          # earlier role wins on overlap


class SpecError(ValueError):
    pass


class Problem:
    """Everything the optimiser needs, as plain arrays (see to_npz)."""

    def __init__(self, spec):
        self.spec = spec
        g = spec["grid"]
        self.h = float(g["h"])
        self.origin = np.array(g["origin"], float)
        self.shape = tuple(int(v) for v in g["shape"])      # (nx, ny, nz)
        nx, ny, nz = self.shape
        k, j, i = np.meshgrid(np.arange(nz), np.arange(ny), np.arange(nx), indexing="ij")
        self.ijk = np.c_[i.ravel(), j.ravel(), k.ravel()]
        self.centres = self.origin + self.h * self.ijk + self.h / 2
        NX, NY, NZ = nx + 1, ny + 1, nz + 1
        kk, jj, ii = np.meshgrid(np.arange(NZ), np.arange(NY), np.arange(NX), indexing="ij")
        self.nijk = np.c_[ii.ravel(), jj.ravel(), kk.ravel()]
        self.nodes = self.origin + self.h * self.nijk
        corner = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]])
        I, J, K = self.ijk.T
        self.enodes = np.stack([(K + c[2]) * NY * NX + (J + c[1]) * NX + (I + c[0]) for c in corner], 1)
        self.nn = NX * NY * NZ
        self._regions()
        self._nodes_sets()

    # ---------------------------------------------------------------- regions
    def _regions(self):
        spec = self.spec
        self._check_ties()
        raw = {}
        for r in spec["regions"]:
            raw[r["name"]] = eval_shape(r["shape"], self.centres, closed=False)
        masks = {}
        for r in spec["regions"]:
            m = raw[r["name"]].copy()
            for other in r.get("minus", []):
                m &= ~raw[other]
            masks[r["name"]] = m
        self.region_masks = masks
        role = {r["name"]: r["role"] for r in spec["regions"]}
        lab = np.full(len(self.centres), LABEL["design"], np.int8)
        taken = np.zeros(len(self.centres), bool)
        for rl in PRECEDENCE:
            m = np.zeros(len(self.centres), bool)
            for name, mm in masks.items():
                if role[name] == rl:
                    m |= mm
            m &= ~taken
            lab[m] = LABEL[rl]
            taken |= m
        self.label = lab
        self.design = lab == LABEL["design"]
        self.solid = lab == LABEL["solid"]
        self.void = lab == LABEL["void"]
        self.rigid = lab == LABEL["rigid"]
        self.active = ~self.void
        # per-element stiffness / mass scale for rigid parts (opt3d: post ke=20, mass 0)
        self.k_scale = np.ones(len(lab))
        self.m_scale = np.ones(len(lab))
        for r in spec["regions"]:
            if r["role"] == "rigid":
                m = masks[r["name"]] & self.rigid
                self.k_scale[m] = r.get("stiffness_scale", 20.0)
                self.m_scale[m] = r.get("mass_scale", 0.0)
        used = np.zeros(self.nn, bool)
        used[self.enodes[self.active].ravel()] = True
        self.used = used

    def _check_ties(self):
        """An element-region bound equal to an element centre makes '<' vs '<=' matter -> reject."""
        h, o = self.h, self.origin
        for r in self.spec["regions"]:
            for kind, ax, v, prim in element_bounds(r["shape"]):
                if kind == "plane":
                    t = (v - o[ax] - h / 2) / h
                    if abs(t - round(t)) < 1e-9 and 0 <= round(t) < self.shape[ax]:
                        raise SpecError(f"region '{r['name']}': bound {v} on axis {'xyz'[ax]} hits element centres")
                else:
                    rr = _cyl_r(self.centres, prim)
                    if np.any(np.abs(rr - v) < 1e-9):
                        raise SpecError(f"region '{r['name']}': radius {v} hits element centres")

    # ------------------------------------------------------------- node sets
    def select_nodes(self, sel):
        m = eval_shape(sel, self.nodes, closed=True) if not isinstance(sel, dict) or "union" in sel \
            else eval_shape([sel], self.nodes, closed=True)
        return np.where(m & self.used)[0]

    def _nodes_sets(self):
        spec = self.spec
        sym = spec["grid"].get("symmetry")
        self.sym_axis = None
        if sym:
            ax = "xyz".index(sym["axis"])
            self.sym_axis = ax
            if abs(self.origin[ax] - sym["at"]) > 1e-9:
                raise SpecError("symmetry plane must be the grid's lower face on that axis")
            self.sym_plane = np.where(self.used & (self.nijk[:, ax] == 0))[0]
        self.supports = {}
        for s in spec["supports"]:
            self.supports[s["name"]] = self.select_nodes(s["nodes"])
            if len(self.supports[s["name"]]) == 0:
                raise SpecError(f"support '{s['name']}' selects no nodes")
        # lumped masses on node sets; a half model carries half, plane nodes weighted 0.5
        self.mass_sets = {}
        self.node_mass = np.zeros(self.nn)
        for pm in spec.get("point_masses", []):
            nds = self.select_nodes(pm["nodes"])
            if len(nds) == 0:
                raise SpecError(f"point mass '{pm['name']}' selects no nodes")
            w = np.ones(len(nds))
            share = 1.0
            if self.sym_axis is not None:
                w[self.nijk[nds, self.sym_axis] == 0] = 0.5
                share = 0.5
            m_t = pm["mass_kg"] * 1e-3                       # kg -> t (N, mm, s units)
            mm = m_t * share * w / w.sum()
            self.mass_sets[pm["name"]] = (nds, mm)
            self.node_mass[nds] += mm

    # -------------------------------------------------------------- loads
    def sym_case(self, direction):
        """Half-model BC case for a load along `direction`: S if normal to the plane, A if along it."""
        if self.sym_axis is None:
            return "F"
        d = np.asarray(direction, float)
        along = abs(d[self.sym_axis]) > 1e-12
        perp = np.linalg.norm(np.delete(d, self.sym_axis)) > 1e-12
        if along and perp:
            raise SpecError("inertial load direction must be along or normal to the symmetry plane")
        return "A" if along else "S"

    def load_vector(self, case, elem_density=None):
        """Nodal force vector (3*nn) for an inertial load case on the analysed (half) model.
        self-inertia uses element mass of the given density field (0/1)."""
        g = 9810.0                                   # mm/s^2
        a = case["accel_g"] * g * np.asarray(case["dir"], float)
        F = np.zeros((self.nn, 3))
        for name in case.get("applies_to", []):
            nds, mm = self.mass_sets[name]
            np.add.at(F, nds, mm[:, None] * a[None, :])
        if case.get("include_self", False) and elem_density is not None:
            rho = self.spec["material"]["rho"]
            me = elem_density * self.m_scale * rho * self.h ** 3 * (~self.void)
            np.add.at(F, self.enodes.ravel(), np.repeat(me / 8, 8)[:, None] * a[None, :])
        return F.ravel()

    def initial_density(self):
        """1st design: design-space elements inside the template's initial members (0/1)."""
        init = self.spec.get("initial_design")
        if not init:
            return np.zeros(len(self.label))
        m = eval_shape(init["shape"] if isinstance(init["shape"], dict) else {"union": [[s] for s in init["shape"]]},
                       self.centres, closed=False)
        return (m & self.design).astype(float)

    # -------------------------------------------------------------- export
    def summary(self):
        return dict(grid=dict(h=self.h, origin=self.origin.tolist(), shape=self.shape),
                    elements=dict(design=int(self.design.sum()), solid=int(self.solid.sum()),
                                  void=int(self.void.sum()), rigid=int(self.rigid.sum())),
                    supports={k: int(len(v)) for k, v in self.supports.items()},
                    point_mass_nodes={k: int(len(v[0])) for k, v in self.mass_sets.items()},
                    half_model_mass_kg=round(float(self.node_mass.sum() * 1e3), 4))

    def to_npz(self, path):
        d = dict(h=self.h, origin=self.origin, shape=np.array(self.shape), label=self.label,
                 k_scale=self.k_scale, m_scale=self.m_scale, node_mass=self.node_mass,
                 used_nodes=np.where(self.used)[0])
        for k, v in self.supports.items():
            d["support__" + k] = v
        if self.sym_axis is not None:
            d["sym_plane_nodes"] = self.sym_plane
            d["sym_axis"] = self.sym_axis
        for c in self.spec.get("load_cases", []):
            if c["type"] == "inertial":
                d["load__" + c["name"]] = self.load_vector(c)
                d["loadcase__" + c["name"]] = np.array(self.sym_case(c["dir"]))
        np.savez_compressed(path, **d)


def load_spec(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)
