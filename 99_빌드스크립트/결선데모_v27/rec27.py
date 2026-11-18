import asyncio, time, json, os
from playwright.async_api import async_playwright
HL_JS = r"""
window.HL=(sels,title,body,pos)=>{
  let w=document.getElementById('hlw');
  if(!w){w=document.createElement('div');w.id='hlw';w.style.cssText='position:fixed;inset:0;z-index:99999;pointer-events:none';
    w.innerHTML='<div class="dm"></div><div class="dm"></div><div class="dm"></div><div class="dm"></div><div id="hlb"></div><div id="hlc"><b></b><span></span></div>';document.body.appendChild(w);
    const st=document.createElement('style');st.textContent=`#hlw .dm{position:fixed;background:rgba(8,14,28,.42);transition:all .6s ease}
     #hlb{position:fixed;border:4px solid #ffb020;border-radius:12px;box-shadow:0 0 0 3px rgba(255,176,32,.35),0 0 24px rgba(255,176,32,.6);transition:all .6s ease}
     #hlc{position:fixed;max-width:430px;background:#111a2b;color:#fff;border-radius:14px;padding:14px 18px;box-shadow:0 10px 30px rgba(0,0,0,.35);border:2px solid #ffb020;transition:all .6s ease;font-family:"Noto Sans CJK KR",sans-serif}
     #hlc b{display:block;font-size:24px;color:#ffd166;margin-bottom:4px}#hlc span{display:block;font-size:19px;line-height:1.45}#hlc em{font-style:normal;color:#5fd3a6;font-weight:700}#hlw.snap *{transition:none!important}`;document.head.appendChild(st);}
  if(!sels){w.style.display='none';return;}
  const snap=w.style.display==='none'||!w.dataset.on; w.dataset.on=1; if(snap)w.classList.add('snap'); w.style.display='';
  let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;
  for(const s of sels){for(const el of document.querySelectorAll(s)){const r=el.getBoundingClientRect();if(r.width<2)continue;x0=Math.min(x0,r.left);y0=Math.min(y0,r.top);x1=Math.max(x1,r.right);y1=Math.max(y1,r.bottom);}}
  const p=6;x0-=p;y0-=p;x1+=p;y1+=p;const W=innerWidth,H=innerHeight,d=w.querySelectorAll('.dm');
  const R=(e,l,t,ww,hh)=>{e.style.left=l+'px';e.style.top=t+'px';e.style.width=Math.max(0,ww)+'px';e.style.height=Math.max(0,hh)+'px';};
  R(d[0],0,0,W,y0);R(d[1],0,y1,W,H-y1);R(d[2],0,y0,x0,y1-y0);R(d[3],x1,y0,W-x1,y1-y0);
  const b=document.getElementById('hlb');R(b,x0,y0,x1-x0,y1-y0);
  const c=document.getElementById('hlc');c.querySelector('b').innerHTML=title;c.querySelector('span').innerHTML=body;
  const cw=Math.min(430,c.offsetWidth||430),ch=c.offsetHeight||110;let l,t;
  if(pos==='r'){l=x1+18;t=y0;} else if(pos==='l'){l=x0-18-cw;t=y0;} else if(pos==='b'){l=x0;t=y1+16;} else if(pos==='t'){l=x0;t=y0-16-ch;} else {l=x0+24;t=y0+90;}
  l=Math.max(10,Math.min(W-cw-10,l));t=Math.max(10,Math.min(H-ch-10,t));c.style.left=l+'px';c.style.top=t+'px';
  if(snap){void w.offsetWidth;requestAnimationFrame(()=>requestAnimationFrame(()=>w.classList.remove('snap')));}};
"""
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        ctx=await b.new_context(viewport={"width":1600,"height":900},record_video_dir=".",record_video_size={"width":1600,"height":900})
        pg=await ctx.new_page(); err=[]; pg.on('pageerror',lambda e:err.append(str(e)))
        T0=time.time(); M={}
        def mark(s): M[s]=round(time.time()-T0,2); print(f"{M[s]:6.1f}s {s}",flush=True)
        await pg.goto("http://127.0.0.1:8799/?ui=pro&video&optscale=0.6"); await pg.wait_for_function("S.demos&&S.demos.length>0",timeout=60000)
        await pg.add_script_tag(content=HL_JS); await pg.wait_for_timeout(600)
        async def hl(*a, **k): return None
        RECT_JS="(sels)=>{const o={};for(const s of sels){let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;for(const e of document.querySelectorAll(s)){const r=e.getBoundingClientRect();if(r.width<2)continue;x0=Math.min(x0,r.left);y0=Math.min(y0,r.top);x1=Math.max(x1,r.right);y1=Math.max(y1,r.bottom);}if(x1>x0)o[s]=[x0,y0,x1-x0,y1-y0];}return o;}"
        async def rects(tag, sels): M.setdefault('rects',{})[tag]=await pg.evaluate(RECT_JS, sels)
        W=pg.wait_for_timeout
        mark('in'); await rects('in',['#text','#sketchBox','#sketchBox .pad','.cin','#reqMap','#specs'])
        await hl(['#text','#sketchBox .pad'],'아이디어 입력','요청은 문장으로, 모양은 스케치로')
        await pg.evaluate("playDemo(0,false)"); await W(500); await pg.wait_for_function("!S.playing",timeout=180000); await W(400)
        mark('inend'); await hl(None,'',''); mark('spec')
        await pg.evaluate("makeSpec(false)"); await pg.wait_for_function("S.spec&&!S.specBusy",timeout=180000); await W(600)
        mark('specshow'); await rects('spec',['#reqMap','#specs','.cin','#reqMap .mr']); await hl(['#reqMap .mr:nth-child(3)','#reqMap .mr:nth-child(4)','#reqMap .mr:nth-child(5)'],'요구 → 물리 조건','“안 흔들리게” → 떨림 주파수 ≥ 95 Hz<br>수치마다 근거 (실측 · 규격)','b'); await W(3600)
        await hl(None,'',''); await pg.click('#bConfirm'); await W(700); await pg.click('#go'); mark('go')
        await pg.wait_for_function("S.rep && S.rows && S.rows.length>0",timeout=500000); mark('first')
        await pg.wait_for_function("V3.mount&&V3.small.every(x=>x.mat||!x.key)",timeout=60000); await W(1500)
        await rects('first',['#vMain','#vS0','#vS1','#vS2','#metrics','.cperf','.cperf .kpis','#vS3','.cperf .kpis, #metrics']); mark('rsim'); await hl(['#vS0','#vS1','#vS2'],'초기 설계 · 정밀 시뮬레이션','응력 · 흔들림 · 온도 분포 — 빨강일수록 불리','l'); await W(3000)
        mark('rjudge'); await hl(['.cperf .kpis','#metrics'],'성능 판정','<em style="color:#ff8a96">5개 기준 중 4개 미달</em>','l'); await W(3200)
        await pg.evaluate("S.rows.forEach((m,i)=>{if(m.key&&!m.ok&&!m.ref)S.sel.add(i)}); updateOpt(); drawMetrics();"); await W(300)
        await hl(None,'',''); await pg.evaluate("window.FP_STEP=1;window.FP_STEP_N=0"); mark('opt'); await pg.click('#optimize')
        await pg.evaluate("window.SIDE=()=>{if($('#vBike').classList.contains('on'))$('#vBike').click();if($('#vPhone').classList.contains('on'))$('#vPhone').click();V3.handlebar.visible=false;V3.cam.fov=13;V3.cam.position.set(38,55+1150,40);V3.ctl.target.set(38,55,40);V3.cam.updateProjectionMatrix();V3.ctl.update();}")
        await pg.wait_for_function("S.opt&&S.opt.queue&&S.opt.queue.length>0",timeout=600000); mark('stepstart')
        os.makedirs('st', exist_ok=True); n=0; seq=[]; hlk=None; r0=None
        HLS={'ai':(['#optBan'],'AI 탐색','형상 AI가 모양을 바꾸고 물리 AI가 성능을 바로 예측<br>옆에서 본 모습 · 노란 반투명 = 처음 형상','b'),
             'graph':(['#vS3'],'AI 탐색 300회','흰 선 = 무게 · 색 선 = 기준별 달성률','t'),
             'pick':(['#candP'],'후보 선택','AI 후보 31개를 정밀 계산(FEM)으로 확인<br>통과 11개 중 <em>흔들림 여유(진동수)가 가장 큰</em> 후보','r'),
             'ref':(['#vMain'],'정밀 최적화','후보에서 출발 · FEM 120회 · 3D 프린트 출력 조건(45°)<br>재료를 깎아 내며 기준을 맞춤','in')}
        while True:
            st=await pg.evaluate("(()=>{const o=S.opt;if(!o)return 'end';if(o.queue.length)return o.queue[0].stage+':'+o.queue[0].it;return o.done?'end':'wait';})()")
            if st=='end': break
            if st=='wait': await W(200); continue
            stage,it=st.split(':'); it=int(it)
            if stage=='ai': want='ai' if it<150 else 'graph'
            elif stage=='pick': want='pick'
            else:
                if r0 is None: r0=n
                want='pick' if n-r0<1 else 'ref'
            if want!=hlk:
                hlk=want

            await pg.evaluate("window.FP_STEP_N=1"); await pg.wait_for_function("window.FP_STEP_N===0",timeout=60000); await pg.evaluate("SIDE()")
            await pg.evaluate("new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))")
            await pg.screenshot(path=f'st/{n:04d}.jpg',type='jpeg',quality=92); seq.append(dict(n=n,stage=stage,it=it,hl=want)); n+=1
            if stage=='pick': await rects('pick',['#vMain','#candP','#metrics'])
        await rects('step',['#vMain','#candP','#optBan','#vS3','#metrics','.cperf']); json.dump(seq,open('seq.json','w')); mark('stepend')
        await pg.wait_for_function("document.body.classList.contains('st-done')",timeout=600000); await W(600)
        await rects('done',['#vMain','#metrics','.cperf','#resBar','#cmpOv','#vS3']); mark('done'); txt=await pg.inner_text('#resBar'); print(txt); M['resbar']=txt
        M['rows']=await pg.evaluate("S.rows.filter(m=>m.key).map(m=>({k:m.key,label:m.label,v:m.value,v0:m.v0,unit:m.unit,ok:m.ok}))"); print(M['rows']); M['mass_final']=await pg.evaluate("parseFloat(document.querySelector('#kMass').textContent)")
        R={r['k']:r for r in M['rows']}
        await hl(['#resBar'],'검증','최종 형상을 정밀 시뮬레이션으로 다시 판정 — <em>5개 기준 모두 충족</em>','b'); await W(3200)
        mark('cmp'); sh=R.get('shake',{}); await rects('cmp',['#cmpOv','#cmpOv .cc[data-k="shake"]'])
        await hl(['#cmpOv .cc[data-k="shake"]'],'흔들림 비교',f"같은 색 척도 · 빨강일수록 불리<br>최대 <em>{sh.get('v0',0):.2f}배 → {sh.get('v',0):.2f}배</em>",'b'); await W(3600)
        await hl(None,'',''); await pg.click('#vDraw'); await W(400); mark('draw')
        dw=await pg.evaluate("S.optLast&&S.optLast.dw"); print('drawing',dw); await rects('draw',['#vMain'])
        await W(6500); mark('end'); M['dw']=dw; M['errors']=err[:3]; json.dump(M,open('marks.json','w'),ensure_ascii=False)
        await ctx.close(); await b.close()
asyncio.run(main())
