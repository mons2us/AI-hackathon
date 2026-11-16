"""필요 물리 조건 카드 — 말 + 스케치 메모 → '1차 설계에 필요한 물리 조건' (발표 5쪽 A: 근거 기반 물리 조건 정의).

카드 하나 = 사용자가 한 말(또는 스케치 메모) 한 토막 → 물리 조건 몇 줄 + 근거.
  from   : ["말"] / ["스케치"] / ["말", "스케치"] / ["기본"]  (기본 = 말 · 스케치에 없지만 이 제품이면 꼭 보는 조건)
  quote  : 말 · 메모에서 찾은 표현 (기본이면 None)
  conds  : 조건 (쉬운 말 + 수치) — 수치는 판정 기준과 같은 값 (같은 상수에서 읽음)
  basis  : 근거 DB | 가정 | 질문 | 목표 | 스케치   (근거가 없으면 '가정' 또는 '질문'으로 표시 = 발표 원칙 '근거가 없으면 묻는다')
  source : 출처 한 줄
  keys   : 이 카드가 정한 판정 항목 (1차 설계 성능 블록의 key)

설계 전에 바로 만들 수 있어야 함(preview): 형상 · 계산 결과에 기대지 않고 말 · 스케치 메모 · 제품 상수만 씀."""
import re

ORDER_BASIS = ("근거 DB", "스케치", "목표", "가정", "질문")


def _find(rx, s):
    m = re.search(rx, s or "")
    return re.sub(r"\s+", " ", m.group(0)).strip() if m else None


def _build(rules, text, note):
    cards = []
    for r in rules:
        q_t, q_n = _find(r["rx"], text), _find(r.get("rx_note", r["rx"]), note)
        if not (q_t or q_n or r.get("default")):
            continue
        frm = [k for k, q in (("말", q_t), ("스케치", q_n)) if q] or ["기본"]
        basis = r["basis"]
        if basis == "스케치" and not q_n:
            basis = "가정"
        cards.append(dict(title=r["title"], **{"from": frm}, quote=q_t or q_n, conds=r["conds"], basis=basis,
                          source=r["source"], keys=r.get("keys", [])))
    return cards


# ------------------------------------------------------------------ P01 (자전거 폰 거치대, 일체형)
def _p01_rules():
    from .integral import targets, SHAKE_LIMIT, evidence
    tg, ev = targets(), evidence()
    road = ev["road_vib_isbs2020"]["value"]
    y, sf = ev["petg_prusament"]["value"]["yield_mpa"], ev["safety_factor"]["value"]["sf"]
    b0, b1 = road["band_hz"]
    return [
        dict(title="흔들림", rx=r"안\s*흔들리(?:게|도록)?", basis="근거 DB", keys=["f1", "shake"],
             conds=[f"떨림 주파수 ≥ {tg['f1_min_hz']} Hz", f"흔들림 ≤ {SHAKE_LIMIT}배 ({b0}–{b1} Hz)"],
             source="ISBS 2020 조약돌길 실측 · 흔들림 배수는 가정(확인 질문)"),
        dict(title="충격", rx=r"울퉁불퉁(?:한)?\s*길|덜덜", basis="근거 DB", keys=["stress"],
             conds=[f"충격 {road['shock_g']} g", f"충격 응력 ≤ {tg['shock_vm_max_mpa']:g} MPa (PETG {y:g} ÷ {sf:g})"],
             source="ISBS 2020 · Prusament PETG"),
        dict(title="무게", rx=r"(?:최대한\s*)?가볍게", basis="목표", keys=[],
             conds=["무게 최소 (조건을 모두 지키면서)"], source="말 = 최적화 목표"),
        dict(title="출력 (3D 프린터)", rx=r"3D\s*프린터(?:로)?(?:\s*뽑을\s*거야)?", basis="질문", keys=["interlayer"],
             conds=[f"층간 응력 ≤ {tg['shock_interlayer_max_mpa']:g} MPa", "PETG FDM · 부재 두께 하한"],
             source="PETG 층간 강도 — 출력 방향 확인 필요"),
        dict(title="하중 (폰)", rx=r"모든\s*폰", basis="근거 DB", keys=[], default=True,
             conds=["폰 + 고정 부품 311 g (관성 포함)", "폭 64–90 · 두께 6–14 mm, 4면 고정"],
             source="시판 폰 + 케이스 범위"),
        dict(title="열", rx=r"열\s*안\s*갇히게?", basis="스케치", keys=["Tmax"], default=True,
             conds=[f"폰 온도 상승 ≤ {tg['phone_Tmax_rise_max_c']} °C"], source="발열 4 W 가정 (내비 사용)"),
        dict(title="터치", rx=r"(?:화면\s*)?눌러도\s*안\s*휘게?", basis="스케치", keys=["touch"], default=True,
             conds=[f"화면 5 N 눌러도 처짐 ≤ {tg['touch_max_mm']} mm"], source="누르는 힘 5 N 가정"),
        dict(title="설치 · 설계 영역", rx=r"35\s*도쯤?|스템\s*옆|\(?거치대\s*모양은\??\)?", basis="질문", keys=[],
             conds=["거치 35° · 스템 옆 · 핸들바 Ø31.8", "'?' 상자 = 설계 영역 (클램프 · 폰 받침 고정)"],
             source="스케치 근사값 → 각도 · 핸들바 지름 확인 질문"),
    ]


# ------------------------------------------------------------------ TV 스탠드
def _tv_rules(text, demo):
    from .products import tv_stand as T
    tv = T.tv_spec(T.parse_size(text or "") or 27)
    tid = demo["template"] if demo else T.keyword_template(text or "")
    orient = T.BY_ID[tid]["orient"]
    oname = "가로" if orient == "landscape" else "세로"
    sw, sh = (tv["W"], tv["H"]) if orient == "landscape" else (tv["H"], tv["W"])
    if demo:
        zc = T.level_zc(tv, orient, demo["level"])
        hcond, hsrc = f"화면 중심 높이 {zc:.0f} mm ({T.LEVEL_NAME[demo['level']]})", "스케치 · 스탠바이미 높이 조절 범위"
    else:
        hcond, hsrc = "화면 중심 높이 = 스케치에서 읽음", "스탠바이미 높이 조절 범위 안으로 맞춤"
    y = T.MAT["yield_mpa"]
    return [
        dict(title="화면", rx=r"\d{2}\s*(?:인치|형)(?:\s*TV)?", basis="근거 DB" if tv["size_in"] == 27 else "가정", keys=[], default=True,
             conds=[f"{tv['size_in']}형 {oname} · {sw:.0f} × {sh:.0f} mm", f"화면 무게 {tv['mass_kg']} kg"],
             source="LG 스탠바이미 27형 사양" if tv["size_in"] == 27 else "27형에서 크기 비례 (가정)"),
        dict(title="넘어짐", rx=r"(?:아이가\s*)?밀어도\s*안\s*넘어지게?|안\s*넘어지게?", rx_note=r"10\s*°?\s*기울여도\??|밀어도\??",
             basis="근거 DB", keys=["tilt", "push"], default=True,
             conds=["10° 기울여도 안 넘어짐", "무게 13 % 수평력으로 밀어도 (참고)"], source="IEC 62368-1 8.6 안정성 시험"),
        dict(title="이동", rx=r"굴려서?\s*옮기(?:는|기|길래)?|바퀴", basis="가정", keys=["caster"],
             conds=["바퀴 5개 · 둥근 받침", f"바퀴 하나 ≤ {T.CASTER_LIMIT_N:.0f} N"], source="소형 캐스터 정격 약 20 kg"),
        dict(title="보는 높이", rx=r"앉아서\s*(?:보기\s*좋은|보는)?\s*(?:높이)?", basis="스케치", keys=[],
             conds=[hcond], source=hsrc),
        dict(title="화면 흔들림", rx=r"흔들리지?\s*않게|안\s*흔들리게?", basis="가정", keys=["defl"], default=True,
             conds=[f"밀 때 화면 윗단 ≤ {T.TOP_DEFLECTION_MM} mm"], source="팀 TV 스탠드 사례와 같은 값"),
        dict(title="튼튼함", rx=r"튼튼|부러지지?\s*않게", basis="가정", keys=["stress"], default=True,
             conds=[f"응력 ≤ {y / T.SF:.0f} MPa (강 {y:.0f} ÷ {T.SF:g})"], source="SS275 일반값 · 안전율 1.5"),
        dict(title="설계 영역", rx=r"\(?받침\s*모양은\??\)?", basis="스케치", keys=[],
             conds=["받침 = 설계 영역 (화면 · 기둥 위치 고정)"], source="스케치 '?' 상자"),
    ]


# ------------------------------------------------------------------ AI 글래스
def _glasses_rules(text):
    from .products import glasses as G
    lw = G.parse_lens_w(text or "")
    lw_t = min(G.LENS_WIDTHS, key=lambda w: abs(w - lw))
    parts = sum(G.PARTS_G.values())
    return [
        dict(title="무게", rx=r"가볍(?:게|고)?", basis="근거 DB", keys=["mass"], default=True,
             conds=[f"총무게 ≤ {G.MASS_LIMIT:.0f} g (테 + 렌즈 + 부품)"], source="보도: 41–50 g"),
        dict(title="흘러내림", rx=r"안\s*흘러내리(?:게|는)?", basis="가정", keys=["clamp_lo"], default=True,
             conds=[f"조이는 힘 ≥ {G.CLAMP_RANGE[0]} N (좌우 각각)"], source="흘러내림 방지 하한 (가정)"),
        dict(title="착용감", rx=r"적당히\s*조이게?|편하게|안\s*아프게", basis="근거 DB", keys=["clamp_hi"], default=True,
             conds=[f"조이는 힘 ≤ {G.CLAMP_RANGE[1]} N ({G.SPREAD_EACH:.0f} mm 벌릴 때)"], source="문헌 0–1 N · 특허 50–110 g"),
        dict(title="열", rx=r"관자놀이(?:가)?\s*(?:안\s*)?뜨겁(?:지\s*않게|게)|안\s*뜨겁게|뜨거우면\s*안\s*돼", basis="근거 DB",
             keys=["skin"], default=True, conds=[f"다리 표면 ≤ {G.T_SKIN_LIMIT:.0f} °C (주변 {G.T_AMB:.0f} °C)"],
             source="IEC 62368-1 TS1 장시간 접촉"),
        dict(title="계속 켜짐", rx=r"하루\s*종일", basis="가정", keys=["skin"],
             conds=[f"칩 {G.SOC_W} W 계속 발열"], source="촬영 · AI 평균 소비전력 (가정)"),
        dict(title="크기", rx=r"렌즈\s*\d{2}", basis="스케치", keys=[],
             conds=[f"렌즈 폭 {lw_t:.0f} mm"], source="템플릿 48 · 50 · 52 mm 중 가까운 것"),
        dict(title="내장 부품", rx=r"카메라|칩|배터리", basis="근거 DB", keys=["mass"],
             conds=[f"카메라 · 칩 · 배터리 {parts:.0f} g (다리 앞부분)"], source="보도 · 유출 사양 (무게는 가정)"),
        dict(title="튼튼함", rx=r"튼튼|부러지지?\s*않게", basis="가정", keys=["clamp_vm", "bridge_vm"], default=True,
             conds=[f"벌림 · 브리지 {G.BRIDGE_F:.0f} N에서 응력 ≤ {G.MAT['yield_mpa'] / G.SF:.0f} MPa"],
             source="아세테이트 40 MPa ÷ 1.5 · ISO 12870 부위"),
    ]


# ------------------------------------------------------------------ 자전거 일반 템플릿 (T · G): 판정 기준(criteria) 수치로
SRC_NAME = {"isbs2020": "ISBS 2020 실측", "team_v3_rigid": "팀 v3 폰 강체", "sdof": "1자유도 근사", "prusament_petg": "Prusament PETG",
            "team_v7": "팀 v7 규칙", "energy_balance": "에너지 평형", "lisbon_reflect": "노면 반사"}


def from_criteria(rep):
    """설계 뒤: 템플릿 거치대의 판정 기준 → 카드 (말에서 온 것은 '말', 나머지는 '기본')."""
    text = (rep.get("input") or {}).get("text") or ""
    sm = rep.get("summary") or {}
    crit = {c["id"]: c for c in rep.get("criteria") or []}
    val = lambda k: (crit[k]["rule"].split(" ", 2)[2] if k in crit else None)

    def src(keys):
        tags = [t for k in keys if k in crit for t in (crit[k].get("source") or [])]
        names = list(dict.fromkeys(SRC_NAME.get(t, None) for t in tags if not str(t).startswith("assumed")))
        return " · ".join(n for n in names if n) or "가정", any(str(t).startswith("assumed") for t in tags)

    rules = []
    def add(title, rx, keys, conds, default=True):
        conds = [c for c in conds if c]
        if not conds:
            return
        s_, assumed = src(keys)
        rules.append(dict(title=title, rx=rx, keys=[k for k in keys if k in crit], conds=conds, default=default,
                          basis="가정" if s_ == "가정" else "근거 DB", source=s_ + (" (일부 가정)" if assumed else "")))
    add("흔들림", r"안\s*흔들리(?:게|도록)?", ["transmissibility", "f1"],
        [val("transmissibility") and f"흔들림 ≤ {val('transmissibility')}배 ({sm.get('vib', '')})",
         val("f1") and f"떨림 주파수 ≥ {val('f1')} Hz"])
    add("충격", r"울퉁불퉁(?:한)?\s*길|자갈|비포장|돌길|험한\s*길", ["stress"],
        [f"충격 {sm.get('shock_g')} g" if sm.get("shock_g") else None, val("stress") and f"충격 응력 ≤ {val('stress')} MPa"])
    add("출력 (3D 프린터)", r"3D\s*프린터|출력", ["interlayer", "min_feature"],
        [val("interlayer") and f"층간 응력 ≤ {val('interlayer')} MPa", val("min_feature") and f"부재 두께 ≥ {val('min_feature')} mm"])
    add("땡볕", r"땡볕|햇빛|여름", ["sun_heat"], ["주차 표면 온도 ≤ 열변형 온도 − 10 K"] if "sun_heat" in crit else [])
    add("무게", r"(?:최대한\s*)?가볍게", [], ["무게 최소 (조건을 모두 지키면서)"], default=False)
    if rules and rules[-1]["title"] == "무게":
        rules[-1].update(basis="목표", source="말 = 최적화 목표")
    add("하중 (폰)", r"모든\s*폰|아이폰|갤럭시|폰", [], [f"폰 + 고정 부품 {sm.get('point_mass_g')} g" if sm.get("point_mass_g") else None,
                                                      sm.get("phone")])
    if rules and rules[-1]["title"] == "하중 (폰)":
        rules[-1].update(basis="근거 DB", source="시판 폰 + 케이스 범위")
    return _build(rules, text, "")


def cards(product, text="", note="", demo=None, p01=False):
    """설계 전에 바로: 말 + 스케치 메모 → 카드 목록. product: bike(P01) | tv | glasses."""
    if product == "tv":
        return _build(_tv_rules(text, demo), text, note)
    if product == "glasses":
        return _build(_glasses_rules(text), text, note)
    if product == "bike" and p01:
        return _build(_p01_rules(), text, note)
    return []


def preview(text="", sketch=None, image=None, template=None, product=None):
    """GUI: '1차 설계 만들기' 직후 형상 계산 전에 보여 줄 카드. (product, cards) — 자전거 일반 템플릿은 [] (설계 뒤 판정 기준에서)."""
    from . import pipeline, demo_inputs, integral
    prod = pipeline.route_product(text, sketch, image, template, product)
    g = sketch if sketch is not None else image
    if prod == "bike":
        p01 = template == "P01" or (not template and ((g is not None and integral.matches_presentation_sketch(g))
                                                      or (g is None and integral.is_presentation_text(text))))
        d = demo_inputs.match("bike", g) if g is not None else None
        note = d["note"] if d else (demo_inputs.by_product("bike")["note"] if p01 and not text else "")
        return prod, cards("bike", text, note, p01=p01)
    d = demo_inputs.match(prod, g) if (g is not None and not template) else None
    return prod, cards(prod, text, d["note"] if d else "", demo=d)
