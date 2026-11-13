import numpy as np, scipy.sparse as sp
_xi=np.array([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]],float)
def hex8_cond(k,h):
    """8x8 conduction matrix for a cube element of size h (2x2x2 Gauss)."""
    g=1/np.sqrt(3); Ke=np.zeros((8,8))
    for a in (-g,g):
        for b in (-g,g):
            for c in (-g,g):
                p=(a,b,c); dN=np.array([[x[0]*(1+x[1]*p[1])*(1+x[2]*p[2]),x[1]*(1+x[0]*p[0])*(1+x[2]*p[2]),x[2]*(1+x[0]*p[0])*(1+x[1]*p[1])] for x in _xi])/8*(2/h)
                Ke+=k*dN@dN.T*(h/2)**3
    return Ke
def quad_mass(h):
    """4x4 consistent face matrix  ∫N^T N dA  for a square face of size h."""
    return h*h/36*np.array([[4,2,1,2],[2,4,2,1],[1,2,4,2],[2,1,2,4]],float)
# local node indices of the 6 faces (ordered around the face)
FACES={(-1,0,0):[0,3,7,4],(1,0,0):[1,2,6,5],(0,-1,0):[0,1,5,4],(0,1,0):[3,2,6,7],(0,0,-1):[0,1,2,3],(0,0,1):[4,5,6,7]}
