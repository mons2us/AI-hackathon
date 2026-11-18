import asyncio, os, json
from playwright.async_api import async_playwright
D=os.path.dirname(os.path.abspath(__file__))
A=json.load(open(os.path.join(D,'anchors.json')))
CAM=dict(pos=[300,-620,140],tgt=[40,0,30],fov=17)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        pg=await b.new_page(viewport={"width":1600,"height":1000})
        async def route(r):
            fn=r.request.url.split('test.local/')[-1] or 'scene.html'
            ct={'html':'text/html; charset=utf-8','js':'text/javascript','json':'application/json'}[fn.rsplit('.',1)[-1]]
            await r.fulfill(path=os.path.join(D,fn),content_type=ct)
        await pg.route("**/*",route)
        await pg.goto("https://test.local/scene.html"); await pg.wait_for_function("window.ready===true",timeout=120000)
        out={}
        for k in ['base','body']:
            await pg.evaluate(f"shot({json.dumps([k+'_R','bar','phone'])},{CAM['pos']},{CAM['tgt']},{CAM['fov']})"); await pg.wait_for_timeout(200)
            await pg.locator('canvas').screenshot(path=os.path.join(D,f'L_{k}.png'))
            out[k]=await pg.evaluate(f"proj({json.dumps([a[2] for a in A[k]])})")
        json.dump(out,open(os.path.join(D,'proj.json'),'w'))
        await b.close()
asyncio.run(main())
