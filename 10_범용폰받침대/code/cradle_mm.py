# 받침대 뒷판 구조 + 열 동시 위상 최적화 (복합물리)
# 좌표: x 폰 가로(0..80), y 폰 세로(0..150), z 두께. 단위 mm, N, W
import numpy as np, scipy.sparse as sp, json, os, time, sys, mmapy, pypardiso
from scipy.spatial import cKDTree
from fem3d import hex8_KB
from thermal3d import hex8_cond, quad_mass, FACES
h=2.; nx,ny=40,75; NP=3                        # PETG 설계층 3층(6 mm)
AL=True               # 알루미늄 판(0.5 mm, 등가 2 mm 층) 유무
NA=1 if AL else 0; NPH=4                       # 폰 4층(8 mm)
nz=NP+NA+NPH
MODE=os.environ.get('MODE','opt')              # opt | flat
TAG=os.environ.get('TAG','x'); ITERS=int(os.environ.get('ITERS','120'))
# 재료 (W/mm·K, MPa)
K_PETG=0.2e-3; K_AIR=0.026e-3*0+1e-6; K_PH=15e-3; K_AL=167e-3*0.25
E_PETG=1700.; E_PH=70000.; nu=0.38
H_RIDE=float(os.environ.get('HRIDE','23'))*1e-6; H_FRONT=float(os.environ.get('HFRONT','11'))*1e-6
Q=4.0                                          # W
ei=np.array([[i,j,k] for k in range(nz) for j in range(ny) for i in range(nx)]); I,J,K=ei.T
xc=h*I+1; yc=h*J+1
petg=K<NP; al=(K>=NP)&(K<NP+NA); ph=K>=NP+NA
hub=petg&((xc-40)**2+(yc-75)**2<=16**2)
corner=petg&(((xc<10)|(xc>70))&((yc<10)|(yc>140)))
fixed_solid=hub|corner
design=petg&~fixed_solid
aldes=al
top=petg&(K==NP-1); bot=petg&(K==0)
src=ph&(K==NP+NA)&(xc>30)&(xc<50)&(yc>100)&(yc<125)
NX,NY,NZ=nx+1,ny+1,nz+1; nid=lambda i,j,k:(k*NY+j)*NX+i
KE,C,B0,xi=hex8_KB(1.,nu,h); corner_=((xi+1)/2).astype(int)
en=np.stack([nid(I+c[0],J+c[1],K+c[2]) for c in corner_],1); nn=NX*NY*NZ
edof=np.stack([3*en,3*en+1,3*en+2],2).reshape(len(ei),24)
KT=hex8_cond(1.,h); MF=quad_mass(h)
ftop=np.array(FACES[(0,0,1)]); fbot=np.array(FACES[(0,0,-1)])
# 폰 앞면 대류 (고정)
front=ph&(K==nz-1)
# 하중: 폰은 모서리 걸림 턱이 잡음 → 충격 시 폰 관성(0.29 kg × 48.5 g = 138 N)이 네 모서리로 들어옴
#   LC1: 폰이 떨어져 나가는 방향(+z), LC2: 폰 세로 방향(+y). 두 경우 합 컴플라이언스로 강성 판정
ce_=np.where(corner&(K==NP-1))[0]; cn=np.unique(en[ce_][:,ftop].ravel())
F1=np.zeros(3*nn); F1[3*cn+2]=138./len(cn); F2=np.zeros(3*nn); F2[3*cn+1]=138./len(cn)
gk=np.arange(nn)//(NX*NY); gi=np.arange(nn)%NX; gj=(np.arange(nn)//NX)%NY
fixn=np.where((gk==0)&(((h*gi-40)**2+(h*gj-75)**2)<=16**2))[0]
fdofs=np.r_[3*fixn,3*fixn+1,3*fixn+2]
# 구조에 쓰는 요소: PETG + 폰 (알루미늄은 보수적으로 제외)
struct=petg
free=np.setdiff1d(np.unique(edof[struct].ravel()),fdofs)
iK=np.repeat(edof,24,1).ravel(); jK=np.tile(edof,(1,24)).ravel()
iT=np.repeat(en,8,1).ravel(); jT=np.tile(en,(1,8)).ravel()
def dens(xd,xa):
    rho=np.zeros(len(ei)); rho[fixed_solid]=1.; rho[design]=xd; rho[aldes]=xa; return rho
P=3.; EMIN=1e-6
def solve(rho):
    # 구조
    Ee=np.where(petg,EMIN*E_PETG+rho**P*(E_PETG-EMIN*E_PETG),0.)
    Ks=sp.coo_matrix(((KE.ravel()[None,:]*Ee[:,None]).ravel(),(iK,jK)),shape=(3*nn,3*nn)).tocsr()
    A=Ks[free][:,free]; u=np.zeros((3*nn,2)); ps=pypardiso.PyPardisoSolver(); u[free]=ps.solve(A,np.c_[F1[free],F2[free]]); ps.free_memory(everything=True)
    # 열
    ke=np.where(ph,K_PH,np.where(al,K_AIR+rho**P*(K_AL-K_AIR),K_AIR+rho**P*(K_PETG-K_AIR)))
    Kt=sp.coo_matrix(((KT.ravel()[None,:]*ke[:,None]).ravel(),(iT,jT)),shape=(nn,nn)).tolil()
    rows=[];cols=[];vals=[]
    def face(e_idx,fl,hv):
        nodes=en[e_idx][:,fl]
        for a in range(4):
            for b in range(4): rows.append(nodes[:,a]); cols.append(nodes[:,b]); vals.append(hv*MF[a,b])
    tt=np.where(top)[0]; bb=np.where(bot)[0]; ff=np.where(front)[0]; aa=ABOVE[tt]
    rt=rho[tt]; ra=rho[aa]
    face(aa,fbot,H_RIDE*ra*(1-rt))          # 알루미늄이 드러난 곳
    face(aa,ftop,H_RIDE*(1-ra)*(1-rt))      # 알루미늄도 PETG도 없는 곳 = 폰 뒷면이 드러남
    face(bb,fbot,H_RIDE*rho[bb]); face(ff,ftop,np.full(len(ff),H_FRONT))
    Kc=sp.coo_matrix((np.concatenate(vals),(np.concatenate(rows),np.concatenate(cols))),shape=(nn,nn))
    Kt=(Kt.tocsr()+Kc).tocsr()
    q=np.zeros(nn); se=np.where(src)[0]; np.add.at(q,en[se].ravel(),Q/len(se)/8)
    used=np.unique(en.ravel()); ps2=pypardiso.PyPardisoSolver(); T=np.zeros(nn); T[used]=ps2.solve(Kt[used][:,used],q[used])
    return u,T,Kt,used,ps2,Ee,ke
phn=np.unique(en[ph].ravel()); PN=8.
ABOVE=np.arange(len(ei))+nx*ny   # PETG 윗층 요소 바로 위 = 알루미늄 층 요소
def evaluate(xd,xa):
    rho=dens(xd,xa); u,T,Kt,used,ps2,Ee,ke=solve(rho)
    Cc=float(F1@u[:,0]+F2@u[:,1]); Tm=T[phn]; Jp=float(np.sum(Tm**PN)**(1/PN))
    return rho,u,T,Kt,used,ps2,Cc,Jp
didx=np.where(design)[0]; nd=len(didx); aidx=np.where(aldes)[0]; na=len(aidx)
all_=np.r_[didx,aidx]; pos=np.c_[xc[all_],yc[all_],h*K[all_]+1+1000*np.r_[np.zeros(nd),np.ones(na)]]; R=float(os.environ.get('RF','4.5'))
tr=cKDTree(pos); pr=tr.query_pairs(R,output_type='ndarray'); a=np.r_[np.arange(nd),pr[:,0],pr[:,1]]; b=np.r_[np.arange(nd),pr[:,1],pr[:,0]]
NV=nd+na
Hf=sp.coo_matrix((R-np.linalg.norm(pos[a]-pos[b],axis=1),(a,b)),shape=(NV,NV)).tocsr(); Hs=np.asarray(Hf.sum(1)).ravel()
proj=lambda x,be,et=.5:(np.tanh(be*et)+np.tanh(be*(x-et)))/(np.tanh(be*et)+np.tanh(be*(1-et)))
dproj=lambda x,be,et=.5:be*(1-np.tanh(be*(x-et))**2)/(np.tanh(be*et)+np.tanh(be*(1-et)))
MAL=h**3*0.25*2.7e-3
mass=lambda rho: float(rho[petg].sum()*h**3*1.27e-3+rho[al].sum()*MAL)
def report(rho,Cc,T,tag):
    r=dict(tag=tag,al_g=round(float(rho[al].sum()*MAL),1),mass_g=round(mass(rho),1),C=round(Cc,2),defl_mm=round(Cc/276.,3),Tmax=round(float(T[phn].max()),2),Tsrc=round(float(T[np.unique(en[src].ravel())].mean()),2),Tback=round(float(T[np.unique(en[ph&(K==NP+NA)][:,fbot].ravel())].mean()),2))
    print(json.dumps(r),flush=True); return r
if MODE=='eval':
    rr=np.load(os.environ['RHO']); rho,u,T,Kt,used,ps2,Cc,Jp=evaluate(rr[didx],rr[aidx]); r=report(rho,Cc,T,'eval'); np.save('T_%s.npy'%TAG,T); np.save('rho_%s.npy'%TAG,rho); json.dump(r,open('res_%s.json'%TAG,'w')); sys.exit()
CMAX=float(os.environ.get('CMAX','1e9')); MMAX=float(os.environ['MMAX']); OBJ=os.environ.get('OBJ','T')
mfix=float(fixed_solid.sum()*h**3*1.27e-3); me=h**3*1.27e-3
x=np.r_[np.full(nd,0.3),np.full(na,0.2)]; xo1=x[:,None].copy(); xo2=x[:,None].copy(); low=np.zeros((NV,1)); upp=np.ones((NV,1))
sched={0:1,30:2,55:4,80:8,100:16}; t0=time.time(); J0=None
tt=np.where(top)[0]; bb=np.where(bot)[0]
loc={e:i for i,e in enumerate(didx)}
for it in range(ITERS):
    be=[v for kk,v in sorted(sched.items()) if kk<=it][-1]
    xt=np.asarray(Hf@x).ravel()/Hs; xb=proj(xt,be)
    rho,u,T,Kt,used,ps2,Cc,Jp=evaluate(xb[:nd],xb[nd:])
    # 열 민감도 (adjoint)
    g=np.zeros(nn); Tm=T[phn]; g[phn]=np.sum(Tm**PN)**(1/PN-1)*Tm**(PN-1)
    lam=np.zeros(nn); lam[used]=ps2.solve(Kt[used][:,used],g[used]); ps2.free_memory(everything=True)
    e=didx; xd_=xb[:nd]; xa_=xb[nd:]
    dke=P*np.maximum(xd_,1e-9)**(P-1)*(K_PETG-K_AIR)
    dJd=-dke*np.einsum('ij,jk,ik->i',lam[en[e]],KT,T[en[e]])
    def fq(idx,fl): return np.einsum('ij,jk,ik->i',lam[en[idx]][:,fl],MF,T[en[idx]][:,fl])
    isb=np.isin(e,bb); dJd+=np.where(isb,-H_RIDE*fq(e,fbot),0.)
    # PETG 윗층: 알루미늄 노출/폰 노출 항 둘 다 (1-ρt) 비례
    ist=np.isin(e,tt); ab=ABOVE[e]; ra_=rho[ab]
    dJd+=np.where(ist, H_RIDE*(ra_*fq(ab,fbot)+(1-ra_)*fq(ab,ftop)),0.)
    # 알루미늄 변수
    ea=aidx; dka=P*np.maximum(xa_,1e-9)**(P-1)*(K_AL-K_AIR)
    dJa=-dka*np.einsum('ij,jk,ik->i',lam[en[ea]],KT,T[en[ea]])
    rt_=rho[ea-nx*ny]
    dJa+=-H_RIDE*(1-rt_)*fq(ea,fbot)+H_RIDE*(1-rt_)*fq(ea,ftop)
    dJ=np.r_[dJd,dJa]
    # 구조 민감도
    dC=np.r_[-P*np.maximum(xb[:nd],1e-9)**(P-1)*(E_PETG*(1-EMIN))*sum(np.einsum('ij,jk,ik->i',u[edof[e],c],KE,u[edof[e],c]) for c in (0,1)),np.zeros(na)]
    if os.environ.get('FD'):
        rng=np.random.default_rng(0); picks=list(rng.choice(np.where(np.isin(didx,tt))[0],3))+list(nd+rng.choice(na,3))+list(rng.choice(np.where(np.isin(didx,bb))[0],2))
        for q in picks:
            ep=1e-4; x2=xb.copy(); x2[q]+=ep; J2=evaluate(x2[:nd],x2[nd:])[7]; x3=xb.copy(); x3[q]-=ep; J3=evaluate(x3[:nd],x3[nd:])[7]
            print(q, 'fd %.6e adj %.6e'%((J2-J3)/(2*ep), dJ[q]))
        sys.exit()
    if OBJ=='C':
        if J0 is None: J0=Cc
        f0=Cc/J0; df0=np.asarray(Hf.T@(dC/J0*dproj(xt,be)/Hs)).ravel()
    else:
        if J0 is None: J0=Jp
        f0=Jp/J0; df0=np.asarray(Hf.T@(dJ/J0*dproj(xt,be)/Hs)).ravel()
    mval=mfix+xb[:nd].sum()*me+xb[nd:].sum()*MAL
    fval=np.array([Cc/CMAX-1, mval/MMAX-1])
    dfdx=np.vstack([np.asarray(Hf.T@(dC/CMAX*dproj(xt,be)/Hs)).ravel(), np.asarray(Hf.T@(np.r_[np.full(nd,me/MMAX),np.full(na,MAL/MMAX)]*dproj(xt,be)/Hs)).ravel()])
    xn,_,_,_,_,_,_,_,_,low,upp=mmapy.mmasub(2,NV,it+1,x[:,None],np.zeros((NV,1)),np.ones((NV,1)),xo1,xo2,f0,df0[:,None],fval[:,None],dfdx,low,upp,1.,np.zeros((2,1)),1e4*np.ones((2,1)),np.zeros((2,1)),move=0.1)
    xo2=xo1.copy(); xo1=x[:,None].copy(); x=xn.ravel()
    if it%5==0 or it==ITERS-1:
        print(json.dumps(dict(it=it,beta=be,mass=round(mval,1),al=round(float(xb[nd:].sum()*MAL),1),C=round(Cc,2),Tmax=round(float(T[phn].max()),2),t=round(time.time()-t0))),flush=True)
    if it%20==0 or it==ITERS-1: np.save('snap_%s_%03d.npy'%(TAG,it),rho)
# 최종: 0/1 형상으로 재평가
xd=(xb>0.5).astype(float); rho,u,T,Kt,used,ps2,Cc,Jp=evaluate(xd[:nd],xd[nd:])
np.save('T_%s.npy'%TAG,T); r=report(rho,Cc,T,'opt_bin')
json.dump(r,open('res_%s.json'%TAG,'w')); np.save('rho_%s.npy'%TAG,rho)
