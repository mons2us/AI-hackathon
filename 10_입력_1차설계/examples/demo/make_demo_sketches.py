"""데모 입력 스케치 (말 + 스케치) — TV 스탠드 · AI 글래스. 발표 P01 입력 스케치(examples/presentation/input_sketch.png)와 같은 모양:
줄 노트 + 펜 선 + 손글씨 메모(조건). 이 그림은 formproof_input/demo_inputs.py 에 지문으로 등록되어 지금의 1차 설계 형상을 그대로 낸다.

  python examples/demo/make_demo_sketches.py      → examples/demo/tv_sketch.png, glasses_sketch.png
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1600, 1120
INK, BLUE, RED, GREY = (52, 56, 66), (38, 92, 140), (196, 58, 48), (110, 114, 120)
FONT = None
for p in ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "C:/Windows/Fonts/malgun.ttf"):
    if os.path.exists(p):
        FONT = p
        break


def paper():
    im = Image.new("RGB", (W, H), (250, 250, 247))
    d = ImageDraw.Draw(im)
    for y in range(70, H, 60):
        d.line([(0, y), (W, y)], fill=(214, 228, 240), width=2)
    d.line([(140, 0), (140, H)], fill=(238, 196, 196), width=2)
    return im, d


def _wobble(pts, amp, rng):
    out = []
    for i, (x, y) in enumerate(pts):
        out.append((x + rng.gauss(0, amp), y + rng.gauss(0, amp)))
    return out


def _dense(pts, step=6):
    out = [pts[0]]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(int(math.hypot(x1 - x0, y1 - y0) / step), 1)
        out += [(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n) for k in range(1, n + 1)]
    return out


def pen(d, pts, color=INK, w=4, rng=None, twice=True, amp=0.8):
    """손으로 그린 선: 잘게 나눠 흔들고, 살짝 어긋나게 한 번 더 (발표 스케치처럼)."""
    rng = rng or random.Random(1)
    P = _dense(pts)
    d.line(_wobble(P, amp, rng), fill=color, width=w, joint="curve")
    if twice:
        c2 = tuple(min(255, c + 70) for c in color)
        d.line(_wobble([(x + 1.5, y + 1.0) for x, y in P], amp, rng), fill=c2, width=max(w - 2, 1), joint="curve")


def ellipse(cx, cy, rx, ry, a0=0, a1=360, n=90):
    return [(cx + rx * math.cos(math.radians(a)), cy + ry * math.sin(math.radians(a))) for a in [a0 + (a1 - a0) * k / n for k in range(n + 1)]]


def rrect(x0, y0, x1, y1, r, n=8):
    pts = []
    for cx, cy, a in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        pts += [(cx + r * math.cos(math.radians(a + 90 * k / n)), cy + r * math.sin(math.radians(a + 90 * k / n))) for k in range(n + 1)]
    return pts + [pts[0]]


def write(im, x, y, s, size=34, color=INK, rng=None, spacing=1.18):
    """손글씨 흉내: 글자마다 크기 · 기울기 · 기준선을 조금씩 흔듦."""
    rng = rng or random.Random(hash(s) & 0xffff)
    f = ImageFont.truetype(FONT, size)
    cx = x
    for ch in s:
        if ch == " ":
            cx += size * 0.45
            continue
        sz = int(size * rng.uniform(0.94, 1.06))
        g = ImageFont.truetype(FONT, sz)
        bb = g.getbbox(ch)
        tile = Image.new("RGBA", (bb[2] + 12, bb[3] + 12), (0, 0, 0, 0))
        ImageDraw.Draw(tile).text((6, 6), ch, font=g, fill=color + (255,))
        tile = tile.rotate(rng.uniform(-5, 5), resample=Image.BICUBIC, expand=True)
        im.paste(tile, (int(cx), int(y + rng.uniform(-3, 3))), tile)
        cx += (bb[2] - bb[0]) * spacing + size * 0.08
    return cx


def arrow(d, p0, p1, color=RED, w=3, rng=None, head=22):
    pen(d, [p0, p1], color, w, rng, twice=False)
    a = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    for s in (-1, 1):
        q = (p1[0] - head * math.cos(a + s * 0.45), p1[1] - head * math.sin(a + s * 0.45))
        pen(d, [p1, q], color, w, rng, twice=False)


def dashed(d, p0, p1, color=BLUE, w=3, dash=26, gap=18):
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    ux, uy = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
    t = 0.0
    while t < L:
        e = min(t + dash, L)
        d.line([(p0[0] + ux * t, p0[1] + uy * t), (p0[0] + ux * e, p0[1] + uy * e)], fill=color, width=w)
        t = e + gap


# ------------------------------------------------------------------ TV 스탠드
def tv_sketch(path):
    rng = random.Random(7)
    im, d = paper()
    # 조건 메모 (왼쪽, P01 스케치처럼)
    write(im, 165, 190, "방마다 굴려서 옮길래!", 40, INK, rng)
    write(im, 165, 270, "아이가 밀어도 안 넘어지게!", 40, INK, rng)
    write(im, 165, 365, "27인치 TV, 가로로", 34, GREY, rng)
    write(im, 165, 435, "- 앉아서 보는 높이", 32, GREY, rng)
    write(im, 165, 495, "- 높이 조절 · 화면 돌리기", 32, GREY, rng)
    write(im, 165, 555, "- 바퀴 달린 둥근 받침", 32, GREY, rng)
    # TV 화면 (가로, 621 × 361 비율)
    x0, y0, w = 860, 230, 520
    h = w * 361 / 621
    pen(d, [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h), (x0, y0)], INK, 6, rng)
    pen(d, [(x0 + 14, y0 + 14), (x0 + w - 14, y0 + 14), (x0 + w - 14, y0 + h - 14), (x0 + 14, y0 + h - 14), (x0 + 14, y0 + 14)], INK, 3, rng, twice=False)
    write(im, x0 + 150, y0 - 70, "27인치 (가로 화면)", 34, BLUE, rng)
    # 기둥 + 높이 조절
    cx = x0 + w / 2
    yb = 930
    pen(d, [(cx - 9, y0 + h), (cx - 9, yb)], INK, 5, rng)
    pen(d, [(cx + 9, y0 + h), (cx + 9, yb)], INK, 5, rng)
    arrow(d, (cx + 60, 700), (cx + 60, 600), BLUE, 3, rng)
    arrow(d, (cx + 60, 700), (cx + 60, 800), BLUE, 3, rng)
    write(im, cx + 85, 680, "높이 조절", 30, BLUE, rng)
    # 둥근 받침 + 바퀴 (정면에서 납작한 원)
    pen(d, ellipse(cx, yb + 10, 200, 42), INK, 5, rng)
    pen(d, ellipse(cx, yb + 24, 200, 42, 0, 180), INK, 3, rng, twice=False)
    for bx in (-150, -75, 0, 75, 150):
        pen(d, ellipse(cx + bx, yb + 78 - abs(bx) * 0.08, 13, 13), INK, 3, rng, twice=False)
    write(im, cx + 230, yb + 20, "바퀴 5개", 30, GREY, rng)
    pen(d, [(cx - 240, yb + 100), (cx + 240, yb + 100)], (180, 180, 180), 3, rng, twice=False)
    # 받침 모양은? (? 상자)
    pen(d, [(cx - 120, yb - 40), (cx + 120, yb - 40), (cx + 120, yb + 60), (cx - 120, yb + 60), (cx - 120, yb - 40)], RED, 3, rng, twice=False)
    write(im, cx - 18, yb - 32, "?", 44, RED, rng)
    write(im, cx - 360, yb - 120, "(받침 모양은?)", 32, RED, rng)
    # 미는 힘 화살표
    arrow(d, (x0 - 150, y0 + 250), (x0 - 18, y0 + 250), RED, 4, rng, 26)
    write(im, x0 - 165, y0 + 270, "밀어도?", 30, RED, rng)
    # 눈 → 화면 (앉아서 보는 높이)
    pen(d, ellipse(300, 975, 36, 36), BLUE, 4, rng)
    write(im, 220, 1030, "앉아서 보이게 (눈)", 30, BLUE, rng)
    dashed(d, (338, 958), (x0 - 20, y0 + h / 2 + 30), BLUE, 3)
    # 10° 기울여도? (흐린 기울인 윤곽)
    t = math.radians(10)
    piv = (cx + 200, yb + 52)
    def rot(p):
        dx, dy = p[0] - piv[0], p[1] - piv[1]
        return (piv[0] + dx * math.cos(t) - dy * math.sin(t), piv[1] + dx * math.sin(t) + dy * math.cos(t))
    ghost = [(x0 + w, y0), (x0 + w, y0 + h), (cx + 9, y0 + h), (cx + 9, yb)]
    for a, b in zip(ghost, ghost[1:]):
        dashed(d, rot(a), rot(b), (200, 200, 200), 2, 14, 10)
    write(im, x0 + w - 40, 610, "10° 기울여도?", 30, GREY, rng)
    im.save(path)


# ------------------------------------------------------------------ AI 글래스
def glasses_sketch(path):
    rng = random.Random(11)
    im, d = paper()
    write(im, 165, 190, "하루 종일 써도 가볍게!", 40, INK, rng)
    write(im, 165, 270, "안 흘러내리게!", 40, INK, rng)
    write(im, 165, 365, "관자놀이 안 뜨겁게", 34, GREY, rng)
    write(im, 165, 435, "- 두꺼운 검정 뿔테", 32, GREY, rng)
    write(im, 165, 495, "- 렌즈 50", 32, GREY, rng)
    write(im, 165, 555, "- 카메라 · 칩 · 배터리 넣기", 32, GREY, rng)
    # 정면: 두꺼운 스퀘어 뿔테 (윗선 곧고 아래 둥금)
    C = 1120
    write(im, C - 90, 110, "앞에서 본 모습", 28, GREY, rng)
    cy = 320
    for sx in (-1, 1):
        cxl = C + sx * 175
        outer = rrect(cxl - 150, cy - 112, cxl + 150, cy + 118, 34)
        inner = rrect(cxl - 118, cy - 82, cxl + 118, cy + 88, 26)
        pen(d, outer, INK, 6, rng)
        pen(d, inner, INK, 4, rng)
    # 브리지 (아치)
    pen(d, [(C - 26, cy - 70), (C, cy - 84), (C + 26, cy - 70)], INK, 6, rng)
    pen(d, [(C - 26, cy - 20), (C, cy - 44), (C + 26, cy - 20)], INK, 4, rng)
    # 카메라 (오른쪽 바깥 위) · LED (왼쪽)
    pen(d, ellipse(C + 175 + 112, cy - 92, 14, 14), INK, 4, rng, twice=False)
    arrow(d, (C + 175 + 200, cy - 190), (C + 175 + 126, cy - 104), RED, 3, rng)
    write(im, C + 175 + 120, cy - 245, "카메라", 32, RED, rng)
    pen(d, ellipse(C - 175 - 112, cy - 92, 7, 7), INK, 3, rng, twice=False)
    write(im, C - 175 - 150, cy - 175, "LED", 26, GREY, rng)
    write(im, C - 175 - 60, cy + 135, "렌즈 50", 30, BLUE, rng)
    pen(d, [(C - 175 - 118, cy + 125), (C - 175 + 118, cy + 125)], BLUE, 2, rng, twice=False)
    # 옆: 다리 (앞이 두껍고 뒤로 가늘어지며 귀에서 꺾임) + 칩 · 배터리 + 열
    write(im, 1150, 650, "옆에서 본 모습", 28, GREY, rng)
    y = 780
    top = [(700, y - 34), (1050, y - 30), (1300, y - 22), (1400, y - 18), (1470, y + 40)]
    bot = [(1455, y + 58), (1390, y + 4), (1300, y - 2), (1050, y + 2), (700, y + 6)]
    pen(d, top + bot + [top[0]], INK, 5, rng)
    pen(d, [(660, y - 60), (700, y - 60), (700, y + 40), (660, y + 40)], INK, 5, rng)       # 앞판 옆모습
    pen(d, [(730, y - 26), (960, y - 26), (960, y - 2), (730, y - 2), (730, y - 26)], RED, 3, rng, twice=False)
    write(im, 735, y + 30, "칩 · 배터리", 28, RED, rng)
    for k in range(3):                                                                          # 열
        xs = 790 + k * 60
        pen(d, [(xs + 8 * math.sin(i / 2), y - 50 - i * 6) for i in range(10)], RED, 2, rng, twice=False)
    write(im, 760, y - 165, "뜨거우면 안 돼", 28, RED, rng)
    # 귀 · 머리 쪽 조이는 힘
    pen(d, ellipse(1420, y + 120, 48, 70, 200, 520), GREY, 3, rng, twice=False)
    arrow(d, (1330, y + 160), (1390, y + 100), BLUE, 3, rng)
    write(im, 1150, y + 190, "적당히 조이게", 28, BLUE, rng)
    # 코 받침
    write(im, C - 70, cy + 200, "코에 걸치는 곳", 26, GREY, rng)
    arrow(d, (C + 10, cy + 195), (C + 10, cy - 10), GREY, 2, rng, 16)
    im.save(path)


if __name__ == "__main__":
    tv_sketch(os.path.join(HERE, "tv_sketch.png"))
    glasses_sketch(os.path.join(HERE, "glasses_sketch.png"))
    print("saved", os.path.join(HERE, "tv_sketch.png"), os.path.join(HERE, "glasses_sketch.png"))
