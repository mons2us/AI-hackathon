"""Bike phone-mount template library (track 1: input -> one of these).

Each template only overrides side-view shape parameters (reach, pad height, arm style).
Bar diameter, phone, road, objective come from the text request, not from the template,
so the same shape can be re-used for any request. The parameter vector (reach, rise, arm)
is also the regression target for the track-2 sketch CNN."""

TEMPLATES = [
    # kind: structure family (bar_top / out_front / gooseneck / braced / under / arm)
    dict(id="T01", name="기본형", desc="팀 v7 기준: 클램프 위에서 앞으로 곧게 뻗은 팔",
         params=dict(arm="straight", pad_x0=80.0, pad_z0=16.0)),
    dict(id="T02", name="짧은 팔", desc="핸들 가까이(스템 앞) 받침",
         params=dict(arm="straight", pad_x0=50.0, pad_z0=16.0)),
    dict(id="T03", name="긴 팔", desc="핸들 앞으로 멀리 뻗은 받침",
         params=dict(arm="straight", pad_x0=120.0, pad_z0=16.0)),
    dict(id="T04", name="높은 받침", desc="받침이 높고 팔이 비스듬히 올라감",
         params=dict(arm="straight", pad_x0=80.0, pad_z0=40.0)),
    dict(id="T05", name="L자 팔", desc="위로 올라간 뒤 앞으로 꺾인 팔",
         params=dict(arm="L", pad_x0=80.0, pad_z0=40.0)),
    dict(id="T06", name="낮은 받침", desc="핸들 높이 앞쪽에 받침, 링 앞면에서 출발",
         params=dict(arm="low", pad_x0=70.0, pad_z0=0.0)),
    dict(id="T07", name="트러스", desc="곧은 팔 + 아래 보강대",
         params=dict(arm="truss", pad_x0=80.0, pad_z0=16.0)),
    dict(id="T08", name="긴 트러스", desc="긴 팔 + 아래 보강대",
         params=dict(arm="truss", pad_x0=120.0, pad_z0=16.0)),
    dict(id="T09", name="짧은 L자", desc="짧게 올라갔다 앞으로 꺾인 팔",
         params=dict(arm="L", pad_x0=50.0, pad_z0=30.0)),
    dict(id="T10", name="낮은 긴 팔", desc="핸들 높이로 멀리 뻗은 받침",
         params=dict(arm="low", pad_x0=110.0, pad_z0=0.0)),
    # --- shapes taken from mounts on sale (structure type and proportions only; see templates/SOURCES.md)
    dict(id="T11", name="핸들 위 직결형", desc="클램프 바로 위 짧은 기둥에 받침 (바 위 직접 고정형)", kind="bar_top",
         params=dict(arm="riser", pad_x0=-10.0, pad_z0=28.0)),
    dict(id="T12", name="높은 직결형", desc="클램프 위 높은 기둥에 받침", kind="bar_top",
         params=dict(arm="riser", pad_x0=-10.0, pad_z0=44.0)),
    dict(id="T13", name="아웃프론트", desc="핸들 높이로 앞으로 나간 뒤 받침으로 올라감 (사이클 컴퓨터 마운트형)", kind="out_front",
         params=dict(arm="step", pad_x0=76.0, pad_z0=24.0)),
    dict(id="T14", name="긴 아웃프론트", desc="앞으로 길게 나간 아웃프론트", kind="out_front",
         params=dict(arm="step", pad_x0=116.0, pad_z0=36.0)),
    dict(id="T15", name="구스넥", desc="비스듬히 올라가 받침 높이에서 앞으로 뻗음", kind="gooseneck",
         params=dict(arm="dogleg", pad_x0=80.0, pad_z0=40.0)),
    dict(id="T16", name="긴 구스넥", desc="짧게 올라가 길게 뻗은 구스넥", kind="gooseneck",
         params=dict(arm="dogleg", pad_x0=120.0, pad_z0=34.0, knee_frac=0.25)),
    dict(id="T17", name="V자 지지", desc="링 위와 앞에서 나온 두 팔이 받침에서 만남", kind="braced",
         params=dict(arm="vee", pad_x0=80.0, pad_z0=16.0)),
    dict(id="T18", name="긴 V자 지지", desc="길게 뻗은 V자 두 팔", kind="braced",
         params=dict(arm="vee", pad_x0=110.0, pad_z0=24.0)),
    dict(id="T19", name="아래 기둥형", desc="링 앞에서 낮게 나가 받침 아래 기둥으로 올라감", kind="under",
         params=dict(arm="stalk", pad_x0=70.0, pad_z0=30.0)),
    dict(id="T20", name="높은 V자 지지", desc="높은 받침을 두 팔이 받침", kind="braced",
         params=dict(arm="vee", pad_x0=80.0, pad_z0=40.0)),
    dict(id="T21", name="짧고 높은 팔", desc="핸들 가까이 높게 올린 받침", kind="bar_top",
         params=dict(arm="straight", pad_x0=50.0, pad_z0=40.0)),
    dict(id="T22", name="아래 우회형", desc="링 아래로 내려가 폰 공간을 피해 돌아 올라감", kind="under",
         params=dict(arm="under", pad_x0=80.0, pad_z0=30.0, stalk_base_z=-16.0)),
]

# ------------------------------------------------------------------ look templates (formproof_input.look modules)
# clamp x arm (side path) x cross-section x joint x phone holder. Each one is built from the same modules as the CAD /
# render (mount_modules), so the analysis grid, the STEP and the sketch describe one product.
#   G01..G16  reviewed look variants (app/gallery), with their own section / joint
#   L-<arm>-<holder>-<clamp>  every arm x holder x clamp combination with the default section / joint
from .. import look as _LK                                                  # noqa: E402

ARM_CODE = {"riser": "RS", "tall_riser": "TR", "angled": "AN", "gooseneck": "GN", "long_gooseneck": "LG",
            "out_front": "OF", "out_front_long": "OL", "L": "LL", "truss": "TS", "vee": "VE"}
HOLDER_CODE = {"side_clamp": "S", "x_grip": "X", "silicone": "C", "magsafe": "M", "twist": "T", "hooks": "H"}
CLAMP_CODE = {"bolt": "b", "hinge": "h", "strap": "s"}
ARM_KIND = {"riser": "bar_top", "tall_riser": "bar_top", "angled": "arm", "gooseneck": "gooseneck",
            "long_gooseneck": "gooseneck", "out_front": "out_front", "out_front_long": "out_front", "L": "arm",
            "truss": "braced", "vee": "braced"}
GALLERY = [   # id, clamp, arm, section, joint, holder, note (app/gallery/variants.py)
    ("G01", "bolt", "angled", "rect", "ball", "side_clamp", "가장 흔한 범용형: 볼트 클램프 + 비스듬한 팔 + 양옆 집게"),
    ("G02", "hinge", "gooseneck", "round", "ball", "x_grip", "둥근 관 구스넥 + X자 집게 (배달·통근용에서 흔함)"),
    ("G03", "strap", "riser", "rect", "fixed", "silicone", "공구 없이 고무 띠로 감는 실리콘 홀더, 핸들 바로 위"),
    ("G04", "bolt", "out_front", "trib", "fixed", "twist", "사이클 컴퓨터 자리 아웃프론트 + 회전 잠금 퍽(전용 케이스)"),
    ("G05", "hinge", "out_front", "taper", "disc", "magsafe", "알루미늄 느낌 아웃프론트 + 자석 원판"),
    ("G06", "bolt", "truss", "ibeam", "ball", "side_clamp", "I자 리브 트러스 팔 (팀 최적화 결과와 가장 닮은 계열)"),
    ("G07", "strap", "riser", "round", "ball", "x_grip", "저가형: 스트랩 + 짧은 기둥 + X자 집게"),
    ("G08", "bolt", "L", "round", "disc", "hooks", "L자 관 + 아래 갈고리 받침(한 손으로 끼우기)"),
    ("G09", "hinge", "long_gooseneck", "round", "ball", "side_clamp", "길게 휜 구스넥 + 양옆 집게, 폰이 핸들 앞으로 나옴"),
    ("G10", "bolt", "tall_riser", "rect", "disc", "magsafe", "높은 기둥 + 자석 원판 (스템 위 높이로 올림)"),
    ("G11", "hinge", "angled", "taper", "fixed", "hooks", "가늘어지는 팔 + 갈고리 받침"),
    ("G12", "strap", "gooseneck", "round", "disc", "magsafe", "스트랩 + 구스넥 + 자석 (가볍게 붙였다 떼는 형)"),
    ("G13", "bolt", "vee", "round", "ball", "side_clamp", "V자 두 팔(보강) + 양옆 집게"),
    ("G14", "hinge", "out_front_long", "rect", "ball", "side_clamp", "긴 아웃프론트 + 양옆 집게 (범용 아웃프론트)"),
    ("G15", "bolt", "L", "trib", "fixed", "x_grip", "T자 리브 L자 팔 + X자 집게"),
    ("G16", "strap", "riser", "rect", "fixed", "twist", "스트랩 + 회전 잠금 퍽 (가장 작은 형)"),
]


def _look_tpl(tid, clamp, arm, section, joint, holder, note=None):
    look = dict(clamp=clamp, arm=arm, section=section, joint=joint, holder=holder)
    name = f"{_LK.ARMS[arm]} · {_LK.HOLDER_SPEC[holder]['name']}"
    desc = note or (f"{_LK.CLAMP_SPEC[clamp]['name']} + {_LK.ARMS[arm]}({_LK.SECTIONS[section]}) + "
                    f"{_LK.JOINTS[joint]} + {_LK.HOLDER_SPEC[holder]['name']}")
    return dict(id=tid, name=name, desc=desc, kind=ARM_KIND[arm], family="look", look=look, params=dict(look=look))


def _looks():
    """G-variants first; an L combination with exactly the same modules as a G-variant is not repeated
    (its id stays valid as an alias of the G-variant)."""
    out = [_look_tpl(g, c, a, s, j, h, n) for g, c, a, s, j, h, n in GALLERY]
    key = lambda L: tuple(L[k] for k in ("clamp", "arm", "section", "joint", "holder"))
    seen = {key(t["look"]): t["id"] for t in out}
    aliases = {}
    for arm in _LK.ARMS:
        for holder in _LK.HOLDER_SPEC:
            for clamp in _LK.CLAMP_SPEC:
                t = _look_tpl(f"L-{ARM_CODE[arm]}-{HOLDER_CODE[holder]}-{CLAMP_CODE[clamp]}", clamp, arm,
                              _LK.ARM_DEFAULT_SECTION[arm], _LK.HOLDER_SPEC[holder]["joint"], holder)
                if key(t["look"]) in seen:
                    aliases[t["id"]] = seen[key(t["look"])]
                else:
                    out.append(t)
    return out, aliases


LOOKS, LOOK_ALIASES = _looks()
# ------------------------------------------------------------------ 발표 사례 (formproof_input.integral)
INTEGRAL = [dict(id="P01", name="일체형 거치대 (발표 사례)", kind="integral", family="integral",
                 desc="클램프 + 20×8 mm 보 + 2 mm 판, 폰 4면 고정 부품(양옆 집게 · 아래 걸이 · 위 레일) — 발표 7·10·22쪽 처음 설계",
                 params=dict(integral="base"))]
ALL = TEMPLATES + LOOKS + INTEGRAL
BY_ID = {t["id"]: t for t in ALL}
BY_ID.update({a: BY_ID[g] for a, g in LOOK_ALIASES.items()})
