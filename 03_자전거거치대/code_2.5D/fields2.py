import numpy as np, json, base64
from model2 import *
out={}
for key,tag in [('base','base'),('r1','r1'),('r2','r2'),('r3','r2b')]:
    s=np.load('v2_clean_%s.npy'%tag); res,X=evaluate(s,5.)
    on=X['on']&~post; idx=np.where(on)[0]
    def cen(vec): return vec[G.edof].reshape(-1,8,3).mean(1)
    modes=[]; tips=[]
    for m in range(1):
        c=cen(X['modes'][m]); tip=X['modes'][m].reshape(-1,3)[topn].mean(0); sc=np.abs(c[idx]).max()
        modes=np.round(c[idx]/sc,3).tolist(); tips=np.round(tip/sc,3).tolist()
    U=X['U']
    out[key]=dict(vox=ei[idx].tolist(),vm=np.round(X['vm'][0][idx],3).tolist(),vmy=np.round(X['vm'][1][idx],3).tolist(),
      dz=np.round(np.linalg.norm(cen(U[:,0])[idx],axis=1),4).tolist(),dy=np.round(np.linalg.norm(cen(U[:,1])[idx],axis=1),4).tolist(),
      mode=modes,tip=tips,f=[round(v,1) for v in res['f']],mass=round(res['mass'],1),tipz=round(res['tipz'],3),tipy=round(res['tipy'],3))
    print(key,out[key]['f'],out[key]['mass'],out[key]['tipz'],out[key]['tipy'])
sn={}
for key,tag in [('r1','r1'),('r2','r2'),('r3','r2b')]:
    a=np.load('v2_snaps_%s.npy'%tag)[:,design]   # design elements order: k,j,i -> take j=0 slice
    a=a.reshape(len(a),16,10,40)[:,:,0,:]
    sn[key]=base64.b64encode((np.clip(a,0,1)*255).round().astype(np.uint8).tobytes()).decode()
# final mesh (1mm)
import trimesh
m=trimesh.load('mesh_r2b_1mm.stl'); v=m.vertices.astype(np.float32); fc=m.faces.astype(np.uint32)
mesh=dict(v=base64.b64encode(v.tobytes()).decode(),f=base64.b64encode(fc.tobytes()).decode())
json.dump(dict(D=out,SN=sn,MESH=mesh),open('page2_data.json','w'),separators=(',',':'))
print(len(open('page2_data.json').read()))
