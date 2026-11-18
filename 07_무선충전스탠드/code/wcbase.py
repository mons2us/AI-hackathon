import numpy as np, json, sys
from wcfem import *
for nm,val in (('plastic_only',0.0),('full_al',1.0)):
    rho=np.zeros(len(ei)); rho[design]=val
    for Q in (3.0,5.0):
        T,_=thermal(rho,Q); dT=T[cn]
        U,_=struct(rho); tap=FS[:,1]@U[:,1]/2.5
        print(json.dumps(dict(design=nm,Q=Q,al_mass_g=round(2*val*design.sum()*h**3*2.7e-3,1),contact_Tmax_C=round(25+dT.max(),1),contact_Tmean_C=round(25+dT.mean(),1),Tmax_all=round(25+T.max(),1),tap_defl_mm=round(tap,4))))
