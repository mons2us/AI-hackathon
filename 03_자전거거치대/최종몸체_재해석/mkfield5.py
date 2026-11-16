# 최종 출력 몸체(body_v3 STL)에 같은 해석기 분포(field_body_v3)를 같은 색 척도로 입힘
import numpy as np, json, sys, trimesh
sys.path.insert(0,'.'); from mkfield2 import b64, sample
from matplotlib import cm
def col(m,d,field,lo,hi,shift=0):
    t=np.radians(35); X,Y,Z=m.vertices.T; xp=X*np.cos(t)+Z*np.sin(t)+shift; zp=-X*np.sin(t)+Z*np.cos(t)+shift; yp=Y+shift
    v=sample(d,field,xp,yp,zp); c=cm.turbo(np.clip((v-lo)/(hi-lo),0,1)*0.92+0.04)[:,:3]
    return dict(pos=b64(m.vertices[m.faces].reshape(-1)),col=b64(c[m.faces].reshape(-1)))
d=np.load('../opt/field_body_v3.npz'); body=trimesh.load('../cad/body_v3_world.stl')
plain=lambda k:(lambda mm:dict(pos=b64(mm.vertices[mm.faces].reshape(-1))))(trimesh.load(f'../cad/w_{k}_76.stl'))
for field,lo,hi,pre in [('trms',1.0,3.5,'R'),('vm',0,12,'V')]:
    J={'B':col(body,d,field,lo,hi)}
    for k in ['J','S','P','PH']: J[k]=plain(k)
    json.dump(J,open(f'meshes_{pre}body.json','w'))
J={'B':col(body,d,'T',0,33),'PH':col(trimesh.load('../cad/w_PH_76.stl'),d,'T',0,33)}
for k in ['J','S','P']: J[k]=plain(k)
json.dump(J,open('meshes_Tbody.json','w')); print('ok')
