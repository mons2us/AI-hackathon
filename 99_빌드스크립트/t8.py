import asyncio,sys
from playwright.async_api import async_playwright
F="formproof_demo_v6.html"
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        pg=await b.new_page(viewport={"width":1240,"height":860})
        errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
        async def route(r):
            u=r.request.url
            if "three.min.js" in u: await r.fulfill(path="libs/package/build/three.min.js",content_type="text/javascript")
            elif "OrbitControls" in u: await r.fulfill(path="libs/package/examples/js/controls/OrbitControls.js",content_type="text/javascript")
            elif "test.local" in u: await r.fulfill(body="<!doctype html><html><head><meta charset='utf-8'></head><body>"+open(F,encoding="utf-8").read()+"</body></html>",content_type="text/html")
            else: await r.fulfill(body="",content_type="text/css")
        await pg.route("**/*",route)
        await pg.goto("https://test.local/");await pg.wait_for_timeout(800)
        clip={"x":0,"y":150,"width":1240,"height":620}
        await pg.click("#next");await pg.wait_for_timeout(600);await pg.screenshot(path="v6_1.png",clip=clip)
        await pg.click("#next");await pg.wait_for_timeout(600);await pg.screenshot(path="v6_2.png",clip=clip)
        await pg.click("#next");await pg.wait_for_timeout(4000);await pg.screenshot(path="v6_3.png",clip=clip)
        await pg.wait_for_selector("#next:not([disabled])",timeout=30000)
        await pg.click("#next");await pg.wait_for_timeout(800);await pg.screenshot(path="v6_4.png",full_page=True)
        await pg.click("#wS");await pg.wait_for_timeout(500);await pg.screenshot(path="v6_5.png",clip=clip)
        print(errs)
        await b.close()
asyncio.run(main())
