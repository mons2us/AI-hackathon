# 일체형 비교 기준(처음 설계 방식): 클램프 + 처음 설계와 같은 단면(20×8 mm) 직선 보 + 시판형 평판 2 mm
import numpy as np
nx,ny,nz=83,20,37; x0,y0,z0=-24.,0.,-36.
I,J,K=np.meshgrid(np.arange(nx),np.arange(ny),np.arange(nz),indexing='ij'); I,J,K=[a.transpose(2,1,0).ravel() for a in (I,J,K)]
xc=x0+2*I+1; yc=y0+2*J+1; zc=z0+2*K+1
beam=(yc<10)&(zc>20)&(zc<28)&(xc>0)&(xc<140)
plate=(xc>-10)&(xc<140)&(zc>28)&(zc<30)
np.save('rbase_int.npy',(beam|plate).astype(float)); print((beam|plate).sum())
