t=open('v6_template.html',encoding='utf-8').read()
def rep(a,b):
    global t; assert a in t,a[:80]; t=t.replace(a,b)
rep('<title>FormProof 시연 v6</title>','<title>FormProof 시연 v7</title>')
rep('grid-template-columns:minmax(0,1fr) minmax(0,340px)','grid-template-columns:minmax(0,340px) minmax(0,1fr)')
a=t.index('    <div class="viewer">');pm='    <div class="card panel" id="panel"></div>\n';b=t.index(pm)
viewer=t[a:b];t=t[:a]+pm+viewer+t[b+len(pm):]
rep('      <div class="tag" id="tag">','      <div class="flow hide" id="flowLeg"><span>힘을 거의 안 받는 재료</span><i></i><span>힘을 많이 받는 재료</span></div>\n      <div class="tag" id="tag">')
rep('.hide{display:none!important}','''.flow{position:absolute;right:10px;bottom:10px;display:flex;align-items:center;gap:8px;font-size:11.5px;color:var(--muted);background:rgba(11,17,25,.86);border:1px solid var(--line);border-radius:8px;padding:6px 10px}
.flow i{display:block;width:90px;height:8px;border-radius:4px;background:linear-gradient(90deg,#30123b,#4686fb,#1ae4b6,#a2fc3c,#fabb39,#e4460a,#7a0403)}
@media (max-width:760px){.flow{bottom:52px}.flow span{display:none}}
.hide{display:none!important}''')
rep("cam.position.set(30,12,34);","cam.position.set(10,7,44);")
rep("ctl.autoRotate=!matchMedia('(prefers-reduced-motion: reduce)').matches;ctl.autoRotateSpeed=0.55;","ctl.autoRotate=false;")
rep("const DRAFT=dec(PRE.draft),SOLID=dec(PRE.solid.x),EN=dec(PRE.en.d);","const DRAFT=dec(PRE.draft),SOLID=dec(PRE.solid.x),AIF=dec(PRE.frames[PRE.frames.length-1].x),ENS={D:dec(PRE.enAll.draft),S:dec(PRE.enAll.solid),A:dec(PRE.enAll.ai)};")
rep("function show(x,opts={}){if(!V)return;clear(V.part);if(!x)return;const E=opts.energy?EN:null;","function show(x,opts={}){if(!V)return;clear(V.part);if(!x)return;const E=opts.energy||null;")
rep("function renderWho(){if(who==='D')show(DRAFT,{color:0xd9dfe6});else if(who==='S')show(SOLID,{color:0xd9dfe6});else show(PRE.frames.length?dec(PRE.frames[PRE.frames.length-1].x):null,{energy:col==='E'})}",
"""function renderWho(){const X=who==='D'?DRAFT:who==='S'?SOLID:AIF,c=who==='A'?0x9fdbe6:0xd9dfe6;show(X,{color:c,energy:col==='E'?ENS[who]:null});
  $('flowLeg').classList.toggle('hide',col!=='E');
  $('tag').innerHTML=col==='E'?(who==='S'?'<b>꽉 찬 형태</b> · 파란 영역은 힘을 거의 받지 않는 재료입니다. 무게만 늘립니다':who==='D'?'<b>초안</b> · 대각 보강대와 상판에 힘이 몰립니다':'<b>AI 설계</b> · 남은 재료 대부분이 힘을 나눠 받습니다')
    :(who==='S'?'<b>꽉 찬 형태</b> · 재료 50%. 가장 덜 휘지만 가장 무겁습니다':who==='D'?'<b>초안</b> · 재료 30%. 같은 무게의 AI 설계보다 4배 이상 휩니다':'<b>AI 설계</b> · 재료 30%. 초안과 같은 무게');}""")
rep("function syncWho(){[['wD','D'],['wA','A'],['wS','S']].forEach(([id,k])=>$(id).classList.toggle('on',who===k));$('cS').classList.toggle('on',col==='S');$('cE').classList.toggle('on',col==='E');$('colBox').style.opacity=who==='A'?1:0.4}",
    "function syncWho(){[['wD','D'],['wA','A'],['wS','S']].forEach(([id,k])=>$(id).classList.toggle('on',who===k));$('cS').classList.toggle('on',col==='S');$('cE').classList.toggle('on',col==='E')}")
rep("$('cE').onclick=()=>{if(who!=='A')return;col='E';syncWho();renderWho()};","$('cE').onclick=()=>{col='E';syncWho();renderWho()};")
rep("if(s===4){ghost(null);who='A';col='S';syncWho();renderWho();$('tag').innerHTML='<b>비교</b> · 위 버튼으로 초안 / AI 설계 / 꽉 찬 형태를 바꿔 보세요';","if(s===4){ghost(null);who='A';col='S';syncWho();renderWho();")
rep("  $('whoBox').classList.toggle('hide',s<4);","  $('whoBox').classList.toggle('hide',s<4);$('flowLeg').classList.add('hide');")
rep('<p class="lead">AI 설계는 꽉 찬 형태보다 강한 것이 아니라, 힘을 거의 받지 않는 재료를 덜어내 무게 대비 성능을 높인 것입니다.</p>',
    '<p class="lead">AI 설계는 꽉 찬 형태보다 강한 것이 아니라, 힘을 거의 받지 않는 재료를 덜어내 무게 대비 성능을 높인 것입니다. 3D 화면 위 “힘의 흐름”을 켜고 세 형상을 바꿔 보세요. 같은 색 기준입니다.</p>')
s=open('v6_surface.js',encoding='utf-8').read()
a="elo=vals[Math.floor(vals.length*0.05)];ehi=vals[Math.floor(vals.length*0.97)]}"
assert a in s; s=s.replace(a,"if(enLog){elo=0;ehi=1}else{elo=vals[Math.floor(vals.length*0.05)];ehi=vals[Math.floor(vals.length*0.97)]}}")
out=t.replace('__DATA__',open('v7_data.json').read()).replace('__SURFACE__',s)
open('formproof_demo_v7.html','w',encoding='utf-8').write(out);print('ok')
