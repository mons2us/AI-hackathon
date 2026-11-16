"""AR(AI) 글래스 — 제품 사진 → 렌즈 윤곽 · 테 치수 추출 → 1차 설계(CAD · 도면) + 물리 조건 + 간이 판정 (데모 시나리오).

대상: 젠틀몬스터 × Google × 삼성 AI 글래스 (Android XR, 디스플레이 없음, 카메라 · 스피커 · 마이크).
사진 분석: 배경 대비 테(어두운 영역) 검출 → 테 안쪽 구멍 = 렌즈 2개 → 좌우 렌즈 윤곽 평균(r(θ)) → mm 환산
(렌즈 폭 기준, 기본 50 mm = 가정, 텍스트 '렌즈 52' 로 바꿈) → 브리지 · 림 두께 · 엔드피스 폭.
좌표 (mm): x = 좌우(착용자 기준 아님, 사진 오른쪽 = +x), y = 앞→뒤(앞면 y = 0, 다리는 +y), z = 위.
물리 조건: 무게(보도 41–50 g), 착용 클램프 힘(문헌 0–1 N 대), 브리지 굽힘(ISO 12870 시험 항목, 하중 가정),
다리 피부 접촉 온도 ≤ 43 °C(IEC 62368-1 TS1 장시간 접촉, ISO 13732-1 근거). 판정: 응력 · 힘 = 복셀 FEM, 온도 = 집중 열저항.
"""
import math
import os
import re
import tempfile
import time

import numpy as np
from scipy import ndimage

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
BRIDGE_F = 5.0                 # N, 브리지 굽힘 하중 (가정: ISO 12870 브리지 변형 시험 항목, 수치 미확인)
SOC_W = 0.5                    # W, 촬영 · AI 지속 사용 시 평균 소비 (가정)
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
}


# ------------------------------------------------------------------ lens shapes
def lens_outline(style="slim_oval", w=None, h=None, n=160):
    """Lens contour for the +x lens, centred at (0, 0), x outward (to the temple), z up. Returns (n, 2) mm."""
    S = STYLES[style]
    w = w or S["w"]
    h = h or S["h"]
    a, b = w / 2, h / 2
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
def build(geo):
    """Frame front (rims + bridge + endpieces + nose pads) + temples with electronics pods. Returns body, lens solids, info."""
    import cadquery as cq
    lens = geo["lens"]
    lw, lh = geo["lens_w"], geo["lens_h"]
    rim, bridge, endw = geo["rim"], geo["bridge"], geo["endpiece"]
    cx = bridge / 2 + lw / 2
    D = FRAME_DEPTH

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
    parts.append(_box(2 * xb, D, 5.5, 0, D / 2, zb - 2.75))                        # bridge (straight, at the inner top line)
    x_out = cx + float(lens[:, 0].max()) + rim
    endinfo = []
    pod_t = 7.0
    ends = []
    for sx in (-1, 1):
        # the photo's endpiece width includes the temple seen end-on: block up to the temple's inner face
        endw = max(endw, pod_t + 3.0)
        x0, x1 = x_out - 3.0, x_out + endw - pod_t + 2.0
        parts.append(_box(x1 - x0, D + 6.0, 14.0, sx * (x0 + x1) / 2, (D + 6.0) / 2, top - 7.0))   # endpiece + hinge block
        ends.append(dict(side=sx, w=x1 - x0, d=D + 6.0, h=14.0))
        endinfo.append((sx, x_out + endw))
        npx = sx * (bridge / 2 + 3.5)
        parts.append(_box(4.0, 6.0, 7.0, npx, D + 3.0, -0.12 * lh))                  # nose pad
    # temples: pod (electronics) + arm + ear bend, along +y from the endpiece back face
    pods = []
    for sx, x1 in endinfo:
        xt = sx * (x1 - pod_t / 2)
        y0 = 1.0                                         # temple front end sits beside the endpiece (hinge overlap)
        pod_len, pod_h = 62.0, 12.0
        parts.append(_box(pod_t, pod_len, pod_h, xt, y0 + pod_len / 2, top - 7.0))
        pods.append(dict(side=sx, x=xt, y0=y0, y1=y0 + pod_len, z=top - 7.0, h=pod_h, t=pod_t))
        arm_y1 = TEMPLE_LEN - 25.0
        parts.append(_box(4.5, arm_y1 - (y0 + pod_len) + 2, 7.0, xt, (y0 + pod_len - 2 + arm_y1) / 2, top - 7.0))
        p0 = np.array([xt, arm_y1 - 2, top - 7.0])
        p1 = p0 + 27.0 * np.array([0, math.cos(math.radians(28)), -math.sin(math.radians(28))])
        parts.append(_bar(p0, p1, 4.5, 7.0))
    body = parts[0]
    for p in parts[1:]:
        body = body.union(p)
    for c in cutters:
        body = body.cut(c)
    lenses = [_yprism(lens * [sx, 1] + [sx * cx, 0], 1.5, 1.5 + LENS_T) for sx in (-1, 1)]
    cam = dict(x=x_out + (ends[1]["w"] - 3.0) / 2, z=top - 7.0)
    info = dict(cx=cx, top=top, x_out=x_out, pods=pods, ends=ends, endw=endw, camera=cam, tips_y=TEMPLE_LEN - 25.0 + 27.0 * math.cos(math.radians(28)),
                temple_x=[p["x"] for p in pods], width=2 * (x_out + endw))
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


def thermal(info):
    """Lumped: SoC heat spread (graphite sheet, assumed) over the right temple surface; skin-side temperature."""
    p = [q for q in info["pods"] if q["side"] > 0][0]
    L_pod = p["y1"] - p["y0"]
    A_pod = 2 * (L_pod * p["h"] + L_pod * p["t"] + p["h"] * p["t"])
    L_arm = TEMPLE_LEN - 25.0 - p["y1"]
    A_arm = 2 * L_arm * (7.0 + 4.5)
    A = (A_pod + A_arm) * 1e-6
    dT = SOC_W / (H_CONV * A)
    return dict(area_cm2=round(A * 1e4, 1), dT=round(dT, 1), T=round(T_AMB + dT, 1),
                P_allow_W=round((T_SKIN_LIMIT - T_AMB) * H_CONV * A, 2))


def fem(body, info, geo, h=0.9):
    import cadquery as cq
    import trimesh
    from .voxfem import VoxModel, voxelize
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "g.stl")
        cq.exporters.export(body, p, tolerance=0.08, angularTolerance=0.2)
        mesh = trimesh.load(p)
    occ, o = voxelize(mesh, h)
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
    u1 = V.solve(fix_c, F)
    d_tip = float(np.mean([np.mean(sx * u1[3 * n]) for sx, n in zip((-1, 1), tips)]))   # mm per 1 N
    k = 1.0 / d_tip
    Fc = k * SPREAD_EACH
    vm1 = V.von_mises(u1) * Fc
    n1, _ = V.nodal(vm1)
    m1 = float(np.percentile(n1, 99.5))              # 격자 계단 모서리 특이점 제외 (상위 0.5 % 절점)
    n1 = np.minimum(n1, m1)
    un1 = np.linalg.norm(u1.reshape(-1, 3), axis=1) * Fc
    # --- case 2: bridge bending: one rim held, the other rim pushed back (+y)
    cx = info["cx"]
    fix_b = np.where(U & (xyz[:, 0] <= -(geo["bridge"] / 2 + 0.3 * geo["lens_w"])) & (xyz[:, 1] <= FRAME_DEPTH + 0.01))[0]
    load_b = np.where(U & (xyz[:, 0] >= geo["bridge"] / 2 + 0.3 * geo["lens_w"]) & (xyz[:, 0] <= cx + geo["lens_w"] / 2 + geo["rim"])
                      & (xyz[:, 1] <= FRAME_DEPTH + 0.01))[0]
    Fb = V.rigid_load(load_b, (cx, 0.0, 0.0), (0.0, BRIDGE_F, 0.0))
    u2 = V.solve(fix_b, Fb)
    vm2 = V.von_mises(u2)
    n2, _ = V.nodal(vm2)
    m2 = float(np.percentile(n2, 99.5))
    n2 = np.minimum(n2, m2)
    tr, _ = V.rigid_fit(u2, load_b, (cx, 0.0, 0.0))
    un2 = np.linalg.norm(u2.reshape(-1, 3), axis=1)
    heat = V.heat({
        "clamp_stress": (n1, 0.0, max(m1, 1e-3), f"응력 — 착용 벌림 (다리 끝 한쪽 {SPREAD_EACH:.0f} mm)", "MPa",
                         f"빨강 = 이 설계 최대 근처 (허용 {lim:.0f} MPa)"),
        "clamp_disp": (un1, 0.0, max(float(np.percentile(un1[U], 99.5)), 1e-3), "변위 — 착용 벌림", "mm", "자동 척도"),
        "bridge_stress": (n2, 0.0, max(m2, 1e-3), f"응력 — 브리지 굽힘 ({BRIDGE_F:.0f} N, 한쪽 테 고정)", "MPa",
                          f"빨강 = 이 설계 최대 근처 (허용 {lim:.0f} MPa)"),
        "bridge_disp": (un2, 0.0, max(float(np.percentile(un2[U], 99.5)), 1e-3), "변위 — 브리지 굽힘", "mm", "자동 척도"),
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
        dict(key="bridge", name="브리지 굽힘", value=f"한쪽 테 고정, 반대 테에 {BRIDGE_F:.0f} N 앞→뒤 → 응력 ≤ 항복/1.5", source="ISO 12870 시험 항목 (하중 수치는 가정)"),
        dict(key="stress", name="응력", value=f"≤ {MAT['yield_mpa']:.0f} ÷ {SF} = {MAT['yield_mpa'] / SF:.0f} MPa", source=f"{MAT['name']} 일반값 (가정)"),
        dict(key="skin", name="피부 접촉 온도", value=f"≤ {T_SKIN_LIMIT:.0f} °C (주변 {T_AMB:.0f} °C, SoC {SOC_W} W 지속)", source="IEC 62368-1 TS1 장시간 접촉 · ISO 13732-1 (근거), 소비전력은 가정"),
        dict(key="drop", name="낙하", value="1 m 낙하 후 기능 유지 (판정은 다음 단계)", source="가정"),
    ]


# ------------------------------------------------------------------ pipeline
def parse_lens_w(text):
    m = re.search(r"렌즈\s*(?:폭|가로)?\s*(\d{2}(?:\.\d)?)", text or "")
    return float(m.group(1)) if m else LENS_W_DEFAULT


def geometry_from(photo=None, text="", style=None):
    lw = parse_lens_w(text)
    an = None
    if photo is not None:
        an = analyze_photo(photo, lens_w=lw)
    if an is not None:
        geo = dict(lens=an["lens"], lens_w=an["lens_w"], lens_h=an["lens_h"], rim=an["rim"], bridge=an["bridge"],
                   endpiece=an["endpiece"], style=an["style"], source="사진 분석")
    else:
        st = style or ("cat_eye" if re.search(r"캣\s*아이|cat", text or "", re.I) else "slim_oval")
        S = STYLES[st]
        L = lens_outline(st, w=lw, h=S["h"] * lw / S["w"])
        geo = dict(lens=L, lens_w=float(np.ptp(L[:, 0])), lens_h=float(np.ptp(L[:, 1])), rim=S["rim"], bridge=18.0,
                   endpiece=7.0, style=st, source="기본 형상 (사진 없음/인식 실패)")
    return geo, an


def design(text="", image=None, out="out", with_mesh=False, style=None):
    import cadquery as cq
    from .common import base_report, finish, mesh_b64
    t0 = time.time()
    os.makedirs(out, exist_ok=True)
    geo, an = geometry_from(image, text, style)
    body, lenses, info = build(geo)
    cq.exporters.export(body, os.path.join(out, "design_1st.step"), exportType="STEP")
    cq.exporters.export(body, os.path.join(out, "design_1st.stl"), tolerance=0.08, angularTolerance=0.2)
    mb = mass_budget(body, lenses, info)
    th = thermal(info)
    fe = fem(body, info, geo)
    lim = MAT["yield_mpa"] / SF
    rows = [
        dict(key="mass", name="총무게 (테 + 렌즈 + 부품)", value=mb["total_g"], unit="g", op="<=", limit=MASS_LIMIT, source="보도 41–50 g"),
        dict(key="clamp_lo", name="착용 클램프 힘 (한쪽, FEM) — 흘러내림 방지", value=fe["clamp_N"], unit="N", op=">=", limit=CLAMP_RANGE[0], source="흘러내림 방지 (가정)"),
        dict(key="clamp_hi", name="착용 클램프 힘 (한쪽, FEM) — 편안함", value=fe["clamp_N"], unit="N", op="<=", limit=CLAMP_RANGE[1], source="문헌 · 특허 편안한 범위"),
        dict(key="clamp_vm", name="착용 벌림 최대 응력 (FEM)", value=fe["clamp_vm"], unit="MPa", op="<=", limit=round(lim, 1), source=f"{MAT['name']} 항복 ÷ 1.5"),
        dict(key="bridge_vm", name=f"브리지 굽힘 {BRIDGE_F:.0f} N 최대 응력 (FEM)", value=fe["bridge_vm"], unit="MPa", op="<=", limit=round(lim, 1),
             source="ISO 12870 항목 · 하중 가정"),
        dict(key="skin", name=f"다리 표면 온도 (SoC {SOC_W} W)", value=th["T"], unit="°C", op="<=", limit=T_SKIN_LIMIT, source="IEC 62368-1 TS1"),
    ]
    for r in rows:
        r["ok"] = bool(r["value"] >= r["limit"] if r["op"] == ">=" else r["value"] <= r["limit"])
    analysis_png(image, an, geo, os.path.join(out, "analysis.png"))
    drawing(body, lenses, info, geo, mb, os.path.join(out, "design_1st_drawing.png"), os.path.join(out, "design_1st_drawing.pdf"))
    analysis_png(None, None, geo, os.path.join(out, "side_view.png"))
    how = "사진 분석" if an else ("텍스트" if text else "기본")
    S = STYLES[geo["style"]]
    rep = base_report(
        product="AR 글래스", tid="AG01", tname=f"AI 글래스 — {S['name']}", tdesc=S["note"], chosen_by=how,
        match=dict(source="사진", frame="photo", candidates=[dict(id=geo["style"], name=S["name"], confidence=1.0)]) if an else None,
        rows=rows, conditions=conditions(geo, mb, th),
        summary=[["제품", "AI 글래스 (Android XR, 디스플레이 없음)"], ["형상 출처", geo["source"]], ["테 재료", MAT["name"]],
                 ["렌즈", f"CR-39 {LENS_T} mm"], ["안전율", SF]],
        design_vars=[["렌즈 폭 × 높이", f"{geo['lens_w']:.1f} × {geo['lens_h']:.1f} mm"], ["브리지", f"{geo['bridge']:.1f} mm"],
                     ["림 두께", f"{geo['rim']:.1f} mm"], ["엔드피스", f"{geo['endpiece']:.1f} mm"], ["테 전체 폭", f"{info['width']:.1f} mm"],
                     ["다리 길이", f"{TEMPLE_LEN:.0f} mm"], ["테 깊이", f"{FRAME_DEPTH:.0f} mm"],
                     ["무게 내역", f"테 {mb['frame_g']} g + 렌즈 {mb['lens_g']} g + 부품 {mb['parts_g']} g"],
                     ["다리 강성 (한쪽)", f"{fe['k_N_per_mm']} N/mm"], ["허용 지속 소비전력", f"{th['P_allow_W']} W (43 °C 기준)"],
                     ["해석 격자", f"{fe['h']} mm · {fe['elements']:,} 요소"]],
        assumptions=[f"렌즈 폭 {geo['lens_w']:.0f} mm 로 사진 축척 환산 (텍스트 '렌즈 52' 로 변경)" if an else "사진이 없어 공개 사진 묘사 기반 기본 형상 사용",
                     f"테 재료 {MAT['name']} E {MAT['E']:.0f} MPa · 항복 {MAT['yield_mpa']:.0f} MPa (일반값)",
                     f"전자부품 {sum(PARTS_G.values()):.0f} g (보드 · 카메라 {PARTS_G['board_camera']} g, 배터리 {PARTS_G['battery']} g, 스피커 · 마이크 {PARTS_G['speakers_mics']} g, 배선 · 힌지 {PARTS_G['wiring_hinges']} g)",
                     "최대 응력 = 절점 응력 상위 0.5 % 제외값 (복셀 계단 모서리의 가짜 응력 집중 제외)",
                     "다리 앞쪽 부품실 · 엔드피스(카메라 · 힌지)는 벽 1 mm 껍데기로 무게 계산, 힌지는 강체 연결로 해석",
                     f"착용 벌림: 머리 폭 ≈ 테 폭 + 10 mm → 다리 끝 한쪽 {SPREAD_EACH:.0f} mm",
                     f"발열: SoC {SOC_W} W 가 방열 시트로 오른쪽 다리 전체에 퍼진다고 보고 h = {H_CONV:.0f} W/m²K 집중 계산",
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
    if photo is not None and an is not None:
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
        a.add_collection(PolyCollection(V[F][:, :, [i, j]], fc="#2b2d31", ec="none"))
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
