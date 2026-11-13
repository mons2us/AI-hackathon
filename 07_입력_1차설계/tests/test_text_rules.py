"""Text request -> conditions -> spec numbers (no LLM)."""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from formproof_input import text_rules as T
from formproof_input.templates.bike_mount import build_spec
from formproof_input.templates.library import TEMPLATES


def spec_for(text):
    r = T.parse(text)
    return r, build_spec(r["params"])


def lim(spec, cid):
    return next(c["value"] for c in spec["constraints"] if c["id"] == cid)


def test_team_v7_request():
    r, s = spec_for("울퉁불퉁한 길에서도 폰이 안 흔들리게, 최대한 가볍게, 3D 프린터로 뽑을 거야")
    assert r["params"] == {"road": "cobblestone", "objective": "min_mass", "material": "PETG"}
    assert lim(s, "f1") == 91.2 and lim(s, "stress") == 26.0          # = team v7 criteria
    assert s["point_masses"][0]["mass_kg"] == 0.25 and len(r["questions"]) == 2


def test_phones_and_bars():
    assert T.parse("갤럭시 S25 울트라")["params"]["phone"] == "galaxy_s25_ultra"
    assert T.parse("S25+ 쓰고 로드 바이크")["params"] == {"phone": "galaxy_s25_plus", "bar_d": 31.8}
    assert T.parse("갤럭시 S25 써요")["params"]["phone"] == "galaxy_s25"
    assert T.parse("핸들 25.4mm 짜리")["params"]["bar_d"] == 25.4
    _, s = spec_for("폰 무게 230g")
    assert abs(s["point_masses"][0]["mass_kg"] - 0.28) < 1e-9


def test_paved_and_strong():
    r, s = spec_for("시내 출퇴근용, 튼튼하게")
    assert r["params"]["safety_factor"] == 2.0 and lim(s, "stress") == 19.5
    assert any("측정 근거가 없어" in a for a in s["assumptions"])          # fallback is reported, not hidden


def test_shape_hints():
    pick = lambda t: T.template_from_hint(T.parse(t)["shape_hint"], TEMPLATES)
    assert pick("") == "T01"
    assert pick("앞으로 길게") == "T03"
    assert pick("짧게") == "T02"
    assert pick("높게, L자로 꺾어서") == "T05"
    assert pick("보강대 넣어서 길게") == "T08"
    assert pick("핸들 높이로 낮게") == "T06"


if __name__ == "__main__":
    for f in (test_team_v7_request, test_phones_and_bars, test_paved_and_strong, test_shape_hints):
        f()
        print("ok", f.__name__)
