"""간이 물리 최적화 (CPU) — 1차 설계에서 시작해 형상이 바뀌어 가는 과정을 보여 주는 단계.

입력 단계 출력(spec.json + initial_design.npy)을 그대로 받아, 같은 격자 · 같은 하중(폰 강체 충격 위아래 · 앞뒤) ·
같은 경계(핸들 고정 · 대칭면)로 3D SIMP 강성 최적화를 돌린다.

  물리 모델 : hex8 선형 정적 FEM (팀 fem3d.hex8_KB, formproof_input.fem 과 같은 요소), 절반 모델 S/A 경우
  목적      : 충격 하중 경우들의 컴플라이언스 합 최소 (같은 무게에서 가장 단단한 형상)
  제약      : 설계 영역 부피 = 목표 (기본 0.15, 또는 1차 설계 무게의 vol_ratio 배)
  갱신      : 밀도 필터(반경 rmin) + OC(최적성 조건) — 팀 엔진(SIMP + MMA, 진동수 · 흔들림 제약)의 간이판
  판정      : eval_every 반복마다 0/1 형상으로 formproof_input.fem.evaluate (진동수 · 흔들림 · 응력 · 층간 · 연결)

  python -m formproof_input.optimize out/ --iters 40           # out/ = run.py 출력 폴더
  -> out/opt/ : history.npz (반복별 밀도) · metrics.json · final_density.npy · final_design.npy
                · frames/iter_XXX.png · evolution.gif · evolution_strip.png

이 단계는 시연용 간이판이다. 발표 수치(진동수 · 흔들림 제약을 직접 거는 최적화)는 팀 엔진
11_구현패키지/FormProof_구현/engine/opt_int.py 로 낸다. final_design.npy 는 initial_design.npy 와 같은 형식이라
그 엔진의 START_RHO 로 바로 넘길 수 있다."""
import argparse
import json
import os
import time

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla

from . import fem, progress
from .compile import Problem

EMIN = 1e-6


def _filter_matrix(P, var, rmin):
    """밀도 필터 H (설계 변수끼리, 거리 rmin 요소 안, 선형 가중)."""
    ijk = P.ijk[var].astype(float)
    nx, ny, nz = P.shape
    pos = -np.ones(len(P.label), int)
    pos[np.where(var)[0]] = np.arange(var.sum())
    R = int(np.ceil(rmin)) - 1 if rmin > 1 else 0
    rows, cols, vals = [], [], []
    base = np.where(var)[0]
    I, J, K = P.ijk[base].T
    for di in range(-R - 1, R + 2):
        for dj in range(-R - 1, R + 2):
            for dk in range(-R - 1, R + 2):
                w = rmin - np.sqrt(di * di + dj * dj + dk * dk)
                if w <= 0:
                    continue
                i2, j2, k2 = I + di, J + dj, K + dk
                ok = (i2 >= 0) & (i2 < nx) & (j2 >= 0) & (j2 < ny) & (k2 >= 0) & (k2 < nz)
                e2 = (k2 * ny + j2) * nx + i2
                e2 = np.where(ok, e2, 0)
                q = pos[e2]
                ok &= q >= 0
                rows.append(np.arange(len(base))[ok])
                cols.append(q[ok])
                vals.append(np.full(ok.sum(), w))
    H = sp.coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
                      shape=(len(base), len(base))).tocsr()
    return H, np.asarray(H.sum(1)).ravel()


class SimpleOptimizer:
    def __init__(self, spec, x_init=None, vol_ratio=1.0, vol_frac=None, p=3.0, rmin=1.5, move=0.15,
                 drop=1e-3):
        self.P = P = Problem(spec) if isinstance(spec, dict) else spec
        self.spec = P.spec
        mat = self.spec["material"]
        self.KE, _, _, _ = fem.hex8_KB(mat["E"], mat["nu"], P.h)
        ne = len(P.label)
        self.edof = np.stack([3 * P.enodes, 3 * P.enodes + 1, 3 * P.enodes + 2], 2).reshape(ne, 24)
        ko = P.keepout if P.keepout is not None else np.zeros(ne, bool)
        self.var = P.design & ~ko
        self.fixed_on = P.solid | P.rigid
        x0 = (np.asarray(x_init, float) if x_init is not None else P.initial_density())[self.var]
        self.x_first = x0.copy()
        nvar = int(self.var.sum())
        if vol_frac is not None:
            self.V = float(vol_frac) * nvar
        else:
            self.V = max(float(vol_ratio) * x0.sum(), 0.02 * nvar)
        # 시작 = 1차 설계(1) + 나머지 설계 영역에 남은 부피를 고르게 (1차 설계가 보이는 상태에서 출발)
        rest = max(self.V - x0.sum(), 0.0)
        bg = min(rest / max((x0 < 0.5).sum(), 1), 0.9)
        self.x = np.where(x0 > 0.5, 1.0, max(bg, 1e-3))
        if self.x.sum() > self.V:                                   # 목표가 1차 설계보다 가벼우면 비율로 줄여 시작
            self.x *= self.V / self.x.sum()
        self.p, self.move, self.drop = p, move, drop
        self.H, self.Hs = _filter_matrix(P, self.var, rmin)
        self.cases = [c for c in self.spec["load_cases"] if c["type"] == "inertial"]
        if not self.cases:
            raise ValueError("spec 에 inertial 하중 경우가 없습니다")
        self.loads = {c["name"]: P.load_vector(c) for c in self.cases}
        self.it = 0
        self._warm = {}
        self.beta, self.beta_every, self.beta_max = 1.0, 8, 16.0
        self.direct_max = 8000                               # 이보다 크면 다중격자 CG (splu 는 메모리가 큼)

    # ------------------------------------------------------------ physics
    def _proj(self, xt):
        b, e = self.beta, 0.5
        return (np.tanh(b * e) + np.tanh(b * (xt - e))) / (np.tanh(b * e) + np.tanh(b * (1 - e)))

    def phys(self, x=None):
        """밀도 필터 → Heaviside 투영(beta 를 반복마다 키워 0/1 로 모음, 회색 줄이기)."""
        return self._proj(self.H @ (self.x if x is None else x) / self.Hs)

    def full_density(self, xp=None):
        P = self.P
        d = np.zeros(len(P.label))
        d[self.fixed_on] = 1.0
        d[self.var] = self.phys() if xp is None else xp
        return d

    def _solver(self, A, fr):
        """작은 문제 = 직접법(splu), 큰 문제 = pyamg 다중격자 전처리 CG (메모리 < 1 GB, 이전 해로 웜 스타트).
        설계 영역 전체가 회색인 초반에는 자유도가 7만 개를 넘어 splu 가 수 GB 를 쓴다."""
        if A.shape[0] <= self.direct_max:
            lu = sla.splu(A.tocsc(), permc_spec="MMD_AT_PLUS_A", options=dict(SymmetricMode=True))
            return lambda b, key: lu.solve(b)
        try:
            import pyamg
        except ImportError:
            pyamg = None
        M = None
        if pyamg is not None:
            xyz = self.P.nodes[fr // 3]
            d = fr % 3
            B = np.zeros((len(fr), 6))                               # 강체 모드 (탄성 다중격자 근영공간)
            B[np.arange(len(fr)), d] = 1.0
            x, y, z = xyz.T
            B[:, 3] = np.where(d == 0, -y, np.where(d == 1, x, 0))
            B[:, 4] = np.where(d == 1, -z, np.where(d == 2, y, 0))
            B[:, 5] = np.where(d == 2, -x, np.where(d == 0, z, 0))
            M = pyamg.smoothed_aggregation_solver(A, B=B, max_coarse=300).aspreconditioner(cycle="V")
        else:
            M = sp.diags(1.0 / A.diagonal())
        warm = self._warm

        def solve(b, key):
            x0 = warm.get(key)
            x0 = x0 if x0 is not None and len(x0) == len(b) else None
            x, info = sla.cg(A, b, x0=x0, rtol=1e-6, maxiter=3000, M=M)
            warm[key] = x
            return x
        return solve

    def solve(self, xp):
        """컴플라이언스 합과 설계 변수 민감도."""
        P = self.P
        d = self.full_density(xp)
        on = self.fixed_on | (self.var & (d > self.drop))
        idx = np.where(on)[0]
        Ee = np.where(self.var[idx], EMIN + d[idx] ** self.p * (1 - EMIN), 1.0) * P.k_scale[idx]
        ed = self.edof[idx]
        K = sp.coo_matrix(((self.KE.ravel()[None, :] * Ee[:, None]).ravel(),
                           (np.repeat(ed, 24, 1).ravel(), np.tile(ed, (1, 24)).ravel())),
                          shape=(3 * P.nn, 3 * P.nn)).tocsc()
        c_tot, dc_full = 0.0, np.zeros(len(P.label))
        per = {}
        lus = {}
        for c in self.cases:
            case = P.sym_case(c["dir"])
            if case not in lus:
                fr = fem._free(P, on, case)
                lus[case] = (fr, self._solver(K[fr][:, fr].tocsr(), fr))
            fr, solve = lus[case]
            u = np.zeros(3 * P.nn)
            F = self.loads[c["name"]]
            u[fr] = solve(F[fr], c["name"])
            ue = u[ed]
            ce = np.einsum("ij,jk,ik->i", ue, self.KE, ue)
            cc = float((Ee * ce).sum())
            w = c.get("opt_weight", 1.0) / len(self.cases) / max(getattr(self, "_c0", {}).get(c["name"], cc), 1e-30)
            per[c["name"]] = cc
            c_tot += w * cc
            dc = np.zeros(len(P.label))
            dc[idx] = -w * self.p * np.where(self.var[idx], d[idx] ** (self.p - 1) * (1 - EMIN), 0.0) \
                * P.k_scale[idx] * ce
            dc_full += dc
        if not hasattr(self, "_c0"):                         # 경우별 정규화 기준 = 시작 형상
            self._c0 = per
            return self.solve(xp)
        return c_tot, dc_full[self.var], per

    def step(self):
        xp = self.phys()
        c, dc, per = self.solve(xp)
        xt = self.H @ self.x / self.Hs
        b = self.beta
        dp = b * (1 - np.tanh(b * (xt - 0.5)) ** 2) / (np.tanh(b * 0.5) + np.tanh(b * 0.5))
        dc = self.H.T @ (dc * dp / self.Hs)                 # 투영 · 필터 체인 룰
        dv = self.H.T @ (dp / self.Hs)
        x = self.x
        l1, l2 = 1e-12, 1e12
        dcn = np.maximum(-dc, 1e-30)
        while (l2 - l1) / (l1 + l2) > 1e-4:                  # OC 이분법 (부피 = 목표)
            lm = 0.5 * (l1 + l2)
            xn = np.clip(x * np.sqrt(dcn / (lm * dv)), np.maximum(0.0, x - self.move), np.minimum(1.0, x + self.move))
            if self.phys(xn).sum() > self.V:
                l1 = lm
            else:
                l2 = lm
        change = float(np.abs(xn - x).max())
        self.x = xn
        self.it += 1
        if self.it % self.beta_every == 0 and self.beta < self.beta_max:   # 투영 점점 날카롭게
            self.beta *= 2
        xp = self.phys()
        gray = float(((xp > 0.1) & (xp < 0.9)).sum() / max((xp > 0.1).sum(), 1))
        return dict(iter=self.it, objective=round(c, 6), compliance={k: float(v) for k, v in per.items()},
                    volume_frac=round(float(xp.sum() / len(xp)), 4), change=round(change, 4), gray=round(gray, 3))

    def evaluate(self):
        """0/1 형상(밀도 > 0.5)으로 입력 단계와 같은 판정."""
        d = self.full_density()
        r = fem.evaluate(self.P, d)
        return dict(mass_g=r["mass_g"], f1_hz=r["f1_hz"], connected=r["connected"], parts=r["parts"],
                    shaking=r.get("transmissibility_band_max"),
                    checks={k: dict(value=v["value"], limit=v["limit"], ok=v["pass"], reference=bool(v.get("reference"))) for k, v in r["checks"].items()},
                    passed=bool(r["pass"]))


# ---------------------------------------------------------------- 그림
def surface(P, dens, iso=0.5, mirror=True, smooth=0.6):
    """밀도장 → 표면 메쉬 (marching cubes, mm). 대칭면 기준 반대쪽도 붙여 전체 모델로."""
    from skimage import measure
    nx, ny, nz = P.shape
    g = np.zeros((nx + 2, ny + 2, nz + 2))
    g[1:-1, 1:-1, 1:-1] = dens.reshape(nz, ny, nx).transpose(2, 1, 0)
    if smooth:                                            # 보기용 표면만 살짝 매끈하게 (계단 줄이기, 판정은 0/1 격자 그대로)
        from scipy.ndimage import gaussian_filter
        g = gaussian_filter(g, smooth)
    ax = P.sym_axis
    if g.max() < iso:
        return np.zeros((0, 3)), np.zeros((0, 3), int)
    v, f, _, _ = measure.marching_cubes(g, iso, spacing=(P.h,) * 3)
    v = v - P.h + P.origin + P.h / 2
    if mirror and ax is not None:
        o = P.origin[ax]                                   # 대칭면 = 격자 원점 면 -> 거울로 붙여 전체 모델
        v2 = v.copy()
        v2[:, ax] = 2 * o - v[:, ax]
        f2 = f[:, ::-1] + len(v)
        v, f = np.vstack([v, v2]), np.vstack([f, f2])
    return v.astype(np.float32), f.astype(np.int32)


def render_frame(P, dens, path, title="", lim=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    v, f = surface(P, dens)
    fig = plt.figure(figsize=(5.2, 4.2), dpi=110)
    a = fig.add_subplot(111, projection="3d")
    if len(f):
        tri = v[f]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        shade = 0.25 + 0.75 * np.abs(n @ (np.array([0.35, -0.55, 0.75]) / np.linalg.norm([0.35, -0.55, 0.75])))
        col = np.c_[0.08 + 0.10 * shade, 0.25 + 0.30 * shade, 0.55 + 0.40 * shade, np.ones_like(shade)]
        a.add_collection3d(Poly3DCollection(tri, facecolors=col, edgecolors="none"))
    if lim is None:
        lim = (P.nodes.min(0), P.nodes.max(0))
    lo, hi = lim
    if P.sym_axis is not None:
        lo = lo.copy()
        lo[P.sym_axis] = 2 * P.origin[P.sym_axis] - hi[P.sym_axis]
    a.set_xlim(lo[0], hi[0]); a.set_ylim(lo[1], hi[1]); a.set_zlim(lo[2], hi[2])
    a.set_box_aspect(hi - lo)
    a.view_init(elev=18, azim=-62)
    a.set_axis_off()
    a.set_title(title, fontsize=10)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def _font():
    import matplotlib
    from matplotlib import font_manager
    for name in ("Malgun Gothic", "NanumGothic", "Noto Sans CJK KR", "Noto Sans KR"):
        if any(name == f.name for f in font_manager.fontManager.ttflist):
            matplotlib.rcParams["font.family"] = name
            return
    matplotlib.rcParams["font.family"] = "DejaVu Sans"


# ---------------------------------------------------------------- 실행
def run(src, out=None, iters=40, vol_ratio=1.0, vol_frac=0.15, eval_every=10, frame_every=5, rmin=1.5,
        on_iter=None, render=True):
    """src = run.py 출력 폴더(spec.json · initial_design.npy) 또는 spec.json 경로.
    on_iter(rec, opt) 는 반복마다 불림 (GUI 실시간 표시용)."""
    d = src if os.path.isdir(src) else os.path.dirname(src)
    spec = json.load(open(os.path.join(d, "spec.json") if os.path.isdir(src) else src, encoding="utf-8"))
    init_p = os.path.join(d, "initial_design.npy")
    x_init = np.load(init_p) if os.path.exists(init_p) else None
    if "load_cases" not in spec:
        raise ValueError("이 1차 설계(P01 발표 사례 형식)는 팀 엔진 opt_int.py 로 최적화합니다 (engine_env.json · initial_design.npy). "
                         "간이 최적화는 T 템플릿 · 외형 템플릿(G · L) 형식만 받습니다")
    out = out or os.path.join(d, "opt")
    os.makedirs(os.path.join(out, "frames"), exist_ok=True)
    for f in os.listdir(os.path.join(out, "frames")):              # 이전 실행의 그림 지우기
        os.remove(os.path.join(out, "frames", f))
    shots = {k for k in (1, 2, 3, 4, 6, 8) if k <= iters} | set(range(frame_every, iters + 1, frame_every)) | {iters}
    t0 = time.time()
    progress.step("간이 최적화 준비", "필터 · 하중")
    opt = SimpleOptimizer(spec, x_init, vol_ratio=vol_ratio, vol_frac=vol_frac, rmin=rmin)
    P = opt.P
    hist = [np.round(opt.phys() * 255).astype(np.uint8)]
    recs = [dict(iter=0, volume_frac=round(float(opt.phys().mean()), 4), eval=opt.evaluate(), start=True)]
    first = dict(iter=0, eval=fem_first(P, x_init, opt))
    if on_iter:
        on_iter(recs[0], opt)
    frames = []
    _font()
    if render:
        fp = os.path.join(out, "frames", "iter_000.png")
        render_frame(P, opt.full_density(), fp, "반복 0 (1차 설계에서 시작)")
        frames.append(fp)
    for k in range(1, iters + 1):
        progress.step(f"간이 최적화 {k}/{iters}", "")
        rec = opt.step()
        rec["seconds"] = round(time.time() - t0, 1)
        if k % eval_every == 0 or k == iters or (render and k in shots):
            rec["eval"] = opt.evaluate()
        hist.append(np.round(opt.phys() * 255).astype(np.uint8))
        recs.append(rec)
        if on_iter:
            on_iter(rec, opt)
        if render and k in shots and rec.get("eval", {}).get("connected", True):   # 끊긴 중간 형상은 그림에서 뺌
            fp = os.path.join(out, "frames", f"iter_{k:03d}.png")
            ev = rec.get("eval")
            sub = f" · {ev['mass_g']:.0f} g · {ev['f1_hz']:.0f} Hz" if ev else ""
            render_frame(P, opt.full_density(), fp, f"반복 {k}{sub}")
            frames.append(fp)
    final = opt.full_density()
    np.save(os.path.join(out, "final_density.npy"), final.astype(np.float32))
    np.save(os.path.join(out, "final_design.npy"), (opt.var & (final > 0.5)).astype(np.float64))   # initial_design.npy 형식
    np.savez_compressed(os.path.join(out, "history.npz"), x=np.stack(hist), var=np.where(opt.var)[0],
                        shape=np.array(P.shape), h=P.h, origin=P.origin, sym_axis=-1 if P.sym_axis is None else P.sym_axis)
    meta = dict(template=spec.get("template", {}).get("id") if isinstance(spec.get("template"), dict) else None,
                model="3D SIMP 강성 최적화 (hex8 FEM, 충격 하중 컴플라이언스 합 최소, 부피 제약, 밀도 필터 + OC)",
                grid=list(P.shape), h_mm=P.h, n_design=int(opt.var.sum()), target_volume_frac=round(opt.V / opt.var.sum(), 4),
                load_cases=[c["name"] for c in opt.cases], iters=iters, seconds=round(time.time() - t0, 1),
                first_design=first["eval"], history=recs,
                note="시연용 간이 최적화. 진동수 · 흔들림 제약을 직접 거는 최적화는 팀 엔진(opt_int.py)에서.")
    json.dump(meta, open(os.path.join(out, "metrics.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if render and frames:
        _animate(frames, out, recs)
    return meta


def fem_first(P, x_init, opt):
    if x_init is None:
        return None
    d = np.zeros(len(P.label))
    d[opt.fixed_on] = 1
    d[P.design] = np.asarray(x_init)[P.design]
    r = fem.evaluate(P, d)
    return dict(mass_g=r["mass_g"], f1_hz=r["f1_hz"], shaking=r.get("transmissibility_band_max"),
                checks={k: dict(value=v["value"], limit=v["limit"], ok=v["pass"], reference=bool(v.get("reference"))) for k, v in r["checks"].items()},
                passed=bool(r["pass"]))


def _animate(frames, out, recs):
    from PIL import Image
    ims = [Image.open(f).convert("RGB") for f in frames]
    ims[0].save(os.path.join(out, "evolution.gif"), save_all=True, append_images=ims[1:] + [ims[-1]] * 3,
                duration=450, loop=0)
    its = [int(os.path.basename(f)[5:8]) for f in frames]
    want = [0, 2, 4, 8, its[-1]]
    pick = [ims[min(range(len(its)), key=lambda i: abs(its[i] - w))] for w in want]
    pick = [p for i, p in enumerate(pick) if p not in pick[:i]]
    w, h = pick[0].size
    strip = Image.new("RGB", (w * len(pick), h), "white")
    for i, im in enumerate(pick):
        strip.paste(im, (i * w, 0))
    strip.save(os.path.join(out, "evolution_strip.png"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("src", help="run.py 출력 폴더 (spec.json · initial_design.npy)")
    ap.add_argument("--out")
    ap.add_argument("--iters", type=int, default=40)
    ap.add_argument("--vol-frac", type=float, default=0.15, help="목표 부피 비율 (설계 영역 대비, 기본 0.15)")
    ap.add_argument("--vol-ratio", type=float, help="대신 목표 무게 = 1차 설계 × 이 값 (주면 --vol-frac 무시)")
    ap.add_argument("--eval-every", type=int, default=10)
    ap.add_argument("--frame-every", type=int, default=5)
    ap.add_argument("--rmin", type=float, default=1.5)
    ap.add_argument("--no-render", action="store_true")
    a = ap.parse_args()
    m = run(a.src, a.out, a.iters, a.vol_ratio or 1.0, None if a.vol_ratio else a.vol_frac, a.eval_every, a.frame_every, a.rmin, render=not a.no_render)
    last = [r for r in m["history"] if "eval" in r][-1]["eval"]
    print(json.dumps(dict(first=m["first_design"], final=last, seconds=m["seconds"],
                          target_volume_frac=m["target_volume_frac"]), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
