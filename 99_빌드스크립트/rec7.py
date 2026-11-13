import asyncio,math,shutil
from playwright.async_api import async_playwright
F="gaming_stand_v5_rec.html";FPS=10
CSS=""".main{grid-template-columns:1fr !important}.main>.card{display:none !important}#gl{height:720px !important}
.viewer .hud{display:none !important}.viewer .tag{display:none}
#ov{position:absolute;inset:0;pointer-events:none;font-family:var(--sans)}
#steps{position:absolute;top:14px;left:14px;right:14px;display:flex;gap:6px}
#steps div{flex:1;background:rgba(11,17,25,.82);border:1px solid #223042;border-radius:8px;padding:6px 8px;font-size:14px;color:#5d6f84;text-align:center;white-space:nowrap}
#steps div.on{border-color:#3fc1d6;color:#06222a;background:#3fc1d6;font-weight:700}
#steps div.done{color:#9FDBE6}
#panel{position:absolute;left:18px;top:70px;width:430px;display:flex;flex-direction:column;gap:10px}
.bub{background:rgba(22,33,46,.95);border:1px solid #2c3b4e;border-radius:12px;padding:12px 14px;font-size:17px;line-height:1.5;color:#e6edf3}
.bub small{display:block;font-size:13px;color:#3fc1d6;font-weight:600;margin-bottom:4px}
.bub.ai small{color:#f5b942}
.spec{font-family:var(--mono);font-size:14.5px;line-height:1.7;color:#eef4f6}
.spec b{color:#9FDBE6;font-weight:500;display:inline-block;width:52px}
.kpi{display:flex;gap:8px}.kpi div{flex:1;background:rgba(14,26,38,.95);border:1px solid #2c3b4e;border-radius:10px;padding:10px;color:#cfe1ee;font-size:13px}
.kpi div b{display:block;font-size:24px;color:#9FDBE6}.kpi div.h b{color:#f2643a}.kpi div.t b{color:#f5b942}
.files{display:grid;grid-template-columns:1fr 1fr;gap:8px}.files div{background:rgba(14,26,38,.95);border:1px solid #2c3b4e;border-radius:10px;padding:12px;color:#e6edf3;font-size:16px;font-weight:600}
.files div span{display:block;font-size:12.5px;color:#8b9bb0;font-weight:400;margin-top:3px}
.badge{display:inline-block;font-size:12px;font-weight:700;border-radius:5px;padding:1px 7px;margin-left:6px;vertical-align:middle}
.hk{background:#f5b942;color:#14202b}.ok{background:#2e9e6b;color:#fff}
#cap{position:absolute;left:18px;right:18px;bottom:16px;background:rgba(11,17,25,.9);border:1px solid #223042;border-radius:10px;padding:10px 16px;font-size:19px;color:#e6edf3}
#cap b{color:#3fc1d6}"""
STEPS=['① 아이디어 입력','② 조건 정리','③ 첫 3D 설계','④ 성능 확인','⑤ 재설계','⑥ 결과','⑦ 파일 출력']
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        pg=await b.new_page(viewport={"width":1312,"height":900})
        async def route(r):
            u=r.request.url
            if "three.min.js" in u: await r.fulfill(path="libs/package/build/three.min.js",content_type="text/javascript")
            elif "OrbitControls" in u: await r.fulfill(path="libs/package/examples/js/controls/OrbitControls.js",content_type="text/javascript")
            elif "test.local" in u: await r.fulfill(body="<!doctype html><html><head><meta charset='utf-8'></head><body>"+open(F,encoding="utf-8").read()+"</body></html>",content_type="text/html")
            else: await r.fulfill(body="",content_type="text/css")
        await pg.route("**/*",route)
        await pg.goto("https://test.local/");await pg.wait_for_timeout(2500)
        await pg.add_style_tag(content=CSS)
        await pg.evaluate("""(S)=>{const o=document.createElement('div');o.id='ov';o.innerHTML='<div id="steps">'+S.map(t=>'<div>'+t+'</div>').join('')+'</div><div id="panel"></div><div id="cap"></div>';document.querySelector('.viewer').appendChild(o);
          window.step=i=>document.querySelectorAll('#steps div').forEach((d,k)=>{d.className=k===i?'on':(k<i?'done':'')});window.panel=h=>{document.getElementById('panel').innerHTML=h};window.cap=h=>{document.getElementById('cap').innerHTML=h};
          window.legend=v=>{document.querySelector('.viewer .legend').style.display=v?'flex':'none'};window.phone=v=>V.phone.forEach(o=>o.visible=v);window.sink=v=>{V.stand.parent.children.forEach(o=>{if(o.isMesh&&o.material&&o.material.color&&o.material.color.getHex()===0xf5b942)o.visible=v})}}""",STEPS)
        vw=await pg.query_selector(".viewer");n=[0]
        async def snap():
            await vw.screenshot(path=f"vid7/f{n[0]:04d}.png");n[0]+=1
        def hold(k):
            for _ in range(k):
                shutil.copy(f"vid7/f{n[0]-1:04d}.png",f"vid7/f{n[0]:04d}.png");n[0]+=1
        async def cam(az,e=0.0,r=1.0):
            await pg.evaluate(f"(()=>{{const t=new THREE.Vector3(70,48,0),c=__cam;const R=Math.hypot(-285,102,210)*{r};const a={az},e=0.36+{e};c.position.set(t.x+R*Math.cos(e)*Math.cos(a),t.y+R*Math.sin(e),t.z+R*Math.cos(e)*Math.sin(a));c.lookAt(t);__ctl.target.copy(t);__ctl.update()}})()")
        E=pg.evaluate;a0=math.atan2(210,-285)
        # ① 입력
        await E("document.getElementById('vP').classList.remove('on');clear(V.stand);clear(V.plate);phone(false);sink(false);legend(false);step(0)");await cam(a0,0,0.9)
        req="폰으로 게임하거나 유튜브를 오래 보면 폰이 뜨거워지고 배터리도 빨리 닳아. 가방에 넣고 다니게 가볍고 접히는 거치대 만들어줘."
        await E("cap('<b>① 아이디어 입력</b> · 텍스트·음성·스케치·이미지·STEP으로 설명 <span class=\"badge hk\">해커톤 개발 · 예시 화면</span>')")
        for k in range(1,13):
            t=req[:int(len(req)*k/12)]
            await E("t=>panel('<div class=\"bub\"><small>🎙 사용자 아이디어 (음성 → 텍스트)</small>'+t+'</div>')",t);await snap()
        hold(12)
        # ② 조건 정리
        await E("step(1);cap('<b>② 조건 정리</b> · AI가 설계 명세로 정리, 빠진 조건만 질문 <span class=\"badge hk\">해커톤 개발 · 예시 화면</span>')")
        spec=[('제품','접이식 스마트폰 거치대'),('크기','옆판 120×100×8 mm × 2'),('재료','PLA · 알루미늄 30%'),('하중','터치 5 N + 폰 200 g'),('고정','앞발·뒷발 바닥 접촉'),('조건','꼭대기 힌지 접이'),('목표','① 가볍게 ② 열 빼기')]
        for k in range(1,len(spec)+1):
            h='<div class="bub ai"><small>AI 설계 명세</small><div class="spec">'+'<br>'.join(f'<b>{a}</b>{v}' for a,v in spec[:k])+'</div></div>'
            await E("h=>panel(h)",h);await snap();hold(1)
        h2=h+'<div class="bub ai"><small>AI 질문</small>케이스 포함 폰 두께는 몇 mm인가요?</div>'
        await E("h=>panel(h)",h2);await snap();hold(14)
        # ③ 첫 3D 설계
        await E("sink(true);panel('');step(2);who='H';flow=false;render();phone(true);legend(false);cap('<b>③ 첫 3D 설계</b> · 요청대로 만든 처음 형상 · 옆판 23.4 g <span class=\"badge hk\">3D 설계 생성: 해커톤 개발</span>')")
        for k in range(30):
            await cam(a0+0.004*k,0,1.0-0.002*k);await snap()
        # ④ 성능 확인
        await E("step(3);flow=true;render();phone(false);legend(true);cap('<b>④ 성능 확인</b> · 힘·온도 계산 → 힘이 몰리는 곳(빨강), 일하지 않는 재료(파랑) 확인 <span class=\"badge ok\">사전 검증</span>')")
        for k in range(30):
            await cam(a0+0.12+0.004*k,0,0.94);await snap()
        # ⑤ 재설계
        await E("step(4);legend(false)")
        its=['3','8','20','40','80']
        for i in range(5):
            await E(f"showStand(dec(ST.frames[{i}].x),null);showPlate(toS(dec(HT.frames[Math.min({i},HT.frames.length-1)].x)),null)")
            await E(f"cap('<b>⑤ 재설계</b> · {its[i]}회 반복 · 접이 구조를 지키며 재료를 힘·열의 길로 재배치 <span class=\"badge ok\">사전 검증</span>')")
            for k in range(8):
                await cam(a0+0.24+0.004*(i*8+k),0,0.94);await snap()
        hold(4)
        # ⑥ 결과
        await E("step(5);who='A';flow=true;render();legend(true);cap('<b>⑥ 결과</b> · 5 N 변위는 처음 이하로 유지하며 옆판 약 1/3 가볍게, 방열판 평균 온도 상승 폭 약 70% 감소 <span class=\"badge ok\">실제 계산</span>')")
        await E("panel('<div class=\"kpi\"><div><b>약 1/3↓</b>옆판 1개 (5 N 변위 이하, 23.4→15.6 g)</div><div class=\"h\"><b>약 70%↓</b>방열판 평균 온도 상승 폭</div><div class=\"t\"><b>약 2분</b>재설계 계산</div></div>')")
        base=a0+0.4
        for k in range(40):
            await cam(base-0.45*math.sin(math.pi*k/40),0,0.94);await snap()
        # 접기
        await E("panel('');cap('<b>⑥ 결과 · 접기</b> · 꼭대기 힌지를 축으로 뒷 다리 회전 (접는 방식은 기본 틀)')")
        for k in range(16):
            t=(k+1)/16;await E(f"foldT={t};foldTarget={t};applyFold()");await cam(base+0.2*t,0.04*t,0.94);await snap()
        hold(8)
        for k in range(12):
            t=1-(k+1)/12;await E(f"foldT={t};foldTarget={t};applyFold()");await cam(base+0.2*t,0.04*t,0.94);await snap()
        # ⑦ 출력
        await E("step(6);flow=false;render();legend(false);cap('<b>⑦ 파일 출력</b> · 3D 설계 파일·도면·3D 프린트 파일과 성능 리포트 제공 <span class=\"badge hk\">파일 변환: 해커톤 개발</span>')")
        await E("panel('<div class=\"files\"><div>3D 설계 (STEP)<span>치수 수정 가능한 형상</span></div><div>3D 프린트 (STL)<span>바로 출력</span></div><div>설계 도면<span>주요 치수</span></div><div>성능 리포트<span>무게·변형·온도</span></div></div>')")
        for k in range(20):
            await cam(base+0.004*k,0,0.94);await snap()
        hold(10)
        print('frames',n[0]);await b.close()
asyncio.run(main())
