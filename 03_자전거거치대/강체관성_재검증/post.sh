#!/bin/bash
# 사용: post.sh TAG [XP]  → STL, 1 mm 필드, 시스템 FRF
T=$1; X=${2:-90}; cd /tmp/claude-0/-home-claude/e964ed80-ee1b-5f91-abd3-3081682a3ad7/scratchpad/opt
XP=$X python3 -c "
import numpy as np
from eval3d import nx,nz
r=np.load('rprint_$T.npy'); full=np.zeros((nz,20,nx)); full[:,5:,:]=r.reshape(nz,15,nx); np.save('rprint_${T}_full.npy',full.ravel())"
XP=$X FULL=1 SIG=1.0 ISO=0.42 python3 mkstl3d.py rprint_${T}_full.npy 0.5 ${T}_i0.42.stl > /dev/null
python3 -c "
import numpy as np
f=np.load('${T}_i0.42_field.npy'); S=f[::2,::2,::2]>0.42; np.savez('field_$T.npz',S=S,origin=np.array([-26.,33.,-38.]))"
XP=$X FRF=frf_$T.json MSYS=0.340 python3 verify_sys.py field_$T.npz | tail -1
XP=$X DIR=x FRF=frfx_$T.json MSYS=0.340 python3 verify_sys.py field_$T.npz | tail -1
