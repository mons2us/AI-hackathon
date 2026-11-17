import asyncio, time, glob, os
from playwright.async_api import async_playwright
CAP="""(t)=>{let c=document.getElementById('vcap');if(!c){c=document.createElement('div');c.id='vcap';
c.style.cssText='position:fixed;left:50%;bottom:22px;transform:translateX(-50%);z-index:9999;background:rgba(14,22,40,.9);color:#fff;font:600 22px/1.4 "Noto Sans CJK KR",sans-serif;padding:12px 26px;border-radius:12px;box-shadow:0 6px 24px rgba(0,0,0,.25);white-space:nowrap;transition:opacity .3s';document.body.appendChild(c);}
c.innerHTML=t;c.style.opacity=t?1:0;}"""
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        ctx=await b.new_context(viewport={"width":1600,"height":900},record_video_dir=".",record_video_size={"width":1600,"height":900})
        pg=await ctx.new_page(); err=[]; pg.on('pageerror',lambda e:err.append(str(e)))
        T0=time.time(); M={}
        def mark(s):
            M[s.split()[0]]=round(time.time()-T0,2); print(f"{time.time()-T0:6.1f}s {s}",flush=True)
        await pg.goto("http://127.0.0.1:8799/?video&optscale=0.35"); await pg.wait_for_function("S.demos&&S.demos.length>0",timeout=60000); await pg.wait_for_timeout(1200)
        cap=lambda t: asyncio.sleep(0)   # 자막은 GUI 머리줄 단계 설명으로 대체
        await cap("① 아이디어 입력 — 요청 문장과 손 스케치"); mark('input')
        await pg.evaluate("playDemo(0,false)"); await pg.wait_for_timeout(500)
        await pg.wait_for_function("!S.playing",timeout=180000); await pg.wait_for_timeout(800)
        await cap("② 설계 사양 — AI가 요청을 물리 조건으로 바꾸고, 항목마다 근거를 붙임")
        mark('specstart')
        await pg.evaluate("makeSpec(false)"); await pg.wait_for_function("S.spec&&!S.specBusy",timeout=180000); mark('spec')
        await pg.wait_for_timeout(7000); await pg.click('#bConfirm'); await pg.wait_for_timeout(1200)
        await pg.click('#go')
        await pg.wait_for_function("S.rep && S.rows && S.rows.length>0",timeout=500000); mark('first')
        await cap("③ 1차 설계 · 성능 확인 — 3D 형상을 만들고 정밀 시뮬레이션으로 판정 → 미충족 4개")
        await pg.wait_for_timeout(7000)
        await pg.evaluate("S.rows.forEach((m,i)=>{if(m.key&&!m.ok&&!m.ref)S.sel.add(i)}); updateOpt(); if(typeof drawMetrics==='function')drawMetrics();")
        await pg.wait_for_timeout(1500)
        await cap("④ 최적 설계 — 미충족 항목을 골라 실행: AI가 형상을 탐색하고 성능을 예측"); mark('opt')
        await pg.click('#optimize')
        await pg.wait_for_function("S.opt&&S.opt.hist&&S.opt.hist.some(h=>h.it>300)",timeout=600000); mark('refine')
        await cap("④ 최적 설계 — AI 후보를 정밀 시뮬레이션으로 확인하며 다듬기")
        await pg.wait_for_function("document.querySelector('#optInfo').classList.contains('ok')||document.querySelector('#optInfo').classList.contains('bad')",timeout=600000)
        txt=await pg.inner_text('#optText'); mark('done '+txt)
        await cap("⑤ 검증 통과 — "+txt)
        await pg.wait_for_timeout(5000)
        await pg.click('#vCmp'); mark('compare'); await pg.wait_for_timeout(11000)
        await pg.click('#vDraw'); mark('draw'); await pg.wait_for_timeout(8000)
        mark('end errors '+str(err[:3])); import json; json.dump(M,open('marks.json','w'))
        await ctx.close(); await b.close()
asyncio.run(main())
