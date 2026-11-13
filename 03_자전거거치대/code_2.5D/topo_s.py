import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla, time, json, sys
from fem3d import Grid
E,nu,rho=2000.,0.38,1.27e-9; Mp=0.2e-3; g=9810.
h=2.; L,W,H=80.,20.,30.; nx,ny,nz=int(L/h),int(W/h),int(H/h)
G=Grid(nx,ny,nz,h,E,nu)
fixed=[G.nid(0,j,k) for k in range(nz+1) for j in range(ny+1)]
tip=[G.nid(nx,j,k) for k in range(nz+1) for j in range(ny+1)]
fd=np.array([[3*n,3*n+1,3*n+2] for n in fixed]).ravel(); free=np.setdiff1d(np.arange(G.ndof),fd)
tipA=np.array(tip)
F=np.zeros((G.ndof,2)); F[3*tipA+2,0]=-Mp*5*g/len(tip); import os; LAT=float(os.environ.get('LAT','2')); F[3*tipA+1,1]=Mp*LAT*g/len(tip)
extra=np.zeros(G.nn); extra[tip]+=Mp/len(tip)
# passive solid: tip plate (last element column, full face) and clamp layer (first column)
ei=np.array([[i,j,k] for k in range(nz) for j in range(ny) for i in range(nx)])
solid=(ei[:,0]>=nx-1)|(ei[:,0]==0)
# density filter
r=1.6; cen=ei*h; from scipy.spatial import cKDTree
T=cKDTree(ei.astype(float)); pairs=T.query_pairs(r,output_type='ndarray')
ii=np.r_[np.arange(G.ne),pairs[:,0],pairs[:,1]]; jj=np.r_[np.arange(G.ne),pairs[:,1],pairs[:,0]]
d=np.linalg.norm(ei[ii]-ei[jj],axis=1); Hf=sp.coo_matrix((r-d,(ii,jj)),shape=(G.ne,G.ne)).tocsr(); Hs=np.asarray(Hf.sum(1)).ravel()
def evaluate(rho_e,tag):
    s=(rho_e>0.5).astype(float); ke=np.where(s>0,1.,1e-9)
    K=G.K(ke)[free][:,free]; me=s*rho*h**3
    M=sp.diags(G.Mlump(me,extra)[free])
    lu=sla.splu(K); U=np.zeros((G.ndof,2)); U[free]=lu.solve(F[free])
    w,_=sla.eigsh(K,k=3,M=M,sigma=0)
    ue=U[:,0][G.edof]; sig=(G.C@G.B0@ue.T).T
    vm=np.sqrt(0.5*((sig[:,0]-sig[:,1])**2+(sig[:,1]-sig[:,2])**2+(sig[:,2]-sig[:,0])**2)+3*(sig[:,3:]**2).sum(1))
    vm=vm*s; inner=vm[(ei[:,0]>=1)]
    return dict(tag=tag,mass_g=round(me.sum()*1e6,2),f_Hz=[round(x,1) for x in np.sqrt(w)/2/np.pi],
                defl_z_mm=round(-U[3*tipA+2,0].mean(),3),defl_y_mm=round(U[3*tipA+1,1].mean(),3),vm_max_MPa=round(float(inner.max()),1))
def topo(vf,iters=60,p=3.):
    x=np.full(G.ne,vf); x[solid]=1.; snaps=[]
    for it in range(iters):
        xp=np.asarray(Hf@x).ravel()/Hs; xp[solid]=1.
        if it%3==0: snaps.append(xp.astype(np.float32))
        K=G.K(1e-9+xp**p)[free][:,free]; lu=sla.splu(K)
        U=np.zeros((G.ndof,2)); U[free]=lu.solve(F[free])
        dc=np.zeros(G.ne); c=0
        for lc,wgt in ((0,1.),(1,1.)):
            ue=U[:,lc][G.edof]; ce=np.einsum('ij,jk,ik->i',ue,G.KE,ue)
            c+=wgt*((1e-9+xp**p)*ce).sum(); dc+=-wgt*p*xp**(p-1)*ce
        dc=np.asarray(Hf@(dc/Hs)).ravel(); dv=np.asarray(Hf@(np.ones(G.ne)/Hs)).ravel()
        l1,l2=1e-9,1e9
        while (l2-l1)/(l1+l2)>1e-4:
            lm=0.5*(l1+l2); xn=np.clip(x*np.sqrt(np.maximum(-dc,0)/dv/lm),np.maximum(0,x-0.2),np.minimum(1,x+0.2)); xn[solid]=1
            if xn.mean()>vf: l1=lm
            else: l2=lm
        x=xn
    xp=np.asarray(Hf@x).ravel()/Hs; xp[solid]=1.
    snaps.append(xp.astype(np.float32)); np.save('snaps_%.3f_L%g.npy'%(vf,LAT),np.array(snaps))
    return xp
res=[]
base=np.zeros(G.ne); base[(ei[:,2]>=4)&(ei[:,2]<8)]=1; base[solid]=1  # 8mm thick bar at mid-height + plates
# baseline: bar centered vertically: z 11..19mm -> elements 6..9 (2mm)  use center
base=np.zeros(G.ne); base[(ei[:,2]>=5)&(ei[:,2]<9)]=1; base[solid]=1
r0=evaluate(base,'처음 설계 (단순 막대)'); print(r0,flush=True); res.append(r0); np.save('rho_base.npy',base)
for vf in [float(v) for v in sys.argv[1:]]:
    t=time.time(); xp=topo(vf); np.save('rho_%.3f_L%g.npy'%(vf,LAT),xp)
    r1=evaluate(xp,'재설계 vf=%.3f'%vf); r1['time_s']=round(time.time()-t,1); print(r1,flush=True); res.append(r1)
json.dump(res,open('res_L%g.json'%LAT,'w'),ensure_ascii=False,indent=1)
