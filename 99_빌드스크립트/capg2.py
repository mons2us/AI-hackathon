import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        pg=await b.new_page(viewport={"width":1280,"height":900},device_scale_factor=2)
        async def route(r):
            u=r.request.url
            if "three.min.js" in u: await r.fulfill(path="libs/package/build/three.min.js",content_type="text/javascript")
            elif "OrbitControls" in u: await r.fulfill(path="libs/package/examples/js/controls/OrbitControls.js",content_type="text/javascript")
            elif "test.local" in u: await r.fulfill(body="<!doctype html><html><head><meta charset='utf-8'></head><body>"+open("glasses_demo_v1.html",encoding="utf-8").read()+"</body></html>",content_type="text/html")
            else: await r.fulfill(body="",content_type="text/css")
        await pg.route("**/*",route)
        await pg.goto("https://test.local/");await pg.wait_for_timeout(2500)
        await pg.evaluate("document.querySelectorAll('.viewer .hud,.viewer .tag,.viewer .note2').forEach(e=>e.style.display='none')")
        g=await pg.query_selector("#gl")
        for js,f in [("who='H';flow=false;render()","gl3d_hu_shape"),("who='H';flow=true;render()","gl3d_hu_flow"),("who='A';flow=false;render()","gl3d_ai_shape")]:
            await pg.evaluate(js);await pg.wait_for_timeout(600);await g.screenshot(path=f"shots/{f}.png")
        await b.close()
asyncio.run(main())
