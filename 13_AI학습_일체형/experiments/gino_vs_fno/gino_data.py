"""GINO 실험용 데이터: FNO 와 같은 389개 형상(칸 0/1) → GINO 입력.
  표면 점  : 재료 칸과 빈 칸(또는 바깥) 사이 면의 중심 + 바깥 방향 법선 (y=0 대칭면은 실제 표면이 아니라 제외)
  잠재 격자: 2×2×2 칸 묶음 중심 (44×10×19), 특징 = 묶음 안 재료 비율 (형상 AI 점유 확률로 바꿔 넣으면 미분 가능)
  출력 점  : 재료 칸 중심 (온도 · 응력 분포 정답이 있는 곳) — 성능 7개는 출력 점 특징을 모아(평균 · 최대) 예측
좌표는 등방 정규화: (mm − 중심) / 최대 반폭  → x ∈ [−1, 1], y · z 는 비율대로 더 좁음."""
import sys, numpy as np, torch
sys.path.insert(0, '/home/claude/input-spec/13_AI학습_일체형')
from ai.data import Grid, load_shards, LabelNorm, split

SH = '/tmp/claude-0/-home-claude/e964ed80-ee1b-5f91-abd3-3081682a3ad7/scratchpad/gino/sh/*.npz'

class Geo:
    def __init__(self, meta='/home/claude/input-spec/13_AI학습_일체형/data/grid_meta.npz'):
        self.g = g = Grid(meta); m = np.load(meta)
        self.h = float(m['h']); xyz = np.c_[m['xc'], m['yc'], m['zc']]
        lo = xyz.min(0) - self.h / 2; hi = xyz.max(0) + self.h / 2
        self.c0 = (lo + hi) / 2; self.s = (hi - lo).max() / 2          # 등방 정규화
        self.cell = ((xyz - self.c0) / self.s).astype(np.float32).reshape(g.nz, g.ny, g.nx, 3)
        self.hn = self.h / self.s                                       # 칸 한 변(정규화)
        self.thermal = g.thermal_region.reshape(g.nz, g.ny, g.nx)
        # 잠재 격자: 2×2×2 묶음 (z 는 37 → 38 로 한 칸 덧댐)
        self.lz, self.ly, self.lx = (g.nz + 1) // 2, g.ny // 2, g.nx // 2
        cz = lo[2] + (np.arange(self.lz) * 2 + 1) * self.h; cy = lo[1] + (np.arange(self.ly) * 2 + 1) * self.h; cx = lo[0] + (np.arange(self.lx) * 2 + 1) * self.h
        Z, Y, X = np.meshgrid(cz, cy, cx, indexing='ij')
        self.latent = ((np.stack([X, Y, Z], -1) - self.c0) / self.s).astype(np.float32)   # (lz, ly, lx, 3)

    def full(self, occ_d):
        f = self.g.solid.copy().astype(np.float32); f[self.g.didx] = occ_d; return f.reshape(self.g.nz, self.g.ny, self.g.nx)

    def surface(self, F):
        """F: (nz, ny, nx) 0/1 → 표면 점 (n, 3), 법선 (n, 3)"""
        P, Nn = [], []
        Fp = np.pad(F > 0.5, 1)
        for ax, (dz, dy, dx) in enumerate([(0, 0, 1), (0, 1, 0), (1, 0, 0)]):     # x, y, z 방향
            for sgn in (1, -1):
                nb = np.roll(Fp, -sgn, axis=2 - ax)[1:-1, 1:-1, 1:-1]
                face = Fp[1:-1, 1:-1, 1:-1] & ~nb
                if ax == 1 and sgn == -1: face[:, 0, :] = False          # y=0 대칭면 제외
                k, j, i = np.nonzero(face)
                c = self.cell[k, j, i].copy(); c[:, ax] += sgn * self.hn / 2
                n = np.zeros_like(c); n[:, ax] = sgn
                P.append(c); Nn.append(n)
        return np.concatenate(P), np.concatenate(Nn)

    def latent_occ(self, F):
        """(nz, ny, nx) → (lz, ly, lx) 묶음 안 재료 비율. torch 텐서면 미분 가능."""
        t = torch.as_tensor(F, dtype=torch.float32)[None, None]
        t = torch.nn.functional.pad(t, (0, 0, 0, 0, 0, 1))
        return torch.nn.functional.avg_pool3d(t, 2)[0, 0]

def load(pattern=SH, test_names=None):
    """test_names: 검증 형상 이름 목록(389개 분할 때 정한 58개) — 주면 그 형상만 검증, 나머지 전부 학습 (데이터 늘린 실험)"""
    geo = Geo(); D = load_shards(pattern, geo.g); N = len(D['occ'])
    if test_names is None: tr, te = split(N, seed=0)
    else:
        nm = [str(x) for x in D['names']]; te = np.array([nm.index(t) for t in test_names]); tr = np.setdiff1d(np.arange(N), te)
    norm = LabelNorm(D['lab'][tr]); Yn = norm.encode(D['lab'])
    T = D['T'].reshape(N, geo.g.nz, geo.g.ny, geo.g.nx); V = np.log1p(D['vm']).reshape(N, geo.g.nz, geo.g.ny, geo.g.nx)
    ts, vs = float(T[tr].std() + 1e-6), float(V[tr].std() + 1e-6)
    return geo, D, tr, te, norm, Yn, T, V, ts, vs
