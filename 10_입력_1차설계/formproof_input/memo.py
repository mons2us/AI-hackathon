"""템플릿 결과 DB — 1차 설계는 템플릿(+ 이산 파라미터)이라 같은 템플릿이면 CAD · 도면 · 성능 계산 결과가 같다.
처음 한 번 계산해 templates/db/precomputed/<키>/ 에 저장하고, 이후에는 파일 복사 + JSON 읽기만 한다 (< 0.5 s).
미리 채우기: python -m formproof_input.memo  (setup.bat 이 실행, 서버도 시작할 때 빈 항목을 뒤에서 채움)."""
import hashlib
import json
import os
import shutil
import uuid

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "templates", "db", "precomputed")
VERSION = "v9"            # 설계 · 해석 코드가 바뀌면 올림 (예전 결과를 쓰지 않게)


def _np(o):
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def key(*parts):
    s = json.dumps([VERSION, *parts], ensure_ascii=False, sort_keys=True, default=_np)
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:20]


def get(k, out):
    """Hit -> copy the stored files into `out` and return the stored data; miss -> None."""
    d = os.path.join(DB, k)
    p = os.path.join(d, "_data.json")
    if not os.path.exists(p):
        return None
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(d):
        if f != "_data.json":
            shutil.copy2(os.path.join(d, f), os.path.join(out, f))
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def put(k, out, files, data):
    os.makedirs(DB, exist_ok=True)
    tmp = os.path.join(DB, f".{k}.{uuid.uuid4().hex[:6]}")
    os.makedirs(tmp)
    for f in files:
        src = os.path.join(out, f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(tmp, f))
    with open(os.path.join(tmp, "_data.json"), "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, default=_np)
    dst = os.path.join(DB, k)
    if os.path.exists(dst):
        shutil.rmtree(tmp, ignore_errors=True)
    else:
        os.replace(tmp, dst)
    return json.loads(json.dumps(data, ensure_ascii=False, default=_np))


def new_files(out, before):
    return sorted(set(os.listdir(out)) - set(before))


# ------------------------------------------------------------------ 미리 채우기
def jobs():
    """데모에서 쓰는 템플릿 조합: P01, TV 스탠드 (가로/세로 × 높이 3), AI 글래스 (형상 2 × 렌즈 폭 3), 폰 거치대 T 템플릿 기본값."""
    from .products import glasses as G
    from .products import tv_stand as TV
    from .templates.library import TEMPLATES
    out = [("P01", lambda d: __import__("formproof_input.integral", fromlist=["design"]).design("", out=d, with_mesh=True))]
    for t in TV.TEMPLATES:
        for lv in TV.LEVELS:
            out.append((f"{t['id']}-{lv}", lambda d, t=t, lv=lv: TV.design(TV.LEVEL_WORD[lv], template=t["id"], out=d, with_mesh=True)))
    for st in G.STYLES:
        for lw in G.LENS_WIDTHS:
            out.append((f"AG-{st}-{lw}", lambda d, st=st, lw=lw: G.design(f"렌즈 {lw:g}", out=d, with_mesh=True, style=st)))
    from . import pipeline
    for t in TEMPLATES:
        out.append((t["id"], lambda d, t=t: pipeline.design("", template=t["id"], out=d, with_mesh=True, product="bike")))
    # P01 물리 기반 최적화: 기본 선택(1차 설계 미충족 5개 · 전부)의 역설계 경로 + FEM 검증 → 누르면 바로 재생
    out.append(("P01-opt", lambda d: __import__("formproof_input.inverse", fromlist=["precompute"]).precompute(log=lambda *a: None)))
    return out


def marker():
    """'전부 채움' 표시 파일 — 공통 VERSION + 제품별 버전(바뀐 제품만 다시 계산되고, 서버 · setup 이 다시 채우게)."""
    from .products.glasses import GM_VERSION
    from .inverse import models_stamp
    return os.path.join(DB, f"_complete_{VERSION}_g{GM_VERSION}_o{models_stamp()}")   # 학습 모델을 넣거나 바꾸면 다시 채움


def fill(names=None, log=print):
    import tempfile
    import time
    for name, fn in jobs():
        if names and name not in names:
            continue
        t = time.time()
        with tempfile.TemporaryDirectory() as d:
            fn(d)
        log(f"{name}: {time.time() - t:.1f} s")
    if not names:                                       # 전부 채움 표시 -> 서버가 시작할 때 다시 돌지 않음
        open(marker(), "w").close()


if __name__ == "__main__":
    import sys
    fill(sys.argv[1:] or None)
