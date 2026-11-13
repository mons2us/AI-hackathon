import asyncio,sys
from playwright.async_api import async_playwright
F=sys.argv[1]
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        pg=await b.new_page(viewport={"width":1200,"height":800})
        errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
        async def route(r):
            u=r.request.url
            if "three.min.js" in u: await r.fulfill(path="libs/package/build/three.min.js",content_type="text/javascript")
            elif "OrbitControls" in u: await r.fulfill(path="libs/package/examples/js/controls/OrbitControls.js",content_type="text/javascript")
            elif "test.local" in u: await r.fulfill(body="<!doctype html><html><head><meta charset='utf-8'></head><body>"+open(F,encoding="utf-8").read()+"</body></html>",content_type="text/html")
            else: await r.fulfill(body="",content_type="text/css")
        await pg.route("**/*",route)
        await pg.goto("https://test.local/");await pg.wait_for_timeout(800)
        await pg.evaluate("V&&(V.part.parent.children.forEach(()=>{}))")
        await pg.click("#go")
        for t in range(30):
            await pg.wait_for_timeout(1000)
            if "완료" in await pg.inner_text("#status"): break
        print(await pg.inner_text("#status"),await pg.inner_text("#kR"))
        clip={"x":20,"y":205,"width":830,"height":570}
        await pg.screenshot(path="v5_ai.png",clip=clip)
        await pg.click("#cE");await pg.wait_for_timeout(400);await pg.screenshot(path="v5_en.png",clip=clip)
        await pg.click("#cS");await pg.click("#sHU");await pg.wait_for_timeout(400);await pg.screenshot(path="v5_hu.png",clip=clip)
        print(errs)
        await b.close()
asyncio.run(main())
