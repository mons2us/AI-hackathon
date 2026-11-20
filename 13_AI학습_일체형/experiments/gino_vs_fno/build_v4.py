import re, json, sys
sys.path.insert(0,'.'); import importlib, new_secs; importlib.reload(new_secs); from new_secs import SEC1, SEC2
F=open('fw2_template.html').read()
A=open('arch_review_v3.html').read()
astyle=re.search(r'<style>(.*?)</style>',A,re.S).group(1)
def vars_of(block): return dict(re.findall(r'(--[\w-]+):([^;]+);',block))
roots=re.findall(r':root\{([^}]*)\}',astyle)
light=vars_of(roots[0]); dark=vars_of(re.search(r':root:not\(\[data-theme="light"\]\)\{([^}]*)\}',astyle).group(1))
ren={'--lat':'--latf'}
fx=lambda d:{ren.get(k,k):v for k,v in d.items()}
light,dark=fx(light),fx(dark)
fv=vars_of(re.search(r':root\{([^}]*)\}',F).group(1))
add_l=''.join(f'{k}:{v};' for k,v in light.items() if k not in fv)
add_d=''.join(f'{k}:{v};' for k,v in dark.items() if k not in fv)
rules=re.sub(r':root\{[^}]*\}','',astyle); rules=re.sub(r'@media \(prefers-color-scheme: dark\)\{:root:not\(\[data-theme="light"\]\)\{[^}]*\}\}','',rules); rules=re.sub(r':root\[data-theme="dark"\]\{[^}]*\}','',rules)
drop=['body{','main{','h1{','p{','.mut{','.key{','.tw{','a{','.lb{','.lb img{','.lb[hidden]']
rules='\n'.join(l for l in rules.split('\n') if l.strip() and not any(l.strip().startswith(d) for d in drop))
rules=rules.replace('th,td{padding:6px 8px','#mx th,#mx td{padding:6px 8px').replace('thead th{font-size:11.5px','#mx thead th{font-size:11.5px').replace('td.d{','#mx td.d{').replace('td.c{','#mx td.c{')
rules=rules.replace('.chip{','.fchip{').replace('var(--lat)','var(--latf)')
rules=re.sub(r'ul\{[^}]*\} li\{[^}]*\}','',rules)
a0=A.index('<section><h2>A. 우리 프레임워크와 들어갈 자리</h2>'); a1=A.index('<section><h2>출처</h2>')
body=A[a0:a1]
body=body.replace('<h2>A. 우리 프레임워크와 들어갈 자리</h2>','<h2>9-1. 8단계로 본 프레임워크 — 단계마다 들어갈 방법</h2><p class="lead">위 모듈(0 · A~E · 신뢰도 · 루프)을 실행 순서 8단계로 펼친 것. 단계를 누르면 방법 · 상태 · 실제 그림. ① 목표 · ② 형상(A + 형상 AI) · ③ 물리 AI 구조 · ④ 학습 방식(③④ = C) · ⑤ 신뢰도 · ⑥ 역설계(D) · ⑦ 솔버 판정 · ⑧ 재학습 · 마무리.</p>')
body=body.replace('<h2>B. 단계 × 방법</h2>','<h2>9-2. 단계 × 방법</h2>').replace('<h2>C. 우리 형상 · 시뮬레이션 실제 모습</h2>','<h2>9-3. 우리 형상 · 시뮬레이션 실제 모습</h2>').replace('<h2>D. 아키텍처별 구조 + 우리 형상에서 보면</h2>','<h2>9-4. 아키텍처 14개 — 구조 그림 + 우리 형상에서 보면</h2>')
body=body.replace('class="chip"','class="fchip"').replace('var(--lat)','var(--latf)')
js='\n'.join(re.findall(r'<script>(.*?)</script>',A,re.S))
js=js.replace('`<span class="chip">','`<span class="fchip">').replace('class="chip"','class="fchip"')
js=js.replace("{id:'ah',","{id:'fah',").replace("'url(#ah)'","'url(#fah)'").replace("{id:'ahw',","{id:'fahw',").replace("'url(#ahw)'","'url(#fahw)'")
js='\n'.join(l for l in js.split('\n') if not l.startswith("const LB=")).replace('var(--lat)','var(--latf)')
F=F.replace('<title>CAD·CAE 물리 AI 통합 프레임워크</title>','<title>물리 AI 설계 프레임워크</title>')
F=F.replace('<h1>CAD·CAE 와 물리 AI 통합 프레임워크 v2 — 모든 제품에 같은 틀</h1>','<h1>물리 AI 설계 프레임워크 v3 — 기존 CAD · CAE 매칭 · 모든 제품 · 아키텍처 지도 통합</h1>')
F=F.replace('· v2 · 2026-11-20 · v1 은 별도 링크로 유지 ·','· v3 · 2026-11-20 · 통합 프레임워크 v2 + 아키텍처 지도 v3 를 한 페이지로, 이전 판은 별도 링크로 유지 ·')
F=F.replace('FormProof 형상 실험을 하나로','FormProof 형상 실험 · 아키텍처 조사를 하나로')
F=F.replace("--sans:'Noto Sans KR'",add_l+"--sans:'Noto Sans KR'",1)
F=F.replace('@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){','@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){'+add_d,1)
F=F.replace(':root[data-theme="dark"]{',':root[data-theme="dark"]{'+add_d,1)
F=F.replace('</style>',rules+'\n#mx th:first-child,#mx td:first-child{text-align:left} .gal figure img{max-height:460px;object-fit:contain}\n.toc{display:flex;flex-wrap:wrap;gap:6px;font-size:12.5px} .toc a{border:1px solid var(--line);background:var(--card);border-radius:20px;padding:3px 11px;text-decoration:none;color:var(--fg)} .toc a:hover{border-color:var(--ai)}\n</style>',1)
toc='<nav class="toc" aria-label="목차"><a href="#s-map">1 기존 ↔ 통합 매칭</a><a href="#s-param">2 입력 · 파라메트릭</a><a href="#s-gen">3 모든 제품</a><a href="#s-two">4 두 사례</a><a href="#s-shape">5 형상 자유도</a><a href="#s-less">6 교훈</a><a href="#s-in">7 물리 AI 안쪽</a><a href="#s-flow">8 흐름 비교</a><a href="#s-arch">9 아키텍처 지도</a><a href="#s-cad">10 CAD 재출력</a><a href="#s-now">11 지금 위치</a></nav>'
F=F.replace('</header>','</header>\n'+toc,1)
i=F.index('<section><h2>1. 기존 방식 vs 물리 AI 방식'); j=F.index('</section>',i)+10; flow=F[i:j]; F=F[:i]+F[j:]
flow=flow.replace('<section><h2>1. 기존 방식 vs 물리 AI 방식 — 같은 설계 반복을 비교</h2>','<section id="s-flow"><h2>8. 흐름으로 보면 — 기존 루프 vs 통합 루프</h2>')
for a,b in [('<section><h2>2. 모든 제품에 같은 틀','<section id="s-gen"><h2>3. 모든 제품에 같은 틀'),('<section><h2>3. 두 사례 상세','<section id="s-two"><h2>4. 두 사례 상세'),('<section><h2>4. 형상이 더해지면','<section id="s-shape"><h2>5. 형상이 더해지면'),('<section><h2>5. FormProof 에서 확인된 것','<section id="s-less"><h2>6. FormProof 에서 확인된 것'),('<section><h2>6. 물리 AI 계층 안쪽','<section id="s-in"><h2>7. 물리 AI 계층 안쪽'),('<section><h2>7. E CAD 재출력','<section id="s-cad"><h2>10. E CAD 재출력'),('<section><h2>8. 정리 — 모듈별 지금 위치</h2>','<section id="s-now"><h2>11. 정리 — 모듈별 지금 위치</h2>')]:
    assert a in F,a; F=F.replace(a,b)
k=F.index('<section id="s-gen">'); F=F[:k]+SEC1+SEC2+F[k:]
k=F.index('<section id="s-cad">'); F=F[:k]+flow+'\n<div id="s-arch"></div>\n'+body+F[k:]
R=[('<text x="700" y="60" font-size="13" font-weight="700">되돌리는 길 4가지</text>','<text x="700" y="60" font-size="13" font-weight="700">되돌리는 길 5가지 (e = FormProof 지금 방식)</text>'),
('<svg viewBox="0 0 1100 300" style="min-width:860px" role="img" aria-label="파라메트릭 CAD 와 AI 출력 형상 비교">','<svg viewBox="0 0 1100 340" style="min-width:860px" role="img" aria-label="파라메트릭 CAD 와 AI 출력 형상 비교">'),
('<text x="700" y="266" font-weight="700" class="t-a">현실적 조합: 넓은 탐색은 자유 형상(AI)</text><text x="700" y="284" font-weight="700" class="t-a">→ 고른 안을 a 또는 b 로 CAD 화 → 정밀 마무리</text>','<text x="700" y="264"><tspan font-weight="700">e. 자유 형상 몸체 + 파라메트릭 기능부</tspan></text><text x="700" y="280" class="t-m">몸체는 매끈한 표면, 체결 · 하우징 · 구멍은 CadQuery 로 다시 결합</text><text x="700" y="310" font-weight="700" class="t-a">현실적 조합: 넓은 탐색은 자유 형상(AI) → 고른 안을</text><text x="700" y="328" font-weight="700" class="t-a">a · b · e 로 CAD 화 → 정밀 마무리</text>'),
('FormProof 는 b 에 가까운 단계(출력용 몸체 변환 · 도면)까지 했고 특징 트리는 없음.','FormProof 는 e(자유 형상 몸체 + 파라메트릭 기능부 · 도면)까지 했고, 몸체의 특징 트리는 없음.'),
('<li>관련 페이지: 통합 프레임워크 v1 ·','<li>저장소 코드 — 10_입력_1차설계 README · formproof_input(file_input · cad · sketch), 03_자전거거치대/일체형_제작형_v1/코드/build_body.py, 13_AI학습_일체형/engine/opt_int.py (2 mm 격자)</li><li>아키텍처 출처: PhysicsNeMo 문서 · PINO · GINO · PI-GANO · Transolver · GeoTransolver · UPT · 레일리 몫 논문 (아키텍처 지도 v3 출처와 같음)</li><li>관련 페이지: 통합 프레임워크 v1 · v2 · 아키텍처 지도 v1~v3 ·')]
for a,b in R: assert a in F,a[:50]; F=F.replace(a,b)
F=F.replace('</script>','</script>\n<script>'+js+'</script>',1)
U=json.load(open('imgs_fw.json'))
for kk,v in U.items(): F=F.replace('@@'+kk,v)
assert '@@' not in F
from nv_sec import NV
F=F.replace('<h1>물리 AI 설계 프레임워크 v3 —','<h1>물리 AI 설계 프레임워크 v4 —').replace('아키텍처 지도 통합</h1>','아키텍처 지도 · NVIDIA 비교</h1>')
F=F.replace('· v3 · 2026-11-20 ·','· v4 · 2026-11-20 · v3 + NVIDIA PhysicsNeMo 비교(12번) ·')
F=F.replace('<a href="#s-now">11 지금 위치</a></nav>','<a href="#s-now">11 지금 위치</a><a href="#s-nv">12 NVIDIA 비교 · 방향</a></nav>')
k=F.index('<section><h2>확인 필요</h2>'); F=F[:k]+NV+F[k:]
F=F.replace('<li>지금 끝까지 한 번 돌린 제품은 FormProof 하나','<li><b>NVIDIA PhysicsNeMo 와 비교하면(12번)</b>: 모델 · 불확실성 · 가드레일 · 능동학습 · 메시 처리는 PhysicsNeMo 가 이미 라이브러리로 가짐 — 우리가 비어 있는 "신뢰도"를 바로 채울 수 있음. 형상 역설계 · 하이브리드 경로 · CAD 재출력 · 다제품 어댑터는 NVIDIA 자료에 없는 우리 몫.</li><li>지금 끝까지 한 번 돌린 제품은 FormProof 하나',1)
F=F.replace('<li>E CAD 재출력에서 a~d 중 어떤 길을 공통 뼈대로 둘지</li>','<li>E CAD 재출력에서 a~e 중 어떤 길을 공통 뼈대로 둘지</li><li>NVIDIA 세션 영상에만 있는 내용(슬라이드 · 데모 세부) — 이 페이지는 공개 요약 · 문서 기준</li><li>FP-DDM PhysicsNeMo 예제 위치, PhysicsNeMo 스킬 배포 경로</li>')
open('physics_ai_framework_v4.html','w').write(F); print(len(F)//1024,'KB')
