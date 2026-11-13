import base64, json, sys
V=json.load(open('opt/final_d.json'))
def img(p): return 'data:image/png;base64,'+base64.b64encode(open(p,'rb').read()).decode()
def jpg(p):
    from PIL import Image; import io
    im=Image.open(p).convert('RGB'); im.thumbnail((1400,1000)); b=io.BytesIO(); im.save(b,'JPEG',quality=80); return 'data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode()
ok=V['f1']>=91.2 and V['vmax']<=26
html=f'''
<div class="sec"><h2>자전거 폰 거치대 · 경로 A (처음 보는 문제)</h2>
<p class="note">모든 숫자는 실제 계산값입니다 (2코어 CPU, 8 GB, GPU 없음). 입력 스케치는 예시이고, 실제 출력·주행 시험은 하지 않았습니다.</p>
<div class="tl">
 <div class="step"><div class="lab"><span class="n">1 · 입력</span><b>요청·자료</b></div><div class="body">
  <p>스케치(핸들바 클램프 + 앞으로 뻗는 팔 + 폰 받침) + “울퉁불퉁한 길에서도 폰이 안 흔들리게, 최대한 가볍게, 3D 프린터로 뽑을 거야”</p></div></div>
 <div class="step"><div class="lab"><span class="n">2 · 3D 설계 생성</span><b>설계 명세 (근거 표시)</b></div><div class="body">
  <div class="kv"><div><span>노면 진동 [1]</span><b>34.6–45.6 Hz · 최대 48.5 g</b></div><div><span>진동 판정</span><b>1차 진동 ≥ 91 Hz</b></div><div><span>강도 판정 [2]</span><b>48.5 g에서 ≤ 26 MPa</b></div><div><span>재료 [2]</span><b>PETG E 1.7 GPa</b></div><div><span>고정 부품</span><b>클램프 링·볼트 귀·받침판</b></div><div><span>폰 + 클램프</span><b>250 g</b></div></div>
  <p class="src">[1] <a href="https://commons.nmu.edu/isbs/vol38/iss1/216/" target="_blank" rel="noopener">ISBS 2020 자갈길 진동 측정</a> · [2] <a href="https://cdn.shopify.com/s/files/1/1745/6181/files/prusament-petg-v0-technical-data-sheet.pdf" target="_blank" rel="noopener">Prusament PETG V0 데이터시트</a> · 91 Hz = 최대 가진 주파수 × 2 (증폭 ≤ 1.33배), 안전율 1.5는 선택값</p>
  <div class="catch">근거 조건을 적용하자 이전에 “충족”이던 설계(61 Hz)가 자갈길 진동을 약 2.3배 키우는 설계로 판정됨</div></div></div>
 <div class="step"><div class="lab"><span class="n">3 · 성능 확인</span><b>처음 설계</b></div><div class="body">
  <div class="imgrow"><img src="{img('thumbs/t0.png')}" alt="처음 설계: 단순 막대형 팔"></div>
  <div class="kv"><div><span>무게 (클램프 포함)</span><b>50.0 g</b></div><div><span>1차 진동</span><b>26.5 Hz</b></div><div><span>충격 응력</span><b>26.4 MPa</b></div><div><span>판정</span><b><span class="pill bad">미충족</span></b></div></div></div></div>
 <div class="step core"><div class="lab"><span class="n">4 · 재설계</span><b>성능 확인 ⇄ 재설계 4회</b></div><div class="body">
  <p>미분 기반 Topology 최적화. 3·4차는 무게 최소화 + 진동 모드 4개 ≥ 91 Hz 제약을 MMA로 풀었습니다 (대칭 절반 약 1.6만 변수, 160회 반복, 약 20분).</p>
  <div class="rounds">
   <div class="rd"><img src="{img('thumbs/t1.png')}" alt="1차"><span class="t">1차 · 같은 단면, 폭 20 mm</span><span class="m">61.0 Hz · 44.7 g</span><span><span class="pill bad">미충족</span></span></div>
   <div class="rd"><img src="{img('thumbs/t2.png')}" alt="2차"><span class="t">2차 · 같은 단면, 폭 32 mm</span><span class="m">100.3 Hz · 75.9 g</span><span><span class="pill good">충족</span> 무거움</span></div>
   <div class="rd"><img src="{img('thumbs/t3.png')}" alt="3차"><span class="t">3차 · 3D 무게 최소화</span><span class="m">설계 91 Hz → 출력 형상 50 Hz</span><span><span class="pill bad">미충족</span> 얇은 부재</span></div>
   <div class="rd"><img src="{img('thumbs/t4.png')}" alt="4차"><span class="t">4차 · 3D 강건 최적화</span><span class="m">{V['f1']:.1f} Hz · {V['mass']:.1f} g</span><span><span class="pill {'good' if ok else 'bad'}">{'충족' if ok else '미충족'}</span></span></div>
  </div>
  <div class="catch">출력 형상 재검증에서 3차 설계의 얇은 부재가 끊겨 성능이 반으로 떨어지는 것을 발견 → 최소 두께 5 mm, 더 얇아진 형상에서도 기준을 만족하도록(강건 최적화) 다시 설계</div>
  <div class="catch">클램프를 설계 대상에 넣자 최적화가 링을 지워 버림 (핸들바에 “붙어 있다”는 가정 때문) → 링 전체를 고정 부품으로 지정</div></div></div>
 <div class="step"><div class="lab"><span class="n">5 · 결과</span><b>출력용 STL + 도면 + 재검증</b></div><div class="body">
  <div class="imgrow"><img src="{img('thumbs/t4.png')}" alt="최종 형상"><img src="{jpg('out/FormProof_자전거거치대_도면_v3.png')}" alt="설계 도면"></div>
  <div class="kv"><div><span>출력물 무게 (클램프 포함)</span><b>{V['mass']:.1f} g</b></div><div><span>1차 진동 (출력 형상)</span><b>{V['f1']:.1f} Hz</b></div><div><span>최대 응력 (48.5 g)</span><b>{V['vmax']:.1f} MPa</b></div><div><span>처음 설계 대비 무게</span><b>50.0 → {V['mass']:.1f} g ({(V['mass']/50.0-1)*100:+.0f}%)</b></div><div><span>처음 설계 대비 1차 진동</span><b>26.5 → {V['f1']:.1f} Hz (×{V['f1']/26.5:.1f})</b></div></div>
  <p class="note">출력 형상 재검증은 STL과 같은 형상을 1 mm 격자로 다시 해석한 값입니다. 3D 자유 형상이라 출력 시 서포트가 필요하며, 출력 방향은 확인이 필요합니다.</p></div></div>
</div></div>'''
t=open('pipe_v5_tpl.html').read().replace('__BIKE__',html)
open('out/formproof_pipeline_v5.html','w').write(t); print(len(t))
