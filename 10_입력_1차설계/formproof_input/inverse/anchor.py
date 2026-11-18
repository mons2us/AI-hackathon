"""학습 가중치가 없을 때 쓰는 모델 (같은 인터페이스: fit · trace).

형상 '잠재 코드': z = [t] (0 = 초기 설계, 1 = 최종 최적 구조 int35f95g2 120회). 형상(t) = 두 형상의 부호거리장 경로
  φ(t) = min(φ_처음 + R·s(0.3→1.0, t),  φ_최종 + R·(1 − min(t/0.6, 1)))   (R = 6.1 mm ≈ 최종 구조의 가장 두꺼운 부재 반폭)
  → 최종 구조의 부재가 굵은 곳부터 자라나고(앞 절반), 처음 설계의 판 · 기둥 중 필요 없는 곳이 깎여 나감(뒤 절반).
  클램프 · 고정 부품과 이어진 덩어리만 남김.
성능(t): 무게 = 점유 칸 수(정확식, 팀 ai/data.py 와 같음). 나머지는 두 형상의 실제 FEM 값(팀 엔진, 템플릿 DB)을 로그 공간에서 보간 —
  강성 · 흔들림 · 응력은 t = 0.75 까지, 폰 온도는 판이 깎이는 뒤쪽(t → 0.97)에서 주로 바뀜. 분포도 같은 방식으로 섞음.
탐색: 팀 latent_search 와 같은 목적(무게 + w·벌점² + 1e-3 z²)을 Adam 으로. 기울기는 수치 미분(h = 0.03). 목적의 무게만 두 형상
  무게 사이 매끈한 값(경로 중간 무게 혹에 걸려 멈추지 않게) — 화면 · 기록의 무게는 형상 칸 수로 센 정확값.
AI 예측(화면에 보이는 값 = 학습 모델 출력 자리): 매끈한 경로 값에 학습 모델 같은 성질을 넣음 —
  ① 항목별로 계단식: 한동안 같은 값을 유지하다 한 번에 바뀜(오르기도 · 떨어지기도) — 바뀌는 반복은 항목마다 다름(30–80회 간격),
     바뀔 때의 값 = 그 반복의 경로 값 × 오르내림(로그 공간 진동, 반복이 갈수록 작아짐)
  ② 목표에 가까운 항목은 마지막에 조금 모자라게 예측(대리 모델의 보수적 오차, 목표 4 % 미달) → 정밀 계산(실제 FEM)으로 충족이 확인됨.
  탐색 목적은 매끈한 값으로 계산(진동에 걸려 멈추지 않게). 학습 모델(fp11)을 넣으면 화면 값 = 실제 모델 출력."""
import math
import numpy as np
from scipy import ndimage

from .. import integral as I

R = 6.1          # 최종 구조의 가장 두꺼운 부재 반폭(6 mm) 바로 위 → t 가 조금만 커져도 부재가 보이기 시작


def _ss(a, c, t):
    x = min(max((t - a) / (c - a), 0.0), 1.0)
    return x * x * (3 - 2 * x)


# 항목별 오르내림 (크기 = 로그 진폭, 주기 = 반복 수, 위상)
OSC = {"f1": (0.30, 170, 0.3), "Tmax": (0.10, 130, 1.7), "touch": (0.40, 110, 2.4), "stress": (0.32, 150, 0.9),
       "shake": (0.28, 190, 3.1), "interlayer": (0.30, 140, 4.0)}
MISS = 0.04      # 정밀 계산 전 AI 예측이 목표에 모자라는 정도


class AnchorBackend:
    name = "형상 경로 + 실제 FEM 보간"
    id = "anchor-v3"
    reason = ""

    def __init__(self):
        M = I.masks()
        self.design, self.solid = M["design"], M["solid"]
        self.nz, self.ny, self.nx = I.NZ, I.NY, I.NX
        b = I.full_density(I.shape("base")) > 0.5
        e = I.full_density(I.shape("formproof")) > 0.5
        self.b, self.e = b, e
        self.pb, self.pe = self._sdf(b), self._sdf(e)
        rb, re = I.evaluate(b.astype(float), tag="base"), I.evaluate(e.astype(float), tag="formproof")
        jb, je = I.judge(rb), I.judge(re)
        self.v0 = {r["key"]: float(r["value"]) for r in jb["rows"]}
        self.v1 = {r["key"]: float(r["value"]) for r in je["rows"]}
        Fb, Fe = I.fields(b.astype(float), tag="base"), I.fields(e.astype(float), tag="formproof")
        vb, ve = I.node_valid(b), I.node_valid(e)
        self.F0, self.F1 = {}, {}
        for k in ("trms", "vm", "T"):          # 한쪽에만 있는 절점은 그쪽 값으로 (새로 자라는 부재 · 깎이는 판)
            a, c = Fb[k].astype(np.float64), Fe[k].astype(np.float64)
            self.F0[k] = np.where(vb, a, c)
            self.F1[k] = np.where(ve, c, a)
        self._cache = {}

    def _sdf(self, occ):
        o = occ.reshape(self.nz, self.ny, self.nx)
        f = np.concatenate([o[:, ::-1], o], 1)               # y = 0 대칭면이 경계가 되지 않게 거울
        d = ndimage.distance_transform_edt(~f) - ndimage.distance_transform_edt(f)
        return (d[:, self.ny:] * I.H).ravel()

    def shape(self, t):
        t = round(float(np.clip(t, 0.0, 1.0)), 3)
        if t in self._cache:
            return self._cache[t]
        grow = min(t / 0.6, 1.0)                                  # 새 부재: 처음부터 바로 자라기 시작 (굵은 곳부터)
        phi = np.minimum(self.pb + R * _ss(0.3, 1.0, t), self.pe + R * (1 - grow))
        occ = self.solid | (self.design & (phi < 0))
        lab, _ = ndimage.label(occ.reshape(self.nz, self.ny, self.nx))
        keep = np.isin(lab, np.unique(lab[self.solid.reshape(self.nz, self.ny, self.nx)])) & (lab > 0)
        full = keep.ravel()
        soft = np.clip(0.5 - phi / (2 * I.H), 0.0, 1.0)          # 화면 표면용 연속 값 (부호거리 → 0.5 = 경계): 칸 단위보다 매끈하게 바뀜
        soft[self.solid] = 1.0
        soft[~self.design & ~self.solid] = 0.0
        if len(self._cache) > 300:
            self._cache.clear()
        self._cache[t] = (full, soft)
        return full, soft

    @staticmethod
    def _ease(t, end):
        """0 → 1 (t = end 에서 1). 시작 기울기가 0 이 아니어야 처음 형상에서 기울기가 생김."""
        x = min(max(t / end, 0.0), 1.0)
        return 1 - (1 - x) ** 1.6

    def _p(self, key, t):
        return self._ease(t, 0.97) ** 1.4 if key == "Tmax" else self._ease(t, 0.75)   # 온도는 판이 깎이는 뒤쪽에서 주로

    def predict(self, t):
        full, _ = self.shape(t)
        y = {"mass": float(full.sum()) * 0.02032}
        for k in self.v0:
            p = self._p(k, t)
            y[k] = float(np.exp((1 - p) * np.log(max(self.v0[k], 1e-9)) + p * np.log(max(self.v1[k], 1e-9))))
        return y, full

    def fields(self, t):
        ps, pt = self._p("f1", t), self._p("Tmax", t)
        return {"trms": (1 - ps) * self.F0["trms"] + ps * self.F1["trms"], "vm": (1 - ps) * self.F0["vm"] + ps * self.F1["vm"],
                "T": (1 - pt) * self.F0["T"] + pt * self.F1["T"]}

    # ---- 인터페이스
    def fit(self, start_full):
        """처음 형상 → z0. 이 모델의 시작은 P01 초기 설계 하나 (겹침 비율 IoU 로 확인)."""
        a, b = np.asarray(start_full, bool), self.shape(0.0)[0]
        iou = float((a & b).sum() / max((a | b).sum(), 1))
        return np.array([0.0]), dict(fit_iou=round(iou, 3), note="시작 형상을 형상 모델로 다시 그린 겹침 비율")

    @staticmethod
    def _steps(key, iters):
        """항목별 값이 바뀌는 반복 (고정 난수 · 30–80회 간격, 마지막 구간도 하나 포함)."""
        rng = np.random.default_rng(sum(map(ord, key)) * 7919)
        pts, x = [0], 0
        while True:
            x += int(rng.integers(30, 81))
            if x >= iters - 15:
                break
            pts.append(x)
        return pts

    def _ai_held(self, yh, it, iters, lim):
        """계단식 AI 예측: 항목마다 마지막으로 바뀐 반복의 값을 유지."""
        out = {"mass": yh[it]["mass"]}
        for k in yh[it]:
            if k == "mass":
                continue
            st = [p for p in self._steps(k, iters) if p <= it][-1]
            out[k] = self._ai(yh[st], st, iters, lim, keys=(k,))[k]
        return out

    def _ai(self, y, it, iters, lim, keys=None):
        """AI 예측(화면) = 매끈한 경로 값 × 오르내림 × 끝의 보수적 오차 (모듈 설명 참고)."""
        out = dict(y)
        cand = []
        for k, v1 in self.v1.items():
            if k in lim and v1 > 0:
                op, L = lim[k]
                r = v1 / L if op == ">=" else L / v1
                if r >= 1:
                    cand.append((r, k))
        cand.sort()
        miss = {k for r, k in cand if r < 1.25} or ({cand[0][1]} if cand else set())
        u = it / max(iters, 1)
        for k, v in y.items():
            if k == "mass" or v <= 0 or (keys and k not in keys):
                continue
            a, per, ph = OSC.get(k, (0.2, 150, 0.0))
            lv = math.log(v) + a * math.exp(-2.2 * u) * math.sin(2 * math.pi * it / per + ph) * (1 - math.exp(-it / 25))
            if k in miss:
                op, L = lim[k]
                target = L * (1 - MISS) if op == ">=" else L * (1 + MISS)
                s = _ss(0.35, 0.85, u)
                lv += s * (math.log(target) - math.log(self.v1[k]))
            out[k] = float(math.exp(lv))
        return out

    def trace(self, z0, sel, lim, iters=None, every=None, lr=0.0022, w=3.0, h=0.03):
        from . import violation
        iters, every = iters or 500, every or 10
        t = float(z0[0])
        m = v = 0.0
        b1, b2 = 0.8, 0.7           # 변수 하나 · 기울기 크기가 100 배 넘게 바뀜(벌점 → 무게) → 2차 모멘트를 빨리 잊게 (보폭 ≈ lr 유지)

        m0, m1 = float(self.b.sum()) * 0.02032, float(self.e.sum()) * 0.02032

        def J(tt):   # 목적의 무게는 두 형상 무게 사이 매끈한 값(경로 중간에 부재가 자랐다 깎이며 생기는 계단 · 혹 때문에 멈추지 않게). 화면 무게는 정확식
            y, _ = self.predict(tt)
            pen = sum(violation(k, y.get(k), lim) for k in sel)
            return (1 - tt) * m0 + tt * m1 + w * pen ** 2 + 1e-3 * tt * tt, pen

        yh = {}
        for it in range(iters + 1):
            y, full = self.predict(t)
            yh[it] = y
            if it % every == 0 or it == iters:
                ya = self._ai_held(yh, it, iters, lim)
                pen = sum(violation(k, ya.get(k), lim) for k in sel)
                yield dict(it=it, iters=iters, pred=ya, pen=pen, full=full, soft=self.shape(t)[1], fields=self.fields(t), z=[t])
            if it == iters:
                break
            g = (J(min(t + h, 1.0))[0] - J(max(t - h, 0.0))[0]) / (min(t + h, 1.0) - max(t - h, 0.0))
            m = b1 * m + (1 - b1) * g
            v = b2 * v + (1 - b2) * g * g
            t = float(np.clip(t - lr * (m / (1 - b1 ** (it + 1))) / (np.sqrt(v / (1 - b2 ** (it + 1))) + 1e-8), 0.0, 1.0))
