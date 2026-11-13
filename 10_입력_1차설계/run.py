"""FormProof input stage, command line (the GUI is app/server.py).

  python run.py --text "자갈길에서도 안 흔들리게, 최대한 가볍게, S25 울트라" --sketch my_sketch.png --out out/
  python run.py --text "..." --image photo.jpg --out out/
  python run.py --text "..." --template T03 --out out/

Writes to --out: spec.json, problem.npz, initial_design.npy, design_1st.step, design_1st_drawing.dxf/.pdf/.png,
design_1st.stl, side_view.png, report.json, handoff.zip (everything the physics / optimisation stage needs).
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from formproof_input.pipeline import design, decode_image
from formproof_input.templates.library import BY_ID


def run(text="", sketch=None, image=None, template=None, out="out"):
    sk = decode_image(open(sketch, "rb").read()) if sketch else None
    im = decode_image(open(image, "rb").read()) if image else None
    return design(text, sk, im, template, out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", default="")
    ap.add_argument("--sketch")
    ap.add_argument("--image", "--photo", dest="image")
    ap.add_argument("--template", choices=sorted(BY_ID))
    ap.add_argument("--out", default="out")
    a = ap.parse_args()
    r = run(a.text, a.sketch, a.image, a.template, a.out)
    c = r["first_design_check"]
    print(json.dumps(dict(template=r["template"]["id"], name=r["template"]["name"], chosen_by=r["template"]["chosen_by"],
                          rules=[x["rule"] for x in r["text"]["fired"]], questions=r["text"]["questions"],
                          cad_mass_g=r["cad"]["mass_g"], f1_hz=c["f1_hz"],
                          checks={k: v["pass"] for k, v in c["checks"].items()},
                          handoff_requirements=[(h["id"], [x["id"] for x in h["constraints"]], h["warnings"])
                                                for h in r["handoff_requirements"]],
                          seconds=r["seconds"]), ensure_ascii=False, indent=1))
