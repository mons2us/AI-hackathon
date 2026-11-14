import numpy as np, sys, json, time
sys.path.insert(0,'../opt')
from gen import sample
from eval3d import evaluate, design
N=int(sys.argv[1]); seed=int(sys.argv[2]); out=sys.argv[3]
rng=np.random.default_rng(seed); O=[];L=[]; t0=time.time()
for i in range(N):
    o=sample(rng)
    if o.sum()<50: continue
    try: r,_=evaluate(o)
    except Exception as e: print('fail',e); continue
    O.append(np.packbits(o[design])); L.append([r['mass'],r['f'][0],r['f'][1],max(r['vmz'],r['vmy'])])
    if len(O)%25==0:
        np.savez(out,occ=np.array(O),lab=np.array(L)); print(len(O),round(time.time()-t0),flush=True)
np.savez(out,occ=np.array(O),lab=np.array(L)); print('done',len(O),round(time.time()-t0))
