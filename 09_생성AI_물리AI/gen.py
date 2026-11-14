# 거치대 계열 형상 생성기: 클램프 링 -> 받침판을 잇는 3D 부재 조합 (2 mm 격자, eval3d 와 같은 영역)
import numpy as np, sys, os
HV=os.environ.get('GEN_HEAVY')=='1'
sys.path.insert(0,'../opt')
from eval3d import xc,yc,zc,design,solid,post,clean,nx,ny,nz
def seg_dist(P,a,b):
    ab=b-a; t=np.clip(((P-a)@ab)/(ab@ab+1e-9),0,1); return np.linalg.norm(P-(a+t[:,None]*ab),axis=1)
P=np.c_[xc,yc,zc]
def sample(rng):
    occ=np.zeros(len(P),bool)
    W=rng.uniform(10,20) if HV else rng.uniform(5,19)
    taper=rng.uniform(0.4,1.0)          # 받침판 쪽 폭 비율
    nch=2 if HV else rng.integers(1,3)
    ring=lambda th: np.array([22*np.cos(th),55,22*np.sin(th)])
    pad=lambda u,z: np.array([80+20*u,55,z])
    segs=[]
    a_top=ring(np.radians(rng.uniform(20,80))); b_top=pad(rng.uniform(0,0.6),rng.uniform(15,19))
    segs.append((a_top,b_top,rng.uniform(7,16) if HV else rng.uniform(4,14)))
    if nch==2:
        a_bot=ring(np.radians(rng.uniform(-40,15))); b_bot=pad(rng.uniform(0,0.5),rng.uniform(6,15))
        segs.append((a_bot,b_bot,rng.uniform(7,16) if HV else rng.uniform(4,14)))
        for k in range(rng.integers(0,4)):     # 웹
            s1,s2=rng.uniform(0.1,0.9,2)
            p=a_top+s1*(b_top-a_top); q=a_bot+s2*(b_bot-a_bot); segs.append((p,q,rng.uniform(3,8)))
    else:
        # 단일 팔 + 하부 보강 리브 (선택)
        if rng.random()<0.6:
            a=ring(np.radians(rng.uniform(-30,20))); s=rng.uniform(0.2,0.8); segs.append((a,a_top+s*(b_top-a_top),rng.uniform(4,10)))
    side=(rng.random()<0.4) and not (HV and rng.random()<0.5)               # 양쪽 레일형 (가운데 비움)
    for a,b,t in segs:
        d=seg_dist(P[:,[0,2]],a[[0,2]],b[[0,2]])
        s=np.clip((P[:,0]-a[0])/max(b[0]-a[0],1e-3),0,1); w=W*(1-(1-taper)*s)
        ay=np.abs(P[:,1]-55)
        inside=(d<=t/2)&(ay<=w)
        if side: inside&=ay>=w-rng.uniform(4,8)
        occ|=inside
    return clean(occ&design)
if __name__=='__main__':
    rng=np.random.default_rng(0); import time
    for i in range(5):
        o=sample(rng); print(o.sum()*8*1.27e-3)
