import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, numpy as np, trimesh
from matplotlib.collections import PolyCollection
exec(open('dwg.py').read().split('# ---------- 슬라이드 집게')[0])   # 공통 함수
T=trimesh.load('../cad/body_v3_phoneframe.stl')
V=T.vertices; F=T.faces
fig,ax=plt.subplots(1,2,figsize=(17,6.4),gridspec_kw=dict(width_ratios=[1.15,1]))
a=ax[0]
P=V[F][:,:,[0,2]]; a.add_collection(PolyCollection(P,fc='#d6e9e7',ec='none'))
t=np.linspace(0,2*np.pi,100); a.plot(16*np.cos(t),16*np.sin(t),c=K,lw=1); a.plot([-20,20],[0,0],c='#999',lw=.5,ls='-.'); a.plot([0,0],[-20,20],c='#999',lw=.5,ls='-.')
a.text(-3,-9,'Ø32.0\n(핸들바 Ø31.8)',fontsize=8,ha='center')
a.plot([-10,160],[30,30],c='#c0392b',lw=.8,ls='--'); a.text(150,31,'폰 뒷면 기준선',fontsize=7.5,color='#c0392b',ha='right')
dim(a,(-16,47),(-10,47),3,'6'); dim(a,(-10,30),(-10,44),-12,'14 (폰 두께 최대)',True)
dim(a,(0,0),(65,0),-44,'65 (집게 중심)'); dim(a,(0,0),(140,0),-50,'140 (위 레일 잠금 나사)')
dim(a,(-10,44),(135,44),9,'145 (폰 길이 최소 · 위 걸이 안쪽 면)'); dim(a,(135,44),(160,44),9,'+25')
dim(a,(55,18),(75,18),-8,'20 (집게 하우징)'); dim(a,(102,12),(150,12),-6,'48 (위 레일)')
xb,zb=-24*np.sin(np.radians(35)),-24*np.cos(np.radians(35)); a.plot(xb,zb,'o',ms=5,mfc='none',mec=K); a.annotate('M4 볼트 구멍 Ø4.5 (조임)',(xb,zb),(xb+20,zb-14),fontsize=8,arrowprops=dict(arrowstyle='->',lw=.6))
a.text(60,-30,'좌표: 폰 뒷면과 평행한 축(폰 길이 방향) 기준 — 실제 장착 시 35° 기울어짐',fontsize=8,color='#555')
setup(a,'옆 (폰 길이 방향, 핸들바 중심 = 원점)',(-40,175),(-58,60))
a=ax[1]
P=V[F][:,:,[0,1]]; a.add_collection(PolyCollection(P,fc='#d6e9e7',ec='none'))
dim(a,(-24,-42),(151,-42),-6,'전체 길이 175'); dim(a,(160,-42),(160,42),3,'84',True)
dim(a,(55,42),(75,42),3,'20 (집게 하우징)')
a.text(130,13,'위 걸이 목 슬롯 8.4',fontsize=7.5,ha='center')
a.text(-14,-24,'아래 걸이\n폭 30',fontsize=7.5,ha='center')
setup(a,'위 (화면 쪽에서)',(-35,175),(-55,58))
fig.suptitle('부품 ① 몸체 — PETG, 채움 100% · 단위 mm · 81.3 g · 형상 원본 = body_v3.stl (자유 곡면이라 STL이 기준)',fontsize=12)
fig.text(.5,.02,'핸들바 구멍·볼트 구멍·슬롯·M3 구멍(Ø3.4)·너트 포켓(5.5 mm)은 STL에 포함 · 출력 방향: 폰 뒷면이 위를 향하게(층 쌓는 방향 = 화면 법선, 해석과 동일), 받침대(서포트) 필요',ha='center',fontsize=8.5,color='#555')
plt.savefig('dwg_body_v1.png',dpi=140,bbox_inches='tight'); print('ok')
