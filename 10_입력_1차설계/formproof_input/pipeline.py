"""One call from user input (text / sketch / photo) to the 1st design and the hand-off package.
Used by run.py (command line) and app/server.py (GUI)."""
import base64
import io
import json
import os
import time
import zipfile

import numpy as np

from . import requirements, text_rules
from .cad import export_step
from .compile import Problem
from .drawing import make_drawing
from .export import side_preview, write_stl
from .fem import evaluate
from .templates.bike_mount import build_spec
from .templates.library import BY_ID, TEMPLATES

HANDOFF_FILES = ["spec.json", "problem.npz", "initial_design.npy", "design_1st.step", "design_1st_drawing.pdf",
                 "design_1st_drawing.dxf", "design_1st.stl", "report.json"]
_MATCHER = None


def matcher():
    global _MATCHER
    if _MATCHER is None:
        from .sketch import Matcher
        _MATCHER = Matcher(TEMPLATES)
    return _MATCHER


def decode_image(data):
    """data URL / base64 / bytes -> gray float array (alpha composited on white paper)."""
    from PIL import Image
    if isinstance(data, str):
        data = base64.b64decode(data.split(",", 1)[1] if data.startswith("data:") else data)
    im = Image.open(io.BytesIO(data))
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        im = Image.alpha_composite(bg, im)
    g = np.asarray(im.convert("L"), float) / 255.0
    if max(g.shape) > 1200:                               # phone photos: keep matching fast
        k = int(np.ceil(max(g.shape) / 1200))
        g = g[::k, ::k]
    return g


def looks_like_photo(gray):
    """Line drawings are mostly paper + ink; photos have many mid tones."""
    mid = ((gray > 0.2) & (gray < 0.8)).mean()
    return bool(mid > 0.15)


def mesh_payload(body, tol=0.05):
    """CAD body -> non-indexed triangle positions (float32, base64) for the three.js viewer."""
    verts, tris = body.val().tessellate(tol, 0.2)
    v = np.array([[p.x, p.y, p.z] for p in verts], np.float32)
    t = np.array(tris, np.int64)
    pos = v[t].reshape(-1, 3).astype(np.float32)
    return dict(pos=base64.b64encode(pos.tobytes()).decode(), triangles=int(len(t)))


def design(text="", sketch=None, image=None, template=None, out="out", with_mesh=False):
    """sketch / image: gray arrays (0..1) or None. template: force a template id (e.g. user picked a candidate)."""
    t0 = time.time()
    os.makedirs(out, exist_ok=True)
    rep = dict(input=dict(text=text, sketch=sketch is not None, image=image is not None, template=template))
    parsed = text_rules.parse(text)
    rep["text"] = parsed

    match = None
    if sketch is not None or image is not None:
        g = sketch if sketch is not None else image
        photo = image is not None and looks_like_photo(image)
        match = matcher().match_image(g, photo=photo)
        match["source"] = "사진(에지 검출)" if photo else ("스케치" if sketch is not None else "스케치 이미지")
    if template:
        tid, how = template, "후보 선택" if match else "지정"
    elif match:
        tid, how = match["candidates"][0]["id"], f"{match['source']} 매칭"
    else:
        tid, how = text_rules.template_from_hint(parsed["shape_hint"], TEMPLATES), "텍스트"
    tpl = BY_ID[tid]
    rep["template"] = dict(id=tid, name=tpl["name"], desc=tpl["desc"], chosen_by=how, match=match)

    params = dict(tpl["params"])
    params.update(parsed["params"])
    spec = build_spec(params, tid, meta=dict(name=tpl["name"], chosen_by=how))
    P = Problem(spec)
    dens = P.initial_density()
    check = evaluate(P, dens)
    rep["first_design_check"] = check
    rep["handoff_requirements"] = requirements.handoff_summary(spec, P)
    rep["problem"] = P.summary()
    rep["criteria"] = [dict(id=c["id"], rule=f'{c["quantity"]} {c["op"]} {c["value"]}', why=c.get("derivation", ""),
                            source=c.get("source"), requirement=c.get("requirement")) for c in spec["constraints"]]
    rep["assumptions"] = spec["assumptions"]
    g = spec["geometry"]
    rep["design_vars"] = dict(bar_d=g["bar_d"], width=g["width"], reach=g["mount_hole"]["x"], pad_top=g["pad"]["z"][1],
                              arm=g["arm"]["style"], arm_t=g["arm"]["t"], phone=g["phone"]["name"],
                              point_mass_g=round(spec["point_masses"][0]["mass_kg"] * 1e3), material=spec["material"]["name"])

    p = spec["template"]["params"]
    road = next(c for c in spec["load_cases"] if c["type"] == "modal")
    shock = next(c for c in spec["load_cases"] if c["name"] == "shock_vertical")
    sf = p.get("safety_factor") or 1.5
    rep["summary"] = dict(
        product="자전거 폰 거치대", road=("자갈·돌길 (측정값)" if p.get("road") == "cobblestone" and "road" in parsed["params"]
                                    else "기본: 자갈길 기준" if p.get("road") == "cobblestone" else f"{p['road']} → 자갈길 값으로 보수"),
        vib=f"{road['excitation_hz'][0]}–{road['excitation_hz'][1]} Hz", shock_g=shock["accel_g"],
        phone=g["phone"]["name"], point_mass_g=round(spec["point_masses"][0]["mass_kg"] * 1e3), bar_d=g["bar_d"],
        objective="무게 최소" if p.get("objective") == "min_mass" else p.get("objective"), safety_factor=sf,
        material=spec["material"]["name"], requirements=[requirements.LIBRARY[r]["name"] for r in spec.get("requirements", [])])

    with open(os.path.join(out, "spec.json"), "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=1)
    P.to_npz(os.path.join(out, "problem.npz"))
    np.save(os.path.join(out, "initial_design.npy"), dens.astype(np.uint8))
    rep["stl"] = write_stl(P, dens, os.path.join(out, "design_1st.stl"))
    side_preview(P, dens, os.path.join(out, "side_view.png"), f"{tid} {tpl['name']} — 1차 설계 / 설계 영역")
    body, cad_info = export_step(spec, os.path.join(out, "design_1st.step"))
    rep["cad"] = dict(step="design_1st.step", **cad_info)
    rep["drawing"] = make_drawing(spec, body, os.path.join(out, "design_1st_drawing.dxf"),
                                  os.path.join(out, "design_1st_drawing.pdf"), title="자전거 폰 거치대 — 1차 설계",
                                  check=check, mass_g=cad_info["mass_g"])
    rep["seconds"] = round(time.time() - t0, 2)
    with open(os.path.join(out, "report.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)
    with zipfile.ZipFile(os.path.join(out, "handoff.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for name in HANDOFF_FILES:
            z.write(os.path.join(out, name), name)
    if with_mesh:
        rep["mesh"] = mesh_payload(body)
        rep["phone"] = g["phone"]
        rep["geometry"] = dict(y_sym=g["y_sym"], pad=g["pad"], bar_d=g["bar_d"], ring_ro=g["ring_ro"])
    return rep
