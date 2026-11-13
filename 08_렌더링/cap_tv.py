import asyncio, os, json
from playwright.async_api import async_playwright
D=os.path.dirname(os.path.abspath(__file__))
V=[("tv_full",["blade3"],True,[1500,-2600,900],[0,0,420],26),("tv_foot",["blade3"],True,[1000,-760,300],[600,0,80],20),
 ("tv_foot_base_S",["blade_base_S"],False,[1150,-820,380],[600,0,60],15),("tv_foot_opt_S",["blade3_S"],False,[1150,-820,380],[600,0,60],15),("tv_foot_opt",["blade3"],False,[1150,-820,380],[600,0,60],15)]
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        pg=await b.new_page(viewport={"width":1600,"height":1000},device_scale_factor=2)
        async def route(r):
            fn=r.request.url.split('test.local/')[-1]
            ct={'html':'text/html; charset=utf-8','js':'text/javascript','json':'application/json','png':'image/png'}[fn.rsplit('.',1)[-1]]
            await r.fulfill(path=os.path.join(D,fn),content_type=ct)
        await pg.route("**/*",route); pg.on('pageerror',lambda e:print('ERR',e))
        await pg.goto("https://test.local/tv.html"); await pg.wait_for_function("window.ready===true",timeout=180000)
        for name,show,phone,pos,tgt,fov in V:
            await pg.evaluate(f"show({json.dumps(show)},{str(phone).lower()});view({pos},{tgt},{fov})"); await pg.wait_for_timeout(400)
            await pg.screenshot(path=os.path.join(D,'out','r_'+name+'.png'))
        await b.close()
asyncio.run(main())
