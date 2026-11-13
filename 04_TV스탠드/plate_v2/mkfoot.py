import numpy as np, json, base64, trimesh
from skimage import measure
from scipy import ndimage as ndi
b64=lambda a: base64.b64encode(np.asarray(a,np.float32).tobytes()).decode()
out={}
for tag in ['c','T_web40']:
    b=np.load('bin_%s.npy'%tag).astype(float)          # (nz,ny) 1 mm
    vol=np.zeros((b.shape[0]+4,b.shape[1]+4,14)); vol[2:-2,2:-2,2:12]=b[:,:,None]   # (z,y,x) thickness 10
    f=ndi.gaussian_filter(vol,0.6); v,fc,_,_=measure.marching_cubes(f,0.5)
    v=v-np.array([2,2,2]); xyz=np.c_[v[:,2]-5, v[:,1]-150, v[:,0]]                   # x centred, y -150..150, z 0..120
    m=trimesh.Trimesh(xyz,fc[:,::-1]); trimesh.smoothing.filter_taubin(m,iterations=8)
    if tag=='c': m.export('../out_tv_foot_c.stl')
    out[tag]=dict(pos=b64(m.vertices[m.faces].reshape(-1,3))); print(tag,len(m.faces),m.is_watertight,round(abs(m.volume)*2.7e-3,1),'g')
json.dump(out,open('scene/meshes.json','w'))
