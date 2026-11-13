import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        pg=await b.new_page(viewport={"width":1280,"height":900},device_scale_factor=2)
        async def route(r):
            u=r.request.url
            if "three.min.js" in u: await r.fulfill(path="libs/package/build/three.min.js",content_type="text/javascript")
            elif "test.local" in u: await r.fulfill(path="ff/facefit.html",content_type="text/html")
            else: await r.fulfill(body="",content_type="text/css")
        await pg.route("**/*",route)
        await pg.goto("https://test.local/");await pg.wait_for_timeout(5000)
        st=await pg.query_selector("#stage");bb=await st.bounding_box();CL={"x":bb["x"],"y":bb["y"],"width":bb["width"],"height":min(bb["height"],900-bb["y"])}
        await pg.evaluate("document.querySelector('#glassStyle [data-v=none]').click()");await pg.wait_for_timeout(800)
        await pg.evaluate("const c=document.getElementById('tMeasure');if(!c.checked)c.click()");await pg.wait_for_timeout(800)
        await pg.screenshot(path="ff/measure.png",clip=CL)
        await pg.evaluate("const c=document.getElementById('tMeasure');if(c.checked)c.click()");await pg.wait_for_timeout(500)
        await pg.screenshot(path="ff/front_noglass.png",clip=CL)
        await pg.evaluate("const c=document.getElementById('tWire');if(!c.checked)c.click()");await pg.wait_for_timeout(800)
        await pg.screenshot(path="ff/wire.png",clip=CL)
        await pg.evaluate("const c=document.getElementById('tWire');if(c.checked)c.click()")
        await b.close()
asyncio.run(main())
