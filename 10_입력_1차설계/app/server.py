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
import numpy as np
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
APP_VERSION = "2026-11-16f"                                 # index.html 의 APP_V 와 같아야 함 (화면 · 서버 버전 확인)
JOBS = {}
OPT_JOBS = {}                                              # 간이 물리 최적화 job id -> 진행 (반복 · 기록 · 최신 표면)
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
        gz = len(body) > 65536 and ctype.startswith("application/json") and "gzip" in (self.headers.get("Accept-Encoding") or "")
        if gz:                                                  # 큰 JSON(최적화 프레임 · 분포)은 gzip — 브라우저가 알아서 풂
            import gzip
            body = gzip.compress(body, 5)
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        if gz:
            self.send_header("Content-Encoding", "gzip")
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
        if p in ("/optimize", "/optimize.html"):         # 간이 물리 최적화 화면 (메인 화면과 따로)
            return self._file(os.path.join(STATIC, "optimize.html"))
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
            if "frames" in J:                                   # 최적화: 아직 안 보낸 프레임만 (since = 받은 개수)
                since = int(parse_qs(u.query).get("since", ["0"])[0] or 0)
                out["frames"] = J["frames"][since:]
                out["nframes"] = len(J["frames"])
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
        if p == "/api/opt_state":                     # 간이 물리 최적화 진행 (optimize.html 이 0.5 s 마다 물음)
            from urllib.parse import parse_qs
            q = parse_qs(u.query)
            J = OPT_JOBS.get(q.get("id", [""])[0])
            if not J:
                return self._send(404, {"error": "unknown job"})
            since = int(q.get("since", ["-1"])[0])
            out = {k: J[k] for k in ("run_id", "stage", "iter", "iters", "done", "error", "first", "target")}
            out["history"] = J["history"][since + 1:]
            if J["mesh"] is not None and J["mesh"]["iter"] > since:
                out["mesh"] = J["mesh"]
            out["elapsed"] = time.time() - J["t0"]
            return self._send(200, out)
        if p == "/api/opt_frame":                     # 끝난 최적화의 반복 k 형상 (다시 보기)
            from urllib.parse import parse_qs
            q = parse_qs(u.query)
            rid, k = q.get("run", [""])[0], int(q.get("k", ["-1"])[0])
            d = os.path.realpath(os.path.join(RUNS, rid))
            if not d.startswith(os.path.realpath(RUNS) + os.sep) or not os.path.isfile(os.path.join(d, "opt", "history.npz")):
                return self._send(404, {"error": "no optimisation history"})
            return self._send(200, _opt_frame(d, k))
        if p == "/api/photos":                        # AI 글래스 예시 사진 (실제 제품 사진은 사용자가 넣음)
            d = os.path.join(EXAMPLES, "glasses")
            fs = sorted(f for f in os.listdir(d) if f.lower().endswith((".png", ".jpg", ".jpeg"))) if os.path.isdir(d) else []
            return self._send(200, [f"/examples/glasses/{f}" for f in fs])
        return self._send(404, {"error": "not found"})

    def _optimize(self):
        """물리 기반 최적화 (P01): GUI 에서 고른 성능 항목을 기준으로 역설계(형상 AI × 물리 AI) — 작업(job)으로 돌리고
        프레임(형상 · 예측값 · 분포)을 진행 조회 때 조금씩 보냄. 끝나면 FEM 검증 관문 + 결과 파일(최적 형상 STL · 최적화 기록 ·
        최적화 입력 묶음 optimize_input.zip)."""
        import re
        import zipfile
        from formproof_input import inverse as OPT
        n = int(self.headers.get("Content-Length", 0))
        try:
            req = json.loads(self.rfile.read(n).decode("utf-8"))
            rid = str(req["run"])
            sel = [str(k) for k in req["targets"]]
        except Exception as e:                                  # noqa: BLE001
            return self._send(400, {"error": f"잘못된 요청: {e}"})
        sel = [k for k in sel if k in OPT.KEYS]
        if not sel:
            return self._send(400, {"error": "최적화할 항목을 하나 이상 고르세요"})
        out = os.path.join(RUNS, rid)
        if not re.fullmatch(r"[\w.-]+", rid) or rid.startswith(".") or not os.path.isfile(os.path.join(out, "handoff.zip")):
            return self._send(404, {"error": "이 1차 설계의 결과 폴더가 없습니다. 1차 설계를 다시 만들어 주세요."})
        jid = "opt-" + uuid.uuid4().hex[:8]
        now = time.time()
        J = JOBS[jid] = dict(stage="대기 (앞 요청 계산 중)", detail="", t0=now, ts=now, history=[], done=False, error=None, rep=None, frames=[])
        with WAIT_LOCK:
            WAITING[0] += 1

        def work():
            try:
                with LOCK:
                    with WAIT_LOCK:
                        WAITING[0] -= 1
                    J.update(stage="역설계 준비 (형상 AI · 물리 AI)", ts=time.time())

                    def on_frame(fr):
                        J["frames"].append(fr)
                        J.update(stage=f"역설계 반복 {fr['it']} / {fr['iters']}", detail=f"무게 {fr['mass_g']:.1f} g · 기준 벌점 {fr['pen']:.2f}")
                    res = OPT.run(sel, on_frame)
                    J.update(stage="FEM 검증 관문 (팀 엔진으로 마지막 형상 다시 계산)", detail="", ts=time.time())
                    g = OPT.gate(res, out=out)
                    with open(os.path.join(out, "optimize_targets.json"), "w", encoding="utf-8") as f:
                        json.dump(dict(run=rid, targets=sel, limits=res["limits"], created=time.strftime("%Y-%m-%d %H:%M:%S")), f, ensure_ascii=False, indent=2)
                    with zipfile.ZipFile(os.path.join(out, "handoff.zip")) as zi, \
                            zipfile.ZipFile(os.path.join(out, "optimize_input.zip"), "w", zipfile.ZIP_DEFLATED) as zo:
                        for it in zi.infolist():
                            zo.writestr(it, zi.read(it.filename))
                        for f in ("optimize_targets.json", "optimize_result.json", "opt_final.stl", "opt_final_rho.npy"):
                            if os.path.exists(os.path.join(out, f)):
                                zo.write(os.path.join(out, f), f)
                files = {f: f"/runs/{rid}/{f}" for f in ("opt_final.stl", "optimize_result.json", "optimize_input.zip")}
                J.update(rep=json.loads(json.dumps(dict(gate=g, files=files, fit=res["fit"], seconds=res["seconds"], cached=res["cached"],
                                                        selection=sel), ensure_ascii=False, default=float)), done=True)
            except Exception as e:                                      # noqa: BLE001
                traceback.print_exc()
                J.update(error=f"최적화 실패: {e}", done=True)

        threading.Thread(target=work, daemon=True).start()
        return self._send(200, {"job": jid})

    def do_POST(self):
        if urlparse(self.path).path == "/api/optimize":
            return self._optimize()
        if urlparse(self.path).path == "/api/opt_run":                 # 간이 물리 최적화 실행 (optimize.html)
            return self._opt_run()
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


    def _opt_run(self):
        """간이 물리 최적화 시작: {run_id} (이미 만든 1차 설계) 또는 {template} (먼저 1차 설계), iters, vol_frac."""
        try:
            n = int(self.headers.get("Content-Length", 0))
            req = json.loads(self.rfile.read(n).decode("utf-8") or "{}")
            rid = req.get("run_id") or ""
            if rid:
                d = os.path.realpath(os.path.join(RUNS, rid))
                if not d.startswith(os.path.realpath(RUNS) + os.sep) or not os.path.isfile(os.path.join(d, "spec.json")):
                    return self._send(400, {"error": "run_id 의 1차 설계가 없습니다"})
            elif not req.get("template"):
                return self._send(400, {"error": "run_id 또는 template 이 필요합니다"})
            iters = max(1, min(int(req.get("iters", 40)), 120))
            vf = float(req.get("vol_frac", 0.15))
            jid = "opt-" + uuid.uuid4().hex[:8]
            J = OPT_JOBS[jid] = dict(run_id=rid, stage="대기 (앞 요청 계산 중)", iter=0, iters=iters, done=False, error=None,
                                     history=[], mesh=None, first=None, target=vf, t0=time.time())

            def work():
                from formproof_input import optimize
                try:
                    with LOCK:
                        r = rid
                        if not r:
                            J["stage"] = "1차 설계 만드는 중"
                            r = time.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
                            pipeline.design("", None, None, req["template"], os.path.join(RUNS, r))
                            J["run_id"] = r
                        d = os.path.join(RUNS, r)

                        def on_iter(rec, opt):
                            if rec["iter"] == 0:
                                J["first"] = rec.get("eval")
                            J["history"].append(rec)
                            J.update(iter=rec["iter"], stage=f"최적화 {rec['iter']}/{iters}")
                            from formproof_input import fem
                            dens = opt.full_density()
                            if not fem.connected(opt.P, fem.on_mask(opt.P, dens))[0]:
                                return                                   # 끊긴 중간 형상은 보내지 않음
                            v, f = optimize.surface(opt.P, dens)
                            J["mesh"] = dict(iter=rec["iter"], v=np.round(v, 2).ravel().tolist(), f=f.ravel().tolist())

                        J["stage"] = "최적화 준비"
                        optimize.run(d, iters=iters, vol_frac=vf, on_iter=on_iter, render=False)
                    J.update(stage="끝", done=True)
                except Exception as e:
                    traceback.print_exc()
                    J.update(error=str(e) or type(e).__name__, done=True)

            threading.Thread(target=work, daemon=True).start()
            return self._send(200, {"job": jid})
        except Exception as e:
            traceback.print_exc()
            return self._send(400, {"error": str(e)})


def _opt_frame(d, k):
    from formproof_input import optimize
    from formproof_input.compile import Problem
    H = np.load(os.path.join(d, "opt", "history.npz"))
    x = H["x"]
    k = len(x) - 1 if k < 0 or k >= len(x) else k
    P = Problem(json.load(open(os.path.join(d, "spec.json"), encoding="utf-8")))
    dens = np.zeros(len(P.label))
    dens[P.solid | P.rigid] = 1.0
    dens[H["var"]] = x[k] / 255.0
    from formproof_input import fem
    if not fem.connected(P, fem.on_mask(P, dens))[0]:
        return dict(iter=int(k), n=int(len(x)), broken=True)          # 끊긴 중간 형상은 보여 주지 않음
    v, f = optimize.surface(P, dens)
    return dict(iter=int(k), n=int(len(x)), v=np.round(v, 2).ravel().tolist(), f=f.ravel().tolist())


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
