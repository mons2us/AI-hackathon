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

from formproof_input import pipeline, progress             # noqa: E402
from formproof_input.templates.library import ALL as TEMPLATES    # noqa: E402

STATIC = os.path.join(APP, "static")
RUNS = os.path.join(APP, "runs")
EXAMPLES = os.path.join(ROOT, "examples")
LOCK = threading.Lock()                                    # one design at a time (matplotlib / OCC are not thread-safe)
APP_VERSION = "2026-11-16c"                                 # index.html 의 APP_V 와 같아야 함 (화면 · 서버 버전 확인)
JOBS = {}
WAITING = [0]                                              # 계산 차례를 기다리는 사용자 요청 수 (뒤 DB 채우기보다 먼저)
WAIT_LOCK = threading.Lock()
FILL = dict(active=False, i=0, n=0, name="")               # 템플릿 결과 DB 채우는 중인지 (대기 문구에 씀)                                                  # job id -> 진행 상태 (단계 이름 · 시작 시각 · 끝난 단계 · 결과)
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
        if p == "/api/version":
            return self._send(200, {"version": APP_VERSION, "pid": os.getpid()})
        if p == "/api/job":                           # 진행 상태 (GUI 가 0.3 s 마다 물음)
            from urllib.parse import parse_qs
            jid = parse_qs(u.query).get("id", [""])[0]
            J = JOBS.get(jid)
            if not J:
                return self._send(404, {"error": "unknown job"})
            now = time.time()
            if J["stage"].startswith("대기") and FILL["active"]:
                J["detail"] = (f"템플릿 결과 DB 를 처음 만드는 중 ({FILL['i']}/{FILL['n']} {FILL['name']}) — "
                               "지금 템플릿 하나가 끝나면 이 요청을 먼저 계산합니다")
            out = dict(stage=J["stage"], detail=J["detail"], elapsed=now - J["t0"], stage_s=now - J["ts"],
                       history=J["history"], done=J["done"], error=J["error"])
            if J["done"]:
                out["result"] = J["rep"]
                JOBS.pop(jid, None)
            return self._send(200, out)
        if p == "/api/templates":
            from formproof_input.products.tv_stand import TEMPLATES as TV
            return self._send(200, [dict(id=t["id"], name=t["name"], desc=t["desc"],
                                         thumb=f"/examples/templates/{t['id']}.png") for t in TEMPLATES + TV])
        if p == "/api/p01_shape":                     # 발표 10쪽 비교 형상 하나 (표면 + 분포)
            from urllib.parse import parse_qs
            from formproof_input import integral
            sid = parse_qs(urlparse(self.path).query).get("id", ["base"])[0]
            if sid not in [s[0] for s in integral.SHAPES]:
                return self._send(404, {"error": "unknown shape"})
            return self._send(200, integral.shape_view(sid))
        if p == "/api/examples":
            hand = sorted(f for f in os.listdir(os.path.join(EXAMPLES, "hand"))      # T templates + reviewed looks G01-G16
                          if f.endswith(".png") and f[5] in "TG")
            return self._send(200, ["/examples/presentation/input_sketch.png"] + [f"/examples/hand/{f}" for f in hand])
        if p == "/api/photos":                        # AI 글래스 예시 사진 (실제 제품 사진은 사용자가 넣음)
            d = os.path.join(EXAMPLES, "glasses")
            fs = sorted(f for f in os.listdir(d) if f.lower().endswith((".png", ".jpg", ".jpeg"))) if os.path.isdir(d) else []
            return self._send(200, [f"/examples/glasses/{f}" for f in fs])
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
            now = time.time()
            J = JOBS[rid] = dict(stage="대기 (앞 요청 계산 중)", detail="", t0=now, ts=now, history=[], done=False, error=None, rep=None)
            with WAIT_LOCK:
                WAITING[0] += 1

            def note(name, detail=""):
                t = time.time()
                if J["stage"] and not J["stage"].startswith("대기"):
                    J["history"].append(dict(name=J["stage"], s=round(t - J["ts"], 2)))
                J.update(stage=name, detail=detail, ts=t)

            def work():
                try:
                    with LOCK:
                        with WAIT_LOCK:
                            WAITING[0] -= 1
                        progress.set_listener(note)
                        note("입력 읽기 · 제품 판단")
                        try:
                            rep = pipeline.design(req.get("text", ""), sketch, image, req.get("template") or None, out, with_mesh=True,
                                                  product=req.get("product") or None)
                        finally:
                            note("결과 보내는 중")
                            progress.set_listener(None)
                    rep["run_id"] = rid
                    rep["timings"] = J["history"][:]
                    rep["files"] = {name: f"/runs/{rid}/{name}" for name in sorted(os.listdir(out))}
                    J.update(rep=json.loads(json.dumps(rep, ensure_ascii=False)), done=True)
                except Exception as e:                                   # show the reason in the page
                    traceback.print_exc()
                    msg = str(e)
                    if "no strokes" in msg:
                        msg = "스케치나 이미지에서 선을 찾지 못했습니다. 조금 더 진하게 그려 주세요."
                    J.update(error=msg, done=True)

            if urlparse(self.path).query == "wait=1":                    # 명령줄 · 시험용: 끝날 때까지 기다려 결과 바로
                work()
                if J["error"]:
                    return self._send(400, {"error": J["error"]})
                JOBS.pop(rid, None)
                return self._send(200, J["rep"])
            threading.Thread(target=work, daemon=True).start()
            return self._send(200, {"job": rid})
        except Exception as e:                                          # show the reason in the page
            traceback.print_exc()
            msg = str(e)
            if "no strokes" in msg:
                msg = "스케치나 이미지에서 선을 찾지 못했습니다. 조금 더 진하게 그려 주세요."
            return self._send(400, {"error": msg})


class Server(ThreadingHTTPServer):
    """윈도우에서 SO_REUSEADDR 는 같은 포트에 서버 두 개가 동시에 붙게 해, 요청이 예전 서버와 새 서버로 나뉘어 간다
    (예: 진행 상태 조회가 다른 프로세스로 가서 'Cannot read properties of undefined'). 포트를 혼자 쓰게 막는다."""
    allow_reuse_address = sys.platform != "win32"

    def server_bind(self):
        import socket
        if sys.platform == "win32" and hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


def fill_template_db():
    """템플릿 결과 DB 의 빈 항목을 뒤에서 채움 (한 항목씩 LOCK — 사용자가 누른 요청이 먼저 끼어들 수 있게).
    이미 있는 항목은 0.3 s 안에 넘어감. setup.bat 이 미리 채워 두면 여기서는 할 일이 없다."""
    import tempfile
    from formproof_input import memo
    done_mark = memo.marker()
    if os.path.exists(done_mark):                                    # 이미 다 채움 -> 요청을 기다리게 하지 않음
        return
    t, n = time.time(), 0
    jobs = memo.jobs()
    FILL.update(active=True, n=len(jobs))
    for i, (name, fn) in enumerate(jobs, 1):
        FILL.update(i=i, name=name)
        while WAITING[0] > 0:                                       # 사용자 요청이 기다리면 양보
            time.sleep(0.1)
        try:
            with LOCK:
                t1 = time.time()
                with tempfile.TemporaryDirectory() as d:
                    fn(d)
                if time.time() - t1 > 1.0:
                    n += 1
        except Exception as e:                                      # 한 항목이 실패해도 서버는 계속
            sys.stderr.write(f"[템플릿 DB] {name}: {e}\n")
    FILL.update(active=False)
    try:
        open(done_mark, "w").close()
    except OSError:
        pass
    if n:
        print(f"[템플릿 DB] 새로 계산한 템플릿 {n}개 ({time.time() - t:.0f}s) — 이제 모두 4 s 안에 나옵니다", flush=True)


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
    try:
        srv = Server((a.host, a.port), Handler)
    except OSError:
        print(f"\n포트 {a.port} 를 이미 다른 서버가 쓰고 있습니다. 예전 서버 창(검은 창)을 닫고 다시 실행하세요."
              f"\n(다른 포트: start.bat --port 8766)\n", flush=True)
        sys.exit(1)
    threading.Thread(target=fill_template_db, daemon=True).start()
    if not a.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(f"http://localhost:{a.port}")).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
