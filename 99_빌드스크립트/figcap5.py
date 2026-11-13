import asyncio,os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch();ctx=await b.new_context(viewport={"width":800,"height":800},device_scale_factor=2);pg=await ctx.new_page()
        await pg.goto("file://"+os.path.abspath("figs5.html"));await pg.wait_for_timeout(600)
        el=await pg.query_selector("#g1");await el.screenshot(path="shots/g1.png");bb=await el.bounding_box();print(bb["width"],bb["height"])
        await b.close()
asyncio.run(main())
