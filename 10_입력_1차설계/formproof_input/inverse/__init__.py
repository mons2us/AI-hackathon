"""물리 기반 최적화 (P01 일체형 거치대) — 역설계: 형상 AI(잠재 코드 z → 형상) × 물리 AI(형상 → 성능).

sosopapa 11_구현패키지 ai/latent_search.trace_run 과 같은 방식:
  1) 1차 설계(처음 설계)에 z 를 맞춘다 (형상 AI fit)
  2) 목적 = 무게 + w · (Σ 고른 기준의 정규화 위반 × 10)² + 1e-3 ‖z‖², Adam 으로 z 를 고침
  3) every 회마다 형상 · 예측값 · 벌점을 프레임으로 기록 → GUI 가 형상이 바뀌는 것을 재생
  4) 마지막 형상을 FEM(팀 엔진)으로 다시 계산 (검증 관문)

모델 두 가지 (같은 인터페이스: fit(처음 형상) → z0, trace(z0, 기준) → 프레임들):
  - fp11  : 학습된 가중치. models/results_fp11.zip (runs/sdf.pt · runs/fno.pt) + models/grid_meta.npz 가 있고 PyTorch 가 있으면 자동 사용
  - anchor: 가중치가 없을 때. 형상 = 1차 설계 → 최종 최적 구조(위상 최적화 int35f95g2) 사이 부호거리장 경로(새 부재가 자라고
            필요 없는 판이 깎임), 성능 = 두 형상의 실제 FEM 값 사이 보간(무게는 점유 칸 수로 정확히). 같은 탐색 루프로 돈다.

명령: python -m formproof_input.inverse check      (어느 모델을 쓰는지 · 가중치 읽기 · 몇 회 시험)
      python -m formproof_input.inverse precompute (기본 선택의 최적화 경로를 미리 계산 → 누르면 바로 재생)"""
import base64
import gzip
import hashlib
import json
import math
import os
import time

import numpy as np

from .. import integral as I
from .. import memo

HERE = os.path.dirname(os.path.abspath(__file__))
INPUT_ROOT = os.path.dirname(os.path.dirname(HERE))
MODELS = os.path.join(INPUT_ROOT, "models")            # results_fp11.zip · grid_meta.npz 를 여기에 그대로 넣음
G_PER_CELL = 1.27e-9 * 8 * 1e6 * 2                      # 요소 하나(2 mm 정육면체, PETG) × 양쪽 = 0.02032 g (팀 ai/data.py 와 같음)

# GUI 성능 블록 키 (integral.judge 행 key) → 기준
KEYS = ("f1", "Tmax", "touch", "stress", "interlayer", "shake")


def limits():
    tg = I.targets()
    return dict(f1=(">=", tg["f1_min_hz"]), Tmax=("<=", tg["phone_Tmax_rise_max_c"]), touch=("<=", tg["touch_max_mm"]),
                stress=("<=", tg["shock_vm_max_mpa"]), interlayer=("<=", tg["shock_interlayer_max_mpa"]), shake=("<=", I.SHAKE_LIMIT))


def violation(key, value, lim):
    """정규화 위반 × 10 (팀 latent_search 와 같은 꼴: relu(FT − f1)/FT·10 …). 예측이 없으면 0."""
    if value is None:
        return 0.0
    op, L = lim[key]
    v = (L - value) / L if op == ">=" else (value - L) / L
    return max(v, 0.0) * 10.0


# ------------------------------------------------------------------ 격자 · 형상
def _masks():
    M = I.masks()
    return M["design"], M["solid"]


def full_from_design(occ_d, design_idx, solid):
    full = solid.copy()
    full[design_idx] = occ_d
    return full


def attached(full):
    """클램프 · 고정 부품과 이어진 덩어리만 (떠 있는 조각은 출력 · 계산에서 뺌 — 팀 엔진 clean 과 같은 뜻)."""
    from scipy import ndimage
    _, solid = _masks()
    f = np.asarray(full, bool).reshape(I.NZ, I.NY, I.NX)
    lab, _ = ndimage.label(f)
    keep = np.isin(lab, np.unique(lab[solid.reshape(I.NZ, I.NY, I.NX)])) & (lab > 0)
    return keep.ravel()


def _sha(a):
    return hashlib.sha1(np.packbits(np.asarray(a, bool)).tobytes()).hexdigest()[:16]


# ------------------------------------------------------------------ 모델 고르기
_BACKEND = {}


def model_files():
    """(sdf, phys, meta) 경로 또는 None. results_fp11.zip 은 처음 한 번 models/fp11/ 에 풀어 둔다."""
    z = os.path.join(MODELS, "results_fp11.zip")
    meta = os.path.join(MODELS, "grid_meta.npz")
    out = os.path.join(MODELS, "fp11")
    if not (os.path.exists(z) and os.path.exists(meta)):
        return None
    sdf, phys = os.path.join(out, "runs", "sdf.pt"), os.path.join(out, "runs", "fno.pt")
    if not (os.path.exists(sdf) and os.path.exists(phys)) or os.path.getmtime(sdf) < os.path.getmtime(z):
        import zipfile
        with zipfile.ZipFile(z) as f:
            names = f.namelist()
            want = [n for n in names if n.endswith(("runs/sdf.pt", "runs/fno.pt", "runs/pino.pt", "runs/cnn.pt"))]
            for n in want:
                dst = os.path.join(out, "runs", os.path.basename(n))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                with f.open(n) as src, open(dst, "wb") as fh:
                    fh.write(src.read())
    if not os.path.exists(phys) and os.path.exists(os.path.join(out, "runs", "pino.pt")):
        phys = os.path.join(out, "runs", "pino.pt")
    if not (os.path.exists(sdf) and os.path.exists(phys)):
        return None
    return sdf, phys, meta


def models_stamp():
    """학습 모델 파일 표시 (없으면 'none') — 템플릿 DB '전부 채움' 표시에 넣어, 모델을 넣거나 바꾸면 다시 채우게."""
    z, m = os.path.join(MODELS, "results_fp11.zip"), os.path.join(MODELS, "grid_meta.npz")
    if not (os.path.exists(z) and os.path.exists(m)):
        return "none"
    return hashlib.sha1(f"{os.path.getsize(z)}-{os.path.getmtime(z):.0f}-{os.path.getsize(m)}".encode()).hexdigest()[:8]


def backend(force=None):
    """학습된 모델(fp11)이 있으면 그것, 없으면 anchor. force='anchor' | 'fp11'."""
    kind = force or os.environ.get("FP_OPT_BACKEND")
    if kind in _BACKEND:
        return _BACKEND[kind]
    reason = ""
    if kind in (None, "fp11"):
        files = model_files()
        if files:
            try:
                from .real import TorchBackend
                _BACKEND["fp11"] = b = TorchBackend(*files)
                _BACKEND.setdefault(None, b)
                return b
            except ImportError as e:
                reason = f"PyTorch 없음 ({e})"
            except Exception as e:                                # noqa: BLE001 — 가중치 · 격자가 안 맞으면 이유를 남기고 anchor
                reason = f"학습 모델을 못 읽음: {e}"
            if kind == "fp11":
                raise RuntimeError(reason)
        else:
            reason = "models/results_fp11.zip · models/grid_meta.npz 없음"
    from .anchor import AnchorBackend
    b = AnchorBackend()
    b.reason = reason
    _BACKEND["anchor"] = b
    _BACKEND.setdefault(None, b)
    return b


# ------------------------------------------------------------------ 프레임 (화면용)
_MESH = {}


def mesh_payload(full, soft=None):
    """형상 → 표면(팀 mkint 와 같은 방법: 평활 + 등치면) → 간소화 → 좌표 int16 양자화 (프레임 크기 ↓).
    soft: 연속 값(형상 AI 점유 확률 · 부호거리)이 있으면 그것으로 — 2 mm 칸 단위보다 매끈하게 바뀜. 떠 있는 조각은 뺌."""
    from scipy import ndimage
    from ..templates.bike_mount import Y_SYM
    if soft is not None:
        near = ndimage.binary_dilation(np.asarray(full, bool).reshape(I.NZ, I.NY, I.NX), iterations=1).ravel()
        dens = np.where(near, np.asarray(soft, float), 0.0)
        k = hashlib.sha1(np.round(dens * 64).astype(np.uint8).tobytes()).hexdigest()[:16]
    else:
        dens = np.asarray(full, float)
        k = _sha(full)
    if k in _MESH:
        return _MESH[k]
    m = I.grid_mesh(dens)
    V, F = I.view_mesh(np.asarray(m.vertices), np.asarray(m.faces), tol=0.3)
    pos = V[F].reshape(-1, 3).astype(np.float64)
    pos[:, 1] += Y_SYM
    lo, hi = pos.min(0), pos.max(0)
    sc = np.maximum(hi - lo, 1e-6) / 65535.0
    q = np.round((pos - lo) / sc - 32768).astype(np.int16)
    out = dict(q16=base64.b64encode(q.tobytes()).decode(), lo=lo.round(4).tolist(), sc=sc.tolist(), triangles=int(len(F)))
    if len(_MESH) > 400:
        _MESH.clear()
    _MESH[k] = out
    return out


def heat_payload(full, F):
    """분포 3개(흔들림 · 충격 응력 · 온도) — 1차 설계 화면과 같은 색 척도 · 같은 격자 정보. 값이 없는 분포는 뺌."""
    from ..heat import grid_info, pack_nodes
    from ..templates.bike_mount import Y_SYM
    valid = I.node_valid(full)
    out = {}
    for k in ("stress", "shake", "temp"):
        sc = I.HEAT_SCALE[k]
        v = F.get(sc["src"]) if F else None
        if v is None:
            continue
        ok = valid & (v > 0.05) if k == "temp" else valid
        out[k] = dict(pack_nodes(np.asarray(v, np.float32), ok, sc["lo"], sc["hi"]), name=sc["name"], unit=sc["unit"])
        out[k]["max"] = round(float(np.max(np.where(ok, v, 0))), 2)
    return dict(grid=grid_info(I.ORIGIN, I.H, (I.NX, I.NY, I.NZ), I.TILT, ysym=Y_SYM, yoff=0.0), fields=out) if out else None


# ------------------------------------------------------------------ 실행
def start_shape():
    """1차 설계 (P01 처음 설계, 판 + 기둥) — 전체 격자 0/1."""
    return I.full_density(I.shape("base")) > 0.5


def run(selection, on_frame=None, use_cache=True, iters=None, every=None):
    """selection: 고른 기준 키 (KEYS 중). on_frame(frame) 을 프레임마다 부름. 반환: 결과 요약 (frames 포함)."""
    sel = sorted(k for k in selection if k in KEYS)
    if not sel:
        raise ValueError("최적화할 항목을 하나 이상 고르세요")
    B = backend()
    lim = limits()
    ck = memo.key("p01opt", B.id, sel, iters, every)
    path = os.path.join(memo.DB, ck, "opt.json.gz")
    if use_cache and os.path.exists(path):                       # 미리 계산한 경로 → 바로 재생
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            res = json.load(fh)
        for fr in res["frames"]:
            if on_frame:
                on_frame(fr)
        res["cached"] = True
        return res
    t0 = time.time()
    start = start_shape()
    z0, fit = B.fit(start)
    frames = []
    prev, n = None, 0
    for fr in B.trace(z0, sel, lim, iters=iters, every=every):
        full = attached(fr.pop("full"))
        pred = fr["pred"]
        mesh = mesh_payload(full, fr.get("soft"))
        last = fr["it"] == fr["iters"]
        frame = dict(it=fr["it"], iters=fr["iters"], mass_g=round(float(pred["mass"]), 2), pen=round(float(fr["pen"]), 4),
                     pred={k: (None if pred.get(k) is None else round(float(pred[k]), 4)) for k in KEYS},
                     mesh=mesh if mesh is not prev else None,                   # 표면이 그대로면 안 보냄 (화면은 앞 프레임 유지)
                     heat=heat_payload(full, fr.get("fields")) if (n % 4 == 0 or last) else None,   # 분포는 4 프레임마다 (크기)
                     sha=_sha(full))
        prev, n = mesh, n + 1
        frames.append(frame)
        if on_frame:
            on_frame(frame)
        last_full = full
    res = dict(backend=B.id, backend_name=B.name, selection=sel, limits={k: list(v) for k, v in lim.items()}, fit=fit,
               frames=frames, seconds=round(time.time() - t0, 1), final_sha=_sha(last_full))
    res["final_rho"] = base64.b64encode(np.packbits(last_full)).decode()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path + ".tmp", "wt", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False)
    os.replace(path + ".tmp", path)
    res["cached"] = False
    return res


def final_shape(res):
    return np.unpackbits(np.frombuffer(base64.b64decode(res["final_rho"]), np.uint8))[:I.NX * I.NY * I.NZ].astype(bool)


def gate(res, out=None, timeout=3600):
    """검증 관문: 마지막 형상을 팀 엔진 FEM 으로 다시 계산 (같은 형상은 캐시). 판정 행 + 분포 + 표면 STL."""
    full = final_shape(res).astype(float)
    r = I.evaluate(full, tag="opt", timeout=timeout)
    j = I.judge(r)
    F = I.fields(full, tag="opt", timeout=timeout)
    g = dict(rows=j["rows"], pass_=j["pass_"], mass_g=round(float(r["mass_g"]), 2), heat=heat_payload(full > 0.5, F))
    if out:
        os.makedirs(out, exist_ok=True)
        np.save(os.path.join(out, "opt_final_rho.npy"), full)
        I.grid_mesh(full).export(os.path.join(out, "opt_final.stl"))
        with open(os.path.join(out, "optimize_result.json"), "w", encoding="utf-8") as fh:
            json.dump(dict(backend=res["backend"], selection=res["selection"], limits=res["limits"], fit=res["fit"],
                           path=[dict(it=f["it"], mass_g=f["mass_g"], pen=f["pen"], pred=f["pred"]) for f in res["frames"]],
                           fem=dict(rows=j["rows"], pass_=j["pass_"], mass_g=r["mass_g"])), fh, ensure_ascii=False, indent=1, default=float)
    return g


DEFAULT_SELECTIONS = (("f1", "Tmax", "touch", "interlayer", "shake"), KEYS)   # 1차 설계에서 미충족 5개 · 전부


def precompute(log=print):
    B = backend()
    log(f"모델: {B.name} ({B.id}){' — ' + B.reason if getattr(B, 'reason', '') else ''}")
    for sel in DEFAULT_SELECTIONS:
        t = time.time()
        res = run(sel)
        g = gate(res)
        log(f"  {'·'.join(sel)}: 프레임 {len(res['frames'])}개, 무게 {res['frames'][0]['mass_g']} → {res['frames'][-1]['mass_g']} g, "
            f"FEM 판정 {'통과' if g['pass_'] else '미충족'}  ({time.time() - t:.1f} s{', 저장된 경로' if res['cached'] else ''})")
