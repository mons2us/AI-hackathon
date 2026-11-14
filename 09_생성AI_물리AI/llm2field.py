# LLM 단독 설계(JSON 프리미티브) -> 1 mm 격자 필드 npz (verify6 입력)
import numpy as np, json, sys, re
txt=open(sys.argv[1]).read(); m=re.findall(r'```(?:json)?\s*(\{.*?\})\s*```',txt,re.S); J=json.loads(m[-1])
x=np.arange(-26,103,1.)+0.0; y=np.arange(33,78,1.); z=np.arange(-38,27,1.)
X,Y,Z=np.meshgrid(x,y,z,indexing='ij'); S=np.zeros(X.shape,bool)
def prim(p):
    t=p['type']
    if t=='box': a,b=p['min'],p['max']; return (X>=a[0])&(X<=b[0])&(Y>=a[1])&(Y<=b[1])&(Z>=a[2])&(Z<=b[2])
    if t=='cyl_y': cx,cz=p['center_xz']; return ((X-cx)**2+(Z-cz)**2<=p['r']**2)&(Y>=min(p['y']))&(Y<=max(p['y']))
    if t=='rod':
        a=np.array(p['p0'],float); b=np.array(p['p1'],float); P=np.stack([X,Y,Z],-1); ab=b-a
        tt=np.clip(((P-a)@ab)/(ab@ab+1e-9),0,1); d=np.linalg.norm(P-(a+tt[...,None]*ab),axis=-1); return d<=p['r']
    raise ValueError(t)
for p in J['primitives']:
    if p.get('op','add')!='sub': S|=prim(p)
for p in J['primitives']:
    if p.get('op','add')=='sub': S&=~prim(p)
S&=~((X**2+Z**2)<16.1**2)
np.savez(sys.argv[2],S=S,origin=np.array([-26.,33.,-38.]))
print(json.dumps(dict(mass_vox_g=round(float(S.sum()*1.27e-3),1),criteria=J.get('criteria'),predicted=J.get('predicted')),ensure_ascii=False))
