import json, base64, io, numpy as np, trimesh
from PIL import Image
V=json.load(open('ver4.json'))
t=open('body6.html').read()
def rep(a,b,cnt=1):
    global t
    assert a in t,a[:70]; t=t.replace(a,b,cnt)
rep("""      <dt>고정 부품</dt><dd>핸들바 클램프 Ø31.8 mm, M4 볼트 1개</dd>
      <dt>폰 받침 연결</dt><dd>받침판 20×20 mm, Ø8 mm 인서트 구멍 (시판 폰 클램프 장착)</dd>
      <dt>설계 공간</dt><dd>팔 80 × 20 × 32 mm</dd>
      <dt>폰 + 클램프</dt><dd>250 g, 무게 중심 받침판 위 약 22 mm</dd>
      <dt>충격</dt><dd>위아래 5 g, 옆 5 g</dd>
      <dt>제작</dt><dd>PETG 3D 프린트, 옆으로 눕혀 출력, 최소 두께 약 4 mm</dd>
      <dt>판정 기준</dt><dd>1차 진동 ≥ 60 Hz, 옆 처짐 ≤ 0.5 mm</dd>""",
"""      <dt>노면 진동</dt><dd>자갈길 주성분 34.6–45.6 Hz, 최대 48.5 g [1]</dd>
      <dt>진동 판정</dt><dd>1차 진동 ≥ 91 Hz (= 2 × 45.6 Hz, 증폭 1.33배 이하)</dd>
      <dt>강도 판정</dt><dd>48.5 g 충격 시 응력 ≤ 26 MPa (항복 39 ÷ 안전율 1.5)</dd>
      <dt>재료</dt><dd>PETG 출력물 E 1.7 GPa, 항복 39 MPa, 층간 16.4 MPa [2]</dd>
      <dt>고정 부품</dt><dd>핸들바 클램프 Ø31.8 mm, M4 볼트</dd>
      <dt>폰 + 클램프</dt><dd>250 g, 무게 중심 받침판 위 약 22 mm</dd>
      <dt>제작</dt><dd>옆으로 눕혀 출력, 최소 두께 약 4 mm</dd>
      <dt>가정</dt><dd>옆 충격 = 위아래 충격, 안전율 1.5, 폰+클램프 250 g</dd>""")
rep('<h2>3D 설계 생성: 형상 + 물리 조건</h2>','<h2>3D 설계 생성: 형상 + 물리 조건 (근거 표시)</h2>')
rep("<th>설계안</th><th>팔 무게</th><th>전체</th><th>1차 진동</th><th>위아래 처짐</th><th>옆 처짐</th><th>판정</th>","<th>설계안</th><th>팔 무게</th><th>전체</th><th>1차 진동</th><th>최대 응력<br>(48.5 g)</th><th>판정</th>")
rep("const NX=40,NZ=16,H=2,X0=20,Y0=45,Z0=-16;","const NX=40,NZ=16,H=2,X0=20,Z0=-16;")
rep("const DESC={base:'',r1:'옆 충격 2 g로 설정',r2:'옆 충격 5 g로 강화',r3:'재료 비율 24 → 28%',stl:'클램프 포함, 1 mm 재해석'};","const DESC={base:'',r1:'이전 설계 (폭 20 mm, 재료 28%)',r2:'재료 비율 28 → 45%',r3:'설계 폭 20 → 32 mm',stl:'클램프 포함, 1 mm 재해석'};")
rep("const VER={mass:43.8,f:[64.0,67.2],tipz:0.091,tipy:0.300};","const VER={mass:%.1f,f:[%.1f,%.1f],vmax:%.1f};"%(V['mass'],V['f'][0],V['f'][1],V['vmax']))
rep("const LIM={f:60,dy:0.5};\nfunction verdict(d){return (d.f[0]>=LIM.f&&d.tipy<=LIM.dy)?['good','충족']:['bad','미충족']}",
    "const LIM={f:91.2,vm:26};const CLAMP={10:24.4,16:38.7};\nfunction verdict(d){return (d.f[0]>=LIM.f&&d.vmax<=LIM.vm)?['good','충족']:['bad','미충족']}")
rep("const SNAP={};for(const k of ['r1','r2','r3']){const a=b64u8(PD.SN[k]);","const SNAP={};for(const k of ['r1','r2','r3']){const a=b64u8(D[k].snap);")
rep("<td>${(k==='stl'?d.mass:d.mass+24.4).toFixed(1)} g</td><td>${d.f[0].toFixed(1)} Hz</td><td>${d.tipz.toFixed(2)} mm</td><td>${d.tipy.toFixed(2)} mm</td>",
    "<td>${(k==='stl'?d.mass:d.mass+CLAMP[d.ny]).toFixed(1)} g</td><td>${d.f[0].toFixed(1)} Hz</td><td>${d.vmax.toFixed(1)} MPa</td>")
# clamps of two widths
i=t.index("{const d2r=Math.PI/180"); j=t.index("clampGrp.push(m,root)}")+len("clampGrp.push(m,root)}")
blk=t[i:j]
new="const clampW={};for(const W of [20,32]){const grp=[];"+blk[1:-1].replace("depth:20","depth:W").replace("m.position.y=65","m.position.y=55+W/2").replace("new THREE.BoxGeometry(4,20,32)","new THREE.BoxGeometry(4,W,32)").replace("clampGrp.push(m,root)","grp.push(m,root);clampW[W]=grp")+"}"
t=t[:i]+new+t[j:]
rep("clampGrp.forEach(m=>m.visible=!stlMesh.visible);","const cw=st.d==='stl'?0:(D[st.d].ny*2);for(const W of [20,32])clampW[W].forEach(m=>m.visible=!stlMesh.visible&&W===cw);")
rep("40*10*18","40*16*18")
rep("const vpos=(i,j,k)=>[X0+i*H+H/2,Y0+j*H+H/2,Z0+k*H+H/2];","let Y0=45;const vpos=(i,j,k)=>[X0+i*H+H/2,Y0+j*H+H/2,Z0+k*H+H/2];")
rep("  hp.position.set(91,55,20);hp.rotation.set(0,0,0);\n","  hp.position.set(91,55,20);hp.rotation.set(0,0,0);if(st.d!=='stl'){Y0=D[st.d].Y0}const NY=st.d!=='stl'?D[st.d].ny:16;\n")
rep("for(let j=0;j<10;j++){M4.makeTranslation(...vpos(i,j,k));IM.setMatrixAt(n,M4);IM.setColorAt(n,col.setRGB","for(let j=0;j<NY;j++){M4.makeTranslation(...vpos(i,j,k));IM.setMatrixAt(n,M4);IM.setColorAt(n,col.setRGB")
rep("for(let i=30;i<40;i++)for(let k=16;k<18;k++)for(let j=0;j<10;j++)","for(let i=30;i<40;i++)for(let k=16;k<18;k++)for(let j=0;j<NY;j++)")
rep("(z?' · 위아래 충격 5 g':' · 옆 충격 5 g')","(z?' · 위아래 충격 48.5 g':' · 옆 충격 48.5 g')")
rep("""'<b>3D 설계 생성</b> · 클램프(고정 부품) + 팔 + 받침판, 물리 조건: 폰+클램프 250 g(무게 중심 위쪽), 위아래·옆 충격 5 g','cCond'""",
    """'<b>3D 설계 생성</b> · 클램프 + 팔 + 받침판, 물리 조건은 측정 논문·재료 데이터시트로 근거를 달아 정의 (자갈길 34.6–45.6 Hz, 최대 48.5 g)','cCond'""")
rep("'<b>성능 확인</b> · 처음 설계: 1차 진동 28.8 Hz, 옆 처짐 0.79 mm → 기준 미충족 (움직임은 과장 표시)'",
    "'<b>성능 확인</b> · 처음 설계: 1차 진동 26.5 Hz로 자갈길 진동 대역 가까이, 충격 응력 26.4 MPa → 미충족 (움직임은 과장 표시)'")
rep("'<b>재설계</b> · 1차 54 Hz → 2차 58 Hz (미충족) → 3차 66 Hz (충족). 성능 확인 결과로 조건·재료 비율을 바꿔 3회 반복'",
    "'<b>재설계</b> · 1차 61 Hz (이전 설계, 공진 증폭 2.3배) → 2차 재료 증가 83 Hz → 3차 폭 32 mm 100 Hz (충족)'")
rep("'<b>결과</b> · 출력용 STL (클램프 포함 약 44 g), 옆으로 눕혀 출력. 출력 형상 재해석: 1차 진동 64.0 Hz, 옆 처짐 0.30 mm → 기준 충족. 설계 도면은 결과물 카드에서 확인'",
    "'<b>결과</b> · 출력용 STL (클램프 포함 약 74 g). 출력 형상 재해석: 1차 진동 %.1f Hz, 최대 응력 %.1f MPa → %s. 도면은 결과물 카드에서 확인'"%(V['f'][0],V['vmax'],'기준 충족' if V['f'][0]>=91.2 and V['vmax']<=26 else '기준 미충족'))
rep("${NAMES[st.d]}: ${d.mass.toFixed(1)} g · 1차 진동 ${d.f[0].toFixed(1)} Hz · 위아래 처짐 ${d.tipz.toFixed(2)} mm · 옆 처짐 ${d.tipy.toFixed(2)} mm",
    "${NAMES[st.d]}: ${d.mass.toFixed(1)} g · 1차 진동 ${d.f[0].toFixed(1)} Hz · 최대 응력 ${d.vmax.toFixed(1)} MPa")
rep("<dt>출력용 STL</dt><dd>클램프 포함 약 44 g, 닫힌 형상 확인</dd>","<dt>출력용 STL</dt><dd>클램프 포함 약 74 g, 닫힌 형상 확인</dd>")
rep("<dd>1차 진동 64.0 Hz, 옆 처짐 0.30 mm (출력 형상 재해석)</dd>","<dd>1차 진동 %.1f Hz, 최대 응력 %.1f MPa (출력 형상 재해석)</dd>"%(V['f'][0],V['vmax']))
rep("v6 · 3D 프린트용","v7 · 근거 기반 조건")
# sources card
rep("""  <div class="card note">
    <h2>계산과 검증</h2>""","""  <div class="card note">
    <h2>근거</h2>
    <p>[1] Viellehner & Potthast, “Road to lab: cobblestone cycling vibrations transferred to the lab”, ISBS Proceedings 38 (2020). 바퀴 축(드롭아웃)에서 측정한 값. <a href="https://commons.nmu.edu/isbs/vol38/iss1/216/" target="_blank" rel="noopener">링크</a></p>
    <p>[2] Prusament PETG V0 기술 데이터시트 v1.0 (2023), 출력 시편 ISO 527-1 수평 방향 값. 일반 PETG와 차이 가능. <a href="https://cdn.shopify.com/s/files/1/1745/6181/files/prusament-petg-v0-technical-data-sheet.pdf" target="_blank" rel="noopener">링크</a></p>
    <p>진동 판정: 1자유도 진동 전달률 1/|1−r²| ≤ 1.33이 되도록 1차 진동을 최대 가진 주파수의 2배 이상으로 설정 (증폭 허용치는 선택값).</p>
  </div>
  <div class="card note">
    <h2>계산과 검증</h2>""")
rep("출력 형상 검증: STL로 만든 최종 형상(클램프 포함)을 1 mm 격자로 다시 해석, 1차 진동 64.0 Hz(설계 계산 66.2 Hz 대비 −3.3%).",
    "출력 형상 검증: STL 최종 형상(클램프 포함)을 1 mm 격자로 다시 해석, 1차 진동 %.1f Hz (설계 계산 100.3 Hz 대비 %+.1f%%)."%(V['f'][0],(V['f'][0]/100.3-1)*100))
rep("가정(확인 필요): 충격 5 g, PETG 물성(E ≈ 2.0 GPa), 클램프는 핸들바에 완전히 고정, 시판 폰 클램프는 강체로 단순화, 판정 기준은 예시값. 실제 출력·장착 시험은 하지 않았습니다.",
    "가정(확인 필요): 노면 진동은 바퀴 축 측정값을 핸들바에 그대로 적용(보수적), 옆 충격은 위아래와 같게, 48.5 g를 정적 하중으로 환산, 클램프는 핸들바에 완전 고정, 시판 폰 클램프는 강체. 실제 출력·주행 시험은 하지 않았습니다.")
rep("팔 무게: 팔 + 받침판. 전체: 클램프(고정 부품, 24.4 g) 포함 출력물 무게. 처짐: 5 g 충격 시 폰 위치. 출력 형상은 클램프까지 포함한 전체를 1 mm 격자로 다시 해석한 값입니다.","팔 무게: 팔 + 받침판. 전체: 클램프 포함 (폭 20 mm 24.4 g, 폭 32 mm 38.7 g). 최대 응력: 48.5 g 충격 시 위아래·옆 중 큰 값. 출력 형상은 클램프까지 포함해 1 mm 격자로 다시 해석한 값입니다.")
rep(".badge{","@media (min-width:901px){.main{grid-template-columns:minmax(0,1.45fr) minmax(0,1fr)}}#cRes table{font-size:11.5px}#cRes th,#cRes td{padding:5px 3px}\n.badge{")
D={k:json.load(open('f3_%s.json'%k)) for k in ['base','r1','r2','r3']}
m=trimesh.load('mesh_w32d_1mm.stl'); mesh=dict(v=base64.b64encode(m.vertices.astype(np.float32).tobytes()).decode(),f=base64.b64encode(m.faces.astype(np.uint32).tobytes()).decode())
im=Image.open('../out/FormProof_자전거거치대_도면_v2.png').convert('RGB'); im=im.resize((1600,int(1600*im.height/im.width)),Image.LANCZOS)
b=io.BytesIO(); im.save(b,'JPEG',quality=82); DRW=base64.b64encode(b.getvalue()).decode()
html=open('css_head.html').read().replace('시나리오 v2','시나리오 v7')+t.replace('__DATA__',json.dumps(dict(D=D,MESH=mesh),separators=(',',':'))).replace('__DRW__',DRW)
open('../out/bike_mount_v7.html','w').write(html); print(len(html))
