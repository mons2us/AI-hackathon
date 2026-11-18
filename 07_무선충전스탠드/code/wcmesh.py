import numpy as np, json, base64, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from wcfem import *
cm=plt.get_cmap('inferno'); TLO,THI=25.,70.
b64=lambda a: base64.b64encode(np.asarray(a,np.float32).tobytes()).decode()
FACES6={(0,0,1):[(0,0,1),(1,0,1),(1,1,1),(0,0,1),(1,1,1),(0,1,1)],(0,0,-1):[(0,0,0),(1,1,0),(1,0,0),(0,0,0),(0,1,0),(1,1,0)],(1,0,0):[(1,0,0),(1,1,0),(1,1,1),(1,0,0),(1,1,1),(1,0,1)],(-1,0,0):[(0,0,0),(0,0,1),(0,1,1),(0,0,0),(0,1,1),(0,1,0)],(0,1,0):[(0,1,0),(0,1,1),(1,1,1),(0,1,0),(1,1,1),(1,1,0)],(0,-1,0):[(0,0,0),(1,0,0),(1,0,1),(0,0,0),(1,0,1),(0,0,1)]}
def mesh(mask,Tel,colorfn):
    # mirror to full model: x index i -> i (x>=0) and -i-1 (x<0)
    idx=np.where(mask)[0]; S=set()
    cells={}
    for e in idx:
        i,j,k=I[e],J[e],K[e]; cells[(i,j,k)]=e; cells[(-i-1,j,k)]=e
    P=[];Cc=[]
    for (i,j,k),e in cells.items():
        for n,f in FACES6.items():
            if (i+n[0],j+n[1],k+n[2]) in cells: continue
            x,y,z=h*i,Y0+h*j,h*k; c=colorfn(e)
            for a,bb,cc in f: P.append((x+h*a,y+h*bb,z+h*cc)); Cc.append(c)
    return np.array(P),np.array(Cc)
out={}; res={}
b=np.load('bin_w3.npy')
designs={'plastic':np.zeros(len(ei),bool),'fullal':design.copy(),'opt':b}
for nm,al in designs.items():
    rho=np.where(al,1.0,0.0); T,_=thermal(rho,5.0)
    Tel=25+T[en].mean(1)
    mask=al|fixedplastic|pads
    P,Cc=mesh(mask,Tel,lambda e: np.array(cm((Tel[e]-TLO)/(THI-TLO))[:3])**2.2)
    out[nm+'_T']=dict(pos=b64(P),col=b64(Cc))
    P,Cc=mesh(mask,Tel,lambda e: (np.array([0.16,0.64,0.65]) if (al[e] or pads[e]) else np.array([0.92,0.93,0.94]))**2.2)
    out[nm+'_mat']=dict(pos=b64(P),col=b64(Cc))
    res[nm]=dict(al_g=round(2*al.sum()*h**3*2.7e-3,1),Tmax=round(25+T[cn].max(),1))
json.dump(out,open('scene/meshes.json','w')); json.dump(res,open('scene/res.json','w')); print(res)
fig=plt.figure(figsize=(4,0.6),dpi=220); ax=fig.add_axes([0.05,0.5,0.9,0.3]); matplotlib.colorbar.ColorbarBase(ax,cmap=cm,norm=matplotlib.colors.Normalize(TLO,THI),orientation='horizontal'); ax.tick_params(labelsize=7); fig.savefig('../deck/shots/wc_cbar.png',facecolor='white')
