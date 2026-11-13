import sys,os,json,numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0,'/tmp/claude-0/-home-claude/e964ed80-ee1b-5f91-abd3-3081682a3ad7/scratchpad/wc'); os.chdir('/tmp/claude-0/-home-claude/e964ed80-ee1b-5f91-abd3-3081682a3ad7/scratchpad/wc')
from scipy.spatial import cKDTree
from PIL import Image
from wcfem import *
OUT='/tmp/claude-0/-home-claude/e964ed80-ee1b-5f91-abd3-3081682a3ad7/scratchpad/render/'
cm=plt.get_cmap('inferno'); TLO,THI=25.,70.
t_dir=np.array([0.,np.cos(ANG),np.sin(ANG)]); nin=np.array([0.,np.sin(ANG),-np.cos(ANG)])
O=np.array([0.,front_y(8.),8.]); SMAX=(HZ-8.)/np.sin(ANG)
b=np.load('bin_w3.npy'); designs={'plastic':np.zeros(len(ei),bool),'fullal':design.copy(),'opt':b}
cen=np.c_[xc,yc,zc]
meta=dict(SMAX=SMAX,O=O.tolist(),P0=P0.tolist(),RKO=RKO,DKO=DKO)
for nm,al in designs.items():
    rho=np.where(al,1.0,0.0); T,_=thermal(rho,5.0); Tel=25+T[en].mean(1)
    # skin texture
    sk=np.where(skin)[0]; tr=cKDTree(cen[sk])
    xs=np.linspace(-HX,HX,240); ss=np.linspace(0,SMAX,360); X,Sg=np.meshgrid(xs,ss)
    P=O+X[...,None]*np.array([1,0,0])+Sg[...,None]*t_dir+1.3*nin; P[...,0]=np.abs(P[...,0])
    _,q=tr.query(P.reshape(-1,3)); img=cm(np.clip((Tel[sk][q]-TLO)/(THI-TLO),0,1))[:,:3].reshape(360,240,3)
    Image.fromarray((img*255).astype(np.uint8)).save(OUT+f'tex_skin_{nm}.png')
    # keep-out back cap texture (disk in plane at depth DKO-1.25)
    kp=np.where(keep)[0]; tr2=cKDTree(cen[kp]); u=np.linspace(-RKO,RKO,200); U,Vv=np.meshgrid(u,u)
    P=P0+U[...,None]*np.array([1,0,0])+Vv[...,None]*t_dir+(DKO-1.3)*nin; P[...,0]=np.abs(P[...,0])
    _,q=tr2.query(P.reshape(-1,3)); img=cm(np.clip((Tel[kp][q]-TLO)/(THI-TLO),0,1))[:,:3].reshape(200,200,3)
    Image.fromarray((img[::-1]*255).astype(np.uint8)).save(OUT+f'tex_keep_{nm}.png')
    meta[nm]=dict(keep_side=list(np.array(cm(np.clip((Tel[kp].mean()-TLO)/(THI-TLO),0,1))[:3])),ledge=list(np.array(cm(np.clip((Tel[ledge].mean()-TLO)/(THI-TLO),0,1))[:3])))
json.dump(meta,open(OUT+'wc_meta.json','w')); print(meta['SMAX'])
