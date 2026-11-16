# 일체형 거치대(클램프 + 팔 + 기울인 받침판) 3D 위상 최적화 — 진동(강체 폰) + 열 + 출력(45°) 동시
# 좌표: 폰 판 기준 좌표계 (x' 폰 길이 방향, z' 판 법선). 핸들바 축 = y 이므로 판을 TILT만큼 기울여도 핸들바는 원 그대로.
#   세계 좌표: X(앞) = x' cos t - z' sin t,  Z(위) = x' sin t + z' cos t
# 절반 모델 (y ≥ 0, y=0 대칭면 uy=0) → 대칭 모드(위아래 · 앞뒤 · 핸들바축 회전)만 계산
# 출력 방향: 폰 닿는 판 윗면을 바닥에 두고 (-z' 방향으로 쌓음)
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla, time, json, os, gc, sys
from scipy.spatial import cKDTree
import mmapy, pypardiso
from fem3d import hex8_KB
from thermal3d import hex8_cond, quad_mass, FACES
env=os.environ.get
E,nu,rho=1700.,0.38,1.27e-9; h=2.
TILT=np.radians(float(env('TILT','35'))); ct,st=np.cos(TILT),np.sin(TILT)
FT=float(env('FT','95')); LT=(2*np.pi*FT)**2; TLIM=float(env('TLIM','22'))
ITERS=int(env('ITERS','160')); AMF=env('AM','1')=='1'; TAG=env('TAG','int'); MODE=env('MODE','opt')
XR=float(env('XR','-10')); PL=150.; ZB=24.                     # 판: x' ∈ [XR, XR+150], z' ∈ [24, 30], 폰 z' ∈ [30, 38]
x0,y0,z0=-24.,0.,-36.; nx,ny,nz=int(env('NX','83')),20,37
KE,C,B0,xi=hex8_KB(E,nu,h)
ei=np.array([[i,j,k] for k in range(nz) for j in range(ny) for i in range(nx)]); I,J,K=ei.T
xc=x0+2*I+1; yc=y0+2*J+1; zc=z0+2*K+1
Xw=xc*ct-zc*st; Zw=xc*st+zc*ct; rr=np.sqrt(xc**2+zc**2)      # 회전은 핸들바 축 기준이라 rr 동일
bore=rr<16.1; contact=(rr>=16.1)&(rr<20.6)&(yc<10)
slit=(np.abs(Xw)<=1)&(Zw<0)&(rr<26); ears=(np.abs(Xw)>1)&(np.abs(Xw)<9)&(Zw>-34)&(Zw<-14)&(yc<10)
foot=(xc>XR)&(xc<XR+PL); xl=xc-XR                              # xl: 판 아래 끝(받침 턱)에서 잰 길이
plate=foot&(zc>ZB)&(zc<ZB+6); phone=foot&(zc>ZB+6)&(zc<ZB+14)
jaw=plate&(yc>32)&(xl>62)&(xl<88); ledge=plate&(xl<8)&(yc<16); band=plate&(zc<ZB+4)&(xl>66)&(xl<84)
toppad=plate&(xl>136)&(yc<16)                                 # 폰 위쪽 끝 뒷면 받침점(고정)
GRIP=env('GRIP','0'); GRIP2=GRIP=='2'; GRIP=GRIP in('1','2')
if GRIP:   # 제작형: 레일 하우징(스프링 집게 2개가 끼워짐) + 하단 걸이 기둥 — cad/parts.py 와 같은 치수
    hous=(xc>55)&(xc<75)&(zc>18)&(zc<30)
    chan=(xc>60)&(xc<70)&(zc>20)&(zc<28)&(yc>5); slot=(xc>63)&(xc<67)&(zc>27)&(zc<30)&(yc>26)
    hook=(xc>-14)&(xc<-10)&(yc<15)&(zc>ZB)
    jaw=hous&~chan&~slot
    void=bore|slit|phone|(((zc>ZB)&~plate)&~hook)|chan|slot
    solid=(contact|ears|jaw|ledge|band|toppad|hook)&~void
    if GRIP2:   # v2: 위쪽 슬라이드 걸이 레일 (cad/parts.py HT)
        rail=(xc>102)&(xc<150)&(yc<10)&(zc>12)&(zc<30)
        rch=(xc>104)&(yc<5)&(zc>14)&(zc<22)&(xc<151); rsl=(xc>128)&(xc<151)&(yc<2.2)&(zc>21)&(zc<30)
        rail=rail&((zc<24)|rsl)   # 레일은 판 아래(z' 12..24), 판 층에는 목 슬롯만
        rs=rail&~(rch|rsl); void=(void&~rs)|(rail&~rs); solid=(solid|rs)&~void
    attach_el=np.where(((jaw&(zc>28))|ledge|toppad|(hook&(zc>ZB+6))|((rail&(zc>28)) if GRIP2 else False))&~void)[0]
else:
    void=bore|slit|phone|((zc>ZB)&~plate)
    solid=(contact|ears|jaw|ledge|band|toppad)&~void
    attach_el=np.where((jaw|ledge|toppad)&(zc>ZB+4))[0]
design=~(void|solid); active=~(void)
NX,NY,NZ=nx+1,ny+1,nz+1; nid=lambda i,j,k:(k*NY+j)*NX+i; corner=((xi+1)/2).astype(int)
en=np.stack([nid(I+c[0],J+c[1],K+c[2]) for c in corner],1); edof=np.stack([3*en,3*en+1,3*en+2],2).reshape(len(ei),24)
nn=NX*NY*NZ; gi=np.arange(nn)%NX; gj=(np.arange(nn)//NX)%NY; gk=np.arange(nn)//(NX*NY); nxc=x0+2*gi; nyc=y0+2*gj; nzc=z0+2*gk
used=np.zeros(nn,bool); used[en[active].ravel()]=True
fixn=np.where(used&(np.sqrt(nxc**2+nzc**2)<=16.7))[0]
symn=np.where(used&(gj==0))[0]
ftop=np.array(FACES[(0,0,1)]); fbot=np.array(FACES[(0,0,-1)])
topn=np.unique(en[attach_el][:,ftop].ravel())
fd=np.unique(np.r_[3*fixn,3*fixn+1,3*fixn+2,3*symn+1])
free=np.setdiff1d(np.where(np.repeat(used,3))[0],fd)
ea=edof[active].astype(np.int32); iK=np.repeat(ea,24,1).ravel(); jK=np.tile(ea,(1,24)).ravel()
didx=np.where(design)[0]; nd=len(didx); pos=np.c_[xc,yc,zc][didx]; R=float(env('RF','5'))
print('design',nd,'solid',solid.sum(),'attach nodes',len(topn),flush=True)
# ---- 강체 폰 (절반: 질량/2), 대칭 자유도 (ux, uz, θy) ----
MT=float(env('MSYS','0.300'))*1e-3/2; Lx,Ly,Lz=165.,80.,15.
CG=np.array([XR+75.,0.,ZB+6+Lz/2])
Pr=np.c_[nxc,nzc][topn]-CG[[0,2]]; nt=len(topn); TT=np.zeros((2*nt,3))
for q,(rx,rz) in enumerate(Pr): TT[2*q]=[1,0,rz]; TT[2*q+1]=[0,1,-rx]
Tp=np.linalg.pinv(TT); Mrb=np.diag([MT,MT,MT*(Lx**2+Lz**2)/12])
Ma=Tp.T@Mrb@Tp; dd=np.c_[3*topn,3*topn+2].reshape(-1)
MA=sp.coo_matrix((Ma.ravel(),(np.repeat(dd,len(dd)),np.tile(dd,len(dd)))),shape=(3*nn,3*nn)).tocsr()
# ---- 화면 터치 5 N (절반 2.5 N, 화면에 수직으로 누름): 위쪽 끝 · 아래쪽 끝 ----
DLIM=float(env('DLIM','0.3')); FTCH=2.5; ZS=ZB+6+8.5
def touch_vec(xlp):
    rx=XR+xlp-CG[0]; rz=ZS-CG[2]; W=np.array([0.,-FTCH,-(-FTCH)*rx]); fn=Tp.T@W; f=np.zeros(3*nn); f[dd]=fn; return f
FT_=[touch_vec(145.),touch_vec(5.)]
# ---- 열 (판 3층 + 폰 4층, 발판 영역) ----
K_PETG=0.2e-3; K_AIR=1e-6; K_PH=15e-3; H_RIDE=float(env('HRIDE','23'))*1e-6; H_FRONT=11e-6; Q=2.0   # 절반 = 2 W
th=plate|phone; the=np.where(th)[0]
KTh=hex8_cond(1.,h); MFq=quad_mass(h)
ptop=np.where(plate&(zc>ZB+4))[0]; pbot=np.where(plate&(zc<ZB+2))[0]; pfront=np.where(phone&(zc>ZB+12))[0]
src=np.where(phone&(zc<ZB+8)&(xl>100)&(xl<125)&(yc<10))[0]
thn=np.unique(en[the].ravel()); phn=np.unique(en[phone].ravel()); PN=8.
iT=np.repeat(en[the],8,1).ravel(); jT=np.tile(en[the],(1,8)).ravel()
qv=np.zeros(nn); np.add.at(qv,en[src].ravel(),Q/len(src)/8)
def facemat(els,fl,hv):
    nodes=en[els][:,fl]; r_=[];c_=[];v_=[]
    for a in range(4):
        for b in range(4): r_.append(nodes[:,a]); c_.append(nodes[:,b]); v_.append(hv*MFq[a,b])
    return sp.coo_matrix((np.concatenate(v_),(np.concatenate(r_),np.concatenate(c_))),shape=(nn,nn))
def thermal(r):
    ke=np.where(phone[the],K_PH,K_AIR+r[the]**3*(K_PETG-K_AIR))
    Kt=sp.coo_matrix(((KTh.ravel()[None,:]*ke[:,None]).ravel(),(iT,jT)),shape=(nn,nn)).tocsr()
    Kt=Kt+facemat(ptop,ftop,H_RIDE*(1-r[ptop]))+facemat(pbot,fbot,H_RIDE*r[pbot])+facemat(pfront,ftop,np.full(len(pfront),H_FRONT))
    A=Kt.tocsr()[thn][:,thn]; ps=pypardiso.PyPardisoSolver(); T=np.zeros(nn); T[thn]=ps.solve(A,qv[thn])
    Tm=T[phn]; J=float(np.sum(Tm**PN)**(1/PN))
    g=np.zeros(nn); g[phn]=np.sum(Tm**PN)**(1/PN-1)*Tm**(PN-1); lam=np.zeros(nn); lam[thn]=ps.solve(A,g[thn]); ps.free_memory(everything=True)
    dJ=np.zeros(len(ei)); pe=np.where(plate)[0]
    dJ[pe]=-3*np.maximum(r[pe],1e-9)**2*(K_PETG-K_AIR)*np.einsum('ij,jk,ik->i',lam[en[pe]],KTh,T[en[pe]])
    ft=lambda els,fl: np.einsum('ij,jk,ik->i',lam[en[els]][:,fl],MFq,T[en[els]][:,fl])
    dJ[ptop]+=H_RIDE*ft(ptop,ftop); dJ[pbot]+=-H_RIDE*ft(pbot,fbot)
    return J,dJ,T
# ---- 필터 · 투영 · 출력 필터 (-z' 방향 적층, 판 윗면 = 바닥) ----
tr=cKDTree(pos); pr=tr.query_pairs(R,output_type='ndarray'); a=np.r_[np.arange(nd),pr[:,0],pr[:,1]]; b=np.r_[np.arange(nd),pr[:,1],pr[:,0]]
Hf=sp.coo_matrix((R-np.linalg.norm(pos[a]-pos[b],axis=1),(a,b)),shape=(nd,nd)).tocsr(); Hs=np.asarray(Hf.sum(1)).ravel()
proj=lambda x,be,et=.5:(np.tanh(be*et)+np.tanh(be*(x-et)))/(np.tanh(be*et)+np.tanh(be*(1-et)))
dproj=lambda x,be,et=.5:be*(1-np.tanh(be*(x-et))**2)/(np.tanh(be*et)+np.tanh(be*(1-et)))
KTOP=int((ZB+6-z0)/h)-1                                         # 판 맨 윗층 k (바닥)
PP=40.; NS=5; QA=PP+np.log(NS)/np.log(0.5); EPS=1e-4
fixval=np.where(solid,1.0,0.0); fixed=~design
def grid(v): return v.reshape(nz,ny,nx)[KTOP::-1].copy()
def ungrid(g,base):
    out=base.reshape(nz,ny,nx).copy(); out[KTOP::-1]=g; return out.reshape(-1)
FX=grid(fixed.astype(float))>0.5; FV=grid(fixval)
def nsum(L):   # 가운데 + 면내 4이웃, y=0 쪽은 대칭(거울)
    P_=np.pad(L,1); P_[0,1:-1]=L[0]; return P_[1:-1,1:-1]+P_[:-2,1:-1]+P_[2:,1:-1]+P_[1:-1,:-2]+P_[1:-1,2:]
def am_forward(xh):
    X=grid(xh); XI=np.zeros_like(X); S=np.zeros_like(X); KS=np.zeros_like(X); XI[0]=X[0]
    for j in range(1,X.shape[0]):
        s=nsum(XI[j-1]**PP)+1e-30; Xi=s**(1/QA); S[j]=s; KS[j]=Xi
        a_=X[j]; d=np.sqrt((a_-Xi)**2+EPS); XI[j]=np.where(FX[j],FV[j],0.5*(a_+Xi-d+np.sqrt(EPS)))
    return XI,S,KS,X
def am_adjoint(L,XI,S,KS,X):
    L=L.copy(); dX=np.zeros_like(X)
    for j in range(X.shape[0]-1,0,-1):
        a_=X[j]; Xi=KS[j]; d=np.sqrt((a_-Xi)**2+EPS)
        lj=np.where(FX[j],0.,L[j]); dX[j]+=lj*0.5*(1-(a_-Xi)/d)
        mu=lj*0.5*(1+(a_-Xi)/d)*(1/QA)*S[j]**(1/QA-1); L[j-1]+=nsum(mu)*PP*XI[j-1]**(PP-1)
    dX[0]+=np.where(FX[0],0.,L[0]); return dX
P=3.; EMIN=1e-6; me0=rho*h**3
def interp(r):
    k=EMIN+(1-EMIN)*r**P; dk=(1-EMIN)*P*r**(P-1); m=np.where(r>0.3,r,r**3/0.09); dm=np.where(r>0.3,1.0,3*r**2/0.09); return k,dk,m,dm
def assemble(r):
    k,dk,m,dm=interp(r); ke=np.where(design,k,0.); ke[solid]=1
    Kg=sp.csr_matrix(((KE.ravel()[None,:]*ke[active][:,None]).ravel(),(iK,jK)),shape=(3*nn,3*nn))
    mel=np.where(design,m,0.); mel[solid]=1; mn=np.zeros(nn); np.add.at(mn,en.ravel(),np.repeat(mel*me0/8,8))
    MM=(sp.diags(np.repeat(mn,3))+MA).tocsr(); return Kg,MM,dk,dm
def analyse(r,neig=4,want_modes=False):
    Kg,MM,dk,dm=assemble(r); A=Kg[free][:,free].tocsr(); MF=MM[free][:,free].tocsr()
    ps=pypardiso.PyPardisoSolver(); ps.factorize(A); OP=sla.LinearOperator(A.shape,matvec=lambda v: ps.solve(A,v),dtype=float)
    lam,V=sla.eigsh(A,k=neig,M=MF,sigma=0,OPinv=OP,tol=1e-8); o=np.argsort(lam); lam,V=lam[o],V[:,o]
    out=[]; phis=[]
    for q in range(neig):
        phi=np.zeros(3*nn); phi[free]=V[:,q]/np.sqrt(V[:,q]@(MF@V[:,q])); phis.append(phi)
        pe=phi[edof]; sk=np.einsum('ij,jk,ik->i',pe,KE,pe); pn=(phi.reshape(-1,3)**2).sum(1); sm=pn[en].sum(1)*me0/8
        out.append((lam[q],np.where(design,dk*sk-lam[q]*dm*sm,0.)))
    stat=[]
    for f_ in FT_:
        u=np.zeros(3*nn); u[free]=ps.solve(A,f_[free]); c=float(f_@u); ue=u[edof]
        stat.append((c/FTCH,np.where(design,-dk*np.einsum('ij,jk,ik->i',ue,KE,ue),0.)/FTCH))
    out=(out,stat) if not want_modes else out
    if want_modes: return out,phis,ps,A,MM
    ps.free_memory(everything=True); del ps; gc.collect(); return out
def massg(r): return float(r[active&~void].sum()*me0*1e6*2)   # 전체(양쪽) g
def frf(r,neig=10,zeta=0.03):
    out,phis,ps,A,MM=analyse(r,neig,True); fr=np.linspace(5,100,191); res={}
    for nm,dvec in (('vert',(st,ct)),('fore',(ct,-st))):          # 세계 위아래 / 앞뒤 단위벡터의 (x', z') 성분
        ri=np.zeros(3*nn); ri[0::3]=dvec[0]; ri[2::3]=dvec[1]; ri[fd]=0
        H=np.ones(len(fr),complex)
        for (lam_,_),phi in zip(out,phis):
            wn=np.sqrt(lam_); G=phi@(MM@ri)
            rb=Tp@np.c_[phi[3*topn],phi[3*topn+2]].reshape(-1); cg=rb[0]*dvec[0]+rb[1]*dvec[1]
            w=2*np.pi*fr; H+=cg*G*w**2/(wn**2-w**2+2j*zeta*wn*w)
        T_=np.abs(H); s=(fr>=10)&(fr<=100); b=(fr>=34.6)&(fr<=45.6)
        s8=(fr>=6.3)&(fr<=80); res[nm]=dict(peak80=round(float(T_[s8].max()),2),rms80=round(float(np.sqrt(np.mean(T_[s8]**2))),3),peak=round(float(T_.max()),2),rms=round(float(np.sqrt(np.mean(T_[s]**2))),3),band=round(float(T_[b].max()),2),T=[round(float(v),4) for v in T_])
    res['freq']=[float(v) for v in fr]; res['f']=[round(float(np.sqrt(l)/2/np.pi),1) for l,_ in out]
    # 충격 48.5 g (세계 위아래 · 앞뒤): 폰 관성력을 집게 · 받침 턱에 분배
    Kg,_,_,_=assemble(r); stress={}
    for nm,dvec in (('vert',(st,ct)),('fore',(ct,-st))):
        Fr=Mrb@np.array([dvec[0],dvec[1],0.])*48.5*9810.; fn=Tp.T@Fr; F=np.zeros(3*nn); F[dd]=fn
        U=np.zeros(3*nn); U[free]=ps.solve(A,F[free]); on=np.where((r>0.5)&active)[0]; on=on[rr[on]>19]
        s_=(C@B0@U[edof[on]].T).T; vm=np.sqrt(0.5*((s_[:,0]-s_[:,1])**2+(s_[:,1]-s_[:,2])**2+(s_[:,2]-s_[:,0])**2)+3*(s_[:,3:]**2).sum(1))
        szt=np.maximum(s_[:,2],0)                                     # 층간: 적층 방향 = z'
        stress[nm]=dict(vm999=round(float(np.percentile(vm,99.9)),1),interlayer999=round(float(np.percentile(szt,99.9)),1))
    res['shock']=stress; ps.free_memory(everything=True); return res
# ==== 11-16 추가: 프레임 생성기(gen_frame) 학습 데이터 — 구조(label3) · 열 전용(tlabel) ===================
GRIPN = 2 if GRIP2 else (1 if GRIP else 0)
def _gen_meta():
    return dict(xc=xc, yc=yc, zc=zc, design=design, solid=solid, plate=plate, nx=nx, ny=ny, nz=nz)
def thermal_T(r):
    """열만 (수반 해석 없이): 폰 온도장. thermal() 과 같은 식"""
    ke=np.where(phone[the],K_PH,K_AIR+r[the]**3*(K_PETG-K_AIR))
    Kt=sp.coo_matrix(((KTh.ravel()[None,:]*ke[:,None]).ravel(),(iT,jT)),shape=(nn,nn)).tocsr()
    Kt=Kt+facemat(ptop,ftop,H_RIDE*(1-r[ptop]))+facemat(pbot,fbot,H_RIDE*r[pbot])+facemat(pfront,ftop,np.full(len(pfront),H_FRONT))
    A=Kt.tocsr()[thn][:,thn]; ps=pypardiso.PyPardisoSolver(); T=np.zeros(nn); T[thn]=ps.solve(A,qv[thn]); ps.free_memory(everything=True)
    return T
EXT_NAMES=['f3_hz','f4_hz','band_vert','band_fore','peak80_vert','peak80_fore','rms80_vert','rms80_fore',
           'shock_vm999_fore_mpa','interlayer999_vert_mpa','interlayer999_fore_mpa']
def label_full(r, neig=int(env('NEIG','10')), zeta=0.03):
    """구조 정답 한 번에: 모드 neig 개 → 흔들림(진동 전달 5–100 Hz, 위아래·앞뒤) · 터치 · 충격(위아래·앞뒤 von Mises, 층간)
    frf() · eval 과 같은 식. 반환: (label2 와 같은 7개 중 구조 6개 dict, 추가값 dict, 요소 vm(위아래))"""
    out,phis,ps,A,MM=analyse(r,neig,True); f=[float(np.sqrt(max(l,0))/2/np.pi) for l,_ in out]
    fr=np.linspace(5,100,191); ext={}
    for nm,dvec in (('vert',(st,ct)),('fore',(ct,-st))):
        ri=np.zeros(3*nn); ri[0::3]=dvec[0]; ri[2::3]=dvec[1]; ri[fd]=0; H=np.ones(len(fr),complex)
        for (lam_,_),phi in zip(out,phis):
            wn=np.sqrt(lam_); G=phi@(MM@ri); rb=Tp@np.c_[phi[3*topn],phi[3*topn+2]].reshape(-1); cg=rb[0]*dvec[0]+rb[1]*dvec[1]
            w=2*np.pi*fr; H+=cg*G*w**2/(wn**2-w**2+2j*zeta*wn*w)
        T_=np.abs(H); b=(fr>=34.6)&(fr<=45.6); s8=(fr>=6.3)&(fr<=80)
        ext['band_'+nm]=float(T_[b].max()); ext['peak80_'+nm]=float(T_[s8].max()); ext['rms80_'+nm]=float(np.sqrt(np.mean(T_[s8]**2)))
    tch=[]
    for f_ in FT_:
        u=np.zeros(3*nn); u[free]=ps.solve(A,f_[free]); tch.append(float(f_@u)/FTCH)
    vm_el=np.zeros(len(ei)); sh={}
    for nm,dvec in (('vert',(st,ct)),('fore',(ct,-st))):
        Fr=Mrb@np.array([dvec[0],dvec[1],0.])*48.5*9810.; fn=Tp.T@Fr; F=np.zeros(3*nn); F[dd]=fn
        U=np.zeros(3*nn); U[free]=ps.solve(A,F[free]); on=np.where((r>0.5)&active)[0]
        s_=(C@B0@U[edof[on]].T).T; vm=np.sqrt(0.5*((s_[:,0]-s_[:,1])**2+(s_[:,1]-s_[:,2])**2+(s_[:,2]-s_[:,0])**2)+3*(s_[:,3:]**2).sum(1))
        szt=np.maximum(s_[:,2],0); k_=rr[on]>19
        sh[nm]=(float(np.percentile(vm[k_],99.9)) if k_.any() else 0., float(np.percentile(szt[k_],99.9)) if k_.any() else 0.)
        if nm=='vert': vm_el[on]=vm
    ps.free_memory(everything=True)
    ext.update(f3_hz=f[2] if len(f)>2 else np.nan, f4_hz=f[3] if len(f)>3 else np.nan, shock_vm999_fore_mpa=sh['fore'][0],
               interlayer999_vert_mpa=sh['vert'][1], interlayer999_fore_mpa=sh['fore'][1])
    base=dict(f1=f[0],f2=f[1],touch_top=tch[0],touch_bot=tch[1],vm_vert=sh['vert'][0])
    return base,ext,vm_el
if MODE=='label3':  # 구조 + 열 정답 (프레임 생성기 또는 SRC). lab = label2 와 같은 7열(ai/ 코드 그대로 사용) + lab_ext 11열
    import gen_frame; rng=np.random.default_rng(int(env('SEED','0'))); t0=time.time(); src=None; SR=env('SRC')
    if SR:
        _d=np.load(SR); _R=np.unpackbits(_d['r'],axis=1)[:,:len(ei)]; _N=list(_d['names']); a0,a1=int(env('I0','0')),int(env('I1',str(len(_N))))
        src=[(_N[q],_R[q]) for q in range(a0,min(a1,len(_N)))]
    N=len(src) if src else int(env('NS','40')); FAM=env('FAMILY') or None; GM=_gen_meta()
    O=[];L=[];X=[];FT_T=[];FT_V=[];NAMES=[];PRM=[]
    for i in range(N):
        if src: nm,_r=src[i]; occ=(np.asarray(_r).ravel()>0.5)&design; prm={}
        else:
            occ,prm=gen_frame.sample(rng,GM,GRIPN,FAM); nm='frame_%d_%d'%(int(env('SEED','0')),i)
            if occ is None: continue
        if occ.sum()<30: continue
        r=np.where(design,occ.astype(float),fixval); t1=time.time()
        try: base,ext,vm_el=label_full(r); T=thermal_T(r)
        except Exception as e: print('fail',nm,e,flush=True); continue
        L.append([massg(r),base['f1'],base['f2'],float(T[phn].max()),base['touch_top'],base['touch_bot'],base['vm_vert']])
        X.append([ext[k] for k in EXT_NAMES]); O.append(np.packbits(occ[didx]))
        FT_T.append(np.asarray(T)[en].mean(1).astype(np.float16)); FT_V.append(vm_el.astype(np.float16)); NAMES.append(nm); PRM.append(json.dumps(prm))
        print(json.dumps(dict(i=i,name=nm,lab=[round(v,3) for v in L[-1]],ext=[round(v,3) for v in X[-1]],dt=round(time.time()-t1,1),t=round(time.time()-t0))),flush=True)
    np.savez_compressed(env('OUT'),occ=np.array(O),lab=np.array(L),lab_ext=np.array(X),T=np.array(FT_T),vm=np.array(FT_V),names=np.array(NAMES),
        prm=np.array(PRM),grip=GRIPN,lab_names=np.array(['mass_g','f1_hz','f2_hz','phone_Tmax_rise_c','touch_top_mm','touch_bottom_mm','shock_vm999_mpa']),
        ext_names=np.array(EXT_NAMES))
    print('done',len(O),round(time.time()-t0),flush=True); sys.exit()
if MODE=='tlabel':  # 열 전용: 받침판 패턴만 바꿔 폰 온도장. 판 아래 몸체는 열 모델에 없으므로 비움
    import gen_frame; rng=np.random.default_rng(int(env('SEED','0'))); N=int(env('NS','200')); t0=time.time()
    pidx=np.where(plate&design)[0]; O=[];Y=[];TF=[];PRM=[]; seen=set(); dup=0
    for i in range(N):
        p=gen_frame.draw_plate(rng); occ=gen_frame.plate_mask(p,xc,yc,zc,plate)&design
        key=np.packbits(occ[pidx]).tobytes()
        if key in seen: dup+=1; continue                                  # 격자 위에서 같은 패턴은 한 번만
        seen.add(key); r=np.where(design,occ.astype(float),fixval); t1=time.time()
        try: T=thermal_T(r)
        except Exception as e: print('fail',i,e,flush=True); continue
        O.append(np.packbits(occ[pidx])); Y.append(float(T[phn].max())); TF.append(np.asarray(T)[en[the]].mean(1).astype(np.float16)); PRM.append(json.dumps(p))
        if i<5 or i%50==0: print(json.dumps(dict(i=i,kind=p['kind'],layers=p['layers'],Tmax=round(Y[-1],3),dt=round(time.time()-t1,2),t=round(time.time()-t0,1))),flush=True)
    np.savez_compressed(env('OUT'),occ_plate=np.array(O),Tmax=np.array(Y),T_thermal=np.array(TF),prm=np.array(PRM),pidx=pidx,the=the,grip=GRIPN)
    print('done',len(O),'중복 건너뜀',dup,round(time.time()-t0),flush=True); sys.exit()
if MODE=='meta':    # 학습 코드가 쓰는 격자 정보 (설계 · 고정 · 빈 영역, 좌표)
    np.savez(env('OUT','grid_meta.npz'),nx=nx,ny=ny,nz=nz,h=h,origin=np.array([x0,y0,z0]),didx=didx,solid=solid,void=void,design=design,
             phone=phone,plate=plate,xc=xc,yc=yc,zc=zc); print('meta ok',env('OUT','grid_meta.npz')); sys.exit()
if MODE=='label2':  # 학습 데이터 v2: 형상 → 스칼라 7개 + 분포 2개(온도 · 충격 응력). SRC 가 있으면 그 파일들(위상 최적화 기록), 없으면 생성기
    import gen_int, glob; rng=np.random.default_rng(int(env('SEED','0'))); t0=time.time()
    src=None; SR=env('SRC')
    if SR and SR.endswith('.npz'):   # 묶음 파일: r = packbits(요소 점유), names
        _d=np.load(SR); _R=np.unpackbits(_d['r'],axis=1)[:,:len(ei)]; _N=list(_d['names']); a0,a1=int(env('I0','0')),int(env('I1',str(len(_N))))
        src=[(_N[q],_R[q]) for q in range(a0,min(a1,len(_N)))]
    elif SR: src=[(os.path.basename(f),np.load(f).ravel()) for f in sorted(glob.glob(SR))]
    N=len(src) if src else int(env('NS','40'))
    O=[];L=[];FT_T=[];FT_V=[];NAMES=[]
    for i in range(N):
        if src: nm,_r=src[i]; occ=(np.asarray(_r).ravel()>0.5)&design
        else: occ=gen_int.sample(rng,xc,yc,zc,design,solid,contact,(nz,ny,nx)); nm='gen_%d_%d'%(int(env('SEED','0')),i)
        if occ.sum()<30: continue
        r=np.where(design,occ.astype(float),fixval)
        try:
            out,phis,ps,A,MM=analyse(r,2,True); J,_,T=thermal(r)
            tch=[]
            for f_ in FT_:
                u=np.zeros(3*nn); u[free]=ps.solve(A,f_[free]); tch.append(float(f_@u)/FTCH)
            dvec=(st,ct); Fr=Mrb@np.array([dvec[0],dvec[1],0.])*48.5*9810.; fn=Tp.T@Fr; F=np.zeros(3*nn); F[dd]=fn
            U=np.zeros(3*nn); U[free]=ps.solve(A,F[free]); on=np.where((r>0.5)&active)[0]
            s_=(C@B0@U[edof[on]].T).T; vm=np.sqrt(0.5*((s_[:,0]-s_[:,1])**2+(s_[:,1]-s_[:,2])**2+(s_[:,2]-s_[:,0])**2)+3*(s_[:,3:]**2).sum(1))
            ps.free_memory(everything=True)
        except Exception as e: print('fail',nm,e,flush=True); continue
        f=[float(np.sqrt(max(l,0))/2/np.pi) for l,_ in out]; ve=np.zeros(len(ei)); ve[on]=vm
        vmc=vm[rr[on]>19]; L.append([massg(r),f[0],f[1],float(T[phn].max()),tch[0],tch[1],float(np.percentile(vmc,99.9)) if len(vmc) else 0.])
        O.append(np.packbits(occ[didx])); FT_T.append(np.asarray(T)[en].mean(1).astype(np.float16)); FT_V.append(ve.astype(np.float16)); NAMES.append(nm)
        print(json.dumps(dict(i=i,name=nm,lab=[round(v,3) for v in L[-1]],t=round(time.time()-t0))),flush=True)
    np.savez_compressed(env('OUT'),occ=np.array(O),lab=np.array(L),T=np.array(FT_T),vm=np.array(FT_V),names=np.array(NAMES),
        lab_names=np.array(['mass_g','f1_hz','f2_hz','phone_Tmax_rise_c','touch_top_mm','touch_bottom_mm','shock_vm999_mpa']))
    print('done',len(O),round(time.time()-t0),flush=True); sys.exit()
if MODE=='label':   # 형상 AI · 물리 AI 학습 데이터: 생성 형상 N개 -> 무게 · 1차 진동수 · 폰 온도 · 터치 처짐
    import gen_int; rng=np.random.default_rng(int(env('SEED','0'))); N=int(env('NS','40')); O=[]; L=[]; t0=time.time()
    for i in range(N):
        occ=gen_int.sample(rng,xc,yc,zc,design,solid,contact,(nz,ny,nx))
        if occ.sum()<30: continue
        r=np.where(design,occ.astype(float),fixval)
        try: res,stt=analyse(r,2); J,_,T=thermal(r)
        except Exception as e: print('fail',e,flush=True); continue
        f1=float(np.sqrt(max(res[0][0],0))/2/np.pi)
        O.append(np.packbits(occ[didx])); L.append([massg(r),f1,float(T[phn].max()),float(stt[0][0])])
    np.savez(env('OUT'),occ=np.array(O),lab=np.array(L)); print('done',len(O),round(time.time()-t0),flush=True); sys.exit()
if MODE=='field':   # 분포 출력: 노면 진동 FF Hz(세계 위아래)에서 핸들바 대비 상대 흔들림 크기(절점), 폰 온도장(절점)
    r=np.load(env('RHO')); r=np.where(design,r,fixval); J,_,T=thermal(r)
    out,phis,ps,A,MM=analyse(r,10,True); FF=float(env('FF','30.5')); w=2*np.pi*FF; dvec=(st,ct)
    ri=np.zeros(3*nn); ri[0::3]=dvec[0]; ri[2::3]=dvec[1]; ri[fd]=0; U=np.zeros(3*nn,complex)
    for (lam_,_),phi in zip(out,phis):
        wn=np.sqrt(lam_); G=phi@(MM@ri); U+=phi*G*w**2/(wn**2-w**2+2j*0.03*wn*w)
    amp=np.sqrt(np.abs(U[0::3])**2+np.abs(U[1::3])**2+np.abs(U[2::3])**2)   # 바닥 진폭 1 대비
    # 같은 척도 비교용: 10–100 Hz 노면 진동(세계 위아래) 동안 각 절점의 흔들림 배율 RMS (핸들바 = 1)
    fr=np.linspace(10,100,46); acc=np.zeros(nn)
    for f_ in fr:
        w_=2*np.pi*f_; Ur=np.zeros(3*nn,complex)
        for (lam_,_),phi in zip(out,phis):
            wn=np.sqrt(lam_); G=phi@(MM@ri); Ur+=phi*G*w_**2/(wn**2-w_**2+2j*0.03*wn*w_)
        ax_=dvec[0]+Ur[0::3]; az_=dvec[1]+Ur[2::3]; ay_=Ur[1::3]
        acc+=np.abs(ax_)**2+np.abs(ay_)**2+np.abs(az_)**2
    trms=np.sqrt(acc/len(fr))
    # 충격 48.5 g 위아래: 요소 von Mises -> 절점 평균
    Fr=Mrb@np.array([dvec[0],dvec[1],0.])*48.5*9810.; fn=Tp.T@Fr; F=np.zeros(3*nn); F[dd]=fn
    Uq=np.zeros(3*nn); Uq[free]=ps.solve(A,F[free]); on=np.where((r>0.5)&active)[0]
    s_=(C@B0@Uq[edof[on]].T).T; vm=np.sqrt(0.5*((s_[:,0]-s_[:,1])**2+(s_[:,1]-s_[:,2])**2+(s_[:,2]-s_[:,0])**2)+3*(s_[:,3:]**2).sum(1))
    vn=np.zeros(nn); cn=np.zeros(nn); np.add.at(vn,en[on].ravel(),np.repeat(vm,8)); np.add.at(cn,en[on].ravel(),1); vmn=vn/np.maximum(cn,1)
    i1=int(np.argmin([l for l,_ in out])); p1=phis[i1]; m1=np.sqrt(p1[0::3]**2+p1[1::3]**2+p1[2::3]**2); m1=m1/m1[used].max()
    np.savez('field_%s.npz'%TAG,r=r,amp=amp,T=np.asarray(T).ravel(),mode1=m1,trms=trms,vm=vmn,f1=float(np.sqrt(out[i1][0])/2/np.pi),nx=nx,FF=FF); ps.free_memory(everything=True)
    print('field ok',TAG,'amp max',float(amp[used].max()),'T max',float(np.asarray(T).max())); sys.exit()
if MODE=='eval':
    r=np.load(env('RHO')); r=np.where(design,r,fixval); J,_,T=thermal(r); out=frf(r)
    _,stt=analyse(r,4); out['touch_mm']=[round(s_[0],3) for s_ in stt]
    out.update(mass_g=round(massg(r),1),Tmax=round(float(T[phn].max()),2),tilt=float(env('TILT','35')))
    json.dump(out,open('frfint_%s.json'%TAG,'w')); print(json.dumps({k:v for k,v in out.items() if k not in('freq',)},default=str)[:1500]); sys.exit()
if MODE=='fd':
    rg=np.random.default_rng(0); r=np.where(design,rg.uniform(0.2,0.8,len(ei)),fixval); J,dJ,_=thermal(r)
    for e in rg.choice(np.where(plate&design)[0],4,replace=False):
        r2=r.copy(); r2[e]+=1e-4; J2,_,_=thermal(r2); print(e,dJ[e],(J2-J)/1e-4)
    sys.exit()
# ---- 최적화: 무게 최소, 제약 f1..f4 ≥ FT, 폰 온도 P-norm ≤ TLIM ----
x=np.full(nd,0.5); START=int(env('START','0'))
if START>0: x=np.load('x_%s.npy'%TAG)
if env('START_RHO'): x=np.clip(0.2+0.6*(np.load(env('START_RHO')).ravel()[didx]>0.5),0,1)   # 형상 AI 후보를 시작 형상으로
xo1=x[:,None].copy(); xo2=x[:,None].copy(); low=np.zeros((nd,1)); upp=np.ones((nd,1)); mcon=7
sched=json.loads(env("SCHED",json.dumps({0:1,30:2,60:4,90:8,120:16,160:32})).replace("\"",chr(34))); sched={int(k):v for k,v in sched.items()}; ETAE=float(env('ETAE','0.6')); t0=time.time()
for it in range(START,ITERS):
    be=[v for kk,v in sorted(sched.items()) if kk<=it][-1]; xt=np.asarray(Hf@x).ravel()/Hs; R_={}
    for tg,et in (('n',0.5),('e',ETAE)):
        xb=proj(xt,be,et); full=fixval.copy(); full[didx]=xb
        if AMF: am=am_forward(full); R_[tg]=(ungrid(am[0],fixval),am)
        else: R_[tg]=(full,None)
    rn,amn=R_['n']; re_,ame=R_['e']
    def chain(gf,am,et):
        g=ungrid(am_adjoint(grid(gf),*am),np.zeros(len(ei)))[didx] if AMF else gf[didx]; return np.asarray(Hf.T@(g*dproj(xt,be,et)/Hs)).ravel()
    res,stat=analyse(re_); J,dJ,T=thermal(rn)
    vm=np.zeros(len(ei)); vm[design]=1.0/nd; f0=rn[design].mean(); df0=chain(vm,amn,0.5)
    cT=float(T[phn].max())/J; fval=np.r_[[1-q[0]/LT for q in res],cT*J/TLIM-1,[s_[0]/DLIM-1 for s_ in stat]]
    dfdx=np.vstack([chain(-q[1]/LT,ame,ETAE) for q in res]+[chain(cT*dJ/TLIM,amn,0.5)]+[chain(s_[1]/DLIM,ame,ETAE) for s_ in stat])
    xn,_,_,_,_,_,_,_,_,low,upp=mmapy.mmasub(mcon,nd,it+1-START,x[:,None],np.zeros((nd,1)),np.ones((nd,1)),xo1,xo2,f0,df0[:,None],fval[:,None],dfdx,low,upp,1.,np.zeros((mcon,1)),1e4*np.ones((mcon,1)),np.zeros((mcon,1)),move=0.1)
    xo2=xo1.copy(); xo1=x[:,None].copy(); x=xn.ravel()
    print(json.dumps(dict(it=it,beta=be,mass_g=round(massg(rn),1),f=[round(float(np.sqrt(q[0])/2/np.pi),1) for q in res],Tmax=round(float(T[phn].max()),2),touch=[round(s_[0],3) for s_ in stat],t=round(time.time()-t0))),flush=True)
    if it%10==0 or it==ITERS-1: np.save('x_%s.npy'%TAG,x); np.save('rprint_%s.npy'%TAG,rn)
    if it%4==0 or it==ITERS-1: np.save('snap_%s_%03d.npy'%(TAG,it),rn.astype(np.float32))
