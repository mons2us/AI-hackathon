import numpy as np, json, base64, trimesh, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
from skimage import measure
from scipy import ndimage as ndi
cm=plt.get_cmap('turbo'); VMAX=26.4
b64=lambda a: base64.b64encode(np.asarray(a,np.float32).tobytes()).decode()
FACES={(0,0,1):[(0,0,1),(1,0,1),(1,1,1),(0,0,1),(1,1,1),(0,1,1)],(0,0,-1):[(0,0,0),(1,1,0),(1,0,0),(0,0,0),(0,1,0),(1,1,0)],(1,0,0):[(1,0,0),(1,1,0),(1,1,1),(1,0,0),(1,1,1),(1,0,1)],(-1,0,0):[(0,0,0),(0,0,1),(0,1,1),(0,0,0),(0,1,1),(0,1,0)],(0,1,0):[(0,1,0),(0,1,1),(1,1,1),(0,1,0),(1,1,1),(1,1,0)],(0,-1,0):[(0,0,0),(1,0,0),(1,0,1),(0,0,0),(1,0,1),(0,0,1)]}
def voxmesh(V,val,X0,Y0,Z0,h=2.):
    S={tuple(v):i for i,v in enumerate(V)}; P=[];Cc=[]
    for n,f in FACES.items():
        for (i,j,k),q in S.items():
            if (i+n[0],j+n[1],k+n[2]) in S: continue
            x,y,z=X0+h*i,Y0+h*j,Z0+h*k; c=np.array(cm(min(val[q]/VMAX,1))[:3])**2.2
            for a,bb,cc in f: P.append((x+h*a,y+h*bb,z+h*cc)); Cc.append(c)
    return np.array(P),np.array(Cc)
out={}
# base arm (stress)
bj=json.load(open('bike/f3_base.json')); V=np.array(bj['vox']); vm=np.maximum(bj['vm'],bj['vmy'])
P,Cc=voxmesh(V,vm,20,bj['Y0'],-16); out['base_stress']=dict(pos=b64(P),col=b64(Cc))
P,_=voxmesh(V,vm*0,20,bj['Y0'],-16); out['base_plain']=dict(pos=b64(P))
# clamp for base (1 mm grid, marching cubes)
x=np.arange(-30,31); y=np.arange(40,71); z=np.arange(-40,31); X,Y,Z=np.meshgrid(x,y,z,indexing='ij'); R=np.sqrt(X**2+Z**2)
cl=((R>=16.1)&(R<21.5)&(np.abs(Y-55)<10))|((np.abs(X)>1)&(np.abs(X)<9)&(Z>-34)&(Z<-14)&(np.abs(Y-55)<10)); cl&=~((np.abs(X)<=1)&(Z<0)); cl&=R>=16.1
v,f,_,_=measure.marching_cubes(ndi.gaussian_filter(cl.astype(float),0.7),0.5); v=v+np.array([x[0],y[0],z[0]])
out['clamp']=dict(pos=b64(v[f].reshape(-1,3)))
# final STL with stress colors
m=trimesh.load('out/FormProof_자전거거치대_v5.stl'); m=m.simplify_quadric_decimation(face_count=60000) if hasattr(m,'simplify_quadric_decimation') else m
dj=json.load(open('opt/f_opt_d.json')); Vd=np.array(dj['vox']); vmd=np.maximum(dj['vm'],dj['vmy'])
cen=np.c_[dj['X0']+2*Vd[:,0]+1,dj['Y0']+2*Vd[:,1]+1,dj['Z0']+2*Vd[:,2]+1]
tri=m.vertices[m.faces].reshape(-1,3); _,ii=cKDTree(cen).query(tri); col=cm(np.clip(vmd[ii]/VMAX,0,1))[:,:3]**2.2
out['final']=dict(pos=b64(tri)); out['final_stress']=dict(pos=b64(tri),col=b64(col))
P,Cc=voxmesh(Vd,vmd,dj['X0'],dj['Y0'],dj['Z0']); out['final_vox_stress']=dict(pos=b64(P),col=b64(Cc))
json.dump(out,open('deck/scene/meshes.json','w')); print({k:len(v['pos']) for k,v in out.items()}, len(m.faces))
