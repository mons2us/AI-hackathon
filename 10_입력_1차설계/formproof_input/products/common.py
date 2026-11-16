"""Report shape shared by the demo products (TV stand, AR glasses) — read by the GUI's renderProduct()."""
import base64
import json
import os
import zipfile

import numpy as np

HANDOFF = ["spec.json", "report.json", "design_1st.step", "design_1st.stl", "design_1st_drawing.pdf"]


def base_report(product, tid, tname, tdesc, chosen_by, match, rows, conditions, summary, design_vars, assumptions,
                sources, cad, extra=None, seconds=0.0, analysis=None):
    ok = all(r["ok"] for r in rows)
    return dict(kind="product", product=product,
                template=dict(id=tid, name=tname, desc=tdesc, chosen_by=chosen_by, match=match),
                judge=dict(rows=rows, pass_=ok, fails=[r["name"] for r in rows if not r["ok"]]),
                conditions=conditions, summary=summary, design_vars=design_vars, assumptions=assumptions,
                sources=sources, cad=cad, analysis=analysis, extra=extra or {}, seconds=round(seconds, 2),
                text=dict(fired=[c for c in conditions if c.get("source", "").startswith(("근거", "IEC", "ISO", "텍스트", "스케치", "사진"))],
                          questions=[]))


def finish(rep, out):
    spec = dict(format="formproof.spec/0.1", kind=rep["product"], template=rep["template"]["id"],
                conditions=rep["conditions"], criteria=[{k: r[k] for k in ("name", "op", "limit", "unit", "source")} for r in rep["judge"]["rows"]],
                assumptions=rep["assumptions"], sources=rep["sources"], design_vars=rep["design_vars"])
    with open(os.path.join(out, "spec.json"), "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=1, default=_np)
    with open(os.path.join(out, "report.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1, default=_np)
    with zipfile.ZipFile(os.path.join(out, "handoff.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for n in HANDOFF + ["side_view.png", "design_1st_drawing.png", "analysis.png"]:
            if os.path.exists(os.path.join(out, n)):
                z.write(os.path.join(out, n), n)


def _np(o):
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def mesh_b64(body, tol=0.3):
    verts, tris = body.val().tessellate(tol, 0.3)
    v = np.array([[p.x, p.y, p.z] for p in verts], np.float32)
    pos = v[np.array(tris, np.int64)].reshape(-1, 3).astype(np.float32)
    return dict(pos=base64.b64encode(pos.tobytes()).decode(), triangles=int(len(tris)))


def trimesh_b64(m):
    pos = np.asarray(m.vertices)[np.asarray(m.faces)].reshape(-1, 3).astype(np.float32)
    return dict(pos=base64.b64encode(pos.tobytes()).decode(), triangles=int(len(m.faces)))
