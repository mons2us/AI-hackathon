"""Browser engine (src/engine.js) vs the Python input stage: same answers?

  python app/artifact/test_parity.py        (needs node and a built dist/: python app/artifact/build.py)

Checks: text rules, spec assembly (every template x bar x request variant), 1st-design check incl.
user-stated phone mass (interpolated in the browser vs real FEM here), sketch matching on the example
sketches and on synthetic hand-drawn sketches (ring centre / radius and top-3 ranking)."""
import base64
import json
import math
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)

from formproof_input import text_rules  # noqa: E402
from formproof_input.compile import Problem  # noqa: E402
from formproof_input.fem import evaluate  # noqa: E402
from formproof_input.pipeline import decode_image, looks_like_photo, matcher  # noqa: E402
from formproof_input.sketch import draw_image, find_ring, ink_points, perturb, template_strokes  # noqa: E402
from formproof_input.templates.bike_mount import build_spec  # noqa: E402
from formproof_input.templates.library import BY_ID, TEMPLATES  # noqa: E402

DIST = os.path.join(HERE, "dist")
NODE = r"""
const fs = require('fs');
const FP = require(process.argv[2]);
FP.init(JSON.parse(fs.readFileSync(process.argv[3] + '/data/tables.json', 'utf8')));
const cases = JSON.parse(fs.readFileSync(0, 'utf8'));
const geoCache = {};
const geo = k => geoCache[k] || (geoCache[k] = JSON.parse(fs.readFileSync(process.argv[3] + '/data/geo/' + k + '.json', 'utf8')));
const out = cases.map(c => {
  try {
    if (c.kind === 'text') return FP.parseText(c.text);
    if (c.kind === 'hint') return FP.templateFromHint(c.hint);
    if (c.kind === 'spec') {
      const parsed = FP.parseText(c.text);
      const {p, barAsked} = FP.resolveParams(c.tid, parsed.params);
      const g = geo(c.tid + '_' + p.bar_d.toFixed(1));
      const spec = FP.buildSpec(g, p, {name: c.name, chosen_by: 'test'}, barAsked);
      return {spec, check: FP.firstDesignCheck(g, spec, p)};
    }
    if (c.kind === 'match') {
      const u = Buffer.from(c.data, 'base64'), g = new Float32Array(u.length);
      for (let i = 0; i < u.length; i++) g[i] = u[i] / 255;
      const photo = c.photo_flag ? FP.looksLikePhoto(g) : false;
      const pts = FP.inkPoints(g, c.w, c.h, photo);
      const r = FP.matchPoints(pts);
      return {photo, frame: r.frame, ring_score: r.ring_score, ring: r.ring, ids: r.candidates.map(x => x.id), scores: r.candidates.map(x => x.score)};
    }
  } catch (e) { return {error: String(e.stack || e)}; }
});
process.stdout.write(JSON.stringify(out));
"""


def node(cases):
    script = os.path.join(DIST, "_parity_runner.js")
    with open(script, "w") as f:
        f.write(NODE)
    try:
        r = subprocess.run(["node", script, os.path.join(HERE, "src", "engine.js"), DIST], input=json.dumps(cases),
                           capture_output=True, text=True, check=True)
    finally:
        os.remove(script)
    return json.loads(r.stdout)


def same(a, b, path="", tol=1e-6, diffs=None):
    diffs = [] if diffs is None else diffs
    if isinstance(a, dict) and isinstance(b, dict):
        for k in set(a) | set(b):
            if k not in a or k not in b:
                diffs.append(f"{path}.{k}: missing in {'py' if k not in a else 'js'}")
            else:
                same(a[k], b[k], f"{path}.{k}", tol, diffs)
    elif isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        if len(a) != len(b):
            diffs.append(f"{path}: len {len(a)} != {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            same(x, y, f"{path}[{i}]", tol, diffs)
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        if abs(a - b) > tol * max(1, abs(a)):
            diffs.append(f"{path}: {a} != {b}")
    elif a != b:
        diffs.append(f"{path}: {a!r} != {b!r}")
    return diffs


TEXTS = [
    "", "자갈길에서도 폰이 안 흔들리게, 최대한 가볍게. 갤럭시 S25 울트라, 3D 프린터로 뽑을 거야",
    "S25 플러스, 로드 바이크, 튼튼하게", "s25 시내 출퇴근용, 따릉이", "MTB 산길, 앞으로 길게 뻗어서 보강대",
    "여름 땡볕에서도 변형 없고 화면 각도는 자유롭게", "핸들 25.4 mm, 230g 폰, 높게 L자로 꺾어서",
    "28.6mm 핸들바, 짧게, 낮게", "가로 모드로 돌려서 보고 싶어, 절대 안 부러지게", "갤럭시 S25 그냥, 미니벨로",
]


def main():
    assert os.path.isdir(DIST), "build first: python app/artifact/build.py"
    fails = 0

    # 1) text rules
    js = node([dict(kind="text", text=t) for t in TEXTS] + [dict(kind="hint", hint=text_rules.parse(t)["shape_hint"]) for t in TEXTS])
    for i, t in enumerate(TEXTS):
        d = same(text_rules.parse(t), js[i])
        h = text_rules.template_from_hint(text_rules.parse(t)["shape_hint"], TEMPLATES)
        if d or h != js[len(TEXTS) + i]:
            fails += 1
            print("TEXT FAIL", repr(t), d[:5], h, js[len(TEXTS) + i])
    print(f"text rules: {len(TEXTS)} sentences checked")

    # 2) spec + 1st-design check
    cases, py = [], []
    for tpl in TEMPLATES:
        for t in TEXTS:
            parsed = text_rules.parse(t)
            params = dict(tpl["params"])
            params.update(parsed["params"])
            bar = params.get("bar_d", 31.8)
            if bar not in (22.2, 25.4, 28.6, 31.8, 35.0):
                continue                           # browser snaps other diameters (separate assumption line)
            cases.append(dict(kind="spec", tid=tpl["id"], name=tpl["name"], text=t))
            py.append((tpl, params))
    js = node(cases)
    n_fem = 0
    for (tpl, params), c, r in zip(py, cases, js):
        if "error" in r:
            fails += 1
            print("SPEC ERROR", c, r["error"][:400])
            continue
        spec = json.loads(json.dumps(build_spec(params, tpl["id"], meta=dict(name=tpl["name"], chosen_by="test"))))
        d = same(spec, r["spec"])
        if d:
            fails += 1
            print("SPEC FAIL", tpl["id"], repr(c["text"]), d[:6])
        if params.get("phone_mass_kg") and n_fem < 6:       # interpolated check vs real FEM
            n_fem += 1
            P = Problem(spec)
            ev = evaluate(P, P.initial_density())
            jc = r["check"]
            df = abs(ev["f1_hz"] - jc["f1_hz"])
            ds = abs(ev["shock_vertical"]["vm_max_mpa"] - jc["shock_vertical"]["vm_max_mpa"])
            ok = df <= 0.15 and ds <= 0.15 and ev["pass"] == jc["pass"]
            print(f"  user mass {tpl['id']}: f1 py {ev['f1_hz']} js {jc['f1_hz']}, vm py {ev['shock_vertical']['vm_max_mpa']} js "
                  f"{jc['shock_vertical']['vm_max_mpa']} {'ok' if ok else 'FAIL'}")
            fails += not ok
    print(f"spec: {len(cases)} template x request cases checked")

    # 3) matcher
    M = matcher()
    imgs = []
    for t in TEMPLATES:
        g = decode_image(open(os.path.join(ROOT, "examples", "hand", f"hand_{t['id']}.png"), "rb").read())
        imgs.append((f"hand_{t['id']}", t["id"], g, False))
    rng = np.random.default_rng(7)
    for k in range(40):
        t = TEMPLATES[k % len(TEMPLATES)]
        strokes = perturb(template_strokes(t["params"], phone=bool(k % 2)), rng, strength=1.0)
        g = draw_image(strokes, px=int(rng.integers(360, 720)), mirror=bool(k % 3 == 0), line=int(rng.integers(2, 5)))
        imgs.append((f"synth{k:02d}", t["id"], g, False))
    cases = []
    for name, _, g, photo in imgs:
        u8 = np.clip(np.round(g * 255), 0, 255).astype(np.uint8)
        cases.append(dict(kind="match", w=int(g.shape[1]), h=int(g.shape[0]), data=base64.b64encode(u8.tobytes()).decode(), photo_flag=photo))
    js = node(cases)
    agree1 = agree3 = right_py = right_js = 0
    for (name, truth, g, photo), r in zip(imgs, js):
        if "error" in r:
            fails += 1
            print("MATCH ERROR", name, r["error"][:300])
            continue
        g8 = np.clip(np.round(g * 255), 0, 255).astype(np.uint8) / 255.0
        pts = ink_points(g8, photo)
        res = M.match_points(pts)
        ring = find_ring(pts)
        ids = [c["id"] for c in res["candidates"]]
        agree1 += ids[0] == r["ids"][0]
        agree3 += ids == r["ids"]
        right_py += ids[0] == truth
        right_js += r["ids"][0] == truth
        ring_d = ""
        if ring is not None and r["ring"]:
            dc = math.hypot(ring[0][0] - r["ring"]["cx"], ring[0][1] - r["ring"]["cy"])
            ring_d = f"ring dc {dc:.2f} dr {abs(ring[1] - r['ring']['r']):.2f}"
        if ids[0] != r["ids"][0] or res["frame"] != r["frame"]:
            print(f"  {name}: py {res['frame']} {ids} {[c['score'] for c in res['candidates']]} | js {r['frame']} {r['ids']} {r['scores']} {ring_d}")
    n = len(imgs)
    print(f"matcher: top-1 same {agree1}/{n}, top-3 same order {agree3}/{n}; correct top-1 py {right_py}/{n}, js {right_js}/{n}")
    if agree1 < 0.95 * n or right_js < right_py - 1:
        fails += 1
    print("PASS" if not fails else f"FAIL ({fails})")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
