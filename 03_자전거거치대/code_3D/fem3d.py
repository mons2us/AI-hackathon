import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla
def hex8_KB(E,nu,h):
    C=E/((1+nu)*(1-2*nu))*np.array([[1-nu,nu,nu,0,0,0],[nu,1-nu,nu,0,0,0],[nu,nu,1-nu,0,0,0],[0,0,0,(1-2*nu)/2,0,0],[0,0,0,0,(1-2*nu)/2,0],[0,0,0,0,0,(1-2*nu)/2]])
    xi=np.array([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]],float)
    g=1/np.sqrt(3);K=np.zeros((24,24))
    def B(p):
        dN=np.array([[xi[a,0]*(1+xi[a,1]*p[1])*(1+xi[a,2]*p[2]),xi[a,1]*(1+xi[a,0]*p[0])*(1+xi[a,2]*p[2]),xi[a,2]*(1+xi[a,0]*p[0])*(1+xi[a,1]*p[1])] for a in range(8)])/8*(2/h)
        Bm=np.zeros((6,24))
        for a in range(8):
            x,y,z=dN[a];i=3*a
            Bm[0,i]=x;Bm[1,i+1]=y;Bm[2,i+2]=z;Bm[3,i]=y;Bm[3,i+1]=x;Bm[4,i+1]=z;Bm[4,i+2]=y;Bm[5,i]=z;Bm[5,i+2]=x
        return Bm
    for a in (-g,g):
        for b in (-g,g):
            for c in (-g,g):
                Bm=B((a,b,c));K+=Bm.T@C@Bm*(h/2)**3
    return K,C,B((0,0,0)),xi
class Grid:
    def __init__(s,nx,ny,nz,h,E,nu):
        s.nx,s.ny,s.nz,s.h=nx,ny,nz,h
        s.KE,s.C,s.B0,xi=hex8_KB(E,nu,h)
        nid=lambda i,j,k:(k*(ny+1)+j)*(nx+1)+i
        s.nid=nid;s.nn=(nx+1)*(ny+1)*(nz+1);s.ndof=3*s.nn
        E_=[];
        for k in range(nz):
            for j in range(ny):
                for i in range(nx):
                    ns=[nid(i+int((x+1)/2),j+int((y+1)/2),k+int((z+1)/2)) for x,y,z in xi]
                    E_.append(np.array([[3*n,3*n+1,3*n+2] for n in ns]).ravel())
        s.edof=np.array(E_);s.ne=len(E_)
        s.iK=np.kron(s.edof,np.ones((24,1))).ravel();s.jK=np.kron(s.edof,np.ones((1,24))).ravel()
    def eidx(s,i,j,k): return (k*s.ny+j)*s.nx+i
    def K(s,ke):
        v=(s.KE.ravel()[None,:]*ke[:,None]).ravel()
        return sp.coo_matrix((v,(s.iK,s.jK)),shape=(s.ndof,s.ndof)).tocsc()
    def Mlump(s,me,extra=None):
        m=np.zeros(s.nn)
        en=s.edof[:,::3]//3
        np.add.at(m,en.ravel(),np.repeat(me/8,8))
        if extra is not None: m+=extra
        return np.repeat(m,3)
