const pptxgen = require('pptxgenjs');
const fs = require('fs');
const { applyTheme } = require('/root/.claude/skills/synced/1e9abda0-994b-4505-92f0-2b787b374f9b_2a6ad69a-e73b-4fbf-b931-59083e82c013/pptx/scripts/apply_theme.js');
const OUT = process.argv[2];
const TH = '/tmp/claude-0/-home-claude/e964ed80-ee1b-5f91-abd3-3081682a3ad7/scratchpad/thumbs/';
const img = f => 'image/png;base64,' + fs.readFileSync(TH + f).toString('base64');

const THEME = {
  name: 'FormProof', headFontFace: '맑은 고딕', bodyFontFace: '맑은 고딕',
  colors: { dk1: '1B2430', lt1: 'FFFFFF', dk2: '14323A', lt2: 'EEF3F2',
    accent1: '0F7C80', accent2: 'E8A33D', accent3: '5B6B78', accent4: 'C8DCDA',
    accent5: 'B4472F', accent6: '2E7D4F', hlink: '0F7C80', folHlink: '5B6B78' } };
const HEX = { teal: '0F7C80', ink: '14323A', amber: 'E8A33D', mute: '5B6B78', tint: 'EEF3F2', line: 'C8DCDA', red: 'B4472F', green: '2E7D4F' };

const pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = 'FormProof 발표 초안 v1';
const C = pres.SchemeColor;

pres.defineSlideMaster({ title: 'DARK', background: { color: C.text2 },
  objects: [{ placeholder: { options: { name: 'title', type: 'title', x: 0.6, y: 1.55, w: 8.8, h: 1.2, fontSize: 36, bold: true, color: C.background1, valign: 'top', align: 'left' }, text: '' } },
            { placeholder: { options: { name: 'body', type: 'body', x: 0.6, y: 2.85, w: 8.8, h: 1.4, fontSize: 16, color: C.accent4, valign: 'top' }, text: '' } }] });
pres.defineSlideMaster({ title: 'CONTENT', background: { color: C.background1 },
  objects: [{ placeholder: { options: { name: 'title', type: 'title', x: 0.5, y: 0.28, w: 9.0, h: 0.6, fontSize: 22, bold: true, color: C.text2, valign: 'middle', margin: 0, align: 'left' }, text: '' } },
            { placeholder: { options: { name: 'body', type: 'body', x: 0.5, y: 0.86, w: 9.0, h: 0.4, fontSize: 13, color: C.accent3, valign: 'top', margin: 0 }, text: '' } },
            { text: { text: 'FormProof  |  사내 AI 해커톤', options: { x: 0.5, y: 5.25, w: 5, h: 0.25, fontSize: 9, color: C.accent3, margin: 0 } } }],
  slideNumber: { x: 9.0, y: 5.25, w: 0.5, h: 0.25, fontSize: 9, color: C.accent3, align: 'right' } });

const sec = (n, t) => { pres.addSection({ title: t }); return t; };
function tag(s, n, x, y) {   // numbered section chip (deck motif)
  s.addShape(pres.shapes.OVAL, { x, y, w: 0.42, h: 0.42, fill: { color: C.accent1 }, line: { color: C.accent1 }, objectName: 'chip' });
  s.addText(String(n), { x, y, w: 0.42, h: 0.42, fontSize: 14, bold: true, color: C.background1, align: 'center', valign: 'middle', margin: 0, isTextBox: true });
}
function card(s, x, y, w, h, head, body, opt = {}) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: opt.fill || C.background2 }, line: { color: opt.fill || C.background2 }, objectName: 'card' });
  s.addText(head, { x: x + 0.18, y: y + 0.14, w: w - 0.36, h: 0.36, fontSize: 14, bold: true, color: opt.headColor || C.text2, margin: 0, valign: 'top', isTextBox: true });
  s.addText(body, { x: x + 0.18, y: y + 0.52, w: w - 0.36, h: h - 0.64, fontSize: 11, color: C.text1, margin: 0, valign: 'top', paraSpaceAfter: 3, isTextBox: true });
}

// 1. 표지
let S = sec(0, '표지');
let s = pres.addSlide({ masterName: 'DARK', sectionTitle: S });
s.addText('FormProof', { placeholder: 'title' });
s.addText('말 한 줄·스케치 한 장에서 성능이 확인된 3D 설계까지\n물리 기반 생성형 AI', { placeholder: 'body' });
s.addText('발표 초안 v1  |  팀원 A · 팀원 B · 팀원 C', { x: 0.6, y: 4.7, w: 8.8, h: 0.3, fontSize: 11, color: C.accent4, margin: 0, isTextBox: true });
s.addNotes('표지. 팀명 FormProof = Form + Proof, 형상을 성능으로 증명한다는 뜻.');

// 2. 목차
S = sec(0, '목차');
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: S });
s.addText('발표 구성', { placeholder: 'title' });
const toc = [['문제 정의', '아이디어를 제작 가능한 설계로 바꾸는 데 필요한 네 가지 장벽'],
  ['기술 차별성', '생성형 AI와 물리 엔진을 검증 단계로 묶은 하나의 설계 과정'],
  ['사업·조직 기여', 'DX 부문 제품 개발에 직접 쓰이는 적용처'],
  ['확장성·파급 효과', '물리 분야·제품군·사용자·데이터 자산으로의 확장']];
toc.forEach((t, i) => {
  const y = 1.3 + i * 0.92;
  tag(s, i + 1, 0.7, y + 0.06);
  s.addText(t[0], { x: 1.35, y, w: 3.0, h: 0.55, fontSize: 18, bold: true, color: C.text2, valign: 'middle', margin: 0, isTextBox: true });
  s.addText(t[1], { x: 4.2, y, w: 5.3, h: 0.55, fontSize: 13, color: C.accent3, valign: 'middle', margin: 0, isTextBox: true });
});

// 3. 문제 정의
S = sec(1, '1. 문제 정의');
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: S });
s.addText('1. 문제 정의 — 검증된 설계로 가는 길이 막혀 있다', { placeholder: 'title' });
s.addText('설계·해석 숙련자가 아니면 제작 전 성능을 알 수 없고, 범용 AI는 근거 없는 결과를 그대로 내놓는다', { placeholder: 'body' });
const probs = [
  ['① 3D 설계 전환 장벽', '아이디어·기존 제품을 치수 수정이 가능한 3D 설계(CAD)로 옮기려면 치수 측정과 설계 도구 숙련이 필요'],
  ['② 제작 전 성능 검증 부재', '강도·변형·진동·발열을 미리 확인하기 어려워 출력 → 확인 → 수정의 시행착오 반복'],
  ['③ 최적 구조의 전문성 요구', '성능을 유지하며 재료를 줄이려면 해석·위상최적화 전문 지식과 시간이 필요'],
  ['④ 범용 LLM 설계의 신뢰성 한계', '하중·고정 조건, 판정 기준, 계산 해상도가 부적절해도 결과가 그대로 제시되고, 비전문가는 판별 불가']];
probs.forEach((p, i) => {
  const x = 0.5 + (i % 2) * 4.6, y = 1.45 + Math.floor(i / 2) * 1.62;
  card(s, x, y, 4.4, 1.45, p[0], p[1], i === 3 ? { headColor: C.accent5 } : {});
});
s.addText('사례: 자전거 폰 거치대 기본 설계는 1차 고유진동수 26.5 Hz — 자갈길 진동(34.6~45.6 Hz) 대역과 가까워 공진 위험. 출력 전에는 알 수 없음', { x: 0.5, y: 4.75, w: 9.0, h: 0.4, fontSize: 11, italic: true, color: C.accent1, margin: 0, isTextBox: true });
s.addNotes('문제 ①~③은 사람의 숙련도 장벽, ④는 LLM만으로 해결하려 할 때의 신뢰성 문제. 하단 사례 수치는 우리 계산값(진동 대역은 ISBS 2020 측정값).');

// 4. 기술 차별성 (비교)
S = sec(2, '2. 기술 차별성');
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: S });
s.addText('2. 기술 차별성 — 생성 · 계산 · 검증을 하나로 묶었다', { placeholder: 'title' });
s.addText('범용 LLM은 형상만, 전문가 도구는 숙련자만 — FormProof는 비전문가 입력에서 검증된 제작 파일까지', { placeholder: 'body' });
const O = { fontSize: 11, color: C.text1, valign: 'middle', margin: [2, 6, 2, 6] };
const H = { fontSize: 11, bold: true, color: C.background1, fill: { color: C.text2 }, align: 'center', valign: 'middle' };
const yes = t => ({ text: t, options: { ...O, color: C.accent6, bold: true } });
const no = t => ({ text: t, options: { ...O, color: C.accent3 } });
const rows = [
  [{ text: '항목', options: H }, { text: '범용 LLM 3D 생성', options: H }, { text: '전문가용 해석·최적화 도구', options: H }, { text: 'FormProof', options: { ...H, fill: { color: C.accent1 } } }],
  [{ text: '입력', options: { ...O, bold: true } }, no('텍스트'), no('CAD 모델 + 조건 직접 설정'), yes('텍스트·스케치·사진·STEP')],
  [{ text: '물리 조건', options: { ...O, bold: true } }, no('없음 또는 임의 가정'), no('사용자가 직접 정의'), yes('표준·문헌 근거로 자동 정의, 빠진 조건은 질문')],
  [{ text: '구조 개선', options: { ...O, bold: true } }, no('없음'), no('가능 (숙련 필요)'), yes('3D 미분 기반 최적화 자동 실행')],
  [{ text: '결과 검증', options: { ...O, bold: true } }, no('없음'), no('사용자 판단'), yes('조건·수렴·제작 형상 재해석 자동 게이트')],
  [{ text: '사용자', options: { ...O, bold: true } }, no('누구나 (신뢰성 낮음)'), no('설계·해석 전문가'), yes('비전문가')]];
s.addTable(rows, { x: 0.5, y: 1.4, w: 9.0, colW: [1.3, 2.2, 2.5, 3.0], rowH: 0.46, border: { type: 'solid', pt: 0.5, color: HEX.line } });
s.addText('※ 비교 대상은 범주 수준의 일반 특성이며, 특정 제품의 기능 비교는 확인 필요', { x: 0.5, y: 4.4, w: 9.0, h: 0.3, fontSize: 10, color: C.accent3, margin: 0, isTextBox: true });
s.addNotes('핵심 메시지: 차별점은 개별 기술이 아니라 연결 방식. 특히 "자동 검증 게이트"가 LLM 단독 설계의 신뢰성 문제(문제 ④)를 막는다. 특정 상용 제품명과의 기능 비교는 확인 후 추가.');

// 5. 기술 차별성 (근거 사례)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: S });
s.addText('2. 기술 차별성 — 실제 계산으로 확인한 결과', { placeholder: 'title' });
s.addText('자전거 폰 거치대: 근거 조건 → 3D 무게 최소화 → 출력 형상 재검증', { placeholder: 'body' });
s.addImage({ data: img('t0.png'), x: 0.5, y: 1.4, w: 2.6, h: 1.69, objectName: 'base design' });
s.addText('기본 설계', { x: 0.5, y: 3.1, w: 2.6, h: 0.3, fontSize: 11, bold: true, color: C.accent3, align: 'center', margin: 0, isTextBox: true });
s.addShape(pres.shapes.RIGHT_ARROW, { x: 3.2, y: 2.05, w: 0.45, h: 0.4, fill: { color: C.accent2 }, line: { color: C.accent2 } });
s.addImage({ data: img('t4.png'), x: 3.75, y: 1.4, w: 2.6, h: 1.69, objectName: 'optimized design' });
s.addText('최적화 설계 (출력용)', { x: 3.75, y: 3.1, w: 2.6, h: 0.3, fontSize: 11, bold: true, color: C.accent1, align: 'center', margin: 0, isTextBox: true });
const stats = [['−20%', '무게 50.0 → 39.8 g'], ['99.4 Hz', '1차 고유진동수 (기준 ≥ 91 Hz)'], ['18.3 MPa', '최대 응력 (기준 ≤ 26 MPa)']];
stats.forEach((t, i) => {
  const y = 1.4 + i * 0.68;
  s.addText(t[0], { x: 6.55, y, w: 1.4, h: 0.55, fontSize: 20, bold: true, color: C.accent1, valign: 'middle', margin: 0, isTextBox: true });
  s.addText(t[1], { x: 7.95, y, w: 1.6, h: 0.55, fontSize: 10, color: C.text1, valign: 'middle', margin: 0, isTextBox: true });
});
card(s, 0.5, 3.6, 9.0, 1.45, '근거가 있는 조건과 판정', '진동 34.6~45.6 Hz·48.5 g (ISBS 2020 실측) → 공진 회피 기준 f1 ≥ 91 Hz  |  재료 PETG 물성 (제조사 TDS) → 응력 ≤ 26 MPa (안전계수 1.5)\n설계 격자 결과를 그대로 믿지 않고, 실제 출력 형상(STL)을 1 mm 격자로 다시 해석해 두 기준 모두 통과 확인\nTV 스탠드(IEC 62368-1 안정성 기준, 알루미늄) 사례는 계산 진행 중');
s.addNotes('수치는 모두 실제 FEM 계산값. 무게 비교 기준은 처음 기본 설계(50.0 g). 1 mm 재검증은 최적화 격자(2 mm)보다 촘촘한 독립 해석. TV 스탠드는 결과 확정 후 반영.');

// 6. 사업·조직 기여
S = sec(3, '3. 사업·조직 기여');
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: S });
s.addText('3. 사업·조직 기여 — DX 부문 제품 개발에 직접 기여', { placeholder: 'title' });
s.addText('구조물·액세서리 설계의 시제품 반복을 줄이고, 해석 전문 인력 의존을 낮춘다', { placeholder: 'body' });
const bus = [['VD (TV·모니터)', 'TV 스탠드·벽걸이 브래킷의 전도 안정성·강성 설계와 경량화', '시연 사례: TV 스탠드'],
  ['MX (모바일·웨어러블)', '액세서리·거치대·웨어러블 프레임의 강도·진동·착용 형상 설계', '시연 사례: 자전거 거치대'],
  ['DA (생활가전)', '내부 브래킷·지지 구조물의 경량화와 진동 회피 설계', '적용 후보']];
bus.forEach((b, i) => {
  const x = 0.5 + i * 3.05;
  card(s, x, 1.4, 2.85, 1.85, b[0], b[1] + '\n\n' + b[2], { headColor: C.accent1 });
});
const eff = [['시제품 반복 감소', '출력 전 성능 확인으로 출력-수정 반복 축소'], ['재료·물류비 절감', '성능 기준 안에서 무게 최소화'], ['설계 리드타임 단축', '해석 요청-대기 없이 설계자가 직접 확인']];
eff.forEach((e, i) => {
  const x = 0.5 + i * 3.05;
  s.addText(e[0], { x, y: 3.45, w: 2.85, h: 0.35, fontSize: 13, bold: true, color: C.text2, margin: 0, isTextBox: true });
  s.addText(e[1], { x, y: 3.8, w: 2.85, h: 0.5, fontSize: 11, color: C.text1, margin: 0, valign: 'top', isTextBox: true });
});
s.addText('※ 사업부별 적용처는 후보이며, 정량 효과(반복 횟수·비용·기간)는 파일럿 적용으로 측정 필요 — 확인 필요', { x: 0.5, y: 4.55, w: 9.0, h: 0.5, fontSize: 10, color: C.accent3, margin: 0, isTextBox: true });
s.addNotes('VD·MX는 시연 사례와 직접 연결. DA는 후보로만 제시. 정량 효과 수치는 근거가 없어 넣지 않음 — 사업부 담당자 인터뷰나 파일럿으로 확보 필요.');

// 7. 확장성·파급 효과
S = sec(4, '4. 확장성·파급 효과');
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: S });
s.addText('4. 확장성·파급 효과 — 문제 하나가 아니라 설계 플랫폼', { placeholder: 'title' });
s.addText('같은 과정에 물리 모듈·제품군·사용자·데이터를 더해 가는 구조', { placeholder: 'body' });
const axes = [['물리 분야', '구조(정적·진동) → 열 → 광학(PINN) → 구조·열 동시 설계'],
  ['제품군', '액세서리·거치대 → 가전·TV 구조물 → 기존 제품 개선(보강·경량화)'],
  ['사용자', '설계자 → 비전문가 임직원 → 고객 맞춤 제품(치수 맞춤)'],
  ['데이터 자산', '해석 결과 축적 → 반복 제품군별 물리 AI 가속 모델 → 설계 시간 단축']];
axes.forEach((a, i) => {
  const y = 1.4 + i * 0.78;
  tag(s, i + 1, 0.5, y + 0.07);
  s.addText(a[0], { x: 1.1, y, w: 1.6, h: 0.56, fontSize: 14, bold: true, color: C.text2, valign: 'middle', margin: 0, isTextBox: true });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 2.75, y, w: 6.75, h: 0.56, rectRadius: 0.08, fill: { color: C.background2 }, line: { color: C.background2 } });
  s.addText(a[1], { x: 2.9, y, w: 6.5, h: 0.56, fontSize: 12, color: C.text1, valign: 'middle', margin: 0, isTextBox: true });
});
s.addText('파급 효과: 생성형 AI 결과에 물리 검증을 붙이는 사내 표준 방식 — 다른 생성형 AI 과제에도 같은 검증 게이트 재사용 가능', { x: 0.5, y: 4.6, w: 9.0, h: 0.45, fontSize: 12, bold: true, color: C.accent1, margin: 0, isTextBox: true });
s.addNotes('확장은 네 축. 데이터 자산 축은 장기적으로 계산 비용을 낮추는 근거.');

// 8. 마무리
S = sec(5, '마무리');
s = pres.addSlide({ masterName: 'DARK', sectionTitle: S });
s.addText('형상을 성능으로 증명한다', { placeholder: 'title' });
s.addText('FormProof — 비전문가의 아이디어를, 검증된 제작 파일로', { placeholder: 'body' });
s.addNotes('마무리 한 문장.');

pres.writeFile({ fileName: OUT }).then(() => applyTheme(OUT, THEME)).then(() => console.log('ok', OUT));
