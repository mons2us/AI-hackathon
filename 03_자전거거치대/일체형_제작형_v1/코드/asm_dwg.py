# 조립도: 3면도(외곽선) + 부품 번호 + 부품표 + 표제란
import numpy as np, trimesh, sys, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from skimage import measure
from matplotlib import font_manager as fm
fp=[f for f in fm.findSystemFonts() if 'NotoSansCJK' in f]; fm.fontManager.addfont(fp[0]); plt.rcParams['font.family']=fm.FontProperties(fname=fp[0]).get_name()
sys.path.insert(0,'../cad'); import parts as P, cadquery as cq
def cqmesh(w):
    cq.exporters.export(w,'/tmp/_a.stl',tolerance=0.05); return trimesh.load('/tmp/_a.stl')
W=76; L=160; yj=W/2; h=P.XR+L
M={'1':trimesh.load('../cad/body_v3_phoneframe.stl'),'2':cqmesh(P.jaw(yj).union(P.jaw(yj,-1))),'3':cqmesh(P.tophook(h)),
   '4':cqmesh(P.spring(yj).union(P.spring(yj,-1))),'5':cqmesh(P.pin().union(P.pin(-1)))}
PH=cqmesh(P.phone(W,L))
def outline(ax,m,i,j,lw,col='k',res=0.25,ls='-'):
    V=m.vertices[:,[i,j]]; lo=V.min(0)-2; hi=V.max(0)+2; n=((hi-lo)/res).astype(int)+1
    img=np.zeros((n[1],n[0]),np.uint8)
    from PIL import Image, ImageDraw
    im=Image.new('L',(n[0],n[1]),0); d=ImageDraw.Draw(im)
    for f in m.faces:
        p=((V[f]-lo)/res); d.polygon([tuple(q) for q in p],fill=1)
    a=np.asarray(im)
    for c in measure.find_contours(a,0.5):
        ax.plot(c[:,1]*res+lo[0],c[:,0]*res+lo[1],color=col,lw=lw,ls=ls)
fig=plt.figure(figsize=(16.5,11.7),dpi=130)   # A3 가로
fig.patch.set_facecolor('white')
fig.add_artist(plt.Rectangle((0.015,0.02),0.97,0.96,fill=False,lw=2,transform=fig.transFigure))
views=[('옆면도 (폰 길이 방향, 폰 좌표)',0,2,[0.04,0.42,0.52,0.52]),('평면도 (화면 쪽에서)',0,1,[0.04,0.06,0.52,0.36]),('정면도 (폰 위쪽에서)',1,2,[0.58,0.42,0.22,0.52])]
cols={'1':'#0b5e61','2':'#b5651d','3':'#b5651d','4':'#555','5':'#555'}
axs={}
for t,i,j,rect in views:
    ax=fig.add_axes(rect); ax.set_aspect('equal'); ax.axis('off'); ax.set_title(t,fontsize=11,loc='left')
    outline(ax,PH,i,j,0.8,'#999',ls='--')
    for k,m in M.items(): outline(ax,m,i,j,1.3 if k=='1' else 1.0,cols[k])
    t_=np.linspace(0,2*np.pi,100)
    if (i,j)==(0,2): ax.plot(15.9*np.cos(t_),15.9*np.sin(t_),'k-.',lw=0.6); ax.text(0,-4,'핸들바\nØ31.8',ha='center',fontsize=8)
    axs[(i,j)]=ax
# 치수 (옆면도)
ax=axs[(0,2)]
def dim(ax,p,q,off,txt,vert=False,fs=9):
    (x0,y0),(x1,y1)=p,q
    if not vert:
        y=y0+off; ax.plot([x0,x0],[y0,y],'k-',lw=0.4); ax.plot([x1,x1],[y1,y],'k-',lw=0.4); ax.annotate('',(x0,y),(x1,y),arrowprops=dict(arrowstyle='<->',lw=0.7)); ax.text((x0+x1)/2,y+1,txt,ha='center',va='bottom',fontsize=fs)
    else:
        x=x0+off; ax.plot([x0,x],[y0,y0],'k-',lw=0.4); ax.plot([x1,x],[y1,y1],'k-',lw=0.4); ax.annotate('',(x,y0),(x,y1),arrowprops=dict(arrowstyle='<->',lw=0.7)); ax.text(x+1.5,(y0+y1)/2,txt,ha='left',va='center',fontsize=fs,rotation=90)
dim(ax,(-24,-37),(151,-37),-6,'175 (몸체 전체 길이)'); dim(ax,(0,0),(65,0),-48,'65 (집게 중심)'); dim(ax,(-10,30),(150,30),34,'145 – 170 (폰 길이, 위 걸이 이동 25)')
dim(ax,(160,-36),(160,47),4,'83',True); 
ax=axs[(0,1)]; dim(ax,(-24,-42),(151,-42),-7,'175'); dim(ax,(158,-42),(158,42),3,'84',True); dim(ax,(55,46),(75,46),3,'20')
ax=axs[(1,2)]; dim(ax,(-45,-37),(45,-37),-6,'폰 폭 64 – 90 (집게 이동 13 × 2)',fs=8)
# 부품 번호 풍선 (옆면도)
ax=axs[(0,2)]
for k,(px,py),(bx,by) in [('1',(100,10),(120,-22)),('2',(65,40),(45,52)),('3',(152,40),(172,52)),('4',(65,24),(88,52)),('5',(65,20),(28,52))]:
    ax.annotate('',(px,py),(bx,by),arrowprops=dict(arrowstyle='-',lw=0.7)); ax.add_patch(plt.Circle((bx,by),4.2,fc='white',ec='k',lw=1)); ax.text(bx,by,k,ha='center',va='center',fontsize=10,fontweight='bold')
# 부품표
axb=fig.add_axes([0.58,0.06,0.395,0.33]); axb.axis('off'); axb.set_title('부품표',fontsize=11,loc='left')
rows=[['번호','부품','수량','재료 · 사양','파일'],['1','몸체 (최적화 형상 + 하우징 · 레일 · 걸이)','1','PETG, 채움 100%, 81.3 g','1_몸체_body_v3.stl'],['2','슬라이드 집게','2','PETG, 3.6 g','2_슬라이드집게_jaw_v3.step'],['3','위쪽 슬라이드 걸이','1','PETG, 8.3 g','3_위걸이_tophook_v3.step'],['4','압축 스프링','2','외경≤5, 자유 길이≈28 (확인)','구매'],['5','M3 볼트 · 너트 (핀 2 + 잠금 3)','5','M3×16 / M3×10','구매'],['6','M4 볼트 · 너트 · 와셔','1','M4×25','구매']]
tb=axb.table(cellText=rows,colWidths=[0.06,0.36,0.06,0.27,0.25],loc='upper left',cellLoc='left'); tb.auto_set_font_size(False); tb.set_fontsize(7.8); tb.scale(1,1.55)
for (r,c),cell in tb.get_celld().items():
    cell.set_linewidth(0.6)
    if r==0: cell.set_facecolor('#e8eeee'); cell.set_text_props(fontweight='bold')
# 표제란
axt=fig.add_axes([0.58,0.025,0.395,0.04]); axt.axis('off')
tt=axt.table(cellText=[['도면명: 자전거 폰 거치대 조립도','도면 번호: FP-BM-000','척도: 1:1 (A3)','단위: mm','2026-11-15']],colWidths=[0.34,0.2,0.16,0.1,0.2],loc='center',cellLoc='center'); tt.auto_set_font_size(False); tt.set_fontsize(8); tt.scale(1,1.6)
fig.text(0.04,0.955,'FormProof — 자전거 폰 거치대 (일체형 · 4면 고정) 조립도',fontsize=15,fontweight='bold')
fig.text(0.04,0.925,'거치 각도 35° — 장착 시 폰 좌표가 핸들바 축 기준 35° 회전.   ',fontsize=9,color='#555'); fig.text(0.30,0.925,'점선 = 폰 (76 × 160 × 8, 참고)   청록 = 출력 몸체   주황 = 출력 슬라이드 부품   회색 = 구매품',fontsize=8,color='#555')
plt.savefig('dwg_assembly_v1.png',dpi=130); print('ok')
