"""A3 제작 도면 (출력용 몸체): 3각법 3면도(투영 윤곽) · 등각도 · 치수 · 구멍 표 · 주기 · 표제란, 척도 1:1 (용지 좌표 = mm).
몸체 좌표 = 폰 판 좌표(x 폰 길이, y 폭, z 화면 법선), 원점 = 핸들바 중심. 구멍 위치는 print_body(팀 build_body)와 같은 치수."""
import os, subprocess, sys, time
import numpy as np


def iso_png(stl, out_png, timeout=120):
    """등각도 렌더 (three.js + 헤드리스 Chromium). 실패하면 None — 도면은 등각도 없이."""
    try:
        r = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "drawing_iso.py"), stl, out_png],
                           capture_output=True, timeout=timeout)
        return out_png if r.returncode == 0 and os.path.exists(out_png) else None
    except Exception:                                                     # noqa: BLE001
        return None


def draw(T, ISO, OUT, MASS, STLNAME, TITLE="자전거 폰 거치대 — 몸체 (최적 설계)", DWGNO="FP-P01-B01", DATE=None):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager as fm
    from PIL import Image, ImageDraw
    from skimage import measure
    DATE = DATE or time.strftime("%Y-%m-%d")
    fp=[f for f in fm.findSystemFonts() if 'NotoSansCJK-Regular' in f or 'NanumGothic' in f or 'malgun' in f.lower()]
    if fp: fm.fontManager.addfont(fp[0]); plt.rcParams['font.family']=fm.FontProperties(fname=fp[0]).get_name()
    Tr=T.vertices[T.faces]; (x0,y0,z0),(x1,y1,z1)=T.bounds
    Tr=T.vertices[T.faces]; (x0,y0,z0),(x1,y1,z1)=T.bounds
    K='#111'; W,H=420,297
    fig=plt.figure(figsize=(W/25.4,H/25.4)); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,W); ax.set_ylim(0,H); ax.set_aspect('equal'); ax.axis('off')
    L=lambda xs,ys,**k: ax.plot(xs,ys,**({'c':K,'lw':.5}|k))
    def T_(x,y,s,fs=2.6,**k): ax.text(x,y,s,fontsize=fs*72/25.4,**({'color':K}|k))
    # 테두리 (왼쪽 철 여백 20)
    ax.add_patch(plt.Rectangle((20,10),W-30,H-20,fill=False,lw=1.0,ec=K))
    def sil(P2,ox,oy):
        lo=P2.reshape(-1,2).min(0)-2; hi=P2.reshape(-1,2).max(0)+2; R=10
        im=Image.new('L',tuple(np.ceil((hi-lo)*R).astype(int)),0); d=ImageDraw.Draw(im)
        for t in P2: d.polygon([tuple(((p-lo)*R)) for p in t],fill=255)
        a=np.asarray(im)>0
        for c in measure.find_contours(a.astype(float),0.5):
            pts=c[:,::-1]/R+lo
            if len(pts)<12: continue
            L(pts[:,0]+ox,pts[:,1]+oy,lw=.55)
    def cl(x,y,r,ox,oy):  # 중심선
        L([ox+x-r-3,ox+x+r+3],[oy+y,oy+y],lw=.25,ls=(0,(8,2,1,2))); L([ox+x,ox+x],[oy+y-r-3,oy+y+r+3],lw=.25,ls=(0,(8,2,1,2)))
    def dim(p,q,off,txt,vert=False):
        (a,b),(c,d)=p,q
        if not vert:
            y=b+off; L([a,a],[b,y+(1.5 if off>0 else -1.5)],lw=.25); L([c,c],[d,y+(1.5 if off>0 else -1.5)],lw=.25)
            ax.annotate('',(a,y),(c,y),arrowprops=dict(arrowstyle='<|-|>,head_length=0.35,head_width=0.12',lw=.35,color=K,shrinkA=0,shrinkB=0)); T_((a+c)/2,y+.8,txt,ha='center',va='bottom',bbox=dict(fc='white',ec='none',pad=0.4))
        else:
            x=a+off; L([a,x+(1.5 if off>0 else -1.5)],[b,b],lw=.25); L([c,x+(1.5 if off>0 else -1.5)],[d,d],lw=.25)
            ax.annotate('',(x,b),(x,d),arrowprops=dict(arrowstyle='<|-|>,head_length=0.35,head_width=0.12',lw=.35,color=K,shrinkA=0,shrinkB=0)); T_(x-.8,(b+d)/2,txt,ha='right',va='center',rotation=90,bbox=dict(fc='white',ec='none',pad=0.4))
    def tag(x,y,s): ax.add_patch(plt.Circle((x,y),2.3,fill=False,lw=.4,ec=K)); T_(x,y,s,fs=2.4,ha='center',va='center')
    # 정면도 (x-z), 원점 = 핸들바 중심
    FX,FY=75,118
    sil(Tr[:,:,[0,2]],FX,FY); T_(FX+x0,FY+z1+5,'정면도',fs=3.2,ha='left')
    ax.add_patch(plt.Circle((FX,FY),16,fill=False,lw=.55,ec=K)); cl(0,0,16,FX,FY)
    dim((FX+x0,FY+z0),(FX+x1,FY+z0),-9,f'{x1-x0:.1f}')
    dim((FX+x0,FY+z0),(FX+x0,FY+z1),-7,f'{z1-z0:.1f}',True)
    dim((FX,FY+z0),(FX+65,FY+z0),-16,'65'); dim((FX,FY+z0),(FX+140,FY+z0),-22.5,'140')
    L([FX+65,FX+65],[FY+z0-14.5,FY+22],lw=.25,ls=(0,(8,2,1,2))); L([FX+140,FX+140],[FY+z0-21,FY+22],lw=.25,ls=(0,(8,2,1,2)))
    tag(FX-13,FY+8,'A'); bx,bz=-13.77,-19.66; ax.plot(FX+bx,FY+bz,'+',c=K,ms=4,mew=.4); tag(FX+bx-6,FY+bz-5,'B'); tag(FX+140+5,FY+18+5,'E'); ax.plot(FX+140,FY+18,'+',c=K,ms=4,mew=.4)
    # 평면도 (x-y) — 3각법: 정면도 위
    PX,PY=FX,236
    sil(Tr[:,:,[0,1]],PX,PY); T_(PX+x0,PY+y1+4,'평면도',fs=3.2,ha='left')
    dim((PX+x1,PY+y0),(PX+x1,PY+y1),9,f'{y1-y0:.1f}',True)
    for s in (1,-1): ax.plot(PX+65,PY+30*s,'+',c=K,ms=4,mew=.4)
    tag(PX+65+6,PY+30+4,'C'); L([PX-30,PX+160],[PY,PY],lw=.25,ls=(0,(8,2,1,2)))
    dim((PX+65,PY-30),(PX+65,PY+30),-13,'60',True)
    # 우측면도 (y-z) — 정면도 오른쪽
    SX,SY=300,FY
    sil(Tr[:,:,[1,2]],SX,SY); T_(SX+y0,SY+z1+14,'우측면도',fs=3.2,ha='left')
    for s in (1,-1): ax.plot(SX+20*s,SY+24,'+',c=K,ms=4,mew=.4)
    tag(SX+20+6,SY+24+5,'D'); dim((SX-20,SY+z1),(SX+20,SY+z1),6,'40'); dim((SX+y0,SY+z0),(SX+y1,SY+z0),-9,f'{y1-y0:.1f}')
    L([SX,SX],[SY+z0-4,SY+z1+4],lw=.25,ls=(0,(8,2,1,2)))
    # 등각도
    if ISO:
        iso=Image.open(ISO); iw,ih=iso.size; bw=118; bh=min(bw*ih/iw,95); bw=bh*iw/ih
        ax.imshow(np.asarray(iso),extent=(282,282+bw,190,190+bh)); T_(282+bw/2,186,'등각도 (참고)',fs=3.0,ha='center')
    # 구멍 표
    HT=[('기호','지름','용도','축','위치 (x, y, z)','수'),('A','Ø32.0','핸들바 (Ø31.8)','y','(0, –, 0)','1'),('B','Ø4.5','M4 조임 볼트','35° 경사','(−13.8, –, −19.7)','1'),
        ('C','Ø3.4','M3 핀 · 너트 포켓 5.5','z','(65, ±30, –)','2'),('D','Ø3.4','M3 집게 잠금 · 너트 포켓','x','(–, ±20, 24)','2'),('E','Ø3.4','M3 위 레일 잠금 · 너트 포켓','y','(140, –, 18)','1')]
    cx=[24,34,48,88,104,140,150]; ty=58
    T_(24,ty+4,'구멍 표 (단위 mm, 원점 = 핸들바 중심)',fs=2.8,fontweight='bold')
    for i,r in enumerate(HT):
        y=ty-i*5.2
        for j,v in enumerate(r): T_(cx[j]+1,y-3.6,v,fs=2.5,fontweight='bold' if i==0 else 'normal')
        L([cx[0],cx[-1]],[y,y],lw=.3)
    L([cx[0],cx[-1]],[ty-len(HT)*5.2]*2,lw=.3)
    for x in cx: L([x,x],[ty,ty-len(HT)*5.2],lw=.3)
    # 주기
    NT=['주기','1. 재질 PETG, 채움 100 %, FDM 3D 프린팅 · 층 쌓는 방향 = 폰 뒷면 법선, 서포트 필요',f'2. 자유 곡면 형상은 STL({STLNAME}) 기준 — 도면 치수는 확인용',
        '3. 구멍 · 슬롯 · 너트 포켓 · 조임 슬릿은 STL에 포함','4. 지시 없는 치수 허용차 ±0.5','5. 조립: 슬라이드 집게 × 2 · 위 걸이 × 1 · M4 볼트 · M3 나사 (별도 도면)']
    for i,s in enumerate(NT): T_(160,58-i*5,s,fs=2.5,fontweight='bold' if i==0 else 'normal')
    # 표제란
    tx,tyb,tw=270,10,140
    rows=[('도명',TITLE),('도번',DWGNO),('재질','PETG'),('질량',f'{MASS:.1f} g (STL 체적 × 1.27 g/cm³)'),
          ('척도','1 : 1 (A3)'),('투상법','3각법'),('단위','mm'),('설계','FormProof 자동 생성 — AI 탐색 + 정밀 최적화'),('일자',DATE)]
    rh=5.4; th=rh*len(rows)
    ax.add_patch(plt.Rectangle((tx,tyb),tw,th,fill=False,lw=.8,ec=K))
    for i,(k,v) in enumerate(rows):
        y=tyb+th-(i+1)*rh; L([tx,tx+tw],[y,y],lw=.3); T_(tx+2,y+1.6,k,fs=2.5,fontweight='bold'); T_(tx+20,y+1.6,v,fs=2.6 if i else 3.0,fontweight='bold' if i==0 else 'normal')
    L([tx+18,tx+18],[tyb,tyb+th],lw=.3)
    plt.savefig(OUT+'.png',dpi=200); plt.savefig(OUT+'.pdf'); plt.close(fig)

