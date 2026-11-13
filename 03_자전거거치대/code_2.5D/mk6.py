from PIL import Image; import base64, io
im=Image.open('../out/FormProof_자전거거치대_도면_v1.png').convert('RGB'); im=im.resize((1600,int(1600*im.height/im.width)),Image.LANCZOS)
b=io.BytesIO(); im.save(b,'JPEG',quality=82); DRW=base64.b64encode(b.getvalue()).decode()
t=open('body5.html').read()
R=[
("holder.userData.ph=[ph,sc]}","holder.userData.ph=[ph,sc]}\nconst hp=new THREE.Group();S.remove(holder);hp.add(holder);holder.position.set(-91,-55,-20);hp.position.set(91,55,20);S.add(hp);\nconst PADM={};for(const k of ['base','r1','r2','r3']){const d=D[k];let s=[0,0,0],n=0;d.vox.forEach((v,e)=>{if(v[2]>=16){s[0]+=d.mode[e][0];s[1]+=d.mode[e][1];s[2]+=d.mode[e][2];n++}});PADM[k]=s.map(x=>x/n)}"),
("  holder.position.set(0,0,0);\n","  hp.position.set(91,55,20);hp.rotation.set(0,0,0);\n"),
("   if(amp)holder.position.set(d.tip[0]*amp,d.tip[1]*amp,d.tip[2]*amp);",
 "   if(amp){const pm=PADM[st.d];hp.position.set(91+pm[0]*amp,55+pm[1]*amp,20+pm[2]*amp);hp.rotation.set(-(d.tip[1]-pm[1])*amp/22,(d.tip[0]-pm[0])*amp/22,0)}"),
("""  <div class="card note">
    <h2>계산과 검증</h2>""","""  <div class="card" id="cOut">
    <h2>결과물</h2>
    <button class="drw" id="drwBtn" aria-label="설계 도면 크게 보기"><img src="data:image/jpeg;base64,__DRW__" alt="설계 도면: 정면도·평면도·우측면도, 주요 치수와 표제란"></button>
    <dl>
      <dt>설계 도면</dt><dd>A4 1:1, 제3각법, 주요 치수·재료·체결 부품</dd>
      <dt>출력용 STL</dt><dd>클램프 포함 약 44 g, 닫힌 형상 확인</dd>
      <dt>성능 확인</dt><dd>1차 진동 64.0 Hz, 옆 처짐 0.30 mm (출력 형상 재해석)</dd>
    </dl>
    <div class="note">도면을 누르면 크게 볼 수 있습니다. PDF·STL 파일은 대화에 첨부되어 있습니다.</div>
  </div>
  <div class="card note">
    <h2>계산과 검증</h2>"""),
("</aside>","</aside>\n<div class=\"lb\" id=\"lb\" hidden><button id=\"lbClose\" aria-label=\"닫기\">닫기 ✕</button><div class=\"lbin\"><img src=\"data:image/jpeg;base64,__DRW__\" alt=\"설계 도면 확대\"></div></div>"),
(".badge{",".drw{all:unset;cursor:zoom-in;display:block;border:1px solid var(--line);border-radius:8px;overflow:hidden;background:#fff}.drw img{display:block;width:100%}\n.drw:focus-visible{outline:2px solid var(--accent)}\n.lb{position:fixed;inset:0;z-index:50;background:rgba(10,14,20,.85);display:flex;flex-direction:column;padding:max(12px,env(safe-area-inset-top,0px)) max(12px,env(safe-area-inset-right,0px)) 12px max(12px,env(safe-area-inset-left,0px))}\n.lb button{all:unset;cursor:pointer;align-self:flex-end;color:#fff;font-weight:700;padding:6px 10px}\n.lbin{flex:1;overflow:auto;background:#fff;border-radius:8px}.lbin img{display:block;width:100%;min-width:900px}\n.badge{"),
("['cIn','cCond','cRes'].forEach(id=>document.getElementById(id).classList.toggle('hl',id===STEPS[i][4]))","['cIn','cCond','cRes','cOut'].forEach(id=>document.getElementById(id).classList.toggle('hl',id===STEPS[i][4]))"),
("옆 처짐 0.30 mm → 기준 충족','cRes']","옆 처짐 0.30 mm → 기준 충족. 설계 도면은 결과물 카드에서 확인','cOut']"),
("v5 · 3D 프린트용","v6 · 3D 프린트용"),
("goStep(0);","goStep(0);\ndocument.getElementById('drwBtn').onclick=()=>{document.getElementById('lb').hidden=false};document.getElementById('lbClose').onclick=()=>{document.getElementById('lb').hidden=true};document.addEventListener('keydown',e=>{if(e.key==='Escape')document.getElementById('lb').hidden=true});"),
]
for a,bb in R:
    assert a in t,a[:60]; t=t.replace(a,bb,1)
open('body6.html','w').write(t)
d=open('page2_data.json').read()
open('../out/bike_mount_v6.html','w').write(open('css_head.html').read().replace('시나리오 v2','시나리오 v6')+t.replace('__DATA__',d).replace('__DRW__',DRW))
print('ok')
