import trimesh,numpy as np,manifold3d as mf,sys
from matplotlib.path import Path
T=trimesh.load(sys.argv[1]); nx=int(sys.argv[3]); ny,nz=20,37
A=mf.Manifold(mf.Mesh(vert_properties=np.asarray(T.vertices,np.float32),tri_verts=np.asarray(T.faces,np.uint32)))
r=np.zeros((nz,ny,nx)); X,Y=np.meshgrid(-24+2*np.arange(nx)+1,2*np.arange(ny)+1)
for k in range(nz):
  acc=np.zeros(X.shape)
  for dz in (-.5,.5):
    cs=A.slice(-36+2*k+1+dz).to_polygons()
    for dx in (-.5,.5):
      for dy in (-.5,.5):
        p=np.c_[(X+dx).ravel(),(Y+dy).ravel()]; w=np.zeros(len(p))
        for poly in cs: w+=Path(poly).contains_points(p)
        acc+=(w%2).reshape(X.shape)
  r[k]=acc/8
rb=(r.ravel()>=0.5).astype(float); np.save(sys.argv[2],rb); print('cells',int(rb.sum()))
