# test-oriented verification: masses, frequencies vs phone mass, hanging-weight deflection, directional stresses (interlayer check)
import os, numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla, json, sys, pypardiso
from scipy import ndimage
from fem3d import hex8_KB
E,nu,rho=1700.,0.38,1.27e-9; g=9810.; h=1.0; PEAK=48.5
d=np.load(sys.argv[1]); S=d['S'].astype(bool); x0,y0,z0=[float(v) for v in d['origin']]
nxp,nyp,nz0=S.shape; ZT=42.; nzt=int((ZT-z0)/h)+1; S2=np.zeros((nxp,nyp,max(nzt,nz0)),bool); S2[:,:,:nz0]=S; nzt=S2.shape[2]
xs=x0+np.arange(nxp)*h; ys=y0+np.arange(nyp)*h; zs=z0+np.arange(nzt)*h
P=np.zeros_like(S2); P[np.ix_((xs>=86)&(xs<=96),(ys>=49)&(ys<=61),(zs>=19.5)&(zs<=ZT))]=True; S2&=~P
lab,n=ndimage.label(S2|P); XX=xs[:,None,None]; ZZ=zs[None,None,:]
near=(np.sqrt(XX**2+ZZ**2)<=18.0)&np.ones_like(S2); keep=np.unique(lab[near&(S2|P)]); keep=keep[keep>0]
mask=np.isin(lab,keep); S2&=mask; P&=mask
KE,C,B0,xi=hex8_KB(E,nu,h)
els=np.argwhere(S2|P); isP=P[els[:,0],els[:,1],els[:,2]]
NX,NY,NZ=nxp+1,nyp+1,nzt+1; nid=lambda i,j,k:(k*NY+j)*NX+i; corner=((xi+1)/2).astype(int)
en=np.stack([nid(els[:,0]+c[0],els[:,1]+c[1],els[:,2]+c[2]) for c in corner],1)
un,inv=np.unique(en,return_inverse=True); en2=inv.reshape(en.shape); nn=len(un)
edof=np.stack([3*en2,3*en2+1,3*en2+2],2).reshape(len(els),24); ke=np.where(isP,20.,1.)
Kg=sp.coo_matrix(((KE.ravel()[None,:]*ke[:,None]).ravel(),(np.repeat(edof,24,1).ravel(),np.tile(edof,(1,24)).ravel())),shape=(3*nn,3*nn)).tocsr()
gi=un%NX; gj=(un//NX)%NY; gk=un//(NX*NY); nxc=x0-h/2+gi*h; nzc=z0-h/2+gk*h
fixn=np.where(np.sqrt(nxc**2+nzc**2)<=16.7)[0]; pn=np.unique(en2[isP]); zt=nzc[pn].max(); top=pn[nzc[pn]>=zt-1e-6]
free=np.setdiff1d(np.arange(3*nn),np.r_[3*fixn,3*fixn+1,3*fixn+2])
A=Kg[free][:,free].tocsr(); ps=pypardiso.PyPardisoSolver(); ps.factorize(A)
out=dict(mass_g=round(float((~isP).sum()*h**3*rho*1e6),1))

# --- 시스템 검증: 폰+받침대를 강체(질량+회전관성)로 붙여 고유진동수 계산 ---
import json as _j
M_T=float(os.environ.get('MSYS','0.340'))*1e-3        # t (= kg×1e-3)
CG=np.array([91.,55.,float(os.environ.get('CGZ','36.5'))])
Lx,Ly,Lz=[float(v) for v in os.environ.get('BOX','165,80,15').split(',')]   # 폰 긴 쪽 = x(앞뒤) 가정
pos=np.c_[x0-h/2+gi*h, y0-h/2+gj*h, nzc][top]-CG
nt=len(top); T=np.zeros((3*nt,6))
for i,(rx,ry,rz) in enumerate(pos):
    T[3*i:3*i+3,:3]=np.eye(3); T[3*i:3*i+3,3:]=-np.array([[0,-rz,ry],[rz,0,-rx],[-ry,rx,0]])
Tp=np.linalg.pinv(T)
def run(J):
    Mrb=np.diag([M_T,M_T,M_T,*J])
    Ma=Tp.T@Mrb@Tp; d=np.r_[3*top[:,None]+np.arange(3)].reshape(-1) if False else (3*top[:,None]+np.arange(3)).reshape(-1)
    m=np.zeros(nn); np.add.at(m,en2[~isP].ravel(),rho*h**3/8)
    Mg=sp.diags(np.repeat(m,3)).tolil()
    for a in range(3*nt):
        for b in range(3*nt): Mg[d[a],d[b]]+=Ma[a,b]
    Mf=Mg.tocsr()[free][:,free]
    w,V=sla.eigsh(A,k=3,M=Mf,sigma=0,OPinv=OP); return [round(float(np.sqrt(x)/2/np.pi),1) for x in w]
OP=sla.LinearOperator(A.shape,matvec=lambda v: ps.solve(A,v),dtype=float)
Jfull=[M_T*(Ly**2+Lz**2)/12, M_T*(Lx**2+Lz**2)/12, M_T*(Lx**2+Ly**2)/12]
out['f_point_mass']=run([0,0,0]); out['f_rigid_inertia']=run(Jfull)
print(_j.dumps(out))
