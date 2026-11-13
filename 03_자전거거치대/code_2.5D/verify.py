import numpy as np, scipy.sparse.linalg as sla, time
from fem3d import Grid
E,nu,rho=2000.,0.38,1.27e-9; L,b,hh=80.,20.,8.; Mp=0.2e-3; g=9810.; a=5*g
I=b*hh**3/12; k=3*E*I/L**3; mb=b*hh*L*rho
print('theory: tip defl %.3f mm, f1 %.1f Hz, beam mass %.1f g'%(Mp*a/k, np.sqrt(k/(Mp+0.2357*mb))/2/np.pi, mb*1e6))
for h in (2.,1.,0.5) if False else (2.,1.):
    t=time.time(); nx,ny,nz=int(L/h),int(b/h),int(hh/h); G=Grid(nx,ny,nz,h,E,nu)
    K=G.K(np.ones(G.ne)); fixed=[]; tip=[]
    for kk in range(nz+1):
        for j in range(ny+1):
            fixed.append(G.nid(0,j,kk)); tip.append(G.nid(nx,j,kk))
    fd=np.array([[3*n,3*n+1,3*n+2] for n in fixed]).ravel(); free=np.setdiff1d(np.arange(G.ndof),fd)
    extra=np.zeros(G.nn); extra[tip]+=Mp/len(tip)
    M=G.Mlump(np.full(G.ne,rho*h**3),extra)
    F=np.zeros(G.ndof); F[3*np.array(tip)+2]=-Mp*a/len(tip)
    u=np.zeros(G.ndof); Kf=K[free][:,free]; u[free]=sla.spsolve(Kf,F[free])
    w,_=sla.eigsh(Kf,k=3,M=__import__('scipy.sparse',fromlist=['diags']).diags(M[free]),sigma=0)
    print('FEM h=%g: tip defl %.3f mm, f %s Hz, %.1fs'%(h,-u[3*np.array(tip)+2].mean(),np.round(np.sqrt(w)/2/np.pi,1),time.time()-t))
