"""Korean request text -> conditions (no LLM; keyword rules, every rule is visible in the report).

Returns parameter overrides for the spec, a shape hint used only when no sketch is given,
the rules that fired, and questions for conditions that are still missing."""
import re
from . import evidence as ev

RULES = [
    # (id, regex, effect, explanation)
    ("road_rough", r"자갈|비포장|울퉁불퉁|돌길|산길|오프로드|임도|MTB|산악", {"road": "cobblestone"},
     "거친 노면 → 자갈길 진동 측정값(ISBS 2020)"),
    ("road_paved", r"포장도로|시내|출퇴근|공도|자전거도로", {"road": "paved"},
     "포장도로 → 측정 근거 없음, 자갈길 값으로 보수 적용"),
    ("light", r"가볍|경량|무게.{0,4}(줄|최소)", {"objective": "min_mass"}, "목표: 무게 최소화"),
    ("strong", r"튼튼|단단|안전하게|부서지지|절대.{0,4}(안|않)", {"safety_factor": 2.0}, "안전율 1.5 → 2.0"),
    ("bar_road", r"로드\s*바이크|로드\s*자전거|로드용", {"bar_d": ev.HANDLEBAR_D["oversize"]}, "로드 핸들 클램프부 31.8 mm(가정)"),
    ("bar_mtb", r"MTB|산악", {"bar_d": ev.HANDLEBAR_D["mtb_35"]}, "MTB 35 mm(가정, 31.8 일 수도 있음)"),
    ("bar_city", r"따릉이|생활\s*자전거|시티|미니벨로", {"bar_d": ev.HANDLEBAR_D["standard"]}, "생활 자전거 25.4 mm(가정)"),
    ("phone_ultra", r"울트라|ultra", {"phone": "galaxy_s25_ultra"}, "Galaxy S25 Ultra 218 g"),
    ("phone_plus", r"(S25|s25)\s*(\+|플러스|plus)", {"phone": "galaxy_s25_plus"}, "Galaxy S25+ 190 g"),
    ("phone_base", r"(S25|s25|갤럭시\s*S25)(?!\s*(\+|플러스|plus|울트라|ultra))", {"phone": "galaxy_s25"},
     "Galaxy S25 162 g"),
    ("print", r"3D\s*프린|출력|프린터", {"material": "PETG"}, "3D 프린트 재료 PETG(데이터시트 보유 재료)"),
]

SHAPE_HINTS = [
    ("long", r"길게|멀리|앞으로\s*쭉|앞쪽으로\s*많이", dict(pad_x0=120.0)),
    ("short", r"짧게|가깝게|핸들\s*가까이|스템\s*앞", dict(pad_x0=50.0)),
    ("high", r"높게|위로\s*올려|눈높이", dict(pad_z0=40.0)),
    ("low", r"낮게|핸들\s*높이", dict(pad_z0=0.0)),
    ("truss", r"보강|지지대|삼각", dict(arm="truss")),
    ("bent", r"꺾|ㄱ자|L자", dict(arm="L")),
]


def parse(text):
    t = text or ""
    params, fired = {}, []
    for rid, rx, eff, why in RULES:
        if re.search(rx, t, flags=re.I):
            for k, v in eff.items():
                if k in params and params[k] != v:            # first (more specific) rule wins
                    continue
                params[k] = v
            fired.append(dict(rule=rid, effect=eff, why=why))
    m = re.search(r"(\d{2}(?:\.\d)?)\s*mm?\s*(?:핸들|바|클램프)|(?:핸들|바|클램프)[^\d]{0,6}(\d{2}(?:\.\d)?)", t)
    if m:
        d = float(m.group(1) or m.group(2))
        if 20 <= d <= 40:
            params["bar_d"] = d
            fired.append(dict(rule="bar_explicit", effect={"bar_d": d}, why=f"핸들 직경 {d} mm 직접 입력"))
    m = re.search(r"(\d{3})\s*g", t)
    if m and 100 <= int(m.group(1)) <= 400:
        params["phone_mass_kg"] = int(m.group(1)) / 1000
        fired.append(dict(rule="phone_mass_explicit", effect={"phone_mass_kg": params["phone_mass_kg"]},
                          why="폰 무게 직접 입력"))
    from .requirements import LIBRARY, detect
    reqs = detect(t)
    if reqs:
        params["requirements"] = reqs
        for r in reqs:
            fired.append(dict(rule="req_" + r, effect={"requirement": r}, why=LIBRARY[r]["name"] + " → " + LIBRARY[r]["physics"]))
    hint = {}
    for hid, rx, eff in SHAPE_HINTS:
        if re.search(rx, t):
            hint.update(eff)
            fired.append(dict(rule="shape_" + hid, effect=eff, why="스케치가 없을 때 템플릿 선택에 사용"))
    questions = []
    if "phone" not in params and "phone_mass_kg" not in params:
        questions.append("어떤 폰을 올리나요? (기본: 폰 200 g + 클램프 50 g 가정)")
    if "bar_d" not in params:
        questions.append("핸들바 굵기(클램프 위치 직경)는? (기본: 31.8 mm)")
    if "road" not in params:
        questions.append("주로 달리는 길은? (기본: 자갈길 기준으로 보수 설계)")
    return dict(params=params, shape_hint=hint, fired=fired, questions=questions)


def template_from_hint(hint, templates):
    """No sketch: pick the template whose shape parameters are closest to the text hint."""
    if not hint:
        return templates[0]["id"]
    from .templates.bike_mount import DEFAULT
    want = dict(arm=DEFAULT["arm"], pad_x0=80.0, pad_z0=16.0)
    want.update(hint)

    def dist(t):
        p = {"arm": DEFAULT["arm"], **t["params"]}
        return (abs(p["pad_x0"] - want["pad_x0"]) / 40 + abs(p["pad_z0"] - want["pad_z0"]) / 20
                + (0 if p["arm"] == want["arm"] else 1.5 if "arm" in hint else 0.3))
    return min(templates, key=dist)["id"]
