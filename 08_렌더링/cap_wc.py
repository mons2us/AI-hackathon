import asyncio, os, json
from playwright.async_api import async_playwright
D=os.path.dirname(os.path.abspath(__file__))
FR=[-260,-360,230]; RE=[280,330,190]; TG=[0,0,55]
V=[("wc_product",["opt_al"],True,FR,TG,24,"mat"),("wc_rear",["opt_al"],False,RE,TG,24,"mat")]
for d in ['plastic','fullal','opt']: V.append(("wc_T_"+d,([d+"_al_T"] if d!="plastic" else []),False,RE,TG,24,d))
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        pg=await b.new_page(viewport={"width":1600,"height":1000},device_scale_factor=2)
        async def route(r):
            fn=r.request.url.split('test.local/')[-1]
            ct={'html':'text/html; charset=utf-8','js':'text/javascript','json':'application/json','png':'image/png'}[fn.rsplit('.',1)[-1]]
            await r.fulfill(path=os.path.join(D,fn),content_type=ct)
        await pg.route("**/*",route); pg.on('pageerror',lambda e:print('ERR',e))
        await pg.goto("https://test.local/wc.html"); await pg.wait_for_function("window.ready===true && window.metaReady===true",timeout=180000); await pg.wait_for_timeout(1500)
        for name,show,phone,pos,tgt,fov,mode in V:
            await pg.evaluate(f"plastic('{mode}');show({json.dumps(show)},{str(phone).lower()});view({pos},{tgt},{fov})"); await pg.wait_for_timeout(400)
            await pg.screenshot(path=os.path.join(D,'out','r_'+name+'.png'))
        await b.close()
asyncio.run(main())
