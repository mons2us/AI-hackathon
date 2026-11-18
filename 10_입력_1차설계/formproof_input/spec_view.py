"""설계 사양 카드 — 어떤 제품 · 입력(말 · 스케치 · 사진)이든 같은 형식의 행 목록으로.

GUI 입력 칸 아래 '설계 사양' 카드와 발표 5쪽 A(설계 사양 표)가 같은 모양이다.
  행 = {group, said, cond, src}
    group : '제품' | '목표' | '기준' | '질문'   (이 순서로 보여 줌)
    said  : 사용자가 한 말 · 그린 것 (없으면 '')
    cond  : 계산할 수 있는 설계 조건 (값 · 단위)
    src   : 출처 태그 목록 — '입력' · '근거 DB' · '가정' · '질문'
제품별 결과 형식이 달라(폰 거치대 P01 = design_spec, 템플릿 T·G = text.fired + criteria, TV · 안경 = conditions)
여기서 한 형식으로 맞춘다. 서버는 pipeline.design() 결과에 rep['spec_rows'] 로 붙여 보낸다."""
import re

GROUPS = ("제품", "목표", "기준", "질문")
_QUOTE = re.compile(r"[\'‘\"“]([^\'’\"”]+)[\'’\"”]")


def tags(source):
    """출처 문자열 → 태그 목록."""
    s = " ".join(source) if isinstance(source, (list, tuple)) else str(source or "")
    out = []
    if re.match(r"\s*(텍스트|스케치|사진|문장|입력)", s):
        out.append("입력")
    if re.search(r"근거|IEC|ISO|ISBS|규격|데이터시트|isbs|prusament|team_|sdof", s):
        out.append("근거 DB")
    if "가정" in s or "assumed" in s:
        out.append("가정")
    if "질문" in s or "확인" in s:
        out.append("질문")
    return out or ["가정"]


def said_of(source):
    m = _QUOTE.search(str(source or ""))
    return m.group(1) if m else ""


def _row(group, cond, said="", src=None):
    return dict(group=group, said=said, cond=cond, src=src or [])


# ---------------------------------------------------------------- P01 (발표 사례, integral)
_P01_CRIT = {("objectives", "vibration"): "f1", ("constraints", "thermal"): "Tmax", ("constraints", "touch"): "touch",
             ("constraints", "shock"): "stress", ("constraints", "manufacturing"): "interlayer"}


def _rule_text(rule):
    return rule.replace(">=", "≥").replace("<=", "≤")


def _integral(rep):
    ds = rep.get("design_spec") or {}
    crit = {c["id"]: c for c in rep.get("criteria", [])}
    g = ds.get("geometry", {})
    rows = [_row("제품", "자전거 폰 거치대 · " + str(g.get("mount_on", {}).get("value", "핸들바")) + " 장착", "", ["입력"])]
    if "handlebar_diameter_mm" in g:
        rows.append(_row("제품", f"핸들바 지름 {g['handlebar_diameter_mm']['value']} mm", "", tags(g["handlebar_diameter_mm"]["source"])))
    for sec, grp in (("objectives", "목표"), ("constraints", "기준")):
        for k, v in ds.get(sec, {}).items():
            c = crit.get(_P01_CRIT.get((sec, k), ""))
            cond = _rule_text(c["rule"]) if c else str(v["value"])
            if (sec, k) == ("constraints", "shock"):
                cond = "충격 48.5 g · 최대 응력" + cond.split("응력", 1)[-1]
            cond = {"mass": "무게 최소", "phones": "대상 폰 " + cond}.get(k, cond) if k in ("mass", "phones") else cond
            src = tags(v["source"])
            rows.append(_row(grp, cond, said_of(v["source"]), src))
    if "shake" in crit:
        rows.append(_row("기준", _rule_text(crit["shake"]["rule"]), "", ["가정"]))
    rows += [_row("질문", q, "", ["질문"]) for q in ds.get("questions_to_user", [])]
    return rows


# ---------------------------------------------------------------- 템플릿 (T01 … · 외형 G/L)
_QTY = {"natural_frequency_hz": ("1차 진동수", "Hz"), "transmissibility_band_max": ("최대 흔들림 (핸들바 대비)", "배"),
        "von_mises_max_mpa": ("충격 최대 응력", "MPa"), "layer_normal_tension_mpa": ("출력 층간 응력", "MPa"),
        "min_member_thickness_mm": ("최소 두께", "mm")}
_OBJ_RULES = {"light", "strong", "min_mass"}


def _template(rep):
    sm = rep.get("summary", {})
    rows = [_row("제품", f"{sm.get('product', '자전거 폰 거치대')} · {rep.get('template', {}).get('name', '')}", "", ["입력"]),
            _row("제품", f"폰 {sm.get('phone', '')} · 핸들바 {sm.get('bar_d', '')} mm", "", ["입력", "가정"])]
    for f in rep.get("text", {}).get("fired", []):
        eff = f.get("effect", {})
        grp = "목표" if (f.get("rule") in _OBJ_RULES or "objective" in eff) else "제품" if ("phone" in eff or "bar_d" in eff) else "기준"
        rows.append(_row(grp, f.get("why", ""), f.get("said", ""), ["입력"]))
    if not any(r["group"] == "목표" for r in rows) and sm.get("objective"):
        rows.append(_row("목표", str(sm["objective"]), "", ["가정"]))
    for c in rep.get("criteria", []):
        m = re.match(r"(\w+)\s*(>=|<=)\s*([\d.]+)", c.get("rule", ""))
        if not m or m.group(1) not in _QTY:
            continue
        name, unit = _QTY[m.group(1)]
        rows.append(_row("기준", f"{name} {'≥' if m.group(2) == '>=' else '≤'} {m.group(3)} {unit}", "", tags(c.get("source"))))
    rows += [_row("질문", q, "", ["질문"]) for q in rep.get("text", {}).get("questions", [])]
    return rows


# ---------------------------------------------------------------- TV 스탠드 · AI 글래스
def _product(rep):
    t = rep.get("template", {})
    rows = [_row("제품", f"{rep.get('product', '')} · {t.get('name', '')}".strip(" ·"), "", ["입력"])]
    for c in rep.get("conditions", []):
        v = str(c.get("value", ""))
        limit = re.search(r"≤|≥|않|유지|이하|이상|\d\s*–\s*[\d.]+\s*N\b", v)
        grp = ("목표" if c.get("key") == "mass" else "기준") if limit else "제품"
        rows.append(_row(grp, f"{c.get('name', '')} {c.get('value', '')}".strip(), said_of(c.get("source")), tags(c.get("source"))))
    return rows


def spec_rows(rep):
    kind = rep.get("kind")
    rows = _integral(rep) if kind == "integral" else _product(rep) if kind == "product" else _template(rep)
    order = {g: i for i, g in enumerate(GROUPS)}
    return sorted(rows, key=lambda r: order.get(r["group"], 9))
