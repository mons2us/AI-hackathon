import numpy as np, os, sys, struct, trimesh
from scipy import ndimage as ndi
from skimage import measure
TAG=os.environ.get('TAG','a'); OUT=sys.argv[1]
m=np.load('metal_%s.npy'%TAG).astype(np.float32)   # (z,y,x) h=6.25
m=np.pad(m,2); f=ndi.zoom(ndi.gaussian_filter(m,0.6),3,order=1)  # ~2.08 mm
v,fc,_,_=measure.marching_cubes(f,0.5,spacing=(6.25/3,)*3)
v=v[:,::-1]-np.array([2*6.25+250, 2*6.25+150, 2*6.25])*np.array([1,1,1])  # -> (x,y,z) mm
v=v[:,[0,1,2]]; mesh=trimesh.Trimesh(v,fc[:,::-1],process=True)
trimesh.smoothing.filter_taubin(mesh,iterations=10)
mesh.export(OUT); print(dict(watertight=mesh.is_watertight,faces=len(mesh.faces),vol_cm3=round(mesh.volume/1e3,1),mass_kg=round(abs(mesh.volume)*2.7e-6,3),bbox=mesh.bounds.round(1).tolist()))
