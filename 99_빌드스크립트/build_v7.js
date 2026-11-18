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
const BK = JSON.parse(fs.readFileSync(__dirname + '/bike_v7.json','utf8'));
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
pres.title = 'FormProof 발표 초안 v7';
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
const kpi = [['기준 통과', '진동·충격 강도', `처음 설계는 둘 다 미달`], [`${(BK.ai_f/BK.base_f).toFixed(1)}배`, '1차 진동수', `${BK.base_f} → ${BK.ai_f} Hz`], [`−${pct((1-BK.ai_m/BK.beam_m)*100)}%`, '단순 보 대비 무게', `${BK.beam_m} → ${BK.ai_m} g`]];
kpi.forEach((k, i) => {
  const x = 0.5 + i * 3.1;
  T(s, k[0], { x, y: 4.05, w: 1.35, h: 0.6, fontSize: 28, bold: true, color: C.accent1, valign: 'middle' });
  T(s, k[1], { x: x + 1.4, y: 4.07, w: 1.6, h: 0.3, fontSize: 11, bold: true, color: C.text2 });
  T(s, k[2], { x: x + 1.4, y: 4.37, w: 1.6, h: 0.3, fontSize: 10, color: C.accent3 });
});
T(s, '※ 자전거 폰 거치대, 출력 형상 1 mm 구조 해석(폰 갤럭시 S26 울트라 + 거치부 254 g). 단순 보 = 직사각형 보로 같은 기준을 맞춘 경우(계산)', { x: 0.5, y: 4.85, w: 9, h: 0.25, fontSize: 9, color: C.accent3 });
s.addNotes('입력이 어떤 형태든 검증된 제작 파일까지. 진동수 배율은 1차 고유진동수 비율. 무게 비교는 기준을 통과하는 단순 보강안 대비(처음 설계는 기준 미달이라 무게 비교 대상이 아님).');

// ---------- 2b. 입력
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '요약' });
s.addText('입력 — 아이디어가 어떤 형태든 설계 명세로 바꾼다', { placeholder: 'title' });
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
T(s, '※ 입력 해석 자동화는 해커톤 기간 개발 범위. 시연 사례 입력: 자전거 거치대 = 스케치 + 텍스트, TV 스탠드 = 텍스트', { x: 0.5, y: 4.6, w: 9, h: 0.3, fontSize: 9, color: C.accent3 });
s.addNotes('핵심: 텍스트 전용이 아니다. 어떤 형태의 입력이든 "설계 명세"(형상 + 물리 조건 + 판정 기준 + 근거)라는 공통 형식으로 바꾸면, 그 뒤 계산·재설계·검증은 동일하다. 특허 아이디어 문서는 청구항·도면에서 구조와 기능 요구를 읽어 형상 후보로 만든다. 입력 해석은 해커톤에서 개발.');

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

// ---------- 4. 기술 차별성: 파이프라인
pres.addSection({ title: '2. 기술 차별성' });
// ===== v7: 프레임워크 아키텍처
const IC2 = {
  robot: await icon(fa.FaRobot, X.white), shape: await icon(fa.FaDraftingCompass, X.teal), atom: await icon(fa.FaAtom, X.teal),
  opt: await icon(fa.FaChartLine, X.teal), ver: await icon(fa.FaClipboardCheck, X.teal), stl: await icon(fa.FaCube, X.teal),
  drw: await icon(fa.FaRulerCombined, X.teal), rep: await icon(fa.FaFileAlt, X.teal), img: await icon(fa.FaImage, X.teal),
  book: await icon(fa.FaBook, X.amber), x: await icon(fa.FaTimesCircle, X.red), ok: await icon(fa.FaCheckCircle, X.green),
};
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 기술 차별성 — FormProof 프레임워크', { placeholder: 'title' });
s.addText('AI 에이전트가 근거를 찾아 설계 명세를 만들고, 물리 도구를 직접 돌려 검증을 통과할 때까지 고친다', { placeholder: 'body' });
// input column
box(s, 0.5, 1.3, 1.55, 3.65, X.tint, 'input col');
T(s, '입력', { x: 0.5, y: 1.36, w: 1.55, h: 0.3, fontSize: 12, bold: true, color: C.accent1, align: 'center' });
[['말 · 텍스트', IC.mic], ['스케치', IC.pen], ['사진', IC.cam], ['문서 · PPT', IC.doc], ['특허 아이디어', IC.pat], ['3D 파일(STEP)', IC.step]].forEach((r, i) => {
  const y = 1.75 + i * 0.52;
  s.addImage({ data: r[1], x: 0.65, y: y + 0.04, w: 0.26, h: 0.26 });
  T(s, r[0], { x: 1.0, y, w: 1.05, h: 0.34, fontSize: 10, color: C.text2, valign: 'middle' });
});
arrow(s, 2.1, 2.0, 0.3, 0.32);
// agent box
box(s, 2.45, 1.3, 4.7, 1.55, X.ink, 'agent');
disc(s, 2.6, 1.4, 0.42, X.teal, IC2.robot, 'agent icon');
T(s, 'AI 설계 에이전트 (LLM)', { x: 3.1, y: 1.43, w: 3.9, h: 0.36, fontSize: 14, bold: true, color: C.background1, valign: 'middle' });
[['① 요구 해석', '근거 자료 조사 →\n출처 있는 설계 명세'], ['② 도구 실행', '해석·최적화 설정과\n코드를 만들어 직접 실행'], ['③ 판정 · 수정', '기준 대비 합격 판정,\n불합격이면 수정 지시']].forEach((a, i) => {
  const x = 2.6 + i * 1.53;
  T(s, a[0], { x, y: 1.9, w: 1.45, h: 0.28, fontSize: 10.5, bold: true, color: C.accent2 });
  T(s, a[1], { x, y: 2.18, w: 1.47, h: 0.6, fontSize: 8.5, color: C.accent4 });
});
// down arrows + loop
s.addShape(pres.shapes.DOWN_ARROW, { x: 3.55, y: 2.9, w: 0.3, h: 0.28, fill: { color: C.accent2 }, line: { color: C.accent2 }, objectName: 'call' });
T(s, '도구 호출', { x: 3.9, y: 2.9, w: 1.0, h: 0.28, fontSize: 9, bold: true, color: C.accent2, valign: 'middle' });
s.addShape(pres.shapes.UP_ARROW, { x: 6.2, y: 2.9, w: 0.3, h: 0.28, fill: { color: C.accent5 }, line: { color: C.accent5 }, objectName: 'loop' });
T(s, '결과 · 불합격 사유', { x: 4.7, y: 2.9, w: 1.45, h: 0.28, fontSize: 9, bold: true, color: C.accent5, align: 'right', valign: 'middle' });
// tool row
const tools = [['형상 모듈', IC2.shape, '설계 영역 · 고정부\n· 비울 곳 3D 생성'], ['물리 엔진', IC2.atom, '유한요소 해석\n구조 · 진동 · 열'], ['최적화 엔진', IC2.opt, '3D 위상최적화\n+ 제조 제약'], ['검증 모듈', IC2.ver, '출력 형상 1 mm\n재해석 · 기준 판정']];
tools.forEach((t, i) => {
  const x = 2.45 + i * 1.19;
  box(s, x, 3.25, 1.1, 1.15, X.tint, 'tool');
  s.addImage({ data: t[1], x: x + 0.08, y: 3.33, w: 0.24, h: 0.24 });
  T(s, t[0], { x: x + 0.36, y: 3.31, w: 0.74, h: 0.3, fontSize: 9.5, bold: true, color: C.text2, valign: 'middle' });
  T(s, t[2], { x: x + 0.08, y: 3.66, w: 1.0, h: 0.66, fontSize: 8, color: C.text1 });
});
// planned strip
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 2.45, y: 4.5, w: 4.7, h: 0.45, rectRadius: 0.06, fill: { color: X.white }, line: { color: C.accent3, width: 1, dashType: 'dash' }, objectName: 'planned' });
T(s, [{ text: '계획  ', options: { bold: true, color: C.accent3 } }, { text: '물리 AI 대리모델(신경 연산자)로 계산 가속 · 형상 AI로 초기안 제안', options: { color: C.accent3 } }], { x: 2.6, y: 4.5, w: 4.5, h: 0.45, fontSize: 9, valign: 'middle' });
arrow(s, 7.2, 2.0, 0.3, 0.32);
// output col
box(s, 7.55, 1.3, 1.95, 3.65, X.tint, 'output col');
T(s, '출력', { x: 7.55, y: 1.36, w: 1.95, h: 0.3, fontSize: 12, bold: true, color: C.accent1, align: 'center' });
[['STL (출력용)', IC2.stl], ['도면', IC2.drw], ['근거 · 검증 리포트', IC2.rep], ['렌더링', IC2.img]].forEach((r, i) => {
  const y = 1.75 + i * 0.52;
  s.addImage({ data: r[1], x: 7.7, y: y + 0.04, w: 0.26, h: 0.26 });
  T(s, r[0], { x: 8.05, y, w: 1.4, h: 0.34, fontSize: 10, color: C.text2, valign: 'middle' });
});
s.addImage({ data: IC2.book, x: 7.7, y: 3.95, w: 0.24, h: 0.24 });
T(s, '근거 자료\n규격 · 재료 · 제품 분해 자료', { x: 8.0, y: 3.88, w: 1.45, h: 0.5, fontSize: 8.5, color: C.text1 });
T(s, '사람은 의도 입력과 최종 승인만', { x: 7.6, y: 4.5, w: 1.85, h: 0.45, fontSize: 9, bold: true, color: C.accent1, align: 'center', valign: 'middle' });
s.addNotes('구조: 입력 → AI 에이전트(요구 해석·도구 실행·판정) ↔ 물리 도구 4종 → 출력. 실선 박스는 이번 사례에 실제 사용한 모듈, 점선은 계획. 핵심은 에이전트가 계산 결과로 스스로 판정하고 고치는 폐루프.');

// ===== v7: 파이프라인 상세 (자전거 거치대 실제 산출물)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 파이프라인 — 자전거 거치대가 실제로 거친 6단계', { placeholder: 'title' });
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
fit(s, SH + 'v7_drw_front.png', px + 0.1, py + 0.45, PW - 0.2, 0.95, 'drawing');
T(s, `STL ${BK.ai_m} g · 도면 · 근거 리포트`, { x: px + 0.15, y: py + 1.42, w: PW - 0.3, h: 0.24, fontSize: 9, bold: true, color: C.accent1 });
T(s, '※ 2 → 5 사이에서 불합격이면 에이전트가 조건·설정을 고쳐 다시 계산. 3단계 이후 수치는 출력 형상 기준 유한요소 해석값(실측 전)', { x: 0.5, y: 4.98, w: 9, h: 0.22, fontSize: 8, color: C.accent3 });
s.addNotes('말 한 줄이 출처 있는 설계 명세가 되고, 처음 설계를 계산해 미달을 확인한 뒤, 3D 최적화로 재료를 재배치하고, 출력 형상을 다시 계산해 통과한 것만 제작 파일로 내보낸다. 실측은 데모 영상에서 다룸.');

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

// ---------- 5. 기술 차별성: 비교
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 기술 차별성 — 누구나 쓰면서도, 결과를 믿을 수 있다', { placeholder: 'title' });
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

// ---------- 5b. 실증 사례 소개
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 실증 사례 ① — 자전거 폰 거치대, 조건은 근거로 정한다', { placeholder: 'title' });
s.addText('AI가 사용 환경을 조사해 하중·판정 기준을 정하고, 출처를 함께 남긴다', { placeholder: 'body' });
box(s, 0.5, 1.3, 4.4, 3.55, X.tint, 'bike card');
fit(s, SH + 'v6_c_bike_full.png', 0.6, 1.4, 2.6, 2.3, 'bicycle with mount');
s.addShape(pres.shapes.OVAL, { x: 1.18, y: 1.42, w: 0.55, h: 0.4, fill: { type: 'none' }, line: { color: C.accent2, width: 2 }, objectName: 'callout ring' });
s.addShape(pres.shapes.LINE, { x: 1.73, y: 1.62, w: 1.45, h: 0.5, line: { color: C.accent2, width: 1.25 } });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 3.15, y: 1.5, w: 1.65, h: 1.75, rectRadius: 0.06, fill: { color: X.white }, line: { color: C.accent2, width: 1.5 } });
fit(s, SH + BK.rider, 3.2, 1.55, 1.55, 1.65, 'mount close-up');
T(s, '"울퉁불퉁한 길에서도 폰이 안 흔들리게, 최대한 가볍게. 3D 프린터로 뽑을 거야"', { x: 0.7, y: 3.85, w: 4.0, h: 0.85, fontSize: 12, bold: true, italic: true, color: C.text2, valign: 'middle' });
const cond = [['노면 진동', '자갈길 34.6~45.6 Hz · 48.5 g', 'ISBS 2020 실측'], ['재료', 'PETG 3D 프린트, 항복 39 MPa', '제조사 데이터시트'], ['하중', '갤럭시 S26 울트라 214 g + 거치부 40 g', '거치부 가정']];
cond.forEach((c, i) => {
  const y = 1.3 + i * 0.62;
  T(s, c[0], { x: 5.15, y, w: 1.1, h: 0.5, fontSize: 12, bold: true, color: C.accent1, valign: 'middle' });
  T(s, c[1], { x: 6.25, y, w: 2.3, h: 0.5, fontSize: 11, color: C.text1, valign: 'middle' });
  pill(s, 8.55, y + 0.11, 0.95, c[2], c[2].includes('가정') ? X.amber : X.tint, c[2].includes('가정') ? X.white : X.ink);
});
// frequency number line
const fx0 = 5.15, fw = 4.35, fmax = 120, fy = 4.05, F = v => fx0 + fw * v / fmax;
T(s, '1차 진동수 판정: 노면 진동의 2배 이상이어야 흔들림 증폭이 작다', { x: 5.15, y: 3.2, w: 4.35, h: 0.3, fontSize: 11, bold: true, color: C.text2 });
s.addShape(pres.shapes.RECTANGLE, { x: F(34.6), y: fy - 0.12, w: F(45.6) - F(34.6), h: 0.24, fill: { color: C.accent2, transparency: 30 }, line: { color: C.accent2 }, objectName: 'road band' });
s.addShape(pres.shapes.LINE, { x: fx0, y: fy, w: fw, h: 0, line: { color: C.accent3, width: 1 } });
s.addShape(pres.shapes.LINE, { x: F(91), y: fy - 0.25, w: 0, h: 0.5, line: { color: X.red, width: 1.5, dashType: 'dash' } });
[[BK.base_f, X.red, '처음 ' + BK.base_f], [BK.ai_f, X.teal, 'AI ' + BK.ai_f]].forEach(d => {
  s.addShape(pres.shapes.OVAL, { x: F(d[0]) - 0.09, y: fy - 0.09, w: 0.18, h: 0.18, fill: { color: d[1] }, line: { color: X.white, width: 1 } });
  T(s, d[2], { x: F(d[0]) - 0.5, y: fy - 0.42, w: 1.0, h: 0.22, fontSize: 10, bold: true, color: d[1] === X.red ? C.accent5 : C.accent1, align: 'center' });
});
T(s, '노면 진동', { x: F(34.6) - 0.2, y: fy + 0.15, w: 1.0, h: 0.22, fontSize: 9, color: C.accent2, bold: true });
T(s, '기준 91 Hz', { x: F(91) - 0.05, y: fy + 0.15, w: 1.0, h: 0.22, fontSize: 9, color: C.accent5, bold: true, align: 'center' });
[0, 30, 60, 90, 120].forEach(v => T(s, v + ' Hz', { x: F(v) - 0.3, y: fy + 0.38, w: 0.6, h: 0.2, fontSize: 8, color: C.accent3, align: 'center' }));
s.addNotes('자전거 전체 그림에서 주황 원이 거치대 위치, 오른쪽 확대가 AI 설계 결과 장착 모습. 조건마다 출처를 붙인다(250 g은 우리 가정). 아래 수직선: 노면 진동 대역(주황), 판정 기준 91 Hz(빨간 점선), 처음 설계 26.5 Hz는 대역 아래쪽에 가깝고 AI 설계 99.4 Hz는 기준 통과.');

// ---------- 6. 실증 결과
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 실증 사례 ① — 기준 미달 설계를 기준 통과 설계로', { placeholder: 'title' });
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
T(s, `※ 무게 = 출력용 STL, 진동수·응력 = 출력 형상 1 mm 재해석(폰+거치부 254 g, 응력은 99.9% 값). 단순 직사각형 보로 같은 기준 충족 시 약 ${BK.beam_m} g. 빨간 점선 = 판정 기준`, { x: 0.5, y: 4.93, w: 9, h: 0.25, fontSize: 8, color: C.accent3 });
s.addNotes('처음 설계는 진동·강도 모두 미달. AI 설계는 둘 다 통과하면서 같은 기준을 맞춘 단순 보강안보다 가볍다. 이전 자료의 50.0 g은 다른 클램프 기준이라 정정(같은 클램프 42.5 g).');

// ---------- 6b. TV 스탠드 실증 (보조: 제품 설계)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 실증 사례 ② — TV 스탠드: 외형은 그대로, 무게는 1/3', { placeholder: 'title' });
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

// ---------- 6c. 무선충전 스탠드 (보조: 물리 확장 — 열)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 실증 사례 ③ — 무선충전 스탠드: 같은 흐름에 열 방정식 추가', { placeholder: 'title' });
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
const ph = [['구조 (탄성)', '정적 · 진동', '입증됨', X.green], ['+ 열 (열전도)', '무선충전 스탠드: 방열판 배치', '입증됨', X.green], ['+ 광학 (PINN)', '디스플레이 광학 역설계', '계획', X.mute], ['+ 전자기', '무선충전 금속 금지 구역 계산', '계획', X.mute]];
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
