import numpy as np, sys, json
from scipy import ndimage
sys.argv=[sys.argv[0]]
exec(open('topo.py').read().split('res=[]')[0])
def clean(rho_e):
    s=(rho_e>0.5).reshape(nz,ny,nx); lab,n=ndimage.label(s); keep=np.unique(lab[:,:,0]); keep=keep[keep>0]
    return np.isin(lab,keep).ravel().astype(float)
for f in ['rho_0.220_L5.npy','rho_0.220_L10.npy']:
    s=clean(np.load(f)); np.save(f.replace('rho_','clean_'),s); print(f,evaluate(s,f))
