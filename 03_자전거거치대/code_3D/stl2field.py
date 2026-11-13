import numpy as np, trimesh, sys, time
m=trimesh.load(sys.argv[1]); t=time.time()
x=np.arange(-26,102+1e-9,0.5); y=np.arange(33,77+1e-9,0.5); z=np.arange(-38,26+1e-9,0.5)
X,Y,Z=np.meshgrid(x[::2],y[::2],z[::2],indexing='ij')   # 1 mm points
pts=np.c_[X.ravel(),Y.ravel(),Z.ravel()]
inside=np.concatenate([m.contains(pts[i:i+20000]) for i in range(0,len(pts),20000)]).reshape(X.shape)
f=np.zeros((len(x),len(y),len(z)),np.float32); f[::2,::2,::2]=inside
np.save(sys.argv[2],f); print('inside frac',inside.mean(),'mass_g',inside.sum()*1.27e-3,'t',round(time.time()-t))
