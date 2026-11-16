import numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
exec(open('sketch.py').read().split('# 핸들바 (옆에서)')[0].replace("figsize=(8,5.6)","figsize=(8,5.6)"))
# 자전거 옆모습 (오른쪽이 앞)
RW=(122,26); FW_=(38,26); R=19
circ(RW,R,lw=1.8); circ(FW_,R,lw=1.8); circ(RW,3); circ(FW_,3)
BB=(72,26); ST=(64,58); HT1=(108,52); HT2=(104,64)
line(FW_,BB); line(BB,ST); line(ST,FW_)            # 뒤 삼각 (왼쪽이 뒤)
line(BB,HT1); line(ST,HT2); line(HT1,HT2)           # 앞 삼각
line(HT1,RW,lw=1.8)                                  # 포크
line((60,62),(70,62),lw=2.2); line(ST,(62,62))       # 안장
line(HT2,(106,70)); line((106,70),(116,72),lw=1.8)   # 스템
circ((117,72),2.2,lw=1.6)                            # 핸들바 (옆에서 본 단면)
line((117,72),(126,66),lw=1.6); line((126,66),(127,58),lw=1.6)   # 드롭/그립
for k in range(0,3): circ((BB[0],BB[1]),4+0*k)
# 폰 (기울여서) + 물음표 상자
t=np.radians(35); u=np.array([np.cos(t),np.sin(t)]); n=np.array([-np.sin(t),np.cos(t)])
o=np.array([112,80]); L=26; T=3.2
P=[o,o+L*u,o+L*u+T*n,o+T*n]; poly([tuple(p) for p in P],lw=2,c=BLUE)
qb=[(113,73),(123,73),(123,80),(113,80)]; poly(qb,c=RED,lw=1.2); txt(118,76.5,'?',16,RED,ha='center')
arrow((140,96),(126,84),c=RED); txt(136,100,'여기에 폰!',17,RED)
txt(128,109,'(거치대 모양은?)',13,RED)
# 시선
for k in np.linspace(0,1,7)[:-1]:
    a=np.array([66,96])+k*np.array([46,-10]); b=a+np.array([46,-10])/7*0.55; line(tuple(a),tuple(b),c=BLUE,lw=1,n=1)
circ((62,97),4,col=BLUE,lw=1.4); txt(48,104,'앉아서 보이게 (눈)',15,BLUE)
# 길
xs=np.linspace(16,158,60); ys=6+1.4*np.sin(xs*0.9)+rng.normal(0,0.3,60); ax.plot(xs,ys,c=INK,lw=1.4)
txt(60,13,'울퉁불퉁한 길  덜덜덜',14,RED)
for x0 in (134,140): arrow((x0,30),(x0,40),c=RED); arrow((x0,40),(x0,30),c=RED)
# 요구 메모
txt(18,99,'',1)
txt(16,90,'안 흔들리게!',19); txt(16,82,'최대한 가볍게!',19); txt(16,74,'3D 프린터로 뽑을 거야',14,'#555')
[txt(16,y,w,13,'#555') for y,w in [(66,'- 모든 폰'),(60,'- 열 안 갇히게'),(54,'- 화면 눌러도 안 휘게')]]

# 폰 각도
a0=o; tt=np.linspace(0,t,15); ax.plot(a0[0]+9*np.cos(tt),a0[1]+9*np.sin(tt),c=BLUE,lw=1.1); line(tuple(a0),tuple(a0+[12,0]),c=BLUE,lw=0.9,n=1)
txt(a0[0]+13,a0[1]+1.5,'35도쯤',12,BLUE)
# 브레이크 케이블
xs=np.linspace(127,140,20); ax.plot(xs,62-6*np.sin((xs-127)/13*np.pi)-0.0*xs,c='#777',lw=1.0,ls='--'); txt(132,50,'케이블, 레버 피하기',11,'#777')
# 위에서 본 핸들바 (작은 그림)
bx0,by0=68,66
line((bx0,by0+6),(bx0+36,by0+6),lw=1.5)
poly([(bx0+14,by0+3),(bx0+19,by0+3),(bx0+19,by0+9),(bx0+14,by0+9)],lw=1.1); txt(bx0+16.5,by0,'스템',10,ha='center')
line((bx0+15,by0+11),(bx0+18,by0+14),c=RED,lw=1.3,n=1); line((bx0+18,by0+11),(bx0+15,by0+14),c=RED,lw=1.3,n=1)
poly([(bx0+22,by0+4),(bx0+26,by0+4),(bx0+26,by0+8),(bx0+22,by0+8)],c=BLUE,lw=1.3); txt(bx0+28,by0+11,'스템 옆에',11,BLUE)
txt(bx0,by0+19,'위에서 본 모습',10,'#555')
plt.savefig('../deck/shots/v17_sketch.png',dpi=200,facecolor=fig.get_facecolor()); print('ok')
