# validation: straight fin, base T fixed, convective sides+tip-adiabatic, vs analytic
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla
from thermal3d import hex8_cond, quad_mass, FACES, _xi
k=167.; hc=10.; L=100.; a=4.; h=1.0          # W/mK, W/m2K, mm   (convert to mm: k W/mK = 1e-3 W/mmK, h W/m2K = 1e-6 W/mm2K)
kk=k*1e-3; hh=hc*1e-6
nx,ny,nz=int(L/h),int(a/h),int(a/h)
E=[(i,j,l) for l in range(nz) for j in range(ny) for i in range(nx)]
NX,NY=nx+1,ny+1; nid=lambda i,j,l:(l*NY+j)*NX+i; cor=((_xi+1)/2).astype(int)
en=np.array([[nid(i+c[0],j+c[1],l+c[2]) for c in cor] for (i,j,l) in E]); nn=NX*NY*(nz+1)
Ke=hex8_cond(kk,h); Mf=quad_mass(h)
rows=[];cols=[];vals=[]
for e in en: rows+=np.repeat(e,8).tolist(); cols+=np.tile(e,8).tolist(); vals+=Ke.ravel().tolist()
f=np.zeros(nn)
S=set(E)
for (i,j,l),e in zip(E,en):
    for n,fl in FACES.items():
        if n[0]!=0: continue                       # x faces: base fixed, tip adiabatic
        if (i,j+n[1],l+n[2]) in S: continue
        fn=e[fl]; rows+=np.repeat(fn,4).tolist(); cols+=np.tile(fn,4).tolist(); vals+=(hh*Mf).ravel().tolist()
K=sp.coo_matrix((vals,(rows,cols)),shape=(nn,nn)).tocsr()
Tinf=0.; Tb=1.
base=np.where(np.arange(nn)%NX==0)[0]; free=np.setdiff1d(np.arange(nn),base)
T=np.zeros(nn); T[base]=Tb
T[free]=sla.spsolve(K[free][:,free],f[free]-K[free][:,base]@T[base])
m=np.sqrt(hh*4*a/(kk*a*a)); x=np.arange(NX)*h
Ta=np.cosh(m*(L-x))/np.cosh(m*L)
Tn=T.reshape(nz+1,NY,NX).mean((0,1))
print('m',m,'tip num',Tn[-1],'tip analytic',Ta[-1],'max err',np.abs(Tn-Ta).max())
