// ---------- 8. 확장성 (v137: 제품 · 물리 · 시스템 연동 3축)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '5. DX 기여 · 확장' });
s.addText('5. 확장성 — 같은 흐름으로 제품 · 물리 · 사내 시스템까지 확장', { placeholder: 'title' });
s.addText('입력 → 설계 사양 → 역설계 → 출력 형상 검증 → 제작 파일 흐름은 그대로, 대상과 연결만 넓힌다', { placeholder: 'body' });
{
const CW = 2.93, G = 0.1, Y = 1.25, H = 3.45;
const IX = { glass: await icon(fa.FaGlasses, '1428A0'), fold: await icon(fa.FaMobileAlt, '1428A0'), tv: await icon(fa.FaTv, '1428A0'), home: await icon(md.MdKitchen, '1428A0'),
  doc: await icon(fa.FaFileAlt, '1428A0'), srch: await icon(fa.FaSearch, '1428A0'), cube: await icon(fa.FaCube, '1428A0'), calc: await icon(fa.FaCalculator, '1428A0'), rep: await icon(fa.FaFileSignature, '1428A0') };
const col = (i, no, t, sub) => { const x = 0.5 + i * (CW + G); box(s, x, Y, CW, H, X.tint, 'axis');
  T(s, [{ text: no + '  ', options: { color: '1428A0' } }, { text: t, options: { color: C.text2 } }], { x: x + 0.14, y: Y + 0.1, w: CW - 0.28, h: 0.3, fontSize: 12, bold: true });
  T(s, sub, { x: x + 0.14, y: Y + 0.4, w: CW - 0.28, h: 0.2, fontSize: 7.5, color: C.accent3 }); return x; };
const row = (x, y, ic, t1, t2, tag) => { s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.12, y, w: CW - 0.24, h: 0.5, rectRadius: 0.04, fill: { color: 'FFFFFF' }, line: { color: 'D3DBEE', width: 0.75 }, objectName: 'row' });
  s.addImage({ data: ic, x: x + 0.22, y: y + 0.13, w: 0.24, h: 0.24 });
  T(s, [{ text: t1, options: { bold: true, color: C.text2, breakLine: true } }, { text: t2, options: { fontSize: 7, color: C.text1 } }], { x: x + 0.55, y, w: CW - 1.35, h: 0.5, fontSize: 8.5, valign: 'middle' });
  if (tag) pill(s, x + CW - 0.8, y + 0.14, 0.62, tag[0], tag[1], X.white); };
// ① 제품
let x = col(0, '①', '제품 확장', '동일 엔진 — 하중 · 재료 · 기준만 변경');
row(x, Y + 0.68, IX.glass, 'AR 글래스', '착용 무게 · 코 하중 · 발열 · 부품 배치');
row(x, Y + 1.24, IX.fold, '폴더블 · 웨어러블', '박형 구조 강성 · 방열 · 착용감');
row(x, Y + 1.8, IX.tv, 'TV · 사이니지', '슬림 구조 · 진동 · 방열');
row(x, Y + 2.36, IX.home, '가전', '구조 · 진동 · 소음 · 방열');
T(s, '실증: 자전거 폰 거치대 (진동 · 열 · 충격)', { x: x + 0.14, y: Y + 2.98, w: CW - 0.28, h: 0.3, fontSize: 7.5, bold: true, color: '1428A0', valign: 'middle' });
// ② 물리
x = col(1, '②', '물리 확장', '방정식 모듈 추가 — 흐름 · 판정 구조 동일');
[['구조 · 진동 · 충격', '정적 · 고유진동 · 진동 응답 · 충격', ['구현', '1428A0'], IC.cogs], ['열전도', '발열 · 방열 경로', ['구현', '1428A0'], IC.heat],
 ['낙하 · 피로', '기구 부품 신뢰성', ['확장', '8A949C'], IC.shieldT], ['소음 · 전자기', '진동 소음 · 무선충전 금속 금지 구역', ['확장', '8A949C'], IC.bolt]].forEach((p, k) => row(x, Y + 0.68 + k * 0.56, p[3], p[0], p[1], p[2]));
T(s, '물리 AI는 새 물리의 FEM 결과로 추가 학습', { x: x + 0.14, y: Y + 2.98, w: CW - 0.28, h: 0.3, fontSize: 7.5, bold: true, color: '1428A0', valign: 'middle' });
// ③ 시스템 연동
x = col(2, '③', '사내 시스템 연동', '특허 시스템: 제안 단계에서 효과를 계산으로 확인');
[[IX.doc, '특허 제안서 (PDF)'], [IX.srch, '청구항 · 효과 주장 추출'], [IX.cube, '특허 구조 · 기준 구조 형상화'], [IX.calc, '같은 조건 FEM 비교'], [IX.rep, '효과 검증 리포트 자동 첨부']].forEach((p, k) => { const y = Y + 0.68 + k * 0.45;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.12, y, w: CW - 0.24, h: 0.36, rectRadius: 0.04, fill: { color: k === 4 ? 'EEF2FB' : 'FFFFFF' }, line: { color: k === 4 ? '1428A0' : 'D3DBEE', width: 0.75 }, objectName: 'pstep' });
  s.addImage({ data: p[0], x: x + 0.22, y: y + 0.07, w: 0.22, h: 0.22 });
  T(s, p[1], { x: x + 0.55, y, w: CW - 0.7, h: 0.36, fontSize: 8.5, bold: k === 4, color: C.text2, valign: 'middle' });
  if (k < 4) s.addShape(pres.shapes.LINE, { x: x + 0.33, y: y + 0.36, w: 0, h: 0.09, line: { color: '8A949C', width: 1, endArrowType: 'triangle' } }); });
T(s, '법적 유효성 판단이 아닌, 주장한 기술 효과의 계산 확인', { x: x + 0.14, y: Y + 2.98, w: CW - 0.28, h: 0.3, fontSize: 7.5, bold: true, color: '1428A0', valign: 'middle' });
}
s.addNotes('확장 3축. ① 제품: 같은 엔진에 하중 · 재료 · 기준만 바꿔 AR 글래스 · 폴더블 · 웨어러블 · TV · 가전으로. 실증은 자전거 폰 거치대. ② 물리: 구조 · 진동 · 충격 · 열전도는 구현, 낙하 · 피로 · 소음 · 전자기는 방정식 모듈 추가로 확장. 물리 AI는 새 물리의 FEM 결과로 추가 학습. ③ 사내 시스템 연동: 특허 제안서를 입력으로 청구항의 효과 주장을 뽑아 특허 구조와 기준 구조를 같은 조건으로 계산 비교하고, 효과 검증 리포트를 제안서에 자동 첨부. 특허의 법적 유효성이 아니라 기술 효과의 계산 확인.');

// ---------- 8b. 향후 계획 (v137)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '5. DX 기여 · 확장' });
s.addText('5. 향후 계획 — 해커톤 구현 범위와 단계별 확대', { placeholder: 'title' });
s.addText('해커톤에서 엔진 · 검증 · 실증까지 완료, 이후 AI 학습 → 입력 · 연동 확대 → 사업부 적용 순으로 진행', { placeholder: 'body' });
{
const ST = [
  ['1단계', '해커톤 구현 범위', '1428A0', true, ['조건 생성기 (LLM + 근거 DB · 설계 사양 JSON)', '위상 최적화 + FEM 엔진 (구조 · 진동 · 충격 · 열)', '출력 형상 자동 검증 (연결성 · 중간 밀도 · 기준)', '자전거 폰 거치대 실증 · 제작 파일 · 도면', '형상 AI · 물리 AI 학습 데이터 282개 구축']],
  ['2단계', 'AI 엔진 완성', '3E5BC8', false, ['형상 AI (DeepSDF) 학습 · 재구성 정확도 확보', '물리 AI (신경 연산자 GINO · FNO) 학습', 'AI 후보에서 시작하는 위상 최적화 → 계산 시간 단축', '학습 데이터 확대 (형상 2,000개 이상)']],
  ['3단계', '입력 · 연동 확대', '6F86D6', false, ['문서 · 이미지 · STEP 입력', '사내 특허 시스템 연동 — 효과 검증 리포트 자동 첨부', '제작성 검사 고도화 (최소 두께 · 서포트)', '근거 리포트 자동 생성']],
  ['4단계', '사업부 적용', '0F1B3D', false, ['MX AR 글래스 · 폴더블 시범 과제', '물리 모듈 확장 (낙하 · 피로 · 소음 · 전자기)', '설계 데이터 누적 → 물리 AI 정확도 향상', '사내 설계 도구 · CAD 연계']]];
const W = 2.17, Gp = 0.1, Y = 1.25;
ST.forEach((p, i) => { const x = 0.5 + i * (W + Gp);
  s.addShape(i ? pres.shapes.CHEVRON : pres.shapes.PENTAGON, { x, y: Y, w: W + 0.12, h: 0.5, fill: { color: p[2] }, line: { color: X.white, width: 1 }, objectName: 'stage' });
  T(s, [{ text: p[0] + '  ', options: { color: 'D9E1F5', fontSize: 8 } }, { text: p[1], options: { bold: true, color: X.white } }], { x: x + (i ? 0.22 : 0.12), y: Y, w: W - 0.2, h: 0.5, fontSize: 10.5, valign: 'middle' });
  box(s, x, Y + 0.62, W, 2.85, p[3] ? 'EEF2FB' : X.tint, 'stage body');
  if (p[3]) s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: Y + 0.62, w: W, h: 2.85, rectRadius: 0.08, fill: { type: 'none' }, line: { color: '1428A0', width: 1.5 }, objectName: 'done frame' });
  pill(s, x + 0.12, Y + 0.74, p[3] ? 0.62 : 0.72, p[3] ? '완료' : '계획', p[3] ? '1428A0' : '8A949C', X.white);
  p[4].forEach((t, k) => T(s, [{ text: (p[3] ? '✓ ' : '· '), options: { bold: true, color: p[3] ? '1428A0' : C.accent3 } }, { text: t }], { x: x + 0.12, y: Y + 1.12 + k * 0.46, w: W - 0.2, h: 0.44, fontSize: 8, color: C.text1, valign: 'top' })); });
T(s, '※ 2단계 학습 데이터 · 코드 · 실행 스크립트는 구현 패키지로 인계 완료 (GPU 학습)', { x: 0.5, y: 4.92, w: 9, h: 0.2, fontSize: 7, color: C.accent3 });
}
s.addNotes('향후 계획. 1단계(해커톤 구현 범위, 완료): 조건 생성기, 위상 최적화 + FEM 엔진, 출력 형상 자동 검증, 자전거 폰 거치대 실증과 제작 파일, 학습 데이터 282개. 2단계 AI 엔진 완성: 형상 AI · 물리 AI 학습과 AI 후보에서 시작하는 위상 최적화. 3단계 입력 · 연동 확대: 문서 · 이미지 · STEP 입력, 사내 특허 시스템 연동, 제작성 검사, 근거 리포트. 4단계 사업부 적용: MX 시범 과제, 물리 모듈 확장, 데이터 누적, 사내 설계 도구 연계.');

