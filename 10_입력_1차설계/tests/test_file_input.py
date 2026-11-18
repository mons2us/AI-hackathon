"""파일 입력 (문서 · CAD) — 예시 파일에서 글 · 그림 · 치수 · 구멍을 읽고, 설계 사양 표에 행이 붙는지."""
import os

from formproof_input import file_input as F, spec_table, pipeline

D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples", "files")


def _ing(name):
    with open(os.path.join(D, name), "rb") as f:
        return F.ingest(name, f.read())


def test_docs_text_and_figure():
    for n in ("요청서_폰거치대.pptx", "요청서_폰거치대.pdf", "요청서_폰거치대.docx"):
        o = _ing(n)
        assert o["kind"] == "doc" and "울퉁불퉁한 길" in o["text"] and o.get("image"), n
        sp = spec_table.preview(o["text"], None, pipeline.decode_image(o["image"]))
        assert sp["template"]["id"] == "P01", n          # 요청서 그림 = 발표 스케치 → 데모와 같은 경로


def test_step_holes_mass():
    o = _ing("기존_거치대_예시.step")
    assert [round(x) for x in o["info"]["size"]] == [70, 20, 110]
    assert o["info"]["holes"] == {31.8: 1, 4.2: 4}
    assert 40 < o["info"]["mass_g"] < 48
    assert any(r["basis"] == "질문" and "31.8" in r["text"] for r in o["rows"])


def test_stl_and_dxf():
    s = _ing("기존_거치대_예시.stl")
    assert abs(s["info"]["mass_g"] - _ing("기존_거치대_예시.step")["info"]["mass_g"]) < 1.0
    d = _ing("거치대_도면_예시.dxf")
    assert d["info"]["dims"] and "핸들바" in d["text"]


def test_attach_rows_in_spec():
    o = _ing("기존_거치대_예시.step")
    att = [dict(name=o["name"], kind=o["kind"], label=o["label"], rows=o["rows"])]
    sp = spec_table.preview("자전거 폰 거치대, 최대한 가볍게", None, None, attach=att)
    rows = [r for r in sp["rows"] if r["group"].startswith("CAD")]
    assert len(rows) == len(o["rows"]) and not any(r["keys"] for r in rows)   # 판정 기준은 안 바꿈
    assert spec_table.limits(sp["rows"]) == spec_table.limits(spec_table.preview("자전거 폰 거치대, 최대한 가볍게")["rows"])


def test_unknown_ext():
    try:
        F.ingest("a.xyz", b"1")
    except ValueError as e:
        assert "가능한 형식" in str(e)
    else:
        raise AssertionError
