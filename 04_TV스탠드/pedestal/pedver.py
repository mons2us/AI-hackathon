import numpy as np, json, sys
exec(open('ped.py').read().split('x=np.full(nv,0.5)')[0])
cols=np.load('ped_cols_%s.npy'%sys.argv[1]); xb=(cols[:,1]>0.5).astype(float)
rb=np.zeros(len(ei)); rb[solid]=1; rb[didx]=P_@xb
U,k=analyse(rb); s,uf,ul=meas(U); mass=2*(rb[active&~tvb].sum())*h**3*rho*1e3
vm=[]
on=(rb>0.5)&active&~tvb
for c in range(3):
    ue=U[:,c][edof[on]]; st=(C@B0@ue.T).T
    v=np.sqrt(0.5*((st[:,0]-st[:,1])**2+(st[:,1]-st[:,2])**2+(st[:,2]-st[:,0])**2)+3*(st[:,3:]**2).sum(1)); vm.append(round(float(np.percentile(v,99.9)),1))
print(json.dumps(dict(mass_kg=round(mass,3),base_plate_kg=round(2*(rb[base].sum())*h**3*rho*1e3,3),sag=round(s,4),utop_fb=round(uf,3),utop_lat=round(ul,3),vm999=vm)))
np.save('ped_bin_%s.npy'%sys.argv[1],np.c_[cols[:,0],xb])
