import numpy as np, glob
O=[];L=[]
for f in sorted(glob.glob('part_*.npz')):
    d=np.load(f); O.append(d['occ']); L.append(d['lab'])
np.savez('data.npz',occ=np.concatenate(O),lab=np.concatenate(L)); L=np.concatenate(L)
print('N',len(L),'mass %.1f-%.1f'%(L[:,0].min(),L[:,0].max()),'f1 %.1f-%.1f'%(L[:,1].min(),L[:,1].max()),'f1>=91:',(L[:,1]>=91).sum())
