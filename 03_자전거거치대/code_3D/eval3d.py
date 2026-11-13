import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla, json, sys, pypardiso
from scipy import ndimage
from fem3d import hex8_KB
E,nu,rho=1700.,0.38,1.27e-9; MP=0.25e-3; g=9810.; h=2.; PEAK=48.5
x0,y0,z0=-24.,35.,-36.; nx,ny,nz=62,20,39
KE,C,B0,xi=hex8_KB(E,nu,h)
ei=np.array([[i,j,k] for k in range(nz) for j in range(ny) for i in range(nx)]); I,J,K=ei.T
xc=x0+2*I+1; yc=y0+2*J+1; zc=z0+2*K+1; rr=np.sqrt(xc**2+zc**2); ay=np.abs(yc-55)
bore=rr<16.1; contact=(rr>=16.1)&(rr<20.6)&(ay<10); slit=(np.abs(xc)<=1)&(zc<0)&(rr<26)
ears=(np.abs(xc)>1)&(np.abs(xc)<9)&(zc>-34)&(zc<-14)&(ay<10)
pad=(xc>80)&(xc<100)&(zc>16)&(zc<20)&(ay<10); post=(xc>86)&(xc<96)&(zc>20)&(ay<6)
holder=(xc>78)&(zc>20)&~post; above=(zc>24)&~post
void=bore|slit|holder|above; solid=(contact|ears|pad)&~void; design=~(void|solid|post)
def full_from_half(rb_half):
    # half grid: ny=10 j=0..9 corresponds y 55..75 ; full j=10..19 same, j=0..9 mirrored
    hh=rb_half.reshape(nz,10,nx); f=np.concatenate([hh[:,::-1,:],hh],axis=1); return f.ravel()
def clean(sd):
    v=(sd|solid|post).reshape(nz,ny,nx); lab,n=ndimage.label(v)
    seed=(contact|post).reshape(nz,ny,nx); keep=np.unique(lab[seed&v]); keep=keep[keep>0]
    return np.isin(lab,keep).ravel()&design
NX,NY,NZ=nx+1,ny+1,nz+1; nid=lambda i,j,k:(k*NY+j)*NX+i; corner=((xi+1)/2).astype(int)
en=np.stack([nid(I+c[0],J+c[1],K+c[2]) for c in corner],1); edof=np.stack([3*en,3*en+1,3*en+2],2).reshape(len(ei),24)
nn=NX*NY*NZ; gi=np.arange(nn)%NX; gj=(np.arange(nn)//NX)%NY; gk=np.arange(nn)//(NX*NY); nxc=x0+2*gi; nyc=y0+2*gj; nzc=z0+2*gk
def evaluate(sd):
    on=sd|solid|post; ke=np.where(post,20.,1.)*on
    used=np.zeros(nn,bool); used[en[on].ravel()]=True
    fixn=np.where(used&(np.sqrt(nxc**2+nzc**2)<=16.7))[0]
    topn=np.where(used&(gk==nz)&(nxc>=86)&(nxc<=96)&(np.abs(nyc-55)<=6))[0]
    fd=np.r_[3*fixn,3*fixn+1,3*fixn+2]; fr=np.setdiff1d(np.where(np.repeat(used,3))[0],fd)
    idx=np.where(on)[0]
    Kg=sp.coo_matrix(((KE.ravel()[None,:]*ke[idx][:,None]).ravel(),(np.repeat(edof[idx],24,1).ravel(),np.tile(edof[idx],(1,24)).ravel())),shape=(3*nn,3*nn)).tocsr()
    mn=np.zeros(nn); np.add.at(mn,en[on&~post].ravel(),rho*h**3/8); mn[topn]+=MP/len(topn)
    A=Kg[fr][:,fr].tocsr(); ps=pypardiso.PyPardisoSolver(); ps.factorize(A)
    OP=sla.LinearOperator(A.shape,matvec=lambda v: ps.solve(A,v),dtype=float)
    w,V=sla.eigsh(A,k=3,M=sp.diags(np.repeat(mn,3)[fr]),sigma=0,OPinv=OP)
    F=np.zeros((3*nn,2)); F[3*topn+2,0]=-MP*PEAK*g/len(topn); F[3*topn+1,1]=MP*PEAK*g/len(topn)
    U=np.zeros((3*nn,2)); U[fr,0]=ps.solve(A,F[fr,0]); U[fr,1]=ps.solve(A,F[fr,1])
    vms=[];syy=[]
    for c in (0,1):
        ue=U[:,c][edof]; s=(C@B0@ue.T).T
        vm=np.sqrt(0.5*((s[:,0]-s[:,1])**2+(s[:,1]-s[:,2])**2+(s[:,2]-s[:,0])**2)+3*(s[:,3:]**2).sum(1)); vm[~(on&~post)]=0; vm[rr<19]=0; vms.append(vm)
    modes=[]
    for q in range(3):
        v=np.zeros(3*nn); v[fr]=V[:,q]; modes.append(v)
    massg=float((on&~post).sum()*rho*h**3*1e6)
    return dict(mass=massg,f=[float(x) for x in np.sqrt(w)/2/np.pi],vmz=float(vms[0].max()),vmy=float(vms[1].max()),
                tipz=float(-U[3*topn+2,0].mean()),tipy=float(U[3*topn+1,1].mean())),dict(U=U,vm=vms,modes=modes,on=on,topn=topn)
if __name__=='__main__':
    rb=np.load(sys.argv[1]); f=full_from_half(rb); sd=clean(f>0.5); np.save(sys.argv[1].replace('.npy','_full.npy'),sd)
    r,_=evaluate(sd); print(json.dumps(r))
