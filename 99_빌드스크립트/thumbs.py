import numpy as np, trimesh, json, sys, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
L=np.array([0.4,-0.6,0.7]); L/=np.linalg.norm(L)
def setup():
    fig=plt.figure(figsize=(6,4.5),dpi=150); ax=fig.add_axes([0,0,1,1],projection='3d'); ax.set_axis_off()
    ax.set_xlim(-25,105); ax.set_ylim(25,85); ax.set_zlim(-40,30); ax.set_box_aspect((130,60,70)); ax.set_proj_type('ortho'); ax.view_init(22,-58); return fig,ax
def mesh(path,out):
    m=trimesh.load(path); tri=m.vertices[m.faces]; sh=0.25+0.75*np.clip(m.face_normals@L,0,1)
    fig,ax=setup(); ax.add_collection3d(Poly3DCollection(tri,facecolors=np.clip(np.c_[0.12+0.45*sh,0.25+0.45*sh,0.55+0.4*sh],0,1),linewidths=0)); fig.savefig(out,facecolor='white'); plt.close(fig)
def vox(js,out,X0=20,Y0=None,Z0=-16):
    d=json.load(open(js)); V=np.array(d['vox']); Y0=d['Y0']
    fig,ax=setup(); tris=[]
    for i,j,k in V:
        x,y,z=X0+2*i,Y0+2*j,Z0+2*k
        for f in [[(0,0,1),(1,0,1),(1,1,1),(0,1,1)],[(0,0,0),(1,0,0),(1,0,1),(0,0,1)],[(1,0,0),(1,1,0),(1,1,1),(1,0,1)]]:
            tris.append([(x+2*a,y+2*b,z+2*c) for a,b,c in f])
    tris=np.array(tris); n=np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0]); n/=np.linalg.norm(n,axis=1,keepdims=True); sh=0.25+0.75*np.clip(n@L,0,1)
    ax.add_collection3d(Poly3DCollection(tris,facecolors=np.clip(np.c_[0.12+0.45*sh,0.25+0.45*sh,0.55+0.4*sh],0,1),linewidths=0))
    # clamp ring for reference
    th=np.linspace(0,2*np.pi,60); 
    for yy in (45,65): ax.plot(23*np.cos(th),np.full_like(th,yy),23*np.sin(th),color='#7d8a99',lw=1.2)
    fig.savefig(out,facecolor='white'); plt.close(fig)
kind=sys.argv[1]
if kind=='mesh': mesh(sys.argv[2],sys.argv[3])
else: vox(sys.argv[2],sys.argv[3])
from PIL import Image, ImageOps
im=Image.open(sys.argv[3]).convert('RGB'); bb=ImageOps.invert(im).getbbox(); im=im.crop((max(0,bb[0]-20),max(0,bb[1]-20),bb[2]+20,bb[3]+20))
W,H=800,520; c=Image.new('RGB',(W,H),'white'); im.thumbnail((W-20,H-20)); c.paste(im,((W-im.width)//2,(H-im.height)//2)); c.save(sys.argv[3])
