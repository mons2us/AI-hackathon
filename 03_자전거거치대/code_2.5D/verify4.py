import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla, json, time, sys
from fem3d import hex8_KB
E,nu,rho=float(__import__('os').environ.get('EV','1700')),0.38,1.27e-9; g=9810.; MP=0.25e-3; h=float(__import__('os').environ.get('HV','1.0'))
f=np.load(sys.argv[1]); step=int(round(h/0.5))
fs=f[::step,::step,::step]; x0,y0,z0=-26.,float(__import__('os').environ.get('YO','36')),-36.
nxp,nyp,nzp=fs.shape
S=fs>0.5
# extend z for post
ZT=42.; nzt=int((ZT-z0)/h)+1; S2=np.zeros((nxp,nyp,nzt),bool); S2[:,:,:nzp]=S
P=np.zeros_like(S2); xs=x0+np.arange(nxp)*h; ys=y0+np.arange(nyp)*h; zs=z0+np.arange(nzt)*h
P[np.ix_((xs>=86)&(xs<=96),(ys>=49)&(ys<=61),(zs>=20.5)&(zs<=ZT))]=True
S2&=~P
from scipy import ndimage
lab,n=ndimage.label(S2|P); XX=x0+np.arange(nxp)[:,None,None]*h; ZZ=z0+np.arange(nzt)[None,None,:]*h
near=(np.sqrt(XX**2+ZZ**2)<=18.0)&np.ones_like(S2); keep=np.unique(lab[near&(S2|P)]); keep=keep[keep>0]
mask=np.isin(lab,keep); print('removed voxels',int(((S2|P)&~mask).sum())); S2&=mask; P&=mask
KE,C,B0,xi=hex8_KB(E,nu,h)
els=np.argwhere(S2|P); isP=P[els[:,0],els[:,1],els[:,2]]
# nodes: voxel centered at (xs,ys,zs) -> corners at +-h/2 ; node grid index (i..i+1)
NX,NY,NZ=nxp+1,nyp+1,nzt+1
nid=lambda i,j,k:(k*NY+j)*NX+i
corner=((xi+1)/2).astype(int)
en=np.stack([nid(els[:,0]+c[0],els[:,1]+c[1],els[:,2]+c[2]) for c in corner],1)
un,inv=np.unique(en,return_inverse=True); en2=inv.reshape(en.shape); nn=len(un)
edof=np.stack([3*en2,3*en2+1,3*en2+2],2).reshape(len(els),24)
ke=np.where(isP,20.,1.)
iK=np.repeat(edof,24,1).ravel(); jK=np.tile(edof,(1,24)).ravel()
Kg=sp.coo_matrix(((KE.ravel()[None,:]*ke[:,None]).ravel(),(iK,jK)),shape=(3*nn,3*nn)).tocsc()
# node coords
gi=un%NX; gj=(un//NX)%NY; gk=un//(NX*NY)
nxc=x0-h/2+gi*h; nyc=y0-h/2+gj*h; nzc=z0-h/2+gk*h
fixn=np.where(np.sqrt(nxc**2+nzc**2)<=16.7)[0]
top=np.where((nzc>ZT)&(nxc>=86)&(nxc<=97)&(nyc>=49)&(nyc<=62))[0]
fd=np.r_[3*fixn,3*fixn+1,3*fixn+2]; free=np.setdiff1d(np.arange(3*nn),fd)
m=np.zeros(nn); np.add.at(m,en2[~isP].ravel(),rho*h**3/8); m[top]+=MP/len(top)
F=np.zeros((3*nn,2)); F[3*top+2,0]=-MP*5*g/len(top); F[3*top+1,1]=MP*5*g/len(top)
t=time.time(); Kf=Kg[free][:,free].tocsr(); import pyamg
ml=pyamg.smoothed_aggregation_solver(Kf,B=None,max_coarse=2000); Mp=ml.aspreconditioner()
U=np.zeros((3*nn,2))
for c in range(2):
    xs,info=sla.cg(Kf,F[free,c],M=Mp,rtol=1e-10,maxiter=3000); U[free,c]=xs
Md=sp.diags(np.repeat(m,3)[free]).tocsr()
X0=np.random.default_rng(0).standard_normal((Kf.shape[0],6))
w,_=sla.lobpcg(Kf,X0,B=Md,M=Mp,tol=1e-6,maxiter=400,largest=False); w=np.sort(w)[:2]
ue=U[:,0][edof]; sg=(C@B0@ue.T).T; vm=np.sqrt(0.5*((sg[:,0]-sg[:,1])**2+(sg[:,1]-sg[:,2])**2+(sg[:,2]-sg[:,0])**2)+3*(sg[:,3:]**2).sum(1))
ue=U[:,1][edof]; sg=(C@B0@ue.T).T; vmy=np.sqrt(0.5*((sg[:,0]-sg[:,1])**2+(sg[:,1]-sg[:,2])**2+(sg[:,2]-sg[:,0])**2)+3*(sg[:,3:]**2).sum(1))
ex=x0+els[:,0]*h; ez=z0+els[:,2]*h; ok=(~isP)&(np.sqrt(ex**2+ez**2)>18.5)
print(json.dumps(dict(h=h,elements=int((~isP).sum()),mass_g=float((~isP).sum()*h**3*rho*1e6),f=[float(v) for v in np.sqrt(w)/2/np.pi],
 tipz=float(-U[3*top+2,0].mean()),tipy=float(U[3*top+1,1].mean()),vmz=float(vm[ok].max()),vmy=float(vmy[ok].max()),dof=len(free),time=round(time.time()-t,1))))
