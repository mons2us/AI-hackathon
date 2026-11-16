"""One call from user input (text / sketch / photo) to the 1st design and the hand-off package.
Used by run.py (command line) and app/server.py (GUI)."""
import base64
import math
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
from .templates.library import ALL, BY_ID, LOOKS, TEMPLATES

HANDOFF_FILES = ["spec.json", "problem.npz", "initial_design.npy", "design_1st.step", "design_1st_drawing.pdf",
                 "design_1st_drawing.dxf", "design_1st.stl", "report.json"]
_MATCHER = None


def matcher():
    global _MATCHER
    if _MATCHER is None:
        from . import skeleton_db
        from .sketch import Matcher
        _MATCHER = Matcher(ALL, refs=skeleton_db.load(ALL))      # stored skeleton DB if it matches the library
    return _MATCHER


WORD_WEIGHT = 0.6     # sketch score units per mismatched look word (holder / clamp / section / joint / arm)


def rerank_with_words(match, hint, k=5):
    """Sketch candidates re-ranked with the look words of the text (the side view hardly shows holder / clamp type).
    T templates have no look: they count as mismatching every look word."""
    cands = match["candidates"]
    if hint:
        for c in cands:
            L = BY_ID[c["id"]].get("look")
            pen = text_rules.look_penalty(hint, L) if L else sum(1.5 if key == "arm" else 1.0 for key in hint)
            c["word_penalty"] = round(WORD_WEIGHT * pen, 3)
        cands.sort(key=lambda c: c["score"] + c["word_penalty"])
        s0 = cands[0]["score"] + cands[0]["word_penalty"]
        for c in cands:
            c["confidence"] = round(math.exp(-(c["score"] + c["word_penalty"] - s0) / 0.5), 3)
        match["words"] = hint
    match["candidates"] = cands[:k]
    return match


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


def payload_summary(spec, cad_info=None):
    """What the mount carries (team v3) and whether the drawn phone holder fits its mass allowance."""
    pm = spec["point_masses"][0]
    out = dict(model=pm.get("model", "point"), total_g=round(pm["mass_kg"] * 1e3, 1), note=pm.get("note", ""))
    if pm.get("model") == "rigid_body":
        out.update(cg=pm["cg"], box_mm=pm["box_mm"], phone_case_g=round(pm["parts"]["phone_case_kg"] * 1e3, 1),
                   holder_allow_g=round(pm["parts"]["holder_kg"] * 1e3, 1))
        if spec["geometry"].get("look"):
            h = round(pm["parts"]["holder_kg"] * 1e3, 1)
            out.update(holder_cad_g=h, holder_within=True, holder_from_cad=True,
                       holder_note=f"폰 홀더·관절 {h:.1f} g — CAD에서 바로 계산해 탑재 하중(무게중심·회전 관성)에 반영")
        elif cad_info and "holder_mass_g" in cad_info:
            h = cad_info["holder_mass_g"]
            out.update(holder_cad_g=h, holder_within=bool(h <= out["holder_allow_g"]),
                       holder_note=(f"그린 폰 홀더 {h:.1f} g ≤ 여유 {out['holder_allow_g']:.0f} g" if h <= out["holder_allow_g"]
                                    else f"그린 폰 홀더 {h:.1f} g > 여유 {out['holder_allow_g']:.0f} g → 탑재 하중을 늘려 다시 판정 필요"))
    return out


def design(text="", sketch=None, image=None, template=None, out="out", with_mesh=False):
    """sketch / image: gray arrays (0..1) or None. template: force a template id (e.g. user picked a candidate)."""
    t0 = time.time()
    os.makedirs(out, exist_ok=True)
    rep = dict(input=dict(text=text, sketch=sketch is not None, image=image is not None, template=template))
    # P01 일체형 (발표 사례): 지정 · 발표 문장 · 발표 입력 스케치(데모 DB) -> 팀 엔진과 같은 문제
    from . import integral
    g0 = sketch if sketch is not None else image
    via = ("지정" if template == "P01" else
           "발표 입력 스케치 (데모 DB)" if (not template and g0 is not None and integral.matches_presentation_sketch(g0)) else
           "텍스트 (발표 문장 · 일체형)" if (not template and g0 is None and integral.is_presentation_text(text)) else None)
    if via:
        return integral.design(text, out=out, with_mesh=with_mesh, chosen_by=via,
                               sketch_note=integral.SKETCH_NOTE if (g0 is not None or not text) else "")
    parsed = text_rules.parse(text)
    rep["text"] = parsed

    match = None
    if sketch is not None or image is not None:
        g = sketch if sketch is not None else image
        photo = image is not None and looks_like_photo(image)
        match = matcher().match_image(g, photo=photo, k=len(ALL))
        match["source"] = "사진(에지 검출)" if photo else ("스케치" if sketch is not None else "스케치 이미지")
        match = rerank_with_words(match, parsed.get("look_hint") or {})
    if template:
        tid, how = template, "후보 선택" if match else "지정"
    elif match:
        tid, how = match["candidates"][0]["id"], f"{match['source']} 매칭"
    elif parsed.get("look_hint"):
        tid, how = text_rules.look_from_hint(parsed["look_hint"], LOOKS), "텍스트(외형 단어)"
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
    if g.get("look"):
        from . import look as LK
        L = g["look"]
        rep["design_vars"]["look"] = dict(
            clamp=LK.CLAMP_SPEC[L["clamp"]]["name"], arm=LK.ARMS[L["arm"]], section=LK.SECTIONS[L["section"]],
            joint=LK.JOINTS[L["joint"]], holder=LK.HOLDER_SPEC[L["holder"]]["name"], tilt_deg=L["tilt_deg"],
            clearance=L["clearance_mm"], codes={k: L[k] for k in ("clamp", "arm", "section", "joint", "holder")})
    rep["template"]["look"] = tpl.get("look")

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
    rep["payload"] = payload_summary(spec, cad_info)
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
        rep["phone"] = dict(g["phone"], **({"pose": dict(center=g["look"]["phone_center"], tilt_deg=g["look"]["tilt_deg"])}
                                            if g.get("look") else {}))
        rep["geometry"] = dict(y_sym=g["y_sym"], pad=g["pad"], bar_d=g["bar_d"], ring_ro=g["ring_ro"])
    return rep
