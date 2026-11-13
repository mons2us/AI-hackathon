import asyncio,os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch();ctx=await b.new_context(viewport={"width":800,"height":2600},device_scale_factor=2);pg=await ctx.new_page()
        await pg.goto("file://"+os.path.abspath("figs.html"));await pg.wait_for_timeout(600)
        for f in ["f1","f2","f3","f4"]:
            el=await pg.query_selector("#"+f);await el.screenshot(path=f"shots/{f}.png");bb=await el.bounding_box();print(f,bb["width"],bb["height"])
        await b.close()
asyncio.run(main())
