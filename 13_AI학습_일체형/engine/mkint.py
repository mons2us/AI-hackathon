# 일체형 결과(rprint) → 세계 좌표 메쉬 (STL + three.js JSON)
import numpy as np, trimesh, json, base64, sys
from skimage import measure
from scipy import ndimage
def mesh(rfile,tilt=35.,iso=0.45,sig=0.6):
    r=np.load(rfile); ny,nz=20,37; nx=r.size//(ny*nz); r=r.reshape(nz,ny,nx); full=np.concatenate([r[:,::-1],r],1)
    v=ndimage.gaussian_filter(np.pad(full,1),sig); vs,f,_,_=measure.marching_cubes(v,iso,spacing=(2,2,2))
    z=vs[:,0]-2-36; y=vs[:,1]-2-40; x=vs[:,2]-2-24; t=np.radians(tilt)
    m=trimesh.Trimesh(np.c_[x*np.cos(t)-z*np.sin(t),y,x*np.sin(t)+z*np.cos(t)],f)
    if m.volume<0: m.invert()
    return m
def b64(m): return base64.b64encode(m.vertices[m.faces].reshape(-1).astype(np.float32).tobytes()).decode()
if __name__=='__main__':
    out={}
    for i in range(1,len(sys.argv)-1,2):
        m=mesh(sys.argv[i]); out[sys.argv[i+1]]=dict(pos=b64(m)); print(sys.argv[i],round(m.volume*1.27e-3,1),'g')
        m.export(sys.argv[i].replace('.npy','.stl'))
    json.dump(out,open(sys.argv[-1],'w'))
