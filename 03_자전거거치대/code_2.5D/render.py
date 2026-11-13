import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, sys; plt.rcParams['font.family']='Noto Sans CJK JP'
nx,ny,nz=40,10,15
def show(f,ax,title):
    s=np.load(f).reshape(nz,ny,nx).transpose(2,1,0)>0.5
    col=np.empty(s.shape,dtype=object); col[:]='#AFC0F5'; col[0,:,:]='#5F6B7A'; col[-1,:,:]='#F5A800'
    ax.voxels(s,facecolors=col,edgecolor='#1428A0',linewidth=0.15)
    ax.set_box_aspect((nx,ny*1.0,nz)); ax.view_init(elev=18,azim=-60); ax.set_axis_off(); ax.set_title(title,fontsize=11)
fs=sys.argv[1::2]; ts=sys.argv[2::2]
fig=plt.figure(figsize=(4.2*len(fs),3.2),dpi=150)
for i,(f,t) in enumerate(zip(fs,ts)):
    show(f,fig.add_subplot(1,len(fs),i+1,projection='3d'),t)
plt.tight_layout(); plt.savefig('designs.png',bbox_inches='tight'); print('ok')
