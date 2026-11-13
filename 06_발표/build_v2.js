const pptxgen = require('pptxgenjs');
const fs = require('fs');
const React = require('react'), RDS = require('react-dom/server'), sharp = require('sharp');
const fa = require('react-icons/fa'), md = require('react-icons/md');
const { applyTheme } = require('/root/.claude/skills/synced/1e9abda0-994b-4505-92f0-2b787b374f9b_2a6ad69a-e73b-4fbf-b931-59083e82c013/pptx/scripts/apply_theme.js');
const OUT = process.argv[2];
const SH = '/tmp/claude-0/-home-claude/e964ed80-ee1b-5f91-abd3-3081682a3ad7/scratchpad/deck/shots/';
const DRW = '/tmp/claude-0/-home-claude/e964ed80-ee1b-5f91-abd3-3081682a3ad7/scratchpad/out/FormProof_자전거거치대_도면_v3.png';
const pic = (p) => 'image/png;base64,' + fs.readFileSync(p).toString('base64');
const im = f => pic(SH + f);
const imgSize = p => { const b = fs.readFileSync(p); return [b.readUInt32BE(16), b.readUInt32BE(20)]; };
function fit(s, path, x, y, w, h, name) {   // contain image in box, centered
  const [iw, ih] = imgSize(path); const r = Math.min(w / iw, h / ih); const W = iw * r, H = ih * r;
  s.addImage({ data: pic(path), x: x + (w - W) / 2, y: y + (h - H) / 2, w: W, h: H, objectName: name, altText: name });
}
async function icon(Comp, hex) {
  const svg = RDS.renderToStaticMarkup(React.createElement(Comp, { color: '#' + hex, size: 256 }));
  return 'image/png;base64,' + (await sharp(Buffer.from(svg)).png().toBuffer()).toString('base64');
}

const THEME = { name: 'FormProof', headFontFace: '맑은 고딕', bodyFontFace: '맑은 고딕',
  colors: { dk1: '1B2430', lt1: 'FFFFFF', dk2: '14323A', lt2: 'EEF3F2', accent1: '0F7C80', accent2: 'E8A33D',
    accent3: '5B6B78', accent4: 'C8DCDA', accent5: 'C0392B', accent6: '2E7D4F', hlink: '0F7C80', folHlink: '5B6B78' } };
const X = { teal: '0F7C80', ink: '14323A', amber: 'E8A33D', mute: '5B6B78', tint: 'EEF3F2', line: 'C8DCDA', red: 'C0392B', green: '2E7D4F', white: 'FFFFFF' };

(async () => {
const IC = {
  tv: await icon(fa.FaTv, X.teal), phone: await icon(fa.FaMobileAlt, X.teal), kitchen: await icon(md.MdKitchen, X.teal),
  chat: await icon(fa.FaCommentDots, X.white), cube: await icon(fa.FaCube, X.white), shield: await icon(fa.FaShieldAlt, X.white),
  redo: await icon(fa.FaRedoAlt, X.white), file: await icon(fa.FaFileExport, X.white), check: await icon(fa.FaCheck, X.green),
  cross: await icon(fa.FaTimes, X.red), bolt: await icon(fa.FaBolt, X.teal), user: await icon(fa.FaUserTie, X.teal),
  db: await icon(fa.FaDatabase, X.teal), heat: await icon(fa.FaThermometerHalf, X.teal), bulb: await icon(fa.FaLightbulb, X.amber),
  cogs: await icon(fa.FaCogs, X.teal), shieldT: await icon(fa.FaShieldAlt, X.teal),
};

const pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = 'FormProof 발표 초안 v2';
const C = pres.SchemeColor;

pres.defineSlideMaster({ title: 'DARK', background: { color: C.text2 },
  objects: [{ placeholder: { options: { name: 'title', type: 'title', x: 0.6, y: 1.5, w: 5.2, h: 1.0, fontSize: 40, bold: true, color: C.background1, align: 'left', valign: 'top', margin: 0 }, text: '' } },
            { placeholder: { options: { name: 'body', type: 'body', x: 0.6, y: 2.6, w: 5.0, h: 1.2, fontSize: 16, color: C.accent4, align: 'left', valign: 'top', margin: 0 }, text: '' } }] });
pres.defineSlideMaster({ title: 'CONTENT', background: { color: C.background1 },
  objects: [{ placeholder: { options: { name: 'title', type: 'title', x: 0.5, y: 0.3, w: 9.0, h: 0.55, fontSize: 22, bold: true, color: C.text2, align: 'left', valign: 'middle', margin: 0 }, text: '' } },
            { placeholder: { options: { name: 'body', type: 'body', x: 0.5, y: 0.85, w: 9.0, h: 0.35, fontSize: 13, color: C.accent3, align: 'left', valign: 'top', margin: 0 }, text: '' } },
            { text: { text: 'FormProof  |  사내 AI 해커톤', options: { x: 0.5, y: 5.28, w: 5, h: 0.22, fontSize: 9, color: C.accent3, margin: 0 } } }],
  slideNumber: { x: 9.0, y: 5.28, w: 0.5, h: 0.22, fontSize: 9, color: C.accent3, align: 'right' } });

const T = (s, text, o) => s.addText(text, { margin: 0, isTextBox: true, valign: 'top', color: C.text1, fontSize: 12, ...o });
const box = (s, x, y, w, h, fill, name) => s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill }, line: { color: fill }, objectName: name || 'box' });
const disc = (s, x, y, d, fill, ic, name) => { s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill }, objectName: name || 'disc' }); if (ic) s.addImage({ data: ic, x: x + d * 0.24, y: y + d * 0.24, w: d * 0.52, h: d * 0.52 }); };
const arrow = (s, x, y, w, h, col) => s.addShape(pres.shapes.RIGHT_ARROW, { x, y, w, h, fill: { color: col || C.accent2 }, line: { color: col || C.accent2 }, objectName: 'arrow' });
const pill = (s, x, y, w, text, fill, col) => { s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.28, rectRadius: 0.14, fill: { color: fill }, line: { color: fill } }); T(s, text, { x, y, w, h: 0.28, fontSize: 10, bold: true, color: col, align: 'center', valign: 'middle' }); };

// ---------- 1. 표지
pres.addSection({ title: '표지' });
let s = pres.addSlide({ masterName: 'DARK', sectionTitle: '표지' });
s.addText('FormProof', { placeholder: 'title' });
s.addText('말 한 줄로 시작해\n성능이 확인된 3D 설계까지', { placeholder: 'body' });
T(s, '물리 기반 생성형 AI  ·  팀원 A · B · C', { x: 0.6, y: 4.6, w: 5, h: 0.3, fontSize: 11, color: C.accent4 });
box(s, 5.9, 0.9, 3.7, 3.8, 'FFFFFF', 'hero card');
fit(s, SH + 'r_final_stl.png', 6.05, 1.2, 3.4, 2.5, 'optimized phone mount');
T(s, '자전거 폰 거치대 — AI가 찾은 최적 구조', { x: 6.05, y: 3.85, w: 3.4, h: 0.3, fontSize: 11, bold: true, color: C.text2, align: 'center' });
T(s, '무게 −20%, 진동·강도 기준 통과', { x: 6.05, y: 4.15, w: 3.4, h: 0.3, fontSize: 10, color: C.accent1, align: 'center' });
s.addNotes('FormProof = Form + Proof. 형상을 성능으로 증명한다. 오른쪽은 실제 계산으로 얻은 거치대 형상(출력용 STL).');

// ---------- 2. 한 장 요약
pres.addSection({ title: '요약' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '요약' });
s.addText('한 장 요약 — 요청 한 줄이 검증된 제작 파일이 된다', { placeholder: 'title' });
s.addText('사람이 하던 설계 → 해석 → 수정 반복을 AI가 근거와 함께 자동으로 수행', { placeholder: 'body' });
const flow = [
  ['입력', null, '"울퉁불퉁한 길에서도\n폰이 안 흔들리게,\n최대한 가볍게"'],
  ['물리 계산', 'r_base_stress.png', '처음 설계: 진동 기준 미달'],
  ['AI 재설계', 'r_final_stress.png', '필요한 곳에만 재료 배치'],
  ['제작 파일', DRW, 'STL · 도면 + 성능 리포트']];
flow.forEach((f, i) => {
  const x = 0.5 + i * 2.32, y = 1.4, w = 2.0, h = 2.45;
  box(s, x, y, w, h, X.tint, 'step card');
  pill(s, x + 0.15, y + 0.12, 1.0, `${i + 1}. ${f[0]}`, X.teal, X.white);
  if (f[1]) fit(s, f[1].startsWith('/') ? f[1] : SH + f[1], x + 0.1, y + 0.5, w - 0.2, 1.35, f[0]);
  else T(s, f[2], { x: x + 0.15, y: y + 0.6, w: w - 0.3, h: 1.3, fontSize: 13, bold: true, color: C.text2, italic: true, valign: 'middle' });
  if (f[1]) T(s, f[2], { x: x + 0.12, y: y + 1.9, w: w - 0.24, h: 0.45, fontSize: 10, color: C.text1, align: 'center' });
  if (i < 3) arrow(s, x + w + 0.04, y + 1.05, 0.24, 0.32);
});
const kpi = [['−20%', '무게', '50.0 → 39.8 g'], ['3.8배', '1차 진동수', '26.5 → 99.4 Hz'], ['1 mm', '출력 형상 재검증 해상도', '진동·강도 기준 모두 통과']];
kpi.forEach((k, i) => {
  const x = 0.5 + i * 3.1;
  T(s, k[0], { x, y: 4.05, w: 1.35, h: 0.6, fontSize: 28, bold: true, color: C.accent1, valign: 'middle' });
  T(s, k[1], { x: x + 1.4, y: 4.07, w: 1.6, h: 0.3, fontSize: 11, bold: true, color: C.text2 });
  T(s, k[2], { x: x + 1.4, y: 4.37, w: 1.6, h: 0.3, fontSize: 10, color: C.accent3 });
});
T(s, '※ 자전거 폰 거치대 사례, 실제 구조 해석(FEM) 계산값. TV 스탠드 사례 계산 진행 중', { x: 0.5, y: 4.85, w: 9, h: 0.25, fontSize: 9, color: C.accent3 });
s.addNotes('임원이 이 장만 봐도 이해하도록: 왼쪽 요청 문장이 오른쪽 도면이 되기까지 사람이 개입하지 않는다는 것. 3.8배는 1차 고유진동수 비율(99.4/26.5).');

// ---------- 3. 문제 정의
pres.addSection({ title: '1. 문제 정의' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '1. 문제 정의' });
s.addText('1. 문제 정의 — 만들어 보기 전에는 성능을 알 수 없다', { placeholder: 'title' });
s.addText('지금은 전문가의 설계·해석 반복이 필요하고, 범용 AI는 검증 없이 그럴듯한 형상만 준다', { placeholder: 'body' });
// left: current loop
box(s, 0.5, 1.35, 4.35, 3.0, X.tint, 'current process');
T(s, '현재 방식: 시행착오 반복', { x: 0.7, y: 1.47, w: 4, h: 0.3, fontSize: 13, bold: true, color: C.text2 });
const loop = [['아이디어', 1.0, 1.9], ['CAD 설계\n(전문가)', 2.95, 1.9], ['출력·시험', 2.95, 3.1], ['실패·수정', 1.0, 3.1]];
loop.forEach(l => { box(s, l[1], l[2], 1.35, 0.72, 'FFFFFF', 'loop node'); T(s, l[0], { x: l[1], y: l[2], w: 1.35, h: 0.72, fontSize: 11, bold: true, color: C.text2, align: 'center', valign: 'middle' }); });
s.addShape(pres.shapes.RIGHT_ARROW, { x: 2.42, y: 2.12, w: 0.45, h: 0.28, fill: { color: C.accent3 }, line: { color: C.accent3 } });
s.addShape(pres.shapes.DOWN_ARROW, { x: 3.48, y: 2.64, w: 0.28, h: 0.45, fill: { color: C.accent3 }, line: { color: C.accent3 } });
s.addShape(pres.shapes.LEFT_ARROW, { x: 2.42, y: 3.32, w: 0.45, h: 0.28, fill: { color: C.accent5 }, line: { color: C.accent5 } });
s.addShape(pres.shapes.UP_ARROW, { x: 1.54, y: 2.64, w: 0.28, h: 0.45, fill: { color: C.accent5 }, line: { color: C.accent5 } });
T(s, '시간·재료 낭비, 해석 전문 인력 의존', { x: 0.7, y: 4.0, w: 4, h: 0.3, fontSize: 11, color: C.accent5, bold: true });
// right: generic AI
box(s, 5.15, 1.35, 4.35, 3.0, X.tint, 'generic AI');
T(s, '검증 없이 만든 설계: 겉보기엔 멀쩡', { x: 5.35, y: 1.47, w: 4, h: 0.3, fontSize: 13, bold: true, color: C.text2 });
fit(s, SH + 'r_base_stress.png', 5.35, 1.85, 2.2, 1.5, 'plausible but weak design');
T(s, '처음 설계 (응력 분포)', { x: 5.35, y: 3.35, w: 2.2, h: 0.25, fontSize: 10, color: C.accent3, align: 'center' });
const facts = [['26.5 Hz', '1차 진동수 — 자갈길 진동 34.6~45.6 Hz와 가까워 공진 위험'], ['26.4 MPa', '최대 응력 — 허용 26 MPa 초과']];
facts.forEach((f, i) => {
  T(s, f[0], { x: 7.7, y: 1.9 + i * 0.85, w: 1.7, h: 0.35, fontSize: 18, bold: true, color: C.accent5 });
  T(s, f[1], { x: 7.7, y: 2.25 + i * 0.85, w: 1.7, h: 0.5, fontSize: 9, color: C.text1 });
});
T(s, '하중 조건·판정 기준이 없으면 비전문가는 문제를 알 수 없음', { x: 5.35, y: 4.0, w: 4, h: 0.3, fontSize: 11, color: C.accent5, bold: true });
T(s, '※ 진동 대역: ISBS 2020 실측(자전거 프레임), 허용 응력: PETG 항복 39 MPa ÷ 안전계수 1.5. 처음 설계 수치는 우리 FEM 계산값', { x: 0.5, y: 4.55, w: 9, h: 0.5, fontSize: 9, color: C.accent3 });
s.addNotes('문제를 두 가지 그림으로: 사람 쪽은 반복 루프, AI 쪽은 그럴듯하지만 실제로는 기준 미달인 형상. 오른쪽 형상은 처음 설계를 계산한 응력 분포(빨강일수록 응력 큼).');

// ---------- 4. 기술 차별성: 파이프라인
pres.addSection({ title: '2. 기술 차별성' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 기술 차별성 — 생성 · 계산 · 재설계를 검증으로 묶었다', { placeholder: 'title' });
s.addText('각 단계 사이에 자동 검증 관문을 두어, 기준을 통과한 결과만 다음 단계로 넘긴다', { placeholder: 'body' });
const st = [['요청 해석', IC.chat, '말·스케치·사진 → 형상 + 물리 조건\n(표준·문헌 근거, 빠진 조건 질문)'],
  ['3D 생성', IC.cube, '치수 수정 가능한 3D 설계(CAD) 자동 생성'],
  ['성능 확인', IC.shield, '물리 엔진으로 강도·진동·처짐 계산'],
  ['AI 재설계', IC.redo, '3D 미분 기반 최적화로\n필요한 곳에만 재료 배치'],
  ['제작 파일', IC.file, '출력 형상을 다시 계산해\n통과 시 STL·도면 출력']];
st.forEach((t, i) => {
  const x = 0.5 + i * 1.86;
  disc(s, x + 0.45, 1.45, 0.7, i === 2 || i === 3 ? X.amber : X.teal, t[1], 'stage icon');
  T(s, t[0], { x, y: 2.25, w: 1.6, h: 0.32, fontSize: 13, bold: true, color: C.text2, align: 'center' });
  T(s, t[2], { x: x - 0.02, y: 2.6, w: 1.64, h: 0.95, fontSize: 9.5, color: C.text1, align: 'center' });
  if (i < 4) { s.addShape(pres.shapes.DIAMOND, { x: x + 1.55, y: 1.62, w: 0.36, h: 0.36, fill: { color: X.white }, line: { color: C.accent1, width: 1.5 }, objectName: 'gate' });
    T(s, '✓', { x: x + 1.55, y: 1.62, w: 0.36, h: 0.36, fontSize: 11, bold: true, color: C.accent1, align: 'center', valign: 'middle' }); }
});
s.addShape(pres.shapes.LINE, { x: 0.95, y: 3.62, w: 7.45, h: 0, line: { color: X.line, width: 1, dashType: 'dash' } });
// loop-back label between 성능 확인 and 재설계
T(s, '기준 미달 → 재설계 → 다시 확인 (자동 반복)', { x: 4.2, y: 3.45, w: 3.2, h: 0.3, fontSize: 10, bold: true, color: C.accent2, align: 'center', fill: { color: X.white } });
const gate = [['조건 검증', '하중·고정·재료·기준의 근거 확인'], ['계산 검증', '이론해 비교·격자 수렴·이상값 감지'], ['제작 형상 검증', '출력용 형상을 더 촘촘한 격자로 재계산']];
gate.forEach((g, i) => {
  const x = 0.5 + i * 3.05;
  box(s, x, 3.95, 2.85, 1.0, X.tint, 'gate card');
  s.addShape(pres.shapes.DIAMOND, { x: x + 0.15, y: 4.12, w: 0.3, h: 0.3, fill: { color: X.white }, line: { color: C.accent1, width: 1.5 } });
  T(s, g[0], { x: x + 0.55, y: 4.1, w: 2.2, h: 0.32, fontSize: 12, bold: true, color: C.accent1 });
  T(s, g[1], { x: x + 0.55, y: 4.45, w: 2.2, h: 0.4, fontSize: 10, color: C.text1 });
});
s.addNotes('차별점은 개별 기술이 아니라 연결 + 검증 관문. 마름모가 자동 검증 관문. 주황 단계(성능 확인↔재설계)가 물리 기반 AI의 핵심.');

// ---------- 5. 기술 차별성: 비교
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 기술 차별성 — 누구나 쓰면서도, 결과를 믿을 수 있다', { placeholder: 'title' });
s.addText('기존 방식은 "쉬움"과 "신뢰" 중 하나만 제공', { placeholder: 'body' });
const cols = [['범용 AI 3D 생성', '쉽지만 검증 없음', X.tint, C.text2], ['전문가용 해석·최적화 도구', '정확하지만 전문가 전용', X.tint, C.text2], ['FormProof', '쉽고, 검증된 결과', X.teal, C.background1]];
const crit = ['일상 언어·스케치로 입력', '물리 조건을 근거로 자동 설정', '구조 자동 개선(최적화)', '제작 형상까지 자동 재검증', '비전문가 사용'];
const marks = [[1, 0, 0, 0, 1], [0, 0, 1, 0, 0], [1, 1, 1, 1, 1]];
cols.forEach((c, j) => {
  const x = 3.2 + j * 2.12;
  box(s, x, 1.35, 1.95, 0.72, c[2], 'col head');
  T(s, c[0], { x: x + 0.05, y: 1.38, w: 1.85, h: 0.38, fontSize: 11, bold: true, color: c[3], align: 'center', valign: 'middle' });
  T(s, c[1], { x: x + 0.05, y: 1.74, w: 1.85, h: 0.28, fontSize: 9, color: j === 2 ? C.accent4 : C.accent3, align: 'center' });
});
crit.forEach((k, i) => {
  const y = 2.2 + i * 0.52;
  if (i % 2 === 0) s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: y - 0.04, w: 9.0, h: 0.5, fill: { color: 'F7FAF9' }, line: { color: 'F7FAF9' } });
  T(s, k, { x: 0.6, y, w: 2.5, h: 0.42, fontSize: 12, color: C.text2, bold: true, valign: 'middle' });
  marks.forEach((m, j) => { const x = 3.2 + j * 2.12 + 0.8; s.addImage({ data: m[i] ? IC.check : IC.cross, x, y: y + 0.06, w: 0.3, h: 0.3 }); });
});
T(s, '※ 범주 수준의 일반 특성 비교. 특정 상용 제품과의 기능 비교는 확인 필요 (상용 도구 중 일부는 자동 최적화를 제공)', { x: 0.5, y: 4.85, w: 9, h: 0.3, fontSize: 9, color: C.accent3 });
s.addNotes('표 대신 체크/엑스로 한눈에. 전문가 도구는 최적화는 되지만 입력·조건 설정·판정을 사람이 해야 함. 상용 도구 세부 비교는 별도 확인 후 보강.');

// ---------- 6. 실증 결과
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 기술 차별성 — 실제 계산으로 증명: 더 가볍고, 더 단단하게', { placeholder: 'title' });
s.addText('자전거 폰 거치대 · 같은 색 = 같은 응력 (빨강일수록 위험)', { placeholder: 'body' });
box(s, 0.5, 1.3, 4.35, 2.25, X.tint, 'before');
pill(s, 0.65, 1.42, 1.1, '처음 설계', X.mute, X.white);
fit(s, SH + 'r_base_stress.png', 0.65, 1.75, 4.05, 1.72, 'before stress');
box(s, 5.15, 1.3, 4.35, 2.25, X.tint, 'after');
pill(s, 5.3, 1.42, 1.3, 'AI 재설계', X.teal, X.white);
fit(s, SH + 'r_final_stress.png', 5.3, 1.75, 4.05, 1.72, 'after stress');
arrow(s, 4.88, 2.25, 0.25, 0.35);
fit(s, SH + 'r_cbar.png', 3.6, 3.56, 2.8, 0.4, 'stress colorbar (MPa)'); T(s, '응력 (MPa)', { x: 6.45, y: 3.6, w: 1, h: 0.2, fontSize: 8, color: C.accent3 });
// metric bars: value vs criterion
const met = [['무게', 50.0, 39.8, 'g', null, '낮을수록 좋음'], ['1차 진동수', 26.5, 99.4, 'Hz', 91, '기준 ≥ 91 Hz'], ['최대 응력', 26.4, 18.3, 'MPa', 26, '기준 ≤ 26 MPa']];
met.forEach((m, i) => {
  const x = 0.5 + i * 3.05, y = 4.02, W = 2.85, mx = Math.max(m[1], m[2], m[4] || 0) * 1.1;
  T(s, m[0] + '  ' + m[5], { x, y, w: W, h: 0.24, fontSize: 10, bold: true, color: C.text2 });
  [[m[1], X.mute, '처음'], [m[2], X.teal, 'AI']].forEach((b, k) => {
    const by = y + 0.28 + k * 0.27, bw = (W - 0.95) * b[0] / mx;
    T(s, b[2], { x, y: by, w: 0.3, h: 0.22, fontSize: 9, color: C.accent3, valign: 'middle' });
    s.addShape(pres.shapes.RECTANGLE, { x: x + 0.32, y: by + 0.03, w: bw, h: 0.16, fill: { color: b[1] }, line: { color: b[1] } });
    T(s, `${b[0]} ${m[3]}`, { x: x + 0.36 + bw, y: by, w: 0.75, h: 0.22, fontSize: 9, bold: true, color: b[1] === X.teal ? C.accent1 : C.accent3, valign: 'middle' });
  });
  if (m[4]) { const lx = x + 0.32 + (W - 0.95) * m[4] / mx; s.addShape(pres.shapes.LINE, { x: lx, y: y + 0.26, w: 0, h: 0.56, line: { color: X.red, width: 1.25, dashType: 'dash' } }); }
});
T(s, '※ 그림은 설계 격자(2 mm) 응력. 수치는 무게=STL, 진동수·응력=출력 형상 1 mm 재해석, 처음 설계는 설계 격자 계산값. 빨간 점선 = 판정 기준', { x: 0.5, y: 5.0, w: 9, h: 0.25, fontSize: 8, color: C.accent3 });
s.addNotes('같은 색 척도로 비교: 처음 설계는 팔 뿌리에 응력 집중(빨강), 재설계는 하중 경로를 따라 재료가 분산(파랑). 막대의 빨간 점선이 판정 기준. 무게 비교 기준은 처음 설계 50.0 g(클램프 포함).');

// ---------- 7. 사업·조직 기여
pres.addSection({ title: '3. 사업·조직 기여' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '3. 사업·조직 기여' });
s.addText('3. 사업·조직 기여 — DX 부문 제품 개발에 바로 쓰인다', { placeholder: 'title' });
s.addText('구조물·액세서리처럼 "가볍고 튼튼해야 하는" 부품이 있는 모든 사업부가 대상', { placeholder: 'body' });
const bu = [['VD', 'TV · 모니터', IC.tv, 'TV 스탠드·벽걸이 브래킷\n전도 안정성 + 경량화', '시연: TV 스탠드 (진행 중)', X.amber],
  ['MX', '모바일 · 웨어러블', IC.phone, '액세서리·거치대·웨어러블 프레임\n진동·강도·착용 형상', '시연: 자전거 거치대 (완료)', X.teal],
  ['DA', '생활가전', IC.kitchen, '내부 브래킷·지지 구조물\n경량화 + 진동 회피', '적용 후보', X.mute]];
bu.forEach((b, i) => {
  const x = 0.5 + i * 3.05;
  box(s, x, 1.35, 2.85, 2.2, X.tint, 'bu card');
  s.addImage({ data: b[2], x: x + 0.2, y: 1.52, w: 0.55, h: 0.55 });
  T(s, b[0], { x: x + 0.9, y: 1.48, w: 1.8, h: 0.35, fontSize: 18, bold: true, color: C.text2 });
  T(s, b[1], { x: x + 0.9, y: 1.82, w: 1.8, h: 0.28, fontSize: 11, color: C.accent3 });
  T(s, b[3], { x: x + 0.2, y: 2.3, w: 2.5, h: 0.65, fontSize: 11, color: C.text1 });
  pill(s, x + 0.2, 3.07, 2.45, b[4], b[5], X.white);
});
const val = [['시제품 반복 ↓', '출력 전에 성능 확인'], ['재료·물류비 ↓', '기준 안에서 무게 최소화'], ['개발 기간 ↓', '해석 요청·대기 없이 설계자가 직접']];
val.forEach((v, i) => {
  const x = 0.5 + i * 3.05;
  disc(s, x, 3.8, 0.5, X.tint, IC.bolt, 'value icon');
  T(s, v[0], { x: x + 0.62, y: 3.78, w: 2.2, h: 0.3, fontSize: 13, bold: true, color: C.accent1 });
  T(s, v[1], { x: x + 0.62, y: 4.08, w: 2.2, h: 0.3, fontSize: 10, color: C.text1 });
});
T(s, '※ 사업부 적용처는 후보. 정량 효과(반복 횟수·비용·기간)는 파일럿 적용으로 측정 필요 — 확인 필요', { x: 0.5, y: 4.75, w: 9, h: 0.3, fontSize: 9, color: C.accent3 });
s.addNotes('VD·MX는 시연 사례와 직접 연결, DA는 후보. 정량 효과는 근거 수치가 없어 넣지 않음.');

// ---------- 8. 확장성·파급 효과
pres.addSection({ title: '4. 확장성·파급 효과' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '4. 확장성·파급 효과' });
s.addText('4. 확장성·파급 효과 — 같은 엔진에 물리 모듈을 더해 간다', { placeholder: 'title' });
s.addText('하나의 문제 풀이가 아니라, 설계할 때마다 데이터가 쌓여 더 빨라지는 플랫폼', { placeholder: 'body' });
const steps = [['해커톤', '구조 · 진동', '거치대 · TV 스탠드', IC.cogs], ['단기', '+ 열', '방열 구조 · 구조-열 동시 설계', IC.heat], ['중기', '+ 광학', '물리 AI(PINN) 기반 광학 역설계', IC.bulb], ['장기', '사내 설계 플랫폼', '전 사업부 공용, 누적 데이터로 가속', IC.db]];
steps.forEach((t, i) => {
  const x = 0.5 + i * 2.3, y = 3.05 - i * 0.48, h = 1.25 + i * 0.48;
  s.addShape(pres.shapes.RECTANGLE, { x, y, w: 2.15, h, fill: { color: [X.line, 'A9CFCB', '5FA8A8', X.teal][i] }, line: { color: X.white }, objectName: 'stair' });
  s.addImage({ data: t[3], x: x + 0.15, y: y + 0.15, w: 0.38, h: 0.38 });
  T(s, t[0], { x: x + 0.62, y: y + 0.12, w: 1.45, h: 0.25, fontSize: 10, bold: true, color: i === 3 ? C.background1 : C.text2 });
  T(s, t[1], { x: x + 0.62, y: y + 0.36, w: 1.45, h: 0.3, fontSize: 13, bold: true, color: i === 3 ? C.background1 : C.text2 });
  T(s, t[2], { x: x + 0.15, y: y + 0.72, w: 1.9, h: 0.5, fontSize: 10, color: i === 3 ? C.background1 : C.text1 });
});
T(s, '파급 효과', { x: 0.5, y: 1.35, w: 2, h: 0.3, fontSize: 13, bold: true, color: C.accent1 });
T(s, [{ text: '생성형 AI 결과에 물리 검증을 붙이는 방식 — 다른 생성형 AI 과제에도 재사용', options: { bullet: { indent: 12 }, breakLine: true } },
      { text: '설계 결과가 쌓일수록 물리 AI 가속 모델이 정확해져 계산 시간 단축', options: { bullet: { indent: 12 } } }],
  { x: 0.5, y: 1.65, w: 4.6, h: 0.8, fontSize: 11, color: C.text1, paraSpaceAfter: 4 });
s.addNotes('계단: 물리 분야를 하나씩 추가. 광학은 디스플레이 광학 역설계(PINN) 경험과 연결 가능. 장기에는 사업부 공용 설계 플랫폼.');

// ---------- 9. 마무리
pres.addSection({ title: '마무리' });
s = pres.addSlide({ masterName: 'DARK', sectionTitle: '마무리' });
T(s, '형상을\n성능으로 증명한다', { x: 0.6, y: 1.5, w: 5.0, h: 1.4, fontSize: 32, bold: true, color: C.background1 });
T(s, '비전문가의 아이디어를, 검증된 제작 파일로', { x: 0.6, y: 3.05, w: 5.0, h: 0.4, fontSize: 16, color: C.accent4 });
box(s, 5.9, 1.1, 3.7, 3.2, 'FFFFFF', 'final card');
fit(s, SH + 'r_final_stl.png', 6.05, 1.3, 3.4, 2.8, 'final design');

await pres.writeFile({ fileName: OUT });
await applyTheme(OUT, THEME);
console.log('ok', OUT);
})();
