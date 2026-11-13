import numpy as np, json
from head import *
cases={'no_spreader':np.zeros(len(ei)),'flatA':np.where(layA,1.,0.),'flatB':np.where(layB,1.,0.),'flatAB':np.where(design,1.,0.)}
for nm,r in cases.items():
    T,ps,A=solve(r); ps.free_memory(everything=True)
    print(json.dumps(dict(case=nm,al_g=round(2*r[design].sum()*h**3*2.7e-3,1),front_max=round(25+T[fn].max(),1),touch_max=round(25+T[tn].max(),1),coil_max=round(25+T[en[coil]].max(),1),pcb_max=round(25+T[en[mosf]].max(),1))))
