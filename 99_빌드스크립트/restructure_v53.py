import re
L=open('build_v52.js').read().split('\n')
def blk(a,b): return '\n'.join(L[a-1:b])
head=blk(1,61); tail=blk(742,745)
B={1:blk(62,73),2:blk(74,128),3:blk(129,220),4:blk(221,244),5:blk(245,319),6:blk(320,350),7:blk(351,383),8:blk(384,406),
   9:blk(407,432),10:blk(433,474),11:blk(475,501),12:blk(502,527),13:blk(528,548),14:blk(549,561),15:blk(562,584),16:blk(585,605),
   17:blk(606,630),18:blk(631,659),19:blk(660,692),20:blk(693,710),21:blk(711,718),22:blk(719,741)}
for k in B: B[k]=re.sub(r"pres\.addSection\(\{ title: '[^']*' \}\);\n?","",B[k])
def sec(k,name): B[k]=re.sub(r"sectionTitle: '[^']*'","sectionTitle: '%s'"%name,B[k])
def rep(k,a,b,n=1):
    c=B[k].count(a); assert c>=1, (k,a[:60]); B[k]=B[k].replace(a,b)
# ---- 섹션
for k in (10,15,14,17): sec(k,'3. 실증')
for k in (18,19): sec(k,'4. DX 기여 · 확장')
for k in (22,6,9,11,12,13,16,20): sec(k,'부록')
# ---- 제목
rep(10,"'2. 실증 ① 자전거 거치대 — 말 한 줄에서 제작 파일까지'","'3. 실증 — 자전거 거치대: 말 한 줄에서 제작 파일까지'")
rep(15,"'2. 실증 ① 물리로 본 차이 — 같은 조건에서 계산한 분포'","'3. 실증 — 물리로 본 차이: 같은 조건에서 계산한 분포'")
rep(17,"'2. 범용 LLM 단독 vs FormProof — 같은 요청, 같은 검증'","'3. 실증 — 범용 LLM 단독 vs FormProof: 같은 요청, 같은 검증'")
rep(6,"'2. 입력 → 설계 명세 — ","'부록. 입력 → 설계 명세 — ")
rep(9,"'2. 실증 ① 자전거 거치대 — 요청 한 줄을 물리 조건으로'","'부록. 자전거 거치대 — 요청 한 줄을 물리 조건으로'")
rep(11,"'2. 실증 ① 자전거 거치대 — 형상은 계산이 만든다'","'부록. 자전거 거치대 — 형상은 계산이 만든다 (최적화 과정)'")
rep(12,"'2. 실증 ① 일체형 — ","'부록. 자전거 거치대 — ")
rep(13,"'2. 실증 ① 일체형 결과 — 비슷한 무게로 흔들림 77%↓'","'부록. 자전거 거치대 결과 — 비슷한 무게로 흔들림 77%↓'")
rep(16,"'2. 실증 ① 제작 구성 — ","'부록. 자전거 거치대 제작 구성 — ")
rep(20,"'4. 확장 근거 — ","'부록. 확장 근거 — ")
# ---- 쪽 번호 (새 번호: 9 분포, 11 LLM, 15 TV, 20 결과 막대)
rep(2,"'분포 상세 → 15쪽'","'분포 상세 → 9쪽'")
rep(3,"(17쪽)","(11쪽)")
rep(4,"(17쪽)","(11쪽)")
rep(17,"재해석 통과(13쪽)","재해석 통과(20쪽)")
# ---- 8: 검증 사례에 폰 고정 누락 추가 (4건)
rep(8,"'이번 사례 작업 중 실제로 불합격 · 오류로 판정되어 다시 설계한 결과 3건'","'이번 작업 중 실제로 불합격 · 오류로 판정되어 다시 설계한 결과 4건 — 그럴듯해 보여도 계산이 통과시키지 않았다'")
rep(8,"['무선충전 방열판', '내부 방열 구조 최적화 v1', '중간 밀도(회색) 형상\\n→ 실제 제작 불가 판정', '실제 제품 구조 기준 재정의\\n→ 알루미늄 판금 2장 형상']];",
 "['무선충전 방열판', '내부 방열 구조 최적화 v1', '중간 밀도(회색) 형상\\n→ 실제 제작 불가 판정', '실제 제품 구조 기준 재정의\\n→ 알루미늄 판금 2장 형상'],\n  ['자전거 거치대 일체형', '1차 일체형 결과 (검토에서 발견)', '폰을 잡는 형상 없음\\n→ 충격 시 빠지는 힘 79 N > 버티는 힘 11 N', '4면 고정(걸이 · 집게 · 잠금)\\n→ 재최적화 · 출력 몸체 재검증 통과']];")
B[8]=B[8].replace("const x = 0.5 + i * 3.05;\n  box(s, x, 1.3, 2.85, 3.0, X.tint, 'fail card');","const x = 0.5 + i * 2.27;\n  box(s, x, 1.3, 2.15, 3.0, X.tint, 'fail card');")
B[8]=B[8].replace("T(s, f[0], { x: x + 0.15, y: 1.4, w: 2.55, h: 0.32, fontSize: 13,","T(s, f[0], { x: x + 0.12, y: 1.4, w: 1.95, h: 0.32, fontSize: 11,")
B[8]=B[8].replace("T(s, f[1], { x: x + 0.15, y: 1.72, w: 2.55, h: 0.28, fontSize: 9.5,","T(s, f[1], { x: x + 0.12, y: 1.72, w: 1.95, h: 0.28, fontSize: 8,")
B[8]=B[8].replace("T(s, '검증 불합격', { x: x + 0.5, y: 2.17, w: 2.2,","T(s, i === 3 ? '검토 발견 → 계산 확인' : '검증 불합격', { x: x + 0.48, y: 2.17, w: 1.65,")
B[8]=B[8].replace("fontSize: 12, bold: true, color: C.accent5, valign: 'middle' });","fontSize: 10, bold: true, color: C.accent5, valign: 'middle' });")
B[8]=B[8].replace("T(s, f[2], { x: x + 0.15, y: 2.55, w: 2.6, h: 0.65, fontSize: 9.5,","T(s, f[2], { x: x + 0.12, y: 2.55, w: 1.95, h: 0.65, fontSize: 8,")
B[8]=B[8].replace("{ x: x + 1.27, y: 3.25,","{ x: x + 0.93, y: 3.25,")
B[8]=B[8].replace("T(s, f[3], { x: x + 0.47, y: 3.57, w: 2.3, h: 0.7, fontSize: 9.5,","T(s, f[3], { x: x + 0.44, y: 3.57, w: 1.66, h: 0.7, fontSize: 8,")
rep(8,"'검증 관문이 없었다면 세 결과 모두 그대로 제작 파일이 됐을 것","'검증이 없었다면 네 결과 모두 그대로 제작 파일이 됐을 것")
# ---- 14 + 16: 구조 · 조립도 · 부품
rep(14,"'2. 실증 ① 최종 구조 — 폰을 4면에서 잡고, 그 사이를 AI가 채웠다'","'3. 실증 — 실제로 만들 수 있다: 구조 · 조립도 · 부품'")
rep(14,"'걸이 · 집게 · 레일 · 받침은 고정 영역으로 두고, 클램프와 받침부를 잇는 삼각 프레임을 계산으로 만들었다'","'폰을 4면에서 잡는 부품은 고정 영역, 그 사이 삼각 프레임은 계산이 만들었다 — 출력 4개 + 시판 부품으로 조립'")
B[14]=B[14].replace("box(s, 0.5, 1.25, 4.6, 3.7, 'FFFFFF', 'labeled');\ns.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 1.25, w: 4.6, h: 3.7,","box(s, 0.5, 1.25, 3.3, 3.7, 'FFFFFF', 'labeled');\ns.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 1.25, w: 3.3, h: 3.7,")
B[14]=B[14].replace("fit(s, SH + 'v25_labeled.png', 0.55, 1.3, 4.5, 3.6,","fit(s, SH + 'v25_labeled.png', 0.55, 1.3, 3.2, 3.6,")
B[14]=B[14].replace("box(s, 5.25, 1.25, 4.25, 3.7, 'FFFFFF', 'asm dwg');\ns.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 5.25, y: 1.25, w: 4.25, h: 3.7,","box(s, 3.9, 1.25, 3.3, 3.7, 'FFFFFF', 'asm dwg');\ns.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 3.9, y: 1.25, w: 3.3, h: 3.7,")
B[14]=B[14].replace("fit(s, SH + 'v25_asm.png', 5.3, 1.3, 4.15, 3.6,","fit(s, SH + 'v25_asm.png', 3.95, 1.3, 3.2, 3.6,")
B[14]=B[14].replace("T(s, '※ 오른쪽 = 조립도(3면도 · 부품표 · 표제란, A3). 부품도 3장 · STL · STEP · 조립 설명서는 제작 파일 묶음에 포함'",
"""T(s, '부품 (합계 출력 96.8 g)', { x: 7.32, y: 1.25, w: 2.2, h: 0.24, fontSize: 9.5, bold: true, color: C.text2 });
[['출력', '몸체 × 1', '프레임 + 집게 하우징 + 레일 + 아래 걸이 일체'], ['출력', '슬라이드 집게 × 2', '스프링 포켓 · 화면 쪽 이탈 방지'], ['출력', '위쪽 슬라이드 걸이 × 1', '25 mm 이동 · M3 잠금'],
 ['구매', '압축 스프링 × 2', '바깥지름 5 mm (사양 확인 필요)'], ['구매', 'M3 볼트 · 너트', '멈춤 핀 2 + 잠금 3'], ['구매', 'M4 볼트 · 너트', '핸들바 조임']].forEach((r, i) => { const y = 1.55 + i * 0.47;
  pill(s, 7.32, y + 0.02, 0.5, r[0], r[0] === '출력' ? X.teal : X.amber, X.white);
  T(s, r[1], { x: 7.88, y, w: 1.65, h: 0.2, fontSize: 8.5, bold: true, color: C.text2 });
  T(s, r[2], { x: 7.88, y: y + 0.2, w: 1.65, h: 0.24, fontSize: 7, color: C.text1 }); });
box(s, 7.32, 4.42, 2.18, 0.52, X.tint, 'fit');
T(s, '폰 폭 64–90 · 두께 6–14 mm · ≤ 290 g\\n핸들바 31.8 mm · PETG 채움 100%', { x: 7.4, y: 4.42, w: 2.05, h: 0.52, fontSize: 7, color: C.text2, valign: 'middle' });
T(s, '※ 가운데 = 조립도(3면도 · 부품표 · 표제란, A3). 부품도 3장 · STL · STEP · 조립 설명서는 제작 파일 묶음에 포함'""")
# ---- 18: DX 기여 (대상 확대 + VD TV 스탠드 실증)
i=B[18].index("s.addText('3. 사업·조직 기여"); 
B[18]=B[18][:i]+r"""s.addText('4. DX 기여 — 설계 단계마다, 누구나 성능을 확인하고 개선한다', { placeholder: 'title' });
s.addText('기여는 사례 제품이 아니라 방법론 — 설계자 · 기획자 · 특허 아이디어 제안자가 같은 흐름으로 쓴다', { placeholder: 'body' });
const stg = [['구상', '경험으로 형상 결정', '요구 조건에서 설계안 자동 생성'],
  ['상세 설계', '해석 의뢰 · 결과 대기', '설계자가 직접 성능 확인 (근거 포함)'],
  ['개선', '해석 결과 보고 수작업 수정', '계산으로 재설계 (경량화 · 보강)'],
  ['시제품', '출력 · 시험 → 실패 → 수정', '출력 전 제작 형상까지 검증']];
T(s, '지금', { x: 1.5, y: 1.26, w: 1.9, h: 0.24, fontSize: 10, bold: true, color: C.accent3 });
T(s, 'FormProof 적용', { x: 3.8, y: 1.26, w: 2.2, h: 0.24, fontSize: 10, bold: true, color: C.accent1 });
stg.forEach((g, i) => { const y = 1.54 + i * 0.56;
  pill(s, 0.5, y + 0.1, 0.9, g[0], X.ink, X.white);
  box(s, 1.5, y, 1.95, 0.46, 'F3F4F5', 'now');
  T(s, g[1], { x: 1.58, y, w: 1.82, h: 0.46, fontSize: 8.5, color: C.accent3, valign: 'middle' });
  arrow(s, 3.5, y + 0.11, 0.24, 0.24);
  box(s, 3.8, y, 2.3, 0.46, X.tint, 'formproof');
  T(s, g[2], { x: 3.88, y, w: 2.18, h: 0.46, fontSize: 8.5, bold: true, color: C.text2, valign: 'middle' }); });
// 실증: VD TV 스탠드
box(s, 6.3, 1.26, 3.2, 2.48, X.tint, 'tv proof');
pill(s, 6.42, 1.34, 1.35, 'VD · 실증', X.green, X.white);
T(s, 'TV 스탠드 다리 — 외형은 그대로', { x: 6.42, y: 1.66, w: 3.0, h: 0.22, fontSize: 9.5, bold: true, color: C.text2 });
fit(s, SH + 'v6_c_tv_foot_base_S.png', 6.42, 1.92, 1.4, 0.95, 'solid foot');
fit(s, SH + 'v6_c_tv_foot_opt_S.png', 7.98, 1.92, 1.4, 0.95, 'AI foot');
T(s, '꽉 찬 판 400 g', { x: 6.42, y: 2.87, w: 1.4, h: 0.18, fontSize: 7.5, color: C.accent3, align: 'center' });
T(s, 'AI 설계 124 g', { x: 7.98, y: 2.87, w: 1.4, h: 0.18, fontSize: 7.5, bold: true, color: C.accent1, align: 'center' });
T(s, [{ text: '−69%', options: { fontSize: 18, bold: true, color: C.accent1 } }, { text: '  다리 무게 · 흔들림 0.23 mm (≤ 1 mm) · 넘어짐 통과', options: { fontSize: 7.5, color: C.text1 } }], { x: 6.42, y: 3.1, w: 3.0, h: 0.56, valign: 'middle' });
// 적용 대상
T(s, '적용 대상 — 같은 엔진, 하중 · 재료 · 기준만 바꿔서', { x: 0.5, y: 3.88, w: 6, h: 0.24, fontSize: 10, bold: true, color: C.text2 });
[['VD', 'TV 스탠드 · 벽걸이', '실증 −69%', X.green], ['MX', '폰 · 폴더블 내부 브래킷', '구조 · 열 · 낙하', X.teal], ['DA', '세탁기 · 에어컨 모터 마운트', '진동 · 음향', X.teal], ['공통', '특허 아이디어 · 기존 부품(STEP)', '성능 근거 · 경량화', X.ink]].forEach((t, i) => { const x = 0.5 + i * 2.27;
  pill(s, x, 4.16, 0.6, t[0], t[3], X.white);
  T(s, [{ text: t[1], options: { bold: true, color: C.text2, breakLine: true } }, { text: t[2], options: { color: C.accent3 } }], { x: x + 0.66, y: 4.12, w: 1.58, h: 0.5, fontSize: 8 }); });
T(s, '※ TV 스탠드: 65형 · 알루미늄 10 mm 판재 · 외곽 고정, 출력 형상 3D 재계산(상세 15쪽). MX · DA 항목은 적용 후보로 사업부 확인 필요. 정량 효과(해석 의뢰 기간, 시제품 반복 횟수)는 담당자 확인 필요', { x: 0.5, y: 4.78, w: 9, h: 0.36, fontSize: 7, color: C.accent3 });
s.addNotes('기여 주체는 방법론. 단계별로 지금 방식과 적용 후를 비교하고, VD TV 스탠드에서 외형을 유지한 채 다리 무게 69%를 줄인 실증을 보인다. MX · DA는 같은 엔진의 적용 후보.');
"""
# ---- 19: 파급 효과 → 해커톤 이후 로드맵
i=B[19].index("T(s, '파급 효과'"); j=B[19].index("s.addNotes(",i)
B[19]=B[19][:i]+r"""T(s, '해커톤 이후', { x: 0.5, y: 3.98, w: 2, h: 0.26, fontSize: 11, bold: true, color: C.accent1 });
[['입력 확장', '문서 · 특허 · STEP 입력'], ['자동 실행', '에이전트가 단계 실행 · 검증 리포트'], ['물리 모듈', '낙하 · 피로 → 전자기'], ['시범 적용', 'VD 스탠드 실제 설계 과제']].forEach((r, i) => { const x = 0.5 + i * 2.27;
  box(s, x, 4.28, 2.15, 0.58, X.tint, 'road');
  T(s, [{ text: (i + 1) + '  ' + r[0], options: { bold: true, color: C.text2, breakLine: true } }, { text: r[1], options: { color: C.text1 } }], { x: x + 0.1, y: 4.3, w: 1.98, h: 0.54, fontSize: 8.5, valign: 'middle' });
  if (i < 3) s.addShape(pres.shapes.CHEVRON, { x: x + 2.16, y: 4.48, w: 0.09, h: 0.18, fill: { color: X.amber }, line: { color: X.amber } }); });
T(s, '파급: 생성형 AI 결과에 물리 검증을 붙이는 관문은 다른 생성형 AI 과제에도 재사용 · 설계가 쌓일수록 물리 AI가 정확해져 계산 시간 단축', { x: 0.5, y: 4.92, w: 9, h: 0.24, fontSize: 7.5, color: C.accent3 });
"""+B[19][j:]
order_main=[1,2,3,4,5,7,8,10,15,14,17,18,19,21]; order_app=[22,6,9,11,12,13,16,20]
S={1:'표지',2:'요약',3:'1. 문제 정의',4:'2. 기술 차별성',10:'3. 실증',18:'4. DX 기여 · 확장',21:'마무리',22:'부록'}
out=[head]
for k in order_main+order_app:
    if k in S: out.append("pres.addSection({ title: '%s' });"%S[k])
    out.append(B[k])
out.append(tail)
open('build_v53.js','w').write('\n'.join(out))
print('ok')
