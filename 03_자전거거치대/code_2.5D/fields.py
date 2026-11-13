import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla, json, sys
sys.argv=[sys.argv[0]]
exec(open('topo.py').read().split('res=[]')[0])
out={}
for key,f in [('base','clean_base.npy'),('r1','clean_0.220.npy'),('r2','clean_0.220_L5.npy')]:
    s=np.load(f); ke=np.where(s>0,1.,1e-9)
    K=G.K(ke)[free][:,free]; M=sp.diags(G.Mlump(s*rho*h**3,extra)[free])
    lu=sla.splu(K); U=np.zeros((G.ndof,2)); U[free]=lu.solve(F[free])
    w,V=sla.eigsh(K,k=2,M=M,sigma=0)
    vm=[]
    for lc in (0,1):
        ue=U[:,lc][G.edof]; sig=(G.C@G.B0@ue.T).T
        vm.append(np.sqrt(0.5*((sig[:,0]-sig[:,1])**2+(sig[:,1]-sig[:,2])**2+(sig[:,2]-sig[:,0])**2)+3*(sig[:,3:]**2).sum(1)))
    idx=np.where(s>0)[0]
    def cen(vec):  # element centroid displacement (3)
        ue=vec[G.edof].reshape(-1,8,3); return ue.mean(1)
    modes=[]
    for m in range(2):
        v=np.zeros(G.ndof); v[free]=V[:,m]; c=cen(v)[idx]; c/=np.abs(c).max(); modes.append(np.round(c,3).tolist())
    dz=cen(U[:,0])[idx]; dy=cen(U[:,1])[idx]
    out[key]=dict(vox=ei[idx].tolist(),vm=np.round(vm[0][idx],3).tolist(),vmy=np.round(vm[1][idx],3).tolist(),
        dz=np.round(np.linalg.norm(dz,axis=1),4).tolist(),dy=np.round(np.linalg.norm(dy,axis=1),4).tolist(),
        modes=modes,f=[round(float(x),1) for x in np.sqrt(w)/2/np.pi],mass=round(float(s.sum()*h**3*rho*1e6),1),
        tipz=round(float(-U[3*tipA+2,0].mean()),3),tipy=round(float(U[3*tipA+1,1].mean()),3))
    print(key,out[key]['f'],out[key]['mass'],out[key]['tipz'],out[key]['tipy'],max(out[key]['vm']))
json.dump(out,open('fields.json','w'))
