import numpy as np, json
from model2 import *
s=np.zeros(G.ne); s[design&(((K>=6)&(K<=9))|((I>=30)&(K>=6)))]=1; s[root]=1
np.save('v2_clean_base.npy',s); res,_=evaluate(s,5.); res['tag']='base'; print(json.dumps(res))
