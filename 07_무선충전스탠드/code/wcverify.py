import numpy as np, json, sys
from scipy import ndimage as ndi
from wcfem import *
tag=sys.argv[1]; Q=float(sys.argv[2]) if len(sys.argv)>2 else 5.0
r=np.load('rho_%s.npy'%tag); b=(r>0.5)&design
v=(b|allsolid&~design).reshape(nz,ny,nx); lab,n=ndi.label(v); keepl=np.unique(lab[(pads|skin).reshape(nz,ny,nx)]); keepl=keepl[keepl>0]
b&=np.isin(lab,keepl).ravel()
rho=np.where(b,1.0,0.0)
out=dict(tag=tag,al_g=round(2*b.sum()*h**3*2.7e-3,1))
for q in (3.0,5.0):
    T,_=thermal(rho,q); out['Tmax_contact_%gW'%q]=round(25+T[cn].max(),1); out['Tmean_contact_%gW'%q]=round(25+T[cn].mean(),1)
U,_=struct(rho); out['tap_mm']=round(FS[:,1]@U[:,1]/2.5,4); out['weight_sag_mm']=round(-(FS[:,0]@U[:,0])/1.0,4)
np.save('bin_%s.npy'%tag,b); print(json.dumps(out))
