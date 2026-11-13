import numpy as np, sys, json
from scipy import ndimage
sys.argv=[sys.argv[0]]
exec(open('topo.py').read().split('res=[]')[0])
def clean(rho_e):
    s=(rho_e>0.5).reshape(nz,ny,nx)
    lab,n=ndimage.label(s)  # 6-connectivity
    keep=np.unique(lab[:,:,0]); keep=keep[keep>0]
    return np.isin(lab,keep).ravel().astype(float)
import glob
out=[]
for f in ['rho_base.npy']+sorted(glob.glob('rho_0*.npy'),reverse=True):
    s=clean(np.load(f)); r=evaluate(s,f); r['removed']=int(((np.load(f)>0.5).sum()-s.sum())); out.append(r); print(r)
    np.save(f.replace('rho_','clean_'),s)
json.dump(out,open('res_clean.json','w'),default=float,indent=1)
