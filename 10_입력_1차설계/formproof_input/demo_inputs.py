"""데모 입력 (말 + 스케치) — 제품마다 하나. 지금의 1차 설계 형상을 그대로 내도록 만든 언어 프롬프트 · 스케치.

스케치 인식은 이후 단계(트랙 2): 지금은 P01 과 같은 방식으로 그림 지문(잉크 썸네일 상관)으로 등록해 두고,
같은 그림(다시 저장 · 축소 · 캔버스 여백 · 덧그린 선 약간 포함)이면 정해 둔 템플릿으로 보낸다.
note = 스케치 속 손글씨 메모 — 조건 생성기(spec_cards)가 문장과 함께 읽는다."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
INPUT_ROOT = os.path.dirname(HERE)

DEMOS = [
    dict(product="bike", key="P01", label="P01 일체형 거치대 (말 + 스케치)",
         sketch=os.path.join(INPUT_ROOT, "examples", "presentation", "input_sketch.png"),
         prompt="울퉁불퉁한 길에서도 폰이 안 흔들리게, 최대한 가볍게. 3D 프린터로 뽑을 거야",
         note="안 흔들리게! · 최대한 가볍게! · 3D 프린터로 뽑을 거야 · 모든 폰 · 열 안 갇히게 · 화면 눌러도 안 휘게 · "
              "앉아서 보이게 (눈) · 여기에 폰! · 35도쯤 · 스템 옆에 · 케이블, 레버 피하기 · (거치대 모양은?) · 울퉁불퉁한 길 덜덜덜"),
    dict(product="tv", key="TV01-low", template="TV01", level="low", label="TV 스탠드 (말 + 스케치)",
         sketch=os.path.join(INPUT_ROOT, "examples", "demo", "tv_sketch.png"),
         prompt="27인치 TV를 방마다 굴려서 옮기는 스탠드. 아이가 밀어도 안 넘어지게, 앉아서 보기 좋은 높이의 가로 화면으로",
         note="방마다 굴려서 옮길래! · 아이가 밀어도 안 넘어지게! · 27인치 TV, 가로로 · 앉아서 보는 높이 · 높이 조절 · 화면 돌리기 · "
              "바퀴 달린 둥근 받침 · 밀어도? · 10° 기울여도? · 바퀴 5개 · (받침 모양은?) · 앉아서 보이게 (눈)"),
    dict(product="glasses", key="AG-gm", style="gm", label="AI 글래스 (말 + 스케치)",
         sketch=os.path.join(INPUT_ROOT, "examples", "demo", "glasses_sketch.png"),
         prompt="하루 종일 써도 가볍고 안 흘러내리는 AI 글래스. 관자놀이가 뜨겁지 않게, 렌즈 50",
         note="하루 종일 써도 가볍게! · 안 흘러내리게! · 관자놀이 안 뜨겁게 · 두꺼운 검정 뿔테 · 렌즈 50 · 카메라 · 칩 · 배터리 넣기 · "
              "카메라 · LED · 코에 걸치는 곳 · 뜨거우면 안 돼 · 칩 · 배터리 · 적당히 조이게"),
]
_FP = {}


def by_product(product):
    return next((d for d in DEMOS if d["product"] == product), None)


def match(product, gray, thr=0.85):
    """등록된 데모 스케치면 그 항목, 아니면 None (P01 과 같은 지문 · 같은 문턱)."""
    from .integral import _fingerprint
    d = by_product(product)
    if d is None or gray is None or not os.path.exists(d["sketch"]):
        return None
    if d["key"] not in _FP:
        from skimage import io
        _FP[d["key"]] = _fingerprint(io.imread(d["sketch"]) / 255.0)
    try:
        s = float((_fingerprint(gray) * _FP[d["key"]]).sum())
    except Exception:                                    # noqa: BLE001
        return None
    return d if s >= thr else None
