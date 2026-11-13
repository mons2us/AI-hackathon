import asyncio, os, json
from playwright.async_api import async_playwright
D=os.path.dirname(os.path.abspath(__file__))
FR=[-260,-380,240]; RE=[300,330,230]; TG=[0,0,60]
V=[("wc2_product",[],True,False,FR,TG,24),("wc2_cut_opt",["sheetA","sheetB"],False,True,RE,TG,22),("wc2_cut_flat",["flatA","flatB"],False,True,RE,TG,22),("wc2_cut_none",[],False,True,RE,TG,22),("wc2_cut_front",["sheetA","sheetB"],False,True,[-230,-330,260],TG,22)]
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        pg=await b.new_page(viewport={"width":1600,"height":1000},device_scale_factor=2)
        async def route(r):
            fn=r.request.url.split('test.local/')[-1]
            ct={'html':'text/html; charset=utf-8','js':'text/javascript','json':'application/json','png':'image/png'}[fn.rsplit('.',1)[-1]]
            await r.fulfill(path=os.path.join(D,fn),content_type=ct)
        await pg.route("**/*",route); pg.on('pageerror',lambda e:print('ERR',e))
        await pg.goto("https://test.local/wc2.html"); await pg.wait_for_function("window.ready===true",timeout=180000)
        for name,show,phone,cut,pos,tgt,fov in V:
            await pg.evaluate(f"show({json.dumps(show)},{str(phone).lower()},{str(cut).lower()});view({pos},{tgt},{fov})"); await pg.wait_for_timeout(400)
            await pg.screenshot(path=os.path.join(D,'out','r_'+name+'.png'))
        await b.close()
asyncio.run(main())
