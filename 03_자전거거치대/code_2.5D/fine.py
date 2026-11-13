import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla, sys, time
from fem3d import Grid
E,nu,rho=2000.,0.38,1.27e-9; Mp=0.2e-3; g=9810.
for f in sys.argv[1:]:
    t=time.time(); s2=np.load(f).reshape(15,10,40)
    s=s2.repeat(2,0).repeat(2,1).repeat(2,2).ravel()
    nx,ny,nz,h=80,20,30,1.; G=Grid(nx,ny,nz,h,E,nu)
    fixed=[G.nid(0,j,k) for k in range(nz+1) for j in range(ny+1)]; tip=np.array([G.nid(nx,j,k) for k in range(nz+1) for j in range(ny+1)])
    fd=np.array([[3*n,3*n+1,3*n+2] for n in fixed]).ravel(); free=np.setdiff1d(np.arange(G.ndof),fd)
    # drop dofs of nodes not attached to solid
    used=np.zeros(G.nn,bool); used[(G.edof[s>0][:,::3]//3).ravel()]=True
    free=free[used[free//3]]
    K=G.K(s)[free][:,free]; extra=np.zeros(G.nn); extra[tip]+=Mp/len(tip)
    M=sp.diags(G.Mlump(s*rho*h**3,extra)[free])
    F=np.zeros(G.ndof); F[3*tip+2]=-Mp*5*g/len(tip)
    u=np.zeros(G.ndof); u[free]=sla.spsolve(K,F[free])
    w,_=sla.eigsh(K,k=2,M=M,sigma=0)
    print(f,'1mm: f',np.round(np.sqrt(w)/2/np.pi,1),'defl_z %.3f'%(-u[3*tip+2].mean()),'%.0fs'%(time.time()-t),flush=True)
