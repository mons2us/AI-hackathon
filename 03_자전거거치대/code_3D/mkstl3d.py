import numpy as np, sys, json
from scipy import ndimage
from skimage import measure
import scipy.sparse as sp
from eval3d import *
src,res,out=sys.argv[1],float(sys.argv[2]),sys.argv[3]
rbh=np.load(src); rbf=full_from_half(rbh); keep=clean(rbf>0.5)
keepd=ndimage.binary_dilation(keep.reshape(nz,ny,nx),iterations=1).ravel()
fe=np.where(keep,1.,0.); fe[solid]=1.; fe[post]=0.
F3=fe.reshape(nz,ny,nx)
x=np.arange(-26,102+1e-9,res); y=np.arange(33,77+1e-9,res); z=np.arange(-38,26+1e-9,res)
X,Y,Z=np.meshgrid(x,y,z,indexing='ij')
ci=(X-x0-1)/2; cj=(Y-y0-1)/2; ck=(Z-z0-1)/2
f=ndimage.map_coordinates(F3,[np.round(ck.ravel()),np.round(cj.ravel()),np.round(ci.ravel())],order=0,mode='constant',cval=0.).reshape(X.shape)
f=ndimage.gaussian_filter(f,0.5/res)
rr=np.sqrt(X**2+Z**2)
cut=(rr<16.1)|((np.abs(X)<=1.0)&(Z<0)&(rr>=15))
for yb in (55-5,55+5): cut|=((Y-yb)**2+(Z+27)**2<=2.25**2)&(np.abs(X)<=10)
cut|=((X-90)**2+(Y-55)**2<=4.0**2)&(Z>=11)
f=np.where(cut,0.,f); f=np.pad(f,1)
ISO=float(__import__('os').environ.get('ISO','0.5')); v,fc,_,_=measure.marching_cubes(f,ISO,spacing=(res,res,res)); v+=np.array([x[0],y[0],z[0]])-res
n=len(v); e=np.r_[fc[:,[0,1]],fc[:,[1,2]],fc[:,[2,0]]]
A=sp.coo_matrix((np.ones(len(e)*2),(np.r_[e[:,0],e[:,1]],np.r_[e[:,1],e[:,0]])),shape=(n,n)).tocsr(); A.data[:]=1
W=sp.diags(1/np.asarray(A.sum(1)).ravel())@A
for _ in range(8): v=v+0.5*(W@v-v); v=v-0.53*(W@v-v)
tri=v[fc].astype(np.float32); nrm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]); nrm/=np.linalg.norm(nrm,axis=1,keepdims=True)+1e-12
data=np.zeros(len(fc),dtype=[('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]); data['n']=nrm; data['v']=tri
with open(out,'wb') as fo: fo.write(b'FormProof bike mount 3D'.ljust(80,b' ')); fo.write(np.uint32(len(fc)).tobytes()); fo.write(data.tobytes())
np.save(out.replace('.stl','_field.npy'),f[1:-1,1:-1,1:-1].astype(np.float32))
import trimesh
m=trimesh.Trimesh(v,fc,process=True)
print(json.dumps(dict(tris=len(fc),watertight=bool(m.is_watertight),vol=float(abs(m.volume)),mass_g=float(abs(m.volume)*1.27e-3),bbox=m.bounds.round(1).tolist())))
