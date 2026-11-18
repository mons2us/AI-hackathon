import asyncio, json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        pg=await b.new_page(viewport={"width":1600,"height":900})
        await pg.goto("http://127.0.0.1:8799/?ui=pro&video&optfast=1"); await pg.wait_for_function("S.demos&&S.demos.length>0",timeout=60000)
        await pg.evaluate("playDemo(0,false)"); await pg.wait_for_timeout(500); await pg.wait_for_function("!S.playing",timeout=180000)
        await pg.evaluate("makeSpec(false)"); await pg.wait_for_function("S.spec&&!S.specBusy",timeout=180000); await pg.wait_for_timeout(900)
        await pg.click('#bConfirm'); await pg.wait_for_timeout(1500); await pg.click('#go')
        await pg.wait_for_function("S.rep && S.rows && S.rows.length>0",timeout=500000); await pg.wait_for_timeout(1500)
        await pg.evaluate("S.rows.forEach((m,i)=>{if(m.key&&!m.ok&&!m.ref)S.sel.add(i)}); updateOpt(); drawMetrics();"); await pg.click('#optimize')
        await pg.wait_for_function("document.body.classList.contains('st-done')",timeout=900000); await pg.wait_for_timeout(1500)
        await pg.evaluate("""window.HERO=(ang,el,dist,showPhone)=>{
          if(!window._HR){window._HR=new THREE.WebGLRenderer({antialias:true,alpha:true,preserveDrawingBuffer:true});_HR.setSize(1600,1200);_HR.setPixelRatio(1);
            if(V3.R){_HR.outputEncoding=V3.R.outputEncoding;_HR.toneMapping=V3.R.toneMapping;_HR.toneMappingExposure=V3.R.toneMappingExposure;_HR.outputColorSpace=V3.R.outputColorSpace;}}
          const vis=[];const set=(o,v)=>{if(o){vis.push([o,o.visible]);o.visible=v;}};
          set(V3.bike,false);set(V3.ground,false);set(V3.handlebar,true);set(V3.holder,showPhone);if(V3.ghost)set(V3.ghost,false);
          const bg=V3.scene.background;V3.scene.background=null;
          const c=new THREE.PerspectiveCamera(22,1600/1200,1,20000);c.up.set(0,0,1);
          const t=new THREE.Vector3(38,55,36);const a=ang*Math.PI/180,e=el*Math.PI/180;
          c.position.set(t.x+dist*Math.cos(e)*Math.sin(a),t.y-dist*Math.cos(e)*Math.cos(a),t.z+dist*Math.sin(e));c.lookAt(t);
          _HR.render(V3.scene,c);const u=_HR.domElement.toDataURL('image/png');
          V3.scene.background=bg;vis.reverse().forEach(([o,v])=>o.visible=v);return u;}""")
        import base64, os
        os.makedirs('orb', exist_ok=True)
        keys=await pg.evaluate("Object.keys(V3)"); print(keys)
        for nm,(a0,a1,el,d,ph) in dict(A3=(-70,-12,16,600,True),C3=(-22,-22,12,640,False)).items():
            os.makedirs(nm,exist_ok=True); n=180 if a0!=a1 else 1
            for i in range(n):
                u=await pg.evaluate("([a,e,d,p])=>HERO(a,e,d,p)",[a0+(a1-a0)*i/max(1,n-1), el, d, ph])
                open(f'{nm}/{i:03d}.png','wb').write(base64.b64decode(u.split(',')[1]))
        await b.close()
asyncio.run(main())
