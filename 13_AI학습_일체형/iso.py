# 몸체 STL → 등각 투상 렌더 (회색 음영, 흰 바탕)
import trimesh, numpy as np, base64, json, asyncio, os, shutil, sys
T=trimesh.load(sys.argv[1]); P=T.vertices[T.faces].reshape(-1).astype(np.float32)
json.dump({'b':base64.b64encode(P.tobytes()).decode()},open('m.json','w'))
shutil.copy('../cmp/three.min.js','three.min.js')
open('iso.html','w').write('''<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:#fff}</style></head><body>
<script src="three.min.js"></script><script>
const W=1400,H=1000;const r=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});r.setSize(W,H);r.setClearColor(0xffffff);document.body.appendChild(r.domElement);
const sc=new THREE.Scene();const cam=new THREE.OrthographicCamera(-W/2,W/2,H/2,-H/2,-5000,5000);cam.up.set(0,0,1);
sc.add(new THREE.HemisphereLight(0xffffff,0x606870,0.55));const d=new THREE.DirectionalLight(0xffffff,0.75);d.position.set(300,-500,700);sc.add(d);const d2=new THREE.DirectionalLight(0xffffff,0.3);d2.position.set(-400,300,200);sc.add(d2);
fetch('m.json').then(x=>x.json()).then(M=>{const b=atob(M.b),u=new Uint8Array(b.length);for(let i=0;i<b.length;i++)u[i]=b.charCodeAt(i);
const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(new Float32Array(u.buffer),3));g.computeVertexNormals();
const m=new THREE.Mesh(g,new THREE.MeshStandardMaterial({color:0xb4bec8,roughness:.6,metalness:.05,side:THREE.DoubleSide}));sc.add(m);
const e=new THREE.LineSegments(new THREE.EdgesGeometry(g,35),new THREE.LineBasicMaterial({color:0x1a1a1a}));sc.add(e);
g.computeBoundingBox();const c=g.boundingBox.getCenter(new THREE.Vector3());const dir=new THREE.Vector3(...(window.DIR||[1,-1,1])).normalize();
cam.position.copy(c.clone().add(dir.multiplyScalar(1000)));cam.lookAt(c);cam.zoom=4.2;cam.updateProjectionMatrix();r.render(sc,cam);window.ready=true;});
</script></body></html>''')
from playwright.async_api import async_playwright
async def m():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"]); pg=await b.new_page(viewport={"width":1400,"height":1000})
        async def route(rq):
            fn=rq.request.url.split('test.local/')[-1]; ct={'html':'text/html','js':'text/javascript','json':'application/json'}[fn.rsplit('.',1)[-1]]
            await rq.fulfill(path=os.path.abspath(fn),content_type=ct)
        await pg.route("**/*",route)
        for i,dv in enumerate([[0.6,-1,-0.45],[-0.5,-1,0.35],[0.9,-1,0.25]]):
            await pg.add_init_script(f"window.DIR={dv}"); await pg.goto("https://test.local/iso.html"); await pg.wait_for_function("window.ready===true",timeout=120000)
            await pg.locator('canvas').screenshot(path=f'iso{i}.png')
        await b.close()
asyncio.run(m())
