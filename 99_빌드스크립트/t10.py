import asyncio
from playwright.async_api import async_playwright
F="formproof_demo_v8.html"
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        pg=await b.new_page(viewport={"width":1240,"height":860})
        async def route(r):
            u=r.request.url
            if "three.min.js" in u: await r.fulfill(path="libs/package/build/three.min.js",content_type="text/javascript")
            elif "OrbitControls" in u: await r.fulfill(path="libs/package/examples/js/controls/OrbitControls.js",content_type="text/javascript")
            elif "test.local" in u: await r.fulfill(body="<!doctype html><html><head><meta charset='utf-8'></head><body>"+open(F,encoding="utf-8").read()+"</body></html>",content_type="text/html")
            else: await r.fulfill(body="",content_type="text/css")
        await pg.route("**/*",route)
        await pg.goto("https://test.local/");await pg.wait_for_timeout(800)
        await pg.click("#next");await pg.wait_for_timeout(400);print(await pg.inner_text("#panel"))
        for i in range(2): await pg.click("#next");await pg.wait_for_timeout(400)
        await pg.wait_for_selector("#next:not([disabled])",timeout=30000);await pg.click("#next");await pg.wait_for_timeout(600)
        print(await pg.inner_text("#cmpCard"))
        el=await pg.query_selector("#cmpCard");await el.screenshot(path="v8_cmp.png")
        await b.close()
asyncio.run(main())
