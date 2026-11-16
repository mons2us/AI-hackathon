"""헤더 오른쪽 위 'SAMSUNG Research' 표시 (남색 바탕 · 흰 글자 PNG). 공식 로고 파일이 있으면 같은 이름으로 바꿔 넣으면 됨:
app/static/brand/samsung_research.png (높이 30 px 로 표시, 3배 해상도 권장)."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
S = 3                                              # 3배 해상도 (화면 높이 30 px)
NAVY, WHITE = (20, 40, 160), (255, 255, 255)
B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
Rg = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
f1, f2 = ImageFont.truetype(B, 15 * S), ImageFont.truetype(Rg, 15 * S)
t1, t2 = "SAMSUNG", "Research"
sp = 1.6 * S                                       # 자간 (SAMSUNG 은 넓게)
w1 = sum(f1.getlength(c) for c in t1) + sp * (len(t1) - 1)
w2 = f2.getlength(t2)
pad, gap, H = 14 * S, 8 * S, 30 * S
W = int(pad * 2 + w1 + gap + w2)
im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
d.rounded_rectangle((0, 0, W - 1, H - 1), radius=8 * S, fill=NAVY)
x, y = pad, H / 2
for c in t1:
    d.text((x, y), c, font=f1, fill=WHITE, anchor="lm")
    x += f1.getlength(c) + sp
d.text((x - sp + gap, y), t2, font=f2, fill=WHITE, anchor="lm")
im.save(os.path.join(HERE, "samsung_research.png"))
print(W // S, "x", H // S)
