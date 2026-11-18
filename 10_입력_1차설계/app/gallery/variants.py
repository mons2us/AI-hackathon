"""Look variants for review (clamp x arm x section x joint x holder). IDs are stable: G01.."""
PHONES = {"ultra": (162.8, 77.6, 8.2), "base": (146.9, 70.5, 7.2), "plus": (158.4, 75.8, 7.3)}

# colour schemes: primary (body), secondary, accent, rubber_col (coloured silicone), phone body
SCHEMES = {
    "matte_black": dict(primary=0x1b1d21, secondary=0x2a2d33, accent=0xe2552b, rubber_col=0x202225, phone=0x2c3038),
    "graphite_orange": dict(primary=0x3a3f46, secondary=0x24272c, accent=0xff7a1a, rubber_col=0x24272c, phone=0x1c1f24),
    "white_grey": dict(primary=0xe9ebee, secondary=0x9aa1aa, accent=0x2f6fed, rubber_col=0xd5d9de, phone=0x2c3038),
    "olive": dict(primary=0x55603f, secondary=0x2b2f25, accent=0xd8b04a, rubber_col=0x2b2f25, phone=0xd9d6cf),
    "teal": dict(primary=0x0b6366, secondary=0x1d2a2c, accent=0xf2a33a, rubber_col=0x1d2a2c, phone=0x24282e),
    "red_black": dict(primary=0xb3262e, secondary=0x1b1d21, accent=0xf0f0f0, rubber_col=0x1b1d21, phone=0x2c3038),
    "alu": dict(primary=0xa9b0b8, secondary=0x30343a, accent=0x2f6fed, rubber_col=0x30343a, phone=0x1e2126),
    "navy": dict(primary=0x1f2f55, secondary=0x0f1626, accent=0x3cc0ff, rubber_col=0x0f1626, phone=0xe8e4dc),
}

V = [
    dict(id="G01", clamp="bolt", arm="angled", section="rect", joint="ball", holder="side_clamp", scheme="matte_black", phone="ultra",
         note="가장 흔한 범용형: 볼트 클램프 + 비스듬한 팔 + 양옆 집게"),
    dict(id="G02", clamp="hinge", arm="gooseneck", section="round", joint="ball", holder="x_grip", scheme="graphite_orange", phone="plus",
         note="둥근 관 구스넥 + X자 집게 (배달·통근용에서 흔함)"),
    dict(id="G03", clamp="strap", arm="riser", section="rect", joint="fixed", holder="silicone", scheme="matte_black", phone="base",
         note="공구 없이 고무 띠로 감는 실리콘 홀더, 핸들 바로 위"),
    dict(id="G04", clamp="bolt", arm="out_front", section="trib", joint="fixed", holder="twist", scheme="graphite_orange", phone="ultra",
         note="사이클 컴퓨터 자리 아웃프론트 + 회전 잠금 퍽(전용 케이스)"),
    dict(id="G05", clamp="hinge", arm="out_front", section="taper", joint="disc", holder="magsafe", scheme="alu", phone="plus",
         note="알루미늄 느낌 아웃프론트 + 자석 원판"),
    dict(id="G06", clamp="bolt", arm="truss", section="ibeam", joint="ball", holder="side_clamp", scheme="teal", phone="ultra",
         note="I자 리브 트러스 팔 (팀 최적화 결과와 가장 닮은 계열)"),
    dict(id="G07", clamp="strap", arm="riser", section="round", joint="ball", holder="x_grip", scheme="white_grey", phone="base",
         note="저가형: 스트랩 + 짧은 기둥 + X자 집게"),
    dict(id="G08", clamp="bolt", arm="L", section="round", joint="disc", holder="hooks", scheme="olive", phone="plus",
         note="L자 관 + 아래 갈고리 받침(한 손으로 끼우기)"),
    dict(id="G09", clamp="hinge", arm="long_gooseneck", section="round", joint="ball", holder="side_clamp", scheme="red_black", phone="ultra",
         note="길게 휜 구스넥 + 양옆 집게, 폰이 핸들 앞으로 나옴"),
    dict(id="G10", clamp="bolt", arm="tall_riser", section="rect", joint="disc", holder="magsafe", scheme="matte_black", phone="ultra",
         note="높은 기둥 + 자석 원판 (스템 위 높이로 올림)"),
    dict(id="G11", clamp="hinge", arm="angled", section="taper", joint="fixed", holder="hooks", scheme="navy", phone="base",
         note="가늘어지는 팔 + 갈고리 받침"),
    dict(id="G12", clamp="strap", arm="gooseneck", section="round", joint="disc", holder="magsafe", scheme="teal", phone="plus",
         note="스트랩 + 구스넥 + 자석 (가볍게 붙였다 떼는 형)"),
    dict(id="G13", clamp="bolt", arm="vee", section="round", joint="ball", holder="side_clamp", scheme="alu", phone="ultra",
         note="V자 두 팔(보강) + 양옆 집게"),
    dict(id="G14", clamp="hinge", arm="out_front_long", section="rect", joint="ball", holder="side_clamp", scheme="white_grey", phone="ultra",
         note="긴 아웃프론트 + 양옆 집게 (범용 아웃프론트)"),
    dict(id="G15", clamp="bolt", arm="L", section="trib", joint="fixed", holder="x_grip", scheme="red_black", phone="plus",
         note="T자 리브 L자 팔 + X자 집게"),
    dict(id="G16", clamp="strap", arm="riser", section="rect", joint="fixed", holder="twist", scheme="navy", phone="base",
         note="스트랩 + 회전 잠금 퍽 (가장 작은 형)"),
]
