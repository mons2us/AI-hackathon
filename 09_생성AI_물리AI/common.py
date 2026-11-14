import numpy as np, sys
sys.path.insert(0,'../opt')
from eval3d import xc,yc,zc,design,solid,post,nx,ny,nz
DI=np.where(design)[0]; ND=len(DI)
PTS=np.c_[(xc[DI]-38)/62,(yc[DI]-55)/20,(zc[DI]+-2)/39].astype(np.float32)   # 대략 [-1,1]
SOL=(solid|post).astype(np.float32)
def load(f):
    d=np.load(f); k=d['lab'][:,1]>5; occ=np.unpackbits(d['occ'][k],axis=1)[:,:ND].astype(np.float32); return occ,d['lab'][k]
def to_grid(occ_d):   # (B,ND) -> (B,nz,ny,nx,1) 전체 격자 (고정부 포함)
    import jax.numpy as jnp
    B=occ_d.shape[0]; full=jnp.tile(jnp.asarray(SOL)[None],(B,1)); full=full.at[:,DI].set(occ_d)
    return full.reshape(B,nz,ny,nx,1)
