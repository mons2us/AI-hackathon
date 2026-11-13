import numpy as np, trimesh, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
m=trimesh.load('mesh_r2b_1mm.stl')
fig=plt.figure(figsize=(12,4.5),dpi=110)
for i,(el,az) in enumerate([(20,-60),(0,-90),(60,-30)]):
    ax=fig.add_subplot(1,3,i+1,projection='3d'); tri=m.vertices[m.faces]
    n=m.face_normals; sh=0.35+0.65*np.clip(n@np.array([0.3,-0.5,0.8]),0,1)
    pc=Poly3DCollection(tri,facecolors=plt.cm.Blues(0.35+0.5*sh),linewidths=0); ax.add_collection3d(pc)
    b=m.bounds; ax.set_xlim(b[0,0],b[1,0]); ax.set_ylim(b[0,1]-50,b[1,1]+50); ax.set_zlim(b[0,2]-30,b[1,2]+30)
    ax.set_box_aspect((1,1,0.8)); ax.view_init(el,az); ax.set_axis_off()
plt.tight_layout(); plt.savefig('stl_view.png')
