# TV stand foot = aluminium plate (laser/CNC cut), 2D plane-stress topology optimisation, Q4, 1 mm grid
import numpy as np, scipy.sparse as sp, json, os, time, mmapy, pypardiso
E,nu,t=68900.,0.33,float(os.environ.get('T','10')); rho=2.7e-9; h=float(os.environ.get('H','1.0'))
LY,LZ=300.,120.; ny,nz=int(LY/h),int(LZ/h)       # y: depth (front -150 .. back +150), z: height
g=9.81; MT=20.8; W=MT*g; F13=0.13*(MT+2*0.6)*g   # N ; stand mass assumed 1.2 kg total (2 feet)
ZB=LZ; ZC=ZB+416.; ZT=ZB+832.                    # TV bottom on top of foot; CG & top heights above table (mm)
SPAN=1200.                                       # foot spacing along TV width (assumed, 65" TV ~1450 mm wide)
SAG=float(os.environ.get('SAG','0.10')); UTOP=float(os.environ.get('UTOP','1.0')); ITERS=int(os.environ.get('ITERS','200')); TAG=os.environ.get('TAG','a')
# element stiffness Q4 plane stress
def q4():
    k=np.array([1/2-nu/6,1/8+nu/8,-1/4-nu/12,-1/8+3*nu/8,-1/4+nu/12,-1/8-nu/8,nu/6,1/8-3*nu/8])
    KE=E*t/(1-nu**2)*np.array([[k[0],k[1],k[2],k[3],k[4],k[5],k[6],k[7]],[k[1],k[0],k[7],k[6],k[5],k[4],k[3],k[2]],[k[2],k[7],k[0],k[5],k[6],k[3],k[4],k[1]],[k[3],k[6],k[5],k[0],k[7],k[2],k[1],k[4]],[k[4],k[5],k[6],k[7],k[0],k[1],k[2],k[3]],[k[5],k[4],k[3],k[2],k[1],k[0],k[7],k[6]],[k[6],k[3],k[4],k[1],k[2],k[7],k[0],k[5]],[k[7],k[2],k[1],k[4],k[3],k[6],k[5],k[0]]])
    return KE
KE=q4()
nel=ny*nz; J,K=np.meshgrid(np.arange(ny),np.arange(nz)); J=J.ravel(); K=K.ravel()
yc=-LY/2+h*(J+.5); zc=h*(K+.5)
nid=lambda j,k:k*(ny+1)+j
n1=nid(J,K); n2=nid(J+1,K); n3=nid(J+1,K+1); n4=nid(J,K+1)
edof=np.stack([2*n1,2*n1+1,2*n2,2*n2+1,2*n3,2*n3+1,2*n4,2*n4+1],1)
nn=(ny+1)*(nz+1); ndof=2*nn; NY=-LY/2+h*(np.arange(nn)%(ny+1)); NZ=h*(np.arange(nn)//(ny+1))
iK=np.repeat(edof,8,1).ravel(); jK=np.tile(edof,(1,8)).ravel()
# regions: TV attachment block (top centre, bolted to TV bottom bracket), feet pads at both ends
attach=(np.abs(yc)<=20)&(zc>=LZ-12)
pads=(zc<=6)&(np.abs(np.abs(yc)-(LY/2-20))<=20)
solid=attach|pads; design=~solid
# BC: pad bottom nodes fixed (vertical) ; one pad also horizontal
padn=np.where((NZ==0)&(np.abs(np.abs(NY)-(LY/2-20))<=20))[0]
fix=np.r_[2*padn+1, 2*padn[NY[padn]<0]]
free=np.setdiff1d(np.arange(ndof),fix)
topn=np.where((NZ==LZ)&(np.abs(NY)<=20))[0]; w=np.ones(len(topn))/len(topn); dy=NY[topn]
def couple(Fh,M):  # horizontal force + moment (about y=0) on attach nodes -> nodal forces
    f=np.zeros(ndof); f[2*topn]+=Fh*w; a=M/((w*dy**2).sum()); f[2*topn+1]+=-a*w*dy; return f
FL=[]
f=np.zeros(ndof); f[2*topn+1]=-W/2*w; FL.append(f)                       # gravity: half TV per foot
FL.append(couple(F13/2,F13/2*(ZT-ZB)))                                   # front-back push at TV top (per foot)
f=np.zeros(ndof); f[2*topn+1]=-(W/2+F13*ZT/SPAN)*w; FL.append(f)          # lateral push -> extra vertical on leeward foot
FL=np.array(FL).T
# limits: sag at attach; top displacement from front-back push = u_attach + theta*(ZT-ZB)
def measures(U):
    sag=-(U[2*topn+1,0]@w)
    ux=U[2*topn,1]@w; th=-((U[2*topn+1,1]*w*dy).sum()/((w*dy**2).sum())); utop=ux+th*(ZT-ZB)
    sag3=-(U[2*topn+1,2]@w); return sag,utop,sag3
# compliance-based constraints (work conjugate, equal to the measures above for these load forms)
LIM=[W/2*SAG, F13/2*UTOP, (W/2+F13*ZT/SPAN)*SAG*1.5]
# filter
R=float(os.environ.get('RF','3.0'))
dpos=np.c_[yc,zc][design]; from scipy.spatial import cKDTree
tr=cKDTree(dpos); pr=tr.query_pairs(R,output_type='ndarray'); nd=len(dpos)
a=np.r_[np.arange(nd),pr[:,0],pr[:,1]]; b=np.r_[np.arange(nd),pr[:,1],pr[:,0]]; ww=R-np.linalg.norm(dpos[a]-dpos[b],axis=1)
Hf=sp.coo_matrix((ww,(a,b)),shape=(nd,nd)).tocsr(); Hs=np.asarray(Hf.sum(1)).ravel()
proj=lambda x,be,et=.5:(np.tanh(be*et)+np.tanh(be*(x-et)))/(np.tanh(be*et)+np.tanh(be*(1-et)))
dproj=lambda x,be,et=.5:be*(1-np.tanh(be*(x-et))**2)/(np.tanh(be*et)+np.tanh(be*(1-et)))
didx=np.where(design)[0]; P=3.; EMIN=1e-6
def solve(rb):
    k=EMIN+(1-EMIN)*rb**P; Kg=sp.csr_matrix(((KE.ravel()[None,:]*k[:,None]).ravel(),(iK,jK)),shape=(ndof,ndof))
    A=Kg[free][:,free]; U=np.zeros((ndof,3)); U[free]=pypardiso.spsolve(A,FL[free]); return U
x=np.full(nd,0.4); low=upp=None; xold1=x[:,None].copy(); xold2=x[:,None].copy(); low=np.zeros((nd,1)); upp=np.ones((nd,1))
m=3; S_=int(os.environ.get('STG','40')); sched={0:1,S_:2,2*S_:4,3*S_:8,4*S_:16}; t0=time.time(); ETAE=float(os.environ.get('ETAE','0.55'))
for it in range(ITERS):
    be=[v for kk,v in sorted(sched.items()) if kk<=it][-1]
    xt=np.asarray(Hf@x).ravel()/Hs; xb=proj(xt,be); xe=proj(xt,be,ETAE)
    rb=np.ones(nel); rb[didx]=xe; U=solve(rb)
    f0=xb.mean(); df0=np.asarray(Hf.T@(dproj(xt,be)/nd/Hs)).ravel()
    fval=[];dfd=[]
    for c in range(3):
        u=U[:,c]; comp=FL[:,c]@u; ue=u[edof]; ce=np.einsum('ij,jk,ik->i',ue,KE,ue)
        dc=-P*(1-EMIN)*rb[didx]**(P-1)*ce[didx]
        fval.append(comp/LIM[c]-1); dfd.append(np.asarray(Hf.T@(dc/LIM[c]*dproj(xt,be,ETAE)/Hs)).ravel())
    xn,_,_,_,_,_,_,_,_,low,upp=mmapy.mmasub(m,nd,it+1,x[:,None],np.zeros((nd,1)),np.ones((nd,1)),xold1,xold2,f0,df0[:,None],np.array(fval)[:,None],np.array(dfd),low,upp,1.,np.zeros((m,1)),1e4*np.ones((m,1)),np.zeros((m,1)),move=0.1)
    xold2=xold1.copy(); xold1=x[:,None].copy(); x=xn.ravel()
    mass=(xb.sum()+solid.sum())*h*h*t*rho*1e3
    if it%10==0 or it==ITERS-1:
        s,ut,s3=measures(U); print(json.dumps(dict(it=it,beta=be,mass_kg=round(mass,4),sag=round(s,4),utop=round(ut,3),sag_lat=round(s3,4),g=[round(v,3) for v in fval],t=round(time.time()-t0))),flush=True)
        np.save('x_%s.npy'%TAG,x)
rbn=np.ones(nel); rbn[didx]=xb; np.save('rb_%s.npy'%TAG,rbn.reshape(nz,ny))
