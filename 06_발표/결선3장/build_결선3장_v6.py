import base64
def b64(f):
    return ('data:image/png;base64,' if f.endswith('png') else 'data:image/jpeg;base64,') + base64.b64encode(open(f, 'rb').read()).decode()
I = {k: b64(f) for k, f in dict(l1='v38_L1_b.jpg', l2='v38_L2_b.jpg', l3='v38_L3_b.jpg', fp='fp_b.jpg', sk='v17_sketch.jpg',
     e0='e0.jpg', e20='e20.jpg', e300='e300.jpg', r120='r120.jpg', dw='p6_dwg.jpg', gl='glass_gui.jpg', hero='hero_end.png').items()}
HTML = f'''<title>FormProof 결선 3장</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800;900&display=swap">
<style>
:root{{--bg:#e9edf3;--paper:#fff;--ink:#111c33;--sub:#5a6680;--line:#dde3ec;--navy:#0f1b33;--blue:#2563eb;--orange:#f59e0b;--ok:#0f9d6e;--bad:#d6334a;--soft:#f3f6fb}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#0b111d;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#0b111d;color-scheme:dark}}
body{{background:var(--bg);font-family:"Noto Sans KR",system-ui,sans-serif;color:var(--ink);padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:24px 48px}}
.top{{max-width:1280px;margin:0 auto 14px;color:#8a94a8;font-size:13px;line-height:1.6}}
.slide{{max-width:1280px;margin:0 auto 28px;aspect-ratio:16/9;background:var(--paper);border-radius:10px;box-shadow:0 6px 24px rgba(0,0,0,.18);container-type:inline-size;position:relative;overflow:hidden}}
.in{{position:absolute;inset:0;padding:3cqw 3.4cqw 2.4cqw;display:flex;flex-direction:column;gap:1.4cqw}}
.kick{{font-size:1.1cqw;font-weight:700;color:var(--blue);letter-spacing:.04em}}
h2{{margin:.3cqw 0 0;font-size:2.7cqw;font-weight:900;line-height:1.22;text-wrap:balance}}
h2 em{{font-style:normal;color:var(--bad)}}h2 strong{{color:var(--ok)}}
.lead{{font-size:1.25cqw;color:var(--sub);margin-top:.5cqw}}
.pg{{position:absolute;right:2cqw;bottom:1.3cqw;font-size:1cqw;color:#9aa4b6}}
/* 1 */
.req{{display:flex;align-items:center;gap:1cqw;background:var(--soft);border-radius:.8cqw;padding:.7cqw 1.2cqw;font-size:1.2cqw}}
.req b{{color:var(--blue);white-space:nowrap}}.req q{{font-weight:700}}
.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:1cqw;flex:1;min-height:0}}
.cd{{display:flex;flex-direction:column;border:1px solid var(--line);border-radius:.9cqw;overflow:hidden;min-height:0}}
.cd .im{{flex:1;min-height:0;background:#f7f8fb}}.cd .im img{{width:100%;height:100%;object-fit:contain;display:block}}
.cd .hd{{padding:.6cqw 1cqw;font-weight:800;font-size:1.3cqw;border-bottom:1px solid var(--line)}}
.cd .say{{padding:.6cqw 1cqw;font-size:1.02cqw;color:var(--sub);background:#fafbfd}}.cd .say b{{color:var(--ink)}}
.cd .res{{padding:.8cqw 1cqw;font-weight:900;font-size:1.6cqw;color:#fff;background:var(--bad);display:flex;justify-content:space-between;align-items:baseline}}
.cd .res small{{font-size:1.05cqw;font-weight:700;opacity:.95}}
.cd.fp{{border:.25cqw solid var(--ok)}}.cd.fp .res{{background:var(--ok)}}
.punch{{display:flex;align-items:center;justify-content:space-between;gap:1.4cqw;background:var(--navy);color:#fff;border-radius:.9cqw;padding:1cqw 1.6cqw}}
.punch b{{font-size:1.75cqw;font-weight:800}}.punch span{{font-size:1.15cqw;color:#c9d3e6}}
/* 2 */
.stg{{display:grid;grid-template-columns:1fr auto 1fr auto 1fr auto 1.15fr auto 1fr;gap:.5cqw;align-items:stretch}}
.sg{{border-radius:.6cqw;padding:.55cqw .8cqw;font-size:1.02cqw;background:var(--soft);line-height:1.35}}.sg span{{display:block;font-weight:800;font-size:1.15cqw}}
.sg.a{{border-top:.32cqw solid var(--blue)}}.sg.b{{border-top:.32cqw solid var(--orange)}}.sg.c{{border-top:.32cqw solid var(--ok)}}
.sa{{align-self:center;color:#9aa4b6;font-size:1.3cqw}}
.mods{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,2.3fr) minmax(0,1fr);gap:1cqw;flex:1;min-height:0}}
.md{{border:1px solid var(--line);border-radius:.9cqw;padding:1cqw 1.1cqw;display:flex;flex-direction:column;gap:.6cqw;min-height:0}}
.md.b{{border:.25cqw solid var(--orange);background:#fffaf0}}
.mh{{display:flex;align-items:center;gap:.6cqw}}.mh i{{font-style:normal;display:grid;place-items:center;width:2.3cqw;height:2.3cqw;border-radius:.5cqw;background:var(--blue);color:#fff;font-weight:900;font-size:1.2cqw}}
.md.b .mh i{{background:var(--orange);color:#1b1300}}.md.c .mh i{{background:var(--ok)}}.mh b{{font-size:1.25cqw}}
.big{{font-size:2.1cqw;font-weight:900;line-height:1.15}}.big small{{display:block;font-size:1cqw;font-weight:500;color:var(--sub);margin-top:.25cqw}}
.md img.fill{{width:100%;flex:1;min-height:0;object-fit:contain;border-radius:.4cqw;background:#fff;border:1px solid var(--line)}}
.evo{{display:grid;grid-template-columns:repeat(4,1fr);gap:.4cqw;flex:1;min-height:0}}
.evo figure{{margin:0;position:relative;background:#16223a;border-radius:.4cqw;overflow:hidden;min-height:0}}.evo img{{width:100%;height:100%;object-fit:contain;display:block}}
.evo figcaption{{position:absolute;left:.4cqw;top:.3cqw;font-size:.9cqw;color:#fff;background:rgba(0,0,0,.5);padding:0 .45cqw;border-radius:.3cqw}}
.bn{{display:grid;grid-template-columns:1fr auto 1fr auto 1fr;gap:.5cqw;align-items:center}}
.bn div{{background:#fff;border-radius:.6cqw;padding:.5cqw .7cqw;text-align:center}}.bn div b{{display:block;font-size:1.9cqw;font-weight:900}}.bn div span{{font-size:.95cqw;color:var(--sub)}}
.bn .ar{{color:#9aa4b6;font-size:1.3cqw;background:none;padding:0}}
.demo{{display:flex;align-items:center;justify-content:space-between;background:var(--navy);color:#fff;border-radius:.9cqw;padding:.8cqw 1.5cqw;font-size:1.2cqw}}
.demo i{{font-style:normal;background:var(--orange);color:#1b1300;font-weight:900;border-radius:2cqw;padding:.3cqw 1.2cqw;white-space:nowrap}}
/* 3 */
.g3{{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);gap:1.4cqw;flex:1;min-height:0}}
.case{{border:1px solid var(--line);border-radius:.9cqw;overflow:hidden;display:flex;flex-direction:column;min-height:0}}
.case .hd{{display:flex;justify-content:space-between;align-items:center;padding:.7cqw 1.1cqw;border-bottom:1px solid var(--line)}}
.case .hd b{{font-size:1.3cqw}}.case .hd span{{font-size:.95cqw;color:#fff;background:var(--ok);border-radius:2cqw;padding:.15cqw .8cqw}}
.case img{{flex:1;min-height:0;width:100%;object-fit:contain;background:#f7f8fb}}
.case p{{margin:0;padding:.6cqw 1.1cqw;font-size:1cqw;color:var(--sub)}}
.right{{display:flex;flex-direction:column;gap:.9cqw;min-height:0}}
.steps{{display:flex;flex-direction:column;gap:.6cqw}}
.rs{{display:grid;grid-template-columns:4.6cqw 1fr;gap:.9cqw;align-items:start;background:var(--soft);border-radius:.7cqw;padding:.7cqw 1cqw}}
.rs i{{font-style:normal;font-weight:800;font-size:.98cqw;color:#fff;background:var(--blue);border-radius:2cqw;padding:.25cqw 0;text-align:center}}
.rs.done i{{background:var(--ok)}}.rs b{{font-size:1.2cqw}}.rs p{{margin:.15cqw 0 0;font-size:.98cqw;color:var(--sub);line-height:1.45}}
.vs{{border:1px solid var(--line);border-radius:.8cqw;padding:.8cqw 1cqw}}
.vs b{{font-size:1.1cqw}}.vs table{{width:100%;border-collapse:collapse;margin-top:.4cqw;font-size:1cqw}}
.vs td{{padding:.3cqw .2cqw;border-bottom:1px solid var(--line)}}.vs td:last-child{{text-align:right;font-weight:800}}
.vs tr.fp td{{color:var(--ok)}}
.close{{display:flex;align-items:center;gap:1.6cqw;background:var(--navy);color:#fff;border-radius:.9cqw;padding:.9cqw 1.6cqw}}
.close b{{font-size:2cqw;font-weight:900}}.close span{{font-size:1.15cqw;color:#c9d3e6}}.close i{{margin-left:auto;font-style:normal;background:var(--orange);color:#1b1300;font-weight:900;border-radius:2cqw;padding:.3cqw 1.1cqw;font-size:1.1cqw;white-space:nowrap}}
</style>
<div class="top"><b>FormProof 결선 발표 3장 시안 v6</b> · 5분 = 슬라이드 1 대조 실험 (40초) → 슬라이드 2 핵심 기술 (1분) → 데모 영상 (1분 25초) → 슬라이드 3 삼성 제품 적용 · 계획 + 실물 (1분) · 여유 약 55초<br>바뀐 점: 일반적인 문제 제기 대신 '같은 요청, AI 3번 모두 불합격'을 첫 장에 · 장마다 큰 숫자 하나 · 마지막은 사업부 적용과 실물</div>

<section class="slide"><div class="in">
 <div><div class="kick">대조 실험 · 같은 요청</div>
 <h2>AI에게 거치대 설계를 맡겼더니 — 그럴듯했지만 <em>3번 모두 불합격</em></h2></div>
 <div class="req"><b>요청</b><q>울퉁불퉁한 길에서도 폰이 안 흔들리게, 최대한 가볍게 … 열이 안 갇히게</q> + 손 스케치 (데모와 같은 입력)</div>
 <div class="cards">
  <div class="cd"><div class="hd">LLM 단독 A</div><div class="im"><img src="{I['l1']}" alt="LLM 단독 A 설계"></div><div class="say">AI 자체 판단: <b>통과</b></div><div class="res">불합격<small>폰 온도 22.6 °C</small></div></div>
  <div class="cd"><div class="hd">LLM 단독 B</div><div class="im"><img src="{I['l2']}" alt="LLM 단독 B 설계"></div><div class="say">AI 자체 판단: <b>통과</b></div><div class="res">불합격<small>흔들림 2.95배</small></div></div>
  <div class="cd"><div class="hd">LLM 단독 C</div><div class="im"><img src="{I['l3']}" alt="LLM 단독 C 설계"></div><div class="say">AI 자체 판단: <b>통과</b></div><div class="res">불합격<small>흔들림 6.6배</small></div></div>
  <div class="cd fp"><div class="hd">FormProof</div><div class="im"><img src="{I['fp']}" alt="FormProof 설계"></div><div class="say">계산으로 확인: <b>5개 기준</b></div><div class="res">합격<small>흔들림 1.41배 · 20.9 °C</small></div></div>
 </div>
 <div class="punch"><b>형상은 AI가 그릴 수 있지만, 성능은 계산해야 압니다</b><span>같은 조건 · 같은 해석기(2 mm FEM)로 판정 · 기준 흔들림 ≤ 1.5배, 온도 ≤ 21 °C<br>LLM은 흔들림 1.2~1.3배로 자체 예측 → 실제 최대 6.6배</span></div>
 <div class="pg">1</div>
</div></section>

<section class="slide"><div class="in">
 <div><div class="kick">핵심 기술 · FormProof 파이프라인</div>
 <h2>AI는 빠르게 찾고, <strong>물리 계산이 확인</strong>합니다</h2></div>
 <div class="stg">
  <div class="sg"><span>입력</span>말 · 스케치 · 사진 · 문서 · CAD</div><div class="sa">→</div>
  <div class="sg a"><span>A 설계 사양</span>요구 → 물리 조건</div><div class="sa">→</div>
  <div class="sg b"><span>B 초기 설계 · 해석</span>3D 형상 · 정밀 시뮬레이션</div><div class="sa">→</div>
  <div class="sg b"><span>B 최적 설계</span>AI 탐색 + 정밀 최적화</div><div class="sa">⇄</div>
  <div class="sg c"><span>C 검증 · 출력</span>미달 → 재설계 · 합격만 출력</div>
 </div>
 <div class="mods">
  <div class="md a"><div class="mh"><i>A</i><b>요구를 계산할 수 있게</b></div>
   <div class="big">수치마다 근거<small>“안 흔들리게” → 떨림 주파수 ≥ 95 Hz · 근거 없으면 질문</small></div>
   <img class="fill" src="{I['sk']}" alt="입력 스케치"></div>
  <div class="md b"><div class="mh"><i>B</i><b>하이브리드 최적 설계 — AI 탐색 + 정밀 계산</b></div>
   <div class="evo"><figure><img src="{I['e0']}" alt="초기 설계"><figcaption>초기 설계</figcaption></figure><figure><img src="{I['e20']}" alt="AI 탐색"><figcaption>AI 탐색</figcaption></figure><figure><img src="{I['e300']}" alt="AI 300회"><figcaption>300회</figcaption></figure><figure><img src="{I['r120']}" alt="정밀 최적화"><figcaption>정밀 최적화</figcaption></figure></div>
   <div class="bn"><div><b>300개</b><span>형상 AI × 물리 AI<br>탐색 · 성능 즉시 예측</span></div><span class="ar">→</span><div><b>31개만</b><span>정밀 계산(FEM)<br>전부 계산 대비 약 1/10</span></div><span class="ar">→</span><div><b>120회</b><span>구조 최적화 + FEM<br>3D 프린트 조건</span></div></div></div>
  <div class="md c"><div class="mh"><i>C</i><b>최종 형상을 다시 계산</b></div>
   <div class="big">5 / 5 통과만<small>제작 형상 그대로 FEM 재판정 · 미달이면 목표 조정 후 재설계</small></div>
   <img class="fill" src="{I['dw']}" alt="자동 생성 A3 도면"></div>
 </div>
 <div class="demo"><span>이 과정 그대로 — 자전거 폰 거치대를 실제 GUI로</span><i>▶ 데모 영상 1분 25초</i></div>
 <div class="pg">2</div>
</div></section>

<section class="slide"><div class="in">
 <div><div class="kick">삼성 제품 적용 · 향후 계획</div>
 <h2>같은 흐름으로, 사업부 제품과 특허까지</h2></div>
 <div class="g3">
  <div class="case"><div class="hd"><b>구현 예 · MX AR 글래스</b><span>같은 GUI에서 동작</span></div>
   <img src="{I['gl']}" alt="AR 글래스 설계 화면 — 말 · 스케치 입력, 물리 조건, 초기 설계와 판정">
   <p>“하루 종일 써도 가볍고 안 흘러내리게” → 총무게 · 조이는 힘 · 다리 표면 온도를 근거와 함께 조건으로 → 3D 설계 · 판정</p></div>
  <div class="right">
   <div class="steps">
    <div class="rs done"><i>완료</i><div><b>해커톤 구현</b><p>입력 → 설계 사양 → AI 탐색 · 정밀 최적화 → 검증 → 도면 · STL · 3D 프린트</p></div></div>
    <div class="rs"><i>다음</i><div><b>사내 특허 시스템 연계</b><p>청구항 · 도면 → 3D 재현 → 같은 조건 계산으로 효과 검증 · 회피 설계 비교</p></div></div>
    <div class="rs"><i>확대</i><div><b>사업부 시범</b><p>MX AR 글래스 · 폴더블 → VD TV · DA 가전 (무게 · 방열 · 진동 · 슬림)</p></div></div>
   </div>
   <div class="vs"><b>사람이 직접 해야 하는 단계</b><table>
    <tr><td>해석 도구 (CAE)</td><td>4단계</td></tr><tr><td>3D 생성 AI</td><td>4단계</td></tr><tr><td>생성형 설계 도구</td><td>3단계</td></tr><tr><td>범용 LLM 단독</td><td style="color:var(--bad)">검증 없음</td></tr><tr class="fp"><td>FormProof</td><td>0단계</td></tr></table></div>
  </div>
 </div>
 <div class="close"><b>FormProof — 형상을 성능으로 증명</b><span>머릿속 아이디어를, 성능이 확인된 제품으로</span><i>실물 출력물 제시</i></div>
 <div class="pg">3</div>
</div></section>
'''
open('FormProof_결선3장_시안_v6.html', 'w').write(HTML)
print(len(HTML) // 1024, 'KB')
