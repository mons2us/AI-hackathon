"""Look templates (clamp x arm x section x joint x holder, templates.library.LOOKS).

  python tests/test_looks.py          -> all checks + templates/db/look_physics.json (1st-design numbers of every look)
"""
import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from formproof_input import look as LK, sketch as S, text_rules as T  # noqa: E402
from formproof_input.compile import Problem  # noqa: E402
from formproof_input.fem import evaluate  # noqa: E402
from formproof_input.templates import bike_mount  # noqa: E402
from formproof_input.templates.library import ALL, BY_ID, LOOK_ALIASES, LOOKS  # noqa: E402

PHYS = os.path.join(os.path.dirname(LK.__file__), "templates", "db", "look_physics.json")


def test_every_look_builds_and_solves(write=False):
    """Spec -> grid -> initial design -> FEM for every look; phone clears the clamp and the arm; payload = CAD table."""
    rows, t0 = [], time.time()
    for t in LOOKS:
        sp = bike_mount.build_spec(t["params"], t["id"])
        g, pm = sp["geometry"], sp["point_masses"][0]
        assert g["look"]["clearance_mm"]["ok"], (t["id"], g["look"]["clearance_mm"])
        P = Problem(sp)
        d = P.initial_density()
        r = evaluate(P, d)
        f1 = r["f1_hz"]
        assert math.isfinite(f1) and f1 > 1.0, (t["id"], f1)
        assert math.isfinite(r["transmissibility_band_max"]), t["id"]
        e = LK.payload_entry(t["look"]["holder"], t["look"]["joint"], g["look"]["tilt_deg"], (g["phone"]["H"], g["phone"]["W"], g["phone"]["D"]))
        assert abs(pm["mass_kg"] - (pm["parts"]["phone_case_kg"] + sum(p["m"] for p in e["parts"]))) < 1e-3, t["id"]
        rows.append(dict(id=t["id"], **t["look"], tilt_deg=g["look"]["tilt_deg"], mass_g=r.get("mass_g"),
                         payload_g=round(pm["mass_kg"] * 1e3), f1_hz=f1, T_band=r["transmissibility_band_max"],
                         stress_mpa=r["checks"]["stress"]["value"], connected=r["connected"], pass_=r.get("pass")))
        assert r["connected"], t["id"]
    if write:
        with open(PHYS, "w", encoding="utf-8") as f:
            json.dump(dict(note="1차 설계(최적화 전) 값. 기본 요청(폰 미지정 350 g 범위, 자갈길, Ø31.8)", rows=rows), f,
                      ensure_ascii=False, indent=0)
    return f"{len(rows)} looks, {time.time() - t0:.0f}s"


def test_payload_table_matches_cad():
    """Table entry + phone mass = direct CadQuery mass properties of the same assembly."""
    from formproof_input import mount_modules as MM
    dims = (160.0, 76.0, 8.0)
    e = LK.payload_entry("side_clamp", "ball", 20.0, dims)
    direct = MM.payload_entry("side_clamp", "ball", 20.0, dims)
    a = LK.combine_payload(e, (10.0, 55.0, 30.0), 0.29)
    b = LK.combine_payload(direct, (10.0, 55.0, 30.0), 0.29)
    assert abs(a["mass_kg"] - b["mass_kg"]) < 1e-6 and np.allclose(a["cg"], b["cg"], atol=1e-2)
    assert np.allclose(a["inertia"], b["inertia"], rtol=1e-3, atol=0.5)
    J = np.asarray(a["inertia"])
    assert np.allclose(J, J.T) and np.all(np.linalg.eigvalsh(J) > 0)
    assert abs(J[0, 1]) < 1e-6 and abs(J[1, 2]) < 1e-6           # symmetric about the y plane: no x-y / y-z products
    return f"{a['mass_kg']*1e3:.0f} g, CG {np.round(a['cg'], 1).tolist()}"


def test_cad_matches_grid():
    """CAD bracket (clamp + arm, printed parts) mass vs voxel initial design, one look per arm (default section)."""
    from formproof_input.cad import export_step
    out, worst = [], 0.0
    for arm in LK.ARMS:
        t = next(x for x in LOOKS if x["look"]["arm"] == arm and x["look"]["clamp"] == "bolt")
        sp = bike_mount.build_spec(t["params"], t["id"])
        P = Problem(sp)
        on = P.solid | (P.design & (P.initial_density() > 0.5))
        vox = 2 * on.sum() * P.h ** 3 * sp["material"]["rho"] * 1e6
        _, info = export_step(sp, "/tmp/_look.step")
        rel = abs(info["bracket_mass_g"] - vox) / info["bracket_mass_g"]
        worst = max(worst, rel)
        out.append(f"{t['id']} {info['bracket_mass_g']:.0f}/{vox:.0f}")
        assert info["valid"], t["id"]
        assert rel < 0.10, (t["id"], info["bracket_mass_g"], vox)
    return f"worst {worst:.0%}"


def test_clean_look_sketches(step=3):
    """The stored sketch of a look (with / without phone) ranks itself first among all templates.
    The cross-section of the arm (rect / T-rib / I-rib) is not visible from the side: a look that differs from the
    sketched one only in its section counts as found. Every `step`-th look (step=1: all, about 7 min)."""
    M = S.Matcher(ALL)
    miss, n = [], 0
    same_side = lambda a, b: a and all(a[k] == b[k] for k in ("clamp", "arm", "joint", "holder"))
    for t in LOOKS[::step]:
        for ph in (True, False):
            img = S.draw_image(S.template_strokes(t["params"], phone=ph))
            top = M.match_image(img)["candidates"][0]["id"]
            n += 1
            if top != t["id"] and not same_side(BY_ID[top].get("look"), t["look"]):
                miss.append((t["id"], ph, top))
    assert len(miss) <= 0.06 * n, miss
    return f"{n - len(miss)}/{n} (단면만 다른 것은 같은 것으로)"


def hand_accuracy(reps=1, seed=11, strength=1.0, words=True):
    """Synthetic hand sketches of looks: arm family / exact template, sketch only and sketch + look words."""
    from formproof_input.pipeline import rerank_with_words
    rng = np.random.default_rng(seed)
    M = S.Matcher(ALL)
    n = arm1 = top1 = top5 = w1 = 0
    for _ in range(reps):
        for t in LOOKS:
            st = S.perturb(S.template_strokes(t["params"], phone=rng.random() < 0.6), rng, strength)
            img = S.draw_image(st, px=int(rng.integers(300, 700)), mirror=rng.random() < 0.5, line=int(rng.integers(2, 6)))
            m = M.match_image(img, k=len(ALL))
            ids = [c["id"] for c in m["candidates"]]
            n += 1
            top1 += ids[0] == t["id"]
            top5 += t["id"] in ids[:5]
            arm1 += (BY_ID[ids[0]].get("look") or {}).get("arm") == t["look"]["arm"]
            if words:            # the request names holder and clamp (e.g. "스트랩으로 묶는 자석 거치대")
                hint = {k: t["look"][k] for k in ("holder", "clamp")}
                r = rerank_with_words(dict(m, candidates=[dict(c) for c in m["candidates"]]), hint)
                w1 += r["candidates"][0]["id"] == t["id"]
    return dict(n=n, arm_top1=round(arm1 / n, 2), top1=round(top1 / n, 2), top5=round(top5 / n, 2),
                with_words_top1=round(w1 / n, 2) if words else None)


def test_hand_drawn_looks():
    r = hand_accuracy()
    assert r["arm_top1"] >= 0.85 and r["top5"] >= 0.85 and r["with_words_top1"] >= 0.85, r
    return r


def test_text_picks_look():
    cases = {"구스넥에 자석으로 붙는 거치대": "G12", "스트랩으로 묶는 실리콘 홀더": "G03", "아웃프론트에 회전 잠금": "G04",
             "길게 뻗은 구스넥 X자 집게": "L-LG-X-b", "원터치 레버 클램프에 V자 두 팔": "L-VE-S-h"}
    for q, want in cases.items():
        got = T.look_from_hint(T.parse(q)["look_hint"], LOOKS)
        assert got == want, (q, got, want)
    assert not T.parse("자갈길에서 가볍게")["look_hint"]
    assert set(LOOK_ALIASES.values()) <= {t["id"] for t in LOOKS}
    return f"{len(cases)} 문장"


if __name__ == "__main__":
    for fn in (test_payload_table_matches_cad, test_text_picks_look, test_clean_look_sketches, test_hand_drawn_looks,
               test_cad_matches_grid):
        t = time.time()
        print(fn.__name__, fn(), f"({time.time() - t:.0f}s)")
    print("physics", test_every_look_builds_and_solves(write=True))
