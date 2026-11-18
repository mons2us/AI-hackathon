# 출력용 몸체: 최적화 밀도(2 mm 격자) → 매끈한 표면 + 정밀 하우징/걸이 결합 − 채널·슬롯·핀/볼트 구멍·핸들바 구멍
import numpy as np, trimesh, manifold3d as mf, cadquery as cq, sys, json
from skimage import measure; from scipy import ndimage
sys.path.insert(0,'.'); import parts as P
TAG=sys.argv[1]; OUT=sys.argv[2]
r=np.load(f'../opt/rprint_{TAG}.npy'); ny,nz=20,37; nx=r.size//(ny*nz); r=r.reshape(nz,ny,nx); full=np.concatenate([r[:,::-1],r],1)
up=ndimage.zoom(np.pad(full,2),4,order=1)                                   # 0.5 mm
v=ndimage.gaussian_filter(up,1.6); vs,f,_,_=measure.marching_cubes(v,0.5,spacing=(.5,.5,.5))
o=lambda n:(-2*2+0.5*1.5)  # zoom 정렬 보정: 셀 중심 = 원래 좌표
z=vs[:,0]-4+(-36)+0.75; y=vs[:,1]-4+(-40)+0.75; x=vs[:,2]-4+(-24)+0.75
body=trimesh.Trimesh(np.c_[x,y,z],f); body=max(body.split(only_watertight=False),key=lambda m:abs(m.volume))
if body.volume<0: body.invert()
def M(t): return mf.Manifold(mf.Mesh(vert_properties=np.asarray(t.vertices,np.float32),tri_verts=np.asarray(t.faces,np.uint32)))
def cqm(w):
    cq.exporters.export(w,'/tmp/_t.stl',tolerance=0.02); t=trimesh.load('/tmp/_t.stl'); t.merge_vertices(); return M(t)
def bx(x0,x1,y0,y1,z0,z1): return mf.Manifold.cube([x1-x0,y1-y0,z1-z0]).translate([x0,y0,z0])
def cyl(r,h,ax,c):   # ax: 'x','y','z' 축 원기둥, 중심 c
    m=mf.Manifold.cylinder(h,r,r,64).translate([0,0,-h/2])
    if ax=='y': m=m.rotate([90,0,0])
    if ax=='x': m=m.rotate([0,90,0])
    return m.translate(c)
body.merge_vertices(); trimesh.repair.fix_normals(body)
print('body wt',body.is_watertight,round(body.volume*1.27e-3,1))
A=M(body); B=cqm(P.H); C=cqm(P.K); print('status',A.status(),B.status(),C.status(),A.volume(),B.volume(),C.volume())
D=cqm(P.HT); U=A+B+C+D
t=np.radians(35); ct,st=np.cos(t),np.sin(t)
def w2p(X,Z): return X*ct+Z*st, -X*st+Z*ct     # 세계→폰좌표
cut=[]
for s in (1,-1):
    cut+= [bx(59.95,70.05,4.95 if s>0 else -43,43 if s>0 else -4.95,19.95,28.05), bx(60.95,69.05,25.95 if s>0 else -43,43 if s>0 else -25.95,26.95,31.5), cyl(1.7,30,'z',[65,30*s,22])]
cut+= [bx(103.95,152,-5.05,5.05,13.95,22.05), bx(127.95,152,-4.25,4.25,20.95,31)]                               # 위 레일 채널·목 슬롯
cut+= [cyl(1.7,14,'y',[140,10,18]), bx(137.25,142.75,6.95,9.65,14.95,21.05)]                          # 위 레일 잠금 M3 + 너트
for s_ in (1,-1): cut+= [cyl(1.7,8,'x',[57,20*s_,24]), bx(56.25,59.05,20*s_-2.8,20*s_+2.8,20.95,27.05)]   # 집게 잠금 M3 + 너트
cut.append(cyl(16.0,200,'y',[0,0,0]))                                         # 핸들바 Ø31.8 + 여유
sl=bx(-1,1,-60,60,-28,0).rotate([0,-35,0]); cut.append(sl)                    # 조임 슬릿 (세계 |X|<1, Z<0) → 폰좌표로 회전
xb,zb=w2p(0,-24); cut.append(cyl(2.25,40,'x',[0,0,0]).rotate([0,-35,0]).translate([xb,0,zb]))  # M4 볼트 구멍 (세계 X축)
cut.append(bx(-10.05,160,-46,46,30.02,44.5))              # 폰 공간(두께 14 mm까지) 비우기, 걸이는 제외
for c in cut: U=U-c
m=U.to_mesh(); T=trimesh.Trimesh(m.vert_properties[:,:3],m.tri_verts)
print('watertight',T.is_watertight,'parts',len(T.split()),'vol cm3',round(T.volume/1000,2),'mass g (PETG 1.27)',round(T.volume*1.27e-3,1),'bbox',T.bounds.round(1).tolist())
T.export(OUT+'_phoneframe.stl')
W=T.copy(); W.apply_transform(trimesh.transformations.rotation_matrix(-t,[0,1,0])); W.export(OUT+'_world.stl')
