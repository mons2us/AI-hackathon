s=open('stand_template_v4.html',encoding='utf-8').read()
def R(a,b):
    global s
    assert a in s,a[:70]; s=s.replace(a,b,1)
R('<title>게이밍 폰 거치대</title>','<title>방열 스마트폰 거치대</title>')
import re
s=re.sub(r'<h1>게이밍 폰 거치대 · .*?</h1>','<h1>방열 스마트폰 거치대 · <span>가볍게 · 접히게</span> + <em>덜 뜨겁게</em></h1>',s,count=1)
s=re.sub(r'(<div class="top">\s*<h1>.*?</h1>\s*)<p>.*?</p>',r'\1<p>요청 한 문장에서 AI가 두 가지 목표를 찾습니다. 접히는 옆판은 3D 구조 계산으로 같은 튼튼함에서 가장 가볍게, 등판 방열판은 열전도 계산으로 열이 잘 빠지게 다시 설계했습니다. 옆판·방열판의 형상과 수치는 실제 계산 결과이고, 폰·연결 막대·금속 막대·화살표·접는 동작은 설명용입니다.</p>',s,count=1,flags=re.S)
R('“게임할 때 쓰는 폰 거치대 만들어줘. 세게 터치해도 안 흔들리고, 폰이 덜 뜨거웠으면 좋겠어.”','“폰으로 게임하거나 유튜브를 오래 보면 폰이 뜨거워지고 배터리도 빨리 닳아. 가방에 넣고 다니게 가볍고 접히는 거치대 만들어줘.”')
R('<div class="goal"><b>① 구조 · 옆판</b><span>터치해도 덜 흔들리게<br>(같은 PLA 양)</span></div>','<div class="goal"><b>① 구조 · 접는 옆판</b><span>튼튼함은 그대로,<br>재료는 최소로 (가볍게)</span></div>')
R('<div><span>옆판 (2장)</span><span>120 × 100 mm, 두께 8 mm</span></div>','<div><span>옆판 (2장)</span><span>120 × 100 mm, 두께 8 mm</span></div>\n        <div><span>접기 (기본 틀)</span><span>꼭대기 힌지 · 뒷 다리 접힘</span></div>')
R('<div class="m"><span>터치 시 흔들림</span><b id="kSway">—</b><small id="kSway2"></small></div>','<div class="m"><span>옆판 무게 (같은 튼튼함)</span><b id="kSway">—</b><small id="kSway2"></small></div>')
R('<p class="note">직관 설계(같은 재료량) = 100% 기준. 낮을수록 좋음.</p>','<p class="note">처음 설계(접이식, 직선 뒷 다리) = 100% 기준. 낮을수록 좋음. 다시 설계 계산 약 <span id="kTime">—</span>분.</p>')
R('<div class="box"><button id="vS">형상</button>','<div class="box"><button id="vF">접기</button></div>\n        <div class="box"><button id="vS">형상</button>')
R('계산 결과: 옆판·방열판 형상과 색 · 설명용: 폰·연결 막대·금속 막대','계산 결과: 옆판·방열판 형상과 색 · 설명용: 폰·연결 막대·금속 막대·접는 동작')
# 옆판 비교 카드
s=re.sub(r'<div class="sec"><span class="pill">① 구조</span>.*?</p>\s*</div>',
'''<div class="sec"><span class="pill">① 구조</span><h2>접는 옆판 · 같은 튼튼함, 다른 무게 · 힘의 흐름</h2></div>
    <div class="grid3">
      <div class="cc"><h3>처음 설계 · 직선 뒷 다리</h3><canvas id="sH" width="360" height="300"></canvas><span class="v" id="tH"></span></div>
      <div class="cc ai"><h3>AI 설계 · 같은 튼튼함</h3><canvas id="sI" width="360" height="300"></canvas><span class="v" id="tI"></span></div>
      <div class="cc"><h3>AI 설계 · 접은 모습</h3><canvas id="sF" width="360" height="300"></canvas><span class="v" id="tF"></span></div>
    </div>
    <p class="note">왼쪽 빈 공간 = 폰 자리. 흰 원 = 힌지(두 다리는 여기서만 연결), 청록 화살표 = 터치 하중, 노란 막대 = 바닥에 닿는 발. 처음 설계는 등받이 두께와 뒷 다리 두께를 바꿔 본 안 중 가장 튼튼한 안입니다. 같은 무게(약 23 g)로 비교하면 AI 설계가 약 1.6배 튼튼합니다.</p>
  </div>''',s,count=1,flags=re.S)
R('<b>구조</b> · 3D 선형 탄성 유한요소, 형상은 2 mm 격자(60×50×4 요소)에서 위상 최적화 <span id="itS">—</span>회 반복(약 <span id="tS2">—</span>초). 흔들림 수치는 같은 형상을 1 mm 격자(4.8만 요소)로 다시 계산한 값(2 mm 격자는 차이를 과대평가해 교체). 1 mm 격자에서 처음부터 다시 최적화해도 차이는 1.33배로 비슷. PLA 탄성계수 3.5 GPa·밀도 1.24 g/cm³·100% 채움 가정. 흔들림은 터치 5 N일 때 등받이 위쪽의 최대 변위.',
 '<b>구조</b> · 3D 선형 탄성 유한요소, 형상은 2 mm 격자(60×50×4 요소)에서 위상 최적화 <span id="itS">—</span>회 반복(약 <span id="tS2">—</span>초). 튼튼함 = 터치 5 N + 폰 200 g일 때 등받이 위쪽 변위, 1 mm 격자로 다시 계산한 값. 두 다리는 꼭대기 힌지 한 줄로만 연결(회전 자유), 펼친 상태에서 두 발은 미끄러지지 않는다고 가정. PLA 탄성계수 3.5 GPa·밀도 1.24 g/cm³·100% 채움 가정. 힌지 위치·접는 방식은 기본 틀이며 AI가 고른 것이 아님.')
# JS: showStand 분리 + 접기
R('''function showStand(x,en){if(!V)return;clear(V.stand);if(!x)return;NX=ST.nelx;NY=ST.nely;NZ=ST.nelz;ZBLUR=false;
  const geo=surface(x,en,true);const mat=new THREE.MeshStandardMaterial({color:en?0xffffff:0xd8dee6,vertexColors:!!en,roughness:0.55,metalness:0.05});
  for(const zc of[-44,44]){const me=new THREE.Mesh(geo,mat);me.scale.set(2,2,2);me.position.set(ST.nelx,ST.nely,zc);V.stand.add(me)}
  /* 두 옆판을 잇는 바닥 막대 (참고용) */
  const bar=new THREE.Mesh(new THREE.BoxGeometry(6,6,80),new THREE.MeshStandardMaterial({color:0x8a97a6,roughness:0.6}));bar.position.set(2*(ST.nelx-4),3,0);V.stand.add(bar)}''',
'''const HX=2*ST.hinge.i,HY=2*ST.hinge.j;
const FOLD=(()=>{const a1=Math.atan2(2-HY,2*(ST.nelx-4)-HX),a0=Math.atan2(2-HY,2*7-HX);return a0-a1})();
let foldT=0,foldTarget=0,rearGroups=[];
const split=(x,front)=>{const o=new Float32Array(x.length);for(let e=0;e<x.length;e++){const i=e%ST.nelx;o[e]=(front?i<ST.hinge.i:i>ST.hinge.i)?x[e]:0}return o};
function showStand(x,en){if(!V)return;clear(V.stand);rearGroups=[];if(!x)return;NX=ST.nelx;NY=ST.nely;NZ=ST.nelz;ZBLUR=false;
  const mat=new THREE.MeshStandardMaterial({color:en?0xffffff:0xd8dee6,vertexColors:!!en,roughness:0.55,metalness:0.05});
  const gF=surface(split(x,true),en,true),gR=surface(split(x,false),en,true);
  for(const zc of[-44,44]){const me=new THREE.Mesh(gF,mat);me.scale.set(2,2,2);me.position.set(ST.nelx,ST.nely,zc);V.stand.add(me);
    const piv=new THREE.Group();piv.position.set(HX,HY,zc);piv.userData.zc=zc;const mr=new THREE.Mesh(gR,mat);mr.scale.set(2,2,2);mr.position.set(ST.nelx-HX,ST.nely-HY,0);piv.add(mr);
    const pin=new THREE.Mesh(new THREE.CylinderGeometry(2.2,2.2,18,20),new THREE.MeshStandardMaterial({color:0xe6edf3,metalness:0.6,roughness:0.3}));pin.rotation.x=Math.PI/2;pin.position.set(HX,HY,zc);V.stand.add(pin);
    V.stand.add(piv);rearGroups.push(piv)}
  /* 두 뒷 다리를 잇는 막대 (설명용) */
  const piv=new THREE.Group();piv.position.set(HX,HY,0);const bar=new THREE.Mesh(new THREE.BoxGeometry(6,6,80),new THREE.MeshStandardMaterial({color:0x8a97a6,roughness:0.6}));bar.position.set(2*(ST.nelx-4)-HX,3-HY,0);piv.add(bar);piv.userData.bar=true;V.stand.add(piv);rearGroups.push(piv);applyFold()}
function applyFold(){const t=foldT,ease=t*t*(3-2*t);for(const g of rearGroups){g.rotation.z=FOLD*ease;if(!g.userData.bar)g.position.z=g.userData.zc-Math.sign(g.userData.zc)*9*ease}
  if(V){V.phone.forEach(o=>o.visible=$('vP').classList.contains('on')&&ease<0.05)}}
(function foldLoop(){requestAnimationFrame(foldLoop);if(Math.abs(foldT-foldTarget)>1e-3){foldT+=Math.sign(foldTarget-foldT)*0.02;foldT=Math.max(0,Math.min(1,foldT));applyFold()}})();''')
R("let who='A',flow=true,playT=null;","let who='A',flow=true,playT=null;\n$('vF').onclick=()=>{foldTarget=foldTarget?0:1;$('vF').classList.toggle('on',!!foldTarget);$('vF').textContent=foldTarget?'펼치기':'접기'};")
R("$('tag').innerHTML=who==='A'?`<b>AI 설계</b> · 흔들림 ${pc(ST.ai.um,ST.hu.um)} · 평균 온도 상승 ${pc(HT.ai.tavg,HT.hu.tavg)} (직관 = 100%)`:`<b>직관 설계</b> · 버팀대 옆판 + 직선 막대 방열판 (같은 재료량)`}",
  "$('tag').innerHTML=who==='A'?`<b>AI 설계</b> · 옆판 ${ST.ai.g.toFixed(1)} g (같은 튼튼함 기준 ${pc(ST.ai.g,ST.hu.g)}) · 평균 온도 상승 약 ${Math.round(HT.ai.tavg/HT.hu.tavg*10)*10}%`:`<b>처음 설계</b> · 직선 뒷 다리 옆판 ${ST.hu.g.toFixed(1)} g + 직선 막대 방열판`}")
# 2D 카드
R("const SP={A:ST.huA,H:ST.hu,I:ST.ai,S:ST.solid},spw=o=>1/(o.um*o.g),base=spw(ST.hu);\nfor(const k in SP){const o=SP[k];prof('s'+k,dec(o.x),dec(o.en));$('t'+k).innerHTML=`${o.g.toFixed(1)} g · 흔들림 ${o.um.toFixed(1)} μm<br>무게당 단단함 ${(spw(o)/base).toFixed(2)}`}",
'''const hingeDot=(id)=>{const cv=$(id),g=cv.getContext('2d'),W=cv.width,H=cv.height,nx=ST.nelx,ny=ST.nely,s=Math.min((W-20)/nx,(H-30)/ny),ox=(W-nx*s)/2,oy=8;g.strokeStyle='#fff';g.lineWidth=2;g.beginPath();g.arc(ox+ST.hinge.i*s,oy+(ny-ST.hinge.j)*s,5,0,7);g.stroke();g.lineWidth=1};
for(const [k,o] of [['H',ST.hu],['I',ST.ai]]){prof('s'+k,dec(o.x),dec(o.en));hingeDot('s'+k);$('t'+k).innerHTML=`${o.g.toFixed(1)} g · 변위 ${o.um.toFixed(1)} μm`}
$('tH').innerHTML+=`<br>무게 100%`;$('tI').innerHTML+=`<br>무게 ${pc(ST.ai.g,ST.hu.g)} · 튼튼함 같은 수준`;
(function(){const cv=$('sF'),g=cv.getContext('2d'),W=cv.width,H=cv.height,nx=ST.nelx,ny=ST.nely,s=Math.min((W-20)/nx,(H-30)/ny),ox=(W-nx*s)/2,oy=8,x=dec(ST.ai.x);
  g.fillStyle='#0d1620';g.fillRect(0,0,W,H);const hx=ST.hinge.i,hy=ST.hinge.j,c=Math.cos(FOLD),sn=Math.sin(FOLD);let minx=1e9,maxx=-1e9,miny=1e9;
  for(let i=0;i<nx;i++)for(let j=0;j<ny;j++){let v=0;for(let k=0;k<ST.nelz;k++)v=Math.max(v,x[i+nx*(j+ny*k)]);if(v<0.5)continue;
    let px=i+0.5,py=j+0.5;if(i>hx){const dx=px-hx,dy=py-hy;px=hx+dx*c-dy*sn;py=hy+dx*sn+dy*c;g.fillStyle='rgba(63,193,214,.85)'}else g.fillStyle='rgb(201,211,220)';
    minx=Math.min(minx,px);maxx=Math.max(maxx,px);miny=Math.min(miny,py);g.fillRect(ox+(px-0.5)*s,oy+(ny-py-0.5)*s,s+0.6,s+0.6)}
  g.strokeStyle='#fff';g.lineWidth=2;g.beginPath();g.arc(ox+hx*s,oy+(ny-hy)*s,5,0,7);g.stroke();
  $('tF').innerHTML=`청록 = 접힌 뒷 다리 (힌지 기준 ${Math.round(-FOLD*180/Math.PI)}° 회전)<br>옆에서 본 깊이 120 → 약 ${Math.round((maxx-Math.min(0,minx))*2/10)*10} mm`})();''')
R("$('kSway').textContent=pc(ST.ai.um,ST.hu.um);$('kSway2').textContent=`${ST.hu.um.toFixed(1)} → ${ST.ai.um.toFixed(1)} μm · ${(ST.hu.um/ST.ai.um).toFixed(2)}배 단단`;",
  "$('kSway').textContent='약 '+Math.round(ST.ai.g/ST.hu.g*10)*10+'%';$('kSway2').textContent=`${ST.hu.g.toFixed(1)} → ${ST.ai.g.toFixed(1)} g · 약 1/3 가볍게`;$('kTime').textContent=Math.max(1,Math.round((ST.sec+HT.time)/60));")
R("$('kAvg').textContent=pc(HT.ai.tavg,HT.hu.tavg);","$('kAvg').textContent='약 '+Math.round(HT.ai.tavg/HT.hu.tavg*10)*10+'%';")
open('stand_template_v4.html','w',encoding='utf-8').write(s)
