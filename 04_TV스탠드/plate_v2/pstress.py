import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
exec(open('plate.py').read().split('x=np.full(nd,0.4)')[0])
Bc=np.array([[-1,0,1,0,1,0,-1,0],[0,-1,0,-1,0,1,0,1],[-1,-1,-1,1,1,1,1,-1]])/(2*h); D=E/(1-nu**2)*np.array([[1,nu,0],[nu,1,0],[0,0,(1-nu)/2]])
VM=12.0
for tag in ['T_web40','c']:
    m=np.load('bin_%s.npy'%tag); rb=np.where(m.ravel(),1.0,1e-9); U=solve(rb)
    ue=U[:,1][edof]; st=(D@Bc@ue.T).T; v=np.sqrt(st[:,0]**2-st[:,0]*st[:,1]+st[:,1]**2+3*st[:,2]**2).reshape(nz,ny)
    img=plt.get_cmap('turbo')(np.clip(v/VM,0,1)); img[~m]=[1,1,1,1]
    fig=plt.figure(figsize=(6,2.6),dpi=250); ax=fig.add_axes([0,0,1,1]); ax.imshow(img,origin='lower',extent=[-150,150,0,120],interpolation='nearest'); ax.set_axis_off()
    fig.savefig('../deck/shots/tv2d_%s.png'%tag,facecolor='white'); plt.close(fig)
    print(tag, np.percentile(v[m],99.5))
fig=plt.figure(figsize=(4,0.6),dpi=220); ax=fig.add_axes([0.05,0.5,0.9,0.3]); matplotlib.colorbar.ColorbarBase(ax,cmap=plt.get_cmap('turbo'),norm=matplotlib.colors.Normalize(0,VM),orientation='horizontal'); ax.tick_params(labelsize=7); fig.savefig('../deck/shots/tv_cbar.png',facecolor='white'); plt.close(fig)
