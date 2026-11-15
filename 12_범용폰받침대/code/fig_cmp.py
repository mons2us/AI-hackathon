import numpy as np, json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams['font.family']='Noto Sans CJK JP'
from matplotlib.colors import ListedColormap
nx,ny=40,75; NX,NY=nx+1,ny+1
cases=[('flat','평판 2 mm (시판형)',False),('stiff40','구조만 최적화',False),('mp40','구조 + 열 동시',False),('mm40c','구조 + 열 + 알루미늄 배치',True)]
fig=plt.figure(figsize=(13,8.6)); W=0.235
for c,(t,name,al) in enumerate(cases):
    r=np.load('rho_%s.npy'%t); T=np.load('T_%s.npy'%t); res=json.load(open('res_%s.json'%t))
    NP=3; kph=NP+(1 if al else 0)
    Tb=T[kph*NX*NY:(kph+1)*NX*NY].reshape(NY,NX)     # 폰 뒷면 온도
    x0=0.03+c*0.243
    # 구조: 윗층(폰 닿는 면) + 아래층 겹쳐 표시
    top=r[(NP-1)*nx*ny:NP*nx*ny].reshape(ny,nx); bot=r[0:nx*ny].reshape(ny,nx)
    img=np.ones((ny,nx,3)); img[bot>0.5]=[0.62,0.78,0.80]; img[top>0.5]=[0.10,0.45,0.48]
    if al:
        a=r[NP*nx*ny:(NP+1)*nx*ny].reshape(ny,nx); img[(a>0.5)&(top<0.5)]=[0.85,0.55,0.15]
    ax=fig.add_axes([x0,0.47,W,0.40]); ax.imshow(img,origin='lower',extent=[0,80,0,150]); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(name,fontsize=12,fontweight='bold')
    ax2=fig.add_axes([x0,0.04,W,0.40]); im=ax2.imshow(Tb+25,origin='lower',extent=[0,80,0,150],cmap='inferno',vmin=30,vmax=65); ax2.set_xticks([]); ax2.set_yticks([])
    ax2.text(40,-12,'최고 %.1f °C · 처짐 %.1f mm · %.1f g'%(res['Tmax']+25,res['defl_mm'],res['mass_g']),ha='center',fontsize=10.5)
cax=fig.add_axes([0.962,0.07,0.01,0.34]); cb=fig.colorbar(im,cax=cax); cb.ax.tick_params(labelsize=8); cb.set_label('폰 뒷면 온도 (°C, 주변 25 °C 가정)',fontsize=8)
fig.text(0.03,0.93,'받침대 뒷판 — 위: 재료 배치 (진청 = 폰 닿는 윗층, 연청 = 아래층, 주황 = 알루미늄)   아래: 폰 뒷면 온도',fontsize=11.5)
fig.savefig('cmp_v2.png',dpi=140); print('ok')
