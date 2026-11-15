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
const BK = JSON.parse(fs.readFileSync(__dirname + '/bike_v14.json','utf8'));
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
pres.title = 'FormProof 발표 초안 v40';
const C = pres.SchemeColor;

pres.defineSlideMaster({ title: 'DARK', background: { color: C.text2 },
  objects: [{ placeholder: { options: { name: 'title', type: 'title', x: 0.6, y: 1.5, w: 5.2, h: 1.0, fontSize: 40, bold: true, color: C.background1, align: 'left', valign: 'top', margin: 0 }, text: '' } },
            { placeholder: { options: { name: 'body', type: 'body', x: 0.6, y: 2.6, w: 5.0, h: 1.2, fontSize: 16, color: C.accent4, align: 'left', valign: 'top', margin: 0 }, text: '' } }] });
pres.defineSlideMaster({ title: 'CONTENT', background: { color: C.background1 },
  objects: [{ placeholder: { options: { name: 'title', type: 'title', x: 0.5, y: 0.3, w: 9.0, h: 0.55, fontSize: 22, bold: true, color: C.text2, align: 'left', valign: 'middle', margin: 0 }, text: '' } },
            { placeholder: { options: { name: 'body', type: 'body', x: 0.5, y: 0.85, w: 9.0, h: 0.35, fontSize: 13, color: C.accent3, align: 'left', valign: 'top', margin: 0 }, text: '' } },
            { text: { text: 'FormProof  |  팀원 A · B · C', options: { x: 0.5, y: 5.28, w: 5, h: 0.22, fontSize: 9, color: C.accent3, margin: 0 } } }],
  slideNumber: { x: 9.0, y: 5.28, w: 0.5, h: 0.22, fontSize: 9, color: C.accent3, align: 'right' } });

const T = (s, text, o) => s.addText(text, { margin: 0, isTextBox: true, valign: 'top', color: C.text1, fontSize: 12, ...o });
const box = (s, x, y, w, h, fill, name) => s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill }, line: { color: fill }, objectName: name || 'box' });
const disc = (s, x, y, d, fill, ic, name) => { s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill }, objectName: name || 'disc' }); if (ic) s.addImage({ data: ic, x: x + d * 0.24, y: y + d * 0.24, w: d * 0.52, h: d * 0.52 }); };
const arrow = (s, x, y, w, h, col) => s.addShape(pres.shapes.RIGHT_ARROW, { x, y, w, h, fill: { color: col || C.accent2 }, line: { color: col || C.accent2 }, objectName: 'arrow' });
const pill = (s, x, y, w, text, fill, col) => { s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.28, rectRadius: 0.14, fill: { color: fill }, line: { color: fill } }); T(s, text, { x, y, w, h: 0.28, fontSize: 10, bold: true, color: col, align: 'center', valign: 'middle' }); };

pres.addSection({ title: '표지' });
// ---------- 1. 표지
let s = pres.addSlide({ masterName: 'DARK', sectionTitle: '표지' });
s.addText('FormProof', { placeholder: 'title' });
s.addText('말 · 스케치 · 사진 · 문서 · 3D 파일, 무엇으로 주든\n성능이 검증된 만들 수 있는 설계로', { placeholder: 'body' });
T(s, '물리 기반 생성형 AI  ·  팀원 A · B · C', { x: 0.6, y: 4.6, w: 5, h: 0.3, fontSize: 11, color: C.accent4 });
box(s, 5.9, 0.9, 3.7, 3.8, 'FFFFFF', 'hero card');
fit(s, SH + 'v17_hero.png', 6.0, 1.0, 3.5, 2.75, 'optimized phone mount on bicycle');
T(s, '자전거 폰 거치대 — AI가 설계한 일체형 구조', { x: 6.05, y: 3.85, w: 3.4, h: 0.3, fontSize: 11, bold: true, color: C.text2, align: 'center' });
T(s, '최대 흔들림 5.6배 → 1.3배 · 몸체 81.3 g', { x: 6.05, y: 4.15, w: 3.4, h: 0.3, fontSize: 10, color: C.accent1, align: 'center' });
s.addNotes('FormProof = Form + Proof. 형상을 성능으로 증명한다. 오른쪽은 실제 계산으로 얻은 일체형 거치대(출력용 STL, 폰 4면 고정).');

pres.addSection({ title: '요약' });
// ---------- 2. 한 장 요약 (v31: 흐름(위) → 증거 + DX(아래))
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '요약' });
s.addText("아이디어를 어떤 형태로 주든, 성능이 검증된 '만들 수 있는 설계'로", { placeholder: 'title' });
s.addText('요구 이해 → 형상 생성 → 물리 판정 · 재설계 → 제작 파일을 한 흐름으로 — 성능 예측만 하는 물리 AI와 다른 점', { placeholder: 'body' });
// ① 흐름 + 핵심 기술
const FY = 1.2;
box(s, 0.5, FY, 9.0, 1.05, X.tint, 'flow');
const FLW = [['v17_sketch.png', 0.92, '말 + 스케치', '입력 형태 무관'], ['v32_spec.png', 0.92, '설계 조건', '생성 AI가 정리\n항목별 출처'], ['v32_evo.png', 1.85, '계산 · 재설계', '물리 계산하며\n재료 배치 반복'], ['v25_asm.png', 0.92, '제작 파일', '조립도 · STL\n설명서']];
let fx = 0.6;
FLW.forEach((f, i) => { const y = FY + 0.06, tw = 0.95;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: fx, y, w: f[1], h: 0.66, rectRadius: 0.04, fill: { color: 'FFFFFF' }, line: { color: X.line, width: 0.5 }, objectName: 'thumb' });
  fit(s, SH + f[0], fx + 0.02, y + 0.02, f[1] - 0.04, 0.62, f[2]);
  T(s, f[2], { x: fx + f[1] + 0.06, y: y + 0.06, w: tw, h: 0.24, fontSize: 9, bold: true, color: C.text2 });
  T(s, f[3], { x: fx + f[1] + 0.06, y: y + 0.3, w: tw, h: 0.34, fontSize: 7, color: C.text1 });
  fx += f[1] + 0.06 + tw;
  if (i < 3) { arrow(s, fx - 0.02, y + 0.23, 0.12, 0.2); fx += 0.14; } });
T(s, [{ text: '물리 모듈  ', options: { bold: true, color: C.accent1 } }, { text: '정적 강성 · 고유진동 · 진동 응답 · 충격 강도 · 열전도 · 터치 처짐 · 출력 층간 강도   (확장: 낙하 · 피로 · 소음 · 유동 · 전자기)', options: { color: C.text1 } }],
  { x: 0.62, y: FY + 0.78, w: 8.8, h: 0.24, fontSize: 7.5, valign: 'middle' });
// ② 증거
const PY = 2.37;
box(s, 0.5, PY, 6.0, 2.6, 'E3F1F0', 'proof');
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: PY, w: 6.0, h: 2.6, rectRadius: 0.08, fill: { type: 'none' }, line: { color: X.teal, width: 1.5 }, objectName: 'proof frame' });
T(s, '대표 사례 — 자전거 폰 거치대 (말 + 스케치로 요청)', { x: 0.62, y: PY + 0.05, w: 5.8, h: 0.24, fontSize: 10, bold: true, color: C.accent1 });
[['처음 설계 (판 + 기둥)', 'v28_Rbase.png', C.accent5, 0.6], ['AI 재설계 (출력 몸체)', 'v51_Rbody.png', C.accent1, 3.08]].forEach(c => {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: c[3], y: PY + 0.33, w: 2.4, h: 1.2, rectRadius: 0.05, fill: { color: 'FFFFFF' }, line: { color: X.line, width: 0.5 }, objectName: 'pair' });
  fit(s, SH + c[1], c[3] + 0.03, PY + 0.35, 2.34, 1.16, c[0]);
  T(s, c[0], { x: c[3], y: PY + 1.55, w: 2.4, h: 0.2, fontSize: 9, bold: true, color: c[2], align: 'center' }); });
s.addImage({ path: SH + 'v30_cb.png', x: 5.55, y: PY + 0.31, w: 0.62, h: 1.24, objectName: 'legend' });
T(s, '두 설계 같은 척도', { x: 5.5, y: PY + 1.58, w: 0.95, h: 0.3, fontSize: 6.3, color: C.accent3 });
const KP = [['폰 흔들림', '77% 감소', '울퉁불퉁한 길 · 5.6 → 1.3배'], ['충격 부담', '80% 감소', '내부 응력 14.7 → 2.9 MPa'], ['폰 온도', '12 °C 낮게', '내비 사용 시 32.6 → 20.8 °C'], ['무게', '3% 가볍게', '출력 몸체 84.0 → 81.3 g'], ['범용 LLM 단독 3회', '3/3 불합격', '공진 2 · 온도 초과 1 · 17쪽']];
KP.forEach((k, i) => { const x = 0.6 + i * 1.17, y = PY + 1.82, bad = i === 4;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 1.1, h: 0.66, rectRadius: 0.06, fill: { color: bad ? 'FBECEA' : 'FFFFFF' }, line: { color: bad ? X.red : X.teal, width: 1 }, objectName: 'kpi card' });
  T(s, k[0], { x: x + 0.07, y: y + 0.04, w: 1.0, h: 0.17, fontSize: 7, bold: true, color: bad ? C.accent5 : C.text2, valign: 'middle' });
  T(s, k[1], { x: x + 0.07, y: y + 0.21, w: 1.0, h: 0.25, fontSize: 12, bold: true, color: bad ? C.accent5 : C.accent1, valign: 'middle' });
  T(s, k[2], { x: x + 0.07, y: y + 0.46, w: 1.02, h: 0.17, fontSize: 5.6, color: C.accent3, valign: 'middle' }); });
T(s, '분포 상세 → 9쪽', { x: 4.4, y: PY + 0.07, w: 2.0, h: 0.2, fontSize: 6.5, color: C.accent3, align: 'right' });
// ③ DX 제품 경쟁력 — 같은 방법론(입력 → 형상 → 물리 판정 → 제작 파일)을 제품에
box(s, 6.65, PY, 2.85, 2.6, X.ink, 'dx panel');
T(s, 'DX 제품 경쟁력으로', { x: 6.78, y: PY + 0.07, w: 2.6, h: 0.26, fontSize: 11, bold: true, color: C.background1 });
T(s, '설계자가 요구를 말하면 검증된 개선안이 나온다', { x: 6.78, y: PY + 0.33, w: 2.62, h: 0.2, fontSize: 7, color: C.accent4 });
const DX = [
  ['VD', 'TV 스탠드 · 벽걸이', '외형 그대로, 더 가볍게', '실증: 다리 무게 −69%', true],
  ['MX', '폰 · 폴더블 내부 브래킷', '더 얇게 · 열은 넓게 퍼지게', '구조 · 열 + 낙하', false],
  ['DA', '세탁기 · 에어컨 모터 마운트', '덜 떨리고 조용하게', '진동 + 음향', false],
  ['공통', '기존 부품 STEP 입력', '같은 성능 · 재료 절감', '형상 유지 경량화', false]];
DX.forEach((d, i) => { const y = PY + 0.6 + i * 0.44;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.76, y: y + 0.03, w: 0.46, h: 0.22, rectRadius: 0.11, fill: { color: X.teal }, line: { color: X.teal }, objectName: 'dx tag' });
  T(s, d[0], { x: 6.76, y: y + 0.03, w: 0.46, h: 0.22, fontSize: 7.5, bold: true, color: C.background1, align: 'center', valign: 'middle' });
  T(s, d[1], { x: 7.28, y, w: 2.15, h: 0.2, fontSize: 8, bold: true, color: C.background1 });
  T(s, [{ text: d[2], options: { color: 'D5E4E6' } }, { text: '   ' + d[3], options: { color: d[4] ? '7FD3D0' : 'F2C27B', bold: true } }], { x: 7.28, y: y + 0.2, w: 2.18, h: 0.18, fontSize: 6.3 }); });
T(s, '물리는 제품별 모듈 추가 · 흐름 그대로', { x: 6.78, y: PY + 2.38, w: 2.65, h: 0.18, fontSize: 6, color: 'A9B8BC' });
T(s, '※ 처음 설계 대비 같은 조건 해석(폰 + 고정 부품 311 g, 감쇠비 3%, 거치 35°, 발열 4 W 가정). 형상 · 물리 AI는 거치대 계열로 학습 · 검증(일체형 적용 진행 중). DX 항목은 적용 후보, 효과는 사업부 확인 필요', { x: 0.5, y: 5.05, w: 9, h: 0.18, fontSize: 6.5, color: C.accent3 });
s.addNotes('한 장 요약. 위: 말 + 스케치 → 생성 AI가 출처 있는 설계 조건으로 → 형상 AI · 물리 AI · 수치해석으로 계산 · 재설계 → 조립도 · STL · 설명서. 아래 왼쪽: 같은 요청의 처음 설계와 AI 재설계를 같은 색 척도로 비교(받침대 쪽 · 옆). 처음 설계는 판 끝이 노면 진동에 3.5배까지 흔들리고, AI 재설계는 1.2배 이하. 숫자 넷: 최대 흔들림, 충격 응력, 폰 온도, 무게. 오른쪽: 같은 엔진을 DX 제품 경쟁력에 적용하는 후보.');

pres.addSection({ title: '1. 문제 정의' });
// ---------- 3. 문제 정의 (v50: 공감 + 시각화 — 떠오른다 → 막힌다 → 서랍 속으로 / 이게 된다면)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '1. 문제 정의' });
s.addText('1. 문제 정의 — 좋은 아이디어, 바로 만들어 보고 싶었던 적 없나요?', { placeholder: 'title' });
s.addText('떠올리는 건 누구나 한다. 그런데 "정말 되는지" 확인하는 길에서 아이디어가 멈춘다', { placeholder: 'body' });
{
const AM = 'B07A1E';
const I4 = { bike: await icon(fa.FaBicycle, X.white), bulb: await icon(fa.FaLightbulb, X.white), pen: await icon(fa.FaPencilRuler, X.white),
  clock: await icon(fa.FaHourglassHalf, X.red), redo: await icon(fa.FaRedoAlt, X.red), x: await icon(fa.FaTimesCircle, X.red),
  arch: await icon(fa.FaArchive, '8A949C'), bulbG: await icon(fa.FaLightbulb, 'C9CED2'), bulbY: await icon(fa.FaLightbulb, X.amber) };
const Y0 = 1.22, HH = 2.56;
const tag = (x, y, t, c) => { box(s, x, y, 0.95, 0.24, c, 'tag'); T(s, t, { x, y, w: 0.95, h: 0.24, fontSize: 8, bold: true, color: X.white, align: 'center', valign: 'middle' }); };
// A. 떠오른다: 손 스케치 + 한마디
box(s, 0.5, Y0, 2.5, HH, 'FDF6EA', 'idea');
tag(0.62, Y0 + 0.1, '떠오른다', X.amber);
s.addImage({ data: I4.bulbY, x: 2.62, y: Y0 + 0.08, w: 0.26, h: 0.26 });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.62, y: Y0 + 0.42, w: 2.26, h: 1.08, rectRadius: 0.04, fill: { color: 'FFFFFF' }, line: { color: 'F0D9AE', width: 0.5 }, objectName: 'sketch' });
fit(s, SH + 'v17_sketch.png', 0.64, Y0 + 0.44, 2.22, 1.04, '손 스케치');
[[I4.bike, '폰이 떨려 지도가 안 보여. 만들어 볼까?'], [I4.bulb, '더 튼튼할 텐데, 증명할 방법이 없네'], [I4.pen, '더 얇게 하고 싶은데, 이 두께로 버틸까?']].forEach((q, i) => { const y = Y0 + 1.58 + i * 0.32;
  s.addShape(pres.shapes.OVAL, { x: 0.62, y: y + 0.02, w: 0.24, h: 0.24, fill: { color: X.amber }, line: { color: X.amber }, objectName: 'p' });
  s.addImage({ data: q[0], x: 0.67, y: y + 0.07, w: 0.14, h: 0.14 });
  T(s, '"' + q[1] + '"', { x: 0.92, y, w: 2.0, h: 0.28, fontSize: 7.5, italic: true, color: C.text2, valign: 'middle' }); });
// B. 그런데 현실은: 4개의 벽 (내려가는 계단)
T(s, '그런데 현실은', { x: 3.15, y: Y0 + 0.06, w: 2, h: 0.26, fontSize: 10.5, bold: true, color: C.accent5 });
const WL = [
  { img: 'v47_cad.png', q: '3D로 옮기려니', h: 'CAD를 다룰 줄 모른다', e: '스케치에서 멈춤' },
  { img: 'v48_base.png', tags: true, q: '버틸지 확인하려니', h: '계산 조건부터 막막하다', big: '67%', ref: '1', e: '맡기면 1주 이상 대기' },
  { img: 'v44_llm.png', q: 'AI에게 맡겨 보니', h: '그럴듯한데 틀렸다', big: '6.6배', ref: '2', e: '흔들림 (AI 예측 1.3배)' },
  { prints: true, q: '그냥 만들어 보니', h: '출력 · 수정만 반복', big: '45%', ref: '1', e: '일정 때문에 해석 생략' }];
const WX = 3.15, WW = 1.17, WG = 0.07;
WL.forEach((w, i) => { const x = WX + i * (WW + WG), y = Y0 + 0.38 + i * 0.07, H = HH - 0.38 - i * 0.07;
  box(s, x, y, WW, H, i === 2 ? 'FBF1EF' : 'F3F4F5', 'wall');
  s.addShape(pres.shapes.RECTANGLE, { x, y, w: WW, h: 0.05, fill: { color: X.red }, line: { color: X.red }, objectName: 'wall top' });
  T(s, w.q, { x: x + 0.08, y: y + 0.1, w: WW - 0.16, h: 0.2, fontSize: 7, color: C.accent3 });
  const iy = y + 0.32;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.08, y: iy, w: WW - 0.16, h: 0.74, rectRadius: 0.03, fill: { color: 'FFFFFF' }, line: { color: X.line, width: 0.5 }, objectName: 'wall img' });
  if (w.img) fit(s, SH + w.img, x + 0.1, iy + 0.02, WW - 0.2, 0.7, w.h);
  if (w.tags) [['하중?', 0.06, 0.06], ['고정?', 0.06, 0.46], ['기준?', 0.6, 0.46]].forEach(g => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.08 + g[1], y: iy + g[2], w: 0.42, h: 0.2, rectRadius: 0.05, fill: { color: X.red }, line: { color: X.white, width: 0.75 }, objectName: 'q tag' });
    T(s, g[0], { x: x + 0.08 + g[1], y: iy + g[2], w: 0.42, h: 0.2, fontSize: 7, bold: true, color: X.white, align: 'center', valign: 'middle' }); });
  if (w.prints) ['1차', '2차', '3차'].forEach((g, k) => { const px = x + 0.12 + k * 0.3, py = iy + 0.06 + k * 0.08;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: px, y: py, w: 0.42, h: 0.42, rectRadius: 0.03, fill: { color: 'FFFFFF' }, line: { color: X.line, width: 0.5 }, objectName: 'print' });
    fit(s, SH + 'v44_body.png', px + 0.02, py + 0.02, 0.38, 0.38, '출력 ' + g);
    T(s, g, { x: px, y: py + 0.43, w: 0.42, h: 0.14, fontSize: 6, bold: true, color: k < 2 ? X.red : C.accent3, align: 'center' });
    if (k < 2) T(s, '✕', { x: px + 0.26, y: py - 0.02, w: 0.16, h: 0.16, fontSize: 9, bold: true, color: X.red, align: 'center', valign: 'middle' }); });
  else if (w.cal) { // 달력: 해석 결과를 기다리는 7일
    const cx = x + 0.14, cw = WW - 0.28, dw = cw / 7;
    s.addShape(pres.shapes.RECTANGLE, { x: cx, y: iy + 0.1, w: cw, h: 0.14, fill: { color: X.red }, line: { color: X.red }, objectName: 'cal head' });
    T(s, '해석 결과 대기', { x: cx, y: iy + 0.1, w: cw, h: 0.14, fontSize: 6, bold: true, color: X.white, align: 'center', valign: 'middle' });
    ['월', '화', '수', '목', '금', '토', '일'].forEach((d, k) => { const dx = cx + k * dw;
      s.addShape(pres.shapes.RECTANGLE, { x: dx, y: iy + 0.24, w: dw, h: 0.36, fill: { color: 'FFFFFF' }, line: { color: X.line, width: 0.5 }, objectName: 'day' });
      T(s, d, { x: dx, y: iy + 0.25, w: dw, h: 0.12, fontSize: 5, color: C.accent3, align: 'center' });
      T(s, '×', { x: dx, y: iy + 0.34, w: dw, h: 0.24, fontSize: 10, bold: true, color: X.red, align: 'center', valign: 'middle' }); });
    T(s, '…  다음 주로', { x: cx, y: iy + 0.6, w: cw, h: 0.12, fontSize: 6, color: C.accent3, align: 'right' }); }
  else if (w.ic) s.addImage({ data: I4[w.ic], x: x + WW / 2 - 0.22, y: iy + 0.15, w: 0.44, h: 0.44 });
  if (!w.cal && !w.tags && !w.prints) s.addImage({ data: I4.x, x: x + 0.12, y: iy + 0.04, w: 0.16, h: 0.16 });
  T(s, w.h, { x: x + 0.08, y: iy + 0.8, w: WW - 0.16, h: 0.36, fontSize: 9, bold: true, color: C.text2 });
  if (w.big) T(s, [{ text: w.big }, { text: w.ref, options: { superscript: true, fontSize: 11 } }], { x: x + 0.08, y: y + H - 0.66, w: WW - 0.16, h: 0.36, fontSize: 17, bold: true, color: C.accent5, valign: 'bottom' });
  T(s, w.e, { x: x + 0.08, y: y + H - 0.3, w: WW - 0.16, h: 0.24, fontSize: 7, color: C.accent5, bold: !w.big }); });
// C. 서랍 속으로
const DX = WX + 4 * (WW + WG) + 0.04;
s.addShape(pres.shapes.CHEVRON, { x: DX - 0.04, y: Y0 + 1.5, w: 0.12, h: 0.28, fill: { color: X.mute }, line: { color: X.mute }, objectName: 'arrow' });
box(s, DX + 0.12, Y0 + 0.38, 9.5 - DX - 0.12, HH - 0.38, 'E9EBED', 'drawer');
[[0.22, 0.5], [0.62, 0.72], [0.36, 1.0]].forEach(p => s.addImage({ data: I4.bulbG, x: DX + 0.12 + p[0], y: Y0 + p[1], w: 0.22, h: 0.22, transparency: 30 }));
s.addImage({ data: I4.arch, x: DX + 0.12 + (9.5 - DX - 0.12) / 2 - 0.3, y: Y0 + 1.34, w: 0.6, h: 0.6 });
T(s, '아이디어는\n서랍 속으로', { x: DX + 0.12, y: Y0 + 2.0, w: 9.5 - DX - 0.12, h: 0.46, fontSize: 9, bold: true, color: C.accent3, align: 'center', valign: 'middle' });
// D. 이게 해결된다면: 벽 ①~④에 하나씩 답 (형상 + 조건 → 물리 → 제작 파일)
const BY2 = 3.86, BH2 = 1.0;
box(s, 0.5, BY2, 9.0, BH2, X.ink, 'wish');
T(s, '이게 해결된다면', { x: 0.64, y: BY2 + 0.1, w: 1.6, h: 0.26, fontSize: 10.5, bold: true, color: X.amber });
T(s, '특허 아이디어는 계산된 성능으로, 제품 아이디어는 기다림 없이 확인한다', { x: 0.64, y: BY2 + 0.4, w: 1.5, h: 0.52, fontSize: 7.5, color: C.accent4, valign: 'top' });
const ST = [['v17_sketch.png', '말 · 스케치', [], '입력 형태 무관'], ['v49_base.png', '형상 + 물리 조건 생성', ['①', '②'], 'CAD · 조건 설정 없이'],
  ['v51_ai.png', '물리로 확인 · 재설계', ['③'], '기준 통과까지 계산 · 재설계'], ['v47_use.png', '제작 파일로 출력', ['④'], '도면 · STL · 설명서']];
const SX0 = 2.3, SW2 = 1.8, IW = 1.42;
ST.forEach((t, i) => { const x = SX0 + i * SW2;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: BY2 + 0.08, w: IW, h: 0.58, rectRadius: 0.03, fill: { color: 'FFFFFF' }, line: { color: 'FFFFFF' }, objectName: 'wish img' });
  fit(s, SH + t[0], x + 0.02, BY2 + 0.1, IW - 0.04, 0.54, t[1]);
  t[2].forEach((n, k) => { const ox = x - 0.07 + k * 0.24;
    s.addShape(pres.shapes.OVAL, { x: ox, y: BY2 + 0.02, w: 0.22, h: 0.22, fill: { color: X.green }, line: { color: X.white, width: 0.75 }, objectName: 'solved' });
    T(s, n, { x: ox, y: BY2 + 0.02, w: 0.22, h: 0.22, fontSize: 7.5, bold: true, color: X.white, align: 'center', valign: 'middle' }); });
  if (i === 1) ['하중 ✓', '고정 ✓', '기준 ✓'].forEach((g, k) => {   // 벽②의 '?'가 '✓'로
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + IW - 0.5, y: BY2 + 0.12 + k * 0.17, w: 0.46, h: 0.15, rectRadius: 0.04, fill: { color: X.green }, line: { color: X.white, width: 0.5 }, objectName: 'ok tag' });
    T(s, g, { x: x + IW - 0.5, y: BY2 + 0.12 + k * 0.17, w: 0.46, h: 0.15, fontSize: 6, bold: true, color: X.white, align: 'center', valign: 'middle' }); });
  T(s, t[1], { x: x - 0.1, y: BY2 + 0.68, w: IW + 0.2, h: 0.17, fontSize: 8.5, bold: true, color: i === 3 ? X.amber : X.white, align: 'center' });
  T(s, t[3], { x: x - 0.1, y: BY2 + 0.84, w: IW + 0.2, h: 0.13, fontSize: 6.5, color: C.accent4, align: 'center' });
  if (i < 3) s.addShape(pres.shapes.CHEVRON, { x: x + IW + 0.13, y: BY2 + 0.26, w: 0.11, h: 0.24, fill: { color: X.amber }, line: { color: X.amber }, objectName: 'arrow' }); });
T(s, [{ text: '1', options: { superscript: true } }, { text: ' engineering.com · Dassault 「State of Simulation, Prototyping and Validation」 2022, 엔지니어 268명 (해석 SW사 후원)     ' },
  { text: '2', options: { superscript: true } }, { text: ' 범용 LLM 단독 독립 3회, 같은 해석기로 판정 (11쪽)', options: { breakLine: true } },
  { text: '※ 한마디는 흔히 겪는 상황의 예시. 그림은 이번 과제 실제 결과(스케치 · 처음 설계 · LLM 형상 · AI 설계 · 최종 설계, 색 = 같은 해석기로 계산한 흔들림). 초록 번호 = 위 벽에 대한 답' }], { x: 0.5, y: 4.92, w: 9, h: 0.3, fontSize: 6.5, color: C.accent3 });
}
s.addNotes('질문으로 시작한다 — 좋은 아이디어, 바로 만들어 보고 싶었던 적 없나요? 출퇴근길 폰이 떨려 지도가 안 보일 때, 특허 아이디어의 효과를 보여 주고 싶을 때, 더 얇게 만들고 싶은데 버틸지 모를 때. 그런데 현실은 네 번 막힌다. ① 스케치를 3D로 옮기려면 CAD를 알아야 하고, ② 버티는지 계산하려면 하중 · 고정 · 기준부터 정해야 한다. 맡기면 67%가 1주 넘게 기다린다. ③ AI에게 맡기면 그럴듯하지만, 스스로 1.3배라던 흔들림이 실제 6.6배였다. ④ 그래서 45%는 해석 없이 출력하고 고치기를 반복한다. 결국 아이디어는 서랍 속으로 들어간다. 이게 해결된다면 — 스케치 한 장에서 형상과 물리 조건이 함께 만들어지고(①②), 계산으로 확인 · 재설계되며(③), 바로 제작 파일이 나온다(④). 그게 FormProof다.');

pres.addSection({ title: '2. 기술 차별성' });
// ---------- 4. 기술 차별성: 비교 (v52: 2장 첫 쪽으로)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 기술 차별성 — 기존 기술은 한 단계씩, 잇는 일은 사람 몫', { placeholder: 'title' });
s.addText('FormProof는 기존 기술이 나누어 맡던 단계를 하나의 과정으로 잇는다 — 요구 이해부터 검증된 제작 파일까지', { placeholder: 'body' });
const cols = [['범용 LLM 단독', '조건을 추측 · 계산 없음', X.tint, C.text2], ['3D 생성 AI', '형상만 · 검증 없음', X.tint, C.text2], ['물리 AI (대리 모델)', '주어진 형상의 성능 예측', X.tint, C.text2], ['전문가 해석 · 최적화', '정확하지만 전문가 전용', X.tint, C.text2], ['FormProof', '요구부터 제작 파일까지', X.teal, C.background1]];
const crit = ['말 · 스케치 · 문서 입력', '물리 조건 자동 설정 (출처)', '형상 생성', '성능 예측 · 판정', '형상 자동 개선 (재설계)', '제작 형상 재검증 · 제작 파일', '비전문가 사용'];
const marks = [[1, 2, 1, 0, 0, 2, 1], [2, 0, 1, 0, 0, 0, 1], [0, 0, 0, 1, 2, 0, 0], [2, 0, 2, 1, 1, 2, 0], [2, 1, 1, 1, 1, 1, 2]];
const CW4 = 1.24, CX0 = 3.0;
cols.forEach((c, j) => {
  const x = CX0 + j * (CW4 + 0.08);
  box(s, x, 1.3, CW4, 0.66, c[2], 'col head');
  T(s, c[0], { x: x + 0.04, y: 1.32, w: CW4 - 0.08, h: 0.34, fontSize: 8.5, bold: true, color: c[3], align: 'center', valign: 'middle' });
  T(s, c[1], { x: x + 0.04, y: 1.65, w: CW4 - 0.08, h: 0.26, fontSize: 6.5, color: j === 4 ? C.accent4 : C.accent3, align: 'center' });
});
crit.forEach((k, i) => {
  const y = 2.06 + i * 0.4;
  if (i % 2 === 0) s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: y - 0.03, w: 9.0, h: 0.38, fill: { color: 'F7FAF9' }, line: { color: 'F7FAF9' } });
  T(s, k, { x: 0.6, y, w: 2.35, h: 0.32, fontSize: 10, color: C.text2, bold: true, valign: 'middle' });
  marks.forEach((m, j) => { const x = CX0 + j * (CW4 + 0.08) + CW4 / 2 - 0.13; s.addImage({ data: m[i] === 2 ? IC.part : m[i] ? IC.check : IC.cross, x, y: y + 0.04, w: 0.26, h: 0.26 }); });
});
T(s, '※ LLM 단독: 같은 조건 실제 실험 3회 모두 불합격(11쪽). 주황 = 일부. FormProof ✓ = 이번 시연에서 실제 수행, 주황 = 말 · 스케치만 시연(문서 · 특허 · STEP 입력 개발 중) · 비전문가 사용성 검증 예정. 상용 제품별 비교는 확인 필요', { x: 0.5, y: 4.88, w: 9, h: 0.3, fontSize: 7.5, color: C.accent3 });
s.addNotes('물리 AI(대리 모델)는 형상이 주어져야 성능을 빨리 예측한다. 형상을 누가 만들고 조건을 누가 정하고 결과를 어떻게 제작 파일로 만드는지는 사람 몫이다. 범용 생성 AI는 형상은 만들지만 성능을 확인하지 않는다. 해석 · 최적화 도구는 정확하지만 조건 설정과 판정을 전문가가 한다. FormProof는 요구 이해(생성 AI) → 형상 생성(형상 AI) → 성능 예측(물리 AI) → 정밀 판정 · 재설계(수치해석) → 제작 파일까지를 한 흐름으로 묶었다. 물리 AI는 그 안의 가속 부품이다.');

// ---------- 5. 기술 차별성: 파이프라인
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
T(s, [{ text: '구조 · 진동 · 열 · 제조 제약 (출력 방향 · 최소 두께 · 고정 외곽)', options: { bold: true, color: C.text2 } }, { text: '   →  다음: 낙하 · 피로 · 소음 · 유동 · 전자기', options: { color: C.accent3 } }], { x: 2.0, y: 4.87, w: 7.4, h: 0.28, fontSize: 8, valign: 'middle' });
s.addNotes('역할 분담: LLM은 요청 이해 · 설계 명세 · 형상 코드 생성 · 도구 실행 · 판정(계산은 하지 않음). 형상 AI(DeepSDF)가 후보 형상을 만들고, 물리 AI(신경 연산자)가 성능과 미분을 수 초에 내서 잠재 공간에서 빠르게 탐색. 고른 후보는 FEM 미분 기반 위상 최적화로 자유 형상을 정밀화하고, 출력 형상을 FEM으로 재해석해 기준 통과 시에만 제작 파일로 출력.');

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
T(s, [{ text: `예측 ${AI.pred_f} Hz · FEM ${AI.fem_f} Hz`, options: { bold: true, breakLine: true } }, { text: `후보 1개 약 ${AI.search_s}초 · ${AI.ncand}개 중 ${AI.npass}개 FEM 통과`, options: { breakLine: true } }, { text: '(학습 당시 기준 91 Hz · 폰 점질량 모델)', options: { color: C.accent3 } }], { x: cx + 0.12, y: cardY + 1.62, w: CW - 0.24, h: 0.9, fontSize: 9, color: C.text1 });
// flow strip
const FL = [[`데이터 최선`, `${AI.start_m} g`, X.mute], [`AI 탐색 후보 (${AI.search_s}초)`, `${AI.cand_m} g · ${AI.fem_f} Hz`, GEN], ['출력 형상 재검증', `${AI.cand_out_f} Hz → 미달`, X.red], ['자유 형상 정밀화 (분리형 거치대)', '30.6 g · 흔들림 1.1배', X.green]];
FL.forEach((f, i) => { const x = 0.5 + i * 2.32;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 4.02, w: 2.05, h: 0.62, rectRadius: 0.06, fill: { color: 'FFFFFF' }, line: { color: f[2], width: 1.5 }, objectName: 'flow box' });
  T(s, f[0], { x: x + 0.08, y: 4.06, w: 1.9, h: 0.24, fontSize: 8.5, color: C.accent3, align: 'center' });
  T(s, f[1], { x: x + 0.08, y: 4.3, w: 1.9, h: 0.3, fontSize: 11, bold: true, color: f[2], align: 'center' });
  if (i < 3) arrow(s, x + 2.08, 4.2, 0.2, 0.26); });
T(s, '※ CPU 2코어 · GPU 없음. 탐색 단계 질량 · 진동수는 2 mm 격자 FEM(폰+거치부 250 g), 최종 설계는 출력 형상 1 mm 재해석(340 g 강체). 물리 AI 학습 라벨은 폰을 점질량으로 둔 모델(회전 관성 미반영)', { x: 0.5, y: 4.72, w: 9, h: 0.4, fontSize: 7.5, color: C.accent3 });
s.addNotes('형상 AI는 거치대 계열 형상을 잠재 변수 16개로 압축하고, 물리 AI는 형상에서 1차 진동수를 0.2초에 예측한다(사용 구간 오차 평균 약 7%). 둘을 이어 잠재 변수를 미분으로 조정하면 데이터에 있던 가장 가벼운 합격 설계보다 11% 가벼운 후보가 약 40초에 나온다. 다만 출력 형상으로 다시 계산하면 86 Hz로 미달이라, 자유 형상 정밀화가 30.6 g · 최대 흔들림 1.1배로 마무리한다(분리형 거치대 실험). AI는 빠른 탐색, 판정은 수치해석.');
// ===== v7: 검증 관문이 걸러낸 사례
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 기술 차별성 — 그럴듯한 형상을 검증이 걸러낸다', { placeholder: 'title' });
s.addText('이번 작업 중 실제로 불합격 · 오류로 판정되어 다시 설계한 결과 4건 — 그럴듯해 보여도 계산이 통과시키지 않았다', { placeholder: 'body' });
const fails = [
  ['자전거 거치대', '폰을 점으로 본 진동 모델', '자체 점검: 폰 회전 관성 누락\n→ 진동수 과대 (178 → 실제 98.5 Hz)', '폰을 관성 있는 강체로 재모델링\n→ 전 설계 재평가 · 재최적화'],
  ['TV 스탠드 다리', '3D 격자 위상최적화', '격자보다 가는 부재 · 중간 밀도 잔존\n→ 출력 형상 재검증 3회 불합격', '판재 평면 최적화로 전환\n→ 124 g · 흔들림 0.23 mm 통과'],
  ['무선충전 방열판', '내부 방열 구조 최적화 v1', '중간 밀도(회색) 형상\n→ 실제 제작 불가 판정', '실제 제품 구조 기준 재정의\n→ 알루미늄 판금 2장 형상'],
  ['자전거 거치대 일체형', '1차 일체형 결과 (검토에서 발견)', '폰을 잡는 형상 없음\n→ 충격 시 빠지는 힘 79 N > 버티는 힘 11 N', '4면 고정(걸이 · 집게 · 잠금)\n→ 재최적화 · 출력 몸체 재검증 통과']];
fails.forEach((f, i) => {
  const x = 0.5 + i * 2.27;
  box(s, x, 1.3, 2.15, 3.0, X.tint, 'fail card');
  T(s, f[0], { x: x + 0.12, y: 1.4, w: 1.95, h: 0.32, fontSize: 11, bold: true, color: C.text2 });
  T(s, f[1], { x: x + 0.12, y: 1.72, w: 1.95, h: 0.28, fontSize: 8, color: C.accent3 });
  s.addImage({ data: IC2.x, x: x + 0.15, y: 2.18, w: 0.28, h: 0.28 });
  T(s, i === 3 ? '검토 발견 → 계산 확인' : '검증 불합격', { x: x + 0.48, y: 2.17, w: 1.65, h: 0.3, fontSize: 10, bold: true, color: C.accent5, valign: 'middle' });
  T(s, f[2], { x: x + 0.12, y: 2.55, w: 1.95, h: 0.65, fontSize: 8, color: C.text1 });
  s.addShape(pres.shapes.DOWN_ARROW, { x: x + 0.93, y: 3.25, w: 0.3, h: 0.25, fill: { color: C.accent2 }, line: { color: C.accent2 } });
  s.addImage({ data: IC2.ok, x: x + 0.15, y: 3.6, w: 0.24, h: 0.24 });
  T(s, f[3], { x: x + 0.44, y: 3.57, w: 1.66, h: 0.7, fontSize: 8, bold: true, color: C.green });
});
T(s, '검증이 없었다면 네 결과 모두 그대로 제작 파일이 됐을 것 — 노면 자료 오독(자갈길 최대값 → 조약돌길 중앙값)도 같은 점검에서 정정', { x: 0.5, y: 4.55, w: 9, h: 0.28, fontSize: 10.5, bold: true, color: C.accent1 });
s.addNotes('실제 작업 로그 기준. 검증 모듈이 출력 형상을 다시 계산하거나 제작 가능성을 판정해 불합격을 냈고, 에이전트가 방식을 바꿔 재설계했다.');

pres.addSection({ title: '3. 실증' });
// ===== v14: 말 한 줄에서 제작 파일까지 (6단계)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '3. 실증' });
s.addText('3. 실증 — 자전거 거치대: 말 한 줄에서 제작 파일까지', { placeholder: 'title' });
s.addText('각 단계의 산출물이 다음 단계의 입력이 된다', { placeholder: 'body' });
const QW = 2.9, QH = 1.72;
const qcard = (i, title, tag) => {
  const x = 0.5 + (i % 3) * (QW + 0.15), y = 1.3 + Math.floor(i / 3) * (QH + 0.12);
  box(s, x, y, QW, QH, X.tint, 'step card');
  disc(s, x + 0.1, y + 0.1, 0.3, X.teal, null, 'num');
  T(s, String(i + 1), { x: x + 0.1, y: y + 0.1, w: 0.3, h: 0.3, fontSize: 11, bold: true, color: C.background1, align: 'center', valign: 'middle' });
  T(s, title, { x: x + 0.48, y: y + 0.1, w: QW - 0.55, h: 0.3, fontSize: 11.5, bold: true, color: C.text2, valign: 'middle' });
  if (tag) T(s, tag, { x: x + QW - 1.15, y: y + 0.1, w: 1.05, h: 0.3, fontSize: 8, color: C.accent3, align: 'right', valign: 'middle' });
  return [x, y]; };
let [qx, qy] = qcard(0, '입력', '말 + 스케치');
T(s, '"울퉁불퉁한 길에서도 폰이 안 흔들리게, 최대한 가볍게. 3D 프린터로 뽑을 거야"', { x: qx + 0.15, y: qy + 0.5, w: 1.38, h: 0.85, fontSize: 9, italic: true, color: C.text2 });
fit(s, SH + 'v17_sketch.png', qx + 1.55, qy + 0.45, 1.28, 0.9, 'input sketch');
T(s, '+ 스케치 · 핸들바 Ø31.8 · 모든 폰', { x: qx + 0.15, y: qy + 1.32, w: QW - 0.3, h: 0.28, fontSize: 9, color: C.accent3 });
[qx, qy] = qcard(1, '설계 명세', 'AI 작성 · 출처 포함');
[['하중', '폰 + 고정 부품 311 g · 관성 포함'], ['흔들림', '10–100 Hz 전달률 최소 (ISBS 2020)'], ['충격', '48.5 g (같은 실측)'], ['재료', 'PETG 39 MPa ÷ 1.5 → 26 MPa'], ['제작', 'PETG 층간 강도 · 폰 4면 고정']].forEach((r, i) => {
  T(s, r[0], { x: qx + 0.15, y: qy + 0.5 + i * 0.235, w: 0.5, h: 0.23, fontSize: 9, bold: true, color: C.accent1 });
  T(s, r[1], { x: qx + 0.65, y: qy + 0.5 + i * 0.235, w: QW - 0.75, h: 0.23, fontSize: 9, color: C.text1 }); });
[qx, qy] = qcard(2, '처음 설계 계산', '판정: 미달');
fit(s, SH + 'v16_base.png', qx + 0.08, qy + 0.45, 1.45, 1.2, 'base');
T(s, [{ text: '5.6배', options: { bold: true, color: C.accent5, fontSize: 15, breakLine: true } }, { text: '최대 흔들림 (30.5 Hz 공진)', options: { fontSize: 8, color: C.accent3, breakLine: true } }, { text: '+32.6 °C', options: { bold: true, color: C.accent5, fontSize: 15, breakLine: true } }, { text: '폰 온도 상승 > 21', options: { fontSize: 8, color: C.accent3 } }], { x: qx + 1.58, y: qy + 0.48, w: 1.3, h: 1.2 });
[qx, qy] = qcard(3, '3D 위상최적화', '반복 계산');
const EV4 = JSON.parse(fs.readFileSync(__dirname + '/evo_v16.json', 'utf8'));
s.addChart(pres.charts.LINE, [{ name: '무게', labels: EV4.it.map(String), values: EV4.mass }], {
  x: qx + 0.05, y: qy + 0.42, w: QW - 0.1, h: 1.05, chartColors: [X.teal], lineSize: 2, lineDataSymbol: 'none',
  catAxisLabelColor: X.mute, valAxisLabelColor: X.mute, catAxisLabelFontSize: 7, valAxisLabelFontSize: 7, catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt',
  valGridLine: { color: 'DDE5E4', size: 0.5 }, catGridLine: { style: 'none' }, showLegend: false, catAxisLabelFrequency: 10, catAxisLabelRotate: 0, valAxisMinVal: 0 });
T(s, `무게 ${EV4.mass[0]} → ${EV4.mass[EV4.mass.length - 1]} g (격자) · 진동 · 열 · 터치 제약`, { x: qx + 0.15, y: qy + 1.45, w: QW - 0.3, h: 0.24, fontSize: 8.5, color: C.accent3 });
[qx, qy] = qcard(4, '최종 형상 검증', '판정: 통과');
fit(s, SH + 'v15_grip.png', qx + 0.08, qy + 0.45, 1.45, 1.2, 'final');
[['1.27배', '최대 흔들림'], ['+20.8 °C', '폰 온도 ≤ 21'], ['층간 2.2', '≤ 10.9 MPa']].forEach((r, i) => {
  s.addImage({ data: IC2.ok, x: qx + 1.6, y: qy + 0.55 + i * 0.37, w: 0.18, h: 0.18 });
  T(s, [{ text: r[0], options: { bold: true, color: C.green, breakLine: true } }, { text: r[1], options: { fontSize: 8, color: C.accent3 } }], { x: qx + 1.83, y: qy + 0.5 + i * 0.37, w: 1.05, h: 0.36, fontSize: 10.5 }); });
[qx, qy] = qcard(5, '제작 파일', '');
fit(s, SH + 'v16_dwg.png', qx + 0.1, qy + 0.45, QW - 0.2, 0.95, 'drawing');
T(s, 'STL 4종 · 도면 · 설명서 (몸체 81.3 g)', { x: qx + 0.15, y: qy + 1.42, w: QW - 0.3, h: 0.24, fontSize: 9, bold: true, color: C.accent1 });
T(s, '※ 수치 = 2 mm 격자 유한요소 해석(폰 + 고정 부품 311 g 강체, 감쇠비 3% · 발열 4 W 가정). 흔들림 = 핸들바 대비 폰 진동 배율, 두 방향 중 큰 값. 최종 형상 검증 = 출력용 몸체(81.3 g) 재해석 값. 이번 사례는 위상 최적화(수치해석) 경로로 설계', { x: 0.5, y: 4.98, w: 9, h: 0.22, fontSize: 7.5, color: C.accent3 });
s.addNotes('말 한 줄이 출처 있는 설계 명세가 되고, 처음 설계(판 + 기둥)를 계산하면 30.5 Hz에서 공진해 흔들림이 최대 5.6배이고 폰 온도도 32.6 °C 오른다. 3D 위상최적화로 재료를 재배치한 뒤 출력 형상을 다시 계산해 통과한 것만 제작 파일로 내보낸다.');

// ===== v24: 물리로 본 차이 (분포)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '3. 실증' });
s.addText('3. 실증 — 물리로 본 차이: 같은 조건에서 계산한 분포', { placeholder: 'title' });
s.addText('두 설계를 같은 색 척도로 — 빨강일수록 나쁨. 처음 설계의 문제 지점이 AI 재설계에서 사라진다', { placeholder: 'body' });
T(s, '처음 설계 (판 + 기둥)', { x: 1.45, y: 1.22, w: 3.6, h: 0.26, fontSize: 11, bold: true, color: C.accent5, align: 'center' });
T(s, 'AI 재설계 (출력 몸체)', { x: 5.15, y: 1.22, w: 3.6, h: 0.26, fontSize: 11, bold: true, color: C.accent1, align: 'center' });
const PR = [
  { lab: '흔들림', sub: '노면 진동 10–100 Hz\n핸들바 대비 배율', a: 'v28_Rbase.png', b: 'v51_Rbody.png', ta: '30.5 Hz 공진 — 판 끝 3.5배', tb: '171 Hz — 전체 1.2배 이하', cb: 'v26_cb_R.png' },
  { lab: '충격', sub: '48.5 g 위아래\nvon Mises 응력', a: 'v28_Vbase.png', b: 'v51_Vbody.png', ta: '판 뿌리 집중 — 최대 14.7 MPa', tb: '분산 — 최대 2.9 MPa', cb: 'v26_cb_V.png' },
  { lab: '열', sub: '폰 발열 4 W\n온도 상승', a: 'v25_Tbase.png', b: 'v51_Tbody.png', ta: '덮인 폰 뒷면 +32.6 °C', tb: '열린 뒷면 +20.8 °C', cb: 'v26_cb_T.png' }];
PR.forEach((r, i) => { const y = 1.5 + i * 1.18, H = 1.1;
  box(s, 0.5, y, 0.88, H, X.ink, 'row label');
  T(s, r.lab, { x: 0.5, y: y + 0.18, w: 0.88, h: 0.3, fontSize: 12, bold: true, color: C.background1, align: 'center' });
  T(s, r.sub, { x: 0.53, y: y + 0.5, w: 0.82, h: 0.5, fontSize: 6.5, color: C.accent4, align: 'center' });
  [[r.a, r.ta, 1.45, C.accent5], [r.b, r.tb, 5.15, C.accent1]].forEach(c => {
    box(s, c[2], y, 3.6, H, 'FFFFFF', 'map');
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: c[2], y, w: 3.6, h: H, rectRadius: 0.06, fill: { type: 'none' }, line: { color: X.line, width: 0.75 }, objectName: 'map frame' });
    fit(s, SH + c[0], c[2] + 0.04, y + 0.04, 2.55, H - 0.08, r.lab);
    T(s, c[1], { x: c[2] + 2.62, y: y + 0.1, w: 0.94, h: H - 0.2, fontSize: 8.5, bold: true, color: c[3], valign: 'middle' }); });
  s.addImage({ path: SH + r.cb, x: 8.85, y: y + 0.02, w: 0.42, h: H - 0.04, objectName: 'colorbar' }); });
T(s, '※ 같은 조건 해석(폰 + 고정 부품 311 g, 감쇠비 3%, 35°, 발열 4 W · 주행풍 가정). 각 줄은 두 설계에 같은 색 척도 적용. 응력은 99.9% 값 기준 최대', { x: 0.5, y: 5.06, w: 9, h: 0.2, fontSize: 7, color: C.accent3 });
s.addNotes('각 줄은 두 설계에 같은 색 척도를 썼다. 빨강일수록 나쁘다. 흔들림: 노면 10–100 Hz 진동 동안 각 지점이 핸들바보다 몇 배 흔들리는지(RMS). 충격: 48.5 g 위아래 충격 때 응력. 열: 폰 발열 4 W 때 온도 상승. 위: 1차 진동 모드. 처음 설계는 30.5 Hz에서 판 끝이 크게 흔들리고 이 진동수가 노면 진동과 겹쳐 최대 5.6배 흔들린다. AI 재설계(출력 몸체)는 1차가 171 Hz로 올라가 노면 대역 밖이고 실제 흔들림은 최대 1.27배. 아래: 폰 발열 4 W일 때 온도. 처음 설계는 판이 폰 뒷면을 덮어 열이 갇히고(+32.6 °C), AI 재설계는 뒷면을 열어 열을 내보낸다(+20.8 °C).');

// ===== v25: 구조 — 무엇이 폰을 잡나 + 조립도
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '3. 실증' });
s.addText('3. 실증 — 실제로 만들 수 있다: 구조 · 조립도 · 부품', { placeholder: 'title' });
s.addText('폰을 4면에서 잡는 부품은 고정 영역, 그 사이 삼각 프레임은 계산이 만들었다 — 출력 4개 + 시판 부품으로 조립', { placeholder: 'body' });
box(s, 0.5, 1.25, 3.3, 3.7, 'FFFFFF', 'labeled');
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 1.25, w: 3.3, h: 3.7, rectRadius: 0.06, fill: { type: 'none' }, line: { color: X.line, width: 0.75 }, objectName: 'labeled frame' });
fit(s, SH + 'v25_labeled.png', 0.55, 1.3, 3.2, 3.6, 'labeled structure');
box(s, 3.9, 1.25, 3.3, 3.7, 'FFFFFF', 'asm dwg');
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 3.9, y: 1.25, w: 3.3, h: 3.7, rectRadius: 0.06, fill: { type: 'none' }, line: { color: X.line, width: 0.75 }, objectName: 'asm frame' });
fit(s, SH + 'v25_asm.png', 3.95, 1.3, 3.2, 3.6, 'assembly drawing');
T(s, '부품 (합계 출력 96.8 g)', { x: 7.32, y: 1.25, w: 2.2, h: 0.24, fontSize: 9.5, bold: true, color: C.text2 });
[['출력', '몸체 × 1', '프레임 + 집게 하우징 + 레일 + 아래 걸이 일체'], ['출력', '슬라이드 집게 × 2', '스프링 포켓 · 화면 쪽 이탈 방지'], ['출력', '위쪽 슬라이드 걸이 × 1', '25 mm 이동 · M3 잠금'],
 ['구매', '압축 스프링 × 2', '바깥지름 5 mm (사양 확인 필요)'], ['구매', 'M3 볼트 · 너트', '멈춤 핀 2 + 잠금 3'], ['구매', 'M4 볼트 · 너트', '핸들바 조임']].forEach((r, i) => { const y = 1.55 + i * 0.47;
  pill(s, 7.32, y + 0.02, 0.5, r[0], r[0] === '출력' ? X.teal : X.amber, X.white);
  T(s, r[1], { x: 7.88, y, w: 1.65, h: 0.2, fontSize: 8.5, bold: true, color: C.text2 });
  T(s, r[2], { x: 7.88, y: y + 0.2, w: 1.65, h: 0.24, fontSize: 7, color: C.text1 }); });
box(s, 7.32, 4.42, 2.18, 0.52, X.tint, 'fit');
T(s, '폰 폭 64–90 · 두께 6–14 mm · ≤ 290 g\n핸들바 31.8 mm · PETG 채움 100%', { x: 7.4, y: 4.42, w: 2.05, h: 0.52, fontSize: 7, color: C.text2, valign: 'middle' });
T(s, '※ 가운데 = 조립도(3면도 · 부품표 · 표제란, A3). 부품도 3장 · STL · STEP · 조립 설명서는 제작 파일 묶음에 포함', { x: 0.5, y: 5.02, w: 9, h: 0.2, fontSize: 7, color: C.accent3 });
s.addNotes('왼쪽은 최종 거치대에서 각 부분이 하는 일. 아래 걸이가 폰 아래 끝을, 스프링 집게가 양옆을, 위쪽 걸이가 위 끝을 잡고, 위쪽 받침이 뒷면을 받친다. 이 부분들은 제작 조건으로 고정해 두고, 클램프에서 받침부까지를 잇는 삼각 프레임만 AI가 계산으로 만들었다. 오른쪽은 조립도: 3면도, 부품 번호, 부품표, 표제란.');

// ===== v38: 범용 LLM 단독 vs FormProof (일체형 · 같은 조건)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '3. 실증' });
s.addText('3. 실증 — 범용 LLM 단독 vs FormProof: 같은 요청, 같은 검증', { placeholder: 'title' });
s.addText('그럴듯한 3개 안 모두 불합격, 스스로 한 예측도 빗나갔다 — 계산 없이는 어느 안이 맞는지 모른다', { placeholder: 'body' });
const LL = [
  { name: 'LLM 단독 A', img: 'v38_L1.png', crit: '≥ 90 Hz', pf: 95, f: 150.6, ps: 1.2, pk: 1.37, m: 87.7, t: 22.6, ok: false, note: '폰 온도 초과' },
  { name: 'LLM 단독 B', img: 'v38_L2.png', crit: '≥ 60 Hz', pf: 70, f: 109.6, ps: 1.25, pk: 2.95, m: 79.8, t: 20.5, ok: false, note: '앞뒤 흔들림 2.95배' },
  { name: 'LLM 단독 C', img: 'v38_L3.png', crit: '≥ 80 Hz', pf: 85, f: 89.7, ps: 1.3, pk: 6.57, m: 80.0, t: 20.6, ok: false, note: '위쪽 레일 공진 6.6배' },
  { name: 'FormProof', img: 'v28_Ropt.png', crit: '계산으로 판정', pf: null, f: 153.9, ps: null, pk: 1.39, m: 77.1, t: 20.7, ok: true, note: '모든 기준 통과 (설계 단계)' }];
const LW = 2.12;
LL.forEach((d, i) => { const x = 0.5 + i * (LW + 0.15), fp = d.ok;
  box(s, x, 1.28, LW, 3.4, fp ? 'E3F1F0' : X.tint, 'llm card');
  if (fp) s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.28, w: LW, h: 3.4, rectRadius: 0.08, fill: { type: 'none' }, line: { color: X.teal, width: 2 }, objectName: 'fp frame' });
  T(s, d.name, { x: x + 0.1, y: 1.34, w: LW - 0.2, h: 0.24, fontSize: 11, bold: true, color: fp ? C.accent1 : C.text2 });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.06, y: 1.6, w: LW - 0.12, h: 0.86, rectRadius: 0.04, fill: { color: 'FFFFFF' }, line: { color: X.line, width: 0.5 }, objectName: 'img' });
  fit(s, SH + d.img, x + 0.08, 1.62, LW - 0.16, 0.82, d.name);
  const R = [['스스로 정한 기준', d.crit, C.text1], ['예측 → 실제 1차', d.pf ? `${d.pf} → ${d.f} Hz` : `${d.f} Hz`, C.text1], ['예측 → 실제 최대 흔들림', d.ps ? `${d.ps} → ${d.pk}배` : `${d.pk}배`, fp ? X.green : (d.pk > 2 ? C.accent5 : C.text1)], ['무게', d.m + ' g', C.text1], ['폰 온도 상승 (≤ 21)', '+' + d.t + ' °C', d.t > 21 ? C.accent5 : (fp ? X.green : C.text1)]];
  R.forEach((r, k) => { const y = 2.55 + k * 0.29;
    T(s, r[0], { x: x + 0.1, y, w: 1.1, h: 0.27, fontSize: 7.5, color: C.accent3, valign: 'middle' });
    T(s, r[1], { x: x + 1.05, y, w: LW - 1.13, h: 0.27, fontSize: 9, bold: true, color: r[2], align: 'right', valign: 'middle' }); });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.1, y: 4.06, w: LW - 0.2, h: 0.5, rectRadius: 0.06, fill: { color: fp ? X.teal : 'FBECEA' }, line: { color: fp ? X.teal : X.red, width: 0.75 }, objectName: 'verdict' });
  T(s, (fp ? '통과 — ' : '불합격 — ') + d.note, { x: x + 0.14, y: 4.06, w: LW - 0.28, h: 0.5, fontSize: 8.5, bold: true, color: fp ? C.background1 : C.accent5, align: 'center', valign: 'middle' }); });
T(s, '※ LLM 단독 = 도구 · 계산 없이 같은 요청 · 같은 일체형 조건(35°, 같은 걸이 · 집게 · 레일, 311 g)을 받은 독립 세션 3회(Claude, 2026-11-15). 판정은 모두 같은 2 mm 격자 FEM · 감쇠비 3% · 발열 4 W. 흔들림 = 핸들바 대비 최대(10–100 Hz, 위아래 · 앞뒤 중 큰 값). 그림 색 = 같은 척도의 흔들림 분포. FormProof 값 = 출력 변환 전 최적화 결과(LLM 안과 같은 단계). 출력 몸체(81.3 g)도 재해석 통과(20쪽)', { x: 0.5, y: 4.74, w: 9, h: 0.4, fontSize: 7, color: C.accent3 });
s.addNotes('같은 요청과 같은 일체형 조건을 도구 없는 LLM 세션 세 개에 줬다. 세 세션 모두 그럴듯한 트러스 · 스파인 구조를 냈고, 스스로 진동 기준(60~90 Hz)과 흔들림 1.2~1.3배를 예측했다. 같은 해석기로 재 보니 A는 흔들림은 1.37배로 양호했지만 폰 뒷면을 덮어 온도 기준(21 °C)을 넘었고 10 g 더 무거웠다. B는 앞뒤로 2.95배, C는 위쪽 레일이 공진해 6.6배 흔들렸다. 예측한 진동수도 A는 실제보다 낮게, B · C는 크게 빗나갔다. 결론: LLM이 우연히 괜찮은 안을 낼 수는 있지만, 계산 없이는 어느 안이 맞는지 알 수 없다. FormProof는 모든 기준을 계산으로 확인하며 가장 가벼운 안을 냈다.');

pres.addSection({ title: '4. DX 기여 · 확장' });
// ---------- 7. 사업·조직 기여
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '4. DX 기여 · 확장' });
s.addText('4. DX 기여 — 설계 단계마다, 누구나 성능을 확인하고 개선한다', { placeholder: 'title' });
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
T(s, [{ text: '−69%', options: { fontSize: 18, bold: true, color: C.accent1 } }, { text: '  다리 무게 · 흔들림 0.23 mm · 넘어짐 통과', options: { fontSize: 7.5, color: C.text1 } }], { x: 6.42, y: 3.1, w: 3.0, h: 0.56, valign: 'middle' });
// 적용 대상
T(s, '적용 대상 — 같은 엔진, 하중 · 재료 · 기준만 바꿔서', { x: 0.5, y: 3.88, w: 6, h: 0.24, fontSize: 10, bold: true, color: C.text2 });
[['VD', 'TV 스탠드 · 벽걸이', '실증 −69%', X.green], ['MX', '폰 · 폴더블 내부 브래킷', '구조 · 열 · 낙하', X.teal], ['DA', '세탁기 · 에어컨 모터 마운트', '진동 · 음향', X.teal], ['공통', '특허 아이디어 · 기존 부품(STEP)', '성능 근거 · 경량화', X.ink]].forEach((t, i) => { const x = 0.5 + i * 2.27;
  pill(s, x, 4.16, 0.6, t[0], t[3], X.white);
  T(s, [{ text: t[1], options: { bold: true, color: C.text2, breakLine: true } }, { text: t[2], options: { color: C.accent3 } }], { x: x + 0.66, y: 4.12, w: 1.58, h: 0.5, fontSize: 8 }); });
T(s, '※ TV 스탠드: 65형 · 알루미늄 10 mm 판재 · 외곽 고정, 출력 형상 3D 재계산(상세 15쪽). MX · DA 항목은 적용 후보로 사업부 확인 필요. 정량 효과(해석 의뢰 기간, 시제품 반복 횟수)는 담당자 확인 필요', { x: 0.5, y: 4.78, w: 9, h: 0.36, fontSize: 7, color: C.accent3 });
s.addNotes('기여 주체는 방법론. 단계별로 지금 방식과 적용 후를 비교하고, VD TV 스탠드에서 외형을 유지한 채 다리 무게 69%를 줄인 실증을 보인다. MX · DA는 같은 엔진의 적용 후보.');

// ---------- 8. 확장성·파급 효과
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '4. DX 기여 · 확장' });
s.addText('4. 확장성·파급 효과 — 제품은 같은 엔진으로, 물리는 모듈로', { placeholder: 'title' });
s.addText('같은 흐름(입력 → 설계 명세 → 계산 → 재설계 → 검증 → 출력)을 유지한 채 넓혀 간다', { placeholder: 'body' });
// two axes
box(s, 0.5, 1.3, 4.35, 2.55, X.tint, 'product axis');
T(s, '제품 확장 — 같은 물리(구조), 다른 제품', { x: 0.65, y: 1.4, w: 4.1, h: 0.3, fontSize: 12, bold: true, color: C.text2 });
pill(s, 3.75, 1.42, 0.95, '입증됨', X.green, X.white);
[['TV 스탠드', '정적 강성 · 넘어짐', 'v6_c_tv_foot_opt.png'], ['자전거 거치대', '진동 · 열 · 충격', 'v47_use.png']].forEach((p, i) => {
  const x = 0.65 + i * 2.1;
  box(s, x, 1.8, 1.95, 1.4, X.white, 'case');
  fit(s, SH + p[2], x + 0.05, 1.85, 1.85, 1.0, p[0]);
  T(s, p[0], { x, y: 2.85, w: 1.95, h: 0.2, fontSize: 9.5, bold: true, color: C.text2, align: 'center' });
  T(s, p[1], { x, y: 3.03, w: 1.95, h: 0.18, fontSize: 8.5, color: C.accent3, align: 'center' });
});
T(s, '하중 · 재료 · 고정 위치 · 판정 기준만 바꿔 다른 설계 문제를 풂', { x: 0.65, y: 3.35, w: 4.1, h: 0.4, fontSize: 10, color: C.text1 });
box(s, 5.15, 1.3, 4.35, 2.55, X.tint, 'physics axis');
T(s, '물리 확장 — 방정식 모듈 추가', { x: 5.3, y: 1.4, w: 4.1, h: 0.3, fontSize: 12, bold: true, color: C.text2 });
const ph = [['구조 (탄성)', '정적 · 진동', '입증됨', X.green], ['+ 열 (열전도)', '무선충전 스탠드: 방열판 배치', '입증됨', X.green], ['+ 낙하 · 피로 · 소음', '폰 · 가전 기구 부품 신뢰성', '다음 단계', X.mute], ['+ 전자기', '무선충전 금속 금지 구역 계산', '다음 단계', X.mute]];
ph.forEach((p, i) => {
  const y = 1.82 + i * 0.5;
  s.addImage({ data: [IC.cogs, IC.heat, IC.bulb, IC.bolt][i], x: 5.3, y: y + 0.07, w: 0.3, h: 0.3 });
  T(s, p[0], { x: 5.7, y, w: 1.45, h: 0.44, fontSize: 10.5, bold: true, color: C.text2, valign: 'middle' });
  T(s, p[1], { x: 7.15, y, w: 1.4, h: 0.44, fontSize: 8.5, color: C.text1, valign: 'middle' });
  pill(s, 8.55, y + 0.08, 0.85, p[2], p[3], X.white);
});
T(s, '해커톤 이후', { x: 0.5, y: 3.98, w: 2, h: 0.26, fontSize: 11, bold: true, color: C.accent1 });
[['입력 확장', '문서 · 특허 · STEP 입력'], ['자동 실행', '에이전트가 단계 실행 · 검증 리포트'], ['물리 모듈', '낙하 · 피로 → 전자기'], ['시범 적용', 'VD 스탠드 실제 설계 과제']].forEach((r, i) => { const x = 0.5 + i * 2.27;
  box(s, x, 4.28, 2.15, 0.58, X.tint, 'road');
  T(s, [{ text: (i + 1) + '  ' + r[0], options: { bold: true, color: C.text2, breakLine: true } }, { text: r[1], options: { color: C.text1 } }], { x: x + 0.1, y: 4.3, w: 1.98, h: 0.54, fontSize: 8.5, valign: 'middle' });
  if (i < 3) s.addShape(pres.shapes.CHEVRON, { x: x + 2.16, y: 4.48, w: 0.09, h: 0.18, fill: { color: X.amber }, line: { color: X.amber } }); });
T(s, '파급: 생성형 AI 결과에 물리 검증을 붙이는 관문은 다른 생성형 AI 과제에도 재사용 · 설계가 쌓일수록 물리 AI가 정확해져 계산 시간 단축', { x: 0.5, y: 4.92, w: 9, h: 0.24, fontSize: 7.5, color: C.accent3 });
s.addNotes('확장은 두 축. 제품 확장은 두 사례로 입증(같은 구조 방정식, 다른 하중·재료·기준). 물리 확장은 방정식 모듈 추가 구조로 설명하고, 열은 무선충전 스탠드와 거치대(폰 온도 제약)로 입증. 낙하·피로·소음·전자기는 다음 단계.');

pres.addSection({ title: '마무리' });
// ---------- 9. 마무리
s = pres.addSlide({ masterName: 'DARK', sectionTitle: '마무리' });
T(s, '형상을\n성능으로 증명한다', { x: 0.6, y: 1.5, w: 5.0, h: 1.4, fontSize: 32, bold: true, color: C.background1 });
T(s, '어떤 형태의 아이디어든, 검증된 제작 파일로', { x: 0.6, y: 3.05, w: 5.0, h: 0.4, fontSize: 16, color: C.accent4 });
box(s, 5.9, 1.1, 3.7, 3.2, 'FFFFFF', 'final card');
fit(s, SH + 'v17_hero.png', 6.0, 1.25, 3.5, 2.9, 'final design');

pres.addSection({ title: '부록' });
// ---------- 6b. TV 스탠드 실증 (보조: 제품 설계)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '부록' });
s.addText('부록. TV 스탠드 — 외형은 그대로, 무게는 1/3', { placeholder: 'title' });
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

// ---------- 2b. 입력
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '부록' });
s.addText('부록. 입력 → 설계 명세 — 어떤 형태의 아이디어든 같은 형식으로', { placeholder: 'title' });
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

// ===== v14: 요청 한 줄 → 설계 명세 (메인 사례)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '부록' });
s.addText('부록. 자전거 거치대 — 요청 한 줄을 물리 조건으로', { placeholder: 'title' });
s.addText('말의 뜻을 계산할 수 있는 지표로 바꾸고, 각 수치에 출처를 붙인다', { placeholder: 'body' });
box(s, 0.5, 1.3, 2.35, 2.55, X.ink, 'request');
T(s, '처음 요청', { x: 0.65, y: 1.42, w: 2.1, h: 0.24, fontSize: 9.5, bold: true, color: C.accent4 });
T(s, '"울퉁불퉁한 길에서도 폰이 안 흔들리게, 최대한 가볍게. 3D 프린터로 뽑을 거야"', { x: 0.65, y: 1.7, w: 2.1, h: 1.15, fontSize: 12.5, italic: true, bold: true, color: C.background1 });
T(s, '스케치 — 위치 · 각도 · 피할 곳', { x: 0.65, y: 2.92, w: 2.1, h: 0.22, fontSize: 9, bold: true, color: C.accent4 });
fit(s, SH + 'v17_sketch.png', 0.62, 3.14, 2.11, 0.66, 'input sketch');
arrow(s, 2.92, 2.4, 0.26, 0.34);
const RQ = [
  ['"안 흔들리게"', '핸들바 → 폰 진동 전달 최소', '10–100 Hz 평균 전달률 · 최대 공진 배율', '조약돌길 실측, 중앙 진동수 34.6–45.6 Hz (ISBS 2020)'],
  ['"울퉁불퉁한 길"', '충격 48.5 g에도 안 부러짐', '응력 ≤ 26 MPa · 층간 ≤ 10.9 MPa', '같은 실측 · PETG 항복 39 MPa ÷ 1.5'],
  ['"최대한 가볍게"', '무게 최소', '출력 몸체 g (폰 고정부 포함)', '—'],
  ['"모든 폰"', '폭 64–90 · 두께 6–14 mm · ≤ 290 g', '4면 고정: 위 · 아래 걸이 + 스프링 집게 + 잠금', '케이스 포함 시판 범위 (폴더블 펼침 제외)'],
  ['"방열"', '폰 발열이 몸체에 갇히지 않게', '폰 온도 상승 ≤ 21 °C', '발열 4 W · 주행풍 가정 (확인 필요)']];
const RX = [3.28, 4.45, 6.0, 7.7], RW = [1.15, 1.53, 1.68, 1.82];
['표현', '물리 해석', '판정 지표', '근거'].forEach((h, k) => T(s, h, { x: RX[k], y: 1.3, w: RW[k], h: 0.24, fontSize: 9, bold: true, color: C.accent1 }));
RQ.forEach((r, i) => { const y = 1.58 + i * 0.47;
  box(s, 3.22, y, 6.28, 0.42, i % 2 ? 'FFFFFF' : X.tint, 'req row');
  r.forEach((c, k) => T(s, c, { x: RX[k], y: y + 0.02, w: RW[k] - 0.05, h: 0.38, fontSize: k === 0 ? 9.5 : 8, bold: k === 0, color: k === 3 ? C.accent3 : C.text1, valign: 'middle' })); });
box(s, 0.5, 4.08, 9.0, 0.62, 'FFF6E8', 'make cond');
T(s, [{ text: '제작 조건 (요구사항이 아니라 설계 제약)  ', options: { bold: true, color: C.accent2 } }, { text: '3D 프린터 · PETG → 출력 방향 층간 강도와 부재 두께 하한(제작 오차만큼 깎아도 성능 유지)을 계산에 포함', options: { color: C.text1 } }], { x: 0.65, y: 4.12, w: 8.7, h: 0.27, fontSize: 9.5, valign: 'middle' });
T(s, '모델 가정: 폰 + 고정 부품 311 g을 크기 · 관성이 있는 강체로, 거치 35° · 스템 옆 · 레버 · 케이블 회피(스케치에서 읽음), 감쇠비 3% · 터치 5 N(가정값)', { x: 0.65, y: 4.4, w: 8.7, h: 0.25, fontSize: 8.5, color: C.accent3, valign: 'middle' });
s.addNotes('출발점은 사용자의 말 한 줄. "안 흔들리게"는 흔들림을 최소화하라는 뜻이므로 핸들바에서 폰으로 가는 진동 전달률을 지표로 삼았다. 노면 진동 근거는 ISBS 2020 조약돌길 실측. 3D 프린터는 요구가 아니라 제작 조건이라 설계 제약(층간 강도, 부재 두께 하한)으로 넣었다. 거치 각도 · 다는 위치 · 피할 곳은 스케치에서 LLM이 읽어 명세에 넣었고(spec_from_input_v1.json), 핸들바 지름 · 발열량은 사용자에게 확인 질문으로 남겼다. 감쇠비 · 터치 하중은 가정값이다.');

// ===== v14: 형상이 만들어지는 과정
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '부록' });
s.addText('부록. 자전거 거치대 — 형상은 계산이 만든다 (최적화 과정)', { placeholder: 'title' });
s.addText('설계 공간을 재료로 채운 뒤, 매 반복 진동 · 폰 온도 · 터치 처짐을 계산해 제약을 지키는 한도에서 재료를 덜어낸다', { placeholder: 'body' });
const FW4 = 1.43;
EV4.frames.forEach((f, i) => { const x = 0.5 + i * (FW4 + 0.08), last = i === EV4.frames.length - 1;
  box(s, x, 1.3, FW4, 1.78, last ? 'E3F1F0' : X.tint, 'frame');
  fit(s, SH + f.img, x + 0.05, 1.36, FW4 - 0.1, 1.05, 'iteration ' + f.it);
  T(s, i === 0 ? '시작' : last ? `최종 (${f.it + 1}회)` : `${f.it}회`, { x: x + 0.08, y: 2.43, w: FW4 - 0.16, h: 0.22, fontSize: 9.5, bold: true, color: C.text2 });
  T(s, `${f.mass} g · ${f.f1} Hz`, { x: x + 0.08, y: 2.67, w: FW4 - 0.16, h: 0.22, fontSize: 9, bold: true, color: last ? C.accent1 : C.accent3 });
  if (!last) arrow(s, x + FW4 - 0.02, 1.85, 0.11, 0.18); });
s.addChart(pres.charts.LINE, [{ name: '무게 (g)', labels: EV4.it.map(String), values: EV4.mass }], {
  x: 0.45, y: 3.15, w: 4.5, h: 1.75, chartColors: [X.teal], lineSize: 2, lineDataSymbol: 'none', showLegend: false, showTitle: true, title: '무게 (g) — 반복할수록 감소', titleFontSize: 9, titleColor: X.ink, titleFontFace: '+mn-lt',
  catAxisLabelColor: X.mute, valAxisLabelColor: X.mute, catAxisLabelFontSize: 7, valAxisLabelFontSize: 7, catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt',
  valGridLine: { color: 'DDE5E4', size: 0.5 }, catGridLine: { style: 'none' }, catAxisLabelFrequency: 5, catAxisLabelRotate: 0, valAxisMinVal: 0 });
s.addChart(pres.charts.LINE, [{ name: '1차 진동수', labels: EV4.it.map(String), values: EV4.f1 }, { name: '하한', labels: EV4.it.map(String), values: EV4.it.map(() => 95) }], {
  x: 4.95, y: 3.15, w: 2.6, h: 1.75, chartColors: [X.amber, X.red], lineSize: 2, lineDataSymbol: 'none', showLegend: false, showTitle: true, title: '1차 진동수 (Hz) — 목표 95 (깎은 형상 기준)', titleFontSize: 9, titleColor: X.ink, titleFontFace: '+mn-lt',
  catAxisLabelColor: X.mute, valAxisLabelColor: X.mute, catAxisLabelFontSize: 7, valAxisLabelFontSize: 7, catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt',
  valGridLine: { color: 'DDE5E4', size: 0.5 }, catGridLine: { style: 'none' }, catAxisLabelFrequency: 10, catAxisLabelRotate: 0, valAxisMinVal: 60, valAxisMaxVal: 180 });
[['1', '설계 공간', '클램프 · 걸이 · 집게 하우징 · 레일은 고정'], ['2', '매 반복 계산', '폰을 관성 있는 강체로 넣고 진동 모드 · 민감도 계산'], ['3', '재료 재배치', '진동 · 온도 · 터치 제약 아래 무게 최소화'], ['4', '두께 제약', '제작 오차만큼 깎아도 성능 유지']].forEach((h, i) => { const y = 3.2 + i * 0.43;
  disc(s, 7.68, y + 0.02, 0.26, X.teal, null, 'step');
  T(s, h[0], { x: 7.68, y: y + 0.02, w: 0.26, h: 0.26, fontSize: 9, bold: true, color: C.background1, align: 'center', valign: 'middle' });
  T(s, h[1], { x: 8.02, y, w: 1.55, h: 0.18, fontSize: 8.5, bold: true, color: C.text2 });
  T(s, h[2], { x: 8.02, y: y + 0.18, w: 1.55, h: 0.24, fontSize: 7, color: C.accent3 }); });
T(s, `※ 그림 = 재료 밀도 0.45 이상 영역, 수치 = 최적화 중 2 mm 격자 값(폰 + 고정 부품 311 g, 진동수는 제작 오차만큼 깎은 형상 기준). 출력용 몸체 81.3 g. CPU 2코어 약 ${EV4.minutes}분`, { x: 0.5, y: 4.95, w: 9, h: 0.22, fontSize: 7.5, color: C.accent3 });
s.addNotes('모양을 미리 정해 둔 것이 아니라, 계산이 재료를 덜어내며 만든 형상이다. 반복마다 폰의 무게와 회전 관성까지 넣어 진동을 계산하고, 1차 진동수를 노면 진동(중앙 34.6~45.6 Hz)보다 높게, 폰 온도 상승 21 °C 이하, 터치 처짐 0.3 mm 이하로 둔 채 기여가 작은 재료를 줄인다. 폰을 잡는 걸이 · 집게 하우징 · 레일은 고정해 두고, 그 사이를 잇는 삼각 프레임이 남는다. 진동수 곡선은 제작 오차만큼 깎은 형상 기준이라 실제 출력 형상은 이보다 높다(154–168 Hz).');

// ===== v15: 일체형 — 물리 검증이 쓸 수 없는 형상을 걸러냄
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '부록' });
s.addText('부록. 자전거 거치대 — 검토에서 찾은 문제를 계산으로 확인하고 고쳤다', { placeholder: 'title' });
s.addText('1차 결과에 폰 고정 형상이 없음을 검토에서 발견 → 충격 계산으로 확인 → 4면 고정 재설계 · 검증 항목에 추가', { placeholder: 'body' });
box(s, 0.5, 1.28, 3.0, 3.3, X.tint, 'nogrip card');
pill(s, 0.62, 1.36, 1.05, '1차 결과', X.mute, X.white);
fit(s, SH + 'v15_nogrip.png', 0.6, 1.72, 2.8, 2.2, 'no grip');
T(s, '폰을 판에 붙어 있다고 가정 —\n옆면 · 앞면을 잡는 형상 없음', { x: 0.62, y: 3.98, w: 2.76, h: 0.5, fontSize: 9, color: C.text1, align: 'center' });
box(s, 3.65, 1.28, 2.7, 3.3, 'FFFFFF', 'force card');
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 3.65, y: 1.28, w: 2.7, h: 3.3, rectRadius: 0.08, fill: { type: 'none' }, line: { color: X.line, width: 1 } });
T(s, '충격 순간 폰이 위로 빠지는 힘', { x: 3.77, y: 1.38, w: 2.46, h: 0.26, fontSize: 10, bold: true, color: C.text2 });
const FB = [['빠지는 힘 (위쪽)', 79, X.red], ['집게 마찰로 버티는 힘', 11, X.mute]];
FB.forEach((f, i) => { const y = 1.78 + i * 0.62, bw = 2.2 * f[1] / 85;
  T(s, f[0], { x: 3.77, y, w: 2.4, h: 0.22, fontSize: 8.5, color: C.accent3 });
  s.addShape(pres.shapes.RECTANGLE, { x: 3.77, y: y + 0.24, w: bw, h: 0.2, fill: { color: f[2] }, line: { color: f[2] } });
  T(s, i ? '3 ~ 11 N' : '79 N', { x: 3.82 + bw, y: y + 0.22, w: 0.9, h: 0.24, fontSize: 10, bold: true, color: f[2], valign: 'middle' }); });
T(s, '→ 집게만으로는 폰이 위로 미끄러져 빠짐\n→ 화면 쪽으로도 113 N이 걸림', { x: 3.77, y: 3.1, w: 2.5, h: 0.5, fontSize: 9, bold: true, color: C.accent1 });
T(s, '해결: 위 · 아래 걸이로 길이 방향을 막고, 집게는 잠금 나사로 고정', { x: 3.77, y: 3.72, w: 2.5, h: 0.6, fontSize: 9, color: C.text1 });
box(s, 6.5, 1.28, 3.0, 3.3, 'E3F1F0', 'grip card');
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.5, y: 1.28, w: 3.0, h: 3.3, rectRadius: 0.08, fill: { type: 'none' }, line: { color: X.teal, width: 2 } });
pill(s, 6.62, 1.36, 1.05, '재설계', X.teal, X.white);
fit(s, SH + 'v15_grip.png', 6.6, 1.72, 2.8, 2.2, 'grip');
T(s, '아래 · 위 걸이 + 양옆 스프링 집게\n+ 잠금 나사 — 4면 고정', { x: 6.62, y: 3.98, w: 2.76, h: 0.5, fontSize: 9, bold: true, color: C.accent1, align: 'center' });
T(s, '※ 충격 48.5 g(ISBS 2020 조약돌길) × 폰 290 g = 138 N을 35° 기울기로 나눔: 위쪽 79 N, 화면 쪽 113 N. 버티는 힘 = 마찰계수 0.3 × 스프링 힘 5–18 N × 양쪽 — 마찰계수 · 스프링 힘은 가정(확인 필요)', { x: 0.5, y: 4.68, w: 9, h: 0.4, fontSize: 7.5, color: C.accent3 });
s.addNotes('1차 일체형 결과는 계산상 폰을 판에 붙어 있다고 놓았기 때문에, 실제로 폰을 잡는 형상이 없었다. 이 문제는 자동 검증이 아니라 결과를 함께 검토하다 찾았고, 이후 폰 고정 점검을 검증 항목에 넣었다. 충격 하중을 기울기 방향으로 나눠 보면 폰이 위로 빠지려는 힘이 79 N인데, 스프링 집게 마찰로는 3~11 N밖에 버티지 못한다. 그래서 아래 · 위 걸이로 길이 방향을 막고 양옆 집게는 잠금 나사로 고정하는 4면 고정으로 바꾸고, 이 부품들을 고정 영역으로 넣어 몸체를 다시 최적화했다.');

// ===== v15: 제작형 결과 — 초기 설계 대비 (같은 걸이 · 집게 · 레일)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '부록' });
s.addText('부록. 자전거 거치대 결과 — 비슷한 무게로 흔들림 77%↓', { placeholder: 'title' });
s.addText('폰을 잡는 부품까지 넣은 같은 조건에서 초기 설계와 비교 — 출력용 몸체 기준', { placeholder: 'body' });
box(s, 0.5, 1.28, 4.7, 3.6, 'FFFFFF', 'result img');
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 1.28, w: 4.7, h: 3.6, rectRadius: 0.06, fill: { type: 'none' }, line: { color: X.line, width: 1 } });
fit(s, SH + 'v15_result.png', 0.6, 1.36, 4.5, 3.15, 'initial vs optimized');
T(s, '초기 설계', { x: 0.6, y: 4.55, w: 2.1, h: 0.25, fontSize: 9, color: C.accent3, align: 'center' });
T(s, '최적화 → 출력용 몸체', { x: 2.85, y: 4.55, w: 2.3, h: 0.25, fontSize: 9, bold: true, color: C.accent1, align: 'center' });
const MET5 = [['무게', 84.0, 81.3, 'g', null, '출력용 STL'], ['최대 흔들림', 5.6, 1.27, '배', null, '10–100 Hz · 두 방향 중 큰 값'], ['폰 온도 상승', 32.6, 20.8, '°C', 21, '제한 21 °C'], ['충격 층간 응력', 17.5, 2.2, 'MPa', 10.9, '허용 10.9 MPa']];
MET5.forEach((m, i) => { const x = 5.4, y = 1.28 + i * 0.9, W = 4.1, mx = Math.max(m[1], m[2], m[4] || 0) * 1.1;
  T(s, m[0] + '  ', { x, y, w: W, h: 0.24, fontSize: 10, bold: true, color: C.text2 });
  T(s, m[5], { x: x + 1.5, y, w: W - 1.5, h: 0.24, fontSize: 8, color: C.accent3, align: 'right' });
  [[m[1], X.mute, '처음'], [m[2], X.teal, 'AI']].forEach((b, k) => { const by = y + 0.28 + k * 0.27, bw = Math.max((W - 1.0) * b[0] / mx, 0.02);
    T(s, b[2], { x, y: by, w: 0.3, h: 0.22, fontSize: 9, color: C.accent3, valign: 'middle' });
    s.addShape(pres.shapes.RECTANGLE, { x: x + 0.32, y: by + 0.03, w: bw, h: 0.16, fill: { color: b[1] }, line: { color: b[1] } });
    T(s, `${b[0]} ${m[3]}`, { x: x + 0.36 + bw, y: by, w: 0.75, h: 0.22, fontSize: 9, bold: true, color: b[1] === X.teal ? C.accent1 : C.accent3, valign: 'middle' }); });
  if (m[4]) { const lx = x + 0.32 + (W - 1.0) * m[4] / mx; s.addShape(pres.shapes.LINE, { x: lx, y: y + 0.26, w: 0, h: 0.56, line: { color: X.red, width: 1.25, dashType: 'dash' } }); } });
T(s, '※ 폰 + 집게 · 걸이 · 스프링 · 나사 311 g 강체, 감쇠비 3%, 거치 35°, 발열 4 W 가정. 무게 = 두 설계 모두 출력용 STL 부피 × PETG 1.27 g/cm³. 흔들림 · 온도 · 응력 = 두 출력 형상을 같은 2 mm 격자로 해석. 평균 흔들림 1.19 → 1.09배', { x: 0.5, y: 4.95, w: 9, h: 0.3, fontSize: 7.5, color: C.accent3 });
s.addNotes('폰을 잡는 걸이 · 집게 · 레일을 같은 조건으로 넣고 초기 설계와 비교했다. 초기 설계는 30.5 Hz에서 공진해 최대 5.6배 흔들리고 폰 온도가 32.6 °C 오른다. 출력용 몸체는 81.3 g으로 처음 설계(84.0 g)와 무게는 비슷하지만, 최대 흔들림 1.27배, 온도 상승 20.8 °C, 충격 층간 응력 2.2 MPa. 강도 점검에서 걸이 · 집게 연결부 3곳이 약해 보강했고, 보강 후 모두 허용치 이내다.');

// ===== v15: 제작 구성
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '부록' });
s.addText('부록. 자전거 거치대 제작 구성 — 출력 4개 + 시판 부품', { placeholder: 'title' });
s.addText('몸체는 최적화 형상과 레일 · 걸이를 한 덩어리로 출력, 폰 크기 차이는 슬라이드 부품이 흡수', { placeholder: 'body' });
box(s, 0.5, 1.28, 4.6, 1.75, 'FFFFFF', 'side');
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 1.28, w: 4.6, h: 3.6, rectRadius: 0.06, fill: { type: 'none' }, line: { color: X.line, width: 1 } });
fit(s, SH + 'v15_grip_side.png', 0.6, 1.33, 2.0, 3.5, 'side view');
fit(s, SH + 'v15_jaw.png', 2.65, 1.6, 2.4, 3.0, 'jaw detail');
T(s, '옆에서', { x: 0.6, y: 4.6, w: 2.0, h: 0.22, fontSize: 8, color: C.accent3, align: 'center' });
T(s, '집게부 (주황 = 출력 슬라이드 부품)', { x: 2.65, y: 4.6, w: 2.4, h: 0.22, fontSize: 8, color: C.accent3, align: 'center' });
const BOM = [['출력', '몸체 × 1', '최적화 형상 + 집게 하우징 + 위쪽 레일 + 아래 걸이 (일체)'], ['출력', '슬라이드 집게 × 2', '3.6 g씩 · 스프링 포켓 · 안쪽 면 기울여 화면 쪽 이탈 방지'], ['출력', '위쪽 슬라이드 걸이 × 1', '8.3 g · 25 mm 이동 · M3 나사로 잠금'],
  ['구매', '압축 스프링 × 2', '바깥지름 5 mm, 자유 길이 약 28 mm (사양 확인 필요)'], ['구매', 'M3 볼트 · 너트', '스프링 멈춤 핀 2 + 잠금 나사 3'], ['구매', 'M4 볼트 · 너트 × 1', '핸들바 조임']];
BOM.forEach((r, i) => { const y = 1.28 + i * 0.42;
  pill(s, 5.3, y + 0.05, 0.55, r[0], r[0] === '출력' ? X.teal : X.amber, X.white);
  T(s, r[1], { x: 5.95, y, w: 3.55, h: 0.2, fontSize: 9.5, bold: true, color: C.text2 });
  T(s, r[2], { x: 5.95, y: y + 0.2, w: 3.55, h: 0.2, fontSize: 8, color: C.text1 }); });
box(s, 5.3, 3.86, 4.2, 1.02, X.tint, 'fit range');
[['대응 폰', '폭 64–90 · 두께 6–14 · 길이 145–170 mm · ≤ 290 g'], ['핸들바', '지름 31.8 mm'], ['출력', 'PETG · 채움 100% (해석 가정과 동일)']].forEach((r, i) => { const y = 3.93 + i * 0.3;
  T(s, r[0], { x: 5.42, y, w: 0.8, h: 0.28, fontSize: 9, bold: true, color: C.accent1, valign: 'middle' });
  T(s, r[1], { x: 6.2, y, w: 3.25, h: 0.28, fontSize: 9, color: C.text1, valign: 'middle' }); });
s.addNotes('출력 부품은 몸체 1, 슬라이드 집게 2, 위쪽 걸이 1로 모두 4개, 합계 96.8 g이다. 몸체에는 최적화 형상과 집게 하우징, 위쪽 레일, 아래 걸이가 한 덩어리로 들어간다. 폰 폭 차이는 스프링 집게가, 길이 차이는 위쪽 슬라이드 걸이가 흡수한다. 시판 부품은 스프링 2개와 M3 · M4 나사뿐이다. 해석은 채움 100%로 했으므로 출력도 채움 100%로 한다. 145 mm보다 짧은 폰은 대응하지 않는다.');
// ---------- 6c. 무선충전 스탠드 (보조: 물리 확장 — 열)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '부록' });
s.addText('부록. 확장 근거 — 열 물리: 무선충전 스탠드 방열판', { placeholder: 'title' });
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

await pres.writeFile({ fileName: OUT });
await applyTheme(OUT, THEME);
console.log('ok', OUT);
})();