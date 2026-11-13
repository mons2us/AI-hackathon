import numpy as np, scipy.sparse.linalg as sla, sys, os, json, time
from model2 import *
LAT=float(os.environ.get('LAT','5')); tag=os.environ.get('TAG','x')
def topo(vf,iters=60,p=3.):
    nv=len(ik); x=np.full(nv,vf); rootv=(ik[:,0]==0); x[rootv]=1; snaps=[]
    F=loads(LAT)
    for it in range(iters):
        xp=np.asarray(Hf@x).ravel()/Hs; xp[rootv]=1
        if it%3==0: snaps.append(expand(xp).astype(np.float32))
        r=expand(xp); ke=stiff(r,p)
        Kf=G.K(ke)[free][:,free]; lu=sla.splu(Kf); U=np.zeros((G.ndof,2)); U[free]=lu.solve(F[free])
        dce=np.zeros(G.ne)
        for lc in (0,1):
            ue=U[:,lc][G.edof]; ce=np.einsum('ij,jk,ik->i',ue,G.KE,ue); dce+=-p*np.where(design,r,0)**(p-1)*ce
        dc2=np.bincount(e2v[design],weights=dce[design],minlength=nv)
        dc=np.asarray(Hf@(dc2/Hs)).ravel(); dv=np.asarray(Hf@(np.ones(nv)/Hs)).ravel()
        l1,l2=1e-12,1e12
        while (l2-l1)/(l1+l2)>1e-4:
            lm=0.5*(l1+l2); xn=np.clip(x*np.sqrt(np.maximum(-dc,0)/dv/lm),np.maximum(0,x-0.2),np.minimum(1,x+0.2)); xn[rootv]=1
            if xn.mean()>vf: l1=lm
            else: l2=lm
        x=xn
    xp=np.asarray(Hf@x).ravel()/Hs; xp[rootv]=1; r=expand(xp); snaps.append(r.astype(np.float32))
    np.save('v2_snaps_%s.npy'%tag,np.array(snaps)); np.save('v2_rho_%s.npy'%tag,r); return r
t=time.time(); vf=float(sys.argv[1]); r=topo(vf); s=clean(r); np.save('v2_clean_%s.npy'%tag,s)
res,_=evaluate(s,5.); res.update(tag=tag,vf=vf,LAT=LAT,time=round(time.time()-t)); print(json.dumps(res),flush=True)
