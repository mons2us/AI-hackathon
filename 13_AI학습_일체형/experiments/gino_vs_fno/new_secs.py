# 통합 v3 에 새로 넣는 섹션: (1) 기존 ↔ 통합 단계 매칭 (2) 입력 → 출력 어디까지 파라메트릭인가
OLD = [  # (기존 단계, 누가, 통합 모듈, 바뀌는 방식, FormProof 근거, 종류)
 ('요구사양 · 목표', '사람', '0 목표 · 기준 입력', '문장 · 스케치 · 문서에서 조건 자동 추출, 기준은 사람이 확정', '키워드 규칙 → 설계 사양 표 → [확정]', 'auto'),
 ('CAD 설계 (형상 1개)', '설계자', '초기 설계 + 형상 AI', '템플릿 + 치수로 초기 설계 자동, 형상 AI 가 여러 형상을 만듦', '스케치 템플릿 매칭(T 22 + 외형 185) → CadQuery CAD', 'auto'),
 ('STEP 변환 · 형상 정리', '자동 · 사람 점검', 'A 형상 변환', 'STEP · IGES · STL · DXF 를 읽어 격자 · 점 · 거리장으로', 'CAD 파일 입력 → 크기 · 부피 · 구멍 읽기, 해석 격자 생성', 'auto'),
 ('Defeaturing', '사람 판단', 'A 형상 변환 (격자 해상도)', '격자보다 작은 디테일은 자동 생략 · 중요 디테일 판단은 남음', '2 mm 격자 (88×40×37)', 'ai'),
 ('메시', '사람 수작업', 'C 물리 AI 입력 + B 정답 계산 격자', '물리 AI 는 메시 없이 격자 · 점 입력 · 정답 격자도 자동', '팀 엔진: 2 mm 육면체 격자 FEM', 'ai'),
 ('해석 설정', '사람', 'B 데이터 자동 생성', '재질 · 하중 · 경계를 템플릿으로 고정, 형상만 바꿔 일괄 실행', '389 → 734 형상 일괄 계산 (형상당 약 1분)', 'auto'),
 ('솔버 계산 (대기)', '컴퓨터', 'C 물리 AI 즉시 예측 · 솔버는 유지', '탐색 중 평가는 AI(0.05초), 솔버는 학습 데이터 · 최종 판정에', 'FNO 0.05초 · GINO 2.4초 vs FEM 약 1분', 'keep'),
 ('결과 분석 · 다음 안 구상', '사람', 'D 역설계 + 신뢰도', '목표에서 형상을 거꾸로 탐색 + AI 를 믿어도 되는지 판단', '형상 AI 숫자 16개 위 탐색 300회 (신뢰도는 아직 없음)', 'new'),
 ('(없음)', '—', '판정 → 재학습 루프', '탐색 후보 몇 개만 솔버로 판정, 결과를 다시 학습', '능동학습 5회 · 경로 31개 판정 → 정밀 최적화 → 합격', 'new'),
 ('도면 · 시제품', '설계자 · 제작', 'E CAD 재출력 · 제작', 'STEP · STL · 도면 자동. 시제품 측정은 유지', '출력용 몸체 · A3 3면도 · 3D 프린트 출력', 'auto'),
]
KIND = {'auto': ('자동화', 'ai'), 'ai': ('AI 로 대체', 'lat'), 'keep': ('솔버 유지 + AI', 'opt'), 'new': ('새로 추가', 'str')}

def map_svg():
    W, rh, top = 1100, 50, 56
    H = top + rh * len(OLD) + 20
    o = [f'<svg viewBox="0 0 {W} {H}" style="min-width:880px" role="img" aria-label="기존 단계와 통합 프레임워크 모듈 매칭">',
         '<text x="20" y="26" font-size="14" font-weight="700">기존 CAD · CAE 단계</text><text x="20" y="44" font-size="11.5" class="t-m">누가 하는지</text>',
         '<text x="470" y="26" font-size="14" font-weight="700">통합 프레임워크 모듈</text><text x="470" y="44" font-size="11.5" class="t-m">어떻게 바뀌나</text>',
         '<text x="860" y="26" font-size="14" font-weight="700">FormProof 에서 구현</text><text x="860" y="44" font-size="11.5" class="t-m">저장소 근거</text>']
    for i, (old, who, mod, how, ev, k) in enumerate(OLD):
        y = top + i * rh; lab, c = KIND[k]
        ocls = 'r-soft' if old == '(없음)' else ('r-hum' if '사람' in who or '설계자' in who else 'r-old')
        o.append(f'<rect x="20" y="{y}" width="250" height="{rh-10}" rx="7" class="{ocls}"/>')
        o.append(f'<text x="32" y="{y+17}" font-size="12.5" font-weight="700">{old}</text><text x="32" y="{y+33}" font-size="11" class="t-m">{who}</text>')
        o.append(f'<path d="M270,{y+20} C 330,{y+20} 400,{y+20} 462,{y+20}" class="ln-{ "s" if k=="new" else "a"}" style="stroke:var(--{c});stroke-dasharray:{"5 4" if k=="new" else "none"}"/>')
        o.append(f'<rect x="300" y="{y+8}" width="128" height="22" rx="11" class="r-{c}"/><text x="364" y="{y+23}" text-anchor="middle" font-size="11" class="t-{ {"ai":"a","lat":"l","opt":"o","str":"s"}[c] }" font-weight="700">{lab}</text>')
        o.append(f'<rect x="466" y="{y}" width="370" height="{rh-10}" rx="7" class="r-{c}"/>')
        o.append(f'<text x="478" y="{y+17}" font-size="12.5" font-weight="700">{mod}</text><text x="478" y="{y+33}" font-size="10.5" class="t-m">{how}</text>')
        w = ev.split(' '); l1 = ''; 
        while w and len(l1 + w[0]) < 22: l1 += w.pop(0) + ' '
        o.append(f'<text x="860" y="{y+16}" font-size="11">{l1.strip()}</text><text x="860" y="{y+32}" font-size="11" class="t-m">{" ".join(w)}</text>')
    o.append('</svg>'); return '\n'.join(o)

SEC1 = '''<section id="s-map"><h2>1. 기존 단계 ↔ 통합 프레임워크 — 한 줄씩 매칭</h2>
<p class="lead">기존 CAD · CAE 의 각 단계가 통합 프레임워크의 어느 모듈로 가는지, 그리고 FormProof 에서 실제로 무엇으로 구현했는지. 색: <span class="chip c-ok">자동화</span> <span class="chip" style="background:var(--latbg);color:var(--lat)">AI 로 대체</span> <span class="chip c-plan">솔버 유지 + AI</span> <span class="chip c-part">새로 추가</span>. 빨간 칸 = 기존에 사람이 하던 단계.</p>
<div class="box sv">''' + map_svg() + '''</div>
<p class="mut" style="margin-top:6px">BLU(v12) 도 같은 매칭: 해석 설정 → LightTools COM API 일괄 실행(B), STEP → 점군 · 거리장(A), 결과 분석 → 역설계(D). 차이는 정답 솔버가 광선추적이라 메시 대신 재질 · 광원 설정이 핵심이라는 점.</p></section>
'''

SEC2 = '''<section id="s-param"><h2>2. 모든 입력을 받는데, 어디까지 파라메트릭인가</h2>
<p class="lead">FormProof 는 문장 · 스케치 · 사진 · 문서(PPT · PDF · Word) · CAD(STEP · IGES · STL · DXF) 를 입력으로 받음. <b>초기 설계까지는 파라메트릭</b>(템플릿 + 치수 → 코드로 만든 CAD), <b>최적화를 거친 몸체는 자유 형상</b>, 결합부는 다시 파라메트릭으로 붙임. 저장소 코드(10_입력_1차설계 · 03_자전거거치대) 기준.</p>
<div class="box sv"><svg viewBox="0 0 1100 305" style="min-width:880px" role="img" aria-label="입력부터 출력까지 파라메트릭 구간">
<defs><marker id="ahp" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--mut)"/></marker></defs>
<g font-size="12">
<rect x="10" y="40" width="150" height="150" rx="10" class="r-soft"/><text x="85" y="62" text-anchor="middle" font-weight="700">입력</text>
<text x="85" y="86" text-anchor="middle" font-size="11.5">문장</text><text x="85" y="104" text-anchor="middle" font-size="11.5">스케치 · 사진</text><text x="85" y="122" text-anchor="middle" font-size="11.5">문서 PPT · PDF · Word</text><text x="85" y="140" text-anchor="middle" font-size="11.5">CAD STEP · IGES</text><text x="85" y="158" text-anchor="middle" font-size="11.5">STL · DXF</text><text x="85" y="178" text-anchor="middle" font-size="10" class="t-m">CAD 는 크기 · 부피 · 구멍을 읽음</text>
<rect x="190" y="40" width="170" height="150" rx="10" class="r-card"/><text x="275" y="62" text-anchor="middle" font-weight="700">해석 · 매칭</text>
<text x="275" y="88" text-anchor="middle" font-size="11.5">문장 → 키워드 규칙</text><text x="275" y="106" text-anchor="middle" font-size="11.5">스케치 → 템플릿 매칭</text><text x="275" y="124" text-anchor="middle" font-size="11" class="t-m">템플릿 T 22 + 외형 185</text><text x="275" y="146" text-anchor="middle" font-size="11.5">→ 설계 사양 (spec.json)</text><text x="275" y="168" text-anchor="middle" font-size="11" class="t-m">치수 · 기준 · 조건</text>
<rect x="390" y="40" width="170" height="150" rx="10" class="r-ai"/><text x="475" y="62" text-anchor="middle" font-weight="700">초기 설계</text>
<text x="475" y="86" text-anchor="middle" font-size="11.5" class="t-a">파라메트릭</text><text x="475" y="108" text-anchor="middle" font-size="11">치수 → CadQuery 코드</text><text x="475" y="126" text-anchor="middle" font-size="11">→ STEP · DXF · PDF · STL</text><text x="475" y="148" text-anchor="middle" font-size="11" class="t-m">치수 바꾸면 다시 생성</text><text x="475" y="166" text-anchor="middle" font-size="11" class="t-m">해석 격자도 같은 치수에서</text>
<rect x="590" y="40" width="170" height="150" rx="10" class="r-hum"/><text x="675" y="62" text-anchor="middle" font-weight="700">최적화</text>
<text x="675" y="86" text-anchor="middle" font-size="11.5" class="t-h">자유 형상</text><text x="675" y="108" text-anchor="middle" font-size="11">2 mm 격자 0/1</text><text x="675" y="126" text-anchor="middle" font-size="11">형상 AI 탐색 → 정밀 최적화</text><text x="675" y="148" text-anchor="middle" font-size="11" class="t-m">치수 · 특징 개념 없음</text><text x="675" y="166" text-anchor="middle" font-size="11" class="t-m">이 구간이 자유도의 원천</text>
<rect x="790" y="40" width="300" height="150" rx="10" class="r-str"/><text x="940" y="62" text-anchor="middle" font-weight="700">출력용 몸체 · 도면</text>
<text x="940" y="86" text-anchor="middle" font-size="11.5" class="t-s">자유 형상 몸체 + 파라메트릭 기능부</text><text x="940" y="108" text-anchor="middle" font-size="11">격자 → 매끈한 표면 (몸체)</text><text x="940" y="126" text-anchor="middle" font-size="11">+ 하우징 · 걸이 · 구멍 · 슬롯 (CadQuery)</text><text x="940" y="148" text-anchor="middle" font-size="11">→ STL · A3 3면도 · 3D 프린트</text><text x="940" y="168" text-anchor="middle" font-size="11" class="t-m">몸체 모양은 숫자로 못 고침</text>
</g>
<path d="M160,115 L188,115" class="ln" marker-end="url(#ahp)"/><path d="M360,115 L388,115" class="ln" marker-end="url(#ahp)"/><path d="M560,115 L588,115" class="ln" marker-end="url(#ahp)"/><path d="M760,115 L788,115" class="ln" marker-end="url(#ahp)"/>
<rect x="390" y="214" width="170" height="10" rx="5" style="fill:var(--ai)"/><rect x="590" y="214" width="170" height="10" rx="5" style="fill:var(--hum)"/><rect x="790" y="214" width="140" height="10" rx="5" style="fill:var(--hum)"/><rect x="930" y="214" width="160" height="10" rx="5" style="fill:var(--ai)"/>
<text x="475" y="244" text-anchor="middle" font-size="11.5" class="t-a">파라메트릭</text><text x="675" y="244" text-anchor="middle" font-size="11.5" class="t-h">자유 형상 (비파라메트릭)</text><text x="860" y="244" text-anchor="middle" font-size="11.5" class="t-h">몸체</text><text x="1010" y="244" text-anchor="middle" font-size="11.5" class="t-a">기능부</text>
<text x="10" y="270" font-size="11.5" class="t-m">주의 ① 올린 CAD 파일은 크기 · 부피 · 구멍을 읽어 조건 · 미리보기로 쓰고, 파라메트릭 모델로 바꾸지는 않음.</text><text x="10" y="290" font-size="11.5" class="t-m">② STEP 은 이력 없는 형식이라, 코드로 만든 초기 설계도 STEP 파일 안에는 치수 이력이 남지 않음 (코드 · spec.json 에 남음).</text>
</svg></div>
<div class="grid3" style="margin-top:12px">
<div class="card"><div class="k">답</div><h3>"파라메트릭이 아니야?" → 절반은 맞음</h3><p class="mut">입력 → 초기 설계 구간은 파라메트릭. 성능을 위해 형상을 자유롭게 바꾸는 최적화 구간에서 파라메트릭이 끊김.</p></div>
<div class="card"><div class="k">왜 끊나</div><h3>자유도와 맞바꿈</h3><p class="mut">치수 몇 개만 바꾸면 템플릿이 허용하는 모양 안에서만 움직임. FormProof 합격 형상은 템플릿에 없던 모양 — 자유 형상 구간 덕분.</p></div>
<div class="card"><div class="k">지금 해법</div><h3>몸체는 자유, 기능부는 파라메트릭</h3><p class="mut">체결 · 하우징처럼 치수가 중요한 곳만 CadQuery 로 다시 붙임 — 섹션 10 의 되돌리는 길 중 e. 몸체까지 파라메트릭으로 되돌리는 건 미해결.</p></div>
</div></section>
'''
