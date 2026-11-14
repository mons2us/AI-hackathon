# Full 3D free-form topology optimisation of the bike phone mount WITH an additive-manufacturing overhang filter
# (Langelaar 2017, 45 deg, build direction +y = part printed lying on its side). Frequency constraints, volume objective.
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla, time, json, os, gc
from scipy.spatial import cKDTree
import mmapy, pypardiso
from fem3d import hex8_KB
E,nu,rho=1700.,0.38,1.27e-9; MP=float(os.environ.get('MP','0.254'))*1e-3; h=2.
FT=float(os.environ.get('FT','95')); LT=(2*np.pi*FT)**2
ITERS=int(os.environ.get('ITERS','160')); TAG=os.environ.get('TAG','am'); AM=os.environ.get('AM','1')=='1'
x0,z0=-24.,-36.; y0=float(os.environ.get("Y0","35")); nx,nz=62,39; ny=int(os.environ.get("NY","20"))          # full model y in [35,75]
KE,C,B0,xi=hex8_KB(E,nu,h)
ei=np.array([[i,j,k] for k in range(nz) for j in range(ny) for i in range(nx)]); I,J,K=ei.T
xc=x0+2*I+1; yc=y0+2*J+1; zc=z0+2*K+1; rr=np.sqrt(xc**2+zc**2); ay=np.abs(yc-55)
bore=rr<16.1; contact=(rr>=16.1)&(rr<20.6)&(ay<10); slit=(np.abs(xc)<=1)&(zc<0)&(rr<26)
ears=(np.abs(xc)>1)&(np.abs(xc)<9)&(zc>-34)&(zc<-14)&(ay<10); pad=(xc>80)&(xc<100)&(zc>16)&(zc<20)&(ay<10)
post=(xc>86)&(xc<96)&(zc>20)&(ay<6); holder=(xc>78)&(zc>20)&~post; above=(zc>24)&~post
void=bore|slit|holder|above; solid=(contact|ears|pad)&~void; design=~(void|solid|post); active=~void
print('design',design.sum(),'solid',solid.sum(),flush=True)
NX,NY,NZ=nx+1,ny+1,nz+1; nid=lambda i,j,k:(k*NY+j)*NX+i; corner=((xi+1)/2).astype(int)
en=np.stack([nid(I+c[0],J+c[1],K+c[2]) for c in corner],1); edof=np.stack([3*en,3*en+1,3*en+2],2).reshape(len(ei),24)
nn=NX*NY*NZ; gi=np.arange(nn)%NX; gj=(np.arange(nn)//NX)%NY; gk=np.arange(nn)//(NX*NY); nxc=x0+2*gi; nyc=y0+2*gj; nzc=z0+2*gk
used=np.zeros(nn,bool); used[en[active].ravel()]=True
fixn=np.where(used&(np.sqrt(nxc**2+nzc**2)<=16.7))[0]
topn=np.where(used&(gk==nz)&(nxc>=86)&(nxc<=96)&(np.abs(nyc-55)<=6))[0]; tipm=np.zeros(nn); tipm[topn]=MP/len(topn)
free=np.setdiff1d(np.where(np.repeat(used,3))[0],np.r_[3*fixn,3*fixn+1,3*fixn+2])
ea=edof[active].astype(np.int32); iK=np.repeat(ea,24,1).ravel(); jK=np.tile(ea,(1,24)).ravel()
didx=np.where(design)[0]; nd=len(didx); pos=np.c_[xc,yc,zc][didx]; R=float(os.environ.get('RF','5'))
tr=cKDTree(pos); pr=tr.query_pairs(R,output_type='ndarray'); a=np.r_[np.arange(nd),pr[:,0],pr[:,1]]; b=np.r_[np.arange(nd),pr[:,1],pr[:,0]]
Hf=sp.coo_matrix((R-np.linalg.norm(pos[a]-pos[b],axis=1),(a,b)),shape=(nd,nd)).tocsr(); Hs=np.asarray(Hf.sum(1)).ravel()
proj=lambda x,be,et=.5:(np.tanh(be*et)+np.tanh(be*(x-et)))/(np.tanh(be*et)+np.tanh(be*(1-et)))
dproj=lambda x,be,et=.5:be*(1-np.tanh(be*(x-et))**2)/(np.tanh(be*et)+np.tanh(be*(1-et)))
# ---- AM filter (layers along y) ----
PP=40.; NS=5; Q=PP+np.log(NS)/np.log(0.5); EPS=1e-4
fixed=~design; fixval=np.where(solid|post,1.0,0.0)
def grid(v): return v.reshape(nz,ny,nx).transpose(1,2,0)      # -> (j, i, k)
def ungrid(g): return g.transpose(2,0,1).reshape(-1)
FX=grid(fixed.astype(float))>0.5; FV=grid(fixval)
def neigh_sum(L):   # sum over support stencil (centre + 4 in-plane neighbours), zero padded
    P_=np.pad(L,1); return P_[1:-1,1:-1]+P_[:-2,1:-1]+P_[2:,1:-1]+P_[1:-1,:-2]+P_[1:-1,2:]
def am_forward(xh):  # xh: full-element blueprint densities (fixed elements already set)
    X=grid(xh); XI=np.zeros_like(X); S=np.zeros_like(X); KS=np.zeros_like(X)
    XI[0]=X[0]
    for j in range(1,ny):
        s=neigh_sum(XI[j-1]**PP)+1e-30; Xi=s**(1/Q); S[j]=s; KS[j]=Xi
        a_=X[j]; d=np.sqrt((a_-Xi)**2+EPS); v=0.5*(a_+Xi-d+np.sqrt(EPS))
        XI[j]=np.where(FX[j],FV[j],v)
    return XI,S,KS,X
def am_adjoint(lamXI,XI,S,KS,X):   # returns dF/dX (blueprint) given dF/dXI
    L=lamXI.copy(); dX=np.zeros_like(X)
    for j in range(ny-1,0,-1):
        a_=X[j]; Xi=KS[j]; d=np.sqrt((a_-Xi)**2+EPS)
        da=0.5*(1-(a_-Xi)/d); dxi=0.5*(1+(a_-Xi)/d)
        lj=np.where(FX[j],0.,L[j]); dX[j]+=lj*da
        mu=lj*dxi*(1/Q)*S[j]**(1/Q-1)          # d/dsum
        Pm=np.pad(mu,1); back=Pm[1:-1,1:-1]+Pm[:-2,1:-1]+Pm[2:,1:-1]+Pm[1:-1,:-2]+Pm[1:-1,2:]
        L[j-1]+=back*PP*XI[j-1]**(PP-1)
    dX[0]+=np.where(FX[0],0.,L[0]); return dX
P=3.; EMIN=1e-6; me0=rho*h**3
def interp(r):
    k=EMIN+(1-EMIN)*r**P; dk=(1-EMIN)*P*r**(P-1); m=np.where(r>0.3,r,r**3/0.09); dm=np.where(r>0.3,1.0,3*r**2/0.09); return k,dk,m,dm
def analyse(r,neig=4):
    k,dk,m,dm=interp(r); ke=np.where(design,k,0.); ke[solid]=1; ke[post]=20.
    Kg=sp.csr_matrix(((KE.ravel()[None,:]*ke[active][:,None]).ravel(),(iK,jK)),shape=(3*nn,3*nn))
    mel=np.where(design,m,0.); mel[solid]=1; mel[post]=0
    mn=np.zeros(nn); np.add.at(mn,en.ravel(),np.repeat(mel*me0/8,8)); mn+=tipm; Md=np.repeat(mn,3)
    A=Kg[free][:,free].tocsr(); ps=pypardiso.PyPardisoSolver(); ps.factorize(A)
    OP=sla.LinearOperator(A.shape,matvec=lambda v: ps.solve(A,v),dtype=float)
    lam,V=sla.eigsh(A,k=neig,M=sp.diags(Md[free]),sigma=0,OPinv=OP,tol=1e-8); ps.free_memory(everything=True); del ps; gc.collect()
    out=[]
    for q in range(neig):
        phi=np.zeros(3*nn); phi[free]=V[:,q]/np.sqrt(V[:,q]@(Md[free]*V[:,q]))
        pe=phi[edof]; sk=np.einsum('ij,jk,ik->i',pe,KE,pe); pn=(phi.reshape(-1,3)**2).sum(1); sm=pn[en].sum(1)*me0/8
        out.append((lam[q],np.where(design,dk*sk-lam[q]*dm*sm,0.)))
    return out
x=np.full(nd,0.5); START=int(os.environ.get('START','0'))
if START>0: x=np.load('x_%s.npy'%TAG)
xo1=x[:,None].copy(); xo2=x[:,None].copy(); low=np.zeros((nd,1)); upp=np.ones((nd,1)); mcon=4
sched={0:1,30:2,60:4,90:8,120:16}; ETAE=float(os.environ.get('ETAE','0.6')); t0=time.time()
for it in range(START,ITERS):
    be=[v for kk,v in sorted(sched.items()) if kk<=it][-1]
    xt=np.asarray(Hf@x).ravel()/Hs
    out_r={}
    for tag_,et in (('n',0.5),('e',ETAE)):
        xb=proj(xt,be,et); full=fixval.copy(); full[didx]=xb
        if AM: XI,S,KS,X=am_forward(full); r=ungrid(XI)
        else: r=full; XI=S=KS=X=None
        out_r[tag_]=(xb,r,(XI,S,KS,X))
    xbn,rn,amn=out_r['n']; xbe,re_,ame=out_r['e']
    res=analyse(re_)
    def chain(g_full,am_,et):   # g wrt printed densities (full) -> wrt x
        if AM:
            dX=ungrid(am_adjoint(grid(g_full),*am_)); g=dX[didx]
        else: g=g_full[didx]
        return np.asarray(Hf.T@(g*dproj(xt,be,et)/Hs)).ravel()
    vm=np.zeros(len(ei)); vm[design]=1.0/nd
    f0=rn[design].mean(); df0=chain(vm,amn,0.5)
    fval=np.array([1-r_[0]/LT for r_ in res]); dfdx=np.array([chain(-r_[1]/LT,ame,ETAE) for r_ in res])
    xn,_,_,_,_,_,_,_,_,low,upp=mmapy.mmasub(mcon,nd,it+1-START,x[:,None],np.zeros((nd,1)),np.ones((nd,1)),xo1,xo2,f0,df0[:,None],fval[:,None],dfdx,low,upp,1.,np.zeros((mcon,1)),1e4*np.ones((mcon,1)),np.zeros((mcon,1)),move=0.1)
    xo2=xo1.copy(); xo1=x[:,None].copy(); x=xn.ravel()
    massg=(rn[design].sum()+solid.sum())*me0*1e6
    print(json.dumps(dict(it=it,beta=be,mass_g=round(float(massg),1),f=[round(float(np.sqrt(r_[0])/2/np.pi),1) for r_ in res],t=round(time.time()-t0))),flush=True)
    if it%10==0 or it==ITERS-1:
        np.save('x_%s.npy'%TAG,x); np.save('rprint_%s.npy'%TAG,rn)
