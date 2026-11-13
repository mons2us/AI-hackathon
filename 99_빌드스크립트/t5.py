import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        pg=await b.new_page()
        html=open("formproof_demo_v4.html",encoding="utf-8").read()
        await pg.route("**/*",lambda r:r.fulfill(body="",content_type="text/javascript") if "test.local" not in r.request.url else r.fulfill(body="<!doctype html><html><head><meta charset='utf-8'></head><body>"+html+"</body></html>",content_type="text/html"))
        await pg.goto("https://test.local/")
        r=await pg.evaluate("""()=>new Promise(res=>{const out=[];let w;try{w=makeWorker()}catch(e){res('make err '+e);return}
          w.onmessage=e=>{out.push(e.data.type+(e.data.it||''));if(out.length>3){w.terminate();res(out.join(','))}};
          w.onerror=e=>{res('worker error: '+e.message+' line '+e.lineno)};w.postMessage({lc:'A'});setTimeout(()=>res('timeout '+out.join(',')),20000)})""")
        print(r)
        await b.close()
asyncio.run(main())
