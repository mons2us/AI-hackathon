import asyncio, os
from playwright.async_api import async_playwright
D=os.path.dirname(os.path.abspath(__file__))
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        pg=await b.new_page(viewport={"width":1200,"height":900},device_scale_factor=1.5)
        async def route(r):
            fn=r.request.url.split('test.local/')[-1].split('?')[0]
            ct={'html':'text/html; charset=utf-8','js':'text/javascript','json':'application/json'}.get(fn.rsplit('.',1)[-1],'application/octet-stream')
            await r.fulfill(path=os.path.join(D,fn),content_type=ct)
        await pg.route("**/*",route)
        for k in ['1','2','3','6','0']:
            await pg.goto(f"https://test.local/cpt.html?f=meshes_shint_{k}.json"); await pg.wait_for_function("window.ready===true",timeout=180000)
            await pg.evaluate("bikeVis(false);show(['B','bar']);view([150,-700,200],[55,0,45],12)"); await pg.wait_for_timeout(400)
            await pg.screenshot(path=os.path.join(D,'out',f'shint_{k}.png'))
        await b.close()
asyncio.run(main())
