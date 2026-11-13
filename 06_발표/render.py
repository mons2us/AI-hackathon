import numpy as np, json, trimesh, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image, ImageOps
L=np.array([0.35,-0.55,0.75]); L/=np.linalg.norm(L); cmap=plt.get_cmap('turbo'); VMAX=26.4
def setup():
    fig=plt.figure(figsize=(7,4.6),dpi=220); ax=fig.add_axes([0,0,1,1],projection='3d'); ax.set_axis_off()
    ax.set_xlim(-28,104); ax.set_ylim(22,88); ax.set_zlim(-42,30); ax.set_box_aspect((132,66,72)); ax.set_proj_type('ortho'); ax.view_init(24,-60); return fig,ax
def crop(out):
    im=Image.open(out).convert('RGB'); bb=ImageOps.invert(im).getbbox(); im=im.crop((max(0,bb[0]-30),max(0,bb[1]-30),bb[2]+30,bb[3]+30)); im.save(out)
FACES={(0,0,1):[(0,0,1),(1,0,1),(1,1,1),(0,1,1)],(0,0,-1):[(0,0,0),(0,1,0),(1,1,0),(1,0,0)],(1,0,0):[(1,0,0),(1,1,0),(1,1,1),(1,0,1)],(-1,0,0):[(0,0,0),(0,0,1),(0,1,1),(0,1,0)],(0,1,0):[(0,1,0),(0,1,1),(1,1,1),(1,1,0)],(0,-1,0):[(0,0,0),(1,0,0),(1,0,1),(0,0,1)]}
def vox(V,val,X0,Y0,Z0,out,ring=False,gray=None):
    V=np.asarray(V); S={tuple(v):i for i,v in enumerate(V)}; tris=[];cols=[]
    for n,f in FACES.items():
        sh=0.45+0.55*max(0,np.dot(n,L))
        for (i,j,k),q in S.items():
            if (i+n[0],j+n[1],k+n[2]) in S: continue
            x,y,z=X0+2*i,Y0+2*j,Z0+2*k; tris.append([(x+2*a,y+2*b,z+2*c) for a,b,c in f])
            c=np.array(cmap(min(val[q]/VMAX,1))[:3]) if gray is None or not gray[q] else np.array([0.55,0.58,0.62])
            cols.append(np.clip(c*sh,0,1))
    fig,ax=setup(); ax.add_collection3d(Poly3DCollection(np.array(tris),facecolors=cols,linewidths=0))
    if ring:
        th=np.linspace(0,2*np.pi,80)
        for yy in (45,65): ax.plot(20.5*np.cos(th),np.full_like(th,yy),20.5*np.sin(th),color='#7d8a99',lw=1.4)
    fig.savefig(out,facecolor='white'); plt.close(fig); crop(out)
def stl(path,out,color=(0.50,0.80,0.82)):
    m=trimesh.load(path); tri=m.vertices[m.faces]; sh=0.45+0.55*np.abs(m.face_normals@L)
    fig,ax=setup(); ax.add_collection3d(Poly3DCollection(tri,facecolors=np.clip(np.outer(sh,color)+0.08,0,1),linewidths=0)); fig.savefig(out,facecolor='white'); plt.close(fig); crop(out)
b=json.load(open('bike/f3_base.json')); vox(b['vox'],np.maximum(b['vm'],b['vmy']),20,b['Y0'],-16,'deck/shots/r_base_stress.png',ring=True)
d=json.load(open('opt/f_opt_d.json')); vm=np.maximum(d['vm'],d['vmy']); 
vox(d['vox'],vm,d['X0'],d['Y0'],d['Z0'],'deck/shots/r_final_stress.png')
stl('out/FormProof_자전거거치대_v5.stl','deck/shots/r_final_stl.png')
# colorbar
fig=plt.figure(figsize=(4,0.6),dpi=220); ax=fig.add_axes([0.05,0.5,0.9,0.3]); matplotlib.colorbar.ColorbarBase(ax,cmap=cmap,norm=matplotlib.colors.Normalize(0,VMAX),orientation='horizontal'); ax.tick_params(labelsize=7); fig.savefig('deck/shots/r_cbar.png',facecolor='white',transparent=False); plt.close(fig)
print('ok')
