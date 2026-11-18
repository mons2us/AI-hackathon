import asyncio, os
from playwright.async_api import async_playwright
D=os.path.dirname(os.path.abspath(__file__))
REAR=[260,330,200]; TG=[0,0,55]; FRONT=[-230,-360,230]
V=[("opt_mat_phone","opt_mat",True,FRONT,TG,26),("opt_mat_rear","opt_mat",False,REAR,TG,24)]
for d in ['plastic','fullal','opt']: V.append((d+"_T_rear",d+"_T",False,REAR,TG,24)); V.append((d+"_T_side",d+"_T",False,[0,420,120],[0,0,55],22))
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
        for name,k,phone,pos,tgt,fov in V:
            await pg.evaluate(f"show('{k}',{str(phone).lower()});view({pos},{tgt},{fov})"); await pg.wait_for_timeout(300)
            await pg.screenshot(path=os.path.join(D,'..','..','deck','shots','wc_'+name+'.png'))
        await b.close()
asyncio.run(main())
