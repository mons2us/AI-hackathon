import numpy as np, glob, subprocess, json, base64, trimesh, os, re
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from eval3d import nx,ny,nz
L={json.loads(l)['it']:json.loads(l) for l in open('am2s.log') if l.startswith('{')}
b64=lambda a: base64.b64encode(np.asarray(a,np.float32).tobytes()).decode()
J=json.load(open('../render/meshes_bike.json')); keys=[]; meta=[]
for f in sorted(glob.glob('snap_am2s_*.npy')):
    it=int(re.findall(r'(\d+)\.npy',f)[0]); r=np.load(f).reshape(nz,15,nx); full=np.zeros((nz,20,nx)); full[:,5:,:]=r
    np.save('evo_full.npy',full.ravel())
    out=subprocess.run(['python3','mkstl3d.py','evo_full.npy','0.5','evo_%03d.stl'%it],env=dict(os.environ,FULL='1',SIG='1.0',ISO='0.42' if it==159 else '0.5'),capture_output=True,text=True).stdout
    m=trimesh.load('evo_%03d.stl'%it)
    try: m=m.simplify_quadric_decimation(face_count=30000)
    except Exception: pass
    k='E%03d'%it; J[k]=dict(pos=b64(m.vertices[m.faces].reshape(-1,3))); keys.append(k)
    meta.append(dict(it=it,mass=L[it]['mass_g'],f1=L[it]['f'][0])); print(meta[-1],flush=True)
json.dump(J,open('../render/meshes_bike.json','w')); json.dump(meta,open('evo_meta.json','w'))
s=open('../render/bike.html').read()
s=re.sub(r"for\(const k of \['am','am2'\]\)\{","for(const k of Object.keys(J).filter(q=>/^E\\d{3}$/.test(q))){ mk(k,J[k],tealMat); } for(const k of ['am','am2']){",s,count=1) if 'E\\d{3}' not in s else s
open('../render/bike.html','w').write(s)
c=open('../render/cap_iso.py').read()
c=re.sub(r'^V=.*$','V=['+','.join('("%s",["%s","bar"],False,[330,900,420],[45,58,-4],11.5)'%(k,k) for k in keys)+']',c,flags=re.M)
open('../render/cap_evo.py','w').write(c); print('ok')
