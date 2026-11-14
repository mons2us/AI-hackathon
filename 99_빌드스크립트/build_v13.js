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
const BK = JSON.parse(fs.readFileSync(__dirname + '/bike_v13.json','utf8'));
const pct = v => Math.round(v);
const IC = {
  tv: await icon(fa.FaTv, X.teal), phone: await icon(fa.FaMobileAlt, X.teal), kitchen: await icon(md.MdKitchen, X.teal),
  chat: await icon(fa.FaCommentDots, X.white), cube: await icon(fa.FaCube, X.white), shield: await icon(fa.FaShieldAlt, X.white),
  redo: await icon(fa.FaRedoAlt, X.white), file: await icon(fa.FaFileExport, X.white), check: await icon(fa.FaCheck, X.green),
  cross: await icon(fa.FaTimes, X.red), bolt: await icon(fa.FaBolt, X.teal), user: await icon(fa.FaUserTie, X.teal),
  db: await icon(fa.FaDatabase, X.teal), heat: await icon(fa.FaThermometerHalf, X.teal), bulb: await icon(fa.FaLightbulb, X.amber),
  cogs: await icon(fa.FaCogs, X.teal), shieldT: await icon(fa.FaShieldAlt, X.teal),
  mic: await icon(fa.FaMicrophone, X.teal), pen: await icon(fa.FaPencilAlt, X.teal), cam: await icon(fa.FaCamera, X.teal),
  doc: await icon(fa.FaFilePowerpoint, X.teal), pat: await icon(fa.FaLightbulb, X.teal), step: await icon(fa.FaCube, X.teal),
  part: await icon(fa.FaMinusCircle, X.amber), spec: await icon(fa.FaClipboardList, X.white),
};

const pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = 'FormProof 발표 초안 v13';
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
s.addText('말·스케치·사진·문서·3D 파일,\n어떤 아이디어든 성능이 확인된 3D 설계로', { placeholder: 'body' });
T(s, '물리 기반 생성형 AI  ·  팀원 A · B · C', { x: 0.6, y: 4.6, w: 5, h: 0.3, fontSize: 11, color: C.accent4 });
box(s, 5.9, 0.9, 3.7, 3.8, 'FFFFFF', 'hero card');
fit(s, SH + BK.rider, 6.0, 1.0, 3.5, 2.75, 'optimized phone mount on bicycle');
T(s, '자전거 폰 거치대 — AI가 설계한 구조', { x: 6.05, y: 3.85, w: 3.4, h: 0.3, fontSize: 11, bold: true, color: C.text2, align: 'center' });
T(s, `진동수 ${(BK.ai_f/BK.base_f).toFixed(1)}배 · 진동·충격 기준 통과`, { x: 6.05, y: 4.15, w: 3.4, h: 0.3, fontSize: 10, color: C.accent1, align: 'center' });
s.addNotes('FormProof = Form + Proof. 형상을 성능으로 증명한다. 오른쪽은 실제 계산으로 얻은 거치대 형상(출력용 STL).');

// ---------- 2. 한 장 요약
pres.addSection({ title: '요약' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '요약' });
s.addText('한 장 요약 — 어떤 형태의 아이디어든 검증된 제작 파일이 된다', { placeholder: 'title' });
s.addText('사람이 하던 설계 → 해석 → 수정 반복을 AI가 근거와 함께 자동으로 수행', { placeholder: 'body' });
const flow = [
  ['입력', null, '"울퉁불퉁한 길에서도\n폰이 안 흔들리게,\n최대한 가볍게"'],
  ['물리 계산', 'v6_c_bike_base_stress.png', '처음 설계: 응력 집중·진동 기준 미달'],
  ['AI 재설계', BK.ai_img, '필요한 곳에만 재료 배치'],
  ['장착·제작', BK.rider, 'STL · 도면 출력, 자전거에 장착']];
flow.forEach((f, i) => {
  const x = 0.5 + i * 2.32, y = 1.4, w = 2.0, h = 2.45;
  box(s, x, y, w, h, X.tint, 'step card');
  pill(s, x + 0.15, y + 0.12, 1.0, `${i + 1}. ${f[0]}`, X.teal, X.white);
  if (f[1]) fit(s, f[1].startsWith('/') ? f[1] : SH + f[1], x + 0.1, y + 0.5, w - 0.2, 1.35, f[0]);
  else { const ins = [[IC.mic, '말·글'], [IC.pen, '스케치'], [IC.cam, '사진'], [IC.doc, '문서'], [IC.pat, '특허'], [IC.step, '3D 파일']];
    ins.forEach((q, k) => { const cx = x + 0.12 + (k % 2) * 0.9, cy = y + 0.55 + Math.floor(k / 2) * 0.48;
      s.addImage({ data: q[0], x: cx, y: cy + 0.06, w: 0.26, h: 0.26 }); T(s, q[1], { x: cx + 0.3, y: cy, w: 0.62, h: 0.4, fontSize: 9, bold: true, color: C.text2, valign: 'middle' }); });
    T(s, '예: 스케치 + "울퉁불퉁한 길에서도 안 흔들리게"', { x: x + 0.12, y: y + 1.95, w: w - 0.24, h: 0.42, fontSize: 9, color: C.accent3, align: 'center' }); }
  if (f[1]) T(s, f[2], { x: x + 0.12, y: y + 1.9, w: w - 0.24, h: 0.45, fontSize: 10, color: C.text1, align: 'center' });
  if (i < 3) arrow(s, x + w + 0.04, y + 1.05, 0.24, 0.32);
});
const kpi = [['기준 통과', '진동·충격 강도', `처음 설계는 둘 다 미달`], [`${(BK.ai_f/BK.base_f).toFixed(1)}배`, '1차 진동수', `${BK.base_f} → ${BK.ai_f} Hz`], ['3 / 3', 'LLM 단독 설계', '근거 기준 미달 — FormProof만 통과']];
kpi.forEach((k, i) => {
  const x = 0.5 + i * 3.1;
  T(s, k[0], { x, y: 4.05, w: 1.35, h: 0.6, fontSize: 28, bold: true, color: C.accent1, valign: 'middle' });
  T(s, k[1], { x: x + 1.4, y: 4.07, w: 1.6, h: 0.3, fontSize: 11, bold: true, color: C.text2 });
  T(s, k[2], { x: x + 1.4, y: 4.37, w: 1.6, h: 0.3, fontSize: 10, color: C.accent3 });
});
T(s, '※ 자전거 폰 거치대, 출력 형상 1 mm 구조 해석(폰 갤럭시 S26 울트라 + 거치부 254 g). LLM 단독 = 도구 없는 독립 세션 3회, 같은 해석기로 판정', { x: 0.5, y: 4.85, w: 9, h: 0.25, fontSize: 9, color: C.accent3 });
s.addNotes('입력이 어떤 형태든 검증된 제작 파일까지. 진동수 배율은 1차 고유진동수 비율. 3/3은 범용 LLM 단독 설계 3건이 근거 기준(91 Hz)에 모두 미달했다는 뜻.');

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
fit(s, SH + 'v6_c_bike_base_stress.png', 5.3, 1.8, 2.3, 1.45, 'plausible but weak design');
T(s, '처음 설계 (응력 분포)', { x: 5.35, y: 3.5, w: 2.2, h: 0.25, fontSize: 10, color: C.accent3, align: 'center' });
const facts = [[`${BK.base_f} Hz`, '1차 진동수 — 자갈길 진동 34.6~45.6 Hz와 가까워 공진 위험'], [`${BK.base_s} MPa`, '충격 시 응력 — 허용 26 MPa 초과']];
facts.forEach((f, i) => {
  T(s, f[0], { x: 7.7, y: 1.9 + i * 0.85, w: 1.7, h: 0.35, fontSize: 18, bold: true, color: C.accent5 });
  T(s, f[1], { x: 7.7, y: 2.25 + i * 0.85, w: 1.7, h: 0.5, fontSize: 9, color: C.text1 });
});
T(s, '하중 조건·판정 기준이 없으면 비전문가는 문제를 알 수 없음', { x: 5.35, y: 4.0, w: 4, h: 0.3, fontSize: 11, color: C.accent5, bold: true });
T(s, '※ 진동 대역: ISBS 2020 실측(자전거 프레임), 허용 응력: PETG 항복 39 MPa ÷ 안전계수 1.5. 처음 설계 수치는 우리 FEM 계산값', { x: 0.5, y: 4.55, w: 9, h: 0.5, fontSize: 9, color: C.accent3 });
s.addNotes('문제를 두 가지 그림으로: 사람 쪽은 반복 루프, AI 쪽은 그럴듯하지만 실제로는 기준 미달인 형상. 오른쪽 형상은 처음 설계를 계산한 응력 분포(빨강일수록 응력 큼).');

// ---------- 5. 기술 차별성: 비교
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '1. 문제 정의' });
s.addText('1. 기존 방식의 한계 — 쉬움과 신뢰 중 하나만 준다', { placeholder: 'title' });
s.addText('기존 방식은 "쉬움"과 "신뢰" 중 하나만 제공', { placeholder: 'body' });
const cols = [['범용 AI 3D 생성', '쉽지만 검증 없음', X.tint, C.text2], ['전문가용 해석·최적화 도구', '정확하지만 전문가 전용', X.tint, C.text2], ['FormProof', '쉽고, 검증된 결과', X.teal, C.background1]];
const crit = ['다양한 입력 (말·사진·문서·3D)', '물리 조건을 근거로 자동 설정', '구조 자동 개선(최적화)', '제작 형상까지 자동 재검증', '비전문가 사용'];
const marks = [[2, 0, 0, 0, 1], [2, 0, 1, 0, 0], [1, 1, 1, 1, 1]];
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
  marks.forEach((m, j) => { const x = 3.2 + j * 2.12 + 0.8; s.addImage({ data: m[i] === 2 ? IC.part : m[i] ? IC.check : IC.cross, x, y: y + 0.06, w: 0.3, h: 0.3 }); });
});
T(s, '※ 범주 수준의 일반 비교 (주황 = 일부 지원: 범용 AI는 텍스트·이미지, 전문가 도구는 CAD 파일 중심). 특정 상용 제품 비교는 확인 필요', { x: 0.5, y: 4.85, w: 9, h: 0.3, fontSize: 9, color: C.accent3 });
s.addNotes('표 대신 체크/엑스로 한눈에. 전문가 도구는 최적화는 되지만 입력·조건 설정·판정을 사람이 해야 함. 상용 도구 세부 비교는 별도 확인 후 보강.');

// ---------- 4. 기술 차별성: 파이프라인
pres.addSection({ title: '2. 기술 차별성' });
// ===== v7: 프레임워크 아키텍처
const IC2 = {
  robot: await icon(fa.FaRobot, X.white), shape: await icon(fa.FaDraftingCompass, X.teal), atom: await icon(fa.FaAtom, X.teal),
  opt: await icon(fa.FaChartLine, X.teal), ver: await icon(fa.FaClipboardCheck, X.teal), stl: await icon(fa.FaCube, X.teal),
  drw: await icon(fa.FaRulerCombined, X.teal), rep: await icon(fa.FaFileAlt, X.teal), img: await icon(fa.FaImage, X.teal),
  book: await icon(fa.FaBook, X.amber), x: await icon(fa.FaTimesCircle, X.red), ok: await icon(fa.FaCheckCircle, X.green),
};
// ===== v9: 파이프라인 — 생성 AI × 물리 AI
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 기술 차별성 — FormProof 파이프라인: 생성 AI × 물리 AI', { placeholder: 'title' });
s.addText('LLM은 이해 · 생성 · 판정을 맡고, 최적화는 물리 AI(빠른 탐색)와 수치해석(정밀화)이 맡는다', { placeholder: 'body' });
const ST = { pre: ['사전 검증', X.green], hk: ['해커톤', X.amber], fut: ['개발 예정', '6B5CA5'], ref: ['기존 연구', X.mute] };
const tag = (x, y, k, w) => { const [t, c] = ST[k]; w = w || (t.length > 3 ? 0.62 : 0.5);
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x - w, y: y - 0.09, w, h: 0.18, rectRadius: 0.09, fill: { color: c }, line: { color: c }, objectName: 'tag' });
  T(s, t, { x: x - w, y: y - 0.09, w, h: 0.18, fontSize: 6.5, bold: true, color: 'FFFFFF', align: 'center', valign: 'middle' }); };
const node = (x, y, w, h, title, sub, k, o = {}) => {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.05, fill: { color: o.fill || 'FFFFFF' }, line: { color: o.line || X.line, width: o.lw || 1 }, objectName: 'node ' + title });
  T(s, title, { x: x + 0.08, y: y + 0.06, w: w - 0.14, h: 0.24, fontSize: o.fs || 9.5, bold: true, color: o.tc || C.text2 });
  if (o.kind) T(s, o.kind, { x: x + 0.08, y: y + 0.29, w: w - 0.14, h: 0.18, fontSize: 7, bold: true, color: o.kc || C.accent1 });
  if (sub) T(s, sub, { x: x + 0.08, y: y + (o.kind ? 0.47 : 0.3), w: w - 0.14, h: h - (o.kind ? 0.5 : 0.33), fontSize: 7.5, color: o.sc || C.accent3 });
  if (k) tag(x + w - 0.05, o.tb ? y + h : y, k);
};
const conn = (x1, y1, x2, y2, o = {}) => s.addShape(pres.shapes.LINE, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.max(Math.abs(x2 - x1), 0.001), h: Math.max(Math.abs(y2 - y1), 0.001),
  flipH: x2 < x1, flipV: y2 < y1, line: { color: o.c || X.teal, width: o.w || 1.5, dashType: o.dash || 'solid', endArrowType: 'triangle' }, objectName: 'flow' });
const stage = (x, w, t, c) => T(s, t, { x, y: 1.22, w, h: 0.2, fontSize: 8.5, bold: true, color: c || C.accent3 });
const GEN = '6B4FA0';   // 생성 AI 색
// 1 입력
stage(0.4, 1.25, '1 · 입력');
node(0.4, 1.47, 1.25, 1.2, '요청 · 자료', '텍스트 · 음성 · 스케치 · 이미지 · 문서 · 특허 · STEP', null);
// legend: 역할 구분
const NUM = '5B6B78';
[[GEN, '생성 AI', '이해 · 생성 (LLM · 형상 AI)'], [X.teal, '물리 AI', '성능 예측 · 빠른 탐색'], [NUM, '수치해석', '정밀 최적화 · 최종 판정']].forEach((l, i) => { const y = 2.92 + i * 0.4;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.4, y, w: 0.62, h: 0.2, rectRadius: 0.1, fill: { color: l[0] }, line: { color: l[0] } });
  T(s, l[1], { x: 0.4, y, w: 0.62, h: 0.2, fontSize: 7, bold: true, color: 'FFFFFF', align: 'center', valign: 'middle' });
  T(s, l[2], { x: 0.4, y: y + 0.2, w: 1.4, h: 0.18, fontSize: 6.5, color: C.accent3 }); });
// 2 생성 AI 패널
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 1.85, y: 1.2, w: 2.4, h: 2.98, rectRadius: 0.08, fill: { color: 'F1ECF8' }, line: { color: GEN, width: 1.5 }, objectName: 'gen panel' });
T(s, '2 · 생성 AI — 형상 + 조건', { x: 1.97, y: 1.25, w: 2.2, h: 0.22, fontSize: 9.5, bold: true, color: GEN });
node(1.97, 1.52, 2.16, 0.8, '설계 명세', '요구 → 하중 · 기준 · 재료, 항목별 출처', null, { kind: '생성형 AI (LLM)', kc: GEN });
node(1.97, 2.42, 2.16, 0.8, 'CAD 형상', '고정 부품 · 설계 공간, 치수 수정 가능', null, { kind: 'LLM → 형상 코드', kc: GEN });
node(1.97, 3.32, 2.16, 0.78, '형상 AI', '형상 잠재 공간에서 후보 생성 · 보간', null, { kind: 'DeepSDF 방식 생성 모델', kc: GEN });
conn(1.65, 1.92, 1.97, 1.92); conn(3.05, 2.32, 3.05, 2.42, { c: GEN }); conn(3.05, 3.22, 3.05, 3.32, { c: GEN });
// 3 물리 AI 패널
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 4.68, y: 1.2, w: 2.62, h: 2.98, rectRadius: 0.08, fill: { color: X.ink }, line: { color: X.ink }, objectName: 'phys panel' });
T(s, '3 · 물리 AI — 성능 예측 ⇄ 재설계', { x: 4.8, y: 1.25, w: 2.4, h: 0.22, fontSize: 9.5, bold: true, color: C.accent4 });
node(4.8, 1.52, 2.38, 0.8, '물리 AI 대리 모델', '형상 → 진동 · 응력을 0.2초에 예측', null, { kind: '3D 합성곱 신경망' });
node(4.8, 2.42, 2.38, 0.8, '잠재 공간 최적화', '형상 AI 변수를 물리 AI 미분으로 조정 → 약 40초 후보', null, { kind: '형상 AI × 물리 AI' });
node(4.8, 3.32, 2.38, 0.78, '자유 형상 정밀화', '3D 위상 최적화 + 제조 제약 (출력 방향 · 고정 외곽)', null, { kind: '수치해석 · 위상 최적화 (FEM 미분)', kc: NUM });
conn(5.99, 2.32, 5.99, 2.42, { c: '8FB8B6' }); conn(5.99, 3.22, 5.99, 3.32, { c: '8FB8B6' });
// 생성 → 물리: 후보 형상 / 물리 → 생성: 형상 수정
conn(4.25, 3.75, 4.8, 3.75, { w: 2.25 });
conn(4.13, 3.4, 4.8, 1.95, { c: GEN });
conn(4.8, 2.9, 4.13, 3.7, { c: X.amber, dash: 'dash' });
T(s, '후보\n형상', { x: 4.25, y: 1.62, w: 0.4, h: 0.4, fontSize: 6.5, bold: true, color: GEN, align: 'center' });
T(s, '설계 공간', { x: 4.27, y: 3.8, w: 0.4, h: 0.3, fontSize: 6.5, bold: true, color: C.accent1, align: 'center' });
T(s, '형상 수정', { x: 4.3, y: 3.47, w: 0.48, h: 0.18, fontSize: 6.5, bold: true, color: C.accent2, align: 'center' });
// 4 판정 · 결과
stage(7.5, 2.1, '4 · 판정 · 결과');
node(7.5, 1.47, 2.1, 0.85, '기준 수치해석 판정', '출력 형상을 1 mm 격자로 재해석 · 기준 대비 합격', null, { kind: '수치해석 (FEM)', kc: NUM });
node(7.5, 2.5, 2.1, 0.6, '제작 파일', 'STL · STEP · 도면', null);
node(7.5, 3.28, 2.1, 0.6, '근거 리포트', '성능 · 조건 출처 · 미확인 항목 표시', null);
conn(7.18, 3.6, 7.5, 1.9, { w: 2.25 }); conn(8.55, 2.32, 8.55, 2.5); conn(8.55, 3.1, 8.55, 3.28);
s.addShape(pres.shapes.LINE, { x: 9.68, y: 1.9, w: 0, h: 2.3, line: { color: X.amber, width: 1.25, dashType: 'dash' }, objectName: 'fail v' });
s.addShape(pres.shapes.LINE, { x: 9.6, y: 1.9, w: 0.08, h: 0, line: { color: X.amber, width: 1.25, dashType: 'dash' } });
T(s, '불합격 → 3단계로', { x: 7.5, y: 3.95, w: 2.1, h: 0.2, fontSize: 7.5, bold: true, color: C.accent2, align: 'right' });
s.addShape(pres.shapes.LINE, { x: 7.3, y: 4.2, w: 2.38, h: 0, line: { color: X.amber, width: 1.25, dashType: 'dash' } });
conn(7.3, 4.2, 7.3, 4.12, { c: X.amber, dash: 'dash', w: 1.25 });
// 공통 모듈
const cm3 = [['LLM 에이전트', '단계별 도구 실행 · 결과 판정 · 재설계 지시'], ['근거 DB', '규격 · 측정 논문 · 재료 데이터시트 · 제품 분해 자료'], ['자동 검증 관문', '모든 단계 결과를 코드로 판정']];
cm3.forEach((c, i) => { node(0.4 + i * 3.08, 4.32, 3.0, 0.42, c[0], '', null, { fill: X.tint, line: X.tint }); T(s, c[1], { x: 0.4 + i * 3.08 + 1.1, y: 4.38, w: 1.85, h: 0.3, fontSize: 7.5, color: C.accent3, valign: 'middle' }); });
node(0.4, 4.82, 9.2, 0.38, '물리 모듈 라이브러리', '', null, { fill: X.tint, line: X.tint });
T(s, [{ text: '구조 · 진동 · 열 · 제조 제약 (출력 방향 · 최소 두께 · 고정 외곽)', options: { bold: true, color: C.text2 } }, { text: '   →  다음: 광학 PINN · 유동 · 전자기', options: { color: C.accent3 } }], { x: 2.0, y: 4.87, w: 7.4, h: 0.28, fontSize: 8, valign: 'middle' });
s.addNotes('역할 분담: LLM은 요청 이해 · 설계 명세 · 형상 코드 생성 · 도구 실행 · 판정(계산은 하지 않음). 형상 AI(DeepSDF)가 후보 형상을 만들고, 물리 AI(신경 연산자)가 성능과 미분을 수 초에 내서 잠재 공간에서 빠르게 탐색. 고른 후보는 FEM 미분 기반 위상 최적화로 자유 형상을 정밀화하고, 출력 형상을 FEM으로 재해석해 기준 통과 시에만 제작 파일로 출력.');

// ---------- 2b. 입력
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 입력 → 설계 명세 — 어떤 형태의 아이디어든 같은 형식으로', { placeholder: 'title' });
s.addText('말 한마디부터 특허 아이디어 문서, 기존 제품의 3D 파일까지 같은 과정으로 이어진다', { placeholder: 'body' });
const inp = [[IC.mic, '말 · 텍스트', '"안 흔들리게, 가볍게"', '목표 · 사용 조건'],
  [IC.pen, '스케치', '손그림 한 장', '형태 · 부품 배치'],
  [IC.cam, '사진', '실물 · 사용 환경 사진', '형상 · 치수 추출'],
  [IC.doc, '문서 · PPT', '기획서 · 요구 사양서', '사양 · 제약 조건'],
  [IC.pat, '특허 아이디어', '발명 신고서 · 청구항 · 도면', '구조 · 기능 요구'],
  [IC.step, '3D 파일 (STEP)', '기존 제품 설계 파일', '기존 제품 보강 · 경량화']];
inp.forEach((q, k) => {
  const x = 0.5 + (k % 2) * 2.62, y = 1.3 + Math.floor(k / 2) * 1.08, w = 2.5, h = 0.96;
  box(s, x, y, w, h, X.tint, 'input tile');
  disc(s, x + 0.12, y + 0.18, 0.6, X.white, null, 'input disc'); s.addImage({ data: q[0], x: x + 0.27, y: y + 0.33, w: 0.3, h: 0.3 });
  T(s, q[1], { x: x + 0.82, y: y + 0.1, w: 1.6, h: 0.28, fontSize: 12, bold: true, color: C.text2 });
  T(s, q[2], { x: x + 0.82, y: y + 0.38, w: 1.62, h: 0.26, fontSize: 9, color: C.accent3 });
  T(s, '→ ' + q[3], { x: x + 0.82, y: y + 0.63, w: 1.62, h: 0.26, fontSize: 9.5, bold: true, color: C.accent1 });
});
arrow(s, 5.8, 2.55, 0.4, 0.5);
box(s, 6.35, 1.3, 3.15, 3.12, X.ink, 'spec card');
disc(s, 6.5, 1.42, 0.5, X.teal, IC.spec, 'spec icon');
T(s, '설계 명세', { x: 7.1, y: 1.45, w: 2.3, h: 0.45, fontSize: 16, bold: true, color: C.background1, valign: 'middle' });
const spec = [['형상', '지킬 곳 · 비울 곳 · 바꿀 곳'], ['물리 조건', '하중 · 고정 위치 · 재료'], ['판정 기준', '강도 · 진동 · 처짐 + 출처'], ['빠진 조건', 'AI가 사용자에게 질문']];
spec.forEach((q, i) => {
  const y = 2.1 + i * 0.56;
  T(s, q[0], { x: 6.55, y, w: 1.0, h: 0.45, fontSize: 11, bold: true, color: C.accent2, valign: 'middle' });
  T(s, q[1], { x: 7.55, y, w: 1.9, h: 0.45, fontSize: 10.5, color: C.background1, valign: 'middle' });
});
T(s, '※ 시연 사례 입력: 자전거 거치대 = 스케치 + 텍스트, TV 스탠드 = 텍스트', { x: 0.5, y: 4.6, w: 9, h: 0.3, fontSize: 9, color: C.accent3 });
s.addNotes('핵심: 텍스트 전용이 아니다. 어떤 형태의 입력이든 "설계 명세"(형상 + 물리 조건 + 판정 기준 + 근거)라는 공통 형식으로 바꾸면, 그 뒤 계산·재설계·검증은 동일하다. 특허 아이디어 문서는 청구항·도면에서 구조와 기능 요구를 읽어 형상 후보로 만든다. 입력 해석은 해커톤에서 개발.');

// ===== v11: 생성 AI × 물리 AI 실제 학습 결과
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
const AI = JSON.parse(fs.readFileSync(__dirname + '/ai_v11.json', 'utf8'));
s.addText('2. 생성 AI × 물리 AI — 거치대 계열로 실제 학습한 결과', { placeholder: 'title' });
s.addText(`두 AI가 약 ${AI.search_s}초 만에 데이터보다 ${Math.round((1 - AI.cand_m / AI.start_m) * 100)}% 가벼운 후보를 찾고, 정밀화와 최종 판정은 수치해석이 맡는다`, { placeholder: 'body' });
const CW = 2.9, cardY = 1.28, cardH = 2.62;
const card = (i, t, kind, kc) => { const x = 0.5 + i * (CW + 0.15); box(s, x, cardY, CW, cardH, X.tint, 'ai card');
  T(s, t, { x: x + 0.12, y: cardY + 0.07, w: CW - 0.24, h: 0.26, fontSize: 11, bold: true, color: C.text2 });
  T(s, kind, { x: x + 0.12, y: cardY + 0.33, w: CW - 0.24, h: 0.2, fontSize: 8, bold: true, color: kc }); return x; };
let cx = card(0, '① 형상 AI — 형상을 잠재 변수로', 'DeepSDF 방식 생성 모델', GEN);
['v11_c_D1.png', 'v11_c_D0.png', 'v11_c_D474.png'].forEach((f, k) => fit(s, SH + f, cx + 0.08 + k * 0.92, cardY + 0.6, 0.9, 0.75, 'sample'));
T(s, [{ text: `거치대 계열 형상 ${AI.n_data}개`, options: { bold: true, breakLine: true } }, { text: '각 형상을 FEM으로 계산해 학습 데이터로 사용', options: { color: C.accent3, breakLine: true } }, { text: '잠재 변수 16개로 형상 표현 · 보간', options: { bold: true, breakLine: true } }, { text: `학습 형상 재구성 IoU ${AI.iou}`, options: { color: C.accent3 } }], { x: cx + 0.12, y: cardY + 1.45, w: CW - 0.24, h: 1.1, fontSize: 9, color: C.text1, paraSpaceAfter: 2 });
cx = card(1, '② 물리 AI — 형상 → 1차 진동수', '3D 합성곱 신경망', C.accent1);
s.addChart(pres.charts.SCATTER, [{ name: 'FEM', values: AI.scat_t }, { name: '물리 AI 예측', values: AI.scat_p }, { name: '일치선', values: AI.scat_t }], {
  x: cx + 0.02, y: cardY + 0.52, w: CW - 0.04, h: 1.42, chartColors: [X.teal, X.mute], lineSize: 0, lineDataSymbolSize: 4, showLegend: false,
  valAxisMinVal: 0, valAxisMaxVal: 180, catAxisMinVal: 0, catAxisMaxVal: 180, valAxisLabelFontSize: 7, catAxisLabelFontSize: 7, valAxisLabelColor: X.mute, catAxisLabelColor: X.mute,
  valAxisLabelFontFace: '+mn-lt', catAxisLabelFontFace: '+mn-lt', valGridLine: { color: 'DDE5E4', size: 0.5 }, catGridLine: { style: 'none' },
  showValAxisTitle: true, valAxisTitle: '예측 (Hz)', valAxisTitleFontSize: 7, valAxisTitleColor: X.mute, showCatAxisTitle: true, catAxisTitle: 'FEM (Hz)', catAxisTitleFontSize: 7, catAxisTitleColor: X.mute });
T(s, [{ text: `오차 평균 ${AI.err50}%`, options: { bold: true, color: C.accent1, fontSize: 12 } }, { text: `  ≥ 50 Hz 구간 ${AI.test_n50}개`, options: { color: C.accent3 } }], { x: cx + 0.12, y: cardY + 1.98, w: CW - 0.24, h: 0.26, fontSize: 8.5, valign: 'middle' });
T(s, `1회 예측 약 ${AI.infer_s}초 (같은 형상 FEM 약 2초)`, { x: cx + 0.12, y: cardY + 2.26, w: CW - 0.24, h: 0.24, fontSize: 8.5, color: C.text1 });
cx = card(2, '③ 잠재 공간 탐색 — 형상 AI × 물리 AI', '미분으로 잠재 변수 조정', C.accent1);
fit(s, SH + 'v11_c_C1.png', cx + 0.1, cardY + 0.58, 1.3, 0.95, 'candidate');
T(s, [{ text: `${AI.start_m} → ${AI.cand_m} g`, options: { bold: true, color: GEN, fontSize: 13, breakLine: true } }, { text: '데이터 최선 → AI 후보', options: { color: C.accent3, fontSize: 8 } }], { x: cx + 1.45, y: cardY + 0.68, w: 1.4, h: 0.7 });
T(s, [{ text: `예측 ${AI.pred_f} Hz · FEM ${AI.fem_f} Hz`, options: { bold: true, breakLine: true } }, { text: `후보 1개 약 ${AI.search_s}초 · ${AI.ncand}개 중 ${AI.npass}개 FEM 통과`, options: { breakLine: true } }, { text: '(진동 기준 91 Hz)', options: { color: C.accent3 } }], { x: cx + 0.12, y: cardY + 1.62, w: CW - 0.24, h: 0.9, fontSize: 9, color: C.text1 });
// flow strip
const FL = [[`데이터 최선`, `${AI.start_m} g`, X.mute], [`AI 탐색 후보 (${AI.search_s}초)`, `${AI.cand_m} g · ${AI.fem_f} Hz`, GEN], ['출력 형상 재검증', `${AI.cand_out_f} Hz → 미달`, X.red], ['자유 형상 정밀화 (약 25분)', `${BK.ai_m} g · ${BK.ai_f} Hz 통과`, X.green]];
FL.forEach((f, i) => { const x = 0.5 + i * 2.32;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 4.02, w: 2.05, h: 0.62, rectRadius: 0.06, fill: { color: 'FFFFFF' }, line: { color: f[2], width: 1.5 }, objectName: 'flow box' });
  T(s, f[0], { x: x + 0.08, y: 4.06, w: 1.9, h: 0.24, fontSize: 8.5, color: C.accent3, align: 'center' });
  T(s, f[1], { x: x + 0.08, y: 4.3, w: 1.9, h: 0.3, fontSize: 11, bold: true, color: f[2], align: 'center' });
  if (i < 3) arrow(s, x + 2.08, 4.2, 0.2, 0.26); });
T(s, '※ CPU 2코어 · GPU 없음. 탐색 단계 질량 · 진동수는 2 mm 격자 FEM(폰+거치부 250 g), 최종 설계는 출력 형상 1 mm 재해석(254 g). 정밀화는 같은 조건의 3D 위상 최적화(출력 방향 제약)로 별도 실행', { x: 0.5, y: 4.72, w: 9, h: 0.4, fontSize: 7.5, color: C.accent3 });
s.addNotes('형상 AI는 거치대 계열 형상을 잠재 변수 16개로 압축하고, 물리 AI는 형상에서 1차 진동수를 0.2초에 예측한다(사용 구간 오차 평균 약 7%). 둘을 이어 잠재 변수를 미분으로 조정하면 데이터에 있던 가장 가벼운 합격 설계보다 11% 가벼운 후보가 약 40초에 나온다. 다만 출력 형상으로 다시 계산하면 86 Hz로 미달이라, 자유 형상 정밀화가 41.7 g · 93.7 Hz로 마무리한다. AI는 빠른 탐색, 판정은 수치해석.');
// ===== v7: 검증 관문이 걸러낸 사례
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 기술 차별성 — 그럴듯한 형상을 검증이 걸러낸다', { placeholder: 'title' });
s.addText('이번 사례 작업 중 실제로 불합격 처리되어 다시 설계한 결과 3건', { placeholder: 'body' });
const fails = [
  ['자전거 거치대', '폭 20 mm 압출형 최적화', '출력 형상 재해석\n1차 진동 85 Hz < 기준 91 Hz', '3D 자유 형상으로 재설계\n→ 95.9 Hz 통과'],
  ['TV 스탠드 다리', '3D 격자 위상최적화', '격자보다 가는 부재 · 중간 밀도 잔존\n→ 출력 형상 재검증 3회 불합격', '판재 평면 최적화로 전환\n→ 124 g · 흔들림 0.23 mm 통과'],
  ['무선충전 방열판', '내부 방열 구조 최적화 v1', '중간 밀도(회색) 형상\n→ 실제 제작 불가 판정', '실제 제품 구조 기준 재정의\n→ 알루미늄 판금 2장 형상']];
fails.forEach((f, i) => {
  const x = 0.5 + i * 3.05;
  box(s, x, 1.3, 2.85, 3.0, X.tint, 'fail card');
  T(s, f[0], { x: x + 0.15, y: 1.4, w: 2.55, h: 0.32, fontSize: 13, bold: true, color: C.text2 });
  T(s, f[1], { x: x + 0.15, y: 1.72, w: 2.55, h: 0.28, fontSize: 9.5, color: C.accent3 });
  s.addImage({ data: IC2.x, x: x + 0.15, y: 2.18, w: 0.28, h: 0.28 });
  T(s, '검증 불합격', { x: x + 0.5, y: 2.17, w: 2.2, h: 0.3, fontSize: 12, bold: true, color: C.accent5, valign: 'middle' });
  T(s, f[2], { x: x + 0.15, y: 2.55, w: 2.6, h: 0.65, fontSize: 9.5, color: C.text1 });
  s.addShape(pres.shapes.DOWN_ARROW, { x: x + 1.27, y: 3.25, w: 0.3, h: 0.25, fill: { color: C.accent2 }, line: { color: C.accent2 } });
  s.addImage({ data: IC2.ok, x: x + 0.15, y: 3.6, w: 0.24, h: 0.24 });
  T(s, f[3], { x: x + 0.47, y: 3.57, w: 2.3, h: 0.7, fontSize: 9.5, bold: true, color: C.green });
});
T(s, '검증 관문이 없었다면 세 결과 모두 그대로 제작 파일이 됐을 것 — 범용 생성 AI와의 핵심 차이', { x: 0.5, y: 4.55, w: 9, h: 0.28, fontSize: 10.5, bold: true, color: C.accent1 });
s.addNotes('실제 작업 로그 기준. 검증 모듈이 출력 형상을 다시 계산하거나 제작 가능성을 판정해 불합격을 냈고, 에이전트가 방식을 바꿔 재설계했다.');

// ===== v7: 파이프라인 상세 (자전거 거치대 실제 산출물)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 실증 ① 자전거 거치대 — 말 한 줄에서 제작 파일까지', { placeholder: 'title' });
s.addText('각 단계의 산출물이 다음 단계의 입력이 된다', { placeholder: 'body' });
const PW = 2.9, PH = 1.72;
const pcard = (i, title, tag) => {
  const x = 0.5 + (i % 3) * (PW + 0.15), y = 1.3 + Math.floor(i / 3) * (PH + 0.12);
  box(s, x, y, PW, PH, X.tint, 'step card');
  disc(s, x + 0.1, y + 0.1, 0.3, X.teal, null, 'num');
  T(s, String(i + 1), { x: x + 0.1, y: y + 0.1, w: 0.3, h: 0.3, fontSize: 11, bold: true, color: C.background1, align: 'center', valign: 'middle' });
  T(s, title, { x: x + 0.48, y: y + 0.1, w: PW - 0.55, h: 0.3, fontSize: 11.5, bold: true, color: C.text2, valign: 'middle' });
  if (tag) T(s, tag, { x: x + PW - 1.15, y: y + 0.1, w: 1.05, h: 0.3, fontSize: 8, color: C.accent3, align: 'right', valign: 'middle' });
  return [x, y];
};
let [px, py] = pcard(0, '입력', '말 한 줄');
T(s, '"울퉁불퉁한 길에서도 폰이 안 흔들리게, 최대한 가볍게. 3D 프린터로 뽑을 거야"', { x: px + 0.15, y: py + 0.55, w: PW - 0.3, h: 0.75, fontSize: 11, italic: true, color: C.text2 });
T(s, '+ 핸들바 Ø31.8 mm · 폰 갤럭시 S26 울트라', { x: px + 0.15, y: py + 1.32, w: PW - 0.3, h: 0.28, fontSize: 9, color: C.accent3 });
[px, py] = pcard(1, '설계 명세', 'AI 작성 · 출처 포함');
const spec7 = [['하중', '254 g (폰 214 + 거치부 40)'], ['진동', '1차 ≥ 91 Hz (노면 최대 45.6 Hz × 2)'], ['충격', '48.5 g (ISBS 2020 실측)'], ['재료', 'PETG 39 MPa ÷ 1.5 → 26 MPa'], ['제조', 'FDM 출력, 층간 강도 별도 확인']];
spec7.forEach((r, i) => {
  T(s, r[0], { x: px + 0.15, y: py + 0.5 + i * 0.235, w: 0.45, h: 0.23, fontSize: 9, bold: true, color: C.accent1 });
  T(s, r[1], { x: px + 0.6, y: py + 0.5 + i * 0.235, w: PW - 0.7, h: 0.23, fontSize: 9, color: C.text1 });
});
[px, py] = pcard(2, '처음 설계 계산', '판정: 미달');
fit(s, SH + 'v6_c_bike_base_stress.png', px + 0.08, py + 0.45, 1.45, 1.2, 'base');
T(s, [{ text: `${BK.base_f} Hz`, options: { bold: true, color: C.accent5, fontSize: 15, breakLine: true } }, { text: '기준 91 Hz ✗', options: { fontSize: 8.5, color: C.accent3, breakLine: true } }, { text: `${BK.base_s} MPa`, options: { bold: true, color: C.accent5, fontSize: 15, breakLine: true } }, { text: '기준 26 MPa ✗', options: { fontSize: 8.5, color: C.accent3 } }], { x: px + 1.6, y: py + 0.5, w: 1.25, h: 1.15 });
[px, py] = pcard(3, '3D 위상최적화', '반복 계산');
const LG = fs.readFileSync(__dirname + '/../opt/' + (BK.log || 'd') + '.log', 'utf8').split('\n').filter(l => l.startsWith('{')).map(JSON.parse).filter((d, i) => i % 10 === 0);
s.addChart(pres.charts.LINE, [{ name: '질량', labels: LG.map(d => String(d.it)), values: LG.map(d => d.mass_g) }], {
  x: px + 0.05, y: py + 0.42, w: PW - 0.1, h: 1.05, chartColors: [X.teal], lineSize: 2, lineDataSymbol: 'none',
  catAxisLabelColor: X.mute, valAxisLabelColor: X.mute, catAxisLabelFontSize: 7, valAxisLabelFontSize: 7, catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt',
  valGridLine: { color: 'DDE5E4', size: 0.5 }, catGridLine: { style: 'none' }, showLegend: false, catAxisLabelFrequency: 4, catAxisLabelRotate: 0, valAxisMinVal: 0,
  showValAxisTitle: false, showCatAxisTitle: false });
T(s, `질량 ${LG[0].mass_g} → ${LG[LG.length - 1].mass_g} g (격자 기준) · 진동 기준 유지`, { x: px + 0.15, y: py + 1.45, w: PW - 0.3, h: 0.24, fontSize: 8.5, color: C.accent3 });
[px, py] = pcard(4, '출력 형상 재검증', '판정: 통과');
fit(s, SH + BK.ai_img, px + 0.08, py + 0.45, 1.45, 1.2, 'final');
[[`${BK.ai_f} Hz`, '≥ 91'], [`${BK.ai_s} MPa`, '≤ 26'], [`층간 ${BK.ai_il || 7.8}`, '≤ 10.9 MPa']].forEach((r, i) => {
  s.addImage({ data: IC2.ok, x: px + 1.6, y: py + 0.55 + i * 0.37, w: 0.18, h: 0.18 });
  T(s, [{ text: r[0], options: { bold: true, color: C.green, breakLine: true } }, { text: r[1], options: { fontSize: 8, color: C.accent3 } }], { x: px + 1.83, y: py + 0.5 + i * 0.37, w: 1.05, h: 0.36, fontSize: 10.5 });
});
[px, py] = pcard(5, '제작 파일', '');
fit(s, SH + 'v12_drw_front.png', px + 0.1, py + 0.45, PW - 0.2, 0.95, 'drawing');
T(s, `출력용 STL ${BK.ai_m} g · 도면 · 근거 리포트`, { x: px + 0.15, y: py + 1.42, w: PW - 0.3, h: 0.24, fontSize: 9, bold: true, color: C.accent1 });
T(s, '※ 2 → 5 사이에서 불합격이면 에이전트가 조건·설정을 고쳐 다시 계산. 3단계 이후 수치는 출력 형상 기준 유한요소 해석값(실측 전)', { x: 0.5, y: 4.98, w: 9, h: 0.22, fontSize: 8, color: C.accent3 });
s.addNotes('말 한 줄이 출처 있는 설계 명세가 되고, 처음 설계를 계산해 미달을 확인한 뒤, 3D 최적화로 재료를 재배치하고, 출력 형상을 다시 계산해 통과한 것만 제작 파일로 내보낸다. 실측은 데모 영상에서 다룸.');

// ===== v12: 형상이 만들어지는 과정 (위상 최적화 반복)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
const EV = JSON.parse(fs.readFileSync(__dirname + '/evo_v12.json', 'utf8'));
s.addText('2. 실증 ① 자전거 거치대 — 형상은 계산이 만든다', { placeholder: 'title' });
s.addText('설계 공간을 재료로 채운 뒤, 매 반복 진동을 계산해 기준을 지키는 한도에서 덜 필요한 재료를 덜어낸다', { placeholder: 'body' });
const FW = 1.43;
EV.frames.forEach((f, i) => {
  const x = 0.5 + i * (FW + 0.08);
  box(s, x, 1.3, FW, 1.78, i === EV.frames.length - 1 ? 'E3F1F0' : X.tint, 'frame');
  fit(s, SH + f.img, x + 0.05, 1.36, FW - 0.1, 1.05, 'iteration ' + f.it);
  T(s, i === 0 ? '시작' : i === EV.frames.length - 1 ? `최종 (${f.it + 1}회)` : `${f.it}회`, { x: x + 0.08, y: 2.43, w: FW - 0.16, h: 0.22, fontSize: 9.5, bold: true, color: C.text2 });
  T(s, `${f.mass} g · ${f.f1} Hz`, { x: x + 0.08, y: 2.67, w: FW - 0.16, h: 0.22, fontSize: 9, bold: true, color: i === EV.frames.length - 1 ? C.accent1 : C.accent3 });
  if (i < EV.frames.length - 1) arrow(s, x + FW - 0.02, 1.85, 0.11, 0.18);
});
// 질량 · 진동 곡선
s.addChart(pres.charts.LINE, [{ name: '무게 (g)', labels: EV.it.map(String), values: EV.mass }], {
  x: 0.45, y: 3.15, w: 4.5, h: 1.75, chartColors: [X.teal], lineSize: 2, lineDataSymbol: 'none', showLegend: false, showTitle: true, title: '무게 (g) — 반복할수록 감소', titleFontSize: 9, titleColor: X.ink, titleFontFace: '+mn-lt',
  catAxisLabelColor: X.mute, valAxisLabelColor: X.mute, catAxisLabelFontSize: 7, valAxisLabelFontSize: 7, catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt',
  valGridLine: { color: 'DDE5E4', size: 0.5 }, catGridLine: { style: 'none' }, catAxisLabelFrequency: 5, catAxisLabelRotate: 0, valAxisMinVal: 0 });
s.addChart(pres.charts.LINE, [{ name: '1차 진동수', labels: EV.it.map(String), values: EV.f1 }, { name: '기준', labels: EV.it.map(String), values: EV.it.map(() => 91) }], {
  x: 4.95, y: 3.15, w: 2.6, h: 1.75, chartColors: [X.amber, X.red], lineSize: 2, lineDataSymbol: 'none', showLegend: false, showTitle: true, title: '1차 진동수 (Hz) — 기준 91 유지', titleFontSize: 9, titleColor: X.ink, titleFontFace: '+mn-lt',
  catAxisLabelColor: X.mute, valAxisLabelColor: X.mute, catAxisLabelFontSize: 7, valAxisLabelFontSize: 7, catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt',
  valGridLine: { color: 'DDE5E4', size: 0.5 }, catGridLine: { style: 'none' }, catAxisLabelFrequency: 10, catAxisLabelRotate: 0, valAxisMinVal: 60, valAxisMaxVal: 120 });
const how = [['1', '설계 공간', '클램프 · 받침판은 고정, 나머지를 재료 밀도 변수로'], ['2', '매 반복 계산', 'FEM으로 진동 모드와 민감도 계산'], ['3', '재료 재배치', '진동 기준을 지키며 무게 최소화 (MMA)'], ['4', '출력 제약', '아래가 비어 45°를 넘는 재료 금지']];
how.forEach((h, i) => { const y = 3.2 + i * 0.43;
  disc(s, 7.68, y + 0.02, 0.26, X.teal, null, 'step');
  T(s, h[0], { x: 7.68, y: y + 0.02, w: 0.26, h: 0.26, fontSize: 9, bold: true, color: C.background1, align: 'center', valign: 'middle' });
  T(s, h[1], { x: 8.02, y, w: 1.55, h: 0.18, fontSize: 8.5, bold: true, color: C.text2 });
  T(s, h[2], { x: 8.02, y: y + 0.18, w: 1.55, h: 0.24, fontSize: 7, color: C.accent3 }); });
T(s, `※ 그림 = 재료 밀도 0.5 이상 영역, 수치 = 최적화 중 2 mm 격자 값(폰+거치부 254 g). 최종 출력 형상 재해석: ${BK.ai_m} g · ${BK.ai_f} Hz. CPU 2코어 약 ${EV.minutes}분`, { x: 0.5, y: 4.95, w: 9, h: 0.22, fontSize: 7.5, color: C.accent3 });
s.addNotes('사람이 모양을 그린 것이 아니라, 계산이 재료를 덜어내며 만든 형상이다. 처음에는 설계 공간 전체가 재료로 차 있고, 반복할 때마다 FEM으로 진동을 계산해 진동 기준(91 Hz)을 지키는 한도에서 기여가 작은 재료를 줄인다. 출력 방향 제약 때문에 아래가 비어 있는 재료는 생기지 않는다.');

// ===== v13: 속 구조와 출력 방법
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 실증 ① 자전거 거치대 — 속은 비어 있고, 그대로 출력된다', { placeholder: 'title' });
s.addText('덩어리가 아니라 윗판 · 옆벽 · 대각 보강재로 된 ㄱ자 얇은 벽 구조 — 출력 방향까지 계산에 넣어 받침대 없이 쌓인다', { placeholder: 'body' });
box(s, 0.5, 1.3, 5.0, 3.6, 'FFFFFF', 'sections');
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 1.3, w: 5.0, h: 3.6, rectRadius: 0.06, fill: { type: 'none' }, line: { color: X.line, width: 1 } });
fit(s, SH + 'v13_sections.png', 0.55, 1.33, 4.9, 3.54, 'cross sections');
box(s, 5.65, 1.3, 3.85, 1.85, X.tint, 'print pose');
fit(s, SH + 'v13_c_print_iso.png', 5.7, 1.35, 3.75, 1.5, 'print orientation');
T(s, '출력 자세 — 옆벽을 바닥에 두고 눕혀서', { x: 5.75, y: 2.86, w: 3.7, h: 0.24, fontSize: 9, bold: true, color: C.text2, align: 'center' });
const pr = [['클램프 링', '세로 원통으로 쌓여 받침대 불필요'], ['속 빈 공간', '위로 열려 있음 · 갇힌 빈 공간 0개'], ['돌출부', '45° 넘는 돌출 0개 (2 mm 격자 검사)'], ['층간 강도', `층 사이 응력 ${BK.ai_il} MPa ≤ 허용 10.9 MPa`], ['권장 설정', 'PETG · 층 0.2 mm · 벽 4겹']];
pr.forEach((r, i) => { const y = 3.27 + i * 0.32;
  s.addImage({ data: IC2.ok, x: 5.7, y: y + 0.04, w: 0.18, h: 0.18 });
  T(s, r[0], { x: 5.95, y, w: 0.9, h: 0.27, fontSize: 9, bold: true, color: C.text2, valign: 'middle' });
  T(s, r[1], { x: 6.85, y, w: 2.65, h: 0.27, fontSize: 8.5, color: C.text1, valign: 'middle' }); });
T(s, '※ 단면 = 출력용 STL 기준(청록 = 재료). 받침대 여부는 2 mm 격자 45° 규칙으로 판정, 매끄럽게 다듬은 STL의 최종 확인은 슬라이서 미리보기로 필요', { x: 0.5, y: 4.95, w: 9, h: 0.22, fontSize: 7.5, color: C.accent3 });
s.addNotes('잘라 보면 속이 꽉 찬 덩어리가 아니다. 위에 약 4 mm 판, 출력 바닥 쪽에 세로 벽, 반대쪽에 대각 보강재가 있고 나머지는 비어 있다. 같은 무게면 재료를 테두리에 둬야 굽힘에 강하다(I빔 원리). 옆벽이 바닥면 쪽에 생긴 것은 출력 방향 제약 때문이다. 눕혀서 출력하면 링은 세로 원통으로, 빈 공간은 위로 열린 채 쌓여 받침대가 필요 없다.');
// ===== v12: 결과 — 장착 모습과 도면
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 실증 ① 자전거 거치대 — 장착 모습과 제작 도면', { placeholder: 'title' });
s.addText('핸들바 클램프 + 폰 거치부 체결 구조까지 포함한 출력용 형상, 도면은 자동 생성', { placeholder: 'body' });
box(s, 0.5, 1.3, 3.4, 2.4, X.tint, 'side');
fit(s, SH + 'v12_c_mnt_side.png', 0.6, 1.38, 3.2, 2.24, 'mount side view');
box(s, 0.5, 3.8, 3.4, 1.35, X.tint, 'bike');
fit(s, SH + 'v12_c_mnt_bike.png', 0.6, 3.85, 1.7, 1.25, 'on bike');
T(s, [{ text: `${BK.ai_m} g`, options: { bold: true, color: C.accent1, fontSize: 16, breakLine: true } }, { text: 'PETG · 옆으로 눕혀 출력', options: { fontSize: 8.5, color: C.accent3, breakLine: true } }, { text: '받침대 없음 (45° 규칙)', options: { fontSize: 8.5, color: C.accent3 } }], { x: 2.35, y: 3.98, w: 1.5, h: 1.0 });
box(s, 4.05, 1.3, 5.45, 3.85, 'FFFFFF', 'drawing frame');
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 4.05, y: 1.3, w: 5.45, h: 3.85, rectRadius: 0.06, fill: { type: 'none' }, line: { color: X.line, width: 1 } });
fit(s, '/tmp/claude-0/-home-claude/e964ed80-ee1b-5f91-abd3-3081682a3ad7/scratchpad/out/FormProof_자전거거치대_도면_v4.png', 4.1, 1.35, 5.35, 3.75, 'drawing');
s.addNotes('왼쪽 위: 핸들바 클램프에 거치대가 물리고, 그 위 받침판에 폰 거치부가 체결된다. 왼쪽 아래: 자전거 장착 모습. 오른쪽: 자동 생성 도면(정면 · 평면 · 우측면, 클램프 Ø32.2, M4 볼트 2조, 폰 클램프 인서트 Ø8). 자유 형상부 치수는 STL 기준.');
// ---------- 6. 실증 결과
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 실증 ① 자전거 거치대 — 기준 미달에서 통과로, 받침대 없이 출력', { placeholder: 'title' });
s.addText('핸들바에 장착한 상태로 계산 · 같은 색 = 같은 응력 (빨강일수록 위험)', { placeholder: 'body' });
box(s, 0.5, 1.3, 4.35, 2.25, X.tint, 'before');
pill(s, 0.65, 1.42, 1.1, '처음 설계', X.mute, X.white);
fit(s, SH + 'v6_c_bike_base_stress.png', 0.65, 1.75, 4.05, 1.72, 'before stress');
box(s, 5.15, 1.3, 4.35, 2.25, X.tint, 'after');
pill(s, 5.3, 1.42, 1.3, 'AI 재설계', X.teal, X.white);
fit(s, SH + BK.ai_img, 5.3, 1.75, 4.05, 1.72, 'after stress');
arrow(s, 4.88, 2.25, 0.25, 0.35);
fit(s, SH + 'r_cbar.png', 3.6, 3.56, 2.8, 0.4, 'stress colorbar (MPa)'); T(s, '응력 (MPa)', { x: 6.45, y: 3.6, w: 1, h: 0.2, fontSize: 8, color: C.accent3 });
// metric bars: value vs criterion
const met = [['무게', BK.base_m, BK.ai_m, 'g', null, '같은 클램프'], ['1차 진동수', BK.base_f, BK.ai_f, 'Hz', 91, '기준 ≥ 91 Hz'], ['충격 응력', BK.base_s, BK.ai_s, 'MPa', 26, '기준 ≤ 26 MPa']];
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
T(s, `※ 무게 = 출력용 STL, 진동수·응력 = 출력 형상 1 mm 재해석(폰+거치부 254 g, 응력은 99.9% 값). 출력: 옆으로 눕혀 받침대 없이(45° 규칙, 격자 기준). 빨간 점선 = 판정 기준`, { x: 0.5, y: 4.93, w: 9, h: 0.25, fontSize: 8, color: C.accent3 });
s.addNotes('처음 설계는 진동·강도 모두 미달. AI 설계는 둘 다 통과하면서 같은 기준을 맞춘 단순 보강안보다 가볍다. 이전 자료의 50.0 g은 다른 클램프 기준이라 정정(같은 클램프 42.5 g).');

// ---------- 6b. TV 스탠드 실증 (보조: 제품 설계)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 실증 ② TV 스탠드 — 외형은 그대로, 무게는 1/3', { placeholder: 'title' });
s.addText('65형 TV · 알루미늄 10 mm 판재 다리 · 외곽선·5 mm 테두리 고정, 안쪽만 AI 결정', { placeholder: 'body' });
box(s, 0.5, 1.3, 4.2, 3.45, X.tint, 'tv card');
fit(s, SH + 'v6_c_tv_full.png', 0.6, 1.38, 4.0, 2.55, 'TV on optimized feet');
T(s, '실제 판매 스탠드(같은 모델): 약 1.0 kg, 깊이 279 mm — 무게만 비교 가능, 실제 기준·형상은 확인 필요', { x: 0.65, y: 4.0, w: 3.9, h: 0.65, fontSize: 9, color: C.text2 });
box(s, 4.9, 1.3, 2.25, 2.35, X.tint, 'before'); pill(s, 5.0, 1.38, 1.6, '같은 외형, 꽉 찬 판', X.mute, X.white);
fit(s, SH + 'v6_c_tv_foot_base_S.png', 4.95, 1.72, 2.15, 1.45, 'solid foot stress');
T(s, '400 g · 흔들림 0.06 mm', { x: 4.95, y: 3.25, w: 2.15, h: 0.3, fontSize: 10, bold: true, color: C.accent3, align: 'center' });
box(s, 7.25, 1.3, 2.25, 2.35, X.tint, 'after'); pill(s, 7.35, 1.38, 1.1, 'AI 설계', X.teal, X.white);
fit(s, SH + 'v6_c_tv_foot_opt_S.png', 7.3, 1.72, 2.15, 1.45, 'optimized foot stress');
T(s, '124 g · 흔들림 0.23 mm ✓', { x: 7.3, y: 3.25, w: 2.15, h: 0.3, fontSize: 10, bold: true, color: C.accent1, align: 'center' });
fit(s, SH + 'v6_tv_cbar.png', 5.4, 3.66, 2.4, 0.36, 'stress colorbar'); T(s, '응력 (MPa)', { x: 7.85, y: 3.72, w: 1.2, h: 0.2, fontSize: 8, color: C.accent3 });
const tvk = [['−69%', '다리 무게', '400 → 124 g (1개)'], ['≤ 1 mm', 'TV 상단 흔들림', '0.23 mm (설계 가정 기준)'], ['통과', '넘어짐 안정성', '10° 기울임 · 13% 수평력']];
tvk.forEach((k, i) => { const x = 4.9 + i * 1.55;
  T(s, k[0], { x, y: 4.05, w: 1.5, h: 0.38, fontSize: 18, bold: true, color: C.accent1 });
  T(s, k[1], { x, y: 4.42, w: 1.5, h: 0.2, fontSize: 9.5, bold: true, color: C.text2 });
  T(s, k[2], { x, y: 4.62, w: 1.5, h: 0.3, fontSize: 8, color: C.accent3 }); });
T(s, '※ 출력 형상 3D 재계산(판 수직 방향 수평력 포함), 최대 응력 11 MPa(허용 184 MPa). 흔들림 1 mm·다리 간격 1.2 m는 설계 가정. 넘어짐 안전계수 1.05~1.21', { x: 0.5, y: 4.95, w: 9, h: 0.3, fontSize: 8, color: C.accent3 });
s.addNotes('제품 설계 기여 예시: 디자이너가 정한 외형은 지키고 내부만 비운다. 꽉 찬 판은 대부분 응력이 낮아(파랑) 재료가 놀고 있음. AI는 힘이 지나는 테두리·V자 기둥·아치만 남김. 실제 판매 스탠드 약 1.0 kg과는 기준을 모르는 상태라 무게만 참고.');

// ===== v11: 범용 LLM 단독 vs FormProof
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 범용 LLM 단독 vs FormProof — 같은 요청, 같은 검증', { placeholder: 'title' });
s.addText('도구 없이 설계한 LLM 3회는 기준부터 낮게 잡았고, 같은 해석기로 계산하니 3건 모두 근거 기준 미달', { placeholder: 'body' });
const LL = JSON.parse(fs.readFileSync(__dirname + '/llm_v11.json', 'utf8'));
const LW = 2.12;
LL.forEach((d, i) => {
  const x = 0.5 + i * (LW + 0.15), fp = d.fp;
  box(s, x, 1.3, LW, 3.25, fp ? 'E3F1F0' : X.tint, 'llm card');
  if (fp) s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.3, w: LW, h: 3.25, rectRadius: 0.08, fill: { type: 'none' }, line: { color: X.teal, width: 2 }, objectName: 'fp frame' });
  T(s, d.name, { x: x + 0.1, y: 1.36, w: LW - 0.2, h: 0.26, fontSize: 11, bold: true, color: fp ? C.accent1 : C.text2 });
  T(s, d.desc, { x: x + 0.1, y: 1.6, w: LW - 0.2, h: 0.22, fontSize: 8, color: C.accent3 });
  fit(s, SH + d.img, x + 0.08, 1.85, LW - 0.16, 1.05, 'design ' + d.name);
  const rows = [['진동 기준', d.crit, fp ? C.accent1 : C.text1], ['스스로 예측', d.pred, C.text1], ['FEM 실제 1차', d.f1 + ' Hz', fp ? X.green : C.accent5], ['자갈길 진동 증폭', d.amp + '배', fp ? X.green : C.accent5], ['무게', d.m + ' g', C.text1]];
  rows.forEach((r, k) => {
    const y = 2.98 + k * 0.255;
    T(s, r[0], { x: x + 0.1, y, w: 0.95, h: 0.24, fontSize: 8, color: C.accent3, valign: 'middle' });
    T(s, r[1], { x: x + 1.0, y, w: LW - 1.08, h: 0.24, fontSize: k === 2 || k === 3 ? 10 : 8.5, bold: k === 2 || k === 3, color: r[2], align: 'right', valign: 'middle' });
  });
  s.addImage({ data: fp ? IC2.ok : IC2.x, x: x + LW / 2 - 0.5, y: 4.27, w: 0.2, h: 0.2 });
  T(s, fp ? '근거 기준 통과' : '근거 기준 미달', { x: x + LW / 2 - 0.26, y: 4.24, w: 1.0, h: 0.26, fontSize: 9.5, bold: true, color: fp ? X.green : C.accent5, valign: 'middle' });
});
T(s, '※ LLM 단독 = 대화 맥락 · 도구 없이 같은 요청 · 좌표계만 받은 독립 세션 3회(Claude). 판정 기준: 1차 진동 ≥ 91 Hz(자갈길 실측 최대 45.6 Hz × 2, ISBS 2020). 증폭 = 45.6 Hz 가진 시 비감쇠 1/(1−r²). 해석은 같은 1 mm FEM, 폰+거치부 254 g. LLM C의 1.6 mm 벽은 1 mm 격자 표현 한계로 무게가 자체 추정(33 g)보다 큼', { x: 0.5, y: 4.62, w: 9, h: 0.5, fontSize: 7.5, color: C.accent3 });
s.addNotes('같은 요청을 도구 없는 LLM에 세 번 줬다. 세 번 모두 진동 기준을 40~60 Hz로 잡았는데, 자갈길 실측 진동이 최대 45.6 Hz라 이 기준으로는 공진을 피할 수 없다. 스스로 예측한 진동수도 실제와 −17~+42% 어긋났다. FormProof는 근거로 91 Hz 기준을 세우고 계산으로 통과를 확인했다.');
// ---------- 7. 사업·조직 기여
pres.addSection({ title: '3. 사업·조직 기여' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '3. 사업·조직 기여' });
s.addText('3. 사업·조직 기여 — DX 제품 설계 과정에 직접 들어간다', { placeholder: 'title' });
s.addText('기여하는 것은 사례 제품이 아니라 방법론: VD·MX·DA 기구 설계자가 설계 단계마다 직접 사용', { placeholder: 'body' });
const stg = [['구상', '경험으로 형상 결정', '요구 조건에서 기준을 만족하는 설계안 자동 생성'],
  ['상세 설계', '해석 부서 의뢰 · 결과 대기', '설계자가 직접 성능 확인 (근거 · 검증 포함)'],
  ['개선', '해석 결과 보고 수작업 수정', '최적화로 재설계 (경량화 · 보강)'],
  ['시제품', '출력 · 시험 → 실패 → 수정 반복', '출력 전 제작 형상까지 검증']];
T(s, '지금', { x: 2.0, y: 1.3, w: 3.2, h: 0.28, fontSize: 11, bold: true, color: C.accent3 });
T(s, 'FormProof 적용', { x: 5.6, y: 1.3, w: 3.9, h: 0.28, fontSize: 11, bold: true, color: C.accent1 });
stg.forEach((g, i) => {
  const y = 1.62 + i * 0.6;
  pill(s, 0.5, y + 0.12, 1.3, g[0], X.ink, X.white);
  box(s, 2.0, y, 3.2, 0.5, 'F3F4F5', 'now');
  T(s, g[1], { x: 2.12, y, w: 3.0, h: 0.5, fontSize: 10.5, color: C.accent3, valign: 'middle' });
  arrow(s, 5.25, y + 0.12, 0.3, 0.26);
  box(s, 5.6, y, 3.9, 0.5, X.tint, 'formproof');
  T(s, g[2], { x: 5.72, y, w: 3.7, h: 0.5, fontSize: 10.5, bold: true, color: C.text2, valign: 'middle' });
});
const tasks = [['지지 구조물 · 브래킷', '강성 · 넘어짐 안정성', 'TV 스탠드'], ['진동이 문제인 부품', '공진 회피', '자전거 거치대'], ['발열 부품 주변 구조', '방열판 배치', '무선충전 스탠드'], ['기존 부품 개선', '경량화 · 보강', 'STEP 입력']];
T(s, '적용 설계 업무 (부품 유형)  ·  실증 사례', { x: 0.5, y: 4.08, w: 9, h: 0.25, fontSize: 10, bold: true, color: C.text2 });
tasks.forEach((t, i) => {
  const x = 0.5 + i * 2.27;
  T(s, [{ text: t[0], options: { bold: true, color: C.accent1, breakLine: true } }, { text: t[1] + '  ·  ' + t[2], options: { color: C.text1 } }], { x, y: 4.34, w: 2.2, h: 0.5, fontSize: 9 });
});
T(s, '※ 정량 효과(해석 의뢰~결과 기간, 시제품 반복 횟수)는 사내 기구 · 해석 담당자 확인 필요', { x: 0.5, y: 4.95, w: 9, h: 0.25, fontSize: 8.5, color: C.accent3 });
s.addNotes('사업 기여의 주체는 방법론. 사례 제품은 증거. 왼쪽 단계별로 지금 방식과 적용 후를 비교. 아래는 어떤 유형의 설계 업무에 쓰는지와 그 유형을 입증한 사례. 정량 효과는 담당자 인터뷰로 채울 예정.');

// ---------- 8. 확장성·파급 효과
pres.addSection({ title: '4. 확장성·파급 효과' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '4. 확장성·파급 효과' });
s.addText('4. 확장성·파급 효과 — 제품은 같은 엔진으로, 물리는 모듈로', { placeholder: 'title' });
s.addText('같은 흐름(입력 → 설계 명세 → 계산 → 재설계 → 검증 → 출력)을 유지한 채 넓혀 간다', { placeholder: 'body' });
// two axes
box(s, 0.5, 1.3, 4.35, 2.55, X.tint, 'product axis');
T(s, '제품 확장 — 같은 물리(구조), 다른 제품', { x: 0.65, y: 1.4, w: 4.1, h: 0.3, fontSize: 12, bold: true, color: C.text2 });
pill(s, 3.75, 1.42, 0.95, '입증됨', X.green, X.white);
[['TV 스탠드', '정적 강성 · 넘어짐', 'v6_c_tv_foot_opt.png'], ['자전거 거치대', '진동 · 충격', BK.ai_img]].forEach((p, i) => {
  const x = 0.65 + i * 2.1;
  box(s, x, 1.8, 1.95, 1.4, X.white, 'case');
  fit(s, SH + p[2], x + 0.05, 1.85, 1.85, 1.0, p[0]);
  T(s, p[0], { x, y: 2.85, w: 1.95, h: 0.2, fontSize: 9.5, bold: true, color: C.text2, align: 'center' });
  T(s, p[1], { x, y: 3.03, w: 1.95, h: 0.18, fontSize: 8.5, color: C.accent3, align: 'center' });
});
T(s, '하중 · 재료 · 고정 위치 · 판정 기준만 바꿔 다른 설계 문제를 풂', { x: 0.65, y: 3.35, w: 4.1, h: 0.4, fontSize: 10, color: C.text1 });
box(s, 5.15, 1.3, 4.35, 2.55, X.tint, 'physics axis');
T(s, '물리 확장 — 방정식 모듈 추가', { x: 5.3, y: 1.4, w: 4.1, h: 0.3, fontSize: 12, bold: true, color: C.text2 });
const ph = [['구조 (탄성)', '정적 · 진동', '입증됨', X.green], ['+ 열 (열전도)', '무선충전 스탠드: 방열판 배치', '입증됨', X.green], ['+ 광학 (PINN)', '디스플레이 광학 역설계', '다음 단계', X.mute], ['+ 전자기', '무선충전 금속 금지 구역 계산', '다음 단계', X.mute]];
ph.forEach((p, i) => {
  const y = 1.82 + i * 0.5;
  s.addImage({ data: [IC.cogs, IC.heat, IC.bulb, IC.bolt][i], x: 5.3, y: y + 0.07, w: 0.3, h: 0.3 });
  T(s, p[0], { x: 5.7, y, w: 1.45, h: 0.44, fontSize: 10.5, bold: true, color: C.text2, valign: 'middle' });
  T(s, p[1], { x: 7.15, y, w: 1.4, h: 0.44, fontSize: 8.5, color: C.text1, valign: 'middle' });
  pill(s, 8.55, y + 0.08, 0.85, p[2], p[3], X.white);
});
T(s, '파급 효과', { x: 0.5, y: 4.0, w: 2, h: 0.3, fontSize: 12, bold: true, color: C.accent1 });
T(s, [{ text: '생성형 AI 결과에 물리 검증을 붙이는 방식 — 다른 생성형 AI 과제에도 같은 검증 관문 재사용', options: { bullet: { indent: 12 }, breakLine: true } },
      { text: '설계 결과가 쌓일수록 물리 AI 가속 모델이 정확해져 계산 시간 단축', options: { bullet: { indent: 12 } } }],
  { x: 0.5, y: 4.3, w: 9, h: 0.6, fontSize: 10.5, color: C.text1, paraSpaceAfter: 3 });
s.addNotes('확장은 두 축. 제품 확장은 두 사례로 입증(같은 구조 방정식, 다른 하중·재료·기준). 물리 확장은 방정식 모듈 추가 구조로 설명하고, 열은 무선충전 스탠드로 다음에 입증 예정. 광학·전자기는 계획.');

// ---------- 6c. 무선충전 스탠드 (보조: 물리 확장 — 열)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '4. 확장성·파급 효과' });
s.addText('4. 확장 근거 — 열 물리: 무선충전 스탠드 방열판', { placeholder: 'title' });
s.addText('실제 제품 구조(코일 2개·페라이트·회로기판)는 고정, 알루미늄 방열판 2장 형상만 AI 결정', { placeholder: 'body' });
box(s, 0.5, 1.3, 2.9, 3.5, X.tint, 'product');
fit(s, SH + 'v6_c_wc2_product.png', 0.55, 1.35, 1.4, 2.4, 'stand with phone');
fit(s, SH + 'v6_c_wc2_cut_opt.png', 1.95, 1.35, 1.4, 2.4, 'cutaway');
T(s, '왼쪽: 폰 거치 · 오른쪽: 하우징 투명 처리, 방열판 2장과 회로기판', { x: 0.6, y: 3.8, w: 2.7, h: 0.45, fontSize: 8.5, color: C.text2 });
T(s, '발열(가정): 코일 2.0 W + 구동 소자 1.5 W', { x: 0.6, y: 4.3, w: 2.7, h: 0.4, fontSize: 8.5, bold: true, color: C.accent2 });
box(s, 3.55, 1.3, 2.6, 3.5, X.tint, 'layers');
fit(s, SH + 'v6_wc2_layers.png', 3.6, 1.35, 2.5, 3.0, 'optimized sheets');
T(s, '판 A: 코일 열을 옆벽으로 · 판 B: 소자 열을 뒷벽 전체로', { x: 3.65, y: 4.38, w: 2.45, h: 0.38, fontSize: 8.5, color: C.text2 });
fit(s, SH + 'v6_wc2_bars.png', 6.3, 1.3, 3.2, 1.75, 'temperature comparison');
const wk = [['같은 무게 ~25 g', '평판 한 장은 한쪽만 식힘(131~147 °C) → AI 배치는 두 곳 모두 70 °C 이하'], ['평판 2장 대비 무게 절반', '코일 쪽 66.5 vs 65.2 °C, 회로 쪽 59.8 vs 44.1 °C']];
wk.forEach((k, i) => { T(s, k[0], { x: 6.35, y: 3.15 + i * 0.75, w: 3.1, h: 0.3, fontSize: 12, bold: true, color: C.accent1 }); T(s, k[1], { x: 6.35, y: 3.45 + i * 0.75, w: 3.1, h: 0.42, fontSize: 8.5, color: C.text1 }); });
T(s, '※ 팬 없는 밀폐 하우징으로는 어떤 배치든 폰 쪽 48 °C 기준 미달 → 실제 제품이 팬을 쓰는 이유와 일치. 주장은 "같은 무게에서 배치 효과". 발열량·열물성·대류 계수 15 W/m²K는 가정, 와전류 미해석', { x: 0.5, y: 4.9, w: 9, h: 0.35, fontSize: 8, color: C.accent3 });
s.addNotes('물리 확장의 실증: 구조 방정식 대신 열전도 방정식을 같은 흐름(설계 명세 → 계산 → 최적화 → 검증)에 넣음. 절대 온도는 가정에 민감하므로 같은 무게에서 평판 대비 배치 효과로 주장.');

// ---------- 9. 마무리
pres.addSection({ title: '마무리' });
s = pres.addSlide({ masterName: 'DARK', sectionTitle: '마무리' });
T(s, '형상을\n성능으로 증명한다', { x: 0.6, y: 1.5, w: 5.0, h: 1.4, fontSize: 32, bold: true, color: C.background1 });
T(s, '어떤 형태의 아이디어든, 검증된 제작 파일로', { x: 0.6, y: 3.05, w: 5.0, h: 0.4, fontSize: 16, color: C.accent4 });
box(s, 5.9, 1.1, 3.7, 3.2, 'FFFFFF', 'final card');
fit(s, SH + BK.rider, 6.0, 1.25, 3.5, 2.9, 'final design');

await pres.writeFile({ fileName: OUT });
await applyTheme(OUT, THEME);
console.log('ok', OUT);
})();
