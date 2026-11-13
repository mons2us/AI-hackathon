import asyncio,math
from playwright.async_api import async_playwright
F="gaming_stand_v5_rec.html"
CSS=open('rec4b.py').read().split('CSS="""')[1].split('"""')[0]
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        pg=await b.new_page(viewport={"width":1312,"height":900})
        async def route(r):
            u=r.request.url
            if "three.min.js" in u: await r.fulfill(path="libs/package/build/three.min.js",content_type="text/javascript")
            elif "OrbitControls" in u: await r.fulfill(path="libs/package/examples/js/controls/OrbitControls.js",content_type="text/javascript")
            elif "test.local" in u: await r.fulfill(body="<!doctype html><html><head><meta charset='utf-8'></head><body>"+open(F,encoding="utf-8").read()+"</body></html>",content_type="text/html")
            else: await r.fulfill(body="",content_type="text/css")
        await pg.route("**/*",route)
        await pg.goto("https://test.local/");await pg.wait_for_timeout(3000)
        await pg.add_style_tag(content=CSS+".viewer .legend{display:none !important}")
        E=pg.evaluate
        await E("document.getElementById('vP').classList.remove('on');V.phone.forEach(o=>o.visible=false);who='A';flow=true;render();V.phone.forEach(o=>o.visible=false)")
        vw=await pg.query_selector(".viewer")
        async def cam(az,e,r):
            await E(f"(()=>{{const t=new THREE.Vector3(70,40,0),c=__cam;const R=Math.hypot(-285,102,210)*{r};const a={az},e={e};c.position.set(t.x+R*Math.cos(e)*Math.cos(a),t.y+R*Math.sin(e),t.z+R*Math.cos(e)*Math.sin(a));c.lookAt(t);__ctl.target.copy(t);__ctl.update()}})()")
        for t,name in [(0,'open'),(1,'fold')]:
            await E(f"foldT={t};foldTarget={t};applyFold();V.phone.forEach(o=>o.visible=false)")
            await cam(math.pi/2,0.05,0.8);await pg.wait_for_timeout(1500)
            await vw.screenshot(path=f"shots/side_{name}.png")
        await b.close()
asyncio.run(main())
