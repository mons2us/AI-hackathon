"""2-D drawing of the 1st design: third-angle views (front / top / right) + isometric, dimensions taken
from spec["geometry"], title block with material and design conditions. Output: DXF (ezdxf) and PDF.

Views are hidden-line projections of the same B-rep as the STEP (OpenCascade HLR), so the drawing,
STEP and analysis grid share one geometry."""
import math
import os

import ezdxf
from ezdxf.enums import TextEntityAlignment
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

A4, A3 = (297.0, 210.0), (420.0, 297.0)   # landscape, mm
SHEETS = [(A4, 1.0), (A3, 1.0), (A3, 0.5)]
SHEET = A4
MARGIN = 10.0
TITLE_H = 36.0

# view direction N (toward the viewer) and horizontal axis Vx; vertical = N x Vx
VIEWS = {
    "front": ((0, -1, 0), (1, 0, 0)),     # x right, z up   (정면도)
    "top": ((0, 0, 1), (1, 0, 0)),        # x right, y up   (평면도, 정면도 위)
    "right": ((1, 0, 0), (0, 1, 0)),      # y right, z up   (우측면도, 정면도 오른쪽)
    "iso": ((1, -1, 1), (1, 1, 0)),
}


def _edges_to_polylines(compound, defl=0.05):
    out = []
    if compound is None or compound.IsNull():
        return out
    exp = TopExp_Explorer(compound, TopAbs_EDGE)
    while exp.More():
        e = TopoDS.Edge_s(exp.Current())
        c = BRepAdaptor_Curve(e)
        d = GCPnts_QuasiUniformDeflection(c, defl)
        if d.IsDone() and d.NbPoints() >= 2:
            pts = [(d.Value(i).X(), d.Value(i).Y()) for i in range(1, d.NbPoints() + 1)]
            out.append(pts)
        exp.Next()
    return out


def project(shape, view):
    n, vx = VIEWS[view]
    nn = math.sqrt(sum(v * v for v in n))
    nv = math.sqrt(sum(v * v for v in vx))
    ax = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*[v / nn for v in n]), gp_Dir(*[v / nv for v in vx]))
    algo = HLRBRep_Algo()
    algo.Add(shape)
    algo.Projector(HLRAlgo_Projector(ax))
    algo.Update()
    algo.Hide()
    h = HLRBRep_HLRToShape(algo)
    vis = []
    for comp in (h.VCompound(), h.OutLineVCompound(), h.Rg1LineVCompound()):
        vis += _edges_to_polylines(comp)
    hid = []
    if view != "iso":
        for comp in (h.HCompound(), h.OutLineHCompound()):
            hid += _edges_to_polylines(comp)
    return vis, hid


def _bounds(polys):
    xs = [p[0] for pl in polys for p in pl]
    ys = [p[1] for pl in polys for p in pl]
    return min(xs), min(ys), max(xs), max(ys)


class Sheet:
    def __init__(self, font):
        self.doc = ezdxf.new("R2010", setup=True)
        self.doc.units = ezdxf.units.MM
        for name, color, lt in (("OUTLINE", 7, "CONTINUOUS"), ("HIDDEN", 8, "DASHED"), ("CENTER", 1, "CENTER"),
                                ("DIM", 3, "CONTINUOUS"), ("TEXT", 7, "CONTINUOUS"), ("FRAME", 7, "CONTINUOUS")):
            self.doc.layers.add(name, color=color, linetype=lt)
        self.doc.styles.add("KR", font=font)
        ds = self.doc.dimstyles.duplicate_entry("EZDXF", "KRDIM")
        ds.dxf.dimtxsty = "KR"
        ds.dxf.dimtxt = 2.5
        ds.dxf.dimasz = 2.0
        ds.dxf.dimexo = 1.0
        ds.dxf.dimexe = 1.5
        ds.dxf.dimdec = 1
        ds.dxf.dimzin = 8
        self.msp = self.doc.modelspace()

    def poly(self, pts, layer, closed=False):
        self.msp.add_lwpolyline(pts, close=closed, dxfattribs={"layer": layer})

    def text(self, s, pos, h=2.5, align=TextEntityAlignment.LEFT, layer="TEXT"):
        t = self.msp.add_text(s, height=h, dxfattribs={"layer": layer, "style": "KR"})
        t.set_placement(pos, align=align)

    def dim(self, p1, p2, base, angle=0):
        d = self.msp.add_linear_dim(base=base, p1=p1, p2=p2, angle=angle, dimstyle="KRDIM",
                                    dxfattribs={"layer": "DIM"})
        d.render()

    def dia(self, centre, r, angle_deg, text=None):
        d = self.msp.add_diameter_dim(center=centre, radius=r, angle=angle_deg, dimstyle="KRDIM",
                                      text=text or "<>", dxfattribs={"layer": "DIM"},
                                      override={"dimtmove": 1})
        d.render()


def make_drawing(spec, body, out_dxf, out_pdf=None, title=None, check=None, mass_g=None, req=None):
    """body = CadQuery Workplane of the 1st design (with holes)."""
    font = "malgun.ttf"                       # Windows (사내 PC) font for the DXF
    g = spec["geometry"]
    shape = body.val().wrapped
    proj = {v: project(shape, v) for v in VIEWS}

    fb = _bounds(proj["front"][0])
    tb = _bounds(proj["top"][0])
    rb = _bounds(proj["right"][0])
    ib = _bounds(proj["iso"][0])
    w_front, h_front = fb[2] - fb[0], fb[3] - fb[1]
    w_right = rb[2] - rb[0]
    h_top = tb[3] - tb[1]
    DIM_OFF = 8.0                        # paper mm between dimension rows
    gap_v, gap_h = 24.0, 32.0            # front->top (room for pad dim), front->right (room for 2 height dims)
    LEFT_ROOM = 54.0                     # bore-diameter note sits left of the front view
    fx0 = MARGIN + LEFT_ROOM
    fy0 = MARGIN + TITLE_H + 2 * DIM_OFF + 6            # two dimension rows under the front view
    sheet, scale = SHEETS[-1]
    for sh_size, s in SHEETS:                           # A4 1:1 -> A3 1:1 -> A3 1:2
        fits_h = fy0 + (h_front + h_top) * s + gap_v + 8 <= sh_size[1] - MARGIN
        fits_w = fx0 + (w_front + w_right) * s + gap_h <= sh_size[0] - MARGIN - 8
        if fits_h and fits_w:
            sheet, scale = sh_size, s
            break
    W, H = sheet

    sh = Sheet(font)
    # third angle: front lower-left, top above it, right side to its right
    place = {
        "front": (fx0 - fb[0] * scale, fy0 - fb[1] * scale),
        "top": (fx0 - tb[0] * scale, fy0 + h_front * scale + gap_v - tb[1] * scale),
        "right": (fx0 + w_front * scale + gap_h - rb[0] * scale, fy0 - rb[1] * scale),
    }
    # isometric: largest free rectangle (right of the right view / above the right view / above the top view)
    right_x1 = fx0 + (w_front + w_right) * scale + gap_h
    top_x1 = fx0 + w_front * scale
    top_y1 = fy0 + (h_front + h_top) * scale + gap_v
    regions = [
        (right_x1 + 12, MARGIN + TITLE_H + 8, W - MARGIN - 4, H - MARGIN - 4),
        (top_x1 + 14, fy0 + h_front * scale + 14, W - MARGIN - 4, H - MARGIN - 4),
        (fx0, top_y1 + 10, W - MARGIN - 4, H - MARGIN - 4),
    ]
    iw, ih = ib[2] - ib[0], ib[3] - ib[1]
    best = max(((min((r[2] - r[0]) / iw, (r[3] - r[1] - 8) / ih, scale), r) for r in regions if r[2] > r[0] and r[3] > r[1]),
               key=lambda x: x[0])
    iso_s, r = best
    ix = (r[0] + r[2]) / 2 - iw * iso_s / 2
    iy = r[3] - ih * iso_s
    place["iso"] = (ix - ib[0] * iso_s, iy - ib[1] * iso_s)

    def tf(view, x, y):
        ox, oy = place[view]
        s = iso_s if view == "iso" else scale
        return (ox + x * s, oy + y * s)

    for v, (vis, hid) in proj.items():
        for pl in vis:
            sh.poly([tf(v, *p) for p in pl], "OUTLINE")
        for pl in hid:
            sh.poly([tf(v, *p) for p in pl], "HIDDEN")

    # centre lines: handlebar axis in front view, symmetry plane in top/right views
    ro = g["ring_ro"]
    for a, b in (((-ro - 4, 0), (ro + 4, 0)), ((0, -ro - 4), (0, ro + 4))):
        sh.poly([tf("front", *a), tf("front", *b)], "CENTER")
    y0 = g["y_sym"]
    sh.poly([tf("top", tb[0] - 4, y0), tf("top", tb[2] + 4, y0)], "CENTER")
    sh.poly([tf("right", y0, rb[1] - 4), tf("right", y0, rb[3] + 4)], "CENTER")

    # --- dimensions (all values from spec geometry, written at true size: DIMLFAC = 1/scale)
    sh.doc.dimstyles.get("KRDIM").dxf.dimlfac = 1.0 / scale
    (px0, px1), (pz0, pz1) = g["pad"]["x"], g["pad"]["z"]
    mh = g["mount_hole"]
    xl, xr = fb[0], fb[2]
    zb, zt = fb[1], fb[3]
    off = DIM_OFF / scale
    sh.dim(tf("front", xl, zb), tf("front", xr, zb), tf("front", 0, zb - off))                   # overall length
    sh.dim(tf("front", 0, 0), tf("front", mh["x"], 0), tf("front", 0, zb - 2 * off))            # reach
    sh.dim(tf("front", xr, 0), tf("front", xr, pz1), tf("front", xr + off, 0), angle=90)        # pad height
    sh.dim(tf("front", xr, zb), tf("front", xr, zt), tf("front", xr + 2 * off, 0), angle=90)    # overall height
    sh.dim(tf("front", px0, pz1), tf("front", px1, pz1), tf("front", 0, zt + off * 0.8))        # pad length
    # bore diameter as a leader note (keeps the text off the ring)
    a = math.radians(160)
    p0 = (g["bore_r"] * math.cos(a), g["bore_r"] * math.sin(a))
    q0 = tf("front", *p0)
    q1 = (tf("front", -ro, 0)[0] - 6.0, tf("front", 0, ro)[1] + 4.0)      # up-left, outside the ring
    sh.poly([q0, q1, (q1[0] - 3, q1[1])], "DIM")
    u = ((q0[0] - q1[0]), (q0[1] - q1[1]))
    n = math.hypot(*u)
    u = (u[0] / n, u[1] / n)
    v = (-u[1], u[0])
    sh.msp.add_solid([q0, (q0[0] - 2.2 * u[0] + 0.6 * v[0], q0[1] - 2.2 * u[1] + 0.6 * v[1]),
                      (q0[0] - 2.2 * u[0] - 0.6 * v[0], q0[1] - 2.2 * u[1] - 0.6 * v[1])], dxfattribs={"layer": "DIM"})
    sh.text(f"Ø{2 * g['bore_r']:.1f}", (q1[0] - 4, q1[1] + 0.8), 2.5, TextEntityAlignment.BOTTOM_RIGHT, layer="DIM")
    sh.text(f"(핸들바 Ø{g['bar_d']})", (q1[0] - 4, q1[1] - 0.8), 2.2, TextEntityAlignment.TOP_RIGHT, layer="DIM")
    w = g["width"]
    sh.dim(tf("top", tb[2], y0 - w / 2), tf("top", tb[2], y0 + w / 2), tf("top", tb[2] + off, 0), angle=90)
    b = g["bolts"]
    sh.dim(tf("right", b["y"][0], b["z"]), tf("right", b["y"][1], b["z"]), tf("right", 0, rb[1] - off))

    # notes on holes / arm
    sh.text(f"2×Ø{b['d']} 관통", (tf("right", rb[0], 0)[0], fy0 - DIM_OFF - 6), 2.2)
    sh.text("(M4 볼트)", (tf("right", rb[0], 0)[0], fy0 - DIM_OFF - 10), 2.2)
    sh.text(f"Ø{mh['d']:.0f} 폰 클램프 체결 구멍", (tf("top", mh["x"], 0)[0], tf("top", 0, tb[3])[1] + 2), 2.2,
            TextEntityAlignment.BOTTOM_CENTER)
    for v, label in (("front", "정면도"), ("top", "평면도"), ("right", "우측면도")):
        bx = {"front": fb, "top": tb, "right": rb}[v]
        sh.text(label, tf(v, (bx[0] + bx[2]) / 2, bx[3]) if v != "front" else tf(v, (bx[0] + bx[2]) / 2, bx[3]),
                2.8, TextEntityAlignment.BOTTOM_CENTER)
    sh.text("등각도", (ix + (ib[2] - ib[0]) * iso_s / 2, iy - 4), 2.8, TextEntityAlignment.TOP_CENTER)

    # --- frame + title block
    sh.poly([(MARGIN, MARGIN), (W - MARGIN, MARGIN), (W - MARGIN, H - MARGIN), (MARGIN, H - MARGIN)], "FRAME", True)
    tx0, ty0, tx1, ty1 = MARGIN, MARGIN, W - MARGIN, MARGIN + TITLE_H
    sh.poly([(tx0, ty1), (tx1, ty1)], "FRAME")
    cols = [tx0, tx0 + 95, tx0 + 165, tx1]
    for x in cols[1:-1]:
        sh.poly([(x, ty0), (x, ty1)], "FRAME")
    tpl = spec["template"]
    cons = {c["id"]: c for c in spec["constraints"]}
    pm = spec["point_masses"][0]
    road = next(c for c in spec["load_cases"] if c["type"] == "modal")
    shock = next(c for c in spec["load_cases"] if c["name"] == "shock_vertical")
    lines_a = [
        (title or "자전거 폰 거치대 — 1차 설계", 4.0),
        (f"템플릿 {tpl['id']} {tpl.get('name', '')} · 팔 {g['arm']['style']}", 2.6),
        ("FormProof 입력 단계 산출 (물리 최적화 전)", 2.4),
        (f"척도 1:{1 / scale:g} · 제3각법 · 단위 mm · {'A4' if sheet == A4 else 'A3'} · 팔 두께 {g['arm']['t']:g}", 2.4),
    ]
    lines_b = [
        (f"재료 {spec['material']['name']} (E {spec['material']['E'] / 1000:.1f} GPa, 항복 {spec['material']['yield_mpa']:g} MPa)", 2.2),
        (f"질량 {mass_g:.1f} g (CAD)" if mass_g else "질량 -", 2.2),
        (f"핸들바 Ø{g['bar_d']} · 폭 {w:g} · M4 볼트 2개", 2.2),
        (f"폰+클램프 {pm['mass_kg'] * 1e3:.0f} g · 출력 색 {'흰색' if spec.get('finish', {}).get('colour') == 'white' else '검정'}", 2.2),
    ]
    req = req or {}
    if "sun_heat" in req:
        r = req["sun_heat"]
        mine = next(x for x in r["rows"] if x["colour"] == r["colour"])
        lines_b.append((f"땡볕: 주차 {mine['parked_c']} °C ≤ {mine['limit_c']} °C {'충족' if r['pass_'] else '미충족'}", 2.2))
    if "free_angle" in req:
        r = req["free_angle"]
        t = r["tilt_now"]
        lines_b.append((f"각도: 360° 회전, 기울기 세로 {t['portrait']['down_deg']}~+{t['portrait']['up_deg']}° "
                        f"{'충족' if r['pass_'] else '미충족'}", 2.2))
    lines_c = [
        ("설계 조건 (물리 최적화 기준)", 2.4),
        (f"노면 {road['excitation_hz'][0]}–{road['excitation_hz'][1]} Hz, 충격 {shock['accel_g']} g", 2.2),
        (f"1차 진동 ≥ {cons['f1']['value']} Hz · 응력 ≤ {cons['stress']['value']} MPa", 2.2),
        (f"층간 ≤ {cons['interlayer']['value']} MPa · 최소 두께 {cons['min_feature']['value']:g}", 2.2),
    ]
    if check:
        ok = "충족" if check.get("pass") else "미충족 → 최적화 대상"
        lines_c.append((f"1차 설계 판정: f1 {check['f1_hz']} Hz, 응력 {check['checks']['stress']['value']} MPa — {ok}", 2.2))
    for col, lines in ((0, lines_a), (1, lines_b), (2, lines_c)):
        y = ty1 - 6
        for s, hgt in lines:
            sh.text(s, (cols[col] + 3, y), hgt)
            y -= hgt + 3.2

    os.makedirs(os.path.dirname(os.path.abspath(out_dxf)), exist_ok=True)
    sh.doc.saveas(out_dxf)
    if out_pdf:
        _render_pdf(sh.doc, out_pdf, sheet)
    return dict(sheet="A4" if sheet == A4 else "A3", scale=f"1:{1 / scale:g}", views=list(VIEWS), dxf=os.path.basename(out_dxf),
                pdf=os.path.basename(out_pdf) if out_pdf else None)


def _render_pdf(doc, path, sheet=A4):
    """Render the DXF to PDF with an installed CJK font (the DXF itself keeps malgun.ttf)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy, ColorPolicy
    from ezdxf.fonts import fonts as F
    style = doc.styles.get("KR")
    keep = style.dxf.font
    for cand in ("malgun.ttf", "NanumGothic.ttf", "NotoSansCJK-Regular.ttc", "AppleGothic.ttf"):
        if F.font_manager.has_font(cand):
            style.dxf.font = cand
            break
    fig = plt.figure(figsize=(sheet[0] / 25.4, sheet[1] / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    cfg = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.BLACK,
                        min_lineweight=0.18)
    Frontend(RenderContext(doc), MatplotlibBackend(ax), config=cfg).draw_layout(doc.modelspace())
    ax.set_xlim(0, sheet[0])
    ax.set_ylim(0, sheet[1])
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig(path)
    if path.endswith(".pdf"):
        fig.savefig(path[:-4] + ".png", dpi=150)
    plt.close(fig)
    style.dxf.font = keep
