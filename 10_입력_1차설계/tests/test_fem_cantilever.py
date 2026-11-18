"""Whole-chain check (spec -> Problem -> half-model FEM): a voxel cantilever with a tip mass
against Euler-Bernoulli. Checks units, supports, symmetry handling, lumped mass and load vectors."""
import os, sys, math
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from formproof_input.compile import Problem
from formproof_input.fem import evaluate

E, NU, RHO = 1700.0, 0.38, 1.27e-9
L, B, T, M_TIP, G = 100.0, 20.0, 10.0, 0.25, 48.5


def cantilever_spec(h=2.0):
    y0 = 55.0
    box = lambda **kw: {"box": kw}
    return {
        "grid": {"h": h, "origin": [0.0, y0, -T / 2], "shape": [int(L / h), int(B / 2 / h), int(T / h)],
                 "symmetry": {"axis": "y", "at": y0, "cases": ["S", "A"]}},
        "material": dict(name="PETG", E=E, nu=NU, rho=RHO, yield_mpa=39, interlayer_mpa=16.4),
        "regions": [dict(name="beam", role="solid", shape=[box(x=[0.0, L])])],
        "supports": [dict(name="wall", nodes=[box(x=[None, 0.0])])],
        "point_masses": [dict(name="tip", mass_kg=M_TIP, nodes=[box(x=[L, None])])],
        "load_cases": [{"name": "shock_vertical", "type": "inertial", "accel_g": G, "dir": [0, 0, -1],
                        "applies_to": ["tip"]}],
        "constraints": [],
    }


def analytic():
    I = B * T ** 3 / 12
    m_beam = RHO * B * T * L
    m = M_TIP * 1e-3 + 0.2357 * m_beam                             # t (tip mass + Rayleigh beam share)
    f = math.sqrt(3 * E * I / (L ** 3 * m)) / (2 * math.pi)
    F = M_TIP * 1e-3 * G * 9810.0
    d = F * L ** 3 / (3 * E * I)
    return f, d


def test_cantilever():
    f_a, d_a = analytic()
    P = Problem(cantilever_spec())
    r = evaluate(P, np.zeros(len(P.label)))
    f_fe = r["f1_hz"]
    d_fe = r["shock_vertical"]["tip_disp_mm"]
    e_f, e_d = f_fe / f_a - 1, d_fe / d_a - 1
    assert r["connected"]
    assert abs(e_f) < 0.05 and abs(e_d) < 0.10, (f_fe, f_a, d_fe, d_a)
    return dict(f_fe=f_fe, f_beam=round(f_a, 2), err_f=f"{e_f:+.1%}", d_fe=d_fe, d_beam=round(d_a, 3), err_d=f"{e_d:+.1%}")


if __name__ == "__main__":
    print("cantilever:", test_cantilever())
