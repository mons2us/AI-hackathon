"""P01 학습 형상 추가: GUI 1차 설계 → 최적 설계(formproof) 경로 형상 + 기준 형상. 출력: data/path_src.npz (r = packbits 전체 격자, names)
GUI 코드(10_입력_1차설계)는 읽기만 한다."""
import sys, os, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', '10_입력_1차설계'))
from formproof_input import integral as I
from formproof_input.inverse.anchor import AnchorBackend
A = AnchorBackend(); R, N = [], []
for t in np.linspace(0, 1, 41):
    full, _ = A.shape(float(t)); R.append(full); N.append(f'path_{t:.3f}')
for nm in ('base', 'formproof'):
    R.append(I.full_density(I.shape(nm)) > 0.5); N.append(f'gui_{nm}')
for f in ('rbin_int35f95g2', 'rho_body_v3'):
    R.append(np.load(os.path.join(H, 'data/reference', f + '.npy')).ravel() > 0.5); N.append(f'ref_{f}')
R = np.array(R, bool); np.savez(os.path.join(H, 'data/path_src.npz'), r=np.packbits(R, axis=1), names=np.array(N), ne=R.shape[1])
print(len(N), R.sum(1).min(), R.sum(1).max())
