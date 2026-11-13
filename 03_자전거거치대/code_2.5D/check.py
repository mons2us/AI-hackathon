import numpy as np, json, sys
from model2 import *
PEAK=48.5; YIELD=39.; INTER=16.4; SF=1.5; FEX=45.6
s=np.load(sys.argv[1]); res,X=evaluate(s,5.)
U=X['U']; on=X['on']&~post
out=dict(file=sys.argv[1],mass=round(res['mass'],1),f1=round(res['f'][0],1),f2=round(res['f'][1],1))
for lc,name in ((0,'z'),(1,'y')):
    ue=U[:,lc][G.edof]; sg=(G.C@G.B0@ue.T).T*(PEAK/5.)
    vm=np.sqrt(0.5*((sg[:,0]-sg[:,1])**2+(sg[:,1]-sg[:,2])**2+(sg[:,2]-sg[:,0])**2)+3*(sg[:,3:]**2).sum(1))
    ok=on&~root
    out['vm_'+name]=round(float(vm[ok].max()),1); out['syy_'+name]=round(float(np.maximum(sg[ok,1],0).max()),1)
r=FEX/res['f'][0]; out['amp']=round(1/abs(1-r*r),2)
out['pass_f']=res['f'][0]>=2*FEX; out['pass_vm']=max(out['vm_z'],out['vm_y'])<=YIELD/SF; out['pass_inter']=max(out['syy_z'],out['syy_y'])<=INTER/SF
print(json.dumps(out))
