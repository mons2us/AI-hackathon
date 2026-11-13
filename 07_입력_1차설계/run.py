"""FormProof input stage, end to end (offline, CPU only).

  python run.py --text "자갈길에서도 안 흔들리게, 최대한 가볍게, S25 울트라" --sketch my_sketch.png --out out/
  python run.py --text "..." --template T03 --out out/

Writes to --out:
  spec.json            design spec (geometry roles, material, loads, supports, criteria, evidence, assumptions)
  problem.npz          voxel problem for the physics stage (labels, supports, symmetry, masses, load vectors)
  initial_design.npy   1st design density (0/1 per element, half model)
  design_1st.step      1st design as exact CAD solid (B-rep, editable in any CAD tool)
  design_1st_drawing.dxf/.pdf/.png  2-D drawing: third-angle views + isometric, dimensions, title block
  design_1st.stl       1st design, full model (mirrored), for viewing / printing
  side_view.png        side view: design space, kept parts, 1st design, supports
  report.json          input interpretation, template candidates, 1st-design check against the criteria
"""
import argparse
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from formproof_input import requirements, text_rules, thermal
from formproof_input.compile import Problem
from formproof_input.export import side_preview, write_stl
from formproof_input.fem import evaluate
from formproof_input.cad import export_step
from formproof_input.drawing import make_drawing
from formproof_input.templates.bike_mount import build_spec
from formproof_input.templates.library import BY_ID, TEMPLATES


def read_image(path):
    from skimage import io
    return io.imread(path, as_gray=True)


def run(text="", sketch=None, photo=None, template=None, out="out", evaluate_1st=True):
    t0 = time.time()
    os.makedirs(out, exist_ok=True)
    report = dict(input=dict(text=text, sketch=sketch, photo=photo, template=template))
    parsed = text_rules.parse(text)
    report["text"] = parsed

    if template:
        tid, how, cands = template, "지정", None
    elif sketch or photo:
        from formproof_input.sketch import Matcher
        m = Matcher(TEMPLATES).match_image(read_image(sketch or photo), photo=bool(photo))
        tid, how, cands = m["candidates"][0]["id"], f"스케치 매칭({m['frame']} 기준)", m
    else:
        tid, how, cands = text_rules.template_from_hint(parsed["shape_hint"], TEMPLATES), "텍스트 힌트", None
    tpl = BY_ID[tid]
    report["template"] = dict(id=tid, name=tpl["name"], desc=tpl["desc"], chosen_by=how, match=cands)

    params = dict(tpl["params"])
    params.update(parsed["params"])
    reqs = params.get("requirements", [])
    report["requirements"] = {}

    # requirement-driven adaptation of the 1st design (before anything is written)
    if "free_angle" in reqs:
        params, table = requirements.adapt_free_angle(params, tid)
        report["requirements"]["free_angle_options"] = table
    spec = build_spec(params, tid, meta=dict(name=tpl["name"], chosen_by=how))
    P = Problem(spec)
    dens = P.initial_density()
    check = evaluate(P, dens) if (evaluate_1st or reqs) else None
    if "sun_heat" in reqs:
        th = thermal.check(spec, check)
        if not th["pass_"] and th["rows"][1]["parked_ok"] and params.get("colour", "black") != "white":
            report["requirements"]["sun_heat_before"] = th                  # black fails -> print white
            params["colour"] = "white"
            spec = build_spec(params, tid, meta=dict(name=tpl["name"], chosen_by=how))
            P = Problem(spec)
            dens = P.initial_density()
    report["requirements"].update(requirements.run_checks(spec, P, dens, check) if reqs else {})

    with open(os.path.join(out, "spec.json"), "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=1)
    P.to_npz(os.path.join(out, "problem.npz"))
    np.save(os.path.join(out, "initial_design.npy"), dens.astype(np.uint8))
    report["problem"] = P.summary()
    report["stl"] = write_stl(P, dens, os.path.join(out, "design_1st.stl"))
    side_preview(P, dens, os.path.join(out, "side_view.png"), f"{tid} {tpl['name']} — 1차 설계 / 설계 영역")
    report["criteria"] = [dict(id=c["id"], rule=f'{c["quantity"]} {c["op"]} {c["value"]}',
                               why=c.get("derivation", ""), source=c.get("source")) for c in spec["constraints"]]
    report["assumptions"] = spec["assumptions"]
    if check is not None:
        report["first_design_check"] = check
    body, cad_info = export_step(spec, os.path.join(out, "design_1st.step"))
    report["cad"] = dict(step="design_1st.step", **cad_info)
    report["drawing"] = make_drawing(spec, body, os.path.join(out, "design_1st_drawing.dxf"),
                                     os.path.join(out, "design_1st_drawing.pdf"),
                                     title=f"자전거 폰 거치대 — 1차 설계",
                                     check=check, mass_g=cad_info["mass_g"], req=report["requirements"])
    report["seconds"] = round(time.time() - t0, 2)
    with open(os.path.join(out, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    return report


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", default="")
    ap.add_argument("--sketch")
    ap.add_argument("--photo")
    ap.add_argument("--template", choices=sorted(BY_ID))
    ap.add_argument("--out", default="out")
    ap.add_argument("--no-eval", action="store_true")
    a = ap.parse_args()
    r = run(a.text, a.sketch, a.photo, a.template, a.out, not a.no_eval)
    c = r.get("first_design_check", {})
    print(json.dumps(dict(template=r["template"]["id"], name=r["template"]["name"], chosen_by=r["template"]["chosen_by"],
                          rules=[x["rule"] for x in r["text"]["fired"]], questions=r["text"]["questions"],
                          problem=r["problem"]["elements"], cad_mass_g=r["cad"]["mass_g"], drawing=r["drawing"],
                          mass_g=c.get("mass_g"), f1_hz=c.get("f1_hz"),
                          checks={k: v["pass"] for k, v in c.get("checks", {}).items()},
                          requirements={k: v.get("pass_") for k, v in r["requirements"].items() if isinstance(v, dict)},
                          seconds=r["seconds"]),
                     ensure_ascii=False, indent=1))
