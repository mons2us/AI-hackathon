# 형상 AI: DeepSDF 방식 auto-decoder (잠재 벡터 z + 좌표 -> 점유 확률)
import numpy as np, jax, jax.numpy as jnp, optax, time, sys, pickle
from common import *
LD=16; NF=6
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
