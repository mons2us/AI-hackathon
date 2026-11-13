"""FormProof input-stage GUI — local server (Python standard library only, no internet needed).

  python app/server.py            -> http://localhost:8765
  python app/server.py --port 9000 --no-browser

The page sends text + sketch (canvas PNG) or an attached image; the server runs the CPU pipeline
(formproof_input.pipeline.design) and returns the 1st design (CAD mesh for the 3D view, drawing,
performance check, hand-off conditions) plus the hand-off files."""
import argparse
import json
import mimetypes
import os
import sys
import threading
import time
import traceback
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

APP = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(APP)
sys.path.insert(0, ROOT)

from formproof_input import pipeline                       # noqa: E402
from formproof_input.templates.library import TEMPLATES    # noqa: E402

STATIC = os.path.join(APP, "static")
RUNS = os.path.join(APP, "runs")
EXAMPLES = os.path.join(ROOT, "examples")
LOCK = threading.Lock()                                    # one design at a time (matplotlib / OCC are not thread-safe)
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("model/step", ".step")
mimetypes.add_type("model/stl", ".stl")


def _safe_join(base, rel):
    p = os.path.realpath(os.path.join(base, rel))
    return p if p.startswith(os.path.realpath(base) + os.sep) and os.path.isfile(p) else None


class Handler(BaseHTTPRequestHandler):
    server_version = "FormProofInput/1.0"

    def log_message(self, fmt, *args):
        sys.stderr.write("[%s] %s\n" % (time.strftime("%H:%M:%S"), fmt % args))

    def _send(self, code, body, ctype="application/json; charset=utf-8", extra=None):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path, download=False):
        if not path:
            return self._send(404, {"error": "not found"})
        ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
        extra = {"Content-Disposition": f"attachment; filename*=UTF-8''{os.path.basename(path)}"} if download else None
        with open(path, "rb") as f:
            self._send(200, f.read(), ctype, extra)

    def do_GET(self):
        u = urlparse(self.path)
        p = unquote(u.path)
        if p == "/favicon.ico":
            return self._send(204, b"", "image/x-icon")
        if p in ("/", "/index.html"):
            return self._file(os.path.join(STATIC, "index.html"))
        if p.startswith("/static/"):
            return self._file(_safe_join(STATIC, p[len("/static/"):]))
        if p.startswith("/examples/"):
            return self._file(_safe_join(EXAMPLES, p[len("/examples/"):]))
        if p.startswith("/runs/"):
            return self._file(_safe_join(RUNS, p[len("/runs/"):]), download="dl=1" in (u.query or ""))
        if p == "/api/templates":
            return self._send(200, [dict(id=t["id"], name=t["name"], desc=t["desc"],
                                         thumb=f"/examples/templates/{t['id']}.png") for t in TEMPLATES])
        if p == "/api/examples":
            hand = sorted(f for f in os.listdir(os.path.join(EXAMPLES, "hand")) if f.endswith(".png"))
            return self._send(200, [f"/examples/hand/{f}" for f in hand])
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        if urlparse(self.path).path != "/api/design":
            return self._send(404, {"error": "not found"})
        try:
            n = int(self.headers.get("Content-Length", 0))
            req = json.loads(self.rfile.read(n).decode("utf-8"))
            sketch = pipeline.decode_image(req["sketch"]) if req.get("sketch") else None
            image = pipeline.decode_image(req["image"]) if req.get("image") else None
            rid = time.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
            out = os.path.join(RUNS, rid)
            with LOCK:
                rep = pipeline.design(req.get("text", ""), sketch, image, req.get("template") or None, out, with_mesh=True)
            rep["run_id"] = rid
            rep["files"] = {name: f"/runs/{rid}/{name}" for name in sorted(os.listdir(out))}
            return self._send(200, rep)
        except Exception as e:                                          # show the reason in the page
            traceback.print_exc()
            msg = str(e)
            if "no strokes" in msg:
                msg = "스케치나 이미지에서 선을 찾지 못했습니다. 조금 더 진하게 그려 주세요."
            return self._send(400, {"error": msg})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args()
    os.makedirs(RUNS, exist_ok=True)
    t = time.time()
    pipeline.matcher()                                     # warm up: template references for sketch matching
    import cadquery  # noqa: F401  (first import is slow; do it before the first request)
    print(f"준비 완료 ({time.time() - t:.1f}s) → http://localhost:{a.port}", flush=True)
    srv = ThreadingHTTPServer((a.host, a.port), Handler)
    if not a.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(f"http://localhost:{a.port}")).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
