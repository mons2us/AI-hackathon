import sys,os,json,base64,numpy as np,trimesh, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0,'/tmp/claude-0/-home-claude/e964ed80-ee1b-5f91-abd3-3081682a3ad7/scratchpad/wc'); os.chdir('/tmp/claude-0/-home-claude/e964ed80-ee1b-5f91-abd3-3081682a3ad7/scratchpad/wc')
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from skimage import measure
from wcfem import *
b64=lambda a: base64.b64encode(np.asarray(a,np.float32).tobytes()).decode()
cm=plt.get_cmap('inferno'); TLO,THI=25.,70.
def full(mask):  # (nz,ny,nx) half -> mirrored (nz,ny,2nx), x from -HX..HX
    a=mask.reshape(nz,ny,nx); return np.concatenate([a[:,:,::-1],a],2)
def smooth(occ,up=4,sig=2.0,order=0):
    g=np.pad(occ.astype(np.float32),3); f=ndi.gaussian_filter(ndi.zoom(g,up,order=order),sig)
    v,fc,_,_=measure.marching_cubes(f,0.5,spacing=(h/up,)*3)   # (z,y,x)
    v=v-3*h; xyz=np.c_[v[:,2]-HX, v[:,1]+Y0, v[:,0]]
    return trimesh.Trimesh(xyz,fc[:,::-1])
cenx=np.r_[-(xc[::-1]),xc]  # not used
out={}; res={}
b=np.load('bin_w3.npy')
designs={'plastic':np.zeros(len(ei),bool),'fullal':design.copy(),'opt':b}
plastic_mask=full(fixedplastic)
mp=smooth(plastic_mask,sig=2.5,order=1); 
for nm,al in designs.items():
    rho=np.where(al,1.0,0.0); T,_=thermal(rho,5.0); Tel=25+T[en].mean(1)
    almask=full(al|pads); 
    meshes={'al':smooth(almask),'pl':mp}
    # element centres (full)
    Tf=full(Tel); kk,jj,ii=np.where(full(al|pads|fixedplastic)); cen=np.c_[(ii+0.5)*h-HX,Y0+(jj+0.5)*h,(kk+0.5)*h]; tv=Tf[kk,jj,ii]
    tree=cKDTree(cen)
    for part,m in meshes.items():
        if len(m.faces)>90000: m=m.simplify_quadric_decimation(face_count=90000)
        tri=m.vertices[m.faces].reshape(-1,3); _,q=tree.query(tri); col=np.array(cm(np.clip((tv[q]-TLO)/(THI-TLO),0,1)))[:,:3]**2.2
        out[f'{nm}_{part}']=dict(pos=b64(tri)); out[f'{nm}_{part}_T']=dict(pos=b64(tri),col=b64(col))
    res[nm]=dict(al_g=round(2*al.sum()*h**3*2.7e-3,1),Tmax=round(25+T[cn].max(),1))
    if nm=='opt': meshes['al'].export('/tmp/claude-0/-home-claude/e964ed80-ee1b-5f91-abd3-3081682a3ad7/scratchpad/render/wc_opt_al.stl')
json.dump(out,open('/tmp/claude-0/-home-claude/e964ed80-ee1b-5f91-abd3-3081682a3ad7/scratchpad/render/meshes_wc.json','w')); print(res)
