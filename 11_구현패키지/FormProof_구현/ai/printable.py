"""3D 프린터(FDM) 출력 규칙의 미분 가능한 벌점 — 잠재 공간 역설계(latent_search)용 (11-18 추가)

규칙은 engine/printability.py · engine/opt_int.py 출력 필터와 같음:
  받침판 윗면(z' = 30)이 베드, -z' 방향으로 쌓음. 한 칸은 바로 아래층의 [같은 자리 + 앞뒤좌우] 중 하나에 재료가 있어야 함 (45°).
  고정 부품(클램프 링 · 집게 하우징 · 레일 · 걸이)은 출력된 것으로 봄 (opt_int 와 같은 가정).
벌점 = Σ relu(칸 점유 - 아래층이 받쳐 주는 정도) = '아래가 빈 칸' 수 (부드러운 점유면 그만큼 비례).
학습 데이터(gen_frame PRINTABLE=1)가 출력 가능 형상이면 형상 AI 의 잠재 공간도 대부분 출력 가능하지만,
최적화가 데이터 바깥으로 나갈 수 있어 벌점으로 붙잡고, 마지막에 engine/printability.make_self_supporting 으로 확정 보정.
"""
import numpy as np, torch
import torch.nn.functional as F

ZB, H = 24.0, 2.0


class PrintPenalty:
    def __init__(self, grid, meta_path):
        m = np.load(meta_path)
        z0 = float(m['zc'].min()) - H / 2
        self.kt = int((ZB + 6 - z0) / H) - 1
        self.grid = grid
        fixed = (m['solid'] & ~m['void']).astype(np.float32).reshape(grid.nz, grid.ny, grid.nx)
        self.free = torch.as_tensor(1.0 - fixed[:self.kt + 1][::-1].copy())          # (층, y, x) 1 = 검사 대상

    def _layers(self, occ_d):
        full = self.grid.to_grid(occ_d)[:, 0]                                      # (B, nz, ny, nx)
        return full[:, :self.kt + 1].flip(1)                                       # 층 0 = 베드

    def support(self, L):
        """L: (B, n, ny, nx) -> 각 칸 아래층이 받쳐 주는 정도 (같은 자리 + 4 이웃의 최댓값, y=0 거울)"""
        P = F.pad(L, (1, 1, 1, 1))
        P = torch.cat([P[:, :, 1:2], P[:, :, 1:]], 2)                               # y=-1 칸 = y=0 칸 (거울)
        c = P[:, :, 1:-1, 1:-1]
        return torch.stack([c, P[:, :, :-2, 1:-1], P[:, :, 2:, 1:-1], P[:, :, 1:-1, :-2], P[:, :, 1:-1, 2:]], 0).max(0).values

    def __call__(self, occ_d):
        """(B, nd) 설계 영역 점유(0–1) -> (B,) 아래가 빈 칸 수 (미분 가능)"""
        L = self._layers(occ_d)
        S = self.support(L[:, :-1])
        over = torch.relu(L[:, 1:] - S) * self.free[1:].to(L.device)
        return over.sum((1, 2, 3))
