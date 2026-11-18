import numpy as np, scipy.sparse as sp, json, os, time, mmapy, pypardiso
from scipy.spatial import cKDTree
from wcfem import *
Q=float(os.environ.get('Q','5')); DTLIM=float(os.environ.get('DT','21')); TAP=float(os.environ.get('TAP','0.1')); ITERS=int(os.environ.get('ITERS','150')); TAG=os.environ.get('TAG','w')
didx=np.where(design)[0]; nd=len(didx); pos=np.c_[xc,yc,zc][didx]; R=float(os.environ.get('RF','5.5'))
tr=cKDTree(pos); pr=tr.query_pairs(R,output_type='ndarray'); a=np.r_[np.arange(nd),pr[:,0],pr[:,1]]; b=np.r_[np.arange(nd),pr[:,1],pr[:,0]]; w=R-np.linalg.norm(pos[a]-pos[b],axis=1)
m2=pos.copy(); m2[:,0]=-m2[:,0]; D=tr.sparse_distance_matrix(cKDTree(m2),R,output_type='coo_matrix')
Hf=sp.coo_matrix((np.r_[w,R-D.data],(np.r_[a,D.row],np.r_[b,D.col])),shape=(nd,nd)).tocsr(); Hs=np.asarray(Hf.sum(1)).ravel()
proj=lambda x,be,et=.5:(np.tanh(be*et)+np.tanh(be*(x-et)))/(np.tanh(be*et)+np.tanh(be*(1-et)))
dproj=lambda x,be,et=.5:be*(1-np.tanh(be*(x-et))**2)/(np.tanh(be*et)+np.tanh(be*(1-et)))
gT=np.zeros(nn); gT[cn]=1.0/len(cn)                       # mean contact temperature rise
dKe_cond=KT
def sens_thermal(rho,T,lam,kel,wf,s):
    # d(mean T)/d rho_e = -lam^T dK/drho T
    dk=np.where(design,(KAL-EMIN*KAL)*P*np.maximum(rho,1e-9)**(P-1),0.)
    Te=T[en]; Le=lam[en]; ce=np.einsum('ij,jk,ik->i',Le,KT,Te); d=-dk*ce
    # convection faces
    Tf=T[F_nodes]; Lf=lam[F_nodes]; cf=HCONV*np.einsum('ij,jk,ik->i',Lf,MF,Tf)
    sj=s[np.maximum(F_j,0)]; si=s[F_i]
    dwi=np.where(F_j<0,1.0,1-2*sj); dwj=np.where(F_j<0,0.0,1-2*si)
    np.add.at(d,F_i,-cf*dwi*design[F_i]); m=(F_j>=0); np.add.at(d,F_j[m],-(cf*dwj)[m]*design[F_j[m]])
    return d
x=np.full(nd,0.3); xold1=x[:,None].copy(); xold2=x[:,None].copy(); low=np.zeros((nd,1)); upp=np.ones((nd,1))
S_=int(os.environ.get('STG','30')); sched={0:1,S_:2,2*S_:4,3*S_:8,4*S_:16}; ETA=0.5; ETAE=float(os.environ.get('ETAE','0.6')); t0=time.time()
LIMW=None
for it in range(ITERS):
    be=[v for kk,v in sorted(sched.items()) if kk<=it][-1]
    xt=np.asarray(Hf@x).ravel()/Hs; xb=proj(xt,be); xe=proj(xt,be,ETAE)
    rho=np.zeros(len(ei)); rho[didx]=xe
    T,(ps,Af,kel,wf,s)=thermal(rho,Q)
    lam=np.zeros(nn); lam[freeT]=ps.solve(Af,gT[freeT]); ps.free_memory(everything=True)
    tmean=gT@T; dT=sens_thermal(rho,T,lam,kel,wf,s)[didx]
    U,Eel=struct(rho); comp=FS[:,1]@U[:,1]; tap=comp/2.5
    ue=U[:,1][edof[didx]]; ce=np.einsum('ij,jk,ik->i',ue,KE,ue); dcomp=-EAL*(1-EMIN)*P*np.maximum(xe,1e-9)**(P-1)*ce
    f0=xb.mean(); df0=np.asarray(Hf.T@(dproj(xt,be)/nd/Hs)).ravel()
    fval=np.array([tmean/DTLIM-1, tap/TAP-1])
    dfdx=np.array([np.asarray(Hf.T@(dT/DTLIM*dproj(xt,be,ETAE)/Hs)).ravel(), np.asarray(Hf.T@(dcomp/2.5/TAP*dproj(xt,be,ETAE)/Hs)).ravel()])
    xn,_,_,_,_,_,_,_,_,low,upp=mmapy.mmasub(2,nd,it+1,x[:,None],np.zeros((nd,1)),np.ones((nd,1)),xold1,xold2,f0,df0[:,None],fval[:,None],dfdx,low,upp,1.,np.zeros((2,1)),1e4*np.ones((2,1)),np.zeros((2,1)),move=0.1)
    xold2=xold1.copy(); xold1=x[:,None].copy(); x=xn.ravel()
    if it%10==0 or it==ITERS-1:
        print(json.dumps(dict(it=it,beta=be,al_g=round(2*xb.sum()*h**3*2.7e-3,1),Tmean=round(25+tmean,2),Tmax=round(25+T[cn].max(),2),tap=round(tap,4),t=round(time.time()-t0))),flush=True)
        np.save('x_%s.npy'%TAG,x); rn=np.zeros(len(ei)); rn[didx]=xb; np.save('rho_%s.npy'%TAG,rn)
