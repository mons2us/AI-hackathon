"""GINO 물리 AI (neuraloperator 2.0.0 의 GINO 그대로) + 성능 7개 머리.
입력: 표면 점(좌표 · 법선) · 잠재 격자 재료 비율 → 출력: 재료 칸 중심마다 [온도 상승, log1p 응력] + 특징 H 개 → 평균 · 최대 → 성능 7개."""
import torch, torch.nn as nn
from neuralop.models import GINO

class GinoSur(nn.Module):
    def __init__(self, H=16, hidden=32, modes=(10, 5, 12), rin=0.06, rout=0.06):
        super().__init__()
        self.H = H
        self.gino = GINO(in_channels=3, out_channels=2 + H, latent_feature_channels=1, gno_coord_dim=3,
                         in_gno_radius=rin, out_gno_radius=rout, fno_n_modes=modes,
                         fno_hidden_channels=hidden, fno_n_layers=4, gno_embed_channels=16,
                         in_gno_channel_mlp_hidden_layers=[64, 64], out_gno_channel_mlp_hidden_layers=[128, 64],
                         gno_use_open3d=False, gno_use_torch_scatter=False, projection_channel_ratio=2)
        self.head = nn.Sequential(nn.Linear(2 * H, 128), nn.GELU(), nn.Linear(128, 7))

    def forward(self, surf_xyz, surf_n, latent_xyz, latent_occ, out_xyz):
        """surf_xyz (n,3) surf_n (n,3) latent_xyz (lz,ly,lx,3) latent_occ (lz,ly,lx) out_xyz (m,3) → scalars_n (7,), fields (m,2)"""
        o = self.gino(input_geom=surf_xyz[None], latent_queries=latent_xyz[None], output_queries=out_xyz[None],
                      x=surf_n[None], latent_features=latent_occ[None, ..., None])[0]
        f, h = o[:, :2], o[:, 2:]
        s = self.head(torch.cat([h.mean(0), h.max(0).values]))
        return s, f
