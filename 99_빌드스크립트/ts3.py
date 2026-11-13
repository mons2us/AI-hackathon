import asyncio
from playwright.async_api import async_playwright
F="gaming_stand_v3.html"
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        pg=await b.new_page(viewport={"width":1280,"height":900})
        errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
        async def route(r):
            u=r.request.url
            if "three.min.js" in u: await r.fulfill(path="libs/package/build/three.min.js",content_type="text/javascript")
            elif "OrbitControls" in u: await r.fulfill(path="libs/package/examples/js/controls/OrbitControls.js",content_type="text/javascript")
            elif "test.local" in u: await r.fulfill(body="<!doctype html><html><head><meta charset='utf-8'></head><body>"+open(F,encoding="utf-8").read()+"</body></html>",content_type="text/html")
            else: await r.fulfill(body="",content_type="text/css")
        await pg.route("**/*",route)
        await pg.goto("https://test.local/");await pg.wait_for_timeout(2500)
        await pg.screenshot(path="s3_1.png",full_page=True);el=await pg.query_selector(".dg");await el.screenshot(path="s3_dg.png")
        await pg.click("#wH");await pg.wait_for_timeout(500);await pg.screenshot(path="s3_2.png",clip={"x":0,"y":100,"width":1280,"height":640})
        await pg.click("#vS");await pg.wait_for_timeout(600);await pg.screenshot(path="s3_3.png",clip={"x":0,"y":100,"width":1280,"height":640});print(errs);await b.close()
asyncio.run(main())
