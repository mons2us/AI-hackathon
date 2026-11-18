"""설계 사양 카드: 제품 · 입력과 관계없이 같은 형식(제품 → 목표 → 기준 → 질문, 항목마다 출처 태그)."""
import os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from formproof_input import pipeline
from formproof_input.spec_view import GROUPS

TAGS = {"입력", "근거 DB", "가정", "질문"}


def _check(rep):
    rows = rep["spec_rows"]
    assert rows and "spec_rows_error" not in rep
    order = [GROUPS.index(r["group"]) for r in rows]
    assert order == sorted(order)                       # 제품 → 목표 → 기준 → 질문
    assert all(r["cond"] and r["src"] and set(r["src"]) <= TAGS for r in rows)
    return rows


def test_spec_rows_all_products():
    with tempfile.TemporaryDirectory() as d:
        p01 = _check(pipeline.design("울퉁불퉁한 길에서도 폰이 안 흔들리게, 최대한 가볍게. 3D 프린터로 뽑을 거야", out=d))
        said = {r["said"] for r in p01}
        assert {"안 흔들리게", "최대한 가볍게", "울퉁불퉁한 길"} <= said           # 사용자 말 → 조건
        assert any("95 Hz" in r["cond"] and r["group"] == "목표" for r in p01)
        assert any(r["group"] == "질문" for r in p01)
        _check(pipeline.design("자갈길에서도 안 흔들리게, 최대한 가볍게", template="T01", out=d))
        gl = _check(pipeline.design("AI 글래스", product="glasses", out=d))
        assert any("50 g" in r["cond"] and r["group"] == "목표" for r in gl)
        _check(pipeline.design("TV 27인치", product="tv", out=d))


if __name__ == "__main__":
    test_spec_rows_all_products(); print("ok")
