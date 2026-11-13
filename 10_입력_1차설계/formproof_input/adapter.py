"""Bridge to the team's optimisers: build the variables opt3d.py defines in its header from a spec,
so the header can be replaced by `globals().update(opt3d_namespace("spec.json"))`.

Names follow opt3d.py: x0,y0,z0,nx,ny,nz,h,E,nu,rho,MP, design,solid,void,post,active,
ei,I,J,K,xc,yc,zc, NX,NY,NZ,nid,en,edof,nn,gi,gj,gk,nxc,nyc,nzc,used, fixn,plane,topn,tipm, FT.
Equality with the hard-coded opt3d.py header is asserted in tests/test_reproduce_opt3d.py."""
import json
import numpy as np
from .compile import Problem


def opt3d_namespace(spec_or_path):
    spec = spec_or_path
    if isinstance(spec_or_path, str):
        with open(spec_or_path, encoding="utf-8") as f:
            spec = json.load(f)
    P = Problem(spec)
    nx, ny, nz = P.shape
    I, J, K = P.ijk.T
    xc, yc, zc = P.centres.T
    NX, NY, NZ = nx + 1, ny + 1, nz + 1
    gi, gj, gk = P.nijk.T
    nxc, nyc, nzc = P.nodes.T
    en = P.enodes
    edof = np.stack([3 * en, 3 * en + 1, 3 * en + 2], 2).reshape(len(en), 24)
    (pm_name, (topn, _)), = P.mass_sets.items()
    mat = spec["material"]
    f_min = next(c["value"] for c in spec["constraints"] if c["id"] == "f1")
    return dict(
        P=P, spec=spec, x0=P.origin[0], y0=P.origin[1], z0=P.origin[2], nx=nx, ny=ny, nz=nz, h=P.h,
        E=mat["E"], nu=mat["nu"], rho=mat["rho"], MP=spec["point_masses"][0]["mass_kg"] * 1e-3, FT=f_min,
        LT=(2 * np.pi * f_min) ** 2,
        design=P.design, solid=P.solid, void=P.void, post=P.rigid, active=P.active,
        ei=P.ijk, I=I, J=J, K=K, xc=xc, yc=yc, zc=zc, NX=NX, NY=NY, NZ=NZ,
        nid=lambda i, j, k: (k * NY + j) * NX + i, en=en, edof=edof, nn=P.nn,
        gi=gi, gj=gj, gk=gk, nxc=nxc, nyc=nyc, nzc=nzc, used=P.used,
        fixn=P.supports[next(iter(P.supports))], plane=P.sym_plane, topn=topn, tipm=P.node_mass,
        keepout=P.keepout if P.keepout is not None else np.zeros(len(P.label), bool),
    )
