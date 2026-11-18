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
    ("outfront", r"아웃\s*프론트|컴퓨터\s*마운트|속도계\s*자리", dict(arm="step")),
    ("gooseneck", r"구스넥|거위\s*목|비스듬히\s*올", dict(arm="dogleg", pad_z0=40.0)),
    ("bartop", r"핸들\s*(바로\s*)?위|바\s*위|직결|스템\s*위", dict(arm="riser", pad_x0=-10.0, pad_z0=28.0)),
    ("vee", r"V자|브이자|두\s*팔|양쪽\s*팔", dict(arm="vee")),
    ("under", r"아래로\s*돌|밑으로|아래쪽으로\s*우회", dict(arm="under", pad_z0=30.0)),
]

# look words (holder / clamp / cross-section / joint) -> look templates (templates.library.LOOKS)
LOOK_HINTS = [
    ("holder", "x_grip", r"X\s*자|엑스\s*자|네\s*모서리|문어발"),
    ("holder", "magsafe", r"자석|맥\s*세이프|magsafe|마그네틱"),
    ("holder", "twist", r"회전\s*잠금|돌려\s*(서\s*)?(잠그|끼우)|퀵\s*락|쿼드\s*락|전용\s*케이스"),
    ("holder", "silicone", r"실리콘|고무\s*홀더|모서리를?\s*감싸"),
    ("holder", "hooks", r"갈고리|고리에?\s*걸"),
    ("holder", "side_clamp", r"양\s*옆\s*집게|스프링\s*집게|집게"),
    ("clamp", "strap", r"스트랩|고무\s*(밴드|띠|줄)|벨크로|묶어"),
    ("clamp", "hinge", r"원\s*터치|퀵\s*(릴리즈|클램프)|레버|경첩|손\s*나사"),
    ("clamp", "bolt", r"볼트|나사로\s*조"),
    ("section", "round", r"파이프|둥근\s*(관|팔)|원형\s*관"),
    ("section", "ibeam", r"I\s*자|아이\s*빔"),
    ("section", "trib", r"T\s*자|리브"),
    ("section", "taper", r"가늘어|끝이\s*가는"),
    ("joint", "ball", r"볼\s*(조인트|헤드)|각도\s*조절"),
    ("joint", "disc", r"360|회전\s*(되|판|원판)"),
    ("joint", "fixed", r"고정형|각도\s*고정"),
]
ARM_FROM_SHAPE = {"step": "out_front", "dogleg": "gooseneck", "L": "L", "truss": "truss", "vee": "vee",
                  "riser": "riser", "straight": "angled"}


def look_hint_from(text, shape_hint):
    t = text or ""
    out, fired = {}, []
    for key, val, rx in LOOK_HINTS:
        if key not in out and re.search(rx, t, flags=re.I):
            out[key] = val
            fired.append(dict(rule=f"look_{key}_{val}", effect={key: val}, why="외형 템플릿 선택에 사용"))
    arm = ARM_FROM_SHAPE.get(shape_hint.get("arm"))
    if arm == "riser" and shape_hint.get("pad_z0", 0) >= 40:
        arm = "tall_riser"
    if arm in ("gooseneck", "out_front") and shape_hint.get("pad_x0", 0) >= 110:
        arm = "long_" + arm if arm == "gooseneck" else "out_front_long"
    if arm == "riser" and re.search(r"높게|위로\s*올려|눈높이", t):
        arm = "tall_riser"
    if arm:
        out["arm"] = arm
    return out, fired


def look_from_hint(hint, looks):
    """Look template closest to the look words: fewest mismatches (arm counts 1.5), reviewed G-variants first."""
    def cost(k_t):
        k, t = k_t
        L = t["look"]
        c = sum((1.5 if key == "arm" else 1.0) for key, v in hint.items() if L.get(key) != v)
        return (c, 0 if t["id"].startswith("G") else 1, 0 if L["clamp"] == "bolt" else 1, k)
    return min(enumerate(looks), key=cost)[1]["id"]


def look_penalty(hint, look):
    return sum((1.5 if key == "arm" else 1.0) for key, v in hint.items() if look.get(key) != v)


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
    look_hint, look_fired = look_hint_from(t, hint)
    fired += look_fired
    if not (set(look_hint) - {"arm"}):          # only an arm from the shape words: keep the T templates
        look_hint = {}
    questions = []
    if "phone" not in params and "phone_mass_kg" not in params:
        questions.append("어떤 폰을 올리나요? (기본: 어떤 폰이든 되도록 폰+케이스 290 g + 폰 홀더 60 g = 350 g 가정)")
    if "bar_d" not in params:
        questions.append("핸들바 굵기(클램프 위치 직경)는? (기본: 31.8 mm)")
    if "road" not in params:
        questions.append("주로 달리는 길은? (기본: 자갈길 기준으로 보수 설계)")
    return dict(params=params, shape_hint=hint, look_hint=look_hint, fired=fired, questions=questions)


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
