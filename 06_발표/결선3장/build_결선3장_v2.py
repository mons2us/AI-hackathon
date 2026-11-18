import base64, os
def b64(f):
    ext = 'png' if f.endswith('png') else 'jpeg'
    return f'data:image/{ext};base64,' + base64.b64encode(open(f, 'rb').read()).decode()
I = {k: b64(f) for k, f in dict(p1='p1_input.jpg', p2='p2_spec.jpg', p3='p3_first.jpg', p4='p4_ai.jpg', p5='p5_ref.jpg', p6='p6_dwg.jpg', cmp='cmp.jpg', hero='hero_end.png', g3='v167_glass_3d.png', gm='v167_glass_maps.png').items()}
HTML = f'''<title>FormProof 결선 3장</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800&display=swap">
<style>
:root{{--bg:#e9edf3;--paper:#ffffff;--ink:#14213d;--sub:#5a6680;--line:#d9dfe8;--navy:#0f1b33;--blue:#2563eb;--orange:#f59e0b;--ok:#0f9d6e;--bad:#d6334a;--soft:#f3f6fb}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#0b111d;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#0b111d;color-scheme:dark}}
body{{background:var(--bg);font-family:"Noto Sans KR",system-ui,sans-serif;color:var(--ink);padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:24px 48px}}
.top{{max-width:1280px;margin:0 auto 14px;color:#8a94a8;font-size:13px}}
.top b{{color:inherit}}
.slide{{max-width:1280px;margin:0 auto 28px;aspect-ratio:16/9;background:var(--paper);border-radius:10px;box-shadow:0 6px 24px rgba(0,0,0,.18);container-type:inline-size;position:relative;overflow:hidden}}
.in{{position:absolute;inset:0;padding:3.2cqw 3.6cqw 2.6cqw;display:flex;flex-direction:column;gap:1.6cqw}}
.kick{{font-size:1.15cqw;font-weight:700;color:var(--blue);letter-spacing:.04em}}
h2{{margin:.3cqw 0 0;font-size:2.55cqw;font-weight:800;line-height:1.25;text-wrap:balance}}
.lead{{font-size:1.3cqw;color:var(--sub);margin:.5cqw 0 0}}
.pg{{position:absolute;right:2.2cqw;bottom:1.5cqw;font-size:1cqw;color:#9aa4b6}}
/* slide 1 */
.prob{{display:grid;grid-template-columns:repeat(4,1fr);gap:1cqw}}
.pc{{background:var(--soft);border-radius:.8cqw;padding:1cqw 1.2cqw;border-left:.35cqw solid var(--bad)}}
.pc b{{display:block;font-size:1.3cqw;margin-bottom:.3cqw}}.pc span{{font-size:1.08cqw;color:var(--sub);line-height:1.45}}
.flow{{display:grid;grid-template-columns:repeat(5,1fr);gap:.9cqw;flex:1;min-height:0}}
.st{{display:flex;flex-direction:column;background:var(--navy);border-radius:.8cqw;overflow:hidden;color:#fff;position:relative}}
.st img{{width:100%;aspect-ratio:4/3;object-fit:cover;object-position:center;display:block}}
.st .tx{{padding:.9cqw 1cqw 1cqw}}
.st .no{{display:inline-grid;place-items:center;width:2cqw;height:2cqw;border-radius:50%;background:var(--blue);font-weight:800;font-size:1.1cqw;margin-right:.5cqw}}
.st b{{font-size:1.35cqw}}.st p{{margin:.5cqw 0 0;font-size:1.02cqw;line-height:1.45;color:#c9d3e6}}.st p em{{font-style:normal;color:#ffd166;font-weight:700}}
.st.core{{outline:.25cqw solid var(--orange)}}
.st.core .badge{{position:absolute;top:.7cqw;left:.7cqw;background:var(--orange);color:#1b1300;font-weight:800;font-size:.95cqw;padding:.2cqw .7cqw;border-radius:2cqw}}
.arrow{{display:none}}
.demo{{display:flex;align-items:center;gap:1cqw;background:#fff7e6;border:1px solid #fde3a7;border-radius:.8cqw;padding:.7cqw 1.2cqw;font-size:1.2cqw}}
.demo i{{font-style:normal;background:var(--orange);color:#1b1300;font-weight:800;border-radius:2cqw;padding:.15cqw .9cqw}}
/* slide 2 */
.g2{{display:grid;grid-template-columns:1.32fr 1fr;gap:1.6cqw;flex:1;min-height:0}}
.cmpw{{display:flex;flex-direction:column;gap:.8cqw;min-height:0}}
.cmpw img{{width:100%;border-radius:.6cqw;display:block;min-height:0;object-fit:cover;flex:1}}
.kp{{display:grid;grid-template-columns:repeat(4,1fr);gap:.7cqw}}
.k{{background:var(--soft);border-radius:.6cqw;padding:.7cqw .9cqw}}
.k small{{display:block;font-size:.95cqw;color:var(--sub)}}.k b{{display:block;font-size:1.75cqw;color:var(--ok);font-weight:800;margin:.1cqw 0}}.k span{{font-size:.95cqw;color:var(--sub)}}
.side{{display:flex;flex-direction:column;gap:1cqw;min-height:0}}
.box{{border:1px solid var(--line);border-radius:.8cqw;padding:1cqw 1.2cqw}}
.box h3{{margin:0 0 .6cqw;font-size:1.3cqw}}
table{{width:100%;border-collapse:collapse;font-size:1.08cqw}}
th{{font-weight:500;color:var(--sub);text-align:center;padding:.35cqw .3cqw;border-bottom:1px solid var(--line);font-size:.98cqw}}
td{{text-align:center;padding:.45cqw .3cqw;border-bottom:1px solid var(--line)}}
td:first-child,th:first-child{{text-align:left}}
.o{{color:var(--ok);font-weight:700}}.x{{color:var(--bad);font-weight:700}}
tr.fp td{{background:#ecfbf4;font-weight:700}}
.note{{font-size:.88cqw;color:#8a94a8;margin-top:.5cqw}}
.print{{flex:1;display:grid;grid-template-columns:1fr 1fr;gap:.8cqw;min-height:0}}
.ph{{border:.2cqw dashed #b9c3d4;border-radius:.8cqw;display:grid;place-items:center;text-align:center;color:#8a94a8;font-size:1.05cqw;padding:.6cqw}}
.ph b{{display:block;color:var(--ink);font-size:1.2cqw}}
.rn{{background:var(--navy);border-radius:.8cqw;overflow:hidden;position:relative}}
.rn img{{width:100%;height:100%;object-fit:cover;display:block}}
.rn span{{position:absolute;left:.7cqw;bottom:.6cqw;font-size:.9cqw;color:#c9d3e6}}
.cap{{font-size:.95cqw;color:var(--sub)}}
/* slide 3 */
.g3{{display:grid;grid-template-columns:minmax(0,1.45fr) minmax(0,1fr);gap:1.8cqw;flex:1;min-height:0}}
.mx th{{font-size:.92cqw;white-space:nowrap}}.mx td{{white-space:nowrap}}.mx td:first-child{{width:24%;white-space:normal}}.mx td{{font-size:1.25cqw;padding:.55cqw .3cqw}}.mx td:first-child{{font-size:1.08cqw}}
.mx td small{{display:block;font-size:.85cqw;color:var(--sub);font-weight:400}}
.au{{color:var(--blue)}}.ex{{color:var(--orange)}}.gs{{color:#a0a9ba}}
tr.fp td .au{{color:var(--ok)}}
.mxb{{display:flex;flex-direction:column}}.mxb table{{flex:1}}.mx td{{height:6.4cqw}}
.lg{{font-size:.92cqw;color:var(--sub);margin-top:.6cqw}}
.road{{display:flex;flex-direction:column;gap:.8cqw}}
.rs{{display:grid;grid-template-columns:5.2cqw 1fr;gap:.9cqw;align-items:start;background:var(--soft);border-radius:.7cqw;padding:.8cqw 1cqw}}
.rs i{{font-style:normal;font-weight:800;font-size:1cqw;color:#fff;background:var(--ok);border-radius:2cqw;padding:.25cqw 0;text-align:center}}
.rs.next i{{background:var(--blue)}}
.rs b{{font-size:1.2cqw}}.rs p{{margin:.2cqw 0 0;font-size:1cqw;color:var(--sub);line-height:1.45}}
.gl{{display:flex;gap:.6cqw;margin-top:.6cqw;background:#fff;border-radius:.5cqw;padding:.4cqw}}.gl img{{height:7.5cqw;object-fit:contain;min-width:0;max-width:50%}}.gn{{font-size:.9cqw!important}}
.tag{{margin-top:auto;display:flex;align-items:center;justify-content:space-between;background:var(--navy);color:#fff;border-radius:.8cqw;padding:1cqw 1.6cqw}}
.tag b{{font-size:1.9cqw;font-weight:800}}.tag span{{font-size:1.15cqw;color:#c9d3e6}}
@media (max-width:640px){{.top{{font-size:12px}}}}
</style>
<div class="top"><b>FormProof 결선 발표 3장 시안 v2</b> · 5분 = 슬라이드 1 (1분) → 데모 영상 (1분 25초) → 슬라이드 2 (1분) → 슬라이드 3 (1분) · 수치 = 데모 영상과 같은 계산(GUI 판정)</div>

<section class="slide"><div class="in">
 <div><div class="kick">FormProof · 물리 기반 생성형 AI</div>
 <h2>말과 스케치로 시작해, 계산으로 성능이 확인된 제품 설계까지</h2></div>
 <div class="prob">
  <div class="pc"><b>① 3D로 옮기기</b><span>CAD를 다룰 줄 알아야 함</span></div>
  <div class="pc"><b>② 성능 확인</b><span>하중 · 고정 · 기준 설정, 해석 의뢰 후 대기</span></div>
  <div class="pc"><b>③ AI에 맡기면</b><span>겉보기엔 맞지만 계산 없이 추정</span></div>
  <div class="pc"><b>④ 결국</b><span>출력하고 고치기만 반복</span></div>
 </div>
 <div class="flow">
  <div class="st"><img src="{I['p1']}" alt="입력 화면"><div class="tx"><span class="no">1</span><b>입력</b><p>문장 한 줄 + 스케치<br>사진 · 문서 · CAD도 가능</p></div></div>
  <div class="st"><img src="{I['p2']}" alt="설계 사양 화면"><div class="tx"><span class="no">2</span><b>설계 사양</b><p>요구 → 물리 조건<br><em>수치마다 근거</em> (근거 DB)</p></div></div>
  <div class="st"><img src="{I['p3']}" alt="초기 설계 화면"><div class="tx"><span class="no">3</span><b>초기 설계 · 판정</b><p>기본형 → 정밀 시뮬레이션(FEM)<br>진동 · 충격 · 열 · 휨</p></div></div>
  <div class="st core"><span class="badge">핵심</span><img src="{I['p4']}" alt="AI 탐색 화면"><div class="tx"><span class="no">4</span><b>AI 탐색 → 정밀 최적화</b><p>형상 AI(DeepSDF) × 물리 AI(FNO) <em>300회</em><br>후보 31개 FEM → 구조 최적화 120회 · 3D 프린트 조건</p></div></div>
  <div class="st"><img src="{I['p6']}" alt="제작 도면"><div class="tx"><span class="no">5</span><b>검증 · 제작 파일</b><p>최종 형상 FEM 재판정<br>A3 도면 · STL 자동 생성</p></div></div>
 </div>
 <div class="demo"><i>▶ 데모</i> 자전거 폰 거치대 — 위 1 → 5 과정을 실제 GUI로 (1분 25초)</div>
 <div class="pg">1</div>
</div></section>

<section class="slide"><div class="in">
 <div><div class="kick">결과 · 같은 조건 정밀 시뮬레이션</div>
 <h2>초기 설계는 5개 기준 중 4개 미달 → FormProof 설계는 모두 충족</h2></div>
 <div class="g2">
  <div class="cmpw">
   <img src="{I['cmp']}" alt="초기 설계와 최적 설계를 같은 색 척도로 비교한 흔들림 · 충격 · 온도 분포">
   <div class="kp">
    <div class="k"><small>최대 흔들림</small><b>−75 %</b><span>5.58 → 1.41배</span></div>
    <div class="k"><small>충격 때 응력</small><b>−79 %</b><span>17.4 → 3.6 MPa</span></div>
    <div class="k"><small>폰 온도 상승</small><b>−11.7 °C</b><span>32.6 → 20.9 °C</span></div>
    <div class="k"><small>무게</small><b>−15.6 %</b><span>94.9 → 80.1 g</span></div>
   </div>
  </div>
  <div class="side">
   <div class="box"><h3>같은 요청, 일반 LLM 단독 설계와 비교</h3>
    <table><tr><th>설계</th><th>흔들림 ≤ 1.5배</th><th>온도 ≤ 21 °C</th><th>판정</th></tr>
     <tr><td>LLM 단독 A</td><td class="o">1.37</td><td class="x">22.6</td><td class="x">불합격</td></tr>
     <tr><td>LLM 단독 B</td><td class="x">2.95</td><td class="o">20.5</td><td class="x">불합격</td></tr>
     <tr><td>LLM 단독 C</td><td class="x">6.6</td><td class="o">20.6</td><td class="x">불합격</td></tr>
     <tr class="fp"><td>FormProof</td><td class="o">1.41</td><td class="o">20.9</td><td class="o">합격</td></tr></table>
    <div class="note">같은 요청 · 같은 조건 · 같은 해석기(2 mm FEM)로 판정. LLM은 도구 없이 독립 세션 3회</div></div>
   <div class="print">
    <div class="ph"><div><b>출력물 사진</b>실물 사진 넣을 자리<br>(발표 때 실물 직접 제시)</div></div>
    <div class="rn"><img src="{I['hero']}" alt="최종 형상 렌더"><span>최종 형상 · 핸들바 장착</span></div>
   </div>
   <div class="cap">출력물은 같은 조건 정밀 최적화로 얻은 같은 계열 구조 · PETG 3D 프린트</div>
  </div>
 </div>
 <div class="pg">2</div>
</div></section>

<section class="slide"><div class="in">
 <div><div class="kick">기술 차별성 · 확장</div>
 <h2>설계 사양부터 제작 파일까지, 사람 손 없이 계산으로 연결</h2></div>
 <div class="g3">
  <div class="box mxb"><table class="mx">
   <tr><th></th><th>설계 사양</th><th>3D 형상</th><th>성능 해석</th><th>최적 설계</th><th>검증 · 제작</th><th>사람 작업</th></tr>
   <tr><td>범용 LLM 단독<small>ChatGPT 등</small></td><td class="gs">추측</td><td class="gs">추측</td><td class="gs">추측</td><td class="gs">추측</td><td class="gs">—</td><td class="x">검증 없음</td></tr>
   <tr><td>3D 생성 AI<small>Meshy 등</small></td><td class="ex">●</td><td class="au">●</td><td class="ex">●</td><td class="ex">●</td><td class="ex">●</td><td class="ex">4단계</td></tr>
   <tr><td>생성형 설계 도구<small>Fusion 360 등</small></td><td class="ex">●</td><td class="ex">●</td><td class="au">●</td><td class="au">●</td><td class="ex">●</td><td class="ex">3단계</td></tr>
   <tr><td>해석 도구 (CAE)<small>Ansys 등</small></td><td class="ex">●</td><td class="ex">●</td><td class="au">●</td><td class="ex">●</td><td class="ex">●</td><td class="ex">4단계</td></tr>
   <tr class="fp"><td>FormProof</td><td class="au">●</td><td class="au">●</td><td class="au">●</td><td class="au">●</td><td class="au">●</td><td class="o">0단계</td></tr>
  </table>
  <div class="lg"><span class="au">●</span> 자동 &nbsp; <span class="ex">●</span> 전문가가 직접 &nbsp; <span class="gs">추측</span> 계산 없이 추정</div></div>
  <div class="road">
   <div class="rs"><i>완료</i><div><b>해커톤 구현</b><p>자전거 폰 거치대: 입력 → 검증된 설계 → 도면 · STL<br>형상 AI · 물리 AI 학습 · 탐색, GUI 한 화면</p></div></div>
   <div class="rs next"><i>다음</i><div><b>사내 특허 시스템 연계</b><p>청구항 · 도면 → 3D 재현 → 같은 조건 계산으로 효과 검증 · 회피 설계 비교</p></div></div>
   <div class="rs next"><i>확대</i><div><b>사업부 제품 시범</b><p>MX AR 글래스 · 폴더블 → VD TV · DA 가전<br>착용 무게 · 방열 · 진동 · 슬림 구조</p>
   <div class="gl"><img src="{I['g3']}" alt="AR 글래스 3D"><img src="{I['gm']}" alt="AR 글래스 물리 분포"></div><p class="gn">구현 예: AR 글래스 — 같은 흐름으로 설계 사양 · 초기 설계 · 판정</p></div></div>
  </div>
 </div>
 <div class="tag"><b>FormProof — 형상을 성능으로 증명</b><span>머릿속 아이디어를, 성능이 확인된 제품으로</span></div>
 <div class="pg">3</div>
</div></section>
'''
open('FormProof_결선3장_시안_v2.html', 'w').write(HTML)
print(len(HTML) // 1024, 'KB')
