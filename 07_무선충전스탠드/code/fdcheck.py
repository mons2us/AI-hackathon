import numpy as np
exec(open('wcopt.py').read().split('x=np.full(nd,0.3)')[0])
rng=np.random.default_rng(0); rho=np.zeros(len(ei)); rho[didx]=rng.uniform(0.2,0.8,nd)
T,(ps,Af,kel,wf,s)=thermal(rho,Q); lam=np.zeros(nn); lam[freeT]=ps.solve(Af,gT[freeT]); t0=gT@T
d=sens_thermal(rho,T,lam,kel,wf,s)
# pick elements near coil zone (high sensitivity)
cand=didx[np.argsort(-np.abs(d[didx]))[:3]].tolist()+[int(didx[nd//2])]
for e in cand:
    r2=rho.copy(); r2[e]+=1e-4; T2,_=thermal(r2,Q); print(e, d[e], (gT@T2-t0)/1e-4)
