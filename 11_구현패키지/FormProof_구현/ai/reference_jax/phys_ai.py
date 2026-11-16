# 물리 AI: 3D CNN 대리 모델 (점유 격자 -> log f1, log 최대응력)
import numpy as np, jax, jax.numpy as jnp, optax, time, sys, pickle
from common import *
occ,lab=load(sys.argv[1]); N=len(occ)
Y=np.c_[np.log(lab[:,1]),np.log(lab[:,3])].astype(np.float32); mu,sd=Y.mean(0),Y.std(0); Yn=(Y-mu)/sd
rng=np.random.default_rng(1); perm=rng.permutation(N); nte=max(int(0.15*N),20); te,tr=perm[:nte],perm[nte:]
CH=[1,8,16,32,48]
def init(key):
    ps=[]
    for i in range(4):
        key,k=jax.random.split(key); ps.append((jax.random.normal(k,(3,3,3,CH[i],CH[i+1]))*np.sqrt(2/(27*CH[i])),jnp.zeros(CH[i+1])))
    key,k=jax.random.split(key); ps.append((jax.random.normal(k,(CH[-1]*2,64))*np.sqrt(1/CH[-1]),jnp.zeros(64)))
    key,k=jax.random.split(key); ps.append((jax.random.normal(k,(64,2))*0.1,jnp.zeros(2)))
    return ps
def net(ps,g):   # g:(B,nz,ny,nx,1)
    h=g
    for i in range(4):
        W,b=ps[i]; h=jax.lax.conv_general_dilated(h,W,(2,2,2),'SAME',dimension_numbers=('NDHWC','DHWIO','NDHWC'))+b; h=jax.nn.gelu(h)
    h=jnp.concatenate([h.mean((1,2,3)),h.max((1,2,3))],-1)
    W,b=ps[4]; h=jax.nn.gelu(h@W+b); W,b=ps[5]; return h@W+b
def predict(ps,occ_d): return net(ps,to_grid(occ_d))
params=init(jax.random.PRNGKey(2)); opt=optax.adamw(optax.cosine_decay_schedule(2e-3,int(sys.argv[3]) if len(sys.argv)>3 else 3000),weight_decay=1e-4); st=opt.init(params)
O=jnp.asarray(occ); YN=jnp.asarray(Yn)
def loss(ps,idx,flip):
    g=to_grid(O[idx]); g=jnp.where(flip,g[:,:,::-1],g)   # y 대칭 증강
    return jnp.mean((net(ps,g)-YN[idx])**2*jnp.array([1.,0.5]))
@jax.jit
def step(ps,st,idx,flip):
    l,gr=jax.value_and_grad(loss)(ps,idx,flip); u,st=opt.update(gr,st,ps); return optax.apply_updates(ps,u),st,l
pf=jax.jit(predict); t0=time.time(); STEPS=int(sys.argv[3]) if len(sys.argv)>3 else 3000
def evalset(ix):
    out=np.concatenate([np.asarray(pf(params,O[ix[i:i+32]])) for i in range(0,len(ix),32)])
    p=np.exp(out*sd+mu); t=np.exp(Y[ix]); return p,t
for it in range(STEPS):
    idx=rng.choice(tr,24); params,st,l=step(params,st,jnp.asarray(idx),bool(rng.random()<0.5))
    if it%250==0:
        p,t=evalset(te); e=np.abs(p[:,0]/t[:,0]-1); print(it,round(float(l),4),'test f1 err mean %.1f%% p90 %.1f%%'%(100*e.mean(),100*np.percentile(e,90)),round(time.time()-t0),flush=True)
p,t=evalset(te); e1=np.abs(p[:,0]/t[:,0]-1); e2=np.abs(p[:,1]/t[:,1]-1)
tt=time.time(); _=np.asarray(pf(params,O[:1])); tinf=time.time()-tt
res=dict(n_train=len(tr),n_test=len(te),f1_err_mean=float(e1.mean()),f1_err_p90=float(np.percentile(e1,90)),vm_err_mean=float(e2.mean()),infer_s=tinf,train_s=time.time()-t0)
print(res); np.savez(sys.argv[2].replace('.pkl','_test.npz'),pred=p,true=t)
pickle.dump({'ps':jax.device_get(params),'mu':mu,'sd':sd,'res':res},open(sys.argv[2],'wb'))
