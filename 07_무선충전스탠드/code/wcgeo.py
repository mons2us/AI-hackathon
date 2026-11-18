# geometry of the wireless-charging stand problem (half model x>=0), units mm
import numpy as np
h=2.5; HX,LY,HZ=37.5,122.5,115.0          # half width, depth, height (EP-N5200 envelope 75.3 x 122.2 x 114.5)
nx,ny,nz=int(HX/h),int(LY/h),int(HZ/h)
Y0=-LY/2
ANG=np.deg2rad(70.)                       # phone lean angle from horizontal (assumed)
def front_y(z): return -40.+(z-10.)/np.tan(ANG)   # front (phone-contact) surface line
ei=np.array([[i,j,k] for k in range(nz) for j in range(ny) for i in range(nx)]); I,J,K=ei.T
xc=h*(I+.5); yc=Y0+h*(J+.5); zc=h*(K+.5)
nvec=np.array([0.,-np.sin(ANG),np.cos(ANG)])       # outward normal of the front surface (pointing to the phone)
nvec=np.array([0.,-np.sin(ANG),np.cos(ANG)]); nvec=np.array([0.,-np.sin(ANG),np.cos(ANG)])
# signed distance behind the front surface (positive = inside stand)
t_dir=np.array([0.,np.cos(ANG),np.sin(ANG)])        # along the surface (up-back)
nrm=np.array([0.,np.sin(ANG),-np.cos(ANG)])          # into the stand (back-down)
ZC0=70.; P0=np.array([0.,front_y(ZC0),ZC0])         # coil centre on the surface (assumed height)
rel=np.c_[xc,yc,zc]-P0
dep=rel@nrm                                          # depth behind surface
s_along=rel@t_dir
rad=np.sqrt(xc**2+s_along**2)                        # in-plane radius from coil axis
base=zc<8.
behind=(yc>=front_y(zc))&(zc>=8.)
body=behind|base
skin=behind&(yc<front_y(zc)+2.6)                     # 2.5 mm plastic contact cover
RCOIL=22.5; RKO=RCOIL+10.; DKO=12.                   # coil radius, keep-out radius & depth (assumed)
keep=body&(rad<RKO)&(dep<DKO)&~skin                  # non-metal zone (thermally conductive plastic)
coil=keep&(rad<RCOIL)&(dep<5.5)&(dep>=2.6)           # heat source region
ledge=(zc>=8.)&(zc<20.)&(yc<front_y(zc))&(yc>front_y(zc)-10.)
pads=base&(np.abs(np.abs(yc)-(LY/2-8.))<=6.)&(xc>=HX-12.)
design=body&~(skin|keep|pads)
fixedplastic=skin|keep|ledge
allsolid=body|ledge
