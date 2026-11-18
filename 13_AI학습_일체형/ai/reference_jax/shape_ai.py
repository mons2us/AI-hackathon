# 형상 AI: DeepSDF 방식 auto-decoder (잠재 벡터 z + 좌표 -> 점유 확률)
import numpy as np, jax, jax.numpy as jnp, optax, time, sys, pickle
from common import *
occ,lab=load(sys.argv[1]); N=len(occ); LD=16; NF=6
key=jax.random.PRNGKey(0)
def penc(p):
    f=2.**jnp.arange(NF)*jnp.pi; a=p[...,None]*f; return jnp.concatenate([p,jnp.sin(a).reshape(*p.shape[:-1],-1),jnp.cos(a).reshape(*p.shape[:-1],-1)],-1)
DIN=LD+3+3*2*NF; H=[DIN,128,128,128,128,1]
def init(key):
    ps=[]
    for i in range(len(H)-1):
        key,k=jax.random.split(key); ps.append((jax.random.normal(k,(H[i],H[i+1]))*np.sqrt(2/H[i]),jnp.zeros(H[i+1])))
    return ps
def dec(ps,z,p):   # z:(LD,) p:(M,3) -> logits (M,)
    h=jnp.concatenate([jnp.broadcast_to(z,(p.shape[0],LD)),penc(p)],-1)
    for W,b in ps[:-1]: h=jax.nn.softplus(h@W+b)*1.0
    W,b=ps[-1]; return (h@W+b)[:,0]
decB=jax.vmap(dec,(None,0,0))
params={'net':init(key),'z':jnp.zeros((N,LD))+0.01*jax.random.normal(key,(N,LD))}
opt=optax.adam(optax.exponential_decay(2e-3,1500,0.5)); st=opt.init(params)
P=jnp.asarray(PTS); O=jnp.asarray(occ)
def loss(params,idx,pidx):
    z=params['z'][idx]; p=P[pidx]; y=O[idx][:,pidx]
    lg=decB(params['net'],z,jnp.broadcast_to(p,(len(idx),)+p.shape))
    w=1+2*y   # 재료 쪽 가중
    return jnp.mean(w*optax.sigmoid_binary_cross_entropy(lg,y))+1e-3*jnp.mean(z**2)
@jax.jit
def step(params,st,idx,pidx):
    l,g=jax.value_and_grad(loss)(params,idx,pidx); u,st=opt.update(g,st,params); return optax.apply_updates(params,u),st,l
rng=np.random.default_rng(0); t0=time.time(); STEPS=int(sys.argv[3]) if len(sys.argv)>3 else 4000
for it in range(STEPS):
    idx=rng.integers(0,N,16); pidx=rng.integers(0,ND,1024)
    params,st,l=step(params,st,jnp.asarray(idx),jnp.asarray(pidx))
    if it%200==0: print(it,float(l),round(time.time()-t0),flush=True)
# 재구성 정확도 (전체 점)
decf=jax.jit(lambda net,z: dec(net,z,P))
iou=[]
for i in range(min(N,200)):
    pr=np.asarray(decf(params['net'],params['z'][i]))>0; t=occ[i]>0.5; iou.append((pr&t).sum()/max((pr|t).sum(),1))
print('train IoU mean',float(np.mean(iou)),'t',round(time.time()-t0))
pickle.dump({'net':jax.device_get(params['net']),'z':np.asarray(params['z']),'LD':LD,'NF':NF},open(sys.argv[2],'wb'))
