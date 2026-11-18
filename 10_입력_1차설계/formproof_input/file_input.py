"""파일 입력 — 문서(PPT · PDF · Word · 글) · CAD(STEP · IGES · STL · DXF) · 이미지 → 같은 입력(요청문 · 형상 그림 · 사양 행).

ingest(name, data) -> dict(
    kind   : 'doc' | 'cad' | 'image'
    name, ext, label (PPT 문서 · STEP 모델 …)
    text   : 문서에서 꺼낸 글 (GUI 가 요청문 칸에 이어 붙임 — 사용자가 보고 고칠 수 있음)
    image  : 형상 그림 PNG data URL (문서 속 가장 큰 그림 · CAD 투영 실루엣) — 스케치가 없을 때 형상 입력으로 씀
    preview: 사람이 보는 미리보기 PNG data URL (CAD 등각 렌더 · 문서 그림)
    rows   : 설계 사양 표에 더할 행 [dict(item, text, basis, source)] — 판정 기준을 바꾸지 않는 '참고 · 확인' 행
    info   : 읽은 값 (치수 · 구멍 · 부피 …), lines: 화면에 보일 요약 줄
    seconds)
CAD 의 구멍은 STEP · IGES 원통면에서 읽음 (STL 은 면 정보가 없어 구멍은 읽지 않음). 해석은 추정이 아니라 읽은 값 그대로 보여 주고,
뜻을 붙이는 값(예: 지름 22–36 mm 구멍 = 핸들바 클램프 후보)은 basis='질문'(확인 필요)으로 둔다."""
import base64
import io
import os
import re
import tempfile
import time

import numpy as np

DOC_EXT = {".pptx": "PPT 문서", ".pdf": "PDF 문서", ".docx": "Word 문서", ".txt": "글 파일", ".md": "글 파일"}
CAD_EXT = {".step": "STEP 모델", ".stp": "STEP 모델", ".igs": "IGES 모델", ".iges": "IGES 모델", ".stl": "STL 메시", ".dxf": "DXF 도면"}
IMG_EXT = {".png": "이미지", ".jpg": "이미지", ".jpeg": "이미지", ".bmp": "이미지", ".webp": "이미지"}
ACCEPT = sorted(DOC_EXT) + sorted(CAD_EXT) + sorted(IMG_EXT)
PETG_G_CM3 = 1.27                                       # integral.MATERIAL (Prusament PETG)
MAX_TEXT = 1200


# ------------------------------------------------------------------ 공통
def _png_url(img):
    """PIL 이미지 → PNG data URL."""
    b = io.BytesIO()
    img.save(b, "PNG")
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()


def _open_img(blob):
    from PIL import Image
    try:
        im = Image.open(io.BytesIO(blob))
        im.load()
        return im
    except Exception:                                    # noqa: BLE001  (EMF · WMF 등 못 여는 그림은 건너뜀)
        return None


def _fit(im, side=800):
    from PIL import Image
    im = im.convert("RGBA")
    bg = Image.new("RGB", im.size, "white")
    bg.paste(im, mask=im.split()[3])
    bg.thumbnail((side, side), Image.LANCZOS)
    return bg


def _clean(lines):
    out, seen = [], set()
    for s in lines:
        s = re.sub(r"^[•·▪■□◦●○\-–*]+\s*", "", re.sub(r"\s+", " ", str(s or "")).strip())
        if s and s not in seen:
            seen.add(s)
            out.append(s)
    return out


def _join(lines):
    t = "\n".join(lines)
    return t if len(t) <= MAX_TEXT else t[:MAX_TEXT].rsplit(" ", 1)[0] + " …"


def _figure(imgs):
    """여러 그림 중 형상 입력으로 쓸 것: 가장 큰(픽셀 수) 그림."""
    imgs = [im for im in imgs if im is not None and min(im.size) >= 64]
    return max(imgs, key=lambda im: im.size[0] * im.size[1]) if imgs else None


# ------------------------------------------------------------------ 문서
def _pptx(data):
    from pptx import Presentation
    from pptx.enum.shapes import MSO_SHAPE_TYPE
    prs = Presentation(io.BytesIO(data))
    lines, imgs = [], []

    def walk(shapes):
        for sh in shapes:
            if sh.shape_type == MSO_SHAPE_TYPE.GROUP:
                walk(sh.shapes)
                continue
            if sh.has_text_frame:
                lines.extend(p.text for p in sh.text_frame.paragraphs)
            if getattr(sh, "has_table", False) and sh.has_table:
                for r in sh.table.rows:
                    lines.append(" · ".join(c.text for c in r.cells if c.text.strip()))
            if sh.shape_type == MSO_SHAPE_TYPE.PICTURE:
                imgs.append(_open_img(sh.image.blob))
    for s in prs.slides:
        walk(s.shapes)
        if s.has_notes_slide:
            lines.extend(s.notes_slide.notes_text_frame.text.splitlines())
    return lines, imgs, dict(pages=len(prs.slides), unit="쪽")


def _pdf(data):
    from pypdf import PdfReader
    rd = PdfReader(io.BytesIO(data))
    lines, imgs = [], []
    for pg in rd.pages:
        lines.extend((pg.extract_text() or "").splitlines())
        try:
            for im in pg.images:
                imgs.append(_open_img(im.data))
        except Exception:                                # noqa: BLE001
            pass
    if not [i for i in imgs if i is not None]:           # 그림이 벡터(선)뿐이면 첫 쪽을 그림으로
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "a.pdf")
            open(p, "wb").write(data)
            os.system(f'pdftoppm -r 80 -f 1 -l 1 -png "{p}" "{d}/pg" >/dev/null 2>&1')
            fs = sorted(f for f in os.listdir(d) if f.startswith("pg"))
            if fs:
                imgs.append(_open_img(open(os.path.join(d, fs[0]), "rb").read()))
    return lines, imgs, dict(pages=len(rd.pages), unit="쪽")


def _docx(data):
    import docx
    d = docx.Document(io.BytesIO(data))
    lines = [p.text for p in d.paragraphs]
    for t in d.tables:
        for r in t.rows:
            lines.append(" · ".join(c.text for c in r.cells if c.text.strip()))
    imgs = [_open_img(rel.target_part.blob) for rel in d.part.rels.values() if "image" in rel.reltype]
    return lines, imgs, {}


def _txt(data):
    for enc in ("utf-8-sig", "cp949", "latin-1"):
        try:
            return data.decode(enc).splitlines(), [], {}
        except UnicodeDecodeError:
            continue
    return [], [], {}


def read_doc(name, data):
    ext = os.path.splitext(name)[1].lower()
    lines, imgs, meta = {".pptx": _pptx, ".pdf": _pdf, ".docx": _docx}.get(ext, _txt)(data)
    lines = _clean(lines)
    fig = _figure(imgs)
    n_img = len([i for i in imgs if i is not None])
    out = dict(kind="doc", text=_join(lines), info=dict(meta, chars=sum(map(len, lines)), images=n_img))
    if fig is not None:
        f = _fit(fig)
        out["image"] = out["preview"] = _png_url(f)
    pages = f"{meta['pages']}{meta['unit']} · " if meta.get("pages") else ""
    out["lines"] = [f"{pages}글 {out['info']['chars']:,}자 · 그림 {n_img}장",
                    "글 → 요청문 칸에 이어 붙임" + (" · 가장 큰 그림 → 형상 입력" if fig is not None else "")]
    out["rows"] = [dict(item="첨부 문서", text=f"{name} — {out['lines'][0]}", basis="문서",
                        source="글은 요청문에 넣어 함께 읽음" + (" · 그림은 스케치가 없을 때 형상 입력" if fig is not None else ""))]
    return out


# ------------------------------------------------------------------ CAD
def _render(tris, title=""):
    """삼각형 (N,3,3) → (실루엣 그림, 등각 미리보기). 실루엣 = 가장 넓게 보이는 축 방향 투영 (형상 입력용)."""
    from PIL import Image, ImageDraw
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    P = tris.reshape(-1, 3)
    lo, hi = P.min(0), P.max(0)
    ext = hi - lo
    ax_drop = int(np.argmin(ext))                        # 가장 얇은 축을 버리면 가장 넓은 면이 보임
    keep = [i for i in range(3) if i != ax_drop]
    W = 800
    s = (W - 80) / max(ext[keep].max(), 1e-9)
    sil = Image.new("L", (W, W), 255)
    d = ImageDraw.Draw(sil)
    for t in tris:
        q = [((p[keep[0]] - lo[keep[0]]) * s + 40, W - ((p[keep[1]] - lo[keep[1]]) * s + 40)) for p in t]
        d.polygon(q, fill=0)
    # 스케치처럼 외곽선만 (채운 면 → 경계 3 px)
    from PIL import ImageFilter, ImageChops
    m = sil.point(lambda v: 255 if v < 128 else 0)
    edge = ImageChops.subtract(m.filter(ImageFilter.MaxFilter(5)), m.filter(ImageFilter.MinFilter(3)))
    sil = edge.point(lambda v: 0 if v > 0 else 255)
    # 등각 미리보기
    fig = plt.figure(figsize=(4, 4), dpi=110)
    ax = fig.add_subplot(111, projection="3d")
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    light = np.array([0.4, -0.5, 0.75]) / np.linalg.norm([0.4, -0.5, 0.75])
    sh = 0.35 + 0.65 * np.abs(n @ light)
    col = np.c_[0.30 * sh, 0.62 * sh, 0.78 * sh, np.ones(len(sh))]
    ax.add_collection3d(Poly3DCollection(tris, facecolors=col, edgecolor="none"))
    c, r = (lo + hi) / 2, ext.max() / 2
    ax.set_xlim(c[0] - r, c[0] + r); ax.set_ylim(c[1] - r, c[1] + r); ax.set_zlim(c[2] - r, c[2] + r)
    ax.view_init(24, -58); ax.set_axis_off(); ax.set_box_aspect((1, 1, 1))
    fig.subplots_adjust(0, 0, 1, 1)
    b = io.BytesIO(); fig.savefig(b, format="png", facecolor="white"); plt.close(fig)
    return sil.convert("RGB"), Image.open(io.BytesIO(b.getvalue())).convert("RGB")


def _holes_occ(shape):
    """STEP/IGES 원통면 → 구멍(안쪽을 향한 원통) 지름 목록 {지름: 개수} — 같은 축 · 같은 지름은 하나로."""
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.GeomAbs import GeomAbs_Cylinder
    from OCP.BRepGProp import BRepGProp_Face
    from OCP.gp import gp_Pnt, gp_Vec
    found = []
    for f in shape.Faces():
        ad = BRepAdaptor_Surface(f.wrapped)
        if ad.GetType() != GeomAbs_Cylinder:
            continue
        cyl = ad.Cylinder()
        r = cyl.Radius()
        ax = cyl.Axis()
        o, dv = np.array(ax.Location().Coord()), np.array(ax.Direction().Coord())
        u = (ad.FirstUParameter() + ad.LastUParameter()) / 2
        v = (ad.FirstVParameter() + ad.LastVParameter()) / 2
        pt, vec = gp_Pnt(), gp_Vec()
        BRepGProp_Face(f.wrapped).Normal(u, v, pt, vec)  # 면 방향(orientation)을 반영한 법선
        p, nv = np.array(pt.Coord()), np.array([vec.X(), vec.Y(), vec.Z()])
        radial = (p - o) - np.dot(p - o, dv) * dv
        if np.linalg.norm(radial) < 1e-9:
            continue
        hole = np.dot(nv, radial) < 0                    # 면 법선이 축 쪽 = 구멍 (바깥쪽 = 축 · 보스)
        key = (round(2 * r, 1), tuple(np.round(o - np.dot(o, dv) * dv, 1)), tuple(np.round(np.abs(dv), 2)))
        found.append((hole, key))
    holes = {}
    for hole, key in dict.fromkeys(found):
        if hole:
            holes[key[0]] = holes.get(key[0], 0) + 1
    return dict(sorted(holes.items(), key=lambda kv: -kv[0]))


def _cad_rows(name, info):
    L, W_, H = info["size"]
    rows = ([dict(item="도면 범위", text=f"{L:.0f} × {W_:.0f} mm", basis="CAD", source=f"{name} 모든 선의 경계 (도면 틀 포함)")]
            if info.get("dxf") else [dict(item="외곽 치수", text=f"{L:.1f} × {W_:.1f} × {H:.1f} mm", basis="CAD", source=f"{name} 경계 상자")])
    if info.get("volume_cm3"):
        rows.append(dict(item="부피 · 무게", text=f"{info['volume_cm3']:.1f} cm³ · PETG면 {info['mass_g']:.1f} g",
                         basis="CAD", source=f"{name} 부피 × PETG {PETG_G_CM3} g/cm³ (기존 부품 무게 비교용)"))
    if info.get("holes"):
        rows.append(dict(item="구멍", text=" · ".join(f"Ø{d:g} × {n}" for d, n in list(info["holes"].items())[:5]) + " mm",
                         basis="CAD", source=f"{name} 원통면"))
        clamp = [d for d in info["holes"] if 22 <= d <= 36]
        if clamp:
            rows.append(dict(item="핸들바 클램프 지름 (후보)", text=f"Ø{clamp[0]:g} mm", basis="질문",
                             source="지름 22–36 mm 구멍 = 핸들바(22.2 · 25.4 · 31.8 · 35 mm) 후보 → 확인 필요"))
    if info.get("dims"):
        rows.append(dict(item="도면 치수 기입", text=" · ".join(info["dims"][:8]), basis="CAD", source=f"{name} DIMENSION"))
    if info.get("circles"):
        rows.append(dict(item="원 · 구멍", text=" · ".join(f"Ø{d:g} × {n}" for d, n in list(info["circles"].items())[:5]) + " mm",
                         basis="CAD", source=f"{name} CIRCLE"))
    return rows


def read_cad(name, data):
    ext = os.path.splitext(name)[1].lower()
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "in" + ext)
        open(p, "wb").write(data)
        if ext == ".dxf":
            return _dxf(name, p)
        info = {}
        if ext in (".step", ".stp", ".igs", ".iges"):
            import cadquery as cq
            if ext in (".step", ".stp"):
                vals = cq.importers.importStep(p).vals()
                shp = vals[0] if len(vals) == 1 else cq.Compound.makeCompound(vals)
            else:
                shp = _iges(p)
            bb = shp.BoundingBox()
            info["size"] = [bb.xlen, bb.ylen, bb.zlen]
            v = shp.Volume() / 1000.0
            if v > 1e-6:
                info["volume_cm3"], info["mass_g"] = round(v, 2), round(v * PETG_G_CM3, 1)
            info["holes"] = _holes_occ(shp)
            info["faces"] = len(shp.Faces())
            vs, fs = shp.tessellate(max(0.2, max(info["size"]) / 400))
            V = np.array([[q.x, q.y, q.z] for q in vs])
            tris = V[np.array(fs)]
        else:                                            # STL
            import trimesh
            m = trimesh.load(p, force="mesh")
            info["size"] = list(map(float, m.extents))
            if m.is_watertight:
                v = abs(m.volume) / 1000.0
                info["volume_cm3"], info["mass_g"] = round(v, 2), round(v * PETG_G_CM3, 1)
            info["triangles"] = int(len(m.faces))
            tris = m.triangles
            if len(tris) > 60000:
                tris = tris[np.random.default_rng(0).choice(len(tris), 60000, replace=False)]
        sil, iso = _render(np.asarray(tris, float))
    out = dict(kind="cad", info=info, image=_png_url(sil), preview=_png_url(iso), text="")
    L, W_, H = info["size"]
    lines = [f"{L:.0f} × {W_:.0f} × {H:.0f} mm" + (f" · {info['mass_g']:g} g (PETG)" if info.get("mass_g") else "")]
    if info.get("holes"):
        lines.append("구멍 " + " · ".join(f"Ø{d:g}×{n}" for d, n in list(info["holes"].items())[:4]))
    elif ext == ".stl":
        lines.append("STL 은 면 정보가 없어 구멍은 읽지 않음")
    out["lines"] = lines
    out["rows"] = _cad_rows(name, info)
    return out


def _iges(p):
    from OCP.IGESControl import IGESControl_Reader
    import cadquery as cq
    r = IGESControl_Reader()
    r.ReadFile(p)
    r.TransferRoots()
    return cq.Shape.cast(r.OneShape())


def _dxf(name, p):
    import ezdxf
    from ezdxf import bbox
    doc = ezdxf.readfile(p)
    msp = doc.modelspace()
    ext = bbox.extents(msp)
    size = [ext.size.x, ext.size.y, 0.0] if ext.has_data else [0.0, 0.0, 0.0]
    circ = {}
    for c in msp.query("CIRCLE"):
        k = round(2 * c.dxf.radius, 1)
        circ[k] = circ.get(k, 0) + 1
    dims = []
    for dm in msp.query("DIMENSION"):
        try:
            v = dm.get_measurement()
            v = float(v) if not hasattr(v, "x") else float(np.hypot(v.x, v.y))
            t = dm.dxf.get("text", "")
            dims.append(t if t and t != "<>" else f"{v:g}")
        except Exception:                                # noqa: BLE001
            pass
    notes = _clean([t.dxf.text for t in msp.query("TEXT")] + [m.plain_text() for m in msp.query("MTEXT")])
    info = dict(dxf=True, size=size, circles=dict(sorted(circ.items(), key=lambda kv: -kv[0])), dims=_clean(dims), notes=len(notes))
    # 그림 (ezdxf drawing → matplotlib)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    from PIL import Image
    fig = plt.figure(figsize=(6, 6), dpi=110)
    ax = fig.add_axes([0, 0, 1, 1])
    Frontend(RenderContext(doc), MatplotlibBackend(ax)).draw_layout(msp)
    ax.set_axis_off()
    b = io.BytesIO(); fig.savefig(b, format="png", facecolor="white"); plt.close(fig)
    im = Image.open(io.BytesIO(b.getvalue())).convert("RGB")
    out = dict(kind="cad", info=info, image=_png_url(im), preview=_png_url(im), text=_join(notes))
    out["lines"] = [f"{size[0]:.0f} × {size[1]:.0f} mm · 치수 {len(info['dims'])}개 · 원 {sum(circ.values())}개",
                    f"주석 {len(notes)}줄 → 요청문 칸에 이어 붙임" if notes else "주석 없음"]
    out["rows"] = _cad_rows(name, info)
    return out


# ------------------------------------------------------------------ 진입점
def ingest(name, data):
    t = time.time()
    ext = os.path.splitext(name or "")[1].lower()
    if ext in DOC_EXT:
        out, label = read_doc(name, data), DOC_EXT[ext]
    elif ext in CAD_EXT:
        out, label = read_cad(name, data), CAD_EXT[ext]
    elif ext in IMG_EXT:
        im = _open_img(data)
        if im is None:
            raise ValueError("이미지를 열지 못했습니다.")
        f = _fit(im)
        out, label = dict(kind="image", text="", image=_png_url(f), preview=_png_url(f), info=dict(size=list(im.size)),
                          lines=[f"{im.size[0]} × {im.size[1]} px → 형상 입력"], rows=[]), IMG_EXT[ext]
    else:
        raise ValueError(f"읽을 수 없는 형식입니다 ({ext or '확장자 없음'}). 가능한 형식: " + " ".join(ACCEPT))
    out.update(name=name, ext=ext, label=label, seconds=round(time.time() - t, 2))
    return out


def decode(data_url):
    """'data:...;base64,xxxx' 또는 base64 문자열 → bytes."""
    return base64.b64decode(data_url.split(",", 1)[1] if data_url.startswith("data:") else data_url)
