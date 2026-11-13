"""1st design as exact B-rep CAD (CadQuery / OpenCascade), built from spec["geometry"].

The same snapped dimensions drive the analysis grid, so CAD and voxel model describe one design.
Frame: x forward, y = handlebar axis, z up, handlebar centre at (x=0, z=0)."""
import math
import cadquery as cq

# CadQuery "XZ" plane: local x = global X, local y = global Z, normal = -Y
def _xz(y):
    return cq.Workplane(cq.Plane(origin=(0, y, 0), xDir=(1, 0, 0), normal=(0, -1, 0)))


def build_solid(spec, holes=True, clip=True):
    g = spec["geometry"]
    y0, w = g["y_sym"], g["width"]
    half = w / 2
    ring = _xz(y0).circle(g["ring_ro"]).extrude(half, both=True)
    ex0, ex1 = g["ear_x"]
    ez0, ez1 = g["ear_z"]
    ears = None
    for sgn in (1, -1):
        xa, xb = sorted((sgn * ex0, sgn * ex1))
        e = _xz(y0).center((xa + xb) / 2, (ez0 + ez1) / 2).rect(xb - xa, ez1 - ez0).extrude(half, both=True)
        ears = e if ears is None else ears.union(e)
    (px0, px1), (pz0, pz1) = g["pad"]["x"], g["pad"]["z"]
    pad = _xz(y0).center((px0 + px1) / 2, (pz0 + pz1) / 2).rect(px1 - px0, pz1 - pz0).extrude(half, both=True)

    t = g["arm"]["t"]
    arms = None
    for (x0, z0), (x1, z1) in g["arm"]["segments"]:
        L = math.hypot(x1 - x0, z1 - z0)
        ang = math.degrees(math.atan2(z1 - z0, x1 - x0))
        a = _xz(y0).center((x0 + x1) / 2, (z0 + z1) / 2).slot2D(L + t, t, ang).extrude(half, both=True)
        arms = a if arms is None else arms.union(a)
    if clip:   # arms stay inside the design space used by the analysis (no bump into the phone space)
        c = g["clip"]
        big = 1000.0
        holder = cq.Workplane("XY").box(big, w + 2, big, centered=(False, True, False)) \
            .translate((c["holder_x"], y0, c["holder_z"]))
        above = cq.Workplane("XY").box(2 * big, w + 2, big, centered=(True, True, False)).translate((0, y0, c["z_above"]))
        arms = arms.cut(holder).cut(above)

    body = ring.union(ears).union(pad).union(arms)
    # cut: handlebar bore, clamp slit
    bore = _xz(y0).circle(g["bore_r"]).extrude(half + 1, both=True)
    slit = _xz(y0).center(0, -g["slit_r"] / 2).rect(2 * g["slit_half"], g["slit_r"]).extrude(half + 1, both=True)
    body = body.cut(bore).cut(slit)
    if holes:
        b = g["bolts"]
        xa, xb = b["x_span"]
        for yb in b["y"]:
            hole = cq.Workplane("YZ", origin=(xa, yb, b["z"])).circle(b["d"] / 2).extrude(xb - xa)
            body = body.cut(hole)
        m = g["mount_hole"]
        mh = cq.Workplane("XY", origin=(m["x"], m["y"], pz0 - 1)).circle(m["d"] / 2).extrude(pz1 - pz0 + 2)
        body = body.cut(mh)
    return body


def solid_info(body, rho_t_mm3):
    s = body.val()
    bb = s.BoundingBox()
    return dict(valid=bool(s.isValid()), solids=len(body.solids().vals()),
                volume_mm3=round(s.Volume(), 1), mass_g=round(s.Volume() * rho_t_mm3 * 1e6, 2),
                bbox=[[round(bb.xmin, 2), round(bb.ymin, 2), round(bb.zmin, 2)],
                      [round(bb.xmax, 2), round(bb.ymax, 2), round(bb.zmax, 2)]])


def export_step(spec, path, holes=True):
    body = build_solid(spec, holes=holes)
    cq.exporters.export(body, path, exportType="STEP")
    return body, solid_info(body, spec["material"]["rho"])
