import asyncio
from playwright.async_api import async_playwright
F="formproof_demo_v8.html"
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
        clip={"x":0,"y":200,"width":1240,"height":600}
        await pg.screenshot(path="v8_0.png",clip=clip)
        for i in range(3): await pg.click("#next");await pg.wait_for_timeout(500)
        await pg.wait_for_selector("#next:not([disabled])",timeout=30000);await pg.click("#next");await pg.wait_for_timeout(600)
        await pg.screenshot(path="v8_a.png",clip=clip)
        await pg.click("#cE");await pg.wait_for_timeout(400);await pg.screenshot(path="v8_aE.png",clip=clip)
        await pg.click("#wS");await pg.wait_for_timeout(400);await pg.screenshot(path="v8_sE.png",clip=clip)
        await pg.click("#wD");await pg.wait_for_timeout(400);await pg.screenshot(path="v8_dE.png",clip=clip)
        print(errs);await b.close()
asyncio.run(main())
