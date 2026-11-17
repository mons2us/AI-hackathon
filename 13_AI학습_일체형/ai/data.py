"""학습 데이터 · 격자 공통 모듈 (PyTorch).

엔진(engine/opt_int.py)이 만든 파일 두 종류를 읽는다.
  grid_meta.npz : MODE=meta 출력. 격자 크기, 설계 영역 인덱스(didx), 고정 부품(solid) 등
  *.npz 샤드    : MODE=label2 출력. occ(설계 영역 점유, packbits) · lab(스칼라 7개) · T · vm(요소 분포)
격자 배열 순서는 엔진과 같다: 요소 번호 e = (k*ny + j)*nx + i  →  reshape(nz, ny, nx).
절반 모델(y ≥ 0, y=0 대칭면)이므로 y 뒤집기 증강은 쓰면 안 된다.
"""
import glob, numpy as np, torch

LAB_NAMES = ['mass_g', 'f1_hz', 'f2_hz', 'phone_Tmax_rise_c', 'touch_top_mm', 'touch_bottom_mm', 'shock_vm999_mpa']
LOG_LABS = [1, 2, 4, 5, 6]          # 로그로 학습하는 항목 (양수, 범위가 넓음)
EXT_NAMES = ['f3_hz', 'f4_hz', 'band_vert', 'band_fore', 'peak80_vert', 'peak80_fore', 'rms80_vert', 'rms80_fore',
             'shock_vm999_fore_mpa', 'interlayer999_vert_mpa', 'interlayer999_fore_mpa']   # label3 lab_ext (흔들림 · 층간 등, 11-16) — 전부 양수 → log
G_PER_CELL = 1.27e-9 * 8 * 1e6 * 2  # 요소 하나(2 mm 정육면체, PETG) × 양쪽 = 0.02032 g

class Grid:
    def __init__(self, meta_path):
        m = np.load(meta_path)
        self.nx, self.ny, self.nz = int(m['nx']), int(m['ny']), int(m['nz'])
        self.ne = self.nx * self.ny * self.nz
        self.didx = m['didx'].astype(np.int64); self.nd = len(self.didx)
        self.solid = m['solid'].astype(bool); self.design = m['design'].astype(bool)
        self.thermal_region = (m['phone'] | m['plate']).astype(bool)
        xyz = np.c_[m['xc'], m['yc'], m['zc']].astype(np.float32)
        lo, hi = xyz.min(0), xyz.max(0)
        self.xyz_norm = (2 * (xyz - lo) / (hi - lo) - 1).astype(np.float32)   # 모든 요소 중심 [-1, 1]
        self.pts = self.xyz_norm[self.didx]                                    # 설계 영역 점 (DeepSDF 질의점)
        self.n_solid = int(self.solid.sum())

    def to_grid(self, occ_d):
        """(B, nd) 설계 영역 점유 → (B, 1, nz, ny, nx) 전체 격자 (고정 부품 = 1). 미분 가능."""
        occ_d = torch.as_tensor(occ_d)
        B = occ_d.shape[0]
        full = torch.as_tensor(self.solid, dtype=occ_d.dtype, device=occ_d.device).repeat(B, 1)
        full = full.index_copy(1, torch.as_tensor(self.didx, device=occ_d.device), occ_d)
        return full.view(B, 1, self.nz, self.ny, self.nx)

    def coords(self, device):
        """(1, 3, nz, ny, nx) 정규화 좌표 채널 (FNO 입력용)."""
        c = torch.as_tensor(self.xyz_norm, device=device).T.reshape(1, 3, self.nz, self.ny, self.nx)
        return c

    def mass_g(self, occ_d):
        """설계 영역 점유(연속값 가능) → 전체 무게 g. 엔진 massg() 와 같은 정의."""
        return (occ_d.sum(-1) + self.n_solid) * G_PER_CELL

def load_shards(pattern, grid, fields=True, ext=False, disp=0):
    """ext=True: lab_ext(11개) 도 읽음(없는 샤드는 NaN). disp=N: 변위 정답(U, float16 정규화 · U_scale) 이 있는 형상을 최대 N 개까지 읽음"""
    files = sorted(glob.glob(pattern)); assert files, f'샤드 없음: {pattern}'
    O, L, T, V, N, X, UI, U, US = [], [], [], [], [], [], [], [], []; n0 = 0
    for f in files:
        d = np.load(f, allow_pickle=True)
        if len(d['occ']) == 0: continue
        O.append(np.unpackbits(d['occ'], axis=1)[:, :grid.nd].astype(np.float32)); L.append(d['lab'].astype(np.float32))
        N += list(d['names']) if 'names' in d else [f] * len(d['occ'])
        if fields: T.append(d['T'].astype(np.float32)); V.append(d['vm'].astype(np.float32))
        if ext: X.append(d['lab_ext'].astype(np.float32) if 'lab_ext' in d else np.full((len(d['occ']), len(EXT_NAMES)), np.nan, np.float32))
        if disp and 'U' in d and len(U) < disp:
            k = min(len(d['occ']), disp - sum(len(u) for u in U)); U.append(d['U'][:k]); US.append(d['U_scale'][:k]); UI.append(n0 + np.arange(k))
        n0 += len(d['occ'])
    out = dict(occ=np.concatenate(O), lab=np.concatenate(L), names=np.array(N))
    if fields: out.update(T=np.concatenate(T), vm=np.concatenate(V))
    if ext: out['ext'] = np.concatenate(X)
    if U: out.update(U_idx=np.concatenate(UI), U=np.concatenate(U), U_scale=np.concatenate(US).astype(np.float32))
    return out

class LabelNorm:
    """스칼라 정규화: LOG_LABS 는 log, 나머지는 그대로 → 평균 0 · 표준편차 1."""
    def __init__(self, lab=None, state=None, log_idx=None):
        if state is not None:
            self.mu, self.sd = np.array(state['mu']), np.array(state['sd']); self.log_idx = state.get('log_idx', LOG_LABS); return
        self.log_idx = list(LOG_LABS if log_idx is None else log_idx)
        y = self._fwd(lab); self.mu, self.sd = np.nanmean(y, 0), np.nanstd(y, 0) + 1e-6
    def _fwd(self, lab):
        y = lab.copy(); y[:, self.log_idx] = np.log(np.maximum(y[:, self.log_idx], 1e-6)); return y
    def encode(self, lab): return ((self._fwd(lab) - self.mu) / self.sd).astype(np.float32)
    def decode_t(self, yn):   # torch, 미분 가능
        mu = torch.as_tensor(self.mu, dtype=yn.dtype, device=yn.device); sd = torch.as_tensor(self.sd, dtype=yn.dtype, device=yn.device)
        y = yn * sd + mu; idx = torch.zeros(y.shape[-1], dtype=torch.bool, device=y.device); idx[self.log_idx] = True
        return torch.where(idx, torch.exp(y), y)
    def state(self): return dict(mu=self.mu.tolist(), sd=self.sd.tolist(), log_idx=list(self.log_idx))

def split(n, test_frac=0.15, seed=0):
    p = np.random.default_rng(seed).permutation(n); k = max(int(test_frac * n), 1); return p[k:], p[:k]

def device(): return torch.device('cuda' if torch.cuda.is_available() else 'cpu')
