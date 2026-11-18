# Central pedestal: fixed neck, base plate pockets optimised (through-thickness extrusion), half model in x with sym/antisym BCs
import numpy as np, scipy.sparse as sp, json, os, time, gc, mmapy, pypardiso
from fem3d import hex8_KB
from scipy.spatial import cKDTree
E,nu,rho=68900.,0.33,2.7e-9; h=float(os.environ.get('H','2.5'))
BX,BY,BT=200.,150.,10.                  # base half-width x, half-depth y, thickness
NKX,NKY,ZN=60.,15.,80.                  # neck half-width x, half-depth y, top z (TV bottom)
MT=20.8; g=9.81; W=MT*g; F13=0.13*(MT+3.0)*g; ZT=ZN+832.
SAG=float(os.environ.get('SAG','0.1')); UTOP=float(os.environ.get('UTOP','1.0')); ITERS=int(os.environ.get('ITERS','150')); TAG=os.environ.get('TAG','p')
nx,ny,nz=int(BX/h),int(2*BY/h),int((ZN+20)/h)
KE,C,B0,xi=hex8_KB(E,nu,h)
ei=np.array([[i,j,k] for k in range(nz) for j in range(ny) for i in range(nx)]); I,J,K=ei.T
xc=h*(I+.5); yc=-BY+h*(J+.5); zc=h*(K+.5)
base=zc<BT
pads=base&(xc>=BX-30)&(np.abs(yc)>=BY-30)
neck=(zc>=BT)&(zc<ZN)&(xc<NKX)&(np.abs(yc)<NKY)
under=base&(xc<NKX+10)&(np.abs(yc)<NKY+10)           # base under neck kept solid
tvb=(zc>=ZN)&(xc<150)&(np.abs(yc)<NKY)                # rigid TV bottom block
active=base|neck|tvb
solid=(pads|under|neck)&active; design=base&~(pads|under)
NX,NY,NZ=nx+1,ny+1,nz+1; nid=lambda i,j,k:(k*NY+j)*NX+i; cor=((xi+1)/2).astype(int)
en=np.stack([nid(I+c[0],J+c[1],K+c[2]) for c in cor],1); edof=np.stack([3*en,3*en+1,3*en+2],2).reshape(len(ei),24)
nn=NX*NY*NZ; gi=np.arange(nn)%NX; gj=(np.arange(nn)//NX)%NY; gk=np.arange(nn)//(NX*NY); nxc=h*gi; nyc=-BY+h*gj; nzc=h*gk
used=np.zeros(nn,bool); used[en[active].ravel()]=True
padn=np.unique(en[pads][:,:4].ravel()); padn=padn[nzc[padn]==0]
plane=np.where(used&(gi==0))[0]
tvn=np.unique(en[tvb].ravel()); w=np.where(nxc[tvn]==0,0.5,1.0); w/=w.sum()
def dist(Ft,M,coord): d=coord-coord@w; a=M/((w*d**2).sum()); return w*Ft+w*a*d
Fl=np.zeros((3*nn,3))
Fl[3*tvn+2,0]=-w*W/2
Fl[3*tvn+1,1]=F13/2*w; Fl[3*tvn+2,1]+=-dist(0,F13/2*(ZT-ZN),nyc[tvn])     # FB push: shear + overturning about x (vertical couple in y)
Fl[3*tvn+0,2]=F13/2*w; Fl[3*tvn+2,2]+=-dist(0,F13/2*(ZT-ZN),nxc[tvn])     # lateral push (antisym): shear + couple in x
def freeset(bc):
    fd=[3*padn,3*padn+1,3*padn+2]; fd.append(3*plane if bc=='S' else np.r_[3*plane+1,3*plane+2])
    return np.setdiff1d(np.where(np.repeat(used,3))[0],np.unique(np.concatenate(fd)))
FREE={'S':freeset('S'),'A':freeset('A')}
ea=edof[active].astype(np.int32); iK=np.repeat(ea,24,1).ravel(); jK=np.tile(ea,(1,24)).ravel()
# top displacement measures
def meas(U):
    s=-(U[3*tvn+2,0]@w)
    def tip(u,coordv,hor):  # horizontal translation + rotation*(ZT-ZN)
        d=coordv-coordv@w; th=-((u[3*tvn+2]*w*d).sum()/((w*d**2).sum())); return u[3*tvn+hor]@w+th*(ZT-ZN)
    return s, tip(U[:,1],nyc[tvn],1), tip(U[:,2],nxc[tvn],0)
LIM=[W/2*SAG, F13/2*UTOP, F13/2*UTOP]
# design variables = columns (i,j) through base thickness
dI=I[design]; dJ=J[design]; col=dI*ny+dJ; ucol,inv=np.unique(col,return_inverse=True); nv=len(ucol)
cxy=np.c_[h*(ucol//ny+.5),-BY+h*(ucol%ny+.5)]; R=float(os.environ.get('RF','7.5'))
tr=cKDTree(cxy); pr=tr.query_pairs(R,output_type='ndarray'); a=np.r_[np.arange(nv),pr[:,0],pr[:,1]]; b=np.r_[np.arange(nv),pr[:,1],pr[:,0]]; ww=R-np.linalg.norm(cxy[a]-cxy[b],axis=1)
m2=cxy.copy(); m2[:,0]=-m2[:,0]; D=tr.sparse_distance_matrix(cKDTree(m2),R,output_type='coo_matrix')
Hf=sp.coo_matrix((np.r_[ww,R-D.data],(np.r_[a,D.row],np.r_[b,D.col])),shape=(nv,nv)).tocsr(); Hs=np.asarray(Hf.sum(1)).ravel()
P_=sp.csr_matrix((np.ones(len(inv)),(np.arange(len(inv)),inv)),shape=(len(inv),nv))   # column var -> design voxels
proj=lambda x,be,et=.5:(np.tanh(be*et)+np.tanh(be*(x-et)))/(np.tanh(be*et)+np.tanh(be*(1-et)))
dproj=lambda x,be,et=.5:be*(1-np.tanh(be*(x-et))**2)/(np.tanh(be*et)+np.tanh(be*(1-et)))
didx=np.where(design)[0]; EMIN=1e-6; P=3.
def analyse(rb):
    k=np.where(tvb,100.,rb); k=EMIN+(1-EMIN)*k**P if False else np.where(tvb,100.,EMIN+(1-EMIN)*rb**P)
    Kg=sp.csr_matrix(((KE.ravel()[None,:]*k[active][:,None]).ravel(),(iK,jK)),shape=(3*nn,3*nn))
    U=np.zeros((3*nn,3))
    for bc,cols in (('S',[0,1]),('A',[2])):
        fr=FREE[bc]; A=Kg[fr][:,fr].tocsr(); ps=pypardiso.PyPardisoSolver(); ps.factorize(A)
        for c in cols: U[fr,c]=ps.solve(A,Fl[fr,c])
        ps.free_memory(everything=True); del ps; gc.collect()
    return U,k
x=np.full(nv,0.5); xold1=x[:,None].copy(); xold2=x[:,None].copy(); low=np.zeros((nv,1)); upp=np.ones((nv,1))
S_=int(os.environ.get('STG','30')); sched={0:1,S_:2,2*S_:4,3*S_:8,4*S_:16}; t0=time.time(); ETAE=float(os.environ.get('ETAE','0.55'))
BASEMODE=os.environ.get('BASE')=='1'
for it in range(ITERS):
    be=[v for kk,v in sorted(sched.items()) if kk<=it][-1]
    xt=np.asarray(Hf@x).ravel()/Hs; xb=proj(xt,be); xe=proj(xt,be,ETAE)
    if BASEMODE: xb=np.ones(nv); xe=xb
    rb=np.zeros(len(ei)); rb[solid]=1; rb[didx]=P_@xe
    U,k=analyse(rb)
    f0=xb.sum()/nv; df0=np.asarray(Hf.T@(dproj(xt,be)/nv/Hs)).ravel()
    fv=[];dd=[]
    for c in range(3):
        u=U[:,c]; comp=Fl[:,c]@u; ue=u[edof[didx]]; ce=np.einsum('ij,jk,ik->i',ue,KE,ue); dc=-P*(1-EMIN)*rb[didx]**(P-1)*ce
        dcv=P_.T@dc; fv.append(comp/LIM[c]-1); dd.append(np.asarray(Hf.T@(dcv/LIM[c]*dproj(xt,be,ETAE)/Hs)).ravel())
    s,uf,ul=meas(U); mass=2*(rb[active&~tvb].sum())*h**3*rho*1e3
    if it%10==0: np.save('ped_x_%s.npy'%TAG,x)
    if it%10==0 or it==ITERS-1 or BASEMODE: print(json.dumps(dict(it=it,beta=be,mass_kg=round(mass,3),sag=round(s,4),utop_fb=round(uf,3),utop_lat=round(ul,3),t=round(time.time()-t0))),flush=True)
    if BASEMODE: break
    xn,_,_,_,_,_,_,_,_,low,upp=mmapy.mmasub(3,nv,it+1,x[:,None],np.zeros((nv,1)),np.ones((nv,1)),xold1,xold2,f0,df0[:,None],np.array(fv)[:,None],np.array(dd),low,upp,1.,np.zeros((3,1)),1e4*np.ones((3,1)),np.zeros((3,1)),move=0.1)
    xold2=xold1.copy(); xold1=x[:,None].copy(); x=xn.ravel()
np.save('ped_x_%s.npy'%TAG,x); np.save('ped_cols_%s.npy'%TAG,np.c_[ucol,xb])
