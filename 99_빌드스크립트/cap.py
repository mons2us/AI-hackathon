import asyncio
from playwright.async_api import async_playwright
F="formproof_demo_v8.html"
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        ctx=await b.new_context(viewport={"width":1500,"height":1000},device_scale_factor=2)
        pg=await ctx.new_page()
        async def route(r):
            u=r.request.url
            if "three.min.js" in u: await r.fulfill(path="libs/package/build/three.min.js",content_type="text/javascript")
            elif "OrbitControls" in u: await r.fulfill(path="libs/package/examples/js/controls/OrbitControls.js",content_type="text/javascript")
            elif "test.local" in u: await r.fulfill(body="<!doctype html><html><head><meta charset='utf-8'></head><body>"+open(F,encoding="utf-8").read()+"</body></html>",content_type="text/html")
            else: await r.fulfill(body="",content_type="text/css")
        await pg.route("**/*",route)
        await pg.goto("https://test.local/");await pg.wait_for_timeout(800)
        # hide HUD overlays for clean shots
        await pg.add_style_tag(content=".hud,.tag,.flow{display:none!important}")
        gl=await pg.query_selector(".viewer")
        async def shot(name): await pg.wait_for_timeout(350);await gl.screenshot(path=f"shots/{name}.png")
        await pg.click("#next");await shot("draft")
        await pg.click("#next");await shot("cond")
        await pg.click("#next");await pg.wait_for_timeout(300)
        n=await pg.evaluate("PRE.frames.length")
        for idx,name in [(1,"it_a"),(5,"it_b"),(12,"it_c"),(n-1,"it_d")]:
            await pg.evaluate(f"clearTimeout(playT);ghost(null);show(dec(PRE.frames[{idx}].x))");await shot(name)
            print(name,await pg.evaluate(f"PRE.frames[{idx}].it"))
        await pg.evaluate("clearTimeout(playT)")
        await pg.evaluate("go(4)");await pg.wait_for_timeout(300)
        for w,c,name in [("A","S","ai"),("D","S","draft2"),("S","S","solid"),("A","E","ai_e"),("S","E","solid_e"),("D","E","draft_e")]:
            await pg.evaluate(f"who='{w}';col='{c}';syncWho();renderWho()");await shot(name)
        await b.close()
asyncio.run(main())
