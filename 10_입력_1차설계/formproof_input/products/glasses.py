"""AR(AI) 글래스 — 제품 사진 → 렌즈 윤곽 · 테 치수 추출 → 1차 설계(CAD · 도면) + 물리 조건 + 간이 판정 (데모 시나리오).

대상: 젠틀몬스터 × Google × 삼성 AI 글래스 (Android XR, 디스플레이 없음, 카메라 · 스피커 · 마이크).
사진 분석: 배경 대비 테(어두운 영역) 검출 → 테 안쪽 구멍 = 렌즈 2개 → 좌우 렌즈 윤곽 평균(r(θ)) → mm 환산
(렌즈 폭 기준, 기본 50 mm = 가정, 텍스트 '렌즈 52' 로 바꿈) → 브리지 · 림 두께 · 엔드피스 폭.
좌표 (mm): x = 좌우(착용자 기준 아님, 사진 오른쪽 = +x), y = 앞→뒤(앞면 y = 0, 다리는 +y), z = 위.
물리 조건: 무게(보도 41–50 g), 착용 클램프 힘(문헌 0–1 N 대), 브리지 누름(양쪽 힌지 고정 · 가운데 5 N, ISO 12870 브리지 변형과 같은 부위, 하중 가정),
다리 피부 접촉 온도 ≤ 43 °C(IEC 62368-1 TS1 장시간 접촉, ISO 13732-1 근거). 판정: 응력 · 힘 = 복셀 FEM, 온도 = 집중 열저항.
"""
import math
import os
import re
import tempfile
import time

import numpy as np
from scipy import ndimage

from .. import progress

SOURCES = {
    "weight41": dict(title="SammyGuru 보도: 표준 렌즈 기준 약 41 g, 이전 보도 46–50 g, Snapdragon AR1 Gen 1, 12 MP, 스피커 2 · 마이크 4",
                     url="https://ppc.land/samsung-smart-glasses-weigh-41g-in-leak-down-from-a-reported-50g/"),
    "unpacked": dict(title="Samsung Newsroom: Galaxy Unpacked(런던) 지능형 아이웨어 — Gentle Monster · Warby Parker 와 개발, Snapdragon AR1 Gen1",
                     url="https://news.samsung.com/us/?p=86825"),
    "battery": dict(title="idevice 정리: 155 mAh 배터리, 약 50 g (초기 사양 유출)",
                    url="https://idevice.com/smart-glasses/samsung-galaxy-glasses/roadmap?view=faq"),
    "clamp": dict(title="Zhang et al. (AHFE 2023): 안경 다리 클램프 힘은 매우 작음(0.0–1.0 N), 다리 높이 1–6 mm",
                  url="https://openaccess.cms-conferences.org/publications/book/978-1-958651-50-6/article/978-1-958651-50-6_6"),
    "clamp_patent": dict(title="US 특허 'Eyewear having a flexural member': 머리 폭 130–180 mm 에서 접촉 힘 약 50–110 g 이 편안한 범위",
                         url="https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/9798161"),
    "iso12870": dict(title="ISO 12870 (안경테 요구사항 · 시험): 브리지 변형 · 내구 시험 항목 (목차)",
                     url="https://www.din.de/de/mitwirken/normenausschuesse/nafuo/veroeffentlichungen/wdc-beuth:din21:288874441/toc-2857598/download"),
    "touch": dict(title="IEC 62368-1 접촉 온도 한계(TS1)는 ISO 13732-1 기반 — 장시간(8 h 이상) 접촉 43 °C",
                  url="https://incompliancemag.com/"),
}
MAT = dict(name="아세테이트 (셀룰로오스 아세테이트)", E=2000.0, nu=0.38, rho=1.29e-3, yield_mpa=40.0)
SF = 1.5
LENS_W_DEFAULT = 50.0
FRAME_DEPTH = 5.0              # 테 앞뒤 두께
TEMPLE_LEN = 145.0             # 다리 길이 (앞면 → 귀 끝)
SPREAD_EACH = 5.0              # 착용 시 다리 끝이 바깥으로 벌어지는 양 (한쪽, 가정: 머리 폭 ≈ 테 폭 + 10 mm)
CLAMP_RANGE = (0.3, 1.1)       # N, 한쪽 — 문헌(0–1 N 대) · 특허(50–110 g) 기반 권장 범위 (하한은 가정)
BRIDGE_F = 5.0                 # N, 브리지 누름 하중 (가정: 손가락으로 브리지를 밀어 올림, ISO 12870 브리지 변형과 같은 부위 · 수치 미확인)
SOC_W = 0.5                    # W, 촬영 · AI 지속 사용 시 평균 소비 (가정)
TEMPLE_T = 6.5                 # 1차 설계 다리 두께 (일반 아세테이트 뿔테 수준, 최적화 전) — 얇게 하는 것은 다음 단계
RIM_EXTRA = 1.0                # 1차 설계 림 = 템플릿 림 + 1 mm (뿔테 두께)
LENS_WIDTHS = (48.0, 50.0, 52.0)   # 템플릿 렌즈 폭 (mm)
H_CONV = 10.0                  # W/m²K, 자연대류 + 복사 (일반값)
T_AMB = 25.0
T_SKIN_LIMIT = 43.0
MASS_LIMIT = 50.0
PARTS_G = dict(board_camera=6.0, battery=4.0, speakers_mics=3.0, wiring_hinges=2.0)   # 전자부품 (가정, 155 mAh 배터리 기준)
LENS_RHO = 1.32e-3             # CR-39 g/mm³
LENS_T = 2.0

STYLES = {   # 사진이 없을 때 · 합성 사진용 기본 형상 (보도 사진 묘사 기반)
    "slim_oval": dict(name="슬림 오벌 (윗선 직선 · 아래 둥근)", w=50.0, h=33.0, p_top=6.0, p_bot=2.3, lift=0.0, rim=4.0,
                      note="공개된 젠틀몬스터 협업 최종 디자인: 얇은 검정 테, 윗선이 곧고 아래가 둥근 형태"),
    "cat_eye": dict(name="캣아이", w=52.0, h=40.0, p_top=3.0, p_bot=2.2, lift=0.30, rim=5.0,
                    note="초기 공개(구글 I/O) 젠틀몬스터 디자인: 바깥 윗모서리가 올라간 캣아이"),
    # 공식 제품 사진 (examples/glasses/젠틀몬스터_구글_삼성_AI글래스.jpg) 에서 본 형상: 검정 아세테이트 두꺼운 스퀘어 뿔테,
    # 윗선 곧고 아래로 조금 좁아지는 렌즈, 코 쪽 위 모서리 둥금, 굵은 브리지, 오른쪽 테 바깥 위 카메라 · 왼쪽 LED, 넓고 납작한 다리
    "gm": dict(name="스퀘어 뿔테 (젠틀몬스터 × Google × 삼성)", w=50.0, h=41.0, shape="rrect", r_to=4.0, r_ti=10.0, r_bo=15.0, r_bi=13.0,
               taper=0.06, rim=6.5, rim_t=7.5, rim_o=6.5, rim_b=5.5, rim_n=4.0, r_out_to=2.5, r_out_ti=9.0,
               depth=7.0, bridge=21.0, bridge_dip=5.0, bridge_h=7.0, endpiece=6.5, bevel=(1.0, 0.7),
               temple=dict(t=5.5, h0=15.5, h40=14.5, h80=11.0, drop80=1.0, bend_y=118.0, drop_b=2.8, h_b=8.6, bend_deg=32.0, tip_len=26.0, tip_h=7.5),
               note="공식 사진 디자인: 두꺼운 검정 스퀘어 뿔테(모서리 둥글게 깎임), 브로우보다 낮은 아치형 브리지, 오른쪽 테 바깥 위 카메라 · 왼쪽 LED, "
                    "앞이 높고 뒤로 가늘어지며 귀 쪽에서 꺾이는 넓은 다리(전자부품 내장)"),
}


# ------------------------------------------------------------------ lens shapes
def lens_outline(style="slim_oval", w=None, h=None, n=160):
    """Lens contour for the +x lens, centred at (0, 0), x outward (to the temple), z up. Returns (n, 2) mm."""
    S = STYLES[style]
    w = w or S["w"]
    h = h or S["h"]
    a, b = w / 2, h / 2
    if S.get("shape") == "rrect":                    # 모서리마다 반지름이 다른 둥근 사각 + 아래로 좁아짐
        def arc(cx_, cz, r, a0, a1, k=14):
            t_ = np.linspace(a0, a1, k)
            return np.c_[cx_ + r * np.cos(t_), cz + r * np.sin(t_)]
        P = np.vstack([arc(a - S["r_to"], b - S["r_to"], S["r_to"], 0, np.pi / 2),                     # 바깥 위
                       arc(-a + S["r_ti"], b - S["r_ti"], S["r_ti"], np.pi / 2, np.pi),                # 코 쪽 위
                       arc(-a + S["r_bi"], -b + S["r_bi"], S["r_bi"], np.pi, 1.5 * np.pi),           # 코 쪽 아래
                       arc(a - S["r_bo"], -b + S["r_bo"], S["r_bo"], 1.5 * np.pi, 2 * np.pi)])       # 바깥 아래
        P[:, 0] *= 1 - S["taper"] * np.clip(-P[:, 1] / b, 0, 1)
        return P
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    c, s = np.cos(t), np.sin(t)
    p = np.where(s >= 0, S["p_top"], S["p_bot"])
    x = a * np.sign(c) * np.abs(c) ** (2 / p)
    z = b * np.sign(s) * np.abs(s) ** (2 / p)
    if S["lift"]:
        up = s > 0
        z[up] += S["lift"] * b * (((x[up] / a) + 1) / 2) ** 3 - 0.08 * b * (1 - (x[up] / a + 1) / 2)
    return np.c_[x, z]


def radial(poly, n=180):
    """Star-shaped closed polygon -> r(θ) about its centroid (for averaging the two lenses)."""
    P = np.asarray(poly, float)
    c = P.mean(0)
    d = P - c
    ang = np.mod(np.arctan2(d[:, 1], d[:, 0]), 2 * np.pi)
    r = np.hypot(d[:, 0], d[:, 1])
    o = np.argsort(ang)
    ang, r = ang[o], r[o]
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    rr = np.interp(th, np.r_[ang - 2 * np.pi, ang, ang + 2 * np.pi], np.r_[r, r, r])
    return th, rr, c


def from_radial(th, r):
    return np.c_[r * np.cos(th), r * np.sin(th)]


# ------------------------------------------------------------------ photo analysis
def _to_gray(img):
    a = np.asarray(img, float)
    if a.ndim == 3:
        a = a[..., :3] @ [0.299, 0.587, 0.114]
    if a.max() > 1.5:
        a = a / 255.0
    return a


def analyze_photo(img, lens_w=LENS_W_DEFAULT, debug=False):
    """Front-view product photo -> lens contour (mm) and frame dimensions. None if no glasses-like layout is found."""
    from skimage import filters, measure, morphology
    g = _to_gray(img)
    H0, W0 = g.shape
    sc = 900.0 / max(H0, W0)
    if sc < 1:
        g = ndimage.zoom(g, sc, order=1)
    border = np.r_[g[0], g[-1], g[:, 0], g[:, -1]]
    bg = float(np.median(border))
    diff = np.abs(g - bg)
    diff = ndimage.gaussian_filter(diff, 1.0)
    thr = max(filters.threshold_otsu(diff), 0.12)
    ink = diff > thr
    ink = ndimage.binary_closing(ink, morphology.disk(3))
    lab0 = measure.label(ink)
    ink = np.isin(lab0, [p.label for p in measure.regionprops(lab0) if p.area >= 200])
    lab = measure.label(ink)
    if lab.max() == 0:
        return None
    big = max(measure.regionprops(lab), key=lambda r: r.area)
    frame = lab == big.label
    r0, c0, r1, c1 = big.bbox
    sil = ndimage.binary_fill_holes(frame)
    holes = sil & ~frame
    hl = measure.label(holes)
    props = sorted([p for p in measure.regionprops(hl) if p.area > 0.01 * sil.sum()], key=lambda p: -p.area)
    mode = "holes"
    if len(props) >= 2:
        A, B = props[0], props[1]
        lenses = sorted([A, B], key=lambda p: p.centroid[1])
        masks = [hl == p.label for p in lenses]
    else:                                                     # dark lenses: no holes -> split the silhouette in two lobes
        mode = "silhouette"
        cols = sil.sum(0)
        mid = (c0 + c1) // 2
        win = slice(mid - (c1 - c0) // 8, mid + (c1 - c0) // 8)
        cut = win.start + int(np.argmin(cols[win]))
        rim_px = max(2, int(0.028 * (c1 - c0)))
        hgt = r1 - r0
        masks = []
        for side in (slice(0, cut), slice(cut, sil.shape[1])):
            m = np.zeros_like(sil)
            m[:, side] = sil[:, side]
            m = ndimage.binary_opening(m, morphology.disk(max(3, int(0.22 * hgt))))   # drop endpiece / bridge stubs
            m = ndimage.binary_erosion(m, morphology.disk(rim_px))
            lb = measure.label(m)
            if lb.max() == 0:
                return None
            p = max(measure.regionprops(lb), key=lambda r: r.area)
            masks.append(lb == p.label)
        lenses = [measure.regionprops(m.astype(int))[0] for m in masks]
    a0, a1 = lenses[0].area, lenses[1].area
    (y0, x0), (y1, x1) = lenses[0].centroid, lenses[1].centroid
    lw_px = np.mean([p.bbox[3] - p.bbox[1] for p in lenses])
    lh_px = np.mean([p.bbox[2] - p.bbox[0] for p in lenses])
    gap = lenses[1].bbox[1] - lenses[0].bbox[3]
    stats = dict(area_ratio=min(a0, a1) / max(a0, a1), dy=abs(y0 - y1) / lh_px, gap=gap / lw_px,
                 sil_aspect=(c1 - c0) / max(r1 - r0, 1), lens_aspect=lh_px / lw_px,
                 hole_frac=(a0 + a1) / sil.sum(), lens_h_frac=lh_px / max(r1 - r0, 1), lens_w_frac=2 * lw_px / max(c1 - c0, 1))
    ok = (stats["area_ratio"] > 0.75 and stats["dy"] < 0.15 and 0.12 < stats["gap"] < 0.6
          and 2.0 < stats["sil_aspect"] < 5.0 and 0.4 < stats["lens_aspect"] < 1.05
          and stats["hole_frac"] > 0.4 and stats["lens_h_frac"] > 0.65 and stats["lens_w_frac"] > 0.6)
    if debug:
        return stats
    if not ok:
        return None
    s = lens_w / lw_px                                         # mm per px
    tilt = math.atan2(-(y1 - y0), x1 - x0)                     # photo roll from the two lens centres
    R = np.array([[math.cos(-tilt), -math.sin(-tilt)], [math.sin(-tilt), math.cos(-tilt)]])
    contours, raw = [], []
    for k, m in enumerate(masks):
        cs = measure.find_contours(np.pad(m, 1).astype(float), 0.5)
        C = max(cs, key=len) - 1
        raw.append((np.c_[C[:, 1], C[:, 0]] / (sc if sc < 1 else 1.0))[::2].round(1).tolist())
        P = np.c_[C[:, 1], -C[:, 0]] * s                      # (x, z) mm, z up
        P = (P - P.mean(0)) @ R.T                              # level the photo
        if k == 0:                                             # image-left lens -> mirror to the +x lens frame
            P[:, 0] = -P[:, 0]
        contours.append(P)
    th, ra, _ = radial(contours[0])
    _, rb, _ = radial(contours[1])
    r = ndimage.gaussian_filter1d(0.5 * (ra + rb), 1.5, mode="wrap")
    lens = from_radial(th, r)
    lens -= (lens.max(0) + lens.min(0)) / 2
    # frame dimensions
    bridge = (lenses[1].bbox[1] - lenses[0].bbox[3]) * s
    ccol = int(round(x1))
    col = sil[:, ccol]
    rows = np.where(col)[0]
    lens_rows = np.where(masks[1][:, ccol])[0]
    rim_top = (lens_rows.min() - rows.min()) * s if len(rows) and len(lens_rows) else 4.0
    rim_bot = (rows.max() - lens_rows.max()) * s if len(rows) and len(lens_rows) else 4.0
    total = (c1 - c0) * s
    rim = float(np.clip(np.median([rim_top, rim_bot]), 2.0, 7.0))
    endw = float(np.clip((total - 2 * lens_w - bridge) / 2 - rim, 3.0, 14.0))
    desc = describe(lens)
    return dict(mode=mode, lens=lens, lens_w=float(np.ptp(lens[:, 0])), lens_h=float(np.ptp(lens[:, 1])),
                bridge=float(np.clip(bridge, 12.0, 24.0)), bridge_raw=float(bridge), rim=rim, rim_top=float(rim_top), rim_bot=float(rim_bot),
                endpiece=endw, total_w=float(total), mm_per_px=float(s / sc if sc < 1 else s), style=desc["style"], features=desc,
                roll_deg=round(math.degrees(tilt), 2),
                px=dict(frame_bbox=[int(c0 / sc if sc < 1 else c0), int(r0 / sc if sc < 1 else r0), int(c1 / sc if sc < 1 else c1), int(r1 / sc if sc < 1 else r1)],
                        contours=raw))


def describe(lens):
    """Shape descriptors: aspect, top-line flatness, outer-top lift (cat-eye)."""
    x, z = lens[:, 0], lens[:, 1]
    w, h = np.ptp(x), np.ptp(z)
    top = z.max()
    up = z > 0
    xs = x[up]
    zs = z[up]
    flat = float(np.mean(np.abs(zs - top) < 0.06 * h) * np.ptp(xs[np.abs(zs - top) < 0.06 * h] if np.any(np.abs(zs - top) < 0.06 * h) else [0]) / w) if up.any() else 0.0
    band = lambda lo, hi: zs[(xs >= lo * w / 2) & (xs <= hi * w / 2)]
    outer, inner = band(0.4, 0.8), band(-0.8, -0.4)
    lift = float((outer.max() - inner.max()) / h) if len(outer) and len(inner) else 0.0
    style = "cat_eye" if lift > 0.04 else "slim_oval"
    return dict(aspect=round(float(h / w), 3), top_flat=round(flat, 3), outer_lift=round(lift, 3), style=style,
                style_name=STYLES[style]["name"])


def is_glasses_image(img):
    try:
        return analyze_photo(img) is not None
    except Exception:
        return False


# ------------------------------------------------------------------ synthetic product photo (demo / tests)
def render_photo(style="slim_oval", px=1200, seed=0, dark_lens=False, tilt_deg=1.5):
    """Studio-like front photo of the frame (gradient backdrop, glossy black acetate, light lenses, shadow, noise).
    Stands in for the real product photo, which cannot be downloaded here."""
    from PIL import Image, ImageDraw, ImageFilter
    rng = np.random.default_rng(seed)
    S = STYLES[style]
    lens = lens_outline(style)
    bridge, rim, endw = 18.0, S["rim"], 7.0
    cx = bridge / 2 + S["w"] / 2
    W_mm = 2 * (cx + S["w"] / 2 + rim + endw) + 30
    k = px / W_mm
    Hpx = int(px * 0.5)
    to_px = lambda P: [(px / 2 + x * k, Hpx * 0.48 - z * k) for x, z in P]
    yy = np.linspace(0, 1, Hpx)[:, None]
    bgimg = (0.97 - 0.07 * yy + 0.02 * np.linspace(-1, 1, px)[None, :] ** 2) * 255
    im = Image.fromarray(np.dstack([bgimg] * 3).astype(np.uint8))
    sh = Image.new("L", im.size, 0)
    ImageDraw.Draw(sh).ellipse([px * 0.18, Hpx * 0.80, px * 0.82, Hpx * 0.90], fill=90)
    sh = sh.filter(ImageFilter.GaussianBlur(px / 60))
    im = Image.composite(Image.new("RGB", im.size, (120, 120, 125)), im, sh)
    d = ImageDraw.Draw(im)
    outer = offset_poly(lens, rim)
    frame_col = (22, 22, 24)
    for sx in (-1, 1):
        P = lens * [sx, 1] + [sx * cx, 0]
        O = outer * [sx, 1] + [sx * cx, 0]
        d.polygon(to_px(O), fill=frame_col)
        top = O[:, 1].max()
        e0 = sx * (cx + S["w"] / 2 + rim - 2)
        e1 = sx * (cx + S["w"] / 2 + rim + endw)
        d.polygon(to_px([(e0, top), (e1, top - 1), (e1, top - 13), (e0, top - 15)]), fill=frame_col)
        d.polygon(to_px([(e1, top - 2), (e1 + sx * 6, top - 3), (e1 + sx * 6, top - 10), (e1, top - 11)]), fill=(35, 35, 38))
    top = outer[:, 1].max()
    zb = bridge_top(outer, S["w"])
    d.polygon(to_px([(-cx + 10, zb), (cx - 10, zb), (cx - 10, zb - 5.5), (-cx + 10, zb - 5.5)]), fill=frame_col)
    lens_col = (40, 44, 48) if dark_lens else (226, 232, 236)
    for sx in (-1, 1):
        P = lens * [sx, 1] + [sx * cx, 0]
        d.polygon(to_px(P), fill=lens_col)
    cam_x = cx + S["w"] / 2 + rim + endw / 2
    cz = top - 7
    d.ellipse([px / 2 + (cam_x - 2.2) * k, Hpx * 0.48 - (cz + 2.2) * k, px / 2 + (cam_x + 2.2) * k, Hpx * 0.48 - (cz - 2.2) * k], fill=(70, 72, 80))
    d.ellipse([px / 2 + (cam_x - 1.0) * k, Hpx * 0.48 - (cz + 1.0) * k, px / 2 + (cam_x + 1.0) * k, Hpx * 0.48 - (cz - 1.0) * k], fill=(10, 10, 14))
    hl = Image.new("L", im.size, 0)                          # glossy highlights on frame and lenses
    hd = ImageDraw.Draw(hl)
    for sx in (-1, 1):
        x = sx * cx
        hd.line([(px / 2 + (x - 14) * k, Hpx * 0.48 - 10 * k), (px / 2 + (x + 6) * k, Hpx * 0.48 + 8 * k)], fill=110, width=int(3 * k))
        hd.line([(px / 2 + (x - 20) * k, Hpx * 0.48 - (top - 1.5) * k), (px / 2 + (x + 8) * k, Hpx * 0.48 - (top - 1.2) * k)], fill=70, width=max(2, int(0.8 * k)))
    hl = hl.filter(ImageFilter.GaussianBlur(k * 0.6))
    im = Image.composite(Image.new("RGB", im.size, (255, 255, 255)), im, hl)
    im = im.rotate(tilt_deg, resample=Image.BICUBIC, fillcolor=tuple(int(v) for v in bgimg[0, 0].repeat(3)))
    a = np.asarray(im, float)
    a += rng.normal(0, 2.5, a.shape)
    return np.clip(a, 0, 255).astype(np.uint8)


def offset_poly(P, d, n=None):
    """Outward offset of a closed (x, z) polygon (radial-ish via normals, smoothed)."""
    P = np.asarray(P, float)
    T = np.roll(P, -1, 0) - np.roll(P, 1, 0)
    N = np.c_[T[:, 1], -T[:, 0]]
    N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-12
    c = P.mean(0)
    if np.mean(np.sum((P - c) * N, 1)) < 0:
        N = -N
    return P + d * N


# ------------------------------------------------------------------ CAD
GM_VERSION = "2"               # 사진형 뿔테(gm) 형상 · 브리지 대칭 하중 — 바꾸면 글래스 템플릿 결과만 다시 계산


def _rrect(xl, xr, zb, zt, r_tl, r_tr, r_bl, r_br, k=24):
    def arc(cx_, cz, r, a0, a1):
        t_ = np.linspace(a0, a1, k)
        return np.c_[cx_ + r * np.cos(t_), cz + r * np.sin(t_)]
    return np.vstack([arc(xr - r_tr, zt - r_tr, r_tr, 0, np.pi / 2), arc(xl + r_tl, zt - r_tl, r_tl, np.pi / 2, np.pi),
                      arc(xl + r_bl, zb + r_bl, r_bl, np.pi, 1.5 * np.pi), arc(xr - r_br, zb + r_br, r_br, 1.5 * np.pi, 2 * np.pi)])


def _taper(P, b, t):
    P = np.array(P, float)
    P[:, 0] *= 1 - t * np.clip(-P[:, 1] / b, 0, 1)
    return P


def _resample(C, step):
    """Closed curve -> points every `step` mm."""
    C = np.vstack([C, C[:1]])
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(C, axis=0).T))]
    s = np.linspace(0, d[-1], max(int(d[-1] / step), 8), endpoint=False)
    return np.c_[np.interp(s, d, C[:, 0]), np.interp(s, d, C[:, 1])]


def _smooth(C, sigma):
    return np.c_[ndimage.gaussian_filter1d(C[:, 0], sigma, mode="wrap"), ndimage.gaussian_filter1d(C[:, 1], sigma, mode="wrap")]


def _union_outline(polys, res=0.05, pad=2.0):
    """2D union of closed polygons (raster 0.05 mm, x-symmetric grid) -> outer contour."""
    from PIL import Image, ImageDraw
    from skimage import measure
    allp = np.vstack(polys)
    xm = float(np.abs(allp[:, 0]).max()) + pad
    z0, z1 = float(allp[:, 1].min()) - pad, float(allp[:, 1].max()) + pad
    W, H = 2 * int(xm / res) + 1, int((z1 - z0) / res) + 1
    x0 = -(W // 2) * res
    im = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(im)
    for P in polys:                                      # PIL 래스터 (skimage.draw.polygon 보다 ~100배 빠름)
        dr.polygon([(float(x), float(z)) for x, z in np.c_[(P[:, 0] - x0) / res, (P[:, 1] - z0) / res]], fill=255)
    C = max(measure.find_contours(np.asarray(im, float), 127.5), key=len)
    return np.c_[C[:, 1] * res + x0, C[:, 0] * res + z0]


def _mirror_closed(C, step):
    """Closed outline crossing x = 0 twice -> exactly x-symmetric outline (right half, resampled, + its mirror)."""
    C = C[:-1] if np.allclose(C[0], C[-1]) else C
    s = np.sign(C[:, 0])
    i = np.where((s[:-1] <= 0) & (s[1:] > 0) | (s[:-1] > 0) & (s[1:] <= 0))[0]
    zc = C[i, 1]
    a, b_ = int(i[np.argmax(zc)]), int(i[np.argmin(zc)])            # top and bottom crossings
    R = np.roll(C, -a - 1, 0)
    n = (b_ - a) % len(C)
    half = R[:n] if R[: n, 0].mean() > 0 else np.roll(C, -b_ - 1, 0)[: len(C) - n][::-1]
    zt, zb = float(C[a, 1]), float(C[b_, 1])
    if half[0, 1] < half[-1, 1]:
        half = half[::-1]
    H = np.vstack([[0.0, zt], half, [0.0, zb]])                     # 위 중심 → 오른쪽 반 → 아래 중심
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(H, axis=0).T))]
    m = max(int(d[-1] / step), 8)
    sp = np.linspace(0, d[-1], m + 1)
    H = np.c_[np.interp(sp, d, H[:, 0]), np.interp(sp, d, H[:, 1])]
    H[0, 0] = H[-1, 0] = 0.0
    return np.vstack([H[:-1], (H[1:] * [-1, 1])[::-1]])             # 닫힌 곡선 (중심점 한 번씩)


def _offset_in(P, d):
    T = np.roll(P, -1, 0) - np.roll(P, 1, 0)
    N = np.c_[T[:, 1], -T[:, 0]]
    N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-12
    if np.mean(np.sum((P - P.mean(0)) * N, 1)) < 0:
        N = -N
    return P - d * N


def _loft(P, layers, to3):
    """Ruled loft through insets of the (u, v) polygon P at given layers [(w, inset)] -> one solid with bevelled edges.
    (다각형 와이어 — 주기 스플라인 로프트는 불리언이 부피를 잃어 쓰지 않음)"""
    import cadquery as cq
    ws = [cq.Wire.makePolygon([cq.Vector(*to3(w, u, v)) for u, v in (_offset_in(P, d) if d else P)], close=True) for w, d in layers]
    return cq.Workplane().add(cq.Solid.makeLoft(ws, True))


def gm_front_outline(S, lens, cx):
    """앞판 윤곽 (x, z): 좌우 테 바깥 + 아치형 브리지의 합 — 매끈하게, 정확히 좌우 대칭."""
    lw, lh = S["w"], S["h"]
    a, b = lw / 2, lh / 2
    bo = b + S["rim_b"]
    outer = _taper(_rrect(-a - S["rim_n"], a + S["rim_o"], -bo, b + S["rim_t"], S["r_out_ti"], S["r_out_to"], S["r_bi"] + S["rim_b"],
                          S["r_bo"] + S["rim_b"]), bo, S["taper"])
    top = b + S["rim_t"]
    xb = S["bridge"] / 2 + 4.0
    xs = np.linspace(-xb, xb, 41)
    zt = top - S["bridge_dip"]
    zb = zt - S["bridge_h"] - 8.0 * (xs / xb) ** 2                 # 아래는 아치 (코 자리)
    bridge = np.r_[np.c_[xs, np.full_like(xs, zt)], np.c_[xs[::-1], zb[::-1]]]
    C = _smooth(_resample(_union_outline([outer + [cx, 0], outer * [-1, 1] + [-cx, 0], bridge]), 1.2), 1.4)
    return _mirror_closed(C, 1.2), top


def gm_temple_profile(tp, D, top):
    """다리 옆 윤곽 (y, z): 힌지 쪽 높고 뒤로 가늘어지며 귀 쪽에서 아래로 꺾임."""
    y0 = D - 3.5
    yb, ang = tp["bend_y"], math.radians(tp["bend_deg"])
    d = np.array([math.cos(ang), -math.sin(ang)])
    nrm = np.array([math.sin(ang), math.cos(ang)])
    pb = np.array([yb, top - tp["drop_b"]])
    p_end = pb + tp["tip_len"] * d
    q_end = p_end - tp["tip_h"] * nrm
    P = np.array([(y0, top), (40.0, top), (80.0, top - tp["drop80"]), tuple(pb), tuple(p_end), tuple(q_end),
                  (yb - 4.0, top - tp["drop_b"] - tp["h_b"]), (80.0, top - tp["drop80"] - tp["h80"]), (40.0, top - tp["h40"]), (y0, top - tp["h0"])])
    return _smooth(_resample(P, 1.2), 1.4), float(p_end[0])


def build_gm(geo):
    """공식 사진형 뿔테: 앞판(테 + 아치 브리지) 하나의 매끈한 윤곽 → 모서리 깎인 판, 렌즈 구멍도 앞뒤 모서리 깎음,
    다리 = 옆 윤곽(앞 높고 뒤로 가늘어짐, 귀 쪽 꺾임) 판, 카메라 링(오른쪽 바깥 위) · LED(왼쪽) · 코받침. 좌우 정확히 대칭(카메라 · LED 제외)."""
    import cadquery as cq
    S = STYLES["gm"]
    lens = geo["lens"]
    lw, lh = geo["lens_w"], geo["lens_h"]
    a, b = float(lens[:, 0].max()), float(lens[:, 1].max())
    cx = geo["bridge"] / 2 + a
    D = geo["depth"]
    bf, bb = S["bevel"]
    C, top = geo["front"], geo["top"]
    body = _loft(C, [(0.0, bf), (bf, 0.0), (D - bb, 0.0), (D, bb)], lambda y, x, z: (float(x), y, float(z)))
    for sx in (-1, 1):
        L = lens * [sx, 1] + [sx * cx, 0]
        body = body.cut(_loft(L, [(-0.01, -bf), (bf, 0.0), (D - bb, 0.0), (D + 0.01, -bb)], lambda y, x, z: (float(x), y, float(z))))
    tp = geo["temple"]
    x_o = float(C[:, 0].max()) - 0.2
    P, y_end = gm_temple_profile(tp, D, top - 0.3)
    t = tp["t"]
    pods = []
    for sx in (-1, 1):
        xin = x_o - t if sx > 0 else -x_o
        lay = [(xin, 1.2), (xin + 1.2, 0.0), (xin + t - 1.2, 0.0), (xin + t, 1.2)]
        body = body.union(_loft(P, lay, lambda x, y, z: (x, float(y), float(z))))
        body = body.cut(cq.Workplane().box(0.5, 0.6, tp["h0"]).translate((sx * (x_o - 0.15), D + 5.0, top - 0.3 - tp["h0"] / 2)))  # 힌지 이음 선
        xt = sx * (x_o - t / 2)
        pods.append(dict(side=sx, x=xt, y0=D, y1=D + 72.0, z=top - 0.3 - tp["h40"] / 2, h=tp["h40"], t=t))
    # 카메라 링 (+x 테 바깥 위 모서리) · LED (-x) — 사진과 같은 자리
    cam = (cx + a + 2.0, b + 0.8)
    body = body.union(cq.Workplane("XZ").circle(2.5).extrude(0.8).translate((cam[0], 0.0, cam[1])))
    body = body.cut(cq.Workplane("XZ").circle(1.3).extrude(1.6).translate((cam[0], 0.8, cam[1])))
    body = body.union(cq.Workplane("XZ").circle(0.9).extrude(0.4).translate((-cam[0], 0.0, cam[1])))
    for sx in (-1, 1):                                    # 코받침: 안쪽 림 뒤에 붙은 아세테이트 패드
        body = body.union(cq.Workplane().box(3.5, 6.0, 11.0).edges("|Y").fillet(1.2)
                          .translate((sx * (geo["bridge"] / 2 - 1.5), D + 2.0, -0.15 * lh)))
    lenses = [_yprism(lens * [sx, 1] + [sx * cx, 0], 1.5, 1.5 + LENS_T) for sx in (-1, 1)]
    info = dict(cx=cx, top=top, x_out=x_o, pods=pods, ends=[], endw=0.0, camera=dict(x=cam[0], z=cam[1]), tips_y=y_end,
                temple_x=[p["x"] for p in pods], width=2 * x_o, depth=D)
    return body, lenses, info


def build(geo):
    """Frame front (rims + bridge + endpieces + nose pads) + temples with electronics pods. Returns body, lens solids, info."""
    import cadquery as cq
    if geo.get("style") == "gm":
        return build_gm(geo)
    lens = geo["lens"]
    lw, lh = geo["lens_w"], geo["lens_h"]
    rim, bridge, endw = geo["rim"], geo["bridge"], geo["endpiece"]
    cx = bridge / 2 + lw / 2
    D = geo.get("depth", FRAME_DEPTH)
    tp = geo.get("temple") or dict(t=TEMPLE_T, pod_t=7.0, pod_h=12.0, pod_len=62.0, arm_h=7.0)

    outer = offset_poly(lens, rim)
    top = float(outer[:, 1].max())
    parts, cutters = [], []
    for sx in (-1, 1):
        O = outer * [sx, 1] + [sx * cx, 0]
        P = lens * [sx, 1] + [sx * cx, 0]
        parts.append(_yprism(O, 0.0, D))
        cutters.append(_yprism(offset_poly(P, 0.0), -1.0, D + 1.0))
    xb = cx - lw / 2 * 0.55
    zb = bridge_top(outer, lw)
    bh = geo.get("bridge_h", 5.5)
    parts.append(_box(2 * xb, D, bh, 0, D / 2, zb - bh / 2))                         # bridge (straight, at the inner top line)
    x_out = cx + float(lens[:, 0].max()) + rim
    endinfo = []
    pod_t = tp["pod_t"]
    ends = []
    for sx in (-1, 1):
        # the photo's endpiece width includes the temple seen end-on: block up to the temple's inner face
        endw = max(endw, pod_t + 1.0)
        x0, x1 = x_out - 3.0, x_out + endw - pod_t / 2          # 힌지: 다리 두께의 절반이 엔드피스에 물림 (복셀에서도 끊기지 않게)
        eh = max(14.0, tp["pod_h"] + 1.0)
        parts.append(_box(x1 - x0, D + 6.0, eh, sx * (x0 + x1) / 2, (D + 6.0) / 2, top - eh / 2))   # endpiece + hinge block
        ends.append(dict(side=sx, w=x1 - x0, d=D + 6.0, h=eh))
        endinfo.append((sx, x_out + endw))
        npx = sx * (bridge / 2 - rim / 2 + 1.0)             # 안쪽 림 위 (렌즈 구멍 쪽으로 1 mm)
        parts.append(_box(4.0, 7.0, 7.0, npx, D + 2.5, -0.12 * lh))                  # nose pad: 안쪽 림 뒤에 (1 mm 겹침)
    # temples: pod (electronics) + arm + ear bend, along +y from the endpiece back face
    pods = []
    for sx, x1 in endinfo:
        xt = sx * (x1 - pod_t / 2)
        y0 = 1.0                                         # temple front end sits beside the endpiece (hinge overlap)
        pod_len, pod_h = tp["pod_len"], tp["pod_h"]
        zt = top - pod_h / 2 - 0.5                       # 다리 윗선 = 테 윗선 (사진처럼 브로우 라인이 다리로 이어짐)
        parts.append(_box(pod_t, pod_len, pod_h, xt, y0 + pod_len / 2, zt))
        pods.append(dict(side=sx, x=xt, y0=y0, y1=y0 + pod_len, z=zt, h=pod_h, t=pod_t))
        arm_y1 = TEMPLE_LEN - 25.0
        za = top - tp["arm_h"] / 2 - 0.5
        parts.append(_box(tp["t"], arm_y1 - (y0 + pod_len) + 2, tp["arm_h"], xt, (y0 + pod_len - 2 + arm_y1) / 2, za))
        p0 = np.array([xt, arm_y1 - 2, za])
        p1 = p0 + 27.0 * np.array([0, math.cos(math.radians(28)), -math.sin(math.radians(28))])
        parts.append(_bar(p0, p1, tp["t"], tp["arm_h"] * 0.8))
    body = parts[0]
    for p in parts[1:]:
        body = body.union(p)
    for c in cutters:
        body = body.cut(c)
    lenses = [_yprism(lens * [sx, 1] + [sx * cx, 0], 1.5, 1.5 + LENS_T) for sx in (-1, 1)]
    # 카메라 (오른쪽 = +x 테 바깥 위 모서리) · LED (왼쪽) — 사진과 같은 자리, 앞면에서 0.6 mm 볼록
    ux = cx + float(lens[:, 0].max()) - 2.0
    uz = top - rim - 1.5 if geo.get("style") == "gm" else top - 7.0
    cam_pt = (ux + 0.5 * rim, uz) if geo.get("style") == "gm" else (x_out + (ends[1]["w"] - 3.0) / 2, top - 7.0)
    cam_s = cq.Workplane("XZ").circle(3.0).extrude(0.6).translate((cam_pt[0], 0.0, cam_pt[1]))
    led_s = cq.Workplane("XZ").circle(1.0).extrude(0.4).translate((-cam_pt[0], 0.0, cam_pt[1]))
    body = body.union(cam_s).union(led_s)
    cam = dict(x=cam_pt[0], z=cam_pt[1])
    info = dict(cx=cx, top=top, x_out=x_out, pods=pods, ends=ends, endw=endw, camera=cam, tips_y=TEMPLE_LEN - 25.0 + 27.0 * math.cos(math.radians(28)),
                temple_x=[p["x"] for p in pods], width=2 * (x_out + endw), depth=D)
    return body, lenses, info


def bridge_top(outer, lw):
    """Top of the rim on the nose side (cat-eye: lower than the outer top) -> bridge top line."""
    inner = outer[outer[:, 0] < -0.45 * lw / 2]
    return float(inner[:, 1].max())


def _yprism(P, y0, y1):
    """Prism of the (x, z) polygon P between y = y0 and y = y1."""
    import cadquery as cq
    pl = cq.Plane(origin=(0, y0, 0), xDir=(1, 0, 0), normal=(0, 1, 0))
    # yDir = normal × xDir = (0, 0, -1): local v = -z
    pts = [(float(x), float(-z)) for x, z in P]
    return cq.Workplane(pl).polyline(pts).close().extrude(y1 - y0)


def _box(dx, dy, dz, x, y, z):
    import cadquery as cq
    return cq.Workplane().box(dx, dy, dz).translate((x, y, z))


def _bar(p0, p1, w, t):
    import cadquery as cq
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    d = p1 - p0
    L = float(np.linalg.norm(d))
    n = d / L
    x = np.array([1.0, 0.0, 0.0])
    pl = cq.Plane(origin=cq.Vector(*p0), xDir=cq.Vector(*x), normal=cq.Vector(*n))
    return cq.Workplane(pl).rect(w, t).extrude(L)


# ------------------------------------------------------------------ physics
def mass_budget(body, lenses, info):
    vol = body.val().Volume()
    cav = sum((p["t"] - 2.0) * (p["y1"] - p["y0"] - 4.0) * (p["h"] - 2.0) for p in info["pods"])   # pod shells 1 mm wall
    cav += sum((e["w"] - 2.0) * (e["d"] - 2.0) * (e["h"] - 2.0) for e in info["ends"])          # endpieces: camera / hinge space
    frame_g = (vol - cav) * MAT["rho"]
    lens_g = sum(l.val().Volume() for l in lenses) * LENS_RHO
    parts_g = sum(PARTS_G.values())
    return dict(frame_g=round(frame_g, 1), lens_g=round(lens_g, 1), parts_g=round(parts_g, 1),
                total_g=round(frame_g + lens_g + parts_g, 1), pod_cavity_mm3=round(cav))


K_FRAME = 0.2                  # W/mK, 셀룰로오스 아세테이트 열전도 (일반값)
SOC_LEN = 30.0                 # mm, SoC 보드 길이 (가정) — 다리 앞쪽 부품실에 놓임


def thermal(info):
    """1차 설계에는 방열 시트가 없다: 아세테이트(0.2 W/mK)는 열을 거의 옮기지 못해, 열은 SoC 보드 길이 + 양쪽 핀 길이 1/m 만큼의
    다리 표면으로만 빠진다 (핀 이론 m = √(hP / kA)). → 피부 쪽 표면 온도 = 주변 + P / (h · 둘레 · 유효 길이)."""
    p = [q for q in info["pods"] if q["side"] > 0][0]
    per = 2 * (p["h"] + p["t"]) * 1e-3                     # 둘레 (m)
    ac = p["h"] * p["t"] * 1e-6                            # 단면적 (m²)
    m = math.sqrt(H_CONV * per / (K_FRAME * ac))
    L_eff = SOC_LEN * 1e-3 + 2.0 / m
    A = per * L_eff
    dT = SOC_W / (H_CONV * A)
    return dict(area_cm2=round(A * 1e4, 1), dT=round(dT, 1), T=round(T_AMB + dT, 1), fin_len_mm=round(1e3 / m, 1), L_eff_mm=round(L_eff * 1e3, 1),
                P_allow_W=round((T_SKIN_LIMIT - T_AMB) * H_CONV * A, 2))


def fem(body, info, geo, h=0.9):
    import cadquery as cq
    import trimesh
    from .voxfem import VoxModel, voxelize
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "g.stl")
        cq.exporters.export(body, p, tolerance=0.08, angularTolerance=0.2)
        mesh = trimesh.load(p)
    progress.step("복셀 격자 만들기", f"{h:.2f} mm")
    occ, o = voxelize(mesh, h, sym_x=True)
    lab, nlab = ndimage.label(occ)
    if nlab > 1:                                         # 떨어진 조각이 있으면 강체 운동 -> 해가 엉터리
        sizes = np.bincount(lab.ravel())[1:]
        big = int(np.argmax(sizes)) + 1
        if sizes.sum() - sizes.max() > 0.005 * sizes.sum():
            raise ValueError(f"glasses voxel model is not connected: {nlab} pieces, sizes {sorted(sizes.tolist())[-4:]}")
        occ = lab == big                                 # 카메라 · LED 0.4–0.6 mm 볼록 같은 장식 부스러기(< 0.5 %)만 버림
    V = VoxModel(occ, o, h, MAT["E"], MAT["nu"])
    xyz = V.node_xyz
    U = V.used
    lim = MAT["yield_mpa"] / SF
    t0 = time.time()
    # --- case 1: wearing spread (both temple tips pushed outward), bridge held
    bw = geo["bridge"] / 2 + 2.0
    fix_c = np.where(U & (np.abs(xyz[:, 0]) <= bw) & (xyz[:, 1] <= FRAME_DEPTH + 0.01))[0]
    tip_y = info["tips_y"] - 6.0
    F = np.zeros(3 * V.nn)
    tips = []
    for sx in (-1, 1):
        nodes = np.where(U & (xyz[:, 1] >= tip_y) & (np.sign(xyz[:, 0]) == sx))[0]
        tips.append(nodes)
        c = xyz[nodes].mean(0)
        F += V.rigid_load(nodes, c, (sx * 1.0, 0.0, 0.0))
    u1 = V.solve(fix_c, F, label=f"FEM 풀이 1/2 — 착용 벌림 ({V.ne:,} 요소)")
    d_tip = float(np.mean([np.mean(sx * u1[3 * n]) for sx, n in zip((-1, 1), tips)]))   # mm per 1 N
    k = 1.0 / d_tip
    Fc = k * SPREAD_EACH
    vm1 = V.von_mises(u1) * Fc
    n1, _ = V.nodal(vm1)
    m1 = float(np.percentile(n1, 99.5))              # 격자 계단 모서리 특이점 제외 (상위 0.5 % 절점)
    n1 = np.minimum(n1, m1)
    un1 = np.linalg.norm(u1.reshape(-1, 3), axis=1) * Fc
    # --- case 2: bridge push (대칭): 양쪽 힌지(다리 앞쪽) 고정, 브리지 가운데를 뒤로 — 손가락으로 안경을 밀어 올릴 때.
    #     예전(한쪽 테 고정 · 반대 테 밀기)은 하중 자체가 비대칭이라 히트맵이 한쪽만 물들었음.
    D = info.get("depth", FRAME_DEPTH)
    xh = min(abs(x) for x in info["temple_x"]) - info["pods"][0]["t"] / 2 - 0.5
    fix_b = np.where(U & (np.abs(xyz[:, 0]) >= xh) & (xyz[:, 1] >= D + 1.0) & (xyz[:, 1] <= D + 12.0))[0]
    load_b = np.where(U & (np.abs(xyz[:, 0]) <= 3.0) & (xyz[:, 1] <= D + 0.01) & (xyz[:, 2] > 0.0))[0]
    cb = xyz[load_b].mean(0)
    cb[0] = 0.0
    Fb = V.rigid_load(load_b, tuple(cb), (0.0, BRIDGE_F, 0.0))
    u2 = V.solve(fix_b, Fb, label=f"FEM 풀이 2/2 — 브리지 누름 ({V.ne:,} 요소)")
    progress.step("응력 · 변위 분포")
    vm2 = V.von_mises(u2)
    n2, _ = V.nodal(vm2)
    m2 = float(np.percentile(n2, 99.5))
    n2 = np.minimum(n2, m2)
    tr, _ = V.rigid_fit(u2, load_b, tuple(cb))
    un2 = np.linalg.norm(u2.reshape(-1, 3), axis=1)
    heat = V.heat({
        "clamp_stress": (n1, 0.0, max(m1, 1e-3), f"응력 — 착용 벌림 (다리 끝 한쪽 {SPREAD_EACH:.0f} mm)", "MPa",
                         f"빨강 = 이 설계 최대 근처 (허용 {lim:.0f} MPa)"),
        "clamp_disp": (un1, 0.0, max(float(np.percentile(un1[U], 99.5)), 1e-3), "변위 — 착용 벌림", "mm", "자동 척도"),
        "bridge_stress": (n2, 0.0, max(m2, 1e-3), f"응력 — 브리지 누름 ({BRIDGE_F:.0f} N 뒤로, 양쪽 힌지 고정)", "MPa",
                          f"빨강 = 이 설계 최대 근처 (허용 {lim:.0f} MPa)"),
        "bridge_disp": (un2, 0.0, max(float(np.percentile(un2[U], 99.5)), 1e-3), "변위 — 브리지 누름", "mm", "자동 척도"),
    })
    return dict(h=h, elements=int(V.ne), k_N_per_mm=round(k, 4), clamp_N=round(Fc, 3), clamp_vm=round(m1, 2),
                bridge_vm=round(m2, 2), bridge_defl=round(float(np.linalg.norm(tr)), 3), solve_s=round(time.time() - t0, 1),
                heat=heat, stress_limit=round(lim, 1))


def conditions(geo, mb, th):
    return [
        dict(key="mass", name="무게", value=f"≤ {MASS_LIMIT:.0f} g (보도: 표준 렌즈 약 41 g, 이전 46–50 g)", source="근거: 언론 보도 (SammyGuru 등)"),
        dict(key="parts", name="내장 부품", value="AR1 Gen1 · 12 MP 카메라 · 스피커 2 · 마이크 4 · 배터리 (약 155 mAh)", source="근거: 언론 보도 · 유출 사양"),
        dict(key="clamp", name="착용 클램프 힘 (한쪽)", value=f"{CLAMP_RANGE[0]}–{CLAMP_RANGE[1]} N, 다리 끝 한쪽 {SPREAD_EACH:.0f} mm 벌림",
             source="근거: 문헌 0–1 N 대 · 특허 50–110 g (하한 · 벌림 양은 가정)"),
        dict(key="bridge", name="브리지 누름", value=f"양쪽 힌지 고정, 브리지 가운데 {BRIDGE_F:.0f} N 앞→뒤 (안경 밀어 올리기) → 응력 ≤ 항복/1.5",
             source="ISO 12870 브리지 변형 시험과 같은 부위 (하중 · 지지 방식은 가정)"),
        dict(key="stress", name="응력", value=f"≤ {MAT['yield_mpa']:.0f} ÷ {SF} = {MAT['yield_mpa'] / SF:.0f} MPa", source=f"{MAT['name']} 일반값 (가정)"),
        dict(key="skin", name="피부 접촉 온도", value=f"≤ {T_SKIN_LIMIT:.0f} °C (주변 {T_AMB:.0f} °C, SoC {SOC_W} W 지속)", source="IEC 62368-1 TS1 장시간 접촉 · ISO 13732-1 (근거), 소비전력은 가정"),
        dict(key="drop", name="낙하", value="1 m 낙하 후 기능 유지 (판정은 다음 단계)", source="가정"),
    ]


# ------------------------------------------------------------------ pipeline
def parse_lens_w(text):
    m = re.search(r"렌즈\s*(?:폭|가로)?\s*(\d{2}(?:\.\d)?)", text or "")
    return float(m.group(1)) if m else LENS_W_DEFAULT


def template_geometry(style, lw):
    """템플릿 형상: 형상(슬림 오벌 / 캣아이) × 렌즈 폭(48 · 50 · 52 mm). 브리지 · 림 · 엔드피스는 템플릿 값."""
    S = STYLES[style]
    L = lens_outline(style, w=lw, h=S["h"] * lw / S["w"])
    if S.get("shape") != "rrect":                        # 둥근 사각은 호 점(4 × 14) 그대로 — r(θ) 재표본은 모서리를 뭉갬
        th, r, c = radial(L, 72)                         # CAD 용 72점 (180점 대비 부피 차 < 0.3 %, 불리언 2.4배 빠름)
        L = from_radial(th, r) + c
    if style == "gm":                                    # 공식 사진 디자인 그대로 (두께 · 다리 크기도 사진 비율)
        Sg = dict(S, w=lw, h=S["h"] * lw / S["w"], bridge=S["bridge"] * lw / 50.0)
        L = _smooth(_resample(L, 1.2), 1.0)
        cx = Sg["bridge"] / 2 + float(L[:, 0].max())
        front, top = gm_front_outline(Sg, L, cx)
        return dict(lens=L, lens_w=float(np.ptp(L[:, 0])), lens_h=float(np.ptp(L[:, 1])), rim=S["rim"], bridge=Sg["bridge"],
                    bridge_h=S["bridge_h"], depth=S["depth"], endpiece=S["endpiece"], temple=S["temple"], front=front, top=top,
                    style=style, source="템플릿", lens_w_t=lw)
    return dict(lens=L, lens_w=float(np.ptp(L[:, 0])), lens_h=float(np.ptp(L[:, 1])), rim=S["rim"] + RIM_EXTRA, bridge=18.0,
                endpiece=12.0, style=style, source="템플릿", lens_w_t=lw)


INPUT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_PHOTOS = {"gm": os.path.join(INPUT_ROOT, "examples", "glasses", "젠틀몬스터_구글_삼성_AI글래스.jpg")}
_REF_FP = None


def _fingerprint(img):
    from skimage.transform import resize
    g = resize(_to_gray(img), (80, 64), anti_aliasing=True)
    g = g - g.mean()
    return g / (np.linalg.norm(g) + 1e-9)


def matches_reference(img, thr=0.95):
    """등록된 공식 제품 사진(다시 저장 · 축소해도 같은 사진)이면 그 템플릿 이름, 아니면 None."""
    global _REF_FP
    if _REF_FP is None:
        from PIL import Image
        _REF_FP = {k: _fingerprint(np.asarray(Image.open(p).convert("L"), float) / 255.0) for k, p in REF_PHOTOS.items() if os.path.exists(p)}
    try:
        f = _fingerprint(img)
    except Exception:
        return None
    best = max(((float((f * v).sum()), k) for k, v in _REF_FP.items()), default=(0.0, None))
    return best[1] if best[0] >= thr else None


def geometry_from(photo=None, text="", style=None):
    """사진 · 문장 → 가장 가까운 템플릿 (형상 · 렌즈 폭). 사진에서 잰 치수는 참고로 함께 돌려줌.
    등록된 공식 제품 사진(3/4 각도) → 'gm' 템플릿, 정면 사진 → 윤곽 분석으로 가까운 형상, 사진 없음 → 'gm'."""
    lw = parse_lens_w(text)
    an, ref = None, None
    if photo is not None:
        progress.step("사진 → 템플릿 (등록 사진 확인 · 테 · 렌즈 윤곽)")
        ref = matches_reference(photo)
        if ref is None:
            an = analyze_photo(photo, lens_w=lw)
    st = style or ref or (an["style"] if an else ("cat_eye" if re.search(r"캣\s*아이|cat", text or "", re.I) else
                                                   "slim_oval" if re.search(r"슬림|오벌", text or "") else "gm"))
    lw_t = min(LENS_WIDTHS, key=lambda w: abs(w - lw))
    geo = template_geometry(st, lw_t)
    geo["source"] = ("공식 제품 사진 → 템플릿" if ref else "사진 → 가까운 템플릿" if an else
                     "사진 인식 실패 → 기본 템플릿" if photo is not None else "템플릿 (사진 없음)")
    geo["ref_photo"] = ref
    return geo, an


def design(text="", image=None, out="out", with_mesh=False, style=None):
    """템플릿(형상 2 × 렌즈 폭 3) 결과 DB 에서 바로 (처음 한 번만 계산). 사진은 템플릿을 고르고, 분석 그림 · 치수는 매번 새로."""
    import json
    from .. import memo
    t0 = time.time()
    os.makedirs(out, exist_ok=True)
    geo, an = geometry_from(image, text, style)
    k = memo.key("glasses", GM_VERSION, geo["style"], geo["lens_w_t"], TEMPLE_T, RIM_EXTRA, STYLES[geo["style"]])
    rep = memo.get(k, out) if with_mesh else None
    if rep is None:
        before = os.listdir(out)
        rep = _design(geo, out, with_mesh)
        if with_mesh:
            rep = memo.put(k, out, memo.new_files(out, before), rep)
    else:
        progress.step("템플릿 결과 DB에서 1차 설계 · 성능 불러오기", STYLES[geo["style"]]["name"])
    S = STYLES[geo["style"]]
    if geo.get("ref_photo"):
        analysis_png(image, None, geo, os.path.join(out, "analysis.png"))
        rep["template"].update(chosen_by="공식 제품 사진 → 템플릿",
                               match=dict(source="사진", frame="photo", candidates=[dict(id=geo["style"], name=S["name"], confidence=1.0)]))
        rep["extra"]["photo"] = dict(mode="reference", file=os.path.basename(REF_PHOTOS[geo["ref_photo"]]))
    elif an:
        analysis_png(image, an, geo, os.path.join(out, "analysis.png"))
        rep["template"].update(chosen_by="사진 → 가까운 템플릿",
                               match=dict(source="사진", frame="photo", candidates=[dict(id=geo["style"], name=S["name"], confidence=1.0)]))
        rep["extra"]["photo"] = {k_: v for k_, v in an.items() if k_ not in ("lens", "px")}
        rep["analysis"]["features"] = an["features"]
        rep["analysis"]["photo_dims"] = dict(lens_w=round(an["lens_w"], 1), lens_h=round(an["lens_h"], 1), bridge=round(an["bridge"], 1),
                                             rim=round(an["rim"], 1))
    else:
        rep["template"].update(chosen_by="텍스트" if text else "기본")
        rep["extra"]["photo"] = None
    rep["summary"] = [[a, geo["source"]] if a == "형상 출처" else [a, b] for a, b in rep["summary"]]
    rep["seconds"] = round(time.time() - t0, 2)
    with open(os.path.join(out, "report.json"), "w", encoding="utf-8") as f:
        json.dump({k_: v for k_, v in rep.items() if k_ not in ("mesh", "heat", "aux")}, f, ensure_ascii=False, indent=1)
    return rep


def _design(geo, out, with_mesh):
    """실제 계산 (템플릿 DB 가 비었을 때만)."""
    import cadquery as cq
    from .common import base_report, finish, mesh_b64
    t0 = time.time()
    image, an, text = None, None, ""
    os.makedirs(out, exist_ok=True)
    progress.step("CAD (테 · 브리지 · 다리 · 부품실)")
    body, lenses, info = build(geo)
    cq.exporters.export(body, os.path.join(out, "design_1st.step"), exportType="STEP")
    cq.exporters.export(body, os.path.join(out, "design_1st.stl"), tolerance=0.08, angularTolerance=0.2)
    progress.step("무게 · 발열 계산")
    mb = mass_budget(body, lenses, info)
    th = thermal(info)
    fe = fem(body, info, geo)
    lim = MAT["yield_mpa"] / SF
    rows = [
        dict(key="mass", name="총무게 (테 + 렌즈 + 부품)", value=mb["total_g"], unit="g", op="<=", limit=MASS_LIMIT, source="보도 41–50 g"),
        dict(key="clamp_lo", name="착용 클램프 힘 (한쪽, FEM) — 흘러내림 방지", value=fe["clamp_N"], unit="N", op=">=", limit=CLAMP_RANGE[0], source="흘러내림 방지 (가정)"),
        dict(key="clamp_hi", name="착용 클램프 힘 (한쪽, FEM) — 편안함", value=fe["clamp_N"], unit="N", op="<=", limit=CLAMP_RANGE[1], source="문헌 · 특허 편안한 범위"),
        dict(key="clamp_vm", name="착용 벌림 최대 응력 (FEM)", value=fe["clamp_vm"], unit="MPa", op="<=", limit=round(lim, 1), source=f"{MAT['name']} 항복 ÷ 1.5"),
        dict(key="bridge_vm", name=f"브리지 누름 {BRIDGE_F:.0f} N 최대 응력 (FEM)", value=fe["bridge_vm"], unit="MPa", op="<=", limit=round(lim, 1),
             source="ISO 12870 항목 · 하중 가정"),
        dict(key="skin", name=f"다리 표면 온도 (SoC {SOC_W} W)", value=th["T"], unit="°C", op="<=", limit=T_SKIN_LIMIT, source="IEC 62368-1 TS1"),
    ]
    for r in rows:
        r["ok"] = bool(r["value"] >= r["limit"] if r["op"] == ">=" else r["value"] <= r["limit"])
    progress.step("도면 · 결과 파일")
    analysis_png(image, an, geo, os.path.join(out, "analysis.png"))
    drawing(body, lenses, info, geo, mb, os.path.join(out, "design_1st_drawing.png"), os.path.join(out, "design_1st_drawing.pdf"))
    analysis_png(None, None, geo, os.path.join(out, "side_view.png"))
    how = "사진 분석" if an else ("텍스트" if text else "기본")
    S = STYLES[geo["style"]]
    rep = base_report(
        product="AR 글래스", tid="AG-" + geo["style"], tname=f"AI 글래스 — {S['name']} · 렌즈 {geo['lens_w_t']:.0f}", tdesc=S["note"], chosen_by=how,
        match=dict(source="사진", frame="photo", candidates=[dict(id=geo["style"], name=S["name"], confidence=1.0)]) if an else None,
        rows=rows, conditions=conditions(geo, mb, th),
        summary=[["제품", "AI 글래스 (Android XR, 디스플레이 없음)"], ["형상 출처", geo["source"]], ["테 재료", MAT["name"]],
                 ["렌즈", f"CR-39 {LENS_T} mm"], ["안전율", SF]],
        design_vars=[["렌즈 폭 × 높이", f"{geo['lens_w']:.1f} × {geo['lens_h']:.1f} mm"], ["브리지", f"{geo['bridge']:.1f} mm"],
                     ["림 두께", f"{geo['rim']:.1f} mm"], ["엔드피스", f"{geo['endpiece']:.1f} mm"], ["테 전체 폭", f"{info['width']:.1f} mm"],
                     ["다리 길이", f"{TEMPLE_LEN:.0f} mm"], ["테 깊이", f"{info.get('depth', FRAME_DEPTH):.0f} mm"],
                     ["무게 내역", f"테 {mb['frame_g']} g + 렌즈 {mb['lens_g']} g + 부품 {mb['parts_g']} g"],
                     ["다리 강성 (한쪽)", f"{fe['k_N_per_mm']} N/mm"], ["허용 지속 소비전력", f"{th['P_allow_W']} W (43 °C 기준)"],
                     ["해석 격자", f"{fe['h']} mm · {fe['elements']:,} 요소"]],
        assumptions=[f"렌즈 폭 {geo['lens_w']:.0f} mm 로 사진 축척 환산 (텍스트 '렌즈 52' 로 변경)" if an else "사진이 없어 공개 사진 묘사 기반 기본 형상 사용",
                     f"테 재료 {MAT['name']} E {MAT['E']:.0f} MPa · 항복 {MAT['yield_mpa']:.0f} MPa (일반값)",
                     f"전자부품 {sum(PARTS_G.values()):.0f} g (보드 · 카메라 {PARTS_G['board_camera']} g, 배터리 {PARTS_G['battery']} g, 스피커 · 마이크 {PARTS_G['speakers_mics']} g, 배선 · 힌지 {PARTS_G['wiring_hinges']} g)",
                     "최대 응력 = 절점 응력 상위 0.5 % 제외값 (복셀 계단 모서리의 가짜 응력 집중 제외)",
                     "다리 앞쪽 부품실 · 엔드피스(카메라 · 힌지)는 벽 1 mm 껍데기로 무게 계산, 힌지는 강체 연결로 해석",
                     f"착용 벌림: 머리 폭 ≈ 테 폭 + 10 mm → 다리 끝 한쪽 {SPREAD_EACH:.0f} mm",
                     f"발열: 1차 설계는 방열 시트 없음 — 아세테이트 {K_FRAME} W/mK 라 열이 SoC 보드({SOC_LEN:.0f} mm, 가정) + 양쪽 {th['fin_len_mm']} mm(핀 길이 1/m)에만 퍼짐, h = {H_CONV:.0f} W/m²K",
                     ("1차 설계 = 공식 사진 디자인을 통 아세테이트로 (다리 · 테 속을 비우지 않음, 방열 시트 없음)" if geo.get("style") == "gm" else
                      f"1차 설계 다리 두께 {TEMPLE_T:g} mm · 림 +{RIM_EXTRA:g} mm (일반 아세테이트 뿔테 수준)") + " — 미충족 항목(무게 · 온도)은 다음 단계(물리 최적화)에서 맞춤",
                     "데모용 1차 설계 — 최적화 단계로 넘기지 않음"],
        sources=[SOURCES[k] for k in ("weight41", "unpacked", "battery", "clamp", "clamp_patent", "iso12870", "touch")],
        cad=dict(mass_g=mb["total_g"], material=MAT["name"]),
        extra=dict(mass=mb, thermal=th, fem={k: v for k, v in fe.items() if k != "heat"},
                   photo=({k: v for k, v in an.items() if k not in ("lens", "px")} if an else None)),
        analysis=dict(png="analysis.png", features=(an or {}).get("features") or describe(geo["lens"])),
        seconds=time.time() - t0)
    finish(rep, out)
    if with_mesh:
        rep["mesh"] = mesh_b64(body, 0.08)
        rep["heat"] = fe["heat"]
        rep["aux"] = [dict(kind="mesh", color="#bcd3e0", opacity=0.35, label="렌즈", **mesh_b64(l, 0.1)) for l in lenses]
        rep["scene"] = dict(floor_z=None, up="z", color="#2b2d31")
    return rep


# ------------------------------------------------------------------ images
def analysis_png(photo, an, geo, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    if photo is not None and an is None:
        fig, ax = plt.subplots(1, 2, figsize=(13, 5.2), gridspec_kw=dict(width_ratios=[1.0, 1.2]))
        ax[0].imshow(np.asarray(photo), cmap="gray" if np.asarray(photo).ndim == 2 else None)
        ax[0].set_title("입력: 공식 제품 사진 (3/4 각도) → 등록된 템플릿", fontsize=10)
        ax[0].axis("off")
        a = ax[1]
    elif photo is not None and an is not None:
        fig, ax = plt.subplots(1, 2, figsize=(13, 4.4), gridspec_kw=dict(width_ratios=[1.6, 1]))
        ax[0].imshow(np.asarray(photo), cmap="gray" if np.asarray(photo).ndim == 2 else None)
        for C in an["px"]["contours"]:
            C = np.asarray(C)
            ax[0].plot(C[:, 0], C[:, 1], c="#e4572e", lw=2)
        x0, y0, x1, y1 = an["px"]["frame_bbox"]
        ax[0].add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec="#2e86ab", lw=1.5, ls="--"))
        ax[0].set_title("입력 사진 + 검출 (빨강 = 렌즈 윤곽, 파랑 = 테 범위)", fontsize=10)
        ax[0].axis("off")
        a = ax[1]
    else:
        fig, a = plt.subplots(figsize=(5.5, 4.2))
    L = geo["lens"]
    if geo.get("front") is not None:                     # 사진형 뿔테: 앞판 전체 윤곽 + 렌즈 2개
        Fo = np.asarray(geo["front"])
        a.fill(Fo[:, 0], Fo[:, 1], fc="#2b2d31", ec="#111", lw=1)
        cx_ = geo["bridge"] / 2 + float(L[:, 0].max())
        for sx in (-1, 1):
            a.fill(sx * L[:, 0] + sx * cx_, L[:, 1], fc="#dfe9ef", ec="#222", lw=1)
    else:
        a.fill(L[:, 0], L[:, 1], fc="#dfe9ef", ec="#222", lw=1.5)
        O = offset_poly(L, geo["rim"])
        a.plot(np.r_[O[:, 0], O[:, 0][:1]], np.r_[O[:, 1], O[:, 1][:1]], c="#555", lw=1)
    f = (an or {}).get("features") or describe(L)
    a.set_title(f"렌즈 윤곽 (mm) — {f['style_name']}\n가로 {np.ptp(L[:, 0]):.1f} · 세로 {np.ptp(L[:, 1]):.1f} · 윗선 직선 {f['top_flat']:.2f} · 바깥 올림 {f['outer_lift']:.2f}",
                fontsize=9)
    a.set_aspect("equal")
    a.grid(alpha=.25)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def drawing(body, lenses, info, geo, mb, png, pdf):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    verts, tris = body.val().tessellate(0.1, 0.3)
    V = np.array([[p.x, p.y, p.z] for p in verts])
    F = np.array(tris)
    fig, ax = plt.subplots(1, 3, figsize=(17, 5), gridspec_kw=dict(width_ratios=[1.4, 1.4, 1.5]))
    for a, (i, j, ttl) in zip(ax, ((0, 2, "정면"), (0, 1, "위 (앞 = 아래)"), (1, 2, "옆 (앞 = 왼쪽)"))):
        a.add_collection(PolyCollection(V[F][:, :, [i, j]], fc="#2b2d31", ec="none", rasterized=True))
        if i == 0 and j == 2:
            for sx in (-1, 1):
                L = geo["lens"] * [sx, 1] + [sx * info["cx"], 0]
                a.fill(L[:, 0], L[:, 1], fc="#cfe0ea", ec="none", alpha=.8)
            c = info["camera"]
            a.add_patch(plt.Circle((c["x"], c["z"]), 2.0, fc="#7a8", ec="k", lw=.5))
            a.annotate("카메라", (c["x"], c["z"]), (c["x"] + 6, c["z"] + 10), fontsize=8, arrowprops=dict(arrowstyle="-", lw=.6))
        a.set_aspect("equal")
        a.autoscale()
        a.grid(alpha=.25)
        a.set_title(ttl, fontsize=10)
    for p in info["pods"]:
        ax[2].add_patch(plt.Rectangle((p["y0"], p["z"] - p["h"] / 2), p["y1"] - p["y0"], p["h"], fill=False, ec="#e4572e", ls="--"))
    ax[2].text(info["pods"][0]["y0"] + 2, info["pods"][0]["z"] + 8, "부품실 (SoC · 배터리)", fontsize=8, color="#e4572e")
    fig.suptitle(f"AI 글래스 — 1차 설계 · {STYLES[geo['style']]['name']} · {MAT['name']} · 예상 {mb['total_g']} g · 단위 mm", fontsize=12)
    fig.savefig(png, dpi=120, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    plt.close(fig)
