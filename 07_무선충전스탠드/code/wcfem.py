import numpy as np, scipy.sparse as sp, pypardiso, gc
from wcgeo import *
from thermal3d import hex8_cond, quad_mass, FACES
from fem3d import hex8_KB
KAL,KTCP,KPL=167e-3,5e-3,0.2e-3          # W/mmK : aluminium, thermally-conductive plastic (assumed), plastic
HCONV=float(__import__('os').environ.get('HC','10'))*1e-6   # W/mm2K natural convection (assumed)
EAL,EPL=68900.,2500.
P=3.; EMIN=1e-6
act=np.where(allsolid)[0]; amap=-np.ones(len(ei),int); amap[act]=np.arange(len(act))
NX,NY,NZ=nx+1,ny+1,nz+1; nid=lambda i,j,k:(k*NY+j)*NX+i
_xi=np.array([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]]); cor=((_xi+1)/2).astype(int)
en=np.stack([nid(I+c[0],J+c[1],K+c[2]) for c in cor],1)
nn=NX*NY*NZ; gi=np.arange(nn)%NX; gj=(np.arange(nn)//NX)%NY; gk=np.arange(nn)//(NX*NY)
KT=hex8_cond(1.0,h); MF=quad_mass(h)
# --- convection faces
eid=-np.ones((nz,ny,nx),int); eid.ravel()[act]=act
F_i=[];F_j=[];F_nodes=[]
phone_zone=(lambda kk,jj: True)
for n,fl in FACES.items():
    di,dj,dk=n
    for e in act:
        i,j,k=I[e],J[e],K[e]
        if di==-1 and i==0: continue                 # symmetry plane
        if dk==-1 and k==0: continue                 # table contact (adiabatic)
        ii,jj,kk=i+di,j+dj,k+dk
        nb=-1
        if 0<=ii<nx and 0<=jj<ny and 0<=kk<nz: nb=eid[kk,jj,ii]
        if nb<0 and skin[e] and n==(0,-1,0) or (nb<0 and skin[e] and n==(0,0,1) and zc[e]<HZ-5): continue  # phone-covered front skin: adiabatic
        if nb>=0 and nb<e: continue                  # count interior pairs once
        F_i.append(e); F_j.append(nb); F_nodes.append(en[e][fl])
F_i=np.array(F_i); F_j=np.array(F_j); F_nodes=np.array(F_nodes)
iT=np.repeat(en[act],8,1).ravel(); jT=np.tile(en[act],(1,8)).ravel()
iF=np.repeat(F_nodes,4,1).ravel(); jF=np.tile(F_nodes,(1,4)).ravel()
usedT=np.zeros(nn,bool); usedT[en[act].ravel()]=True; freeT=np.where(usedT)[0]
# heat source (half model)
coilidx=np.where(coil)[0]
def qvec(Q):
    q=np.zeros(nn); np.add.at(q,en[coilidx].ravel(),Q/2/len(coilidx)/8); return q
# contact surface nodes (outer skin face near coil)
cn=np.unique(en[np.where(skin&(rad<RKO))[0]].ravel()); cn=cn[(gj[cn]*h+Y0)<=np.array([front_y(z) for z in gk[cn]*h])+0.6]
def solid_ind(rho):
    s=np.zeros(len(ei)); s[allsolid]=1.0; s[design]=rho[design]; return s
def thermal(rho,Q):
    s=solid_ind(rho)
    kel=np.where(design,EMIN*KAL+(KAL-EMIN*KAL)*rho**P,0.); kel[keep]=KTCP; kel[skin|ledge]=KPL; kel[pads]=KAL
    wf=np.where(F_j<0,s[F_i],s[F_i]*(1-s[np.maximum(F_j,0)])+s[np.maximum(F_j,0)]*(1-s[F_i]))
    A=sp.csr_matrix(((KT.ravel()[None,:]*kel[act][:,None]).ravel(),(iT,jT)),shape=(nn,nn))
    A=A+sp.csr_matrix((((HCONV*MF).ravel()[None,:]*wf[:,None]).ravel(),(iF,jF)),shape=(nn,nn))
    Af=A[freeT][:,freeT].tocsr(); q=qvec(Q)
    T=np.zeros(nn); ps=pypardiso.PyPardisoSolver(); ps.factorize(Af); T[freeT]=ps.solve(Af,q[freeT])
    return T,(ps,Af,kel,wf,s)
# --- structure
KE,CC,B0,_=hex8_KB(1.0,0.33,h)
iK=np.repeat(np.stack([3*en,3*en+1,3*en+2],2).reshape(len(ei),24)[act],24,1).ravel()
edof=np.stack([3*en,3*en+1,3*en+2],2).reshape(len(ei),24)
jK=np.tile(edof[act],(1,24)).ravel()
padn=np.unique(en[pads][:,:4].ravel()); padn=padn[gk[padn]==0]
plane=np.where(usedT&(gi==0))[0]
fixS=np.unique(np.r_[3*padn,3*padn+1,3*padn+2,3*plane])
freeS=np.setdiff1d(np.where(np.repeat(usedT,3))[0],fixS)
# loads: phone weight 2 N on ledge top, finger tap 5 N normal to front surface near top (half model)
ledn=np.unique(en[np.where(ledge)[0]].ravel()); ledn=ledn[gk[ledn]==gk[ledn].max()]
topskin=np.unique(en[np.where(skin&(zc>95))[0]].ravel())
FS=np.zeros((3*nn,2))
FS[3*ledn+2,0]=-1.0/len(ledn)
nrm_in=np.array([0.,np.sin(ANG),-np.cos(ANG)])
for d in range(3): FS[3*topskin+d,1]=2.5*nrm_in[d]/len(topskin)
def struct(rho):
    Eel=np.where(design,EAL*(EMIN+(1-EMIN)*rho**P),0.); Eel[fixedplastic]=EPL; Eel[pads]=EAL
    A=sp.csr_matrix(((KE.ravel()[None,:]*Eel[act][:,None]).ravel(),(iK,jK)),shape=(3*nn,3*nn))[freeS][:,freeS].tocsr()
    U=np.zeros((3*nn,2)); U[freeS]=pypardiso.spsolve(A,FS[freeS]); return U,Eel
