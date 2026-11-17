"""학습된 형상 AI · 물리 AI (results_fp11.zip) 로 도는 역설계 — sosopapa ai/latent_search.trace_run 과 같은 계산.

  fit  : 1차 설계에 z 를 맞춤 (디코더 고정, 무작위 16,384 점 BCE, Adam 5e-3, FP11_FIT_STEPS 회 = 기본 1500).
         한 번 맞춘 z0 는 models/fp11/z0_<형상 해시>.npy 에 저장 (CPU 에서 오래 걸림)
  trace: 목적 = 무게(정확식) + w·(Σ 고른 기준 정규화 위반 × 10)² + 1e-3‖z‖², Adam lr 0.02, FP11_ITERS 회(기본 500),
         FP11_EVERY 회(기본 10)마다 형상(디코더 sharp 2, 0.5 기준) · 예측값 · 분포를 프레임으로.
물리 AI 출력: 스칼라 7개 [무게, f1, f2, 폰 온도, 터치 위, 터치 아래, 충격 응력(위아래)] (+ --ext 로 학습했으면 11개:
  f3, f4, 노면 대역 흔들림 위아래/앞뒤, 80 Hz 까지 최대 흔들림 위아래/앞뒤, RMS 위아래/앞뒤, 충격 응력 앞뒤, 층간 위아래/앞뒤).
  화면 키: f1, Tmax, touch = max(터치 위 · 아래), stress = max(충격 위아래 · 앞뒤), interlayer · shake(80 Hz 까지 최대) 는 ext 가 있을 때만.
  분포: FNO 2채널 [온도 상승 / ts, log1p(충격 응력) / vs] → 절점 값(이웃 재료 요소 평균). 흔들림 분포는 물리 AI 출력에 없음."""
import hashlib
import os

import numpy as np

from .. import integral as I


def _sha_file(p, n=1 << 20):
    h = hashlib.sha1(str(os.path.getsize(p)).encode())
    with open(p, "rb") as f:
        h.update(f.read(n))
    return h.hexdigest()[:10]


class TorchBackend:
    name = "학습 모델 (results_fp11: DeepSDF 형상 AI × FNO 물리 AI)"
    reason = ""

    def __init__(self, sdf_path, phys_path, meta_path):
        import torch                                             # 없으면 ImportError → 상위에서 대체 모델
        from .fp11.data import Grid
        from .fp11.deepsdf import ShapeAI
        from .fp11.surrogate import Surrogate
        self.torch = torch
        self.grid = Grid(meta_path)
        M = I.masks()                                            # 우리 P01 격자와 같은지 (다르면 형상 · 분포가 어긋남)
        if self.grid.ne != len(M["design"]) or not np.array_equal(self.grid.design, M["design"]) or not np.array_equal(self.grid.solid, M["solid"]):
            raise ValueError("grid_meta.npz 의 격자(설계 영역 · 고정 부품)가 P01 격자와 다릅니다")
        self.S = ShapeAI(sdf_path, self.grid)
        self.M = Surrogate(phys_path, self.grid, self.S.dev)
        st = torch.load(phys_path, map_location="cpu", weights_only=False)
        self.field_scale = st.get("field_scale")
        self.n_out = int(st["cfg"].get("n_out", 7))
        self.trace_keys = ("f1", "Tmax", "touch", "stress") + (("interlayer", "shake") if self.n_out >= 18 else ())   # 탐색 벌점에 쓰는 기준
        self.id = f"fp11-{_sha_file(sdf_path)}-{_sha_file(phys_path)}"
        self.dir = os.path.dirname(os.path.dirname(sdf_path))

    # ---- 예측값 → 화면 키
    def _keys(self, y):
        y = [float(v) for v in y]
        out = dict(mass=y[0], f1=y[1], Tmax=y[3], touch=max(y[4], y[5]), stress=y[6], interlayer=None, shake=None)
        if self.n_out >= 18:
            out.update(stress=max(y[6], y[15]), interlayer=max(y[16], y[17]), shake=max(y[11], y[12]))
        return out

    def _fields(self, fld, occ_full):
        if fld is None or not self.field_scale:
            return None
        ts, vs = self.field_scale
        f = fld[0].detach().cpu().numpy().astype(np.float64)                     # (2, nz, ny, nx)
        T, vm = f[0] * ts, np.expm1(np.clip(f[1] * vs, 0, 20))
        occ = occ_full.reshape(I.NZ, I.NY, I.NX).astype(np.float64)
        th = self.grid.thermal_region.reshape(I.NZ, I.NY, I.NX).astype(np.float64)

        def nodes(v, w):                                                          # 요소 → 절점 (이웃 요소 가중 평균)
            s = np.zeros((I.NZ + 1, I.NY + 1, I.NX + 1))
            c = np.zeros_like(s)
            for dk in (0, 1):
                for dj in (0, 1):
                    for di in (0, 1):
                        s[dk:dk + I.NZ, dj:dj + I.NY, di:di + I.NX] += v * w
                        c[dk:dk + I.NZ, dj:dj + I.NY, di:di + I.NX] += w
            return (s / np.maximum(c, 1e-9)).ravel()
        return {"T": nodes(T, th), "vm": nodes(vm, occ)}

    # ---- 인터페이스
    def fit(self, start_full, steps=None):
        torch = self.torch
        import torch.nn.functional as F
        from .fp11.deepsdf import iou
        steps = int(steps or os.environ.get("FP11_FIT_STEPS", 1500))
        r0 = np.asarray(start_full, float).ravel()
        h = hashlib.sha1(np.packbits(r0 > 0.5).tobytes()).hexdigest()[:12]
        cache = os.path.join(self.dir, f"z0_{h}_{steps}.npy")
        tgt = torch.as_tensor((r0[self.grid.didx] > 0.5).astype(np.float32), device=self.S.dev)
        if os.path.exists(cache):
            z = torch.as_tensor(np.load(cache), device=self.S.dev)
        else:
            z = self.S.Z.mean(0, keepdim=True).clone().to(self.S.dev).requires_grad_(True)
            opt = torch.optim.Adam([z], lr=5e-3)
            for _ in range(steps):
                idx = torch.randint(0, self.grid.nd, (16384,), device=self.S.dev)
                lg = self.S.dec(z, self.S.P[idx])[0]
                loss = F.binary_cross_entropy_with_logits(lg, tgt[idx]) + 1e-4 * (z ** 2).mean()
                opt.zero_grad()
                loss.backward()
                opt.step()
            z = z.detach()
            np.save(cache, z.cpu().numpy())
        with torch.no_grad():
            fit_iou = iou(self.S.decode(z)[0].cpu().numpy(), tgt.cpu().numpy())
        return z.cpu().numpy(), dict(fit_iou=round(float(fit_iou), 3), note="시작 형상을 형상 AI 로 다시 그린 겹침 비율")

    def trace(self, z0, sel, lim, iters=None, every=None, lr=0.02, w=3.0):
        torch = self.torch
        from . import violation
        iters = int(iters or os.environ.get("FP11_ITERS", 500))
        every = int(every or os.environ.get("FP11_EVERY", 10))
        z = torch.as_tensor(np.asarray(z0, np.float32), device=self.S.dev).reshape(1, -1).clone().requires_grad_(True)
        opt = torch.optim.Adam([z], lr=lr)
        relu = torch.relu

        def pen_t(y):
            """미분 가능한 벌점 (팀 latent_search 와 같은 꼴). 키 → 예측 텐서."""
            keys = {"f1": y[1], "Tmax": y[3], "touch": torch.maximum(y[4], y[5]), "stress": y[6]}
            if self.n_out >= 18:
                keys.update(stress=torch.maximum(y[6], y[15]), interlayer=torch.maximum(y[16], y[17]), shake=torch.maximum(y[11], y[12]))
            p = torch.zeros((), device=y.device)
            for k in sel:
                if k not in keys:
                    continue
                op, L = lim[k]
                p = p + (relu(L - keys[k]) if op == ">=" else relu(keys[k] - L)) / L * 10
            return p

        for it in range(iters + 1):
            o = self.S.decode(z, sharp=2.0)
            out = self.M.predict(o)
            y = out["scalars"][0]
            pen = pen_t(y)
            if it % every == 0 or it == iters:
                with torch.no_grad():
                    prob = o[0].cpu().numpy().astype(np.float64)
                full = self.grid.solid.copy()
                full[self.grid.didx] = prob > 0.5
                soft = self.grid.solid.astype(np.float64)                 # 화면 표면: 형상 AI 점유 확률 그대로 (0.5 = 경계)
                soft[self.grid.didx] = prob
                pred = self._keys(y.detach().cpu().numpy())
                pred["mass"] = float(full.sum()) * 0.02032          # 화면 무게 = 0/1 형상 칸 수 (출력할 형상 기준)
                yield dict(it=it, iters=iters, pred=pred, pen=float(sum(violation(k, pred.get(k), lim) for k in sel)), full=full, soft=soft,
                           fields=self._fields(out["fields"], full), z=z.detach().cpu().numpy()[0].tolist())
            if it == iters:
                break
            loss = y[0] + w * pen ** 2 + 1e-3 * (z ** 2).sum()
            opt.zero_grad()
            loss.backward()
            opt.step()
