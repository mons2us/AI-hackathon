# LLM 단독 일체형 설계(JSON 프리미티브, 폰 좌표) -> opt_int 격자 rho (nz,ny,nx)=(37,20,88), 절반 y>=0, 셀 2 mm, 셀당 8점 샘플
import numpy as np, json, sys, re
txt=open(sys.argv[1]).read(); m=re.findall(r'```(?:json)?\s*(\{.*?\})\s*```',txt,re.S); J=json.loads(m[-1])
nx,ny,nz=88,20,37; x0,y0,z0=-24.,0.,-36.
K,Jj,I=np.meshgrid(np.arange(nz),np.arange(ny),np.arange(nx),indexing='ij')
acc=np.zeros(K.shape)
for dx in (-.5,.5):
  for dy in (-.5,.5):
    for dz in (-.5,.5):
      X=x0+2*I+1+dx; Y=y0+2*Jj+1+dy; Z=z0+2*K+1+dz
      def prim(p):
        t=p['type']
        if t=='box': a,b=p['min'],p['max']; return (X>=min(a[0],b[0]))&(X<=max(a[0],b[0]))&(Y>=min(a[1],b[1]))&(Y<=max(a[1],b[1]))&(Z>=min(a[2],b[2]))&(Z<=max(a[2],b[2]))
        if t=='cyl_y': cx,cz=p['center_xz']; return ((X-cx)**2+(Z-cz)**2<=p['r']**2)&(Y>=min(p['y']))&(Y<=max(p['y']))
        if t=='rod':
          a=np.array(p['p0'],float); b=np.array(p['p1'],float); P=np.stack([X,Y,Z],-1); ab=b-a
          tt=np.clip(((P-a)@ab)/(ab@ab+1e-9),0,1); return np.linalg.norm(P-(a+tt[...,None]*ab),axis=-1)<=p['r']
        raise ValueError(t)
      S=np.zeros(K.shape,bool)
      for p in J['primitives']:
        if p.get('op','add')!='sub': S|=prim(p)
      for p in J['primitives']:
        if p.get('op','add')=='sub': S&=~prim(p)
      acc+=S
r=(acc/8>=0.5).astype(float).ravel(); np.save(sys.argv[2],r)
print(json.dumps(dict(cells=int(r.sum()),criteria=J.get('criteria'),predicted=J.get('predicted')),ensure_ascii=False))
