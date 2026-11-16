"""데모 입력(말 + 스케치) → 필요 물리 조건 카드 · 지금 1차 설계 형상 그대로."""
import os
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from formproof_input import demo_inputs, pipeline, spec_cards        # noqa: E402


def _gray(path):
    from skimage import io
    a = io.imread(path) / 255.0
    if a.ndim == 3 and a.shape[2] == 4:
        return a[..., :3].mean(-1) * a[..., 3] + (1 - a[..., 3])
    return a[..., :3].mean(-1) if a.ndim == 3 else a


def _canvas(g):
    """GUI 그림판처럼: 800 × 600 흰 캔버스 가운데 0.92 배로 그림 (예시 선택 → 캔버스 → PNG)."""
    from skimage.transform import resize
    r = min(800 / g.shape[1], 600 / g.shape[0]) * 0.92
    h, w = int(g.shape[0] * r), int(g.shape[1] * r)
    c = np.ones((600, 800))
    y0, x0 = (600 - h) // 2, (800 - w) // 2
    c[y0:y0 + h, x0:x0 + w] = resize(g, (h, w), anti_aliasing=True)
    return c


def test_demo_cards():
    """제품마다: 말 · 스케치에서 온 카드가 있고, 카드 수치 = 판정 기준 수치, 모든 카드에 근거."""
    out = []
    for d in demo_inputs.DEMOS:
        prod, cs = spec_cards.preview(d["prompt"], sketch=_canvas(_gray(d["sketch"])), product=d["product"])
        assert prod == d["product"] and len(cs) >= 6, (prod, len(cs))
        said = [c for c in cs if "말" in c["from"]]
        drawn = [c for c in cs if "스케치" in c["from"]]
        assert len(said) >= 3 and len(drawn) >= 3, (prod, len(said), len(drawn))
        for c in cs:
            assert c["conds"] and c["basis"] in spec_cards.ORDER_BASIS and c["source"], c
            if "말" in c["from"]:
                assert c["quote"] and c["quote"].replace(" ", "") in d["prompt"].replace(" ", ""), c
        txt = " ".join(x for c in cs for x in c["conds"])
        need = {"bike": ["95 Hz", "48.5 g", "26 MPa", "10.9 MPa", "21 °C", "0.3 mm", "311 g"],
                "tv": ["10°", "200 N", "4.8 kg", "1.0 mm", "884 mm"],
                "glasses": ["50 g", "0.3 N", "1.1 N", "43 °C", "렌즈 폭 50 mm"]}[prod]
        miss = [n for n in need if n not in txt]
        assert not miss, (prod, miss)
        out.append(f"{prod} {len(cs)}장(말 {len(said)} · 스케치 {len(drawn)})")
    return ", ".join(out)


def test_demo_inputs_keep_first_design():
    """데모 말 + 스케치(그림판을 거친 그림) → 지금의 1차 설계와 같은 템플릿 · 같은 판정 (형상 바뀌지 않음)."""
    tmp = tempfile.mkdtemp()
    got = []
    for d in demo_inputs.DEMOS:
        rep = pipeline.design(d["prompt"], sketch=_canvas(_gray(d["sketch"])), out=os.path.join(tmp, d["key"]), product=d["product"])
        assert rep["spec_cards"], d["key"]
        if d["product"] == "bike":
            ref = pipeline.design(template="P01", out=os.path.join(tmp, "ref_p01"))
            assert rep["template"]["id"] == "P01"
        elif d["product"] == "tv":
            ref = pipeline.design("", sketch=_gray(os.path.join(demo_inputs.INPUT_ROOT, "examples", "hand", "hand_TV01.png")),
                                  out=os.path.join(tmp, "ref_tv"), product="tv")
            assert rep["template"]["id"] == "TV01" and rep["template"]["level"] == "low" == ref["template"]["level"]
        else:
            ref = pipeline.design("", out=os.path.join(tmp, "ref_gl"), product="glasses")
            assert rep["template"]["id"] == ref["template"]["id"] == "AG-gm"
        a = [(r["key"], r["value"], r["ok"]) for r in rep["judge"]["rows"]]
        b = [(r["key"], r["value"], r["ok"]) for r in ref["judge"]["rows"]]
        assert a == b, (d["key"], a, b)
        got.append(f"{d['key']} = 기존 ({', '.join(f'{k} {v}' for k, v, _ in a[:2])} …)")
    # 등록 안 된 그림은 데모로 가지 않음
    assert demo_inputs.match("tv", _gray(demo_inputs.by_product("glasses")["sketch"])) is None
    assert demo_inputs.match("glasses", _gray(demo_inputs.by_product("tv")["sketch"])) is None
    return "; ".join(got)


if __name__ == "__main__":
    print(test_demo_cards())
    print(test_demo_inputs_keep_first_design())
