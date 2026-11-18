# Wireless-charging stand HEAD (panel-aligned frame): u = width (half, symmetry at u=0), v = up along panel, w = depth (0 = phone side)
import numpy as np, scipy.sparse as sp, pypardiso, os
from thermal3d import hex8_cond, quad_mass, FACES
h=1.25; HU,HV,HW=37.5,115.0,25.0
nu_,nv,nw=int(HU/h),int(HV/h),int(HW/h)
ei=np.array([[i,j,k] for k in range(nw) for j in range(nv) for i in range(nu_)]); I,J,K=ei.T
uc=h*(I+.5); vc=h*(J+.5); wc=h*(K+.5)
SH=2.5                                                     # PC/ABS housing wall
shell=(wc<SH)|(wc>HW-SH)|(uc>HU-SH)|(vc<SH)|(vc>HV-SH)
front=shell&(wc<SH)                                         # phone-contact cover
COILS=[float(c) for c in os.environ.get('COILV','42,78').split(',')]; RC=22.0
rcoil=np.min([np.sqrt(uc**2+(vc-c)**2) for c in COILS],0)
coil=(wc>=SH)&(wc<SH+2.5)&(rcoil<RC)                        # litz coil layer 2.5 mm
ferr=(wc>=SH+2.5)&(wc<SH+3.75)&(uc<30)&(vc>14)&(vc<106)      # ferrite sheet 1.25 mm
pcb=(wc>=HW-SH-2.5)&(wc<HW-SH-1.25)&(uc<28)&(vc>12)&(vc<60)  # PCB bonded to back spreader via thermal pad
mosf=pcb&(uc<8)&(vc>30)&(vc<40)                             # inverter MOSFET / controller hot spot
layA=(wc>=SH+3.75)&(wc<SH+5.0)&~shell                       # design sheet A: behind ferrite (1.25 mm)
layB=(wc>=HW-SH-1.25)&(wc<HW-SH)&~shell                     # design sheet B: inside back wall (1.25 mm)
design=(layA|layB)
air=~(shell|coil|ferr|pcb|design)
K_PC,K_AIR,K_COIL,K_FER,K_PCB,K_AL=0.2e-3,0.026e-3,1.0e-3,4.0e-3,3.0e-3,167e-3   # W/mmK (assumed effective values)
HC=float(os.environ.get('HC','15'))*1e-6   # natural convection ~10 + radiation ~5 (assumed)
NU,NV,NW=nu_+1,nv+1,nw+1; nid=lambda i,j,k:(k*NV+j)*NU+i
_xi=np.array([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]]); cor=((_xi+1)/2).astype(int)
en=np.stack([nid(I+c[0],J+c[1],K+c[2]) for c in cor],1); nn=NU*NV*NW
gi=np.arange(nn)%NU; gj=(np.arange(nn)//NU)%NV; gk=np.arange(nn)//(NU*NV)
KT=hex8_cond(1.0,h); MF=quad_mass(h)
iT=np.repeat(en,8,1).ravel(); jT=np.tile(en,(1,8)).ravel()
# convection on outer faces: back (w=HW), side (u=HU), top (v=HV); front = phone covered (adiabatic); bottom joins base (adiabatic)
cf=[]
for e in np.where(shell)[0]:
    i,j,k=I[e],J[e],K[e]
    if k==nw-1: cf.append(en[e][FACES[(0,0,1)]])
    if i==nu_-1: cf.append(en[e][FACES[(1,0,0)]])
    if j==nv-1: cf.append(en[e][FACES[(0,1,0)]])
cf=np.array(cf); iF=np.repeat(cf,4,1).ravel(); jF=np.tile(cf,(1,4)).ravel()
Hconv=sp.csr_matrix((np.tile((HC*MF).ravel(),len(cf)),(iF,jF)),shape=(nn,nn))
QC=float(os.environ.get('QC','2.0')); QP=float(os.environ.get('QP','1.5'))   # W, full model (assumed TX-side losses)
def qvec():
    q=np.zeros(nn)
    for m,Q in ((coil,QC),(mosf,QP)):
        idx=np.where(m)[0]; np.add.at(q,en[idx].ravel(),Q/2/len(idx)/8)
    return q
Q=qvec()
fn=np.unique(en[np.where(front)[0]][:,[0,1,2,3]].ravel()); fn=fn[gk[fn]==0]       # phone-contact outer surface nodes
tn=np.unique(cf.ravel())                                                          # touchable outer surfaces
P=3.; EMIN=1e-4
def kel(rho):
    k=np.full(len(ei),K_AIR); k[shell]=K_PC; k[coil]=K_COIL; k[ferr]=K_FER; k[pcb]=K_PCB
    k[design]=K_AIR+(K_AL-K_AIR)*rho[design]**P; return k
def solve(rho):
    A=sp.csr_matrix(((KT.ravel()[None,:]*kel(rho)[:,None]).ravel(),(iT,jT)),shape=(nn,nn))+Hconv
    ps=pypardiso.PyPardisoSolver(); ps.factorize(A); T=ps.solve(A,Q); return T,ps,A
