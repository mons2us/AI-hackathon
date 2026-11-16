"""설계 사양 표 — 말 + 스케치 → 1차 설계 전에 정하는 물리 사양 (한 줄 = 한 항목 · 한 수치, 사용자가 고친 뒤 확정).

행(row):
  id      : 행 이름 (판정 항목 key 또는 param 이름 — 고친 값을 돌려받을 때 씀)
  group   : 같은 말 · 메모에서 나온 행 묶음 이름 (흔들림, 충격 …)
  quote   : 그 말 · 메모 토막 (묶음의 첫 행에만), from: ["말"] / ["스케치"] / ["말", "스케치"] / ["기본"]
  item    : 항목 (쉬운 말)
  op      : ">=" | "<=" | "=" | ""   (""= 글로 된 사양)
  value · unit : 수치 · 단위 (text: 글로 된 사양)
  keys    : 이 수치가 정하는 1차 설계 판정 항목 (고치면 판정 기준이 바뀜)
  param   : 이 수치가 정하는 형상 값 (고치면 템플릿 선택이 바뀜: 렌즈 폭 · 화면 크기 · 화면 높이)
  edit    : 고칠 수 있는지 (False = 계산 조건으로 고정된 값, 예: 충격 48.5 g · 폰 311 g — 팀 엔진 / 템플릿 결과 DB 조건)
  basis · source : 근거 (근거 DB | 스케치 | 목표 | 가정 | 질문) · 출처 한 줄

설계 전에 바로 만들 수 있어야 함: 형상 · 계산 결과에 기대지 않고 말 · 스케치 메모 · 제품 상수 · 템플릿 선택만 씀."""
import re

BASES = ("근거 DB", "스케치", "목표", "가정", "질문")


def R(item, op="", value=None, unit="", keys=(), param=None, edit=None, text=None):
    return dict(item=item, op=op, value=value, unit=unit, keys=list(keys), param=param, text=text,
                edit=(bool(keys) or bool(param)) if edit is None else edit)


def _find(rx, s):
    m = re.search(rx, s or "")
    return re.sub(r"\s+", " ", m.group(0)).strip() if m else None


def _build(rules, text, note):
    rows = []
    for r in rules:
        q_t, q_n = _find(r["rx"], text), _find(r.get("rx_note", r["rx"]), note)
        if not (q_t or q_n or r.get("default")):
            continue
        frm = [k for k, q in (("말", q_t), ("스케치", q_n)) if q] or ["기본"]
        basis = r["basis"]
        if basis == "스케치" and not q_n:
            basis = "가정"
        for i, x in enumerate(r["rows"]):
            rid = x["param"] or (x["keys"][0] if x["keys"] else f"{r['group']}:{i}")
            rows.append(dict(x, id=rid, group=r["group"], quote=(q_t or q_n) if i == 0 else None, **{"from": frm},
                             basis=x.pop("basis", None) or basis, source=r["source"]))
    seen = set()
    for x in rows:                                       # id 겹치면 뒤에 번호
        while x["id"] in seen:
            x["id"] += "'"
        seen.add(x["id"])
    return rows


# ------------------------------------------------------------------ P01 (자전거 폰 거치대, 일체형)
def _p01_rules():
    from .integral import targets, SHAKE_LIMIT, evidence
    tg, ev = targets(), evidence()
    road = ev["road_vib_isbs2020"]["value"]
    y, sf = ev["petg_prusament"]["value"]["yield_mpa"], ev["safety_factor"]["value"]["sf"]
    b0, b1 = road["band_hz"]
    return [
        dict(group="흔들림", rx=r"안\s*흔들리(?:게|도록)?", basis="근거 DB", default=True,
             rows=[R("떨림 주파수", ">=", tg["f1_min_hz"], "Hz", ["f1"]),
                   R(f"흔들림 ({b0}–{b1} Hz)", "<=", SHAKE_LIMIT, "배", ["shake"])],
             source="ISBS 2020 조약돌길 실측 · 흔들림 배수는 가정(확인 질문)"),
        dict(group="충격", rx=r"울퉁불퉁(?:한)?\s*길|덜덜", basis="근거 DB", default=True,
             rows=[R("충격 가속도", "=", road["shock_g"], "g", edit=False),
                   R("충격 응력", "<=", tg["shock_vm_max_mpa"], "MPa", ["stress"])],
             source=f"ISBS 2020 · Prusament PETG {y:g} MPa ÷ {sf:g}"),
        dict(group="무게", rx=r"(?:최대한\s*)?가볍게", basis="목표",
             rows=[R("무게", text="최소 (조건을 모두 지키면서)")], source="말 = 최적화 목표"),
        dict(group="출력", rx=r"3D\s*프린터(?:로)?(?:\s*뽑을\s*거야)?", basis="질문", default=True,
             rows=[R("층간 응력", "<=", tg["shock_interlayer_max_mpa"], "MPa", ["interlayer"])],
             source="PETG 층간 강도 — 출력 방향 확인 필요"),
        dict(group="폰", rx=r"모든\s*폰", rx_note=r"폰", basis="근거 DB", default=True,
             rows=[R("폰 + 고정 부품", "=", 311, "g", edit=False), R("폰 크기", text="폭 64–90 · 두께 6–14 mm, 4면 고정")],
             source="시판 폰 + 케이스 범위"),
        dict(group="열", rx=r"열이?\s*안\s*갇히(?:게)?", basis="가정", default=True,
             rows=[R("폰 온도 상승", "<=", tg["phone_Tmax_rise_max_c"], "°C", ["Tmax"])], source="발열 4 W 가정 (내비 사용)"),
        dict(group="터치", rx=r"(?:화면을?\s*)?눌러도\s*안\s*휘(?:게)?", basis="가정", default=True,
             rows=[R("화면 5 N 누를 때 처짐", "<=", tg["touch_max_mm"], "mm", ["touch"])], source="누르는 힘 5 N 가정"),
        dict(group="설치", rx=r"스템\s*옆(?:에)?|35\s*(?:도|°)", rx_note=r"35\s*°|35\s*도", basis="질문", default=True,
             rows=[R("거치 각도", "=", 35, "°", edit=False), R("핸들바 지름", "=", 31.8, "mm", edit=False),
                   R("피할 곳", text="스템 · 케이블 · 레버")],
             source="스케치 근사값 → 각도 · 핸들바 지름 확인 질문"),
        dict(group="설계 영역", rx=r"\?", rx_note=r"\?", basis="스케치",
             rows=[R("설계 영역", text="'?' 상자 (클램프 · 폰 받침은 고정)")], source="스케치 '?' 상자"),
    ]


# ------------------------------------------------------------------ TV 스탠드
def _tv_rules(pk):
    from .products import tv_stand as T
    tv, orient, level = pk["tv"], pk["orient"], pk["level"]
    sw, sh = (tv["W"], tv["H"]) if orient == "landscape" else (tv["H"], tv["W"])
    hsrc = ("스케치 · 스탠바이미 높이 조절 범위" if pk["demo"] else
            "말" if pk["zc_how"] == "문장" else "스케치 비율" if pk["zc_how"] else "템플릿 가운데 높이")
    y = T.MAT["yield_mpa"]
    return [
        dict(group="화면", rx=r"\d{2}\s*(?:인치|형)(?:\s*TV)?", rx_note=r"\d{2}\s*(?:\"|인치|형)", basis="근거 DB" if tv["size_in"] == 27 else "가정",
             default=True, rows=[R("화면 크기", "=", tv["size_in"], "인치", param="size_in"),
                                 R("화면 무게", "=", tv["mass_kg"], "kg", edit=False),
                                 R(f"화면 ({'가로' if orient == 'landscape' else '세로'})", text=f"{sw:.0f} × {sh:.0f} mm")],
             source="LG 스탠바이미 27형 사양 (다른 크기는 비례)"),
        dict(group="넘어짐", rx=r"(?:아이가\s*)?밀어도\s*안\s*넘어지(?:게)?|안\s*넘어지(?:게)?", rx_note=r"10\s*°", basis="근거 DB", default=True,
             rows=[R("기울여도 안 넘어지는 각", ">=", 10.0, "°", ["tilt"]), R("수평으로 밀 때 여유 (참고)", ">=", 1.0, "배", ["push"])],
             source="IEC 62368-1 8.6 안정성 시험"),
        dict(group="이동", rx=r"(?:바퀴로\s*)?굴려서?\s*옮기(?:고|는|기)?|바퀴", basis="가정", default=True,
             rows=[R("바퀴 하나 하중", "<=", T.CASTER_LIMIT_N, "N", ["caster"]), R("바퀴", text="5개 · 둥근 받침")],
             source="소형 캐스터 정격 약 20 kg"),
        dict(group="높이", rx=r"앉아서\s*(?:보기\s*좋은|보는)?\s*(?:높이)?|높이\s*조절", basis="스케치", default=True,
             rows=[R("화면 중심 높이", "=", round(pk["zc_t"]), "mm", param="zc")], source=hsrc + " → 템플릿 3단에 맞춤"),
        dict(group="흔들림", rx=r"흔들리지?\s*않게|안\s*흔들리게?", basis="가정", default=True,
             rows=[R("밀 때 화면 윗단 흔들림", "<=", T.TOP_DEFLECTION_MM, "mm", ["defl"])], source="팀 TV 스탠드 사례와 같은 값"),
        dict(group="튼튼함", rx=r"튼튼|부러지지?\s*않게", basis="가정", default=True,
             rows=[R("응력", "<=", round(y / T.SF, 1), "MPa", ["stress"])], source=f"강 SS275 {y:.0f} MPa ÷ {T.SF:g}"),
        dict(group="설계 영역", rx=r"받침\s*모양은\??", rx_note=r"\?", basis="스케치",
             rows=[R("설계 영역", text="받침 (화면 · 기둥 위치는 고정)")], source="스케치 '?' 상자"),
    ]


# ------------------------------------------------------------------ AI 글래스
def _glasses_rules(lw_t):
    from .products import glasses as G
    parts = sum(G.PARTS_G.values())
    y = G.MAT["yield_mpa"]
    return [
        dict(group="무게", rx=r"가볍(?:게|고)?", basis="근거 DB", default=True,
             rows=[R("총무게 (테 + 렌즈 + 부품)", "<=", G.MASS_LIMIT, "g", ["mass"])], source="보도: 41–50 g"),
        dict(group="흘러내림", rx=r"안\s*흘러내리(?:게|는)?", basis="가정", default=True,
             rows=[R("조이는 힘 (좌우 각각)", ">=", G.CLAMP_RANGE[0], "N", ["clamp_lo"])], source="흘러내림 방지 하한 (가정)"),
        dict(group="착용감", rx=r"적당히\s*조이(?:게)?|편하게|안\s*아프게", basis="근거 DB", default=True,
             rows=[R(f"조이는 힘 ({G.SPREAD_EACH:.0f} mm 벌릴 때)", "<=", G.CLAMP_RANGE[1], "N", ["clamp_hi"])],
             source="문헌 0–1 N · 특허 50–110 g"),
        dict(group="열", rx=r"관자놀이(?:가)?\s*(?:안\s*)?뜨겁(?:지\s*않게|게)|안\s*뜨겁게", basis="근거 DB", default=True,
             rows=[R("다리 표면 온도", "<=", G.T_SKIN_LIMIT, "°C", ["skin"]), R("칩 발열 (계속 켜짐)", "=", G.SOC_W, "W", edit=False)],
             source=f"IEC 62368-1 TS1 장시간 접촉 · 주변 {G.T_AMB:.0f} °C · 발열은 가정"),
        dict(group="크기", rx=r"렌즈\s*\d{2}", rx_note=r"\b\d{2}\b", basis="스케치", default=True,
             rows=[R("렌즈 폭", "=", lw_t, "mm", param="lens_w")], source="템플릿 48 · 50 · 52 mm 중 가까운 것"),
        dict(group="부품", rx=r"카메라|칩|배터리", basis="근거 DB",
             rows=[R("카메라 · 칩 · 배터리", "=", parts, "g", edit=False)], source="보도 · 유출 사양 (무게는 가정)"),
        dict(group="튼튼함", rx=r"튼튼|부러지지?\s*않게", basis="가정", default=True,
             rows=[R(f"벌림 · 브리지 {G.BRIDGE_F:.0f} N 응력", "<=", round(y / G.SF, 1), "MPa", ["clamp_vm", "bridge_vm"])],
             source=f"아세테이트 {y:.0f} MPa ÷ {G.SF:g} · ISO 12870 부위"),
    ]


# ------------------------------------------------------------------ 자전거 템플릿 거치대 (T · G): 설계 명세(constraints)에서
QNAME = {"transmissibility": ("흔들림 (노면 대역)", "배"), "f1": ("떨림 주파수", "Hz"), "stress": ("충격 응력", "MPa"),
         "interlayer": ("층간 응력", "MPa"), "min_feature": ("부재 두께", "mm")}
SRC_NAME = {"isbs2020": "ISBS 2020 실측", "team_v3_rigid": "팀 v3 폰 강체", "sdof": "1자유도 근사", "prusament_petg": "Prusament PETG",
            "team_v7": "팀 v7 규칙", "energy_balance": "에너지 평형", "lisbon_reflect": "노면 반사"}
JUDGED = ("transmissibility", "f1", "stress", "interlayer")


def _bike_rules(spec):
    C = {c["id"]: c for c in spec["constraints"]}
    sm = spec.get("summary") or {}
    pm = spec["point_masses"][0]["mass_kg"] * 1e3 if spec.get("point_masses") else None
    shock = next((c for c in spec.get("load_cases", []) if c.get("name") == "shock_vertical"), {})

    def row(k):
        c = C[k]
        name, unit = QNAME.get(k, (k, ""))
        try:
            v = float(c["value"])
        except (TypeError, ValueError):
            return R(name, text=f"{c['op']} {c['value']}")
        return R(name, c["op"], v, unit, [k] if k in JUDGED else [], edit=k in JUDGED)

    def src(keys):
        tags = [t for k in keys if k in C for t in (C[k].get("source") or [])]
        names = [n for n in dict.fromkeys(SRC_NAME.get(t) for t in tags) if n]
        return " · ".join(names) or "가정"
    rules = []
    if "transmissibility" in C or "f1" in C:
        rules.append(dict(group="흔들림", rx=r"안\s*흔들리(?:게|도록)?|흔들림", basis="근거 DB", default=True,
                          rows=[row(k) for k in ("transmissibility", "f1") if k in C], source=src(["transmissibility", "f1"])))
    if "stress" in C:
        g = shock.get("accel_g") or shock.get("g")
        rules.append(dict(group="충격", rx=r"울퉁불퉁(?:한)?\s*길|자갈|비포장|돌길", basis="근거 DB", default=True,
                          rows=([R("충격 가속도", "=", float(g), "g", edit=False)] if g else []) + [row("stress")], source=src(["stress"])))
    if "interlayer" in C or "min_feature" in C:
        rules.append(dict(group="출력", rx=r"3D\s*프린터|출력", basis="근거 DB", default=True,
                          rows=[row(k) for k in ("interlayer", "min_feature") if k in C], source=src(["interlayer", "min_feature"])))
    SPECIAL = {"sun_heat": ("땡볕", r"땡볕|햇빛|여름", "주차 표면 온도", "≤ 열변형 온도 − 10 K")}
    for k, c in C.items():
        if k in QNAME:
            continue
        grp, rx, item, txt = SPECIAL.get(k, (c.get("requirement") or k, r"(?!)", c.get("quantity", k), f"{c['op']} {c['value']}"))
        rules.append(dict(group=grp, rx=rx, basis="근거 DB", default=True, rows=[R(item, text=txt)], source=src([k])))
    rules.append(dict(group="무게", rx=r"(?:최대한\s*)?가볍게", basis="목표", rows=[R("무게", text="최소 (조건을 모두 지키면서)")],
                      source="말 = 최적화 목표"))
    if pm:
        rules.append(dict(group="폰", rx=r"모든\s*폰|아이폰|갤럭시", basis="근거 DB", default=True,
                          rows=[R("폰 + 고정 부품", "=", round(pm), "g", edit=False)], source="시판 폰 + 케이스 범위"))
    return rules


# ------------------------------------------------------------------ 진입점
def preview(text="", sketch=None, image=None, template=None, product=None, edits=None):
    """'설계 사양' 버튼: 말 + 스케치 → {product, template, rows}. edits({id: 값})가 있으면 고친 값으로 다시 (형상 값은 템플릿 다시 고름)."""
    from . import pipeline, demo_inputs, integral
    edits = {k: float(v) for k, v in (edits or {}).items() if v is not None and v != ""}
    prod = pipeline.route_product(text, sketch, image, template, product)
    g = sketch if sketch is not None else image
    d = None
    if prod == "tv":
        from .products import tv_stand as T
        pk = T.pick(text, g, template if (template or "").startswith("TV") else None, edits.get("size_in"), edits.get("zc"))
        d = pk["demo"]
        rows = _build(_tv_rules(pk), text, d["note"] if d else "")
        tpl = dict(id=pk["tid"], name=T.BY_ID[pk["tid"]]["name"], level=pk["level"])
    elif prod == "glasses":
        from .products import glasses as G
        d = demo_inputs.match("glasses", g) if g is not None else None
        lw = edits.get("lens_w") or G.parse_lens_w(text or "")
        lw_t = min(G.LENS_WIDTHS, key=lambda w: abs(w - lw))
        rows = _build(_glasses_rules(lw_t), text, d["note"] if d else "")
        tpl = dict(id="AG-" + (d["style"] if d else "gm"), name="AI 글래스")
    else:
        p01 = template == "P01" or (not template and ((g is not None and integral.matches_presentation_sketch(g))
                                                      or (g is None and integral.is_presentation_text(text))))
        if p01:
            d = demo_inputs.match("bike", g) if g is not None else None
            note = d["note"] if d else ("? · 35°" if g is not None else "")
            rows = _build(_p01_rules(), text, note)
            tpl = dict(id="P01", name="일체형 거치대")
        else:
            pk = pipeline.bike_pick(text, sketch, image, template)
            rows = _build(_bike_rules(pk["spec"]), text, "")
            tpl = dict(id=pk["tid"], name=pk["tpl"]["name"])
    for x in rows:                                       # 고친 값 표시 (형상 값은 템플릿에 맞춘 값으로 다시 계산됨)
        if x["id"] in edits and x["edit"]:
            if not x["param"]:
                x["value"] = edits[x["id"]]
            x["edited"] = True
    return dict(product=prod, template=tpl, rows=rows, note=d["note"] if d else "")


def spec_params(product, rows):
    """형상 값 (템플릿 선택에 쓰는 값) — pipeline.design(spec_params=…)."""
    p = {x["param"]: x["value"] for x in rows if x.get("param") and x.get("edited")}
    return {product: p} if p else {}


def limits(rows):
    """판정 기준 {key: (op, 값)} — 1차 설계 판정 · 최적화 기준."""
    return {k: (x["op"], float(x["value"])) for x in rows if x.get("keys") and x.get("value") is not None for k in x["keys"]}


def _ok(op, v, L):
    return v >= L if op == ">=" else v <= L


def relimit(rows, lim):
    """판정 행(judge rows)의 기준을 lim 으로 바꾸고 충족 다시. 반환 = 전부 충족인지 (참고 행 제외)."""
    for r in rows:
        if r.get("key") in lim and isinstance(r.get("value"), (int, float)):
            op, L = lim[r["key"]]
            r["limit"], r["op"] = L, op
            r["ok"] = bool(_ok(op, r["value"], L))
    return all(r["ok"] for r in rows if not r.get("ref") and not r.get("reference"))


def apply_limits(rep, lim):
    """1차 설계 결과에 확정한 사양의 판정 기준을 반영 (P01 · TV · 글래스 judge, 템플릿 거치대 checks)."""
    if not lim:
        return rep
    J = rep.get("judge")
    if J and J.get("rows"):
        J["pass_"] = relimit(J["rows"], lim)
        J["fails"] = [r["name"] for r in J["rows"] if not r["ok"] and not r.get("ref") and not r.get("reference")]
    ck = (rep.get("first_design_check") or {}).get("checks")
    if ck and not J:
        for k, c in ck.items():
            if k in lim and isinstance(c.get("value"), (int, float)):
                op, L = lim[k]
                c["limit"] = f"{op} {L:g}"
                c["pass"] = bool(_ok(op, c["value"], L))
        rep["first_design_check"]["pass"] = all(c["pass"] for c in ck.values() if not c.get("reference"))
    return rep
