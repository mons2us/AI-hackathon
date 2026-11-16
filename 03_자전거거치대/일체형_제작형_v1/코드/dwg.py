import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
from matplotlib import font_manager as fm
fp=[f for f in fm.findSystemFonts() if 'NotoSansCJK' in f or 'NanumGothic' in f] or [f for f in fm.findSystemFonts() if 'CJK' in f]
fm.fontManager.addfont(fp[0]); plt.rcParams['font.family']=fm.FontProperties(fname=fp[0]).get_name()
K='#1a1a1a'
def poly(a,pts,hidden=False,fill='#eef3f2'):
    a.add_patch(Polygon(pts,closed=True,fc=fill if not hidden else 'none',ec=K,lw=1.1,ls='--' if hidden else '-'))
def rect(a,x0,y0,w,h,**k): poly(a,[(x0,y0),(x0+w,y0),(x0+w,y0+h),(x0,y0+h)],**k)
def dim(a,p,q,off,txt,vert=False):
    (x0,y0),(x1,y1)=p,q
    if not vert:
        y=y0+off; a.plot([x0,x0],[y0,y],c='#666',lw=.5); a.plot([x1,x1],[y1,y],c='#666',lw=.5)
        a.annotate('',(x0,y),(x1,y),arrowprops=dict(arrowstyle='<->',lw=.7,color='#333')); a.text((x0+x1)/2,y+.4,txt,ha='center',va='bottom',fontsize=8)
    else:
        x=x0+off; a.plot([x0,x],[y0,y0],c='#666',lw=.5); a.plot([x1,x],[y1,y1],c='#666',lw=.5)
        a.annotate('',(x,y0),(x,y1),arrowprops=dict(arrowstyle='<->',lw=.7,color='#333')); a.text(x+.4,(y0+y1)/2,txt,ha='left',va='center',fontsize=8,rotation=90)
def setup(a,t,xl,yl):
    a.set_aspect('equal'); a.set_xlim(*xl); a.set_ylim(*yl); a.axis('off'); a.set_title(t,fontsize=10)

# ---------- 슬라이드 집게 (로컬: 슬라이더 바닥 z=0, 집게 안쪽 면 y=0, x 중심 0) ----------
fig,ax=plt.subplots(1,3,figsize=(15,5.6))
a=ax[0]   # 정면 (y-z)
rect(a,-27,0,30,7.2); rect(a,-24,0,25,7.2,hidden=True)
rect(a,0,6.6,5,3.5)
poly(a,[(0,9.6),(5,9.6),(5,26.6),(-3,26.6),(-3,23.6),(0,15.6)])
dim(a,(-27,0),(3,0),-3,'30'); dim(a,(-24,0),(1,0),-6,'25 (스프링 포켓, 관통)')
dim(a,(5,0),(5,7.2),2,'7.2',True); dim(a,(5,9.6),(5,26.6),5,'17',True)
dim(a,(-3,26.6),(5,26.6),2,'8'); dim(a,(-3,26.6),(0,26.6),5,'3 (턱)')
a.annotate('안쪽 면 (폰 옆면 닿음)',(-0.3,13),(-20,18),fontsize=7.5,arrowprops=dict(arrowstyle='->',lw=.6))
setup(a,'정면 (폰 폭 방향)',(-30,14),(-9,35))
a=ax[1]   # 위 (x-y)
rect(a,-4.6,-27,9.2,30); rect(a,-2.7,-24,5.4,25,hidden=True); rect(a,-8,-3,16,8,fill='#fbe3cf')
dim(a,(-4.6,-27),(4.6,-27),-3,'9.2'); dim(a,(-8,5),(8,5),2,'16'); dim(a,(-2.7,-24),(2.7,-24),3,'5.4')
setup(a,'위 (화면 쪽에서)',(-14,14),(-32,10))
a=ax[2]   # 옆 (x-z)
rect(a,-4.6,0,9.2,7.2); rect(a,-3.6,6.6,7.2,3.5); rect(a,-8,9.6,16,17,fill='#fbe3cf')
dim(a,(-3.6,10.1),(3.6,10.1),-14,'7.2 (목)'); dim(a,(-4.6,0),(4.6,0),-3,'9.2'); dim(a,(8,0),(8,26.6),3,'26.6',True)
setup(a,'옆 (폰 길이 방향)',(-14,16),(-6,30))
fig.suptitle('부품 ② 슬라이드 집게 × 2 (좌우 대칭) — PETG, 채움 100% · 단위 mm · 3.6 g',fontsize=12)
fig.text(.5,.02,'하우징 채널 10 × 8 mm 에 끼움 (슬라이더 9.2 × 7.2, 틈 0.4 mm) · 목은 하우징 윗면 8 mm 슬롯을 지남 · 출력: 옆으로 눕혀서 · 압축 스프링은 포켓 안쪽 벽과 M3 핀 사이 · 점선 = 숨은 선',ha='center',fontsize=8.5,color='#555')
plt.savefig('dwg_jaw_v2.png',dpi=150,bbox_inches='tight'); plt.close()

# ---------- 위쪽 슬라이드 걸이 v3 (로컬: 걸이 안쪽 면 x=0, 슬라이더 바닥 z=0) ----------
fig,ax=plt.subplots(1,3,figsize=(15,5.8))
a=ax[0]   # 옆 (x-z)
rect(a,-30,0,42,7.2); rect(a,0,6.6,12,9.5); rect(a,0,15.6,6,17,fill='#fbe3cf'); rect(a,-4,29.6,10,3,fill='#fbe3cf'); rect(a,6,15.6,6,6,fill='#fbe3cf')
dim(a,(-30,0),(12,0),-3,'42'); dim(a,(12,0),(12,32.6),3,'32.6',True); dim(a,(-30,0),(-30,7.2),-3,'7.2',True)
dim(a,(-4,32.6),(6,32.6),2,'10'); a.text(6,11,'목 12',ha='center',fontsize=8)
a.annotate('안쪽 면 (폰 위 끝 닿음)',(0.2,24),(-24,24),fontsize=7.5,arrowprops=dict(arrowstyle='->',lw=.6))
setup(a,'옆 (폰 길이 방향)',(-36,18),(-7,37))
a=ax[1]   # 위 (x-y)
rect(a,-30,-4.6,42,9.2); rect(a,-4,-12,10,24,fill='#fbe3cf'); rect(a,6,-3.8,6,7.6,fill='#fbe3cf')
dim(a,(-4,12),(6,12),2,'10'); dim(a,(6,-12),(6,12),8,'24',True); dim(a,(-30,-4.6),(-30,4.6),-3,'9.2',True); dim(a,(6,-3.8),(12,-3.8),-10,'6 (보강)')
setup(a,'위 (화면 쪽에서)',(-36,18),(-17,17))
a=ax[2]   # 정면 (y-z)
rect(a,-4.6,0,9.2,7.2); rect(a,-3.8,6.6,7.6,9.5); rect(a,-12,15.6,24,17,fill='#fbe3cf')
dim(a,(-3.8,10),(3.8,10),-15,'7.6 (목)'); dim(a,(-12,32.6),(12,32.6),2,'24')
setup(a,'정면 (폰 위쪽에서)',(-16,16),(-7,37))
fig.suptitle('부품 ③ 위쪽 슬라이드 걸이 × 1 — PETG, 채움 100% · 단위 mm · 8.3 g',fontsize=12)
fig.text(.5,.02,'위쪽 레일 채널 10 × 8 mm 에 끼움 · 목은 레일 윗면 8.4 mm 슬롯을 지남 · 이동 25 mm (폰 길이 145–170 mm) · 레일 옆면 M3 나사로 잠금 · 출력: 옆으로 눕혀서',ha='center',fontsize=8.5,color='#555')
plt.savefig('dwg_tophook_v2.png',dpi=150,bbox_inches='tight'); plt.close()
print('ok')
