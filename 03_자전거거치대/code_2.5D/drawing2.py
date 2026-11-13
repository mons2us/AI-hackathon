import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from skimage import measure
from matplotlib.patches import Circle, Rectangle, FancyArrowPatch
plt.rcParams['font.family']='Noto Sans CJK JP'
f=np.load('../out/FormProof_자전거거치대_v4_field.npy'); res=0.5; X0,Y0,Z0=-26,36,-36
S=f>0.5
fig=plt.figure(figsize=(297/25.4,210/25.4)); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,297); ax.set_ylim(0,210); ax.set_aspect('equal'); ax.axis('off')
LW=0.6; TH=0.25
ax.add_patch(Rectangle((8,8),281,194,fill=False,lw=0.9))
from scipy import ndimage
def outline(mask,ox,oy,ux,uy,org):
    m=ndimage.gaussian_filter(np.pad(mask.astype(float),1),1.6)
    for c in measure.find_contours(m.astype(float),0.5):
        a=(c[:,0]-1)*res+org[0]; b=(c[:,1]-1)*res+org[1]
        ax.plot(ox+ux*a,oy+uy*b,'k',lw=LW,solid_joinstyle='round')
# front view (xz): sheet = (FX+x, FY+z)
FX,FY=52,100
outline(S.any(1),FX,FY,1,1,(X0,Z0))
# top view (xy) above
TY=144
outline(S.any(2),FX,TY-39,1,1,(X0,Y0))
# right view (yz): sheet = (RX+(y-45), FY+z)
RX=215
outline(S.any(0),RX-39,FY,1,1,(Y0,Z0))
def cl(x1,y1,x2,y2): ax.plot([x1,x2],[y1,y2],color='#C0392B',lw=TH,dashes=(8,2,1,2))
def hid(x1,y1,x2,y2): ax.plot([x1,x2],[y1,y2],'k',lw=TH+0.1,dashes=(3,1.5))
# center lines
cl(FX-30,FY,FX+30,FY); cl(FX,FY-40,FX,FY+30)
cl(FX+90,FY+8,FX+90,FY+26); hid(FX+86,FY+11,FX+86,FY+20); hid(FX+94,FY+11,FX+94,FY+20)
hid(FX-8,FY-27+2.25,FX+8,FY-27+2.25); hid(FX-8,FY-27-2.25,FX+8,FY-27-2.25); cl(FX-11,FY-27,FX+11,FY-27)
ax.add_patch(Circle((FX+90,TY+16),4,fill=False,lw=LW)); cl(FX+84,TY+16,FX+96,TY+16); cl(FX+90,TY+10,FX+90,TY+22)
cl(RX+16,FY-40,RX+16,FY+30)
for yb in (8,24): ax.add_patch(Circle((RX+yb,FY-27),2.25,fill=False,lw=LW)); cl(RX+yb-5,FY-27,RX+yb+5,FY-27)
# dims
def dim(p1,p2,off,txt,vert=False,fs=6.5):
    (x1,y1),(x2,y2)=p1,p2
    if not vert:
        y=max(y1,y2)+off if off>0 else min(y1,y2)+off
        for xx,yy in ((x1,y1),(x2,y2)): ax.plot([xx,xx],[yy+np.sign(off)*1,y+np.sign(off)*1.5],'k',lw=TH)
        ax.add_patch(FancyArrowPatch((x1,y),(x2,y),arrowstyle='<|-|>',mutation_scale=5,lw=TH,color='k'))
        ax.text((x1+x2)/2,y+0.8,txt,ha='center',va='bottom',fontsize=fs)
    else:
        x=max(x1,x2)+off if off>0 else min(x1,x2)+off
        for xx,yy in ((x1,y1),(x2,y2)): ax.plot([xx+np.sign(off)*1,x+np.sign(off)*1.5],[yy,yy],'k',lw=TH)
        ax.add_patch(FancyArrowPatch((x,y1),(x,y2),arrowstyle='<|-|>',mutation_scale=5,lw=TH,color='k'))
        ax.text(x-0.8,(y1+y2)/2,txt,ha='right',va='center',fontsize=fs,rotation=90)
dim((FX-23,FY-34),(FX+100,FY-34),-9,'123')
dim((FX,FY-34),(FX+100,FY-34),-4.5,'100 (핸들바 중심 ~ 팔 끝)')
dim((FX+80,FY+20),(FX+100,FY+20),5,'20')
dim((FX+100,FY-16),(FX+100,FY+20),6,'36',vert=True)
dim((FX-23,FY-34),(FX-23,FY+23),-6,'57',vert=True)
dim((FX-8,FY-34),(FX+8,FY-34),-4.5,'16')
dim((RX,FY+23),(RX+32,FY+23),5,'32')
dim((RX+8,FY-34),(RX+24,FY-34),-5,'16 (볼트 간격)')
dim((RX+32,FY-34),(RX+32,FY+23),6,'57',vert=True)
dim((FX+100,TY),(FX+100,TY+32),5,'32',vert=True)
def lead(xy,txy,txt):
    ax.annotate(txt,xy=xy,xytext=txy,fontsize=6.5,arrowprops=dict(arrowstyle='-|>',lw=TH,color='k',mutation_scale=5),ha='left',va='center')
lead((FX-11.4,FY+11.4),(FX-42,FY+40),'Ø32.2 (핸들바 Ø31.8 + 0.4)')
lead((FX-16.3,FY+16.3),(FX-42,FY+28),'Ø46')
lead((FX+1,FY-30),(FX+16,FY-24),'슬릿 2')
lead((RX+25.5,FY-28.5),(RX+38,FY-14),'Ø4.5 관통 ×2\n(M4 볼트·너트)')
lead((FX+92.8,TY+18.8),(FX+60,TY+40),'Ø8 깊이 9 (폰 클램프용 인서트, 규격 확인 필요)')
lead((FX+55,FY+3),(FX+64,FY+40),'팔 자유 형상부: 치수는 STL 기준')
for t,x,y in (('정면도',FX+35,FY-52),('평면도',FX+35,TY+38),('우측면도',RX+16,FY+33)): ax.text(x,y,t,ha='center',fontsize=8,fontweight='bold')
# iso image
img=plt.imread('iso.png'); iax=fig.add_axes([186/297,140/210,100/297,58/210]); iax.imshow(img); iax.axis('off')
ax.text(236,141,'참고 입체도',fontsize=7,fontweight='bold',ha='center')
# title block
x0,y0=196,10; w,hh=93,48
rows=[('품명','자전거 폰 거치대 (FormProof 사례, STL v4)'),('재료','PETG (3D 프린트, FDM)'),('무게','약 74 g (클램프 약 39 g + 팔·받침판 약 36 g)'),
('출력','옆면(폭 32 mm 방향)을 베드에 두고 출력'),('체결','M4 볼트·너트 2조, 폰 클램프 인서트 1개'),('척도 / 단위','1:1 (A4) / mm'),('투상법','제3각법'),('비고','자유 형상부는 STL 파일 기준')]
ax.add_patch(Rectangle((x0,y0),w,hh,fill=False,lw=0.8)); rh=hh/len(rows)
for i,(a,b) in enumerate(rows):
    yy=y0+hh-(i+1)*rh; ax.plot([x0,x0+w],[yy,yy],'k',lw=TH); ax.text(x0+1.5,yy+rh/2,a,fontsize=6,va='center',color='#444'); ax.text(x0+20,yy+rh/2,b,fontsize=6.3,va='center')
ax.plot([x0+18.5,x0+18.5],[y0,y0+hh],'k',lw=TH)
ax.text(14,196,'설계 도면 · 자전거 폰 거치대',fontsize=11,fontweight='bold'); ax.text(14,190,'FormProof 생성 · 근거 기반 조건 · 출력 형상 재해석: 1차 진동 94.4 Hz (기준 91 Hz 이상), 48.5 g 충격 최대 응력 15.6 MPa (기준 26 MPa 이하) · 2026.11',fontsize=7,color='#444')
fig.savefig('../out/FormProof_자전거거치대_도면_v2.pdf'); fig.savefig('../out/FormProof_자전거거치대_도면_v2.png',dpi=200); print('ok')
