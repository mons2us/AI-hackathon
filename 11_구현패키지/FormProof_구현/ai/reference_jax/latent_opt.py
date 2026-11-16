# 잠재 공간 최적화: 형상 AI(z→형상) + 물리 AI(형상→f1) 미분으로 '가볍고 f1≥목표' 후보 탐색 → FEM 판정
import numpy as np, jax, jax.numpy as jnp, optax, pickle, time, json, sys
from common import *
sys.path.insert(0,'../opt')
from eval3d import evaluate, clean, solid
import shape_ai_lib as SA, phys_ai_lib as PA
S=pickle.load(open('shape.pkl','rb')); Pm=pickle.load(open('phys.pkl','rb'))
occ,lab=load('data.npz'); P=jnp.asarray(PTS); NS=float(solid.sum())
FT=float(sys.argv[1]) if len(sys.argv)>1 else 100.
def occ_of(z): return jax.nn.sigmoid(SA.dec(S['net'],z,P)*2.0)
def f1_of(o): out=PA.net(Pm['ps'],to_grid(o[None]))[0]; return jnp.exp(out[0]*Pm['sd'][0]+Pm['mu'][0])
def mass_of(o): return (o.sum()+NS)*8*1.27e-3
def obj(z):
    o=occ_of(z); f=f1_of(o); return mass_of(o)+3.0*jax.nn.relu(FT-f)**2/FT+1e-2*jnp.sum(z**2), (mass_of(o),f)
g=jax.jit(jax.value_and_grad(obj,has_aux=True))
feas=np.where(lab[:,1]>=91)[0]; best=feas[np.argsort(lab[feas,0])][:6]
print('data best feasible', [(round(lab[i,0],1),round(lab[i,1],1)) for i in best[:3]])
res=[]; t0=time.time()
for k,i in enumerate(best):
    z=jnp.asarray(S['z'][i]); opt=optax.adam(0.02); st=opt.init(z); ts=time.time()
    for it in range(150):
        (l,(m,f)),gr=g(z); u,st=opt.update(gr,st); z=optax.apply_updates(z,u)
    tsearch=time.time()-ts
    o=np.asarray(occ_of(z))>0.5; full=np.zeros(len(design),bool); full[DI]=o; sd=clean(full)
    r,_=evaluate(sd)
    res.append(dict(start=int(i),start_mass=float(lab[i,0]),start_f1=float(lab[i,1]),pred_mass=float(m),pred_f1=float(f),fem_mass=r['mass'],fem_f1=r['f'][0],search_s=tsearch))
    np.save('cand_%d.npy'%k,sd.astype(np.float32)); print(json.dumps(res[-1]),flush=True)
json.dump(res,open('latent_res.json','w'),indent=1); print('total',round(time.time()-t0))
