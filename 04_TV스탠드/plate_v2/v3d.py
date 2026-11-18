# 3D check of the extruded plate foot (includes out-of-plane lateral shear)
import numpy as np, scipy.sparse as sp, json, sys, pypardiso
from fem3d import hex8_KB
E,nu=68900.,0.33; h=1.0; T=10
b=np.load('bin_%s.npy'%sys.argv[1])           # (nz,ny)
nz,ny=b.shape; nx=T
KE,C,B0,xi=hex8_KB(E,nu,h)
kk,jj=np.where(b); ii=np.repeat(np.arange(nx),len(kk)); kk=np.tile(kk,nx); jj=np.tile(jj,nx)
NX,NY=nx+1,ny+1; nid=lambda i,j,k:(k*NY+j)*NX+i; cor=((xi+1)/2).astype(int)
en=np.stack([nid(ii+c[0],jj+c[1],kk+c[2]) for c in cor],1); edof=np.stack([3*en,3*en+1,3*en+2],2).reshape(len(ii),24).astype(np.int64)
nn=NX*NY*(nz+1); gi=np.arange(nn)%NX; gj=(np.arange(nn)//NX)%NY; gk=np.arange(nn)//(NX*NY)
Yn=-150+gj*h; Zn=gk*h
used=np.zeros(nn,bool); used[en.ravel()]=True
fixn=np.where(used&(gk==0))[0]
topn=np.where(used&(gk==nz)&(np.abs(Yn)<=20))[0]; w=np.ones(len(topn))/len(topn); dy=Yn[topn]
MT=20.8; g=9.81; W=MT*g; F13=0.13*(MT+1.2)*g; ZB=120.; ZT=ZB+832.; SPAN=1200.
F=np.zeros((3*nn,3))
F[3*topn+2,0]=-W/2*w
a=(F13/2*(ZT-ZB))/((w*dy**2).sum()); F[3*topn+1,1]=F13/2*w; F[3*topn+2,1]=-a*w*dy
F[3*topn+2,2]=-(W/2+F13*ZT/SPAN)*w; F[3*topn+0,2]=F13/2*w     # lateral: extra vertical + out-of-plane shear
Kg=sp.csr_matrix((np.tile(KE.ravel(),len(edof)),(np.repeat(edof,24,1).ravel(),np.tile(edof,(1,24)).ravel())),shape=(3*nn,3*nn))
fr=np.setdiff1d(np.where(np.repeat(used,3))[0],np.r_[3*fixn,3*fixn+1,3*fixn+2])
U=np.zeros((3*nn,3)); U[fr]=pypardiso.spsolve(Kg[fr][:,fr].tocsr(),F[fr])
out=dict(mass_g=round(len(ii)*h**3*2.7e-3,1))
sag=-(U[3*topn+2,0]@w); ux=U[3*topn+1,1]@w; th=-((U[3*topn+2,1]*w*dy).sum()/((w*dy**2).sum())); utop=ux+th*(ZT-ZB)
ulat=np.abs(U[3*topn,2]@w)
out.update(sag=round(sag,4),utop_fb=round(utop,3),u_lat_attach=round(ulat,4))
for c,nm in enumerate(['g','fb','lat']):
    ue=U[:,c][edof]; s=(C@B0@ue.T).T; vm=np.sqrt(0.5*((s[:,0]-s[:,1])**2+(s[:,1]-s[:,2])**2+(s[:,2]-s[:,0])**2)+3*(s[:,3:]**2).sum(1))
    out['vm_'+nm]=round(float(np.percentile(vm,99.9)),1)
print(json.dumps(out))
