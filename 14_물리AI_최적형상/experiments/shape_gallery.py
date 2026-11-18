import sys, numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, __import__('os').path.join(__import__('os').path.dirname(__file__), '..'))
from fp08 import problems, shapes
from skimage import measure
fig=plt.figure(figsize=(16,20))
ks=list(problems.GROUPS)
for r,k in enumerate(ks):
    p=problems.get(k); cv=shapes.Canvas(p); g=p.grid
    for c in range(4):
        o,m=shapes.make_shape(p,k,c,cv)
        full=g.eshape(o|cv.fixed).astype(float)
        ax=p.sym_axis
        A=np.concatenate([np.flip(full,2-ax),full],2-ax)  # eshape (z,y,x): axis index = 2-ax
        A=np.pad(A,1)
        v,f,_,_=measure.marching_cubes(A,0.5)
        ax3=fig.add_subplot(len(ks),4,r*4+c+1,projection='3d')
        ax3.plot_trisurf(v[:,2],v[:,1],f,v[:,0],color='#4a90d9',lw=0,alpha=.9)
        ax3.set_box_aspect((A.shape[2],A.shape[1],A.shape[0])); ax3.set_axis_off()
        ax3.set_title(f"{k} #{c} {m['family']}{'+E' if m['reinforced'] else ''} vf{m['vf']:.2f}",fontsize=9)
plt.tight_layout(); plt.savefig('docs/random_shapes_gallery.png',dpi=70)
