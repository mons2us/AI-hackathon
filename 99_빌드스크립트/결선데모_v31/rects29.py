"""v29 화면 구성 장면용: 단계별 화면의 영역 좌표(1600×900) 기록 — 진행 단계 표시줄 · 계산 기록 등 v28 녹화에 없던 영역."""
import asyncio, json
from playwright.async_api import async_playwright
RECT_JS = "(sels)=>{const o={};for(const s of sels){let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;for(const e of document.querySelectorAll(s)){const r=e.getBoundingClientRect();if(r.width<2)continue;x0=Math.min(x0,r.left);y0=Math.min(y0,r.top);x1=Math.max(x1,r.right);y1=Math.max(y1,r.bottom);}if(x1>x0)o[s]=[x0,y0,x1-x0,y1-y0];}return o;}"
SEL = ['#steps', '#text', '#sketchBox', '#reqMap', '#specs', '#vMain', '#vS0', '#vS1', '#vS2', '.cperf', '.cperf .kpis', '#metrics', '#plog', '#optimize', '#resBar', '#cmpOv', '.cin', 'header', '.top']
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
        pg = await b.new_page(viewport={"width": 1600, "height": 900}); R = {}
        await pg.goto("http://127.0.0.1:8799/?ui=pro&video"); await pg.wait_for_function("S.demos&&S.demos.length>0", timeout=60000)
        await pg.keyboard.press('1'); await pg.wait_for_timeout(500); await pg.wait_for_function("!S.playing", timeout=180000)
        await pg.click('#bSpec'); await pg.wait_for_function("S.spec&&!S.specBusy", timeout=180000); await pg.wait_for_timeout(3000)
        R['s1'] = await pg.evaluate(RECT_JS, SEL); await pg.screenshot(path='s1.png')
        await pg.click('#bConfirm'); await pg.wait_for_timeout(500); await pg.click('#go')
        await pg.wait_for_function("S.rep && S.rows && S.rows.length>0", timeout=500000)
        await pg.wait_for_function("V3.mount&&V3.small.every(x=>x.mat||!x.key)", timeout=60000); await pg.wait_for_timeout(2500)
        R['s2'] = await pg.evaluate(RECT_JS, SEL); await pg.screenshot(path='s2.png')
        json.dump(R, open('rects29.json', 'w'), indent=1); print(json.dumps(R))
        await b.close()
asyncio.run(main())
