import os,re
b=open('build_v10.js').read()
R=[("[`−${pct((1-BK.ai_m/BK.beam_m)*100)}%`, '단순 보 대비 무게', `${BK.beam_m} → ${BK.ai_m} g`]","['3 / 3', 'LLM 단독 설계', '근거 기준 미달 — FormProof만 통과']"),
("단순 보 = 직사각형 보로 같은 기준을 맞춘 경우(계산)","LLM 단독 = 도구 없는 독립 세션 3회, 같은 해석기로 판정"),
("무게 비교는 기준을 통과하는 단순 보강안 대비(처음 설계는 기준 미달이라 무게 비교 대상이 아님).","3/3은 범용 LLM 단독 설계 3건이 근거 기준(91 Hz)에 모두 미달했다는 뜻."),
("단순 직사각형 보로 같은 기준 충족 시 약 ${BK.beam_m} g. 빨간 점선 = 판정 기준","출력: 옆으로 눕혀 받침대 없이(45° 규칙, 격자 기준). 빨간 점선 = 판정 기준"),
("bike_v10.json","bike_v11.json"),("{ kind: '신경 연산자 (GINO 계열)' }","{ kind: '3D 합성곱 신경망' }"),("'형상(SDF) → 응력 · 진동 · 온도를 수 초에 예측'","'형상 → 진동 · 응력을 0.2초에 예측'"),("'DeepSDF 계열 생성 모델'","'DeepSDF 방식 생성 모델'"),("'형상 AI 변수를 물리 AI 미분으로 조정 → 수 초 후보'","'형상 AI 변수를 물리 AI 미분으로 조정 → 약 40초 후보'"),("fit(s, SH + 'v7_drw_front.png', px + 0.1, py + 0.45, PW - 0.2, 0.95, 'drawing');","fit(s, SH + BK.rider, px + 0.1, py + 0.45, PW - 0.2, 0.95, 'mount');"),("T(s, `STL ${BK.ai_m} g · 도면 · 근거 리포트`","T(s, `출력용 STL ${BK.ai_m} g · 근거 리포트`"),("발표 초안 v10","발표 초안 v11"),
("s.addText('2. 기술 차별성 — 누구나 쓰면서도, 결과를 믿을 수 있다'","s.addText('1. 기존 방식의 한계 — 쉬움과 신뢰 중 하나만 준다'"),
("s.addText('2. 파이프라인 적용 — 자전거 거치대 (경로 A) 6단계'","s.addText('2. 실증 ① 자전거 거치대 — 말 한 줄에서 제작 파일까지'"),
("s.addText('2. 실증 사례 ① — 기준 미달 설계를 기준 통과 설계로'","s.addText('2. 실증 ① 자전거 거치대 — 기준 미달에서 통과로, 받침대 없이 출력'"),
("s.addText('2. 실증 사례 ② — TV 스탠드: 외형은 그대로, 무게는 1/3'","s.addText('2. 실증 ② TV 스탠드 — 외형은 그대로, 무게는 1/3'"),
("s.addText('2. 실증 사례 ③ — 무선충전 스탠드: 같은 흐름에 열 방정식 추가'","s.addText('4. 확장 근거 — 열 물리: 무선충전 스탠드 방열판'"),
]
for a,c in R:
    assert a in b,a; b=b.replace(a,c)
M=lambda t: b.index(t)
keys=['// ---------- 1. 표지','// ---------- 2. 한 장 요약','// ---------- 3. 문제 정의','// ---------- 4. 기술 차별성: 파이프라인','// ---------- 2b. 입력','// ===== v7: 파이프라인 상세','// ===== v7: 검증 관문이 걸러낸 사례','// ---------- 5. 기술 차별성: 비교','// ---------- 5b. 실증 사례 소개','// ---------- 6. 실증 결과','// ---------- 6b. TV','// ---------- 6c. 무선충전','// ---------- 7. 사업','// ---------- 8. 확장성','// ---------- 9. 마무리']
pos=[M(k) for k in keys]; assert pos==sorted(pos)
head=b[:pos[0]]; tail_end=b.index('await pres.writeFile')
blk={}
for i,k in enumerate(keys):
    e=pos[i+1] if i+1<len(pos) else tail_end; blk[k]=b[pos[i]:e]
blk[keys[7]]=blk[keys[7]].replace("sectionTitle: '2. 기술 차별성'","sectionTitle: '1. 문제 정의'")
blk[keys[11]]=blk[keys[11]].replace("sectionTitle: '2. 기술 차별성'","sectionTitle: '4. 확장성·파급 효과'")
phys=open('v11_phys.js').read() if os.path.exists('v11_phys.js') else ''
llm=open('v11_llm.js').read()
order=[keys[0],keys[1],keys[2],keys[7],keys[3],keys[4],'PHYS',keys[6],keys[5],keys[9],keys[10],'LLM',keys[12],keys[13],keys[11],keys[14]]
out=head+''.join(phys if k=='PHYS' else llm if k=='LLM' else blk[k] for k in order)+b[tail_end:]
open('build_v11.js','w').write(out); print('ok', 'phys' if phys else 'no phys')
