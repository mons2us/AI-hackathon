# 일체형 거치대 계열 형상 생성기 (폰 정렬 좌표, 절반 모델 y>=0): 클램프 링 -> 집게 하우징 · 위 레일 · 아래 걸이를 잇는 부재 조합
import numpy as np
from scipy import ndimage
def seg_dist(P,a,b):
    ab=b-a; t=np.clip(((P-a)@ab)/(ab@ab+1e-9),0,1); return np.linalg.norm(P-(a+t[:,None]*ab),axis=1)
def sample(rng,xc,yc,zc,design,solid,contact,shape):
    P=np.c_[xc,zc]; occ=np.zeros(len(xc),bool)
    ring=lambda th: np.array([19*np.cos(np.radians(th)),19*np.sin(np.radians(th))])
    segs=[]
    hb=np.array([rng.uniform(57,73),18.]); segs.append((ring(rng.uniform(20,100)),hb))                 # 클램프 -> 집게 하우징
    rp=np.array([rng.uniform(104,148),12.])
    if rng.random()<0.9: segs.append((ring(rng.uniform(-60,10)),rp))                                  # 아래 사재 -> 위 레일
    if rng.random()<0.8: segs.append((np.array([rng.uniform(62,74),19.]),np.array([rng.uniform(104,135),13.])))  # 하우징 -> 레일
    segs.append((ring(rng.uniform(70,150)),np.array([-12.,rng.uniform(25,30)])))  # 클램프 -> 아래 걸이 (항상: 걸이가 떠 있으면 안 됨)
    base=list(segs)
    for _ in range(rng.integers(0,4)):                                                                 # 웹
        (a1,b1),(a2,b2)=[base[i] for i in rng.choice(len(base),2)]
        s1,s2=rng.uniform(0.15,0.85,2); segs.append((a1+s1*(b1-a1),a2+s2*(b2-a2)))
    for a,b in segs:
        t=rng.uniform(4,12); w=rng.uniform(4,16); side=rng.random()<0.25
        d=seg_dist(P,a,b); ins=(d<=t/2)&(yc<=w)
        if side: ins&=yc>=w-rng.uniform(4,8)
        occ|=ins
    if rng.random()<0.3:                                                                               # 판 띠 (폰 뒤)
        x0=rng.uniform(-8,60); x1=x0+rng.uniform(20,80); occ|=(xc>x0)&(xc<x1)&(zc>24)&(zc<28)&(yc<rng.uniform(8,30))
    occ&=design
    lab,n=ndimage.label((occ|solid).reshape(shape)); lab=lab.ravel()
    keep=np.unique(lab[contact&(lab>0)]); occ&=np.isin(lab,keep)
    return occ
