"""Build the browser-only version of the input-stage GUI (claude.ai Artifact / any static host).

Everything that needs CadQuery / OpenCascade / scipy is computed here, ahead of time, for every
template x handlebar diameter. The page then does the rest in the browser:
text rules, sketch / image matching (same algorithm as formproof_input.sketch), spec assembly for the
chosen phone / safety factor / requirements, the 1st-design check (from the precomputed FEM runs),
3D view, drawing and the hand-off zip.

  python app/artifact/build.py            -> app/artifact/dist/  (index.html + data/ + ex/)

What is precomputed per geometry (template, bar_d):
  base spec, CAD mesh, STEP, drawing (DXF + vector primitives, title block filled in the page),
  initial_design.npy, side-view label raster, FEM of the 1st design for each phone mass,
  keep-out space (free_angle requirement) for each phone size.
"""
import base64
import copy
import gzip
import io
import json
import os
import re
import shutil
import sys
import tempfile
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)

from formproof_input import drawing, evidence as ev, requirements, text_rules  # noqa: E402
from formproof_input.cad import export_step  # noqa: E402
from formproof_input.compile import Problem  # noqa: E402
from formproof_input.fem import evaluate  # noqa: E402
from formproof_input.sketch import Matcher  # noqa: E402
from formproof_input.templates.bike_mount import DEFAULT, build_spec  # noqa: E402
from formproof_input.templates.library import TEMPLATES  # noqa: E402

BARS = [22.2, 25.4, 28.6, 31.8, 35.0]
PHONE_KEYS = ["default", "galaxy_s25", "galaxy_s25_plus", "galaxy_s25_ultra"]
DIST = os.path.join(HERE, "dist")
DATA = os.path.join(DIST, "data")
TITLE_TOP = drawing.MARGIN + drawing.TITLE_H


def b64gz(b):
    if isinstance(b, str):
        b = b.encode("utf-8")
    return base64.b64encode(gzip.compress(b, 9, mtime=0)).decode()


def key(tid, bar):
    return f"{tid}_{bar:.1f}"


# ------------------------------------------------------------------ drawing: placeholders + vector primitives
class _TitleSheet(drawing.Sheet):
    """Title-block texts become @@Tnn@@ placeholders; the page writes them for the actual conditions."""
    counter = 0

    def text(self, s, pos, h=2.5, align=drawing.TextEntityAlignment.LEFT, layer="TEXT"):
        if pos[1] < TITLE_TOP:
            s = f"@@T{_TitleSheet.counter:02d}@@"
            _TitleSheet.counter += 1
        super().text(s, pos, h, align, layer)


def _text_prim(e, layer):
    t = e.dxftype()
    if t == "TEXT":
        ha, va = e.dxf.get("halign", 0), e.dxf.get("valign", 0)
        p = e.dxf.align_point if (ha or va) and e.dxf.hasattr("align_point") else e.dxf.insert
        return dict(k="tx", l=layer, s=e.dxf.text, x=round(p[0], 3), y=round(p[1], 3), h=e.dxf.height,
                    ha=int(ha), va=int(va), r=round(e.dxf.get("rotation", 0.0), 2))
    # MTEXT (dimension text): attachment 1..9 = top/middle/bottom x left/center/right
    ap = e.dxf.get("attachment_point", 1)
    ha = (ap - 1) % 3
    va = {0: 3, 1: 2, 2: 1}[(ap - 1) // 3]
    p = e.dxf.insert
    return dict(k="tx", l=layer, s=e.plain_text(), x=round(p[0], 3), y=round(p[1], 3), h=e.dxf.char_height,
                ha=ha, va=va, r=round(e.dxf.get("rotation", 0.0), 2))


def _prims(entities, layer=None, out=None):
    out = [] if out is None else out
    for e in entities:
        t = e.dxftype()
        lay = layer or e.dxf.layer
        if t == "LWPOLYLINE":
            pts = [(round(x, 3), round(y, 3)) for x, y, *_ in e.get_points()]
            out.append(dict(k="pl", l=lay, p=pts, c=bool(e.closed)))
        elif t == "LINE":
            out.append(dict(k="pl", l=lay, p=[(round(e.dxf.start[0], 3), round(e.dxf.start[1], 3)),
                                               (round(e.dxf.end[0], 3), round(e.dxf.end[1], 3))], c=False))
        elif t in ("SOLID", "TRACE"):
            v = [e.dxf.vtx0, e.dxf.vtx1, e.dxf.vtx3, e.dxf.vtx2]
            pts = []
            for q in v:
                q = (round(q[0], 3), round(q[1], 3))
                if q not in pts:
                    pts.append(q)
            out.append(dict(k="so", l=lay, p=pts))
        elif t in ("TEXT", "MTEXT"):
            out.append(_text_prim(e, lay))
        elif t in ("DIMENSION", "INSERT"):
            _prims(e.virtual_entities(), "DIM" if t == "DIMENSION" else lay, out)
    return out


def make_drawing_assets(spec, body, tmp):
    _TitleSheet.counter = 0
    real = drawing.Sheet
    drawing.Sheet = _TitleSheet
    try:
        dummy = {"pass": False, "f1_hz": 0.0, "checks": {"stress": {"value": 0.0}}}
        path = os.path.join(tmp, "d.dxf")
        meta = drawing.make_drawing(spec, body, path, None, title="자전거 폰 거치대 — 1차 설계", check=dummy, mass_g=1.0)
    finally:
        drawing.Sheet = real
    import ezdxf
    doc = ezdxf.readfile(path)
    prims = _prims(doc.modelspace())
    W, H = drawing.A4 if meta["sheet"] == "A4" else drawing.A3
    with open(path, "rb") as f:
        dxf = f.read()
    return dict(sheet=meta["sheet"], scale=meta["scale"], W=W, H=H, prims=prims, n_title=_TitleSheet.counter), dxf


# ------------------------------------------------------------------ per geometry
def side_raster(P, dens):
    nx, ny, nz = P.shape
    lab = P.label.reshape(nz, ny, nx)
    first = (P.design & (dens > 0.5)).reshape(nz, ny, nx).any(1)
    img = np.zeros((nz, nx), np.uint8)
    img[(lab == 0).any(1)] = 1
    img[first] = 2
    img[(lab == 1).any(1)] = 3
    img[(lab == 3).any(1)] = 4
    sup = P.supports[next(iter(P.supports))]
    pts = np.unique(np.round(P.nodes[sup][:, [0, 2]], 2), axis=0)
    return dict(nx=nx, nz=nz, h=P.h, origin=[float(P.origin[0]), float(P.origin[2])],
                cells="".join(map(str, img[::-1].ravel())), supports=pts.tolist())


def fem_entry(P, dens, fields=False):
    r = evaluate(P, dens, fields=fields)
    r.pop("checks", None)
    r.pop("pass", None)
    return r


def pack_fields(P, raw):
    """Per-element heat-map fields as uint8 (0 = no material, 1..255 = value / max), element order k, j, i."""
    out = dict(shape=list(P.shape), h=P.h, origin=[float(v) for v in P.origin], cases={})
    for name, f in raw.items():
        d = {}
        for q in ("vm", "disp"):
            v = f[q]
            mask = f["on"] & ~P.rigid if q == "vm" else f["on"]
            top = float(v[f["judged"]].max()) if q == "vm" else float(v[mask].max())
            u8 = np.where(mask, np.clip(np.ceil(v / top * 254), 0, 254) + 1, 0).astype(np.uint8)
            d[q] = dict(max=round(top, 4), data=b64gz(u8.tobytes()))
        out["cases"][name] = d
    return out


def build_geometry(tpl, bar, tmp):
    params = dict(tpl["params"], bar_d=bar)
    spec = build_spec(params, tpl["id"], meta=dict(name=tpl["name"], chosen_by=""))
    P = Problem(spec)
    dens = P.initial_density()
    out = dict(key=key(tpl["id"], bar), template=tpl["id"], bar_d=bar, spec=spec, problem=P.summary(),
               side=side_raster(P, dens))
    buf = io.BytesIO()
    np.save(buf, dens.astype(np.uint8))
    out["npy"] = b64gz(buf.getvalue())

    fem, keep = {}, {}
    for pk in PHONE_KEYS:
        sp = build_spec(dict(params, phone=pk), tpl["id"])
        Pk = Problem(sp)
        fe = fem_entry(Pk, dens, fields=pk == "default")
        if pk == "default":                     # fields scale with the point mass (inertial load on the phone only)
            out["fields"] = pack_fields(Pk, fe.pop("fields"))
        fem[pk] = dict(mass_kg=sp["point_masses"][0]["mass_kg"], half_model_mass_kg=Pk.summary()["half_model_mass_kg"], **fe)
        sk = build_spec(dict(params, phone=pk, requirements=["free_angle"]), tpl["id"])
        Pq = Problem(sk)
        ko = Pq.keepout
        nx, ny, nz = Pq.shape
        proj = ko.reshape(nz, ny, nx).any(1)[::-1]
        keep[pk] = dict(elements=int(ko.sum()), clash=int((ko & (Pq.solid | Pq.rigid)).sum()),
                        xz="".join("1" if v else "0" for v in proj.ravel()))
    out["fem"], out["keepout"] = fem, keep

    out["cad"] = {}
    for pk in PHONE_KEYS:                       # the holder is sized to the phone -> CAD, mesh, drawing per phone
        sp = build_spec(dict(params, phone=pk), tpl["id"], meta=dict(name=tpl["name"], chosen_by=""))
        step_path = os.path.join(tmp, "d.step")
        body, cad_info = export_step(sp, step_path)
        c = dict(info=dict(step="design_1st.step", **cad_info), holder=sp["geometry"]["holder"])
        with open(step_path, "rb") as f:
            c["step"] = b64gz(f.read())
        verts, tris = body.val().tessellate(0.06, 0.15)
        v = np.array([[p.x, p.y, p.z] for p in verts], np.float32)
        t = np.array(tris, np.uint32)
        c["mesh"] = dict(nv=len(v), nt=len(t), data=b64gz(v.tobytes() + t.tobytes()))
        dmeta, dxf = make_drawing_assets(sp, body, tmp)
        c["drawing"] = dmeta
        c["dxf"] = b64gz(dxf)
        out["cad"][pk] = c
    return out


# ------------------------------------------------------------------ shared tables
def _jsre(rx):
    """Python regex -> JS source (the patterns used here are in the common subset)."""
    return rx


def shared_tables(matcher):
    refs = {}
    for frame in ("ring", "bbox"):
        refs[frame] = [dict(t=r["t"], phone=r["phone"],
                            bits=base64.b64encode(np.packbits(r["img"].ravel() > 0.5).tobytes()).decode())
                       for r in matcher.refs[frame]]
    return dict(
        version=time.strftime("%Y-%m-%d"),
        bars=BARS, phone_keys=PHONE_KEYS,
        templates=[dict(id=t["id"], name=t["name"], desc=t["desc"], params=t["params"]) for t in TEMPLATES],
        default=DEFAULT,
        ev=dict(SOURCES=ev.SOURCES, MATERIALS=ev.MATERIALS, ROADS=ev.ROADS, ROAD_FALLBACK=ev.ROAD_FALLBACK,
                PHONES=ev.PHONES, PHONE_DEFAULT_DIMS=ev.PHONE_DEFAULT_DIMS, PHONE_DEFAULT_MASS=ev.PHONE_DEFAULT_MASS,
                PHONE_CLAMP_MASS=ev.PHONE_CLAMP_MASS, HANDLEBAR_D=ev.HANDLEBAR_D, FACTORS=ev.FACTORS, SUN=ev.SUN,
                ABSORPTANCE_SOURCE=ev.ABSORPTANCE_SOURCE),
        rules=[dict(id=r[0], rx=_jsre(r[1]), effect=r[2], why=r[3]) for r in text_rules.RULES],
        shape_hints=[dict(id=h[0], rx=_jsre(h[1]), effect=h[2]) for h in text_rules.SHAPE_HINTS],
        requirements={k: dict(v, triggers=_jsre(v["triggers"])) for k, v in requirements.LIBRARY.items()},
        matcher=dict(W=128, H=96, C0=[26.0, 40.0], R_PX=8.0, PAD=6, ring_min=Matcher.RING_MIN_SCORE,
                     rotations=list(Matcher.ROTATIONS), w_hist=matcher.w_hist, refs=refs),
    )


def main():
    t0 = time.time()
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(os.path.join(DATA, "geo"))
    matcher = Matcher(TEMPLATES)
    with open(os.path.join(DATA, "tables.json"), "w", encoding="utf-8") as f:
        json.dump(shared_tables(matcher), f, ensure_ascii=False, separators=(",", ":"))
    with tempfile.TemporaryDirectory() as tmp:
        for tpl in TEMPLATES:
            for bar in BARS:
                g = build_geometry(tpl, bar, tmp)
                with open(os.path.join(DATA, "geo", g["key"] + ".json"), "w", encoding="utf-8") as f:
                    json.dump(g, f, ensure_ascii=False, separators=(",", ":"))
                c = g["cad"]["default"]
                print(f"{g['key']}: {c['info']['mass_g']} g (holder {c['info']['holder_mass_g']}), f1 {g['fem']['default']['f1_hz']} Hz, "
                      f"{c['drawing']['sheet']} {c['drawing']['scale']}  ({time.time() - t0:.0f}s)", flush=True)
    ex = os.path.join(DIST, "ex")
    os.makedirs(ex)
    for t in TEMPLATES:
        shutil.copy(os.path.join(ROOT, "examples", "templates", t["id"] + ".png"), os.path.join(ex, t["id"] + ".png"))
        shutil.copy(os.path.join(ROOT, "examples", "hand", f"hand_{t['id']}.png"), os.path.join(ex, f"hand_{t['id']}.png"))
    assemble()
    print(f"done in {time.time() - t0:.0f}s -> {DIST}")


def assemble():
    """index.html = src/page.html with src/engine.js and src/app.js inlined."""
    src = os.path.join(HERE, "src")
    with open(os.path.join(src, "page.html"), encoding="utf-8") as f:
        page = f.read()
    for name in ("engine.js", "app.js"):
        with open(os.path.join(src, name), encoding="utf-8") as f:
            page = page.replace(f"/*@@{name}@@*/", f.read())
    with open(os.path.join(DIST, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)


if __name__ == "__main__":
    if sys.argv[1:] == ["--assemble"]:
        assemble()
    else:
        main()
