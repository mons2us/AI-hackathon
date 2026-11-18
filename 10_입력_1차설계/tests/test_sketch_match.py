"""Track-1 sketch matcher on synthetic hand-drawn sketches (wobble, tilt, scale, omitted details,
random image size / line width / mirroring, phone drawn or not)."""
import os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from formproof_input import sketch as S
from formproof_input.templates.library import TEMPLATES


def run(strength, reps=4, seed=7):
    rng = np.random.default_rng(seed)
    M = S.Matcher(TEMPLATES)
    top1 = top3 = n = 0
    t0 = time.time()
    for _ in range(reps):
        for t in TEMPLATES:
            st = S.perturb(S.template_strokes(t["params"], phone=rng.random() < 0.5), rng, strength)
            img = S.draw_image(st, px=int(rng.integers(300, 700)), mirror=rng.random() < 0.5,
                               line=int(rng.integers(2, 6)))
            ids = [c["id"] for c in M.match_image(img)["candidates"]]
            top1 += ids[0] == t["id"]
            top3 += t["id"] in ids
            n += 1
    return dict(strength=strength, top1=round(top1 / n, 2), top3=round(top3 / n, 2), n=n,
                sec_per_query=round((time.time() - t0) / n, 2))


def test_clean_sketches_exact():
    M = S.Matcher(TEMPLATES)
    for t in TEMPLATES:
        for ph in (False, True):
            img = S.draw_image(S.template_strokes(t["params"], phone=ph))
            assert M.match_image(img)["candidates"][0]["id"] == t["id"], (t["id"], ph)


def test_hand_drawn():
    r = run(1.0)
    assert r["top1"] >= 0.8 and r["top3"] >= 0.95, r
    return r


if __name__ == "__main__":
    test_clean_sketches_exact()
    print("clean sketches: 20/20")
    for s in (0.5, 1.0, 1.5):
        print(run(s))
