import numpy as np, json
exec(open('plate.py').read().split('x=np.full(nd,0.4)')[0])
Y=yc.reshape(nz,ny); Z=zc.reshape(nz,ny)
designs={'T_web40':(np.abs(Y)<=20)|(Z<=10), 'T_web60':(np.abs(Y)<=30)|(Z<=10)}
for nm,m in designs.items():
    rb=np.where(m.ravel(),1.0,1e-9); U=solve(rb); s,ut,s3=measures(U); np.save('bin_%s.npy'%nm,m)
    print(json.dumps(dict(name=nm,mass_g=round(m.sum()*h*h*t*rho*1e6,1),sag=round(s,4),utop=round(ut,3),sag_lat=round(s3,4))))
