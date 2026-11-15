import numpy as np, jax, jax.numpy as jnp
from common import *
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
