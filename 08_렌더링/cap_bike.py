import asyncio, os, json, sys
from playwright.async_api import async_playwright
D=os.path.dirname(os.path.abspath(__file__))
V=[("bike_full",["final","holder"],True,[1400,2700,600],[-380,0,-420],25),
   ("bike_rider",["final","holder"],True,[-420,760,560],[60,40,0],17),
   ("bike_front",["final","holder"],True,[620,700,260],[50,45,5],17),
   ("bike_base_stress",["base_smooth_stress","clamp","bar"],False,[330,900,420],[45,55,-4],11),
   ("bike_final_stress",["final_stress","bar"],False,[330,900,420],[45,55,-4],11),
   ("bike_final_plain",["final","bar"],False,[330,900,420],[45,55,-4],11)]
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        pg=await b.new_page(viewport={"width":1600,"height":1000},device_scale_factor=2)
        async def route(r):
            fn=r.request.url.split('test.local/')[-1]
            ct={'html':'text/html; charset=utf-8','js':'text/javascript','json':'application/json','png':'image/png'}[fn.rsplit('.',1)[-1]]
            await r.fulfill(path=os.path.join(D,fn),content_type=ct)
        await pg.route("**/*",route); pg.on('pageerror',lambda e:print('ERR',e))
        await pg.goto("https://test.local/bike.html"); await pg.wait_for_function("window.ready===true",timeout=180000)
        for name,show,bk,pos,tgt,fov in V:
            await pg.evaluate(f"bikeVis({str(bk).lower()});show({json.dumps(show)});view({pos},{tgt},{fov})"); await pg.wait_for_timeout(400)
            await pg.screenshot(path=os.path.join(D,'out','r_'+name+'.png'))
        await b.close()
asyncio.run(main())
