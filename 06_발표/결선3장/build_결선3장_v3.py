import base64, os
def b64(f):
    ext = 'png' if f.endswith('png') else 'jpeg'
    return f'data:image/{ext};base64,' + base64.b64encode(open(f, 'rb').read()).decode()
I = {k: b64(f) for k, f in dict(p1='p1_input.jpg', p2='p2_spec.jpg', p3='p3_first.jpg', p4='p4_ai.jpg', p5='p5_ref.jpg', p6='p6_dwg.jpg', cmp='cmp.jpg', hero='hero_end.png', c1='v47_cad.jpg', c2='v48_base.jpg', c3='v44_llm.jpg', l1='v38_L1.jpg', l2='v38_L2.jpg', l3='v38_L3.jpg', fs='fp_s.jpg', g3='v167_glass_3d.png', gm='v167_glass_maps.png').items()}
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
.hook{{font-size:1.35cqw;color:var(--sub);margin-top:.4cqw}}
.pb{{display:grid;grid-template-columns:repeat(4,1fr);gap:1.1cqw;flex:1;min-height:0}}
.pbc{{display:flex;flex-direction:column;border:1px solid var(--line);border-radius:.9cqw;overflow:hidden;background:#fff}}
.pbc .im{{flex:1;min-height:0;background:#f6f8fb;display:grid;place-items:center;overflow:hidden}}
.pbc .im img{{width:100%;height:100%;object-fit:contain}}
.pbc .t{{padding:.9cqw 1.1cqw 1.1cqw;border-top:.35cqw solid var(--bad)}}
.pbc .q{{font-size:1.02cqw;color:var(--sub)}}.pbc b{{display:block;font-size:1.5cqw;margin:.2cqw 0}}.pbc span{{font-size:1.05cqw;color:var(--sub)}}
.loop{{font-size:3.2cqw;font-weight:800;color:#c3cad8;text-align:center;line-height:1}}
.sol{{display:flex;align-items:center;gap:1.4cqw;background:var(--navy);color:#fff;border-radius:.9cqw;padding:1.1cqw 1.6cqw}}
.sol b{{font-size:1.6cqw}}.sol span{{font-size:1.15cqw;color:#c9d3e6}}.sol i{{margin-left:auto;font-style:normal;background:var(--orange);color:#1b1300;font-weight:800;border-radius:2cqw;padding:.3cqw 1.1cqw;font-size:1.2cqw;white-space:nowrap}}
.arch{{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);gap:1.6cqw;flex:1;min-height:0}}
.blocks{{display:flex;flex-direction:column;gap:.9cqw;min-height:0}}
.blocks .blk{{flex:1;align-items:center}}.blk{{display:grid;grid-template-columns:3.4cqw 1fr;gap:1cqw;align-items:start;border:1px solid var(--line);border-radius:.9cqw;padding:1cqw 1.2cqw;background:#fff}}
.blk .l{{display:grid;place-items:center;width:3.4cqw;height:3.4cqw;border-radius:.7cqw;background:var(--blue);color:#fff;font-weight:800;font-size:1.6cqw}}
.blk.core{{border:.22cqw solid var(--orange);background:#fffaf0}}.blk.core .l{{background:var(--orange);color:#1b1300}}
.blk b{{font-size:1.45cqw}}.blk p{{margin:.3cqw 0 0;font-size:1.08cqw;color:var(--sub);line-height:1.5}}
.blk .fl{{display:grid;grid-template-columns:1fr auto 1fr auto 1fr;align-items:stretch;gap:.5cqw;margin-top:.7cqw}}.blk .fl .ar{{align-self:center}}
.blk .fl span{{background:var(--soft);border-radius:.5cqw;padding:.35cqw .7cqw;font-size:1.02cqw}}
.blk .fl span em{{font-style:normal;font-weight:800;color:var(--ink)}}.blk .fl .ar{{background:none;color:#9aa4b6;padding:0}}
.back{{font-size:1cqw;color:var(--sub);padding-left:4.4cqw}}
.proof{{display:flex;flex-direction:column;gap:.9cqw;background:var(--soft);border-radius:.9cqw;padding:1.2cqw 1.3cqw;min-height:0}}
.proof h3{{margin:0;font-size:1.4cqw}}.proof .s{{font-size:1.05cqw;color:var(--sub)}}
.proof table{{background:#fff;border-radius:.6cqw;overflow:hidden}}
.ti{{height:4.2cqw;width:5.6cqw;object-fit:cover;border-radius:.4cqw;vertical-align:middle;margin-right:.7cqw}}.proof td{{padding:.35cqw .3cqw}}.proof table{{flex:1}}
.pr2{{display:grid;grid-template-columns:1fr 1fr;gap:.7cqw}}
.pr2 div{{background:#fff;border-radius:.6cqw;padding:.7cqw .9cqw;font-size:1cqw;color:var(--sub);line-height:1.45}}.pr2 b{{display:block;color:var(--ink);font-size:1.15cqw}}
</style>
<div class="top"><b>FormProof 결선 발표 3장 시안 v3</b> · 5분 = 슬라이드 1 문제 (40초) → 데모 영상 (1분 25초) → 슬라이드 2 핵심 기술 · 신뢰 근거 (1분 15초) → 슬라이드 3 차별성 · 확장 + 실물 (1분) · 결과 수치는 데모 영상이 보여 줌</div>

<section class="slide"><div class="in">
 <div><div class="kick">FormProof · 물리 기반 생성형 AI</div>
 <h2>좋은 아이디어도, 성능을 확인하지 못해 제품이 되지 못합니다</h2>
 <div class="hook">“폰이 떨려서 지도가 안 보여. 안 흔들리는 거치대를 만들어 볼까?”</div></div>
 <div class="pb">
  <div class="pbc"><div class="im"><img src="{I['c1']}" alt="스케치에서 3D로 옮기는 장벽"></div><div class="t"><div class="q">3D로 옮기려니</div><b>CAD를 다룰 줄 모른다</b><span>스케치에서 멈춤</span></div></div>
  <div class="pbc"><div class="im"><img src="{I['c2']}" alt="하중 고정 기준 설정"></div><div class="t"><div class="q">버틸지 확인하려니</div><b>계산 조건부터 막막하다</b><span>해석 의뢰 · 결과 대기</span></div></div>
  <div class="pbc"><div class="im"><img src="{I['c3']}" alt="일반 AI 설계의 흔들림"></div><div class="t"><div class="q">AI에게 맡겨 보니</div><b>겉보기엔 맞는데 틀렸다</b><span>계산 없이 추정</span></div></div>
  <div class="pbc"><div class="im"><div class="loop">출력 ↻ 수정</div></div><div class="t"><div class="q">그냥 만들어 보니</div><b>고치기만 반복한다</b><span>만들어 봐야 앎</span></div></div>
 </div>
 <div class="sol"><b>FormProof</b><span>말 · 스케치만 넣으면 → 계산으로 성능이 확인된 설계와 제작 파일까지</span><i>▶ 데모 1분 25초</i></div>
 <div class="pg">1</div>
</div></section>

<section class="slide"><div class="in">
 <div><div class="kick">핵심 기술 · 왜 믿을 수 있나</div>
 <h2>AI는 빠르게 찾고, 물리 계산이 확인합니다</h2></div>
 <div class="arch">
  <div class="blocks">
   <div class="blk"><div class="l">A</div><div><b>설계 사양 — 요구를 계산 가능한 조건으로</b><p>“안 흔들리게” → 떨림 주파수 ≥ 95 Hz · 수치마다 근거(규격 · 실측 · 데이터시트), 근거가 없으면 질문</p></div></div>
   <div class="blk core"><div class="l">B</div><div><b>하이브리드 최적 설계 — AI 탐색 + 정밀 계산</b>
    <div class="fl"><span>형상 AI(DeepSDF) × 물리 AI(FNO)<br><em>형상 300개</em> 탐색 · 성능 즉시 예측</span><span class="ar">→</span><span>후보만 정밀 계산(FEM)<br><em>31개</em> 확인 → 1개 선택</span><span class="ar">→</span><span>구조 최적화 + FEM<br><em>120회</em> · 3D 프린트 조건</span></div>
    <p>모든 형상을 FEM으로 계산하지 않고, AI가 좁힌 후보만 정밀 계산</p></div></div>
   <div class="blk"><div class="l">C</div><div><b>자동 검증 — 최종 형상을 다시 계산해 합격만 출력</b><p>제작 형상 그대로 FEM 재판정(진동 · 충격 · 열 · 휨) → 미달이면 목표를 조정해 B로 · 합격이면 도면 · STL</p></div></div>
  </div>
  <div class="proof">
   <h3>같은 요청, 계산 없이 설계하면?</h3>
   <div class="s">일반 LLM 단독 3회 vs FormProof — 같은 조건 · 같은 해석기(2 mm FEM)로 판정</div>
   <table><tr><th>설계</th><th>흔들림 ≤ 1.5배</th><th>온도 ≤ 21 °C</th><th>판정</th></tr>
    <tr><td><img class="ti" src="{I['l1']}" alt="LLM 단독 A 설계">LLM 단독 A</td><td class="o">1.37</td><td class="x">22.6</td><td class="x">불합격</td></tr>
    <tr><td><img class="ti" src="{I['l2']}" alt="LLM 단독 B 설계">LLM 단독 B</td><td class="x">2.95</td><td class="o">20.5</td><td class="x">불합격</td></tr>
    <tr><td><img class="ti" src="{I['l3']}" alt="LLM 단독 C 설계">LLM 단독 C</td><td class="x">6.6</td><td class="o">20.6</td><td class="x">불합격</td></tr>
    <tr class="fp"><td><img class="ti" src="{I['fs']}" alt="FormProof 설계">FormProof</td><td class="o">1.41</td><td class="o">20.9</td><td class="o">합격</td></tr></table>
   <div class="pr2"><div><b>LLM은 스스로 “통과”를 예측</b>흔들림 1.2~1.3배로 예측했지만 실제 계산은 최대 6.6배</div><div><b>FormProof는 계산으로 확인</b>최종 형상을 다시 계산해 5개 기준 모두 충족한 것만 출력</div></div>
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
 <div class="tag"><b>FormProof — 형상을 성능으로 증명</b><span>머릿속 아이디어를, 성능이 확인된 제품으로 · 실물 출력물 제시</span></div>
 <div class="pg">3</div>
</div></section>
'''
open('FormProof_결선3장_시안_v3.html', 'w').write(HTML)
print(len(HTML)//1024,'KB')
