import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla, time, json, sys, os
from scipy.spatial import cKDTree
import mmapy, pyamg, warnings, pypardiso
warnings.filterwarnings('ignore')
PREV={}
from fem3d import hex8_KB
E,nu,rho=1700.,0.38,1.27e-9; MP=0.25e-3; h=2.
FT=float(os.environ.get('FT','91.2')); LT=(2*np.pi*FT)**2
ITERS=int(os.environ.get('ITERS','150')); TAG=os.environ.get('TAG','a')
x0,y0,z0=-24.,55.,-36.; nx,ny,nz=62,10,39          # half model y in [55,75]
KE,C,B0,xi=hex8_KB(E,nu,h)
ei=np.array([[i,j,k] for k in range(nz) for j in range(ny) for i in range(nx)]); I,J,K=ei.T
xc=x0+2*I+1; yc=y0+2*J+1; zc=z0+2*K+1; rr=np.sqrt(xc**2+zc**2)
bore=rr<16.1
contact=(rr>=16.1)&(rr<20.6)&(yc<65)
slit=(np.abs(xc)<=1)&(zc<0)&(rr<26)
ears=(np.abs(xc)>1)&(np.abs(xc)<9)&(zc>-34)&(zc<-14)&(yc<65)
pad=(xc>80)&(xc<100)&(zc>16)&(zc<20)&(yc<65)
post=(xc>86)&(xc<96)&(zc>20)&(yc<61)
holder=(xc>78)&(zc>20)&~post
above=((zc>24)&~post)|(yc>float(os.environ.get('YMAX','75')))
void=bore|slit|holder|above
solid=(contact|ears|pad)&~void
design=~(void|solid|post)
active=~void
print('design elems',design.sum(),'solid',solid.sum(),'post',post.sum(),flush=True)
# nodes
NX,NY,NZ=nx+1,ny+1,nz+1
nid=lambda i,j,k:(k*NY+j)*NX+i
corner=((xi+1)/2).astype(int)
en=np.stack([nid(I+c[0],J+c[1],K+c[2]) for c in corner],1)
edof=np.stack([3*en,3*en+1,3*en+2],2).reshape(len(ei),24)
nn=NX*NY*NZ; gi=np.arange(nn)%NX; gj=(np.arange(nn)//NX)%NY; gk=np.arange(nn)//(NX*NY)
nxc=x0+2*gi; nyc=y0+2*gj; nzc=z0+2*gk
used=np.zeros(nn,bool); used[en[active].ravel()]=True
fixn=np.where(used&(np.sqrt(nxc**2+nzc**2)<=16.7))[0]
plane=np.where(used&(gj==0))[0]
topn=np.where(used&(gk==nz)&(nxc>=86)&(nxc<=96)&(nyc<=61))[0]
wt=np.where(nyc[topn]==55,0.5,1.0); tipm=np.zeros(nn); tipm[topn]=MP/2*wt/wt.sum()
def freeset(bc):
    fd=[3*fixn,3*fixn+1,3*fixn+2]
    if bc=='S': fd.append(3*plane+1)          # symmetric: uy=0
    else: fd+= [3*plane,3*plane+2]            # antisymmetric: ux=uz=0
    fd=np.unique(np.concatenate(fd)); dof=np.where(np.repeat(used,3))[0]
    return np.setdiff1d(dof,fd)
FREE={b:freeset(b) for b in 'SA'}
RBM={}
for bc in 'SA':
    fr=FREE[bc]; nd_=fr//3; c_=fr%3; X=nxc[nd_];Y=nyc[nd_];Z=nzc[nd_]
    Bm=np.zeros((len(fr),6)); 
    for q in range(3): Bm[c_==q,q]=1
    # rotations
    Bm[c_==0,3]=-Y[c_==0]; Bm[c_==1,3]=X[c_==1]
    Bm[c_==1,4]=-Z[c_==1]; Bm[c_==2,4]=Y[c_==2]
    Bm[c_==0,5]=Z[c_==0]; Bm[c_==2,5]=-X[c_==2]
    RBM[bc]=Bm
iK=np.repeat(edof[active],24,1).ravel(); jK=np.tile(edof[active],(1,24)).ravel()
# EXTRUSION along y (print lying on the side face: every wall vertical -> no supports, layers normal to y)
didx=np.where(design)[0]
col=I[didx]*nz+K[didx]; ucol,inv=np.unique(col,return_inverse=True); nv=len(ucol)
P_=sp.csr_matrix((np.ones(len(didx)),(np.arange(len(didx)),inv)),shape=(len(didx),nv))
cpos=np.c_[x0+2*(ucol//nz)+1, z0+2*(ucol%nz)+1]
R=float(os.environ.get('RF','3.2')); tree=cKDTree(cpos); pr=tree.query_pairs(R,output_type='ndarray')
a=np.r_[np.arange(nv),pr[:,0],pr[:,1]]; b=np.r_[np.arange(nv),pr[:,1],pr[:,0]]; w=R-np.linalg.norm(cpos[a]-cpos[b],axis=1)
Hf=sp.coo_matrix((w,(a,b)),shape=(nv,nv)).tocsr(); Hs=np.asarray(Hf.sum(1)).ravel()
def proj(xt,beta,eta=0.5):
    return (np.tanh(beta*eta)+np.tanh(beta*(xt-eta)))/(np.tanh(beta*eta)+np.tanh(beta*(1-eta)))
def dproj(xt,beta,eta=0.5):
    return beta*(1-np.tanh(beta*(xt-eta))**2)/(np.tanh(beta*eta)+np.tanh(beta*(1-eta)))
P=3.; EMIN=1e-6
def interp(rb):
    k=EMIN+(1-EMIN)*rb**P; dk=(1-EMIN)*P*rb**(P-1)
    m=np.where(rb>0.3,rb,rb**3/0.09); dm=np.where(rb>0.3,1.0,3*rb**2/0.09)
    return k,dk,m,dm
me0=rho*h**3
def analyse(rbar_all,neig=2):
    k,dk,m,dm=interp(rbar_all)
    ke=np.where(design,k,0.); ke[solid]=1; ke[post]=20.
    Kg=sp.coo_matrix(((KE.ravel()[None,:]*ke[active][:,None]).ravel(),(iK,jK)),shape=(3*nn,3*nn)).tocsc()
    mel=np.where(design,m,0.); mel[solid]=1; mel[post]=0
    mn=np.zeros(nn); np.add.at(mn,en.ravel(),np.repeat(mel*me0/8,8)); mn+=tipm; Md=np.repeat(mn,3)
    out=[]
    for bc in 'SA':
        fr=FREE[bc]; Kf=Kg[fr][:,fr]; Mf=sp.diags(Md[fr])
        A=Kf.tocsr(); ps=pypardiso.PyPardisoSolver(); ps.factorize(A)
        OP=sla.LinearOperator(A.shape,matvec=lambda v: ps.solve(A,v),dtype=float)
        lam,V=sla.eigsh(A,k=neig,M=Mf,sigma=0,OPinv=OP,tol=1e-8); ps.free_memory(everything=True); del ps, OP; import gc; gc.collect()
        PREV[bc]=V.copy()
        for q in range(neig):
            phi=np.zeros(3*nn); phi[fr]=V[:,q]/np.sqrt(V[:,q]@(Md[fr]*V[:,q]))
            pe=phi[edof]; sk=np.einsum('ij,jk,ik->i',pe,KE,pe)
            pn=(phi.reshape(-1,3)**2).sum(1); sm=pn[en].sum(1)*me0/8
            dl=np.where(design,dk*sk-lam[q]*dm*sm,0.)
            out.append((lam[q],dl,bc))
    return out
nd=nv; x=np.full(nd,0.5)
START=int(os.environ.get('START','0'))
if START>0: x=np.load('x_%s.npy'%TAG)
xmin=np.zeros((nd,1)); xmax=np.ones((nd,1)); xold1=x[:,None].copy(); xold2=x[:,None].copy(); low=np.zeros((nd,1)); upp=np.ones((nd,1))
mcon=4; a0=1.; aa=np.zeros((mcon,1)); cc=1e4*np.ones((mcon,1)); dd=np.zeros((mcon,1))
hist=[]; t0=time.time(); beta=1.
sched={0:1,30:2,60:4,90:8,120:16}
for it in range(START,ITERS):
    beta=[v for k,v in sorted(sched.items()) if k<=it][-1]
    xt=np.asarray(Hf@x).ravel()/Hs; xb=proj(xt,beta); ETAE=float(os.environ.get('ETAE','0.5')); xe=proj(xt,beta,ETAE)
    rb=np.zeros(len(ei)); rb[didx]=P_@xb; re_=np.zeros(len(ei)); re_[didx]=P_@xe
    res=analyse(re_)
    vol=(P_@xb).mean(); dvol=np.asarray(P_.T@np.ones(len(didx))).ravel()/len(didx)
    chain=lambda g: np.asarray(Hf.T@(g*dproj(xt,beta)/Hs)).ravel()
    f0=vol; df0=chain(dvol)
    fval=np.array([1-r[0]/LT for r in res]); dfdx=np.array([np.asarray(Hf.T@((np.asarray(P_.T@(-r[1][didx]/LT)).ravel())*dproj(xt,beta,ETAE)/Hs)).ravel() for r in res])
    xn,_,_,_,_,_,_,_,_,low,upp=mmapy.mmasub(mcon,nd,it+1-START,x[:,None],xmin,xmax,xold1,xold2,f0,df0[:,None],fval[:,None],dfdx,low,upp,a0,aa,cc,dd,move=0.1)
    xold2=xold1.copy(); xold1=x[:,None].copy(); x=xn.ravel()
    fr=[float(np.sqrt(r[0])/2/np.pi) for r in res]
    massg=((P_@xb).sum()*me0*2+ (solid.sum())*me0*2)*1e6
    hist.append(dict(it=it,beta=beta,vol=round(float(vol),4),mass_g=round(float(massg),1),f=[round(v,1) for v in fr],t=round(time.time()-t0),rss=__import__("resource").getrusage(__import__("resource").RUSAGE_SELF).ru_maxrss//1024))
    print(json.dumps(hist[-1]),flush=True)
    if it%10==0 or it==ITERS-1:
        np.save('x_%s.npy'%TAG,x); np.save('xb_%s.npy'%TAG,rb)
    if it%5==0: 
        snap=np.zeros(len(ei),np.float32); snap[didx]=P_@xb; 
        with open('snaps_%s.bin'%TAG,'ab') as fo: fo.write((np.clip(snap,0,1)*255).astype(np.uint8).tobytes())
json.dump(hist,open('hist_%s_%d.json'%(TAG,START),'w'))
