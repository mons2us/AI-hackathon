import numpy as np,sys
from scipy import ndimage
from skimage.morphology import skeletonize
ny,nz=20,37
for tag in sys.argv[1:]:
    r=np.load('rprint_%s.npy'%tag); nx=r.size//740; b=(r>0.5).astype(float); np.save('rbin_%s.npy'%tag,b)
    g=b.reshape(nz,ny,nx) if b.size==nx*ny*nz else None
    if g is None: print(tag,'size',b.size); continue
    lab,n=ndimage.label(g); sz=np.bincount(lab.ravel())[1:]
    # mirror for thickness (half model y>=0 at y index 0)
    full=np.concatenate([g[:,::-1],g],1)
    dt=ndimage.distance_transform_edt(full)*2.0
    sk=skeletonize(full>0); t=2*dt[sk]
    print(tag,'grey',int(((r>0.05)&(r<0.95)).sum()),'comps',n,sorted(sz)[-3:],'thick mm p10/50/90',np.percentile(t,[10,50,90]).round(1))
