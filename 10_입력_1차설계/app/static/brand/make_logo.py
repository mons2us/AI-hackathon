"""헤더 오른쪽 위 Samsung Research 표시: 공식 사이트(research.samsung.com) 헤더 로고 그대로, 글자만 흰색 · 바탕 투명.

원본: https://cdn.codeground.org/nsr/images/layout/logo-sr.png (250 × 26 px, 검정 글자 · 투명 바탕, 글자 테두리는 반투명)
→ 색만 흰색으로 바꾸고 알파(글자 모양 · 테두리 부드러움)는 그대로 둠. 화면에는 원본 크기(높이 26 px)로 표시.

  python app/static/brand/make_logo.py <받은 logo-sr.png>     → app/static/brand/samsung_research.png
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "logo-sr.png")
a = np.array(Image.open(src).convert("RGBA"))
a[..., :3] = 255                                   # 글자 = 흰색, 바탕은 원래대로 투명 (알파 그대로)
Image.fromarray(a).save(os.path.join(HERE, "samsung_research.png"))
print(a.shape[1], "x", a.shape[0], "흰 글자 · 투명 바탕")
