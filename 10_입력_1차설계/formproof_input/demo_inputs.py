"""데모 입력 (말 + 스케치) — 제품마다 하나. 지금의 초기 설계 형상을 그대로 내도록 만든 언어 프롬프트 · 스케치.

스케치 = GUI 그림판(800 × 600)의 획 (examples/demo/<제품>.json, make_demo_sketches.py 로 만듦). 그림 위주에 글자는 2–3개뿐,
나머지 조건은 말(prompt)로. GUI 는 예시를 고르면 이 획을 그림판에 그리고, 영상 모드에서는 한 획씩 그려 감.
스케치 인식은 이후 단계(트랙 2): 지금은 P01 과 같은 방식으로 그림 지문(잉크 썸네일 상관 ≥ 0.85)으로 등록해 두고,
같은 그림이면 정해 둔 템플릿으로 보낸다. note = 스케치 속 글자 — 설계 사양 표(spec_table)가 문장과 함께 읽는다."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
INPUT_ROOT = os.path.dirname(HERE)
DEMO_DIR = os.path.join(INPUT_ROOT, "examples", "demo")

DEMOS = [
    dict(product="bike", key="P01", label="폰 거치대",
         prompt="자전거 핸들바 가운데에 다는 폰 거치대. 울퉁불퉁한 길에서도 폰이 안 흔들리게, 최대한 가볍게. 3D 프린터로 뽑을 거야. "
                "모든 폰이 들어가고 열이 안 갇히게, 화면을 눌러도 안 휘게. 케이블과 레버는 피해서"),
    dict(product="tv", key="TV01-low", template="TV01", level="low", label="TV 스탠드",
         prompt="27인치 TV 스탠드. 방마다 바퀴로 굴려서 옮기고, 아이가 밀어도 안 넘어지게. "
                "앉아서 보기 좋은 높이의 가로 화면에, 높이 조절이 되는 둥근 받침으로"),
    dict(product="glasses", key="AG-gm", style="gm", label="AI 글래스",
         prompt="AI 글래스. 하루 종일 써도 가볍고 안 흘러내리게, 관자놀이가 뜨겁지 않게. "
                "두꺼운 검정 뿔테에 렌즈 50, 카메라 · 칩 · 배터리를 다리에 넣고 적당히 조이게"),
]
for _d in DEMOS:
    _d["strokes"] = os.path.join(DEMO_DIR, f"{_d['product']}.json")
    _d["sketch"] = os.path.join(DEMO_DIR, f"{_d['product']}_sketch.png")
    try:
        with open(_d["strokes"], encoding="utf-8") as _f:
            _d["note"] = " · ".join(L["t"] for L in json.load(_f)["labels"])
    except OSError:
        _d["note"] = ""
_FP = {}


def by_product(product):
    return next((d for d in DEMOS if d["product"] == product), None)


def _ref(d):
    if d["key"] not in _FP:
        from skimage import io
        from .integral import _fingerprint
        _FP[d["key"]] = _fingerprint(io.imread(d["sketch"]) / 255.0)
    return _FP[d["key"]]


def score(product, gray):
    from .integral import _fingerprint
    d = by_product(product)
    if d is None or gray is None or not os.path.exists(d["sketch"]):
        return -1.0
    try:
        return float((_fingerprint(gray) * _ref(d)).sum())
    except Exception:                                    # noqa: BLE001
        return -1.0


def match(product, gray, thr=0.85):
    """등록된 데모 스케치면 그 항목, 아니면 None (P01 과 같은 지문 · 같은 문턱)."""
    d = by_product(product)
    return d if d is not None and score(product, gray) >= thr else None


def match_any(gray, thr=0.85):
    """어느 제품의 데모 스케치인지 (말에 제품 단어가 없을 때 제품 고르기)."""
    if gray is None:
        return None
    best = max(DEMOS, key=lambda d: score(d["product"], gray))
    return best if score(best["product"], gray) >= thr else None
