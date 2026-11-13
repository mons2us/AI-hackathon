import numpy as np, scipy.sparse as sp, json, os, time, mmapy
from scipy.spatial import cKDTree
from head import *
VF=float(os.environ.get('VF','0.5')); ITERS=int(os.environ.get('ITERS','120')); TAG=os.environ.get('TAG','a'); PN=10.
didx=np.where(design)[0]; nd=len(didx)
lay=np.where(layA[didx],0,1); pos=np.c_[uc[didx],vc[didx],lay*1000.]   # filter within each layer
R=float(os.environ.get('RF','3.2'))
tr=cKDTree(pos); pr=tr.query_pairs(R,output_type='ndarray'); a=np.r_[np.arange(nd),pr[:,0],pr[:,1]]; b=np.r_[np.arange(nd),pr[:,1],pr[:,0]]; w=R-np.linalg.norm(pos[a]-pos[b],axis=1)
m2=pos.copy(); m2[:,0]=-m2[:,0]; D=tr.sparse_distance_matrix(cKDTree(m2),R,output_type='coo_matrix')
Hf=sp.coo_matrix((np.r_[w,R-D.data],(np.r_[a,D.row],np.r_[b,D.col])),shape=(nd,nd)).tocsr(); Hs=np.asarray(Hf.sum(1)).ravel()
proj=lambda x,be,et=.5:(np.tanh(be*et)+np.tanh(be*(x-et)))/(np.tanh(be*et)+np.tanh(be*(1-et)))
dproj=lambda x,be,et=.5:be*(1-np.tanh(be*(x-et))**2)/(np.tanh(be*et)+np.tanh(be*(1-et)))
mon=np.unique(np.r_[fn,np.unique(en[mosf].ravel())])
x=np.full(nd,VF); xo1=x[:,None].copy(); xo2=x[:,None].copy(); low=np.zeros((nd,1)); upp=np.ones((nd,1))
sched={0:1,25:2,50:4,75:8,100:16}; t0=time.time(); J0=None
for it in range(ITERS):
    be=[v for kk,v in sorted(sched.items()) if kk<=it][-1]
    xt=np.asarray(Hf@x).ravel()/Hs; xb=proj(xt,be)
    rho=np.zeros(len(ei)); rho[didx]=xb
    T,ps,A=solve(rho); Tm=T[mon]; Jp=(np.sum(Tm**PN))**(1/PN)
    g=np.zeros(nn); g[mon]=(np.sum(Tm**PN))**(1/PN-1)*Tm**(PN-1)
    lam=ps.solve(A,g); ps.free_memory(everything=True)
    dk=(K_AL-K_AIR)*P*np.maximum(xb,1e-9)**(P-1)
    ce=np.einsum('ij,jk,ik->i',lam[en[didx]],KT,T[en[didx]]); dJ=-dk*ce
    if J0 is None: J0=Jp
    f0=Jp/J0; df0=np.asarray(Hf.T@(dJ/J0*dproj(xt,be)/Hs)).ravel()
    fval=np.array([xb.mean()/VF-1]); dfdx=np.asarray(Hf.T@(np.ones(nd)/nd/VF*dproj(xt,be)/Hs)).ravel()[None,:]
    xn,_,_,_,_,_,_,_,_,low,upp=mmapy.mmasub(1,nd,it+1,x[:,None],np.zeros((nd,1)),np.ones((nd,1)),xo1,xo2,f0,df0[:,None],fval[:,None],dfdx,low,upp,1.,np.zeros((1,1)),1e4*np.ones((1,1)),np.zeros((1,1)),move=0.1)
    xo2=xo1.copy(); xo1=x[:,None].copy(); x=xn.ravel()
    if it%10==0 or it==ITERS-1: print(json.dumps(dict(it=it,beta=be,al_g=round(2*xb.sum()*h**3*2.7e-3,1),front=round(25+T[fn].max(),1),pcb=round(25+T[en[mosf]].max(),1),touch=round(25+T[tn].max(),1),t=round(time.time()-t0))),flush=True)
np.save('rho_%s.npy'%TAG,rho)
# binary verification
rb=np.where(design&(rho>0.5),1.,0.); T,ps,A=solve(rb); ps.free_memory(everything=True)
print(json.dumps(dict(verify=True,al_g=round(2*rb.sum()*h**3*2.7e-3,1),front=round(25+T[fn].max(),1),pcb=round(25+T[en[mosf]].max(),1),touch=round(25+T[tn].max(),1))))
np.save('bin_%s.npy'%TAG,rb)
