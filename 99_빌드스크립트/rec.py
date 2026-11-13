import asyncio,math
from playwright.async_api import async_playwright
F="gaming_stand_v4_rec.html"
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
        await pg.add_style_tag(content=".main{grid-template-columns:1fr !important}.main>.card{display:none !important}#gl{height:720px !important}.viewer .hud,.viewer .tag:nth-of-type(2){display:none !important}.tag{font-size:20px !important;padding:10px 16px !important}.tag b{font-weight:700}")
        await pg.evaluate("document.querySelectorAll('.viewer .tag')[1].style.display='none'")
        await pg.wait_for_timeout(800)
        el=await pg.query_selector("#gl");vw=await pg.query_selector(".viewer")
        await pg.evaluate("document.getElementById('vP').classList.remove('on');V.phone.forEach(o=>o.visible=false)")
        n=[0]
        async def snap(k=1):
            for _ in range(k):
                await vw.screenshot(path=f"vid/f{n[0]:04d}.png");n[0]+=1
        async def cam(az,el_=0.0,r=1.0):
            await pg.evaluate(f"(()=>{{const t=new THREE.Vector3(55,48,0),c=__cam;const R=Math.hypot(-285,102,210)*{r};const a={az},e=0.36+{el_};c.position.set(t.x+R*Math.cos(e)*Math.cos(a),t.y+R*Math.sin(e),t.z+R*Math.cos(e)*Math.sin(a));c.lookAt(t);__ctl.target.copy(t);__ctl.update()}})()")
        tag=lambda h:pg.evaluate("h=>{document.getElementById('tag').innerHTML=h}",h)
        a0=math.atan2(210,-285)
        FPS=12
        # A: 재설계 과정
        for i in range(5):
            await pg.evaluate(f"showStand(dec(ST.frames[{i}].x),null);showPlate(toS(dec(HT.frames[Math.min({i},HT.frames.length-1)].x)),null)")
            await tag(f"<b>① AI 재설계 과정</b> · 옆판 {['3','8','20','40','80'][i]}회 반복 · 재료가 힘·열의 길을 따라 재배치")
            for k in range(FPS):
                await cam(a0+0.004*(i*FPS+k));await snap()
        # B: 힘·온도 분포 + 회전
        await pg.evaluate("who='A';flow=true;render()")
        await tag("<b>② AI 설계 결과</b> · 색 = 계산된 힘 크기(옆판)·온도(방열판) · 옆판 무게 약 1/3↓, 온도 상승 폭 약 70%↓")
        base=a0+0.004*5*FPS
        for k in range(FPS*6):
            await cam(base-0.9*math.sin(math.pi*k/(FPS*6))*0.5);await snap()
        # C: 접기
        await tag("<b>③ 접기</b> · 꼭대기 힌지를 축으로 뒷 다리 회전 (접이 구조를 유지한 채 설계)")
        for k in range(FPS*2):
            t=(k+1)/(FPS*2);await pg.evaluate(f"foldT={t};foldTarget={t};applyFold()");await cam(base+0.25*t,0.05*t);await snap()
        await snap(FPS)
        for k in range(FPS*2):
            t=1-(k+1)/(FPS*2);await pg.evaluate(f"foldT={t};foldTarget={t};applyFold()");await cam(base+0.25*t,0.05*t);await snap()
        # D: 처음 설계 vs AI
        await pg.evaluate("who='H';render()");await tag("<b>④ 비교: 처음 설계</b> · 직선 뒷 다리 옆판 23.4 g + 직선 막대 방열판");await cam(base);await snap(FPS*2)
        await pg.evaluate("who='A';render()");await tag("<b>④ 비교: AI 설계</b> · 같은 튼튼함, 옆판 15.6 g · 계산 약 2분");await snap(FPS*2)
        print('frames',n[0]);await b.close()
asyncio.run(main())
