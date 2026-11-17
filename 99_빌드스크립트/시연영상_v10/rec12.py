import asyncio, time, json
from playwright.async_api import async_playwright
HL_JS = r"""
window.HL=(sels,title,body,pos)=>{
  let w=document.getElementById('hlw');
  if(!w){w=document.createElement('div');w.id='hlw';w.style.cssText='position:fixed;inset:0;z-index:99999;pointer-events:none';
    w.innerHTML='<div class="dm"></div><div class="dm"></div><div class="dm"></div><div class="dm"></div><div id="hlb"></div><div id="hlc"><b></b><span></span></div>';document.body.appendChild(w);
    const st=document.createElement('style');st.textContent=`#hlw .dm{position:fixed;background:rgba(8,14,28,.42);transition:all .35s}
     #hlb{position:fixed;border:4px solid #ffb020;border-radius:12px;box-shadow:0 0 0 3px rgba(255,176,32,.35),0 0 24px rgba(255,176,32,.6);transition:all .35s}
     #hlc{position:fixed;max-width:430px;background:#111a2b;color:#fff;border-radius:14px;padding:14px 18px;box-shadow:0 10px 30px rgba(0,0,0,.35);border:2px solid #ffb020;transition:all .35s;font-family:"Noto Sans CJK KR",sans-serif}
     #hlc b{display:block;font-size:24px;color:#ffd166;margin-bottom:4px}#hlc span{display:block;font-size:19px;line-height:1.45}#hlc em{font-style:normal;color:#5fd3a6;font-weight:700}`;document.head.appendChild(st);}
  if(!sels){w.style.display='none';return;} w.style.display='';
  let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;
  for(const s of sels){for(const el of document.querySelectorAll(s)){const r=el.getBoundingClientRect();if(r.width<2)continue;x0=Math.min(x0,r.left);y0=Math.min(y0,r.top);x1=Math.max(x1,r.right);y1=Math.max(y1,r.bottom);}}
  const p=6;x0-=p;y0-=p;x1+=p;y1+=p;const W=innerWidth,H=innerHeight,d=w.querySelectorAll('.dm');
  const R=(e,l,t,ww,hh)=>{e.style.left=l+'px';e.style.top=t+'px';e.style.width=Math.max(0,ww)+'px';e.style.height=Math.max(0,hh)+'px';};
  R(d[0],0,0,W,y0);R(d[1],0,y1,W,H-y1);R(d[2],0,y0,x0,y1-y0);R(d[3],x1,y0,W-x1,y1-y0);
  const b=document.getElementById('hlb');R(b,x0,y0,x1-x0,y1-y0);
  const c=document.getElementById('hlc');c.querySelector('b').innerHTML=title;c.querySelector('span').innerHTML=body;
  const cw=Math.min(430,c.offsetWidth||430),ch=c.offsetHeight||110;let l,t;
  if(pos==='r'){l=x1+18;t=y0;} else if(pos==='l'){l=x0-18-cw;t=y0;} else if(pos==='b'){l=x0;t=y1+16;} else if(pos==='t'){l=x0;t=y0-16-ch;} else {l=x0+20;t=y0+20;}
  l=Math.max(10,Math.min(W-cw-10,l));t=Math.max(10,Math.min(H-ch-10,t));c.style.left=l+'px';c.style.top=t+'px';};
"""
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        ctx=await b.new_context(viewport={"width":1600,"height":900},record_video_dir=".",record_video_size={"width":1600,"height":900})
        pg=await ctx.new_page(); err=[]; pg.on('pageerror',lambda e:err.append(str(e)))
        T0=time.time(); M={}
        def mark(s): M[s]=round(time.time()-T0,2); print(f"{M[s]:6.1f}s {s}",flush=True)
        await pg.goto("http://127.0.0.1:8799/?video&optscale=0.35"); await pg.wait_for_function("S.demos&&S.demos.length>0",timeout=60000)
        await pg.add_script_tag(content=HL_JS); await pg.wait_for_timeout(600)
        hl=lambda s,t,bd,pos='r': pg.evaluate("([s,t,b,p])=>HL(s,t,b,p)",[s,t,bd,pos])
        W=pg.wait_for_timeout
        mark('in')
        await hl(['#text','#sketchBox .pad'],'아이디어 입력','요청을 문장으로 쓰고<br>모양은 손 스케치로 (사진도 가능)')
        await pg.evaluate("playDemo(0,false)"); await W(500); await pg.wait_for_function("!S.playing",timeout=180000); await W(600)
        mark('spec'); await hl(None,'','')
        await pg.evaluate("makeSpec(false)"); await pg.wait_for_function("S.spec&&!S.specBusy",timeout=180000); await W(900)
        await hl(['#specs'],'설계 사양','AI가 요청을 물리 조건으로 바꿈<br><em>자료</em> = 규격 · 실측 논문 근거 · <em>목표</em> = 최적화 목표')
        await W(6500); await hl(None,'',''); await pg.click('#bConfirm'); await W(900); await pg.click('#go')
        await pg.wait_for_function("S.rep && S.rows && S.rows.length>0",timeout=500000); await W(800); mark('first')
        await hl(['.csim .vrow #vS0','.csim .vrow #vS1','.csim .vrow #vS2'],'물리 시뮬레이션','응력 · 흔들림 · 온도 분포<br>빨강일수록 불리','l'); await W(4200)
        await hl(['#metrics'],'1차 설계 판정','정밀 시뮬레이션으로 기준 확인<br><em style="color:#ff8a96">빨강 = 기준 미달 · 5개 중 4개</em>','l'); await W(4500)
        await pg.evaluate("S.rows.forEach((m,i)=>{if(m.key&&!m.ok&&!m.ref)S.sel.add(i)}); updateOpt(); drawMetrics();"); await W(700)
        await hl(['#optimize'],'물리 최적화 실행','미달 항목을 골라 실행','l'); await W(1800); await hl(None,'','')
        mark('opt'); await pg.click('#optimize'); await W(1500)
        await hl(['#vMain'],'AI 탐색','형상 AI가 모양을 바꾸고<br>물리 AI가 성능을 바로 예측','r'); await W(6500)
        await hl(['#vS3'],'목표 달성 그래프','선이 위쪽 점선에 닿으면 목표 달성<br>(계산 기록 재생)','l'); await W(5500)
        await hl(['#metrics'],'AI 예측 값','항목마다 <em>AI 예측</em> 값이 바뀜','l')
        await pg.wait_for_function("S.opt&&S.opt.aiN",timeout=600000); mark('refine')
        await hl(['#metrics'],'정밀 최적화','AI 후보 31개만 정밀 계산 →<br>값이 <em>정밀 계산</em>으로 바뀜','l')
        await pg.wait_for_function("document.querySelector('#optInfo').classList.contains('ok')||document.querySelector('#optInfo').classList.contains('bad')",timeout=600000); await W(600)
        mark('done'); txt=await pg.inner_text('#optText'); print(txt)
        await hl(['.cperf .kpis','#metrics'],'검증 통과','5개 기준 모두 충족<br>무게 <em>94.9 → 83.9 g</em>','l'); await W(5500)
        await hl(None,'',''); await pg.click('#vCmp'); await W(1200); mark('cmp')
        await hl(['#cmpOv .cc[data-k="shake"]'],'흔들림 비교','같은 색 척도 · 빨강일수록 불리<br>최대 <em>3.42배 → 1.2배</em>','r'); await W(4200)
        await hl(['#cmpOv .cc[data-k="temp"]'],'폰 온도 비교','뒷면을 열어 열이 빠짐<br>최대 <em>32.56 → 20.95 °C</em>','r'); await W(4200)
        await hl(None,'',''); await pg.click('#vDraw'); await W(400); mark('draw')
        dw=await pg.evaluate("S.optLast&&S.optLast.dw"); print('drawing',dw)
        await W(7000); mark('end'); M['dw']=dw; M['errors']=err[:3]; json.dump(M,open('marks.json','w'),ensure_ascii=False)
        await ctx.close(); await b.close()
asyncio.run(main())
