import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla
from scipy import ndimage
from fem3d import Grid
import os
E,nu,rho=float(os.environ.get('EMOD','2000')),0.38,1.27e-9; g=9810.; MP=0.25e-3   # phone 200 g + clamp 50 g (t)
h=2.; ZB=float(os.environ.get('ZB','-16')); YW=float(os.environ.get('YW','20')); X0,Y0,Z0=20.,55-YW/2,ZB; nx,ny=40,int(YW/2); jp0=int((49-Y0)/2); KD=int((16-ZB)/2); nz=int((42-ZB)/2)
G=Grid(nx,ny,nz,h,E,nu)
ei=np.array([[i,j,k] for k in range(nz) for j in range(ny) for i in range(nx)])
I,J,K=ei.T
design=(K<KD)
pad=(I>=30)&(K>=KD)&(K<=KD+1)
post=(I>=33)&(I<=37)&(J>=jp0)&(J<=jp0+5)&(K>=KD+2)
active=design|pad|post
root=design&(I==0)
EPOST=20.
# nodes
used=np.zeros(G.nn,bool); used[(G.edof[active][:,::3]//3).ravel()]=True
fixed=[G.nid(0,j,k) for k in range(0,KD+1) for j in range(ny+1)]
fd=np.array([[3*n,3*n+1,3*n+2] for n in fixed]).ravel()
free=np.setdiff1d(np.where(np.repeat(used,3))[0],fd)
topn=np.array(sorted({G.nid(i,j,nz) for i in range(33,39) for j in range(jp0,jp0+7)}))
def loads(lat):
    F=np.zeros((G.ndof,2)); F[3*topn+2,0]=-MP*5*g/len(topn); F[3*topn+1,1]=MP*lat*g/len(topn); return F
extra=np.zeros(G.nn); extra[topn]+=MP/len(topn)
def stiff(rho_e,p=3.,emin=1e-9):
    ke=np.zeros(G.ne); ke[design]=emin+rho_e[design]**p; ke[pad]=1.; ke[post]=EPOST; return ke
def clean(s):
    s=s.copy(); m=(s>0.5)&design
    v=np.zeros(G.ne,bool); v[m|pad|post]=True
    lab,n=ndimage.label(v.reshape(nz,ny,nx)); keep=np.unique(lab[:,:,0]); keep=keep[keep>0]
    v=np.isin(lab,keep).ravel(); out=np.zeros(G.ne); out[v&design]=1; return out
def evaluate(s,lat=5.):
    ke=np.zeros(G.ne); ke[design]=np.where(s[design]>0.5,1.,0.); ke[pad]=1; ke[post]=EPOST
    on=ke>0; u2=np.zeros(G.nn,bool); u2[(G.edof[on][:,::3]//3).ravel()]=True
    fr=free[u2[free//3]]
    Kf=G.K(ke)[fr][:,fr]; me=np.where(on&~post,1.,0.)*rho*h**3
    M=sp.diags(G.Mlump(me,extra)[fr])
    F=loads(lat); lu=sla.splu(Kf); U=np.zeros((G.ndof,2)); U[fr]=lu.solve(F[fr])
    w,V=sla.eigsh(Kf,k=2,M=M,sigma=0)
    vm=[]
    for lc in (0,1):
        ue=U[:,lc][G.edof]; sg=(G.C@G.B0@ue.T).T
        v=np.sqrt(0.5*((sg[:,0]-sg[:,1])**2+(sg[:,1]-sg[:,2])**2+(sg[:,2]-sg[:,0])**2)+3*(sg[:,3:]**2).sum(1)); v[~(on&~post)]=0; vm.append(v)
    modes=[]
    for m in range(2):
        vv=np.zeros(G.ndof); vv[fr]=V[:,m]; modes.append(vv)
    return dict(mass=float(me.sum()*1e6),f=[float(x) for x in np.sqrt(w)/2/np.pi],
                tipz=float(-U[3*topn+2,0].mean()),tipy=float(U[3*topn+1,1].mean()),
                vmz=float(vm[0][~root].max()),vmy=float(vm[1][~root].max())),dict(U=U,vm=vm,modes=modes,on=on)
# 2D filter on (i,k) for extrusion along y
ik=np.array([[i,k] for k in range(KD) for i in range(nx)])
from scipy.spatial import cKDTree
R=2.2; pr=cKDTree(ik.astype(float)).query_pairs(R,output_type='ndarray')
a=np.r_[np.arange(len(ik)),pr[:,0],pr[:,1]]; b=np.r_[np.arange(len(ik)),pr[:,1],pr[:,0]]
d=np.linalg.norm(ik[a]-ik[b],axis=1); Hf=sp.coo_matrix((R-d,(a,b)),shape=(len(ik),)*2).tocsr(); Hs=np.asarray(Hf.sum(1)).ravel()
# map element -> 2D var index (design only)
e2v=np.full(G.ne,-1); e2v[design]=K[design]*nx+I[design]
def expand(x2):
    r=np.zeros(G.ne); r[design]=x2[e2v[design]]; return r
