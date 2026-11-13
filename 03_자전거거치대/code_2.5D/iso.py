import numpy as np, trimesh, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, sys
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
m=trimesh.load('../opt/mesh_d_1mm.stl'); tri=m.vertices[m.faces]; n=m.face_normals
L=np.array([0.4,-0.6,0.7]); L/=np.linalg.norm(L); sh=0.25+0.75*np.clip(n@L,0,1)
c=np.c_[0.12+0.45*sh,0.25+0.45*sh,0.55+0.4*sh]; c=np.clip(c,0,1)
fig=plt.figure(figsize=(6,4),dpi=200); ax=fig.add_axes([0,0,1,1],projection='3d')
ax.add_collection3d(Poly3DCollection(tri,facecolors=c,linewidths=0))
b=m.bounds; ctr=b.mean(0); r=(b[1]-b[0]).max()/2
ax.set_xlim(ctr[0]-r,ctr[0]+r); ax.set_ylim(ctr[1]-r,ctr[1]+r); ax.set_zlim(ctr[2]-r*0.6,ctr[2]+r*0.6); ax.set_box_aspect((1,1,0.6))
ax.view_init(int(sys.argv[1]),int(sys.argv[2])); ax.set_axis_off(); fig.savefig(sys.argv[3],transparent=False,facecolor='white')
