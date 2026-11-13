import numpy as np, json, base64, trimesh, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from skimage import measure
from scipy import ndimage as ndi
exec(open('plate_blade.py').read().split('x=np.full(nd,0.4)')[0])
b64=lambda a: base64.b64encode(np.asarray(a,np.float32).tobytes()).decode()
Bc=np.array([[-1,0,1,0,1,0,-1,0],[0,-1,0,-1,0,1,0,1],[-1,-1,-1,1,1,1,1,-1]])/(2*h); Dm=E/(1-nu**2)*np.array([[1,nu,0],[nu,1,0],[0,0,(1-nu)/2]])
cm=plt.get_cmap('turbo'); VM=float(__import__('os').environ.get('VM','12'))
out={}
for tag in ['blade3','blade_base']:
    m2=np.load('bin_%s.npy'%tag); rb=np.where(m2.ravel(),1.0,1e-9); U=solve(rb)
    ue=U[:,1][edof]; st=(Dm@Bc@ue.T).T; vm=np.sqrt(st[:,0]**2-st[:,0]*st[:,1]+st[:,1]**2+3*st[:,2]**2).reshape(nz,ny)
    print(tag,'vm99.5',np.percentile(vm[m2],99.5))
    vol=np.zeros((m2.shape[0]+6,m2.shape[1]+6,16),np.float32); vol[3:-3,3:-3,3:13]=m2[:,:,None]
    f=ndi.gaussian_filter(ndi.zoom(vol,2,order=0),1.2); v,fc,_,_=measure.marching_cubes(f,0.5,spacing=(0.5,0.5,0.5))
    v=v-3; xyz=np.c_[v[:,2]-5,v[:,1]-150,v[:,0]]
    mm=trimesh.Trimesh(xyz,fc[:,::-1])
    if len(mm.faces)>120000: mm=mm.simplify_quadric_decimation(face_count=120000)
    tri=mm.vertices[mm.faces].reshape(-1,3)
    jj=np.clip(((tri[:,1]+150)/h).astype(int),0,ny-1); kk=np.clip((tri[:,2]/h).astype(int),0,nz-1)
    vmf=np.where(m2,vm,0); vmf=ndi.grey_dilation(vmf,size=3)
    col=cm(np.clip(vmf[kk,jj]/VM,0,1))[:,:3]**2.2
    out[tag]=dict(pos=b64(tri)); out[tag+'_S']=dict(pos=b64(tri),col=b64(col))
json.dump(out,open('/tmp/claude-0/-home-claude/e964ed80-ee1b-5f91-abd3-3081682a3ad7/scratchpad/render/meshes_tv.json','w'))
fig=plt.figure(figsize=(4,0.6),dpi=220); ax=fig.add_axes([0.05,0.5,0.9,0.3]); matplotlib.colorbar.ColorbarBase(ax,cmap=cm,norm=matplotlib.colors.Normalize(0,VM),orientation='horizontal'); ax.tick_params(labelsize=7); fig.savefig('/tmp/claude-0/-home-claude/e964ed80-ee1b-5f91-abd3-3081682a3ad7/scratchpad/render/tv_cbar.png',facecolor='white')
