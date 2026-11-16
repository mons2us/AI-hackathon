# 요소 밀도 npy(65,120) → 반모델 y 대칭 복원 → marching cubes → cpt.html 형식 메시 JSON (키 'B')
import numpy as np, json, base64, sys
from skimage import measure
M=np.load('pkg/FormProof_impl/data/grid_meta.npz'); nx,ny,nz=int(M['nx']),int(M['ny']),int(M['nz'])
xc,yc,zc=M['xc'],M['yc'],M['zc']
I=np.indices((nz,ny,nx)).reshape(3,-1).T[:,::-1].astype(float)   # (ix,iy,iz)
A=np.c_[I,np.ones(len(I))]; W=np.c_[xc,yc,zc]; T,_,_,_=np.linalg.lstsq(A,W,rcond=None)
print('affine resid',np.abs(A@T-W).max())
b64=lambda a: base64.b64encode(np.asarray(a,np.float32).tobytes()).decode()
for src,out in zip(sys.argv[1::2],sys.argv[2::2]):
    r=np.load(src).reshape(nz,ny,nx)
    # y 대칭: yc 최소 쪽이 대칭면이라 가정 → 뒤집어 붙임
    full=np.concatenate([r[:,::-1,:],r],axis=1); full=np.pad(full,1)
    v,f,_,_=measure.marching_cubes(full,0.5)
    iz,iy,ix=v[:,0]-1,v[:,1]-1-ny,v[:,2]-1      # iy: 0..ny-1 원래 쪽, 음수 = 대칭 쪽
    sgn=np.where(iy<-0.5,-1,1); iy2=np.where(iy<-0.5,-iy-1,iy)
    P=np.c_[ix,iy2,iz,np.ones(len(ix))]@T; y0=yc.min()-(T[1,1]*0.5)
    P[:,1]=np.where(sgn<0,2*y0-P[:,1],P[:,1])
    t=np.radians(35); X=P[:,0]*np.cos(t)-P[:,2]*np.sin(t); Z=P[:,0]*np.sin(t)+P[:,2]*np.cos(t); P[:,0]=X; P[:,2]=Z
    tri=P[f].reshape(-1,3); json.dump({'B':{'pos':b64(tri)}},open(out,'w')); print(out,len(f))
