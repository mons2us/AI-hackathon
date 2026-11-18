"""v28 녹화: 사람이 조작하는 것처럼 보이게 — 화면에 마우스 커서 · 클릭 표시를 그리고 실제 버튼을 누름.
(설계 사양 → 확정 → 초기 설계 만들기 → 미달 항목 선택 → 물리 기반 최적화 실행 → 도면). 강조 상자 · 설명은 편집에서."""
import asyncio, time, json, os
from playwright.async_api import async_playwright
CUR_JS = r"""
(()=>{const c=document.createElement('div');c.id='fpcur';c.style.cssText='position:fixed;left:800px;top:500px;width:26px;height:26px;z-index:100000;pointer-events:none;transition:left .65s cubic-bezier(.4,.1,.2,1),top .65s cubic-bezier(.4,.1,.2,1)';
c.innerHTML='<svg width="26" height="26" viewBox="0 0 24 24"><path d="M3 2l7 19 2.6-7.4L20 11z" fill="#fff" stroke="#111" stroke-width="1.4" stroke-linejoin="round"/></svg>';document.body.appendChild(c);
const st=document.createElement('style');st.textContent='.fprip{position:fixed;width:16px;height:16px;margin:-8px 0 0 -8px;border-radius:50%;border:3px solid #ffb020;z-index:99999;pointer-events:none;animation:fprip .55s ease-out forwards}@keyframes fprip{to{transform:scale(3.2);opacity:0}}';document.head.appendChild(st);
window.CUR=(x,y)=>{c.style.left=x+'px';c.style.top=y+'px';};
window.RIP=(x,y)=>{const r=document.createElement('div');r.className='fprip';r.style.left=x+'px';r.style.top=y+'px';document.body.appendChild(r);setTimeout(()=>r.remove(),700);};
window.CURHIDE=v=>{c.style.display=v?'none':'';};})();
"""
RECT_JS="(sels)=>{const o={};for(const s of sels){let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;for(const e of document.querySelectorAll(s)){const r=e.getBoundingClientRect();if(r.width<2)continue;x0=Math.min(x0,r.left);y0=Math.min(y0,r.top);x1=Math.max(x1,r.right);y1=Math.max(y1,r.bottom);}if(x1>x0)o[s]=[x0,y0,x1-x0,y1-y0];}return o;}"
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        ctx=await b.new_context(viewport={"width":1600,"height":900},record_video_dir=".",record_video_size={"width":1600,"height":900})
        pg=await ctx.new_page(); err=[]; pg.on('pageerror',lambda e:err.append(str(e)))
        T0=time.time(); M={}
        def mark(s): M[s]=round(time.time()-T0,2); print(f"{M[s]:6.1f}s {s}",flush=True)
        async def rects(tag, sels): M.setdefault('rects',{})[tag]=await pg.evaluate(RECT_JS, sels)
        W=pg.wait_for_timeout
        async def move(sel, dx=0.5, dy=0.5):
            r=await pg.evaluate("s=>{const e=document.querySelector(s);if(!e)return null;const r=e.getBoundingClientRect();return [r.left,r.top,r.width,r.height];}",sel)
            x,y=r[0]+r[2]*dx, r[1]+r[3]*dy; await pg.evaluate("([x,y])=>CUR(x,y)",[x,y]); await W(750); return x,y
        async def tap(sel, name, dx=0.5, dy=0.5):
            x,y=await move(sel,dx,dy); mark('tap_'+name); await pg.evaluate("([x,y])=>RIP(x,y)",[x,y]); await pg.click(sel); await W(350)
        await pg.goto("http://127.0.0.1:8799/?ui=pro&video&optscale=0.6"); await pg.wait_for_function("S.demos&&S.demos.length>0",timeout=60000)
        await pg.add_script_tag(content=CUR_JS); await W(600)
        await move('#text',0.3,0.4)
        mark('in'); await rects('in',['#text','#sketchBox','#bSpec'])
        await pg.evaluate("playDemo(0,false)"); await W(400); await move('#sketchBox .pad',0.6,0.5)
        await pg.wait_for_function("!S.playing",timeout=180000); await W(300); mark('inend')
        await tap('#bSpec','spec'); mark('spec')
        await pg.wait_for_function("S.spec&&!S.specBusy",timeout=180000); await W(500)
        mark('specshow'); await rects('spec',['#reqMap','#specs','.cin','#reqMap .mr','#bConfirm','#go']); await W(3400)
        await tap('#bConfirm','confirm'); await W(500); await tap('#go','go'); mark('go')
        await pg.wait_for_function("S.rep && S.rows && S.rows.length>0",timeout=500000); mark('first')
        await pg.wait_for_function("V3.mount&&V3.small.every(x=>x.mat||!x.key)",timeout=60000); await W(1200)
        await rects('first',['#vMain','#vS0','#vS1','#vS2','#metrics','.cperf','.cperf .kpis','.cperf .kpis, #metrics','#optimize']); mark('rsim'); await W(3000)
        mark('rjudge'); await W(3000)
        fails=await pg.evaluate("S.rows.map((m,i)=>[i,!!(m.key&&!m.ok&&!m.ref)]).filter(x=>x[1]).map(x=>x[0])")
        pick=await pg.evaluate("!!S.pick"); print('fails',fails,'pick',pick)
        mark('selstart')
        for k,i in enumerate(fails):
            if pick: await tap(f'#metrics .metric[data-i="{i}"]',f'sel{k}',0.25,0.5)
            else:
                await move(f'#metrics .metric[data-i="{i}"]',0.25,0.5); mark(f'tap_sel{k}')
                await pg.evaluate("i=>{S.sel.add(i);updateOpt();drawMetrics();}",i); await W(350)
        await rects('sel',['#metrics','#optimize']); await W(500)
        await pg.evaluate("window.FP_STEP=1;window.FP_STEP_N=0"); await tap('#optimize','opt'); mark('opt')
        await pg.evaluate("window.SIDE=()=>{if($('#vBike').classList.contains('on'))$('#vBike').click();if($('#vPhone').classList.contains('on'))$('#vPhone').click();V3.handlebar.visible=false;V3.cam.fov=13;V3.cam.position.set(38,55+1150,40);V3.ctl.target.set(38,55,40);V3.cam.updateProjectionMatrix();V3.ctl.update();}")
        await pg.evaluate("CURHIDE(true)")
        await pg.wait_for_function("S.opt&&S.opt.queue&&S.opt.queue.length>0",timeout=600000); mark('stepstart')
        os.makedirs('st', exist_ok=True); n=0; seq=[]
        while True:
            st=await pg.evaluate("(()=>{const o=S.opt;if(!o)return 'end';if(o.queue.length)return o.queue[0].stage+':'+o.queue[0].it;return o.done?'end':'wait';})()")
            if st=='end': break
            if st=='wait': await W(200); continue
            stage,it=st.split(':'); it=int(it)
            await pg.evaluate("window.FP_STEP_N=1"); await pg.wait_for_function("window.FP_STEP_N===0",timeout=60000); await pg.evaluate("SIDE()")
            await pg.evaluate("new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))")
            await pg.screenshot(path=f'st/{n:04d}.jpg',type='jpeg',quality=92); seq.append(dict(n=n,stage=stage,it=it)); n+=1
            if stage=='pick': await rects('pick',['#vMain','#candP','#metrics'])
        await rects('step',['#vMain','#candP','#optBan','#vS3','#metrics','.cperf']); json.dump(seq,open('seq.json','w')); mark('stepend')
        await pg.wait_for_function("document.body.classList.contains('st-done')",timeout=600000); await pg.evaluate("CURHIDE(false)"); await W(600)
        await rects('done',['#vMain','#metrics','.cperf','#resBar','#cmpOv','#vS3']); mark('done'); txt=await pg.inner_text('#resBar'); print(txt); M['resbar']=txt
        M['rows']=await pg.evaluate("S.rows.filter(m=>m.key).map(m=>({k:m.key,label:m.label,v:m.value,v0:m.v0,unit:m.unit,ok:m.ok}))"); M['mass_final']=await pg.evaluate("parseFloat(document.querySelector('#kMass').textContent)")
        await W(3200); mark('cmp'); await rects('cmp',['#cmpOv','#cmpOv .cc[data-k="shake"]']); await W(3600)
        await tap('#vDraw','draw'); mark('draw')
        dw=await pg.evaluate("S.optLast&&S.optLast.dw"); print('drawing',dw); await rects('draw',['#vMain'])
        await W(4000); mark('end'); M['dw']=dw; M['errors']=err[:3]; json.dump(M,open('marks.json','w'),ensure_ascii=False)
        await ctx.close(); await b.close()
asyncio.run(main())
