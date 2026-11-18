"""Screenshot every variant mesh in out/mesh with render.html (headless Chromium, software GL)."""
import asyncio, json, os, sys
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
VIEWS = {"hero": ([0.80, 0.58, 0.22], 26, 1.15, False, False), "bare": ([0.72, 0.62, 0.32], 26, 1.2, False, True),
         "side": ([0.0, 1.0, 0.06], 22, 1.12, True, False), "rider": ([-0.85, 0.30, 0.62], 26, 1.2, False, False)}


async def main(ids):
    os.makedirs(os.path.join(OUT, "img"), exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
        pg = await b.new_page(viewport={"width": 960, "height": 720})
        pg.on("pageerror", lambda e: print("ERR", e))

        async def route(r):
            fn = r.request.url.split("gallery.local/")[-1]
            ct = {"html": "text/html; charset=utf-8", "js": "text/javascript", "json": "application/json"}[fn.rsplit(".", 1)[-1]]
            await r.fulfill(path=os.path.join(HERE, fn) if not fn.startswith("out/") else os.path.join(HERE, fn), content_type=ct)
        await pg.route("**/*", route)
        await pg.goto("https://gallery.local/render.html")
        await pg.wait_for_function("window.ready===true", timeout=60000)
        files = sorted(f for f in os.listdir(os.path.join(OUT, "mesh")) if f.endswith(".json"))
        for fn in files:
            vid = fn[:-5]
            if ids and vid not in ids:
                continue
            data = open(os.path.join(OUT, "mesh", fn)).read()
            await pg.evaluate(f"window.load({data})")
            for name, (d, fov, zoom, cut, bare) in VIEWS.items():
                js = lambda b: "true" if b else "false"
                await pg.evaluate(f"window.view({d},{fov},{zoom},{js(cut)},{js(bare)})")
                await pg.wait_for_timeout(150)
                await pg.screenshot(path=os.path.join(OUT, "img", f"{vid}_{name}.jpg"), type="jpeg", quality=88)
            print(vid, flush=True)
        await b.close()

asyncio.run(main(sys.argv[1:]))
