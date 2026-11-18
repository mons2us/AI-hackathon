import asyncio, os, sys, json
from playwright.async_api import async_playwright
D=os.path.dirname(os.path.abspath(__file__))
V=json.load(open(os.path.join(D,'views.json')))
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        pg=await b.new_page(viewport={"width":1600,"height":1000})
        async def route(r):
            fn=r.request.url.split('test.local/')[-1] or 'scene.html'
            ct={'html':'text/html; charset=utf-8','js':'text/javascript','json':'application/json'}[fn.rsplit('.',1)[-1]]
            await r.fulfill(path=os.path.join(D,fn),content_type=ct)
        await pg.route("**/*",route); pg.on('console',lambda m: print('console',m.text))
        await pg.goto("https://test.local/scene.html"); await pg.wait_for_function("window.ready===true",timeout=120000)
        for v in V:
            await pg.evaluate(f"shot({json.dumps(v['show'])},{v['pos']},{v['tgt']},{v['fov']})"); await pg.wait_for_timeout(200)
            await pg.locator('canvas').screenshot(path=os.path.join(D,v['name']+'.png'))
        await b.close()
asyncio.run(main())
