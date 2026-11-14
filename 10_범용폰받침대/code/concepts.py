# 사람이 쓰는 대안 형태를 같은 무게(40 g)로 만들어 같은 조건에서 비교
import numpy as np, subprocess, json, os
nx,ny,NP,h=40,75,3,2.
xc=(np.arange(nx)*h+1)[None,:]; yc=(np.arange(ny)*h+1)[:,None]
hub=((xc-40)**2+(yc-75)**2<=16**2); corner=(((xc<10)|(xc>70))&((yc<10)|(yc>140)))
def segd(ax,ay,bx,by):
    px,py=np.broadcast_to(xc,(ny,nx)),np.broadcast_to(yc,(ny,nx)); dx,dy=bx-ax,by-ay
    t=np.clip(((px-ax)*dx+(py-ay)*dy)/(dx*dx+dy*dy),0,1); return np.hypot(px-(ax+t*dx),py-(ay+t*dy))
def build(kind,w):
    L=np.zeros((NP,ny,nx),bool)
    if kind=='X':      # 사람이 그린 단순 X (균일 두께)
        m=(segd(5,5,75,145)<=w/2)|(segd(75,5,5,145)<=w/2); L[:]=m
    if kind=='plus':
        m=(segd(40,5,40,145)<=w/2)|(segd(5,75,75,75)<=w/2)|(segd(5,5,75,5)<=w/2)|(segd(5,145,75,145)<=w/2); L[:]=m
    if kind=='H':
        m=(segd(5,5,5,145)<=w/2)|(segd(75,5,75,145)<=w/2)|(segd(5,75,75,75)<=w/2); L[:]=m
    if kind=='frame':  # 테두리 + 가운데 원
        m=(segd(5,5,75,5)<=w/2)|(segd(75,5,75,145)<=w/2)|(segd(75,145,5,145)<=w/2)|(segd(5,145,5,5)<=w/2)|(segd(40,75,40,5)<=w/2)|(segd(40,75,40,145)<=w/2); L[:]=m
    if kind=='holes':  # 2 mm 판 대신 6 mm 판에 원형 구멍 격자 (w = 구멍 지름)
        px,py=np.broadcast_to(xc,(ny,nx)),np.broadcast_to(yc,(ny,nx))
        m=np.ones((ny,nx),bool); 
        for cx in np.arange(10,80,16):
            for cy in np.arange(10,150,16): m&=np.hypot(px-cx,py-cy)>w/2
        L[:]=m
    if kind=='ribs':   # 윗층 판 2 mm + 아래 두 층 리브(세로·가로 격자, w = 리브 폭)
        L[2]=True; px,py=np.broadcast_to(xc,(ny,nx)),np.broadcast_to(yc,(ny,nx))
        rib=(np.abs(((px-8)%24)-0)<w)|(np.abs(((py-8)%24)-0)<w); L[0]=rib; L[1]=rib
    L|=hub[None]|corner[None]
    return L
def mass(L): return L.sum()*h**3*1.27e-3
res={}
for kind,lo,hi,inc in (('X',2,40,True),('plus',2,30,True),('H',2,30,True),('frame',2,30,True),('holes',2,30,False),('ribs',0.5,12,True)):
    for _ in range(30):
        mid=(lo+hi)/2; m=mass(build(kind,mid))
        if (m<40)==inc: lo=mid
        else: hi=mid
    L=build(kind,(lo+hi)/2); rho=np.zeros(nx*ny*(NP+4)); rho[:NP*nx*ny]=L.ravel().astype(float)
    np.save('rho_c_%s.npy'%kind,rho)
    out=subprocess.run(['python3','cradle_mp.py'],env=dict(os.environ,MODE='eval',RHO='rho_c_%s.npy'%kind,TAG='c_'+kind),capture_output=True,text=True).stdout.strip().split('\n')
    r=json.loads(out[0]); s=json.loads(out[1]); res[kind]=dict(mass=r['mass_g'],T=round(r['Tmax']+25,1),defl=r['defl_mm'],vm=s['LC1_떨어지는방향']['vm_max']); print(kind,res[kind],flush=True)
json.dump(res,open('concepts_res.json','w'),ensure_ascii=False)
