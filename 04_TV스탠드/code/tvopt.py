import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla, time, json, os, warnings, gc
from scipy.spatial import cKDTree
import mmapy, pypardiso
from fem3d import hex8_KB
warnings.filterwarnings('ignore')
E,nu,rho=68900.,0.33,2.7e-9; g=9810.; h=float(os.environ.get('H','12.5'))
MTV=20.8e-3; WTV=MTV*g                       # N (t*mm/s^2)
F13=0.13*(20.8+3.0)*9.81                     # N, 13% of TV+stand(assumed 3 kg)
ZC,ZTOP=474.,890.
UMAX=float(os.environ.get('UMAX','2.0')); SAG=float(os.environ.get('SAG','1.0'))
ITERS=int(os.environ.get('ITERS','150')); TAG=os.environ.get('TAG','a'); ETAE=float(os.environ.get('ETAE','0.6')); START=int(os.environ.get('START','0'))
x0,y0,z0=0.,-150.,0.; nx,ny,nz=int(round(250/h)),int(round(300/h)),int(round(637.5/h))          # half model x in [0,250]
KE,C,B0,xi=hex8_KB(E,nu,h)
ei=np.array([[i,j,k] for k in range(nz) for j in range(ny) for i in range(nx)]); I,J,K=ei.T
xc=x0+h*I+h/2; yc=y0+h*J+h/2; zc=z0+h*K+h/2
tvband=(yc>-26)&(yc<0)&(zc>58)
front=(yc<-26)&(zc>58)
tv=tvband&(xc<212.5)&(zc>312.5)&(zc<637.5)         # rigid TV slab around VESA 400x300
vesa=(yc>0)&(yc<12.5)&(np.abs(xc-200)<=12.5)&((np.abs(zc-324)<=12.5)|(np.abs(zc-624)<=12.5))&(zc<637.5)
feet=(zc<12.5)&(np.abs(xc-200)<=25)&(np.abs(np.abs(yc)-125)<=25)
void=(tvband&~tv)|front
solid=(vesa|feet)&~void
design=~(void|solid|tv)
active=~void
print('design',design.sum(),'solid',solid.sum(),'tv',tv.sum(),flush=True)
NX,NY,NZ=nx+1,ny+1,nz+1; nid=lambda i,j,k:(k*NY+j)*NX+i; corner=((xi+1)/2).astype(int)
en=np.stack([nid(I+c[0],J+c[1],K+c[2]) for c in corner],1); edof=np.stack([3*en,3*en+1,3*en+2],2).reshape(len(ei),24)
nn=NX*NY*NZ; gi=np.arange(nn)%NX; gj=(np.arange(nn)//NX)%NY; gk=np.arange(nn)//(NX*NY); nxc=x0+h*gi; nyc=y0+h*gj; nzc=z0+h*gk
used=np.zeros(nn,bool); used[en[active].ravel()]=True
footn=np.unique(en[feet][:, :4].ravel()); footn=footn[nzc[footn]==0]
plane=np.where(used&(gi==0))[0]
tvn=np.unique(en[tv].ravel()); wt=np.where(nxc[tvn]==0,0.5,1.0); wt/=wt.sum()
def dist(Ftot,M):   # y- or x-direction force with moment via linear z distribution (half model gets half)
    dz=nzc[tvn]-nzc[tvn]@wt; a=M/((wt*dz**2).sum()); return wt*Ftot+wt*a*dz
Fl=np.zeros((3*nn,3))
Fl[3*tvn+2,0]=-wt*WTV/2                                  # gravity (sym)
Fl[3*tvn+1,1]=dist(F13/2,F13/2*(ZTOP-ZC))               # front-back push at TV top (sym)
Fl[3*tvn+0,2]=dist(F13/2,F13/2*(ZTOP-ZC))               # lateral push at TV top (antisym)
def freeset(bc):
    fd=[3*footn,3*footn+1,3*footn+2]
    fd.append(3*plane if bc=='S' else np.r_[3*plane+1,3*plane+2])
    return np.setdiff1d(np.where(np.repeat(used,3))[0],np.unique(np.concatenate(fd)))
FREE={'S':freeset('S'),'A':freeset('A')}
ea=edof[active].astype(np.int32); iK=np.repeat(ea,24,1).ravel(); jK=np.tile(ea,(1,24)).ravel(); del ea
didx=np.where(design)[0]; pos=np.c_[xc,yc,zc][didx]; R=float(os.environ.get('RF','31'))
tree=cKDTree(pos); pr=tree.query_pairs(R,output_type='ndarray')
a=np.r_[np.arange(len(didx)),pr[:,0],pr[:,1]]; b=np.r_[np.arange(len(didx)),pr[:,1],pr[:,0]]; w=R-np.linalg.norm(pos[a]-pos[b],axis=1)
mpos=pos.copy(); mpos[:,0]=-mpos[:,0]
Dm=tree.sparse_distance_matrix(cKDTree(mpos),R,output_type='coo_matrix'); ma,mb,mw=Dm.row,Dm.col,R-Dm.data; del Dm
Hf=sp.coo_matrix((np.r_[w,mw],(np.r_[a,ma],np.r_[b,mb])),shape=(len(didx),)*2).tocsr(); Hs=np.asarray(Hf.sum(1)).ravel()
proj=lambda xt,be,et=0.5:(np.tanh(be*et)+np.tanh(be*(xt-et)))/(np.tanh(be*et)+np.tanh(be*(1-et)))
dproj=lambda xt,be,et=0.5:be*(1-np.tanh(be*(xt-et))**2)/(np.tanh(be*et)+np.tanh(be*(1-et)))
P=3.; EMIN=1e-6
def analyse(rb):
    k=EMIN+(1-EMIN)*rb**P; dk=(1-EMIN)*P*rb**(P-1)
    ke=np.where(design,k,0.); ke[solid]=1; ke[tv]=100.
    Kg=sp.csr_matrix(((KE.ravel()[None,:].astype(np.float64)*ke[active][:,None]).ravel(),(iK,jK)),shape=(3*nn,3*nn))
    out=[]
    for bc,cols in (('S',[0,1]),('A',[2])):
        fr=FREE[bc]; A=Kg[fr][:,fr].tocsr(); ps=pypardiso.PyPardisoSolver(); ps.factorize(A)
        for c in cols:
            u=np.zeros(3*nn); u[fr]=ps.solve(A,Fl[fr,c]); comp=Fl[:,c]@u
            ue=u[edof]; ce=np.einsum('ij,jk,ik->i',ue,KE,ue); dc=np.where(design,-dk*ce,0.)
            out.append((comp,dc,u))
        ps.free_memory(everything=True); del ps; gc.collect()
    return out
# constraint scales: full compliance = 2*half ; u = Cfull/F
LIM=[WTV*SAG/2, F13*UMAX/2, F13*UMAX/2]
nd=len(didx); x=np.full(nd,0.3)
if START>0: x=np.load('x_%s.npy'%TAG)
xmin=np.zeros((nd,1)); xmax=np.ones((nd,1)); xold1=x[:,None].copy(); xold2=x[:,None].copy(); low=np.zeros((nd,1)); upp=np.ones((nd,1))
mcon=3; a0=1.; aa=np.zeros((mcon,1)); cc=1e4*np.ones((mcon,1)); dd=np.zeros((mcon,1))
S_=int(os.environ.get('STG','30')); sched={0:1,S_:2,2*S_:4,3*S_:8,4*S_:16}; me0=rho*h**3; t0=time.time()
for it in range(START,ITERS):
    beta=[v for kk,v in sorted(sched.items()) if kk<=it][-1]
    xt=np.asarray(Hf@x).ravel()/Hs; xb=proj(xt,beta); xe=proj(xt,beta,ETAE)
    rb=np.zeros(len(ei)); rb[didx]=xb; re_=np.zeros(len(ei)); re_[didx]=xe
    res=analyse(re_)
    f0=xb.mean(); df0=np.asarray(Hf.T@(np.ones(nd)/nd*dproj(xt,beta)/Hs)).ravel()
    fval=np.array([r[0]/L-1 for r,L in zip(res,LIM)])
    dfdx=np.array([np.asarray(Hf.T@((r[1][didx]/L)*dproj(xt,beta,ETAE)/Hs)).ravel() for r,L in zip(res,LIM)])
    xn,_,_,_,_,_,_,_,_,low,upp=mmapy.mmasub(mcon,nd,it+1-START,x[:,None],xmin,xmax,xold1,xold2,f0,df0[:,None],fval[:,None],dfdx,low,upp,a0,aa,cc,dd,move=0.1)
    xold2=xold1.copy(); xold1=x[:,None].copy(); x=xn.ravel()
    mass=(xb.sum()+solid.sum())*me0*2*1e3   # kg
    print(json.dumps(dict(it=it,beta=beta,mass_kg=round(float(mass),3),sag=round(float(2*res[0][0]/WTV),3),u_fb=round(float(2*res[1][0]/F13),3),u_lat=round(float(2*res[2][0]/F13),3),t=round(time.time()-t0))),flush=True)
    if it%10==0 or it==ITERS-1: np.save('x_%s.npy'%TAG,x); np.save('xb_%s.npy'%TAG,rb)
    if it%5==0:
        s=np.zeros(len(ei),np.float32); s[didx]=xb
        with open('snaps_%s.bin'%TAG,'ab') as fo: fo.write((np.clip(s,0,1)*255).astype(np.uint8).tobytes())
