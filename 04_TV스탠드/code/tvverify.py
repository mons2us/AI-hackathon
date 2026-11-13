# full-model output-shape verification at h=6.25 mm (2x finer than design grid)
import numpy as np, scipy.sparse as sp, json, os, sys, gc
from scipy import ndimage as ndi
import pypardiso
from fem3d import hex8_KB
TAG=os.environ.get('TAG','a'); ETA=float(os.environ.get('ETA','0.5'))
src=open('tvopt.py').read()
# reuse geometry/filter definitions from tvopt (stop before analysis loop)
exec(src.split('P=3.; EMIN')[0].replace("print('design'","pass#"))
x=np.load('x_%s.npy'%TAG); xt=np.asarray(Hf@x).ravel()/Hs; xb=proj(xt,16.,ETA)
rho_h=np.zeros(len(ei)); rho_h[didx]=xb; rho_h[solid]=1
F=rho_h.reshape(nz,ny,nx); T=tv.reshape(nz,ny,nx).astype(float); S=solid.reshape(nz,ny,nx).astype(float)
full=lambda A:np.concatenate([A[:,:,::-1],A],2)        # x mirror -> [-250,250]
F,T,S=full(F),full(T),full(S)
up=lambda A,o:ndi.zoom(A,2,order=o)
Ff=up(F,1)>0.5; Tf=up(T,0)>0.5; Sf=up(S,0)>0.5
metal=(Ff|Sf)&~Tf
lab,n=ndi.label(metal|Tf); keep=np.unique(lab[0][Sf[0]]); keep=keep[keep>0]
metal&=np.isin(lab,keep)
h2=h/2; E_=68900.; KE2,C2,B02,xi2=hex8_KB(E_,0.33,h2)
nz2,ny2,nx2=metal.shape; X0,Y0,Z0=-250.,y0,z0
kk,jj,ii=np.where(metal|Tf); typ=np.where(Tf[kk,jj,ii],100.,1.)
NX,NY=nx2+1,ny2+1; nidf=lambda i,j,k:(k*NY+j)*NX+i; cor=((xi2+1)/2).astype(int)
en=np.stack([nidf(ii+c[0],jj+c[1],kk+c[2]) for c in cor],1); edof=np.stack([3*en,3*en+1,3*en+2],2).reshape(len(ii),24)
nn=NX*NY*(nz2+1); gi=np.arange(nn)%NX; gj=(np.arange(nn)//NX)%NY; gk=np.arange(nn)//(NX*NY)
nzc_=Z0+h2*gk
used=np.zeros(nn,bool); used[en.ravel()]=True
isfoot=Sf[kk,jj,ii]&(kk==0)
fixn=np.unique(en[isfoot][:,:4].ravel())
tvn_=np.unique(en[typ==100.].ravel()); wt_=np.ones(len(tvn_))/len(tvn_); dz=nzc_[tvn_]-nzc_[tvn_]@wt_
WT=20.8e-3*9810.; F13_=0.13*(20.8+3.0)*9.81; M=F13_*(890.-474.)
a_=M/((wt_*dz**2).sum())
Fl=np.zeros((3*nn,3)); Fl[3*tvn_+2,0]=-wt_*WT; Fl[3*tvn_+1,1]=wt_*F13_+wt_*a_*dz; Fl[3*tvn_,2]=wt_*F13_+wt_*a_*dz
Kg=sp.coo_matrix(((KE2.ravel()[None,:]*typ[:,None]).ravel(),(np.repeat(edof,24,1).ravel(),np.tile(edof,(1,24)).ravel())),shape=(3*nn,3*nn)).tocsr()
fr=np.setdiff1d(np.where(np.repeat(used,3))[0],np.r_[3*fixn,3*fixn+1,3*fixn+2])
A=Kg[fr][:,fr].tocsr(); ps=pypardiso.PyPardisoSolver(); ps.factorize(A)
out=dict(mass_kg=float(metal.sum()*h2**3*2.7e-6),h=h2,eta=ETA,dofs=int(len(fr)))
nm=['sag','u_fb','u_lat']; Fm=[WT,F13_,F13_]; m_el=typ==1.
for c in range(3):
    u=np.zeros(3*nn); u[fr]=ps.solve(A,Fl[fr,c])
    out[nm[c]]=float(Fl[:,c]@u/Fm[c])
    out[nm[c]+'_top']=float(np.abs(u[3*tvn_+[2,1,0][c]][nzc_[tvn_]>=nzc_[tvn_].max()-1]).mean()) if c else float(np.abs(u[3*tvn_+2]).mean())
    ue=u[edof]; s=(C2@B02@ue.T).T; vm=np.sqrt(0.5*((s[:,0]-s[:,1])**2+(s[:,1]-s[:,2])**2+(s[:,2]-s[:,0])**2)+3*(s[:,3:]**2).sum(1))
    out[nm[c]+'_vm999']=float(np.percentile(vm[m_el],99.9)); out[nm[c]+'_vmmax']=float(vm[m_el].max())
    if c==0: np.save('u0_%s.npy'%TAG,u)
ps.free_memory(everything=True)
np.save('metal_%s.npy'%TAG,metal); np.save('tvf_%s.npy'%TAG,Tf); np.save('Ff_%s.npy'%TAG,up(F,1))
json.dump(out,open('verify_%s.json'%TAG,'w'),indent=1); print(json.dumps(out))
