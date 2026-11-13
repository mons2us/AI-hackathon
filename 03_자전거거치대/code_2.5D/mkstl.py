import numpy as np, sys, json
from scipy import ndimage
from skimage import measure
import scipy.sparse as sp
tag=sys.argv[1]; res=float(sys.argv[2]); out=sys.argv[3]
nx,nz=40,16
r=np.load('v2_rho_%s.npy'%tag); s=np.load('v2_clean_%s.npy'%tag)
# 2D density on (k,i) from design layer j=0, masked by clean connectivity
r3=r.reshape(29,10,40); s3=s.reshape(29,10,40)
d2=(r3[:16,0,:]*(s3[:16,0,:]>0.5)) if tag!='base' else s3[:16,0,:]
d2=np.where(s3[:16,0,:]>0.5,np.maximum(d2,0.5001),np.minimum(d2,0.49))
x=np.arange(-26,104+1e-9,res); y=np.arange(40,70+1e-9,res); z=np.arange(-36,26+1e-9,res)
X,Y,Z=np.meshgrid(x,y,z,indexing='ij')
# arm field (element centers at x=20+2i+1, z=-16+2k+1)
ci=(X-21)/2; ck=(Z+15)/2
arm=ndimage.map_coordinates(d2,[ck.ravel(),ci.ravel()],order=1,mode='nearest').reshape(X.shape)
inbox=(X>=20)&(X<=100)&(Z>=-16)&(Z<=16)&(Y>=45)&(Y<=65)
f=np.where(inbox,arm,0.)
inY=(Y>=45)&(Y<=65)
rr=np.sqrt(X**2+Z**2)
solid=np.zeros(X.shape,bool)
solid|=inY&(rr<=23)&(rr>=16.1)                       # clamp ring
solid|=inY&(X>=0)&(X<=22)&(np.abs(Z)<=16)&(rr>=16.1)  # root web to arm
solid|=inY&(np.abs(X)<=8)&(Z<=-14)&(Z>=-34)&(rr>=16.1) # bolt ears
solid|=inY&(X>=80)&(X<=100)&(Z>=15.5)&(Z<=20)          # mount pad
f=np.maximum(f,ndimage.gaussian_filter(solid.astype(float),0.6/res))
# cuts
cut=(np.abs(X)<=1.0)&(Z<0)&(rr>=15)                    # split slit
cut|=((Y-55)**2+(Z+27)**2<=2.25**2)&(np.abs(X)<=9)     # M4 bolt hole along x
cut|=((X-90)**2+(Y-55)**2<=4.0**2)&(Z>=11)             # heat-set insert hole (1/4" or M5)
cut|=rr<16.1
f=np.where(cut,0.,f)
f=np.pad(f,1)
v,fc,_,_=measure.marching_cubes(f,0.5,spacing=(res,res,res))
v+=np.array([x[0],y[0],z[0]])-res
# Taubin smoothing
n=len(v); e=np.r_[fc[:,[0,1]],fc[:,[1,2]],fc[:,[2,0]]]
A=sp.coo_matrix((np.ones(len(e)*2),(np.r_[e[:,0],e[:,1]],np.r_[e[:,1],e[:,0]])),shape=(n,n)).tocsr(); A.data[:]=1
deg=np.asarray(A.sum(1)).ravel(); W=sp.diags(1/deg)@A
for _ in range(8):
    v=v+0.5*(W@v-v); v=v-0.53*(W@v-v)
def write_stl(path,v,fc):
    tri=v[fc]; nrm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]); nrm/=np.linalg.norm(nrm,axis=1,keepdims=True)+1e-12
    data=np.zeros(len(fc),dtype=[('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]); data['n']=nrm; data['v']=tri
    with open(path,'wb') as fo: fo.write(b'FormProof bike mount'.ljust(80,b' ')); fo.write(np.uint32(len(fc)).tobytes()); fo.write(data.tobytes())
write_stl(out,v.astype(np.float32),fc)
np.save(out.replace('.stl','_field.npy'),f[1:-1,1:-1,1:-1].astype(np.float32))
import trimesh
m=trimesh.Trimesh(v,fc,process=True)
print(json.dumps(dict(tris=len(fc),watertight=bool(m.is_watertight),vol_mm3=float(abs(m.volume)),mass_g=float(abs(m.volume)*1.27e-3),bbox=m.bounds.round(1).tolist())))
