import numpy as np, json, base64, sys
from eval3d import *
tag=sys.argv[1]
rb=full_from_half(np.load('xb_%s.npy'%tag)); sd=clean(rb>0.5)
r,X=evaluate(sd); on=X['on']&~post; idx=np.where(on)[0]
cen=lambda v: v[edof].reshape(-1,8,3).mean(1)
c=cen(X['modes'][0]); tip=X['modes'][0].reshape(-1,3)[X['topn']].mean(0); sc=np.abs(c[idx]).max()
U=X['U']
d=dict(X0=x0,Y0=y0,Z0=z0,ny=ny,vox=ei[idx].tolist(),vm=np.round(X['vm'][0][idx],2).tolist(),vmy=np.round(X['vm'][1][idx],2).tolist(),
 dz=np.round(np.linalg.norm(cen(U[:,0])[idx],axis=1),4).tolist(),dy=np.round(np.linalg.norm(cen(U[:,1])[idx],axis=1),4).tolist(),
 mode=np.round(c[idx]/sc,3).tolist(),tip=np.round(tip/sc,3).tolist(),f=[round(v,1) for v in r['f']],mass=round(r['mass'],1),vmax=round(max(r['vmz'],r['vmy']),1),
 pad=[int(v) for v in np.where(pad[idx])[0]])
raw=np.fromfile('snaps_%s.bin'%tag,dtype=np.uint8).reshape(-1,nz,10,nx)
d['snap3']=base64.b64encode(raw.tobytes()).decode(); d['snapn']=int(raw.shape[0])
json.dump(d,open('f_opt_%s.json'%tag,'w'),separators=(',',':')); print(json.dumps({k:d[k] for k in ['f','mass','vmax','snapn']}))
