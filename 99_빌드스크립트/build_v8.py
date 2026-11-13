import re
s=open('formproof_demo_v7.html',encoding='utf-8').read()
def rep(a,b):
    global s; assert a in s,a[:80]; s=s.replace(a,b)
rep('<title>FormProof 시연 v7</title>','<title>FormProof 시연 v8</title>')
# physical constants
rep("const eid=(i,j,k)=>i+NX*(j+NY*k);","""const eid=(i,j,k)=>i+NX*(j+NY*k);
const PHY={Lx:120,Ly:80,T:8,h:2,rho:1.24,E:3500,kg:5};
const VOLCM3=PHY.Lx*PHY.Ly*PHY.T/1000;
const grams=v=>v*VOLCM3*PHY.rho;
const mm=c=>c*(PHY.kg*9.81/2)/(PHY.E*PHY.h);""")
# idea default text
rep("벽에 나사 2개로 다는 선반 브래킷. 위에 책을 올려둘 거야</textarea>","벽에 나사 2개로 다는 선반 브래킷. 위에 책 5kg 정도 올려둘 거야</textarea>")
# step2 kv
rep("<div><span>재료량</span><span>설계 공간의 ${pct(PRE.v)}</span></div></div>",
    "<div><span>크기</span><span>${PHY.Lx}×${PHY.Ly}mm, 두께 ${PHY.T}mm</span></div><div><span>재질</span><span>PLA</span></div><div><span>무게</span><span>${grams(PRE.v).toFixed(1)} g</span></div><div><span>책 ${PHY.kg}kg 처짐</span><span>${mm(PRE.cD).toFixed(3)} mm</span></div></div>")
rep("<li><span class=\"dot\" style=\"background:var(--ok)\"></span><span><b>목표</b> · 초안과 같은 무게로 처짐 최소화</span></li></ul>",
    "<li><span class=\"dot\" style=\"background:var(--ok)\"></span><span><b>목표</b> · 초안과 같은 무게(${grams(PRE.v).toFixed(1)} g)로 처짐 최소화</span></li></ul>")
# compare card html
rep('<h2>VERIFY · 같은 하중, 같은 3D 해석</h2><span class="note">처짐 지수 = 하중이 한 일(compliance), 낮을수록 덜 휨</span>',
    '<h2>VERIFY · PLA · 책 5kg · 같은 3D 해석</h2><span class="note">처짐 = 선반 면 평균 처짐</span>')
rep('''      <div class="claim"><b id="clB">—</b><span id="clBs"></span></div>
    </div>''','''      <div class="claim"><b id="clB">—</b><span id="clBs"></span></div>
      <div class="claim"><b id="clC">—</b><span id="clCs"></span></div>
    </div>''')
rep('.claims{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}','.claims{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}')
row=lambda p:f'<div class="row"><span>재료량</span><b id="{p}V">—</b></div><div class="row"><span>무게 (PLA)</span><b id="{p}G">—</b></div><div class="row"><span>책 5kg 처짐</span><b id="{p}M">—</b></div><div class="row"><span>무게당 강성 (초안=1)</span><b id="{p}K">—</b></div>'
for p in ['d','a','s']:
    rep(f'<div class="row"><span>재료량</span><b id="{p}V">—</b></div><div class="row"><span>처짐 지수</span><b id="{p}C">—</b></div>',row(p))
# note under compare
i=s.index('<p class="note">세 형상 모두 판 두께가 같고');j=s.index('</p>',i)+4
s=s[:i]+'<p class="note">조건: PLA(밀도 1.24 g/cm³, 탄성계수 3.5 GPa 가정), 120×80mm·두께 8mm, 100% 채움, 나사 2곳 고정, 선반 면에 책 5kg 균일 하중. 무게는 계산 형상의 부피 기준이며 실제 출력 무게는 채움률에 따라 다릅니다. 처짐은 선형 탄성 해석값이라 실측과 차이가 있을 수 있습니다. 같은 무게의 꽉 찬 삼각형(두께 60%)은 두께 비례 근사로 처짐 약 <span id="sThin">—</span> mm입니다.</p>'+s[j:]
# step4 JS values
i=s.index("    $('dV').textContent=pct(vA);");j=s.index("$('tot').textContent=PRE.total.toFixed(0);")+len("$('tot').textContent=PRE.total.toFixed(0);")
s=s[:i]+"""    const gD=grams(vA),gA=grams(vA),gS=grams(vS),k=(c,g)=>(cD*gD)/(c*g);
    const put=(p,v,g,c)=>{$(p+'V').textContent=pct(v);$(p+'G').textContent=g.toFixed(1)+' g';$(p+'M').textContent=mm(c).toFixed(3)+' mm';$(p+'K').textContent=k(c,g).toFixed(1)};
    put('d',vA,gD,cD);put('a',vA,gA,cA);put('s',vS,gS,cS);
    $('clA').textContent=(cD/cA).toFixed(1)+'배 덜 처짐';$('clAs').textContent=`초안과 같은 ${gA.toFixed(1)} g에서`;
    $('clB').textContent=(gS-gA).toFixed(0)+' g 가벼움';$('clBs').textContent=`꽉 찬 삼각형(${gS.toFixed(1)} g) 대비 −${((1-vA/vS)*100).toFixed(0)}%. 대신 처짐 ${((cA/cS-1)*100).toFixed(0)}% 큼`;
    $('clC').textContent='무게당 강성 '+k(cA,gA).toFixed(1);$('clCs').textContent=`초안 1.0 · 꽉 찬 형태 ${k(cS,gS).toFixed(1)}. 같은 1g이 가장 많이 일함`;
    $('sThin').textContent=mm(cS*vS/vA).toFixed(3);$('tot').textContent=PRE.total.toFixed(0);"""+s[j:]
# step5 kv
rep("<div class=\"kv\"><div><span>출력 방향</span><span>판을 바닥에 눕혀서</span></div>",
    "<div class=\"kv\"><div><span>재질 · 무게</span><span>PLA · ${grams(PRE.v).toFixed(1)} g</span></div><div><span>출력 방향</span><span>판을 바닥에 눕혀서 (서포트 불필요)</span></div><div><span>구조 최소 단위</span><span>2 mm 격자 (0.4 mm 노즐로 출력 가능한 크기)</span></div>")
# tags with grams
rep("'<b>꽉 찬 형태</b> · 재료 50%. 가장 덜 휘지만 가장 무겁습니다'","`<b>꽉 찬 형태</b> · ${grams(PRE.solid.v).toFixed(1)} g. 가장 덜 휘지만 가장 무겁습니다`")
rep("'<b>초안</b> · 재료 30%. 같은 무게의 AI 설계보다 4배 이상 휩니다'","`<b>초안</b> · ${grams(PRE.v).toFixed(1)} g. 같은 무게의 AI 설계보다 4배 이상 휩니다`")
rep("'<b>AI 설계</b> · 재료 30%. 초안과 같은 무게'","`<b>AI 설계</b> · ${grams(PRE.v).toFixed(1)} g. 초안과 같은 무게`")
rep("재료는 등방성 정규화값이고,","재료는 등방성(PLA 가정값)이고,")
open('formproof_demo_v8.html','w',encoding='utf-8').write(s);print('ok')
