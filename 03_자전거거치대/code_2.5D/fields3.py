import numpy as np, json, base64, sys
from model2 import *
key,tag,snap=sys.argv[1],sys.argv[2],sys.argv[3]
PEAK=48.5
s=np.load('v2_clean_%s.npy'%tag); res,X=evaluate(s,5.)
on=X['on']&~post; idx=np.where(on)[0]
cen=lambda vec: vec[G.edof].reshape(-1,8,3).mean(1)
c=cen(X['modes'][0]); tip=X['modes'][0].reshape(-1,3)[topn].mean(0); sc=np.abs(c[idx]).max()
U=X['U']; vmx=[]
for lc in (0,1):
    ue=U[:,lc][G.edof]; sg=(G.C@G.B0@ue.T).T*(PEAK/5.)
    vm=np.sqrt(0.5*((sg[:,0]-sg[:,1])**2+(sg[:,1]-sg[:,2])**2+(sg[:,2]-sg[:,0])**2)+3*(sg[:,3:]**2).sum(1)); vmx.append(vm)
ok=on&~root
d=dict(Y0=Y0,ny=ny,KD=KD,vox=ei[idx].tolist(),vm=np.round(vmx[0][idx],2).tolist(),vmy=np.round(vmx[1][idx],2).tolist(),
  dz=np.round(np.linalg.norm(cen(U[:,0])[idx],axis=1)*(PEAK/5.),4).tolist(),dy=np.round(np.linalg.norm(cen(U[:,1])[idx],axis=1)*(PEAK/5.),4).tolist(),
  mode=np.round(c[idx]/sc,3).tolist(),tip=np.round(tip/sc,3).tolist(),f=[round(v,1) for v in res['f']],mass=round(res['mass'],1),
  vmax=round(float(max(vmx[0][ok].max(),vmx[1][ok].max())),1))
if snap!='-':
    a=np.load('v2_snaps_%s.npy'%snap)[:,design].reshape(-1,KD,ny,nx)[:,:,0,:]
    d['snap']=base64.b64encode((np.clip(a,0,1)*255).round().astype(np.uint8).tobytes()).decode()
json.dump(d,open('f3_%s.json'%key,'w'),separators=(',',':')); print(key,d['f'],d['mass'],d['vmax'])
