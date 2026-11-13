import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        pg=await b.new_page(viewport={"width":1280,"height":900},device_scale_factor=2)
        errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
        async def route(r):
            u=r.request.url
            if "three.min.js" in u: await r.fulfill(path="libs/package/build/three.min.js",content_type="text/javascript")
            elif "test.local" in u: await r.fulfill(path="ff/facefit.html",content_type="text/html")
            else: await r.fulfill(body="",content_type="text/css")
        await pg.route("**/*",route)
        await pg.goto("https://test.local/");await pg.wait_for_timeout(5000)
        await pg.screenshot(path="ff/full.png",full_page=True)
        # 안경 선택 시도
        for t in ["라운드","스퀘어 뿔테"]:
            try:
                await pg.get_by_text(t,exact=True).first.click(timeout=3000);break
            except Exception as e: errs.append('click '+t)
        await pg.wait_for_timeout(1500);await pg.screenshot(path="ff/glass.png")
        print(errs[:5]);await b.close()
asyncio.run(main())
