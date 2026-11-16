import sys; sys.path.insert(0,'.'); import parts as P, cadquery as cq
W=float(sys.argv[1]); L=float(sys.argv[2]); yj=W/2; h=P.XR+L
S=(P.screw3((48,20,24),'x',14).union(P.screw3((48,-20,24),'x',14))   # 집게 잠금 M3 (x' 방향)
   .union(cq.Workplane('XZ').circle(1.5).extrude(-14).translate((140,4,18))))  # 위 걸이 잠금
parts=dict(H=P.H.union(P.HT),K=P.K,J=P.jaw(yj).union(P.jaw(yj,-1)).union(P.tophook(h)),S=P.spring(yj).union(P.spring(yj,-1)),P=P.pin().union(P.pin(-1)).union(S),PH=P.phone(W,L))
for k,v in parts.items():
    cq.exporters.export(v.rotate((0,0,0),(0,1,0),-35),f'w_{k}_{int(W)}.stl',tolerance=0.05)
print('ok')
