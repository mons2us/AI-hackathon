import asyncio
from playwright.async_api import async_playwright
F="gaming_stand_v3.html"
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        pg=await b.new_page(viewport={"width":1280,"height":900},device_scale_factor=2)
        async def route(r):
            u=r.request.url
            if "three.min.js" in u: await r.fulfill(path="libs/package/build/three.min.js",content_type="text/javascript")
            elif "OrbitControls" in u: await r.fulfill(path="libs/package/examples/js/controls/OrbitControls.js",content_type="text/javascript")
            elif "test.local" in u: await r.fulfill(body="<!doctype html><html><head><meta charset='utf-8'></head><body>"+open(F,encoding="utf-8").read()+"</body></html>",content_type="text/html")
            else: await r.fulfill(body="",content_type="text/css")
        await pg.route("**/*",route)
        await pg.goto("https://test.local/");await pg.wait_for_timeout(2500)
        await pg.evaluate("document.querySelectorAll('.viewer .hud,.viewer .tag,.viewer .legend').forEach(e=>e.style.display='none');document.getElementById('vP').click()")
        J=lambda i:pg.evaluate(f"document.getElementById('{i}').click()")
        g=await pg.query_selector("#gl")
        for who,mode,name in [("wH","vS","st_hu_shape"),("wH","vT","st_hu_flow"),("wA","vS","st_ai_shape"),("wA","vT","st_ai_flow")]:
            await J(who);await J(mode);await pg.wait_for_timeout(700);await g.screenshot(path=f"shots/{name}_full.png")
        await b.close()
asyncio.run(main())
