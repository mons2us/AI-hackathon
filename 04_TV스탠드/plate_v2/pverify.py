import numpy as np, sys, os, json
exec(open('plate.py').read().split('x=np.full(nd,0.4)')[0])
from scipy import ndimage as ndi
TAGV=sys.argv[1]; r=np.load('rb_%s.npy'%TAGV)
for thr in (0.5,):
    bmask=(r>thr); lab,n=ndi.label(bmask); keep=np.unique(lab[(attach|pads).reshape(nz,ny)]); keep=keep[keep>0]; bmask=np.isin(lab,keep)
    rb=np.where(bmask.ravel(),1.0,1e-9); U=solve(rb); s,ut,s3=measures(U)
    # von Mises at element centres (plane stress)
    Bc=np.array([[-1,0,1,0,1,0,-1,0],[0,-1,0,-1,0,1,0,1],[-1,-1,-1,1,1,1,1,-1]])/(2*h)
    D=E/(1-nu**2)*np.array([[1,nu,0],[nu,1,0],[0,0,(1-nu)/2]])
    vm=[]
    for c in range(3):
        ue=U[:,c][edof]; st=(D@Bc@ue.T).T; v=np.sqrt(st[:,0]**2-st[:,0]*st[:,1]+st[:,1]**2+3*st[:,2]**2); vm.append(np.percentile(v[bmask.ravel()],99.5))
    mass=bmask.sum()*h*h*t*rho*1e3
    print(json.dumps(dict(tag=TAGV,thr=thr,mass_kg=round(mass,4),sag=round(s,4),utop=round(ut,3),sag_lat=round(s3,4),vm995=[round(v,1) for v in vm],min_width_check=None)))
np.save('bin_%s.npy'%TAGV,bmask)
