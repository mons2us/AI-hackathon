"""1st-design CAD: exact B-rep from the spec geometry, consistent with the analysed voxel model and the drawing."""
import os, sys, tempfile
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from formproof_input.compile import Problem
from formproof_input.templates.bike_mount import build_spec
from formproof_input.templates.library import TEMPLATES
from formproof_input.cad import build_solid, export_step, solid_info


def test_step_all_templates():
    import cadquery as cq
    out = []
    with tempfile.TemporaryDirectory() as d:
        for t in TEMPLATES:
            s = build_spec(t["params"], t["id"])
            body, info = export_step(s, os.path.join(d, t["id"] + ".step"))
            assert info["valid"] and info["solids"] == 1, (t["id"], info)
            back = cq.importers.importStep(os.path.join(d, t["id"] + ".step"))
            assert abs(back.val().Volume() / info["volume_mm3"] - 1) < 1e-4, t["id"]    # STEP round trip
            # analysed voxel model vs CAD without holes (holes are not in the analysis)
            P = Problem(s)
            on = P.solid | (P.design & (P.initial_density() > 0.5))
            vox_g = 2 * on.sum() * P.h ** 3 * s["material"]["rho"] * 1e6
            cad_g = solid_info(build_solid(s, holes=False, with_holder=False), s["material"]["rho"])["mass_g"]
            assert abs(cad_g / vox_g - 1) < 0.05, (t["id"], cad_g, vox_g)
            out.append(f"{t['id']} {cad_g:.1f}/{vox_g:.1f} g")
    return out


def test_drawing_dimensions():
    """Every dimension written in the DXF equals the spec geometry (true size, any sheet scale)."""
    import ezdxf
    from formproof_input.drawing import make_drawing
    res = []
    with tempfile.TemporaryDirectory() as d:
        for tid in ("T01", "T05", "T08"):
            t = next(x for x in TEMPLATES if x["id"] == tid)
            s = build_spec(t["params"], tid)
            g = s["geometry"]
            body, info = export_step(s, os.path.join(d, "a.step"))
            r = make_drawing(s, body, os.path.join(d, "a.dxf"))
            doc = ezdxf.readfile(os.path.join(d, "a.dxf"))
            lfac = doc.dimstyles.get("KRDIM").dxf.dimlfac
            got = sorted(round(e.get_measurement() * lfac, 1) for e in doc.modelspace().query("DIMENSION"))
            (x0, y0, z0), (x1, y1, z1) = info["bbox"]
            want = sorted(round(v, 1) for v in (x1 - x0, g["mount_hole"]["x"], g["pad"]["z"][1], z1 - z0,
                                                 g["pad"]["x"][1] - g["pad"]["x"][0], g["width"],
                                                 g["bolts"]["y"][1] - g["bolts"]["y"][0]))
            assert got == want, (tid, got, want)
            res.append(f"{tid} {r['sheet']} {r['scale']} dims {got}")
    return res


if __name__ == "__main__":
    print("\n".join(test_step_all_templates()))
    print("\n".join(test_drawing_dimensions()))
