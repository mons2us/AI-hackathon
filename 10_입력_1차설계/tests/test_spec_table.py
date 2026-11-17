"""설계 사양 표: 데모 입력(말 + 스케치) → 사양 행 · 수치 = 판정 기준 · 고친 값 반영 · 지금 1차 설계 그대로."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from formproof_input import demo_inputs, pipeline, spec_table        # noqa: E402


def _gray(path):
    from skimage import io
    a = io.imread(path) / 255.0
    if a.ndim == 3 and a.shape[2] == 4:
        return a[..., :3].mean(-1) * a[..., 3] + (1 - a[..., 3])
    return a[..., :3].mean(-1) if a.ndim == 3 else a


def test_demo_spec_rows():
    """제품마다: 말 · 스케치 글자에서 온 행, 수치 = 판정 기준, 판정 항목은 모두 고칠 수 있는 행으로, 모든 행에 근거."""
    out = []
    need = {"bike": {"f1": 95, "Tmax": 21, "touch": 0.3, "stress": 26, "shake": 1.5},
            "tv": {"tilt": 10, "caster": 200, "defl": 1.0, "size_in": 27, "zc": 884},
            "glasses": {"mass": 50, "clamp_lo": 0.3, "clamp_hi": 1.1, "skin": 43, "lens_w": 50}}
    for d in demo_inputs.DEMOS:
        sp = spec_table.preview(d["prompt"], sketch=_gray(d["sketch"]))
        rows = {x["id"]: x for x in sp["rows"]}
        assert sp["product"] == d["product"], sp["product"]
        assert sp["template"]["id"] == {"bike": "P01", "tv": "TV01", "glasses": "AG-gm"}[d["product"]]
        for k, v in need[d["product"]].items():
            assert k in rows and rows[k]["edit"] and abs(float(rows[k]["value"]) - v) < 1e-6, (k, rows.get(k))
        said = {x["group"] for x in sp["rows"] if "말" in x["from"]}
        drawn = {x["group"] for x in sp["rows"] if "스케치" in x["from"]}
        assert len(said) >= 4 and len(drawn) >= 2, (said, drawn)
        for x in sp["rows"]:
            assert x["basis"] in spec_table.BASES and x["source"] and (x["value"] is not None or x["text"]), x
            if "말" in x["from"] and x["quote"]:
                assert x["quote"].replace(" ", "") in d["prompt"].replace(" ", ""), x
        out.append(f"{d['product']} {len(sp['rows'])}줄 (말 {len(said)} · 스케치 {len(drawn)})")
    return ", ".join(out)


def test_demo_inputs_keep_first_design():
    """데모 말 + 스케치 → 지금의 1차 설계와 같은 템플릿 · 같은 판정 (형상 바뀌지 않음), 확정 사양은 파일로."""
    tmp = tempfile.mkdtemp()
    got = []
    refs = {"bike": dict(template="P01"), "tv": dict(text="", sketch=_gray(os.path.join(demo_inputs.INPUT_ROOT, "examples", "hand", "hand_TV01.png")),
                                                       product="tv"),
            "glasses": dict(text="", product="glasses")}
    for d in demo_inputs.DEMOS:
        rep = pipeline.design(d["prompt"], sketch=_gray(d["sketch"]), out=os.path.join(tmp, d["key"]))
        ref = pipeline.design(out=os.path.join(tmp, "ref_" + d["key"]), **refs[d["product"]])
        assert rep["template"]["id"] == ref["template"]["id"], (rep["template"]["id"], ref["template"]["id"])
        if d["product"] == "tv":
            assert rep["template"]["level"] == ref["template"]["level"] == "low"
        a = [(r["key"], r["value"], r["limit"], r["ok"]) for r in rep["judge"]["rows"]]
        b = [(r["key"], r["value"], r["limit"], r["ok"]) for r in ref["judge"]["rows"]]
        assert a == b, (d["key"], a, b)
        assert os.path.exists(os.path.join(tmp, d["key"], "design_spec_confirmed.json"))
        got.append(f"{d['key']} = 기존 ({', '.join(f'{k} {v}' for k, v, _, _ in a[:2])} …)")
    for p in ("tv", "glasses"):                      # 다른 제품 그림은 데모로 가지 않음
        other = demo_inputs.by_product("glasses" if p == "tv" else "tv")["sketch"]
        assert demo_inputs.match(p, _gray(other)) is None
    return "; ".join(got)


def test_edited_spec():
    """사용자가 고친 사양: 판정 수치 → 1차 설계 판정 기준, 형상 값 → 템플릿 (렌즈 폭 52 · 화면 32형 높게)."""
    tmp = tempfile.mkdtemp()
    tv = demo_inputs.by_product("tv")
    rep = pipeline.design(tv["prompt"], sketch=_gray(tv["sketch"]), out=os.path.join(tmp, "tv"), spec={"tilt": 7.5, "zc": 1150})
    t = next(r for r in rep["judge"]["rows"] if r["key"] == "tilt")
    assert t["limit"] == 7.5 and t["ok"] == (t["value"] >= 7.5) and rep["template"]["level"] == "high", (t, rep["template"]["level"])
    gl = demo_inputs.by_product("glasses")
    sp = spec_table.preview(gl["prompt"], sketch=_gray(gl["sketch"]), edits={"lens_w": 52.4, "skin": 60})
    assert next(x for x in sp["rows"] if x["id"] == "lens_w")["value"] == 52.0
    rep2 = pipeline.design(gl["prompt"], sketch=_gray(gl["sketch"]), out=os.path.join(tmp, "gl"), spec={"lens_w": 52.4, "skin": 60})
    s = next(r for r in rep2["judge"]["rows"] if r["key"] == "skin")
    assert "52" in rep2["template"]["name"] and s["limit"] == 60 and s["ok"], (rep2["template"]["name"], s)
    return (f"TV 기울기 기준 10 → 7.5° (값 {t['value']}°, {'충족' if t['ok'] else '미충족'}), 높이 1150 mm → '높게'; "
            f"글래스 렌즈 52.4 → 52 mm 템플릿, 피부 기준 43 → 60 °C ({s['value']} °C 충족)")


if __name__ == "__main__":
    print(test_demo_spec_rows())
    print(test_demo_inputs_keep_first_design())
    print(test_edited_spec())
