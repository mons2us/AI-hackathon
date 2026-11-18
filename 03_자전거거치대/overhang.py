import trimesh, numpy as np, sys, json
for p in sys.argv[1:]:
    m=trimesh.load(p); n=m.face_normals; a=m.area_faces; c=m.triangles_center
    ymin=m.bounds[0,1]
    down=(n[:,1]< -np.cos(np.radians(45)))&(c[:,1]>ymin+0.6)
    bed=(n[:,1]< -0.9)&(c[:,1]<=ymin+0.6)
    print(json.dumps(dict(file=p.split('/')[-1],mass_g=round(abs(m.volume)*1.27e-3,1),overhang_cm2=round(a[down].sum()/100,2),bed_cm2=round(a[bed].sum()/100,2),total_cm2=round(a.sum()/100,1)),ensure_ascii=False))
