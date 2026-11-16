# 제작용 부품 (폰 정렬 좌표: x'=폰 길이, y=폭, z'=화면 법선). 단위 mm
import cadquery as cq, numpy as np, json, sys
XR=-10.; ZB=24.; PB=ZB+6     # 폰 뒷면 z'=30
def box(x0,x1,y0,y1,z0,z1): return cq.Workplane().box(x1-x0,y1-y0,z1-z0).translate(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
# --- 몸체에 붙는 고정부 (최적화 비설계 영역) ---
# 레일 하우징: x' 55..75, y -42..42, z' 18..30, 양쪽 채널 x' 60..70, z' 20..28 (y 5..42), 윗면 목 슬롯 x' 63..67 (y 26..42)
H=box(55,75,-42,42,18,30)
for s in (1,-1):
    H=H.cut(box(60,70,5*s if s>0 else -42,42 if s>0 else -5,20,28))
    H=H.cut(box(61,69,26 if s>0 else -42,42 if s>0 else -26,27,31))
    H=H.cut(cq.Workplane().circle(1.7).extrude(20).translate((65,30*s,15)))   # M3 핀 구멍
# 하단 걸이: x' -14..-10 기둥 + 윗 턱 (x' -14..-6), y -15..15, z' 24..47
K=box(-16,-10,-15,15,ZB,47).union(box(-16,-6,-15,15,44,47))
# --- 슬라이드 집게 (출력, 2개) : 집게 내면 위치 yj ---
def jaw(yj,s=1):
    sl=box(60.4,69.6,yj-27,yj+3,20.4,27.6).cut(box(62.3,67.7,yj-24,yj+1,19,29))   # 슬라이더 + 스프링 포켓(핀 관통)
    nk=box(61.4,68.6,yj,yj+5,27,30.5)   # 폰 옆면(y<yj)과 겹치지 않게                                             # 목
    pr=(cq.Workplane('YZ').polyline([(yj,30),(yj+5,30),(yj+5,47),(yj-3,47),(yj-3,44),(yj,36)]).close().extrude(16).translate((57,0,0)))
    j=sl.union(nk).union(pr)
    return j if s>0 else j.mirror('XZ')
def spring(yj,s=1):   # 압축 스프링 OD5: 포켓 안쪽 벽(yj-24) ~ 핀(30)
    a=yj-24; L=30-1.5-a
    sp=cq.Workplane('XZ').circle(2.5).circle(2.0).extrude(-L).translate((65,a,24))
    return sp if s>0 else sp.mirror('XZ')
def pin(s=1): return cq.Workplane().circle(1.5).extrude(16).translate((65,30*s,16))
def phone(W=76,L=160,T=8):
    return cq.Workplane().box(L,W,T).edges('|Z').fillet(8).edges().fillet(min(2.5,T/2-0.5)).translate((XR+L/2,0,PB+T/2))
if __name__=='__main__':
    W=float(sys.argv[1]) if len(sys.argv)>1 else 76
    yj=W/2
    parts=dict(H=H,K=K,J=jaw(yj).union(jaw(yj,-1)),S=spring(yj).union(spring(yj,-1)),P=pin().union(pin(-1)),PH=phone(W))
    vol={k:v.val().Volume() for k,v in parts.items()}
    print({k:round(v,0) for k,v in vol.items()}, 'jaw pair g (PETG 1.27):',round(vol['J']*1.27e-3,1),'hook g',round(vol['K']*1.27e-3,1),'housing g',round(vol['H']*1.27e-3,1))
    t=np.radians(35)
    for k,v in parts.items():
        w=v.rotate((0,0,0),(0,1,0),-35)   # x'->세계: X=x'cos-z'sin, Z=x'sin+z'cos  (y축 회전 -35°: cadquery 부호 확인용)
        cq.exporters.export(w,f'w_{k}_{int(W)}.stl',tolerance=0.05)
    cq.exporters.export(jaw(yj),'jaw.step'); cq.exporters.export(K,'hook.step'); cq.exporters.export(H,'housing.step')

# ===== v2: 위쪽 슬라이드 걸이 + 잠금 나사 =====
# 위쪽 레일 (몸체 고정부): x' 102..150, |y|<10, z' 18..30 / 채널 x' 104..151, |y|<5, z' 20..28 / 목 슬롯 x' 128..151, |y|<2.2, z' 27..31
HT=box(102,150,-10,10,12,24).cut(box(104,151,-5,5,14,22)).cut(box(128,151,-4.2,4.2,21,31))   # 판 아래로 내림: 폰 뒷면 냉각면 유지
HT=HT.cut(cq.Workplane('XZ').circle(1.7).extrude(-12).translate((140,4,18)))            # 잠금 M3 (y방향) 구멍 → 슬라이더 옆면 누름
HT=HT.cut(box(137.3,142.7,7,9.6,15,21))                                                     # M3 너트(5.5) 포켓
for s in (1,-1):                                                                            # 집게 잠금 M3 (x'방향, 하우징 벽 x' 55..60)
    H=H.cut(cq.Workplane('YZ').circle(1.7).extrude(6).translate((54.5,20*s,24))).cut(box(56.3,59,20*s-2.75,20*s+2.75,21,27))
def tophook(h):   # h = 폰 위 끝 x' (135..160) — 폰 길이 145~170 mm
    sl=box(h-30,h+12,-4.6,4.6,14.4,21.6)
    nk=box(h,h+12,-3.8,3.8,21,30.5)   # 폰 위 끝(x'<h)과 겹치지 않게
    col=box(h,h+6,-12,12,30,47).union(box(h-4,h+6,-12,12,44,47)).union(box(h+6,h+12,-3.8,3.8,30,36))   # 기둥 6 mm + 목 위 보강
    return sl.union(nk).union(col)
def screw3(p,ax,L=12):   # 시각용 M3 나사
    w=cq.Workplane({'x':'YZ','y':'XZ','z':'XY'}[ax]).circle(1.5).extrude(L)
    return w.translate(p)
