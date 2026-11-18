import asyncio, os, json
from playwright.async_api import async_playwright
D=os.path.dirname(os.path.abspath(__file__))
V=[("tv_full","c",True,[1500,-2600,900],[0,0,420],26),("tv_foot","c",True,[900,-700,260],[600,0,70],22),
   ("foot_opt","c",False,[900,-650,320],[600,0,55],17),("foot_base","T_web40",False,[900,-650,320],[600,0,55],17)]
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        pg=await b.new_page(viewport={"width":1600,"height":1000},device_scale_factor=2)
        async def route(r):
            fn=r.request.url.split('test.local/')[-1] or 'scene.html'
            ct={'html':'text/html; charset=utf-8','js':'text/javascript','json':'application/json'}[fn.rsplit('.',1)[-1]]
            await r.fulfill(path=os.path.join(D,fn),content_type=ct)
        await pg.route("**/*",route)
        await pg.goto("https://test.local/scene.html"); await pg.wait_for_function("window.ready===true",timeout=120000)
        for name,k,tvon,pos,tgt,fov in V:
            await pg.evaluate(f"show('{k}',{str(tvon).lower()});view({pos},{tgt},{fov})"); await pg.wait_for_timeout(300)
            await pg.screenshot(path=os.path.join(D,'..','..','deck','shots','tv_'+name+'.png'))
        await b.close()
asyncio.run(main())
