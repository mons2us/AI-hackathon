import numpy as np, json, base64, trimesh, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from skimage import measure
S='/tmp/claude-0/-home-claude/e964ed80-ee1b-5f91-abd3-3081682a3ad7/scratchpad/'
b64=lambda a: base64.b64encode(np.asarray(a,np.float32).tobytes()).decode()
cm=plt.get_cmap('turbo'); VMAX=26.4
def smooth_from_vox(V,X0,Y0,Z0,h=2.,up=2,sig=0.9):
    V=np.asarray(V); mn=V.min(0)-2; mx=V.max(0)+3; g=np.zeros(mx-mn,float); g[tuple((V-mn).T)]=1
    f=ndi.zoom(g,up,order=1); f=ndi.gaussian_filter(f,sig)
    v,fc,_,_=measure.marching_cubes(f,0.5,spacing=(h/up,)*3)
    v=v+np.array([X0,Y0,Z0])+(mn)*h - h/up*0.5 + h/2* (1-1/up)
    m=trimesh.Trimesh(v,fc); trimesh.smoothing.filter_taubin(m,iterations=10); return m
def colorize(m,V,val,X0,Y0,Z0,h=2.):
    cen=np.c_[X0+h*V[:,0]+h/2,Y0+h*V[:,1]+h/2,Z0+h*V[:,2]+h/2]; tri=m.vertices[m.faces].reshape(-1,3)
    _,ii=cKDTree(cen).query(tri); return tri,(cm(np.clip(val[ii]/VMAX,0,1))[:,:3])**2.2
out=json.load(open(S+'deck/scene/meshes.json'))
bj=json.load(open(S+'bike/f3_base.json')); V=np.array(bj['vox']); vm=np.maximum(bj['vm'],bj['vmy'])
m=smooth_from_vox(V,20,bj['Y0'],-16); tri,col=colorize(m,V,vm,20,bj['Y0'],-16)
out['base_smooth_stress']=dict(pos=b64(tri),col=b64(col)); out['base_smooth']=dict(pos=b64(tri))
json.dump(out,open('meshes_bike.json','w')); print('ok',len(m.faces))
