"""gen_frame 미리보기: python3 gen_frame_render.py 출력.png [열 수]  (현재 폴더의 occ.npy · prm.json, /tmp/meta_g{0,1,2}.npz 필요)"""
import sys, json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from skimage import measure
import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import gen_frame as G
meta={g:dict(np.load(f'/tmp/meta_g{g}.npz')) for g in range(3)}
O=np.load('occ.npy'); P=json.load(open('prm.json'))
t=np.radians(35); ct,st=np.cos(t),np.sin(t)
def mesh(mask,m):
    nx,ny,nz=int(m['nx']),int(m['ny']),int(m['nz'])
    A=mask.reshape(nz,ny,nx).astype(float); A=np.concatenate([A[:,::-1],A],1); A=np.pad(A,1)
    if A.max()<0.5: return None
    v,f,_,_=measure.marching_cubes(A,0.5); v=v-1
    z=-36+2*v[:,0]+0; y=2*v[:,1]-2*ny; x=-24+2*v[:,2]
    X=x*ct-z*st; Z=x*st+z*ct
    return np.c_[X,y,Z][f]
fams=list(G.FAMILIES); cols=int(sys.argv[2]) if len(sys.argv)>2 else 7
sel=[i for i,p in enumerate(P) if (i%14)<cols]
fig=plt.figure(figsize=(cols*3.2,len(fams)*3.0))
for i in sel:
    o,p=O[i],P[i]
    m=meta[p['grip']]; occ=np.unpackbits(o)[:len(m['xc'])].astype(bool)
    r=fams.index(p['family']); c=i%cols
    ax=fig.add_subplot(len(fams),cols,r*cols+c+1,projection='3d')
    for mask,colr in ((occ,(0.93,0.55,0.25)),(m['solid'].astype(bool),(0.45,0.47,0.52))):
        T=mesh(mask,m)
        if T is None: continue
        n=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]); n/=np.linalg.norm(n,axis=1,keepdims=True)+1e-12
        sh=0.35+0.65*np.clip(n@np.array([0.35,-0.55,0.75]),0,1)
        ax.add_collection3d(Poly3DCollection(T,facecolors=np.c_[sh[:,None]*np.array(colr),np.ones(len(T))],linewidths=0))
    ax.set_xlim(-35,125); ax.set_ylim(-45,45); ax.set_zlim(-35,105); ax.set_box_aspect((160,90,140)); ax.view_init(14,-62); ax.set_axis_off()
    mass=occ.sum()*8*1.27e-3*2
    ax.set_title(f"{G.FAMILY_KO[p['family']]} G{p['grip']} {G.SECTION_KO[p['section']]}\nt{p['t']:.0f} w{p['w']:.0f} · 몸체 {mass:.0f} g",fontsize=10)
plt.subplots_adjust(0,0,1,0.97,-0.05,0.18); plt.savefig(sys.argv[1] if len(sys.argv)>1 else 'sheet.png',dpi=70)
