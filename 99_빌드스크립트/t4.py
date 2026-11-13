import asyncio,sys
from playwright.async_api import async_playwright
F=sys.argv[1]
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        pg=await b.new_page(viewport={"width":1200,"height":900})
        logs=[]
        pg.on("console",lambda m:logs.append(("console",m.type,m.text)) if m.type!="warning" else None)
        pg.on("pageerror",lambda e:logs.append(("pageerror",str(e))))
        async def route(r):
            u=r.request.url
            if "three.min.js" in u: await r.fulfill(path="libs/package/build/three.min.js",content_type="text/javascript")
            elif "OrbitControls" in u: await r.fulfill(path="libs/package/examples/js/controls/OrbitControls.js",content_type="text/javascript")
            elif "fonts.g" in u: await r.fulfill(body="",content_type="text/css")
            else: await r.continue_()
        await pg.route("**/*",route)
        html=open(F,encoding="utf-8").read()
        await pg.route("https://test.local/",lambda r:r.fulfill(body="<!doctype html><html><head><meta charset='utf-8'></head><body>"+html+"</body></html>",content_type="text/html"))
        await pg.goto("https://test.local/")
        await pg.wait_for_timeout(1500)
        print("THREE?",await pg.evaluate("!!window.THREE"))
        await pg.click("#go")
        for t in range(10):
            await pg.wait_for_timeout(3000)
            print(t, await pg.inner_text("#status"), await pg.inner_text("#mIt"), await pg.inner_text("#kR"))
            if "완료" in await pg.inner_text("#status"): break
        await pg.screenshot(path=F+".png")
        for l in logs[:20]: print(l)
        await b.close()
asyncio.run(main())
