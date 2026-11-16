"""데모 입력 스케치 — 폰 거치대 · TV 스탠드 · AI 글래스. 그림 위주 + 꼭 필요한 글자 2–3개 (나머지 조건은 말로).

스케치는 GUI 그림판(800 × 600)의 '획' 그대로 저장 → GUI 가 예시를 고르면 이 획을 그림판에 그리고(영상 모드에서는 한 획씩
그려 가며), 서버는 같은 획을 그린 그림과 지문으로 비교해 데모 템플릿으로 보냄.

  python examples/demo/make_demo_sketches.py     → examples/demo/{bike,tv,glasses}.json + _sketch.png
"""
import json
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 800, 600
INK, BLUE, RED, GREY = "#262a33", "#2662a6", "#c8392e", "#9aa0a8"
FONTS = ("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
         "C:/Windows/Fonts/malgunbd.ttf", "C:/Windows/Fonts/malgun.ttf")


class Sketch:
    def __init__(self, seed):
        self.rng = random.Random(seed)
        self.strokes, self.labels = [], []

    def _dense(self, pts, step=5.0):
        out = [pts[0]]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            n = max(int(math.hypot(x1 - x0, y1 - y0) / step), 1)
            out += [(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n) for k in range(1, n + 1)]
        return out

    def line(self, pts, c=INK, w=3.5, amp=0.6, dense=True):
        """손으로 그린 선: 잘게 나눠 아주 조금 흔듦 (천천히 휘는 흔들림 + 작은 떨림)."""
        P = self._dense(pts) if dense else pts
        ph, a2 = self.rng.uniform(0, 6.3), self.rng.uniform(0.5, 1.2)
        q = [(x + amp * math.sin(i * 0.11 + ph) * a2 + self.rng.gauss(0, amp * 0.25),
              y + amp * math.cos(i * 0.09 + ph) * a2 + self.rng.gauss(0, amp * 0.25)) for i, (x, y) in enumerate(P)]
        self.strokes.append(dict(c=c, w=w, p=[[round(x, 1), round(y, 1)] for x, y in q]))

    def dashed(self, p0, p1, c=GREY, w=2.5, dash=14, gap=10):
        L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        ux, uy = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
        t = 0.0
        while t < L:
            e = min(t + dash, L)
            self.line([(p0[0] + ux * t, p0[1] + uy * t), (p0[0] + ux * e, p0[1] + uy * e)], c, w, 0.2)
            t = e + gap

    def arrow(self, p0, p1, c=RED, w=3, head=14):
        self.line([p0, p1], c, w, 0.4)
        a = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        self.line([(p1[0] - head * math.cos(a - 0.45), p1[1] - head * math.sin(a - 0.45)), p1,
                   (p1[0] - head * math.cos(a + 0.45), p1[1] - head * math.sin(a + 0.45))], c, w, 0.3)

    def ellipse(self, cx, cy, rx, ry, c=INK, w=3.5, a0=0, a1=360, n=72):
        self.line([(cx + rx * math.cos(math.radians(a)), cy + ry * math.sin(math.radians(a)))
                   for a in [a0 + (a1 - a0) * k / n for k in range(n + 1)]], c, w, 0.5, dense=False)

    def rrect(self, x0, y0, x1, y1, r, c=INK, w=3.5):
        pts = []
        for cx, cy, a in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
            pts += [(cx + r * math.cos(math.radians(a + 90 * k / 8)), cy + r * math.sin(math.radians(a + 90 * k / 8))) for k in range(9)]
        self.line(pts + [pts[0]], c, w)

    def rbox(self, cx, cy, w_, h_, deg, c=INK, w=3.5):
        t = math.radians(deg)
        pts = [(cx + x * math.cos(t) - y * math.sin(t), cy + x * math.sin(t) + y * math.cos(t))
               for x, y in ((-w_ / 2, -h_ / 2), (w_ / 2, -h_ / 2), (w_ / 2, h_ / 2), (-w_ / 2, h_ / 2), (-w_ / 2, -h_ / 2))]
        self.line(pts, c, w)

    def label(self, x, y, t, s=26, c=RED):
        self.labels.append(dict(x=x, y=y, t=t, s=s, c=c))

    def data(self):
        return dict(w=W, h=H, strokes=self.strokes, labels=self.labels)


def render(d, path=None):
    """GUI 그림판과 같은 방식으로 그림 (흰 바탕 · 둥근 끝 선 · 글자는 굵은 고딕)."""
    im = Image.new("RGB", (d["w"], d["h"]), "white")
    dr = ImageDraw.Draw(im)
    for s in d["strokes"]:
        p = [tuple(q) for q in s["p"]]
        dr.line(p, fill=s["c"], width=int(round(s["w"])), joint="curve")
        r = s["w"] / 2
        for x, y in (p[0], p[-1]):
            dr.ellipse((x - r, y - r, x + r, y + r), fill=s["c"])
    font = next((f for f in FONTS if os.path.exists(f)), None)
    for L in d["labels"]:
        f = ImageFont.truetype(font, L["s"]) if font else ImageFont.load_default()
        dr.text((L["x"], L["y"]), L["t"], font=f, fill=L["c"], anchor="ls")       # 왼쪽 · 글자 기준선 = canvas fillText
    if path:
        im.save(path)
    return im


# ------------------------------------------------------------------ 폰 거치대 (옆에서 본 자전거 + 핸들바 위 폰)
def bike():
    S = Sketch(3)
    for x in (190, 600):                                            # 바퀴
        S.ellipse(x, 440, 95, 95)
        S.ellipse(x, 440, 10, 10, w=3)
    BB, ST, HT, HB = (370, 455), (330, 300), (548, 292), (560, 345)
    for a, b in ((ST, BB), (ST, HT), (BB, HB), (HT, HB), (BB, (190, 440)), (ST, (190, 440)), (HB, (600, 440))):
        S.line([a, b])
    S.line([ST, (322, 268)]); S.line([(290, 266), (356, 262)], w=6)      # 안장
    S.line([HT, (578, 274)]); S.ellipse(584, 272, 9, 9, w=3.5)            # 스템 + 핸들바(옆에서 원)
    S.ellipse(370, 455, 18, 18, w=3)                                      # 크랭크
    S.line([(370, 455), (395, 490)], w=3)
    road = [(40 + i * 8, 548 + 7 * math.sin(i * 0.9) * (1 if i % 5 else 1.6)) for i in range(91)]   # 울퉁불퉁한 길
    S.line(road, GREY, 3)
    S.arrow((700, 410), (700, 360), RED, 3); S.arrow((700, 420), (700, 470), RED, 3)              # 흔들림
    S.dashed((574, 214), (646, 214), RED); S.dashed((646, 214), (646, 262), RED)                  # '?' 상자 = 설계 영역
    S.dashed((646, 262), (574, 262), RED); S.dashed((574, 262), (574, 214), RED)
    S.rbox(615, 176, 124, 14, -35, INK, 4.5)                                                       # 폰 (35°, 화면은 라이더 쪽)
    S.dashed((566, 207), (690, 207), GREY, 2)
    S.ellipse(566, 207, 62, 62, BLUE, 2.5, -35, 0, 16)
    S.ellipse(420, 108, 14, 14, BLUE, 3)                                                           # 눈 → 폰
    S.dashed((436, 114), (596, 170), BLUE, 2.5)
    S.label(600, 252, "?", 34, RED)
    S.label(660, 200, "35°", 24, BLUE)
    S.label(682, 160, "폰", 26, INK)
    return S.data()


# ------------------------------------------------------------------ TV 스탠드 (정면)
def tv():
    S = Sketch(7)
    x0, y0, w = 300, 60, 330
    h = w * 361 / 621
    S.line([(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h), (x0, y0)], INK, 4.5)
    S.line([(x0 + 10, y0 + 10), (x0 + w - 10, y0 + 10), (x0 + w - 10, y0 + h - 10), (x0 + 10, y0 + h - 10), (x0 + 10, y0 + 10)], INK, 2.5)
    cx, yb = x0 + w / 2, 505
    S.line([(cx - 7, y0 + h), (cx - 7, yb)], INK, 3.5); S.line([(cx + 7, y0 + h), (cx + 7, yb)], INK, 3.5)
    S.line([(cx - 22, 330), (cx + 22, 330), (cx + 22, 372), (cx - 22, 372), (cx - 22, 330)], INK, 3)   # 높이 조절 캐리지
    S.arrow((cx + 70, 360), (cx + 70, 300), BLUE, 3); S.arrow((cx + 70, 370), (cx + 70, 430), BLUE, 3)
    S.ellipse(cx, yb + 8, 125, 26)                                        # 둥근 받침 + 바퀴 5
    S.ellipse(cx, yb + 18, 125, 26, a0=0, a1=180, w=2.5)
    for bx in (-95, -48, 0, 48, 95):
        S.ellipse(cx + bx, yb + 56 - abs(bx) * 0.1, 9, 9, w=3)
    S.line([(cx - 170, yb + 70), (cx + 170, yb + 70)], GREY, 2.5)
    S.dashed((cx - 70, yb - 28), (cx + 70, yb - 28), RED); S.dashed((cx + 70, yb - 28), (cx + 70, yb + 44), RED)
    S.dashed((cx + 70, yb + 44), (cx - 70, yb + 44), RED); S.dashed((cx - 70, yb + 44), (cx - 70, yb - 28), RED)
    S.arrow((x0 - 110, y0 + 60), (x0 - 12, y0 + 60), RED, 4, 16)          # 아이가 미는 힘
    S.ellipse(120, 330, 16, 16, BLUE, 3)                                  # 앉은 눈높이 → 화면
    S.dashed((138, 322), (x0 - 10, y0 + h / 2 + 10), BLUE, 2.5)
    t, piv = math.radians(10), (cx + 125, yb + 60)                        # 10° 기울인 윤곽
    rot = lambda p: (piv[0] + (p[0] - piv[0]) * math.cos(t) - (p[1] - piv[1]) * math.sin(t),
                     piv[1] + (p[0] - piv[0]) * math.sin(t) + (p[1] - piv[1]) * math.cos(t))
    ghost = [(x0 + w, y0), (x0 + w, y0 + h), (cx + 7, y0 + h), (cx + 7, yb)]
    for a, b in zip(ghost, ghost[1:]):
        S.dashed(rot(a), rot(b), GREY, 2, 10, 8)
    S.label(x0 + w / 2 - 22, y0 - 14, "27\"", 26, BLUE)
    S.label(cx - 9, yb + 20, "?", 32, RED)
    S.label(x0 + w + 62, 300, "10°", 24, GREY)
    return S.data()


# ------------------------------------------------------------------ AI 글래스 (앞 + 옆)
def glasses():
    S = Sketch(11)
    C, cy = 400, 150
    for sx in (-1, 1):
        cl = C + sx * 112
        S.rrect(cl - 92, cy - 72, cl + 92, cy + 74, 22, INK, 4.5)
        S.rrect(cl - 72, cy - 52, cl + 72, cy + 56, 16, INK, 3)
    S.line([(C - 22, cy - 46), (C, cy - 56), (C + 22, cy - 46)], INK, 4.5)            # 브리지
    S.line([(C - 22, cy - 14), (C, cy - 30), (C + 22, cy - 14)], INK, 3)
    S.ellipse(C + 112 + 76, cy - 56, 8, 8, INK, 3)                                     # 카메라
    S.arrow((C + 112 + 150, cy - 108), (C + 112 + 88, cy - 64), RED, 3)
    S.ellipse(C - 112 - 76, cy - 56, 4, 4, INK, 2.5)                                    # LED
    S.line([(C - 112 - 72, cy + 92), (C - 112 + 72, cy + 92)], BLUE, 2.5)              # 렌즈 폭 치수
    for xx in (C - 112 - 72, C - 112 + 72):
        S.line([(xx, cy + 84), (xx, cy + 100)], BLUE, 2.5)
    y = 420                                                                             # 옆: 다리
    top = [(140, y - 22), (360, y - 20), (520, y - 14), (580, y - 11), (640, y + 32)]
    bot = [(630, y + 44), (574, y + 4), (520, y), (360, y + 2), (140, y + 4)]
    S.line(top + bot + [top[0]], INK, 4)
    S.line([(112, y - 44), (140, y - 44), (140, y + 26), (112, y + 26), (112, y - 44)], INK, 4)
    S.line([(160, y - 16), (300, y - 16), (300, y - 2), (160, y - 2), (160, y - 16)], RED, 3)   # 칩 · 배터리
    for k in range(3):                                                                  # 열
        xs = 190 + k * 42
        S.line([(xs + 6 * math.sin(i / 1.6), y - 32 - i * 5) for i in range(9)], RED, 2.5, 0.2)
    S.ellipse(626, y + 92, 34, 52, GREY, 3, 200, 520)                                    # 귀
    S.arrow((540, y + 120), (590, y + 70), BLUE, 3)                                     # 조이는 힘
    S.label(C - 112 - 14, cy + 128, "50", 24, BLUE)
    S.label(C + 112 + 112, cy - 112, "카메라", 22, RED)
    S.label(200, y + 40, "칩", 24, RED)
    return S.data()


if __name__ == "__main__":
    for name, fn in (("bike", bike), ("tv", tv), ("glasses", glasses)):
        d = fn()
        with open(os.path.join(HERE, f"{name}.json"), "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, separators=(",", ":"))
        render(d, os.path.join(HERE, f"{name}_sketch.png"))
        print(name, len(d["strokes"]), "획", sum(len(s["p"]) for s in d["strokes"]), "점", [L["t"] for L in d["labels"]])
