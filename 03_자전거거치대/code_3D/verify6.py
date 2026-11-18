# test-oriented verification: masses, frequencies vs phone mass, hanging-weight deflection, directional stresses (interlayer check)
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla, json, sys, pypardiso
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
# frequencies vs payload mass (phone + holder)
OP=sla.LinearOperator(A.shape,matvec=lambda v: ps.solve(A,v),dtype=float)
for MP in (0.214,0.254,0.274):
    m=np.zeros(nn); np.add.at(m,en2[~isP].ravel(),rho*h**3/8); m[top]+=MP*1e-3/len(top)
    w,_=sla.eigsh(A,k=2,M=sp.diags(np.repeat(m,3)[free]),sigma=0,OPinv=OP); out['f1_%dg'%int(MP*1000)]=round(float(np.sqrt(w[0])/2/np.pi),1)
# hanging weight at holder top (vertical, 0.5 kg and 1 kg): deflection
for kg in (0.5,1.0):
    F=np.zeros(3*nn); F[3*top+2]=-kg*1e-3*g/len(top); U=np.zeros(3*nn); U[free]=ps.solve(A,F[free]); out['defl_%gkg_mm'%kg]=round(float(-U[3*top+2].mean()),3)
# 48.5 g shock (payload 254 g): directional normal stresses -> interlayer check for build direction x/y/z
MP=0.254e-3; ex=x0+els[:,0]*h; ez=z0+els[:,2]*h; ok=(~isP)&(np.sqrt(ex**2+ez**2)>19.5)
res={}
for c,nm in ((2,'shock_z'),(1,'shock_y')):
    F=np.zeros(3*nn); F[3*top+c]=(-1 if c==2 else 1)*MP*PEAK*g/len(top); U=np.zeros(3*nn); U[free]=ps.solve(A,F[free])
    s=(C@B0@U[edof].T).T; vm=np.sqrt(0.5*((s[:,0]-s[:,1])**2+(s[:,1]-s[:,2])**2+(s[:,2]-s[:,0])**2)+3*(s[:,3:]**2).sum(1))
    r=dict(vm999=round(float(np.percentile(vm[ok],99.9)),1))
    for k,ax in enumerate('xyz'): r['sig_'+ax+'_tens999']=round(float(np.percentile(np.maximum(s[ok,k],0),99.9)),1)
    res[nm]=r
out['shock']=res; print(json.dumps(out))
