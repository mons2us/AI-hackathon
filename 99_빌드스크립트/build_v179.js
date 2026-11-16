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
  colors: { dk1: '1A1F2B', lt1: 'FFFFFF', dk2: '0F1B3D', lt2: 'F0F3FA', accent1: '1428A0', accent2: '5B8DEF',
    accent3: '46536A', accent4: 'D3DBEE', accent5: '5E6B7D', accent6: '1428A0', hlink: '1428A0', folHlink: '46536A' } };
const X = { teal: '1428A0', ink: '0F1B3D', amber: '5B8DEF', mute: '46536A', tint: 'F0F3FA', line: 'D3DBEE', red: '5E6B7D', green: '1428A0', white: 'FFFFFF' };

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
            { text: { text: 'FormProof', options: { x: 0.5, y: 5.28, w: 5, h: 0.22, fontSize: 9, color: C.accent3, margin: 0 } } }],
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
s.addText([{ text: '머릿속 아이디어를', options: { breakLine: true } }, { text: '성능이 검증된 제품', options: { color: X.amber, bold: true } }, { text: '으로', options: { breakLine: true } }, { text: ' ', options: { fontSize: 6.5, breakLine: true } }, { text: '입력: 말 · 스케치 · 문서 · 이미지 · 3D 파일', options: { fontSize: 11, color: 'B9C5E3' } }], { placeholder: 'body' });
T(s, '물리 기반 생성형 AI', { x: 0.6, y: 4.6, w: 5, h: 0.3, fontSize: 11, color: C.accent4 });
box(s, 5.7, 0.62, 3.9, 4.25, 'FFFFFF', 'hero card');
{ // 아이디어 → 초기 설계 → 최종 설계 → 제작 파일 (시계 방향)
const PW = 1.75, PH = 1.7, L = 5.82, Rr = 7.73, T1 = 0.74, T2 = 2.66;
const P = [[L, T1, 'v17_sketch.png', '1 아이디어 입력', '말 + 스케치', C.text2],
  [Rr, T1, 'v28_Rbase_side.png', '2 초기 설계 · 해석', '판 끝 공진 · 기준 미달', C.accent5],
  [Rr, T2, 'v179_cover_phone.png', '3 AI 최적 설계', '흔들림 77% 감소 · 폰 장착', C.accent1],
  [L, T2, 'v25_asm.png', '4 제작 파일', 'STL · STEP · 도면', C.text2]];
P.forEach(p => { s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: p[0], y: p[1], w: PW, h: PH, rectRadius: 0.04, fill: { color: 'F5F7FB' }, line: { color: 'DDE3F0', width: 0.5 }, objectName: 'cover panel' });
  fit(s, SH + p[2], p[0] + 0.04, p[1] + 0.04, PW - 0.08, PH - 0.5, p[3]);
  T(s, p[3], { x: p[0] + 0.06, y: p[1] + PH - 0.45, w: PW - 0.12, h: 0.2, fontSize: 8, bold: true, color: C.text2 });
  T(s, p[4], { x: p[0] + 0.06, y: p[1] + PH - 0.25, w: PW - 0.12, h: 0.2, fontSize: 7.5, bold: true, color: p[5] }); });
arrow(s, L + PW + 0.02, T1 + 0.62, 0.14, 0.24);
s.addShape(pres.shapes.DOWN_ARROW, { x: Rr + PW / 2 - 0.1, y: T1 + PH + 0.02, w: 0.2, h: 0.18, fill: { color: X.amber }, line: { color: X.amber } });
s.addShape(pres.shapes.LEFT_ARROW, { x: L + PW + 0.0, y: T2 + 0.62, w: 0.16, h: 0.24, fill: { color: X.amber }, line: { color: X.amber } });
T(s, 'FormProof가 설계한 자전거 폰 거치대', { x: 5.8, y: 4.45, w: 3.7, h: 0.3, fontSize: 10, bold: true, color: C.text2, align: 'center' }); }
s.addNotes('FormProof = Form + Proof, 형상을 성능으로 증명. 오른쪽: 구현 결과 흐름 — 말 + 스케치 입력 → 초기 설계 해석(흔들림 5.6배, 기준 미달) → AI 최적 설계(1.3배, 몸체 81.3 g) → 제작 파일(STL · STEP · 도면).');

pres.addSection({ title: '요약' });
// ---------- 2. 한 장 요약 (v31: 흐름(위) → 증거 + DX(아래))
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '요약' });
s.addText([{ text: '아이디어만 입력하면 ', options: { fontSize: 19 } }, { text: '성능이 검증된 설계와 제작 파일', options: { color: '1428A0', fontSize: 19 } }, { text: '을 자동으로 만드는 AI', options: { fontSize: 19 } }], { placeholder: 'title', fontSize: 19 });

s.addText('설계, 성능 확인, 개선, 제작 준비까지 전문가 없이 한 번에 진행', { placeholder: 'body' });
// ① 입력 + 6단계 흐름 (4쪽과 같은 단계)
const FY = 1.18;
box(s, 0.5, FY, 9.0, 0.9, X.tint, 'flow');
const ICI = [await icon(fa.FaMicrophone, X.teal), await icon(fa.FaPencilAlt, X.teal), await icon(fa.FaFileAlt, X.teal), await icon(fa.FaImage, X.teal), await icon(fa.FaCube, X.teal)];
const ST6 = [['입력', '말 · 스케치 · 문서 · 이미지 · STEP', null], ['1. 설계 사양', '요구 정의 + 물리 조건 · 항목별 출처', 'v32_spec.png'],
  ['2. 3D 형상 생성', '초기 설계 (초기안)', 'v146_p_base.png'], ['3. 성능 해석', '진동 · 충격 · 열 판정 → 미달', 'v146_c_base.png'], ['4. 최적 설계', 'AI 탐색 → 상위 후보만 FEM 정밀화', 'v87_gen_grid.png'], ['5. 검증 · 제작 파일', '출력 형상 재판정 → STL · 도면', 'v25_asm.png']];
const CW6 = 1.34, GP6 = 0.158;
ST6.forEach((f, i) => { const x = 0.58 + i * (CW6 + GP6), y = FY + 0.06;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: CW6, h: 0.44, rectRadius: 0.04, fill: { color: 'FFFFFF' }, line: { color: i ? X.line : X.teal, width: i ? 0.5 : 1 }, objectName: 'thumb' });
  if (f[2] === null) ICI.forEach((ic, k) => s.addImage({ data: ic, x: x + 0.2 + k * 0.2, y: y + 0.13, w: 0.17, h: 0.17 }));
  else if (f[2] === 'req') T(s, [{ text: '목표  ', options: { bold: true, color: C.accent1 } }, { text: '무게 최소', options: { breakLine: true } }, { text: '제약  ', options: { bold: true, color: C.accent1 } }, { text: '흔들림 · 충격 · 발열', options: { breakLine: true } }, { text: '제작  ', options: { bold: true, color: C.accent1 } }, { text: '3D 프린터 · 4면 고정', options: {} }],
    { x: x + 0.06, y, w: CW6 - 0.1, h: 0.44, fontSize: 6.1, color: C.text1, valign: 'middle' });
  else fit(s, SH + f[2], x + 0.02, y + 0.02, CW6 - 0.04, 0.4, f[0]);
  T(s, f[0], { x, y: y + 0.46, w: CW6, h: 0.17, fontSize: 7.8, bold: true, color: i ? C.text2 : C.accent1, align: 'center' });
  T(s, f[1], { x: x - 0.06, y: y + 0.62, w: CW6 + 0.12, h: 0.18, fontSize: 6.1, color: C.text1, align: 'center' });
  const BD = [null, 'A', 'B', 'B', 'B', 'C'][i];
  if (BD) { s.addShape(pres.shapes.OVAL, { x: x - 0.06, y: y - 0.06, w: 0.2, h: 0.2, fill: { color: X.red }, line: { color: X.white, width: 0.75 }, objectName: 'core' });
    T(s, BD, { x: x - 0.06, y: y - 0.06, w: 0.2, h: 0.2, fontSize: 7, bold: true, color: X.white, align: 'center', valign: 'middle' }); }
  if (i < 5) arrow(s, x + CW6 + 0.025, y + 0.14, 0.1, 0.16); });
// v145 제거: T(s, [{ text: '정밀 물리 시뮬레이션 (FEM)  ', options: { bo
// v145 제거:   { x: 0.62, y: FY + 0.88, w: 8.8, h: 0.2, fontSiz
// ② 증거
const PY = 2.18;
box(s, 0.5, PY, 6.0, 2.82, 'EEF2FB', 'proof');
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: PY, w: 6.0, h: 2.82, rectRadius: 0.08, fill: { type: 'none' }, line: { color: X.teal, width: 1.5 }, objectName: 'proof frame' });
T(s, '대표 사례 — 자전거 폰 거치대 (이 사례의 입력: 말 + 스케치)', { x: 0.62, y: PY + 0.05, w: 5.8, h: 0.24, fontSize: 10, bold: true, color: C.accent1 });
{
const CO = JSON.parse(fs.readFileSync('/tmp/claude-0/-home-claude/e964ed80-ee1b-5f91-abd3-3081682a3ad7/scratchpad/deck/v148_callouts.json', 'utf8'));
const seg = (x1, y1, x2, y2, col) => s.addShape(pres.shapes.LINE, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.max(Math.abs(x2 - x1), 0.001), h: Math.max(Math.abs(y2 - y1), 0.001), flipH: (x2 < x1) !== (y2 < y1), line: { color: col, width: 0.75 }, objectName: 'leader' });
[['초기 설계 (거치대 + 받침대)', 'base', C.accent5, 0.6], ['FormProof 최적 설계 (출력 몸체)', 'body', C.accent1, 3.08]].forEach(c => {
  const x0 = c[3], y0 = PY + 0.33, PW = 2.4, PH = 1.42;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x0, y: y0, w: PW, h: PH, rectRadius: 0.05, fill: { color: 'FFFFFF' }, line: { color: X.line, width: 0.5 }, objectName: 'pair' });
  const ih = 0.9, iw = ih * CO.aspect, ix = x0 + (PW - iw) / 2, iy = y0 + 0.26;
  s.addImage({ data: pic(SH + 'v148_' + c[1] + '.png'), x: ix, y: iy, w: iw, h: ih, objectName: c[0] });
  const A = CO[c[1]].map(d => ({ ...d, px: ix + d.u * iw, py: iy + d.v * ih }));
  const top = A.slice().sort((p, q) => p.py - q.py).slice(0, 3).sort((p, q) => p.px - q.px);
  const bot = A.slice().sort((p, q) => p.py - q.py).slice(3).sort((p, q) => p.px - q.px);
  [[top, y0 + 0.02, true], [bot, y0 + PH - 0.25, false]].forEach(([row, ly, isTop]) => row.forEach((d, k) => {
    const lx = x0 + 0.04 + k * 0.79, lw = 0.77, hot = d.lab === '판 끝' || d.lab === '삼각 프레임';
    const col = hot ? (c[1] === 'base' ? '5E6B7D' : C.accent1) : C.text2;
    T(s, [{ text: d.lab, options: { bold: true, color: col, breakLine: true } }, { text: d.sub, options: { fontSize: 5.4, color: C.text1 } }], { x: lx, y: ly, w: lw, h: 0.23, fontSize: 6.4, align: 'center', valign: 'middle', margin: 0 });
    const ax = lx + lw / 2, ay = isTop ? ly + 0.235 : ly - 0.005;
    seg(ax, ay, d.px, d.py, '8A949C');
    s.addShape(pres.shapes.OVAL, { x: d.px - 0.022, y: d.py - 0.022, w: 0.044, h: 0.044, fill: { color: C.text2 }, line: { color: 'FFFFFF', width: 0.5 }, objectName: 'dot' }); }));
  T(s, c[0], { x: x0, y: PY + 1.77, w: 2.4, h: 0.2, fontSize: 9, bold: true, color: c[2], align: 'center' }); });
}
T(s, '흔들림', { x: 5.52, y: PY + 0.33, w: 0.9, h: 0.18, fontSize: 7.5, bold: true, color: C.text2 });
s.addImage({ path: SH + 'v149_cbar.png', x: 5.6, y: PY + 0.55, w: 0.13, h: 1.05, objectName: 'legend' });
T(s, '큼', { x: 5.78, y: PY + 0.52, w: 0.5, h: 0.16, fontSize: 7, color: C.text1 });
T(s, '작음', { x: 5.78, y: PY + 1.47, w: 0.5, h: 0.16, fontSize: 7, color: C.text1 });
T(s, '두 설계 같은 척도', { x: 5.5, y: PY + 1.66, w: 0.95, h: 0.2, fontSize: 6.8, color: C.accent3 });
const KP = [['폰 흔들림', '77% 감소', '요철 길 주행 시 최대 흔들림'], ['충격 응력', '80% 감소', '최대 응력 14.7 → 2.9 MPa'], ['폰 온도', '12 °C 저감', '온도 상승 32.6 → 20.8 °C'], ['몸체 무게', '84 → 81 g', '무게 증가 없이 성능 개선'], ['범용 LLM 비교', '3/3 불합격', '흔들림 2 · 온도 1 미달']];
KP.forEach((k, i) => { const x = 0.6 + i * 1.17, y = PY + 2.04, bad = i === 4;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 1.1, h: 0.66, rectRadius: 0.06, fill: { color: bad ? 'E4E8EF' : 'FFFFFF' }, line: { color: bad ? 'E4E8EF' : X.teal, width: 1 }, objectName: 'kpi card' });
  if (bad) s.addShape(pres.shapes.LINE, { x: x - 0.04, y: y + 0.06, w: 0, h: 0.54, line: { color: '8A949C', width: 1, dashType: 'dash' } });
  T(s, k[0], { x: x + 0.07, y: y + 0.04, w: 1.0, h: 0.17, fontSize: 7, bold: true, color: bad ? C.accent5 : C.text2, valign: 'middle' });
  T(s, k[1], { x: x + 0.07, y: y + 0.21, w: 1.0, h: 0.25, fontSize: 12, bold: true, color: bad ? C.accent5 : C.accent1, valign: 'middle' });
  T(s, k[2], { x: x + 0.07, y: y + 0.46, w: 1.02, h: 0.17, fontSize: 6.1, color: C.accent3, valign: 'middle' }); });
// ③ DX 제품 경쟁력 — 같은 방법론(입력 → 형상 → 물리 판정 → 제작 파일)을 제품에
box(s, 6.65, PY, 2.85, 2.82, X.ink, 'dx panel');
T(s, 'DX 제품 확장', { x: 6.78, y: PY + 0.07, w: 2.6, h: 0.26, fontSize: 11, bold: true, color: C.background1 });
T(s, '같은 흐름으로 다른 제품 · 사내 시스템까지 확장', { x: 6.78, y: PY + 0.33, w: 2.65, h: 0.2, fontSize: 7.2, color: C.accent4 });
const DX = [
  ['MX', 'AR 글래스', '착용 무게 · 코 하중 · 발열'],
  ['MX', '폴더블 · 웨어러블', '박형 구조 강성 · 방열 · 착용감'],
  ['VD · DA', 'TV · 가전', '슬림 구조 · 진동 · 소음 · 방열'],
  ['연동', '사내 특허 시스템', '제안서 → 효과 검증 리포트']];
DX.forEach((d, i) => { const y = PY + 0.58 + i * 0.32;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.76, y: y + 0.03, w: 0.5, h: 0.2, rectRadius: 0.1, fill: { color: X.teal }, line: { color: X.teal }, objectName: 'dx tag' });
  T(s, d[0], { x: 6.76, y: y + 0.03, w: 0.5, h: 0.2, fontSize: 6.8, bold: true, color: C.background1, align: 'center', valign: 'middle' });
  T(s, [{ text: d[1] + '  ', options: { bold: true, color: C.background1, fontSize: 7.8 } }, { text: d[2], options: { color: 'E3E8F4', fontSize: 6.5 } }], { x: 7.32, y, w: 2.14, h: 0.28, valign: 'middle' }); });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.76, y: PY + 2.0, w: 2.63, h: 0.72, rectRadius: 0.05, fill: { color: 'FFFFFF' }, line: { color: 'FFFFFF' }, objectName: 'ar card' });
fit(s, SH + 'v100_ar_cut.png', 6.79, PY + 2.02, 0.98, 0.68, 'AR glass cutaway');
T(s, [{ text: '확장 예: AR 글래스', options: { bold: true, color: C.text2, breakLine: true } }, { text: '광학 · 연산 칩 · 배터리 배치와\n착용 무게 · 발열을 함께 설계', options: { fontSize: 6.3, color: C.text1 } }],
  { x: 7.8, y: PY + 2.02, w: 1.57, h: 0.68, fontSize: 7, valign: 'middle' });
// v145 제거: T(s, '※ 최적 설계 = 초기 설계를 고치는 것이 아니라, 허용 설계 공간 전체에서 재료를
s.addNotes('한 장 요약. 상단: 입력 형태 무관(말 · 스케치 · 문서 · 이미지 · STEP) → 생성 AI의 출처 기반 설계 조건 작성 → 형상 AI · 물리 AI · 수치해석으로 계산 · 최적 설계 → 조립도 · STL · 설명서 출력. 좌하단: 동일 요청의 초기 설계와 AI 최적 설계를 동일 색 척도로 비교. 초기 설계는 판 끝 최대 3.5배 흔들림, AI 최적 설계는 1.2배 이하. 핵심 수치: 최대 흔들림, 충격 응력, 폰 온도, 무게. 우측: DX 제품 적용 — AR 글래스 · 폴더블 · 웨어러블 · TV · 가전의 무게 · 발열 · 진동 제약을 설계 초기에 검증, 특허 · 신제품 아이디어의 성능 근거 확보. [화면에서 뺀 주석] ※ 최적 설계 = 초기 설계를 고치는 것이 아니라, 허용 설계 공간 전체에서 재료를 다시 배치. 같은 조건 해석(폰 + 고정 부품 311 g, 감쇠비 3%, 35°, 발열 4 W, 길 진동 10–100 Hz). 우측 = 확장 적용 대상');

pres.addSection({ title: '1. 문제 정의' });
// ---------- 3. 문제 정의 (v50: 공감 + 시각화 — 떠오른다 → 막힌다 → 서랍 속으로 / 이게 된다면)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '1. 문제 정의' });
s.addText([{ text: '좋은 아이디어도 ' }, { text: '성능을 확인하기 어려워', options: { color: '1428A0' } }, { text: ' 제품이 되지 못하는 현실' }], { placeholder: 'title' });
T(s, '1. 문제 정의', { x: 0.5, y: 0.08, w: 4, h: 0.22, fontSize: 9, bold: true, color: '1428A0', margin: 0 });
s.addText('3D 설계와 성능 해석에 전문성과 시간이 필요해, 비전문가는 시작이 어렵고 엔지니어도 반복에 시간이 걸림', { placeholder: 'body' });
{
const AM = '5B8DEF', RD = '0F1B3D';
const I4 = { bike: await icon(fa.FaBicycle, X.white), bulb: await icon(fa.FaLightbulb, X.white), pen: await icon(fa.FaPencilRuler, X.white),
  clock: await icon(fa.FaHourglassHalf, RD), redo: await icon(fa.FaRedoAlt, RD), x: await icon(fa.FaTimesCircle, RD),
  arch: await icon(fa.FaArchive, '6B7585'), bulbG: await icon(fa.FaLightbulb, 'C9CED2'), bulbY: await icon(fa.FaLightbulb, '46536A') };
const Y0 = 1.22, HH = 2.56;
const tag = (x, y, t, c) => { box(s, x, y, 0.95, 0.24, c, 'tag'); T(s, t, { x, y, w: 0.95, h: 0.24, fontSize: 8, bold: true, color: X.white, align: 'center', valign: 'middle' }); };
// A. 떠오른다: 손 스케치 + 한마디
box(s, 0.5, Y0, 2.5, HH, 'F3F4F5', 'idea');
tag(0.62, Y0 + 0.1, '구상', X.ink);
s.addImage({ data: I4.bulbY, x: 2.62, y: Y0 + 0.08, w: 0.26, h: 0.26 });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.62, y: Y0 + 0.42, w: 2.26, h: 1.08, rectRadius: 0.04, fill: { color: 'FFFFFF' }, line: { color: X.line, width: 0.5 }, objectName: 'sketch' });
fit(s, SH + 'v17_sketch.png', 0.64, Y0 + 0.44, 2.22, 1.04, '손 스케치');
[[I4.bike, '폰이 떨려 지도가 안 보여. 만들어 볼까?'], [I4.bulb, '더 튼튼할 텐데, 증명할 방법이 없네'], [I4.pen, '더 얇게 하고 싶은데, 이 두께로 버틸까?']].forEach((q, i) => { const y = Y0 + 1.58 + i * 0.32;
  s.addShape(pres.shapes.OVAL, { x: 0.62, y: y + 0.02, w: 0.24, h: 0.24, fill: { color: X.ink }, line: { color: X.ink }, objectName: 'p' });
  s.addImage({ data: q[0], x: 0.67, y: y + 0.07, w: 0.14, h: 0.14 });
  T(s, '"' + q[1] + '"', { x: 0.92, y, w: 2.0, h: 0.28, fontSize: 7.5, italic: true, color: C.text2, valign: 'middle' }); });
// B. 그런데 현실은: 4개의 벽 (내려가는 계단)
T(s, '그런데 현실은', { x: 3.15, y: Y0 + 0.06, w: 2, h: 0.26, fontSize: 10.5, bold: true, color: RD });
const WL = [
  { img: 'v47_cad.png', q: '3D로 옮기려니', h: 'CAD를\n다룰 줄 모른다', e: '스케치에서 멈춘다' },
  { img: 'v48_base.png', tags: true, q: '버틸지 확인하려니', h: '계산 조건부터\n막막하다', e: '맡기면\n결과까지 한참' },
  { img: 'v44_llm.png', q: 'AI에게 맡겨 보니', h: '그럴듯한데\n틀렸다', e: '맞는지\n알 길이 없다' },
  { prints: true, q: '그냥 만들어 보니', h: '출력하고\n고치기만 반복', e: '만들어 봐야\n안다' }];
const WX = 3.15, WW = 1.17, WG = 0.07;
WL.forEach((w, i) => { const x = WX + i * (WW + WG), y = Y0 + 0.38 + i * 0.07, H = HH - 0.38 - i * 0.07;
  box(s, x, y, WW, H, 'F3F4F5', 'wall');
  s.addShape(pres.shapes.RECTANGLE, { x, y, w: WW, h: 0.03, fill: { color: RD }, line: { color: RD }, objectName: 'wall top' });
  s.addShape(pres.shapes.OVAL, { x: x + 0.06, y: y + 0.1, w: 0.2, h: 0.2, fill: { color: RD }, line: { color: X.white, width: 0.5 }, objectName: 'wall no' });
  T(s, '1234'[i], { x: x + 0.06, y: y + 0.1, w: 0.2, h: 0.2, fontSize: 8, bold: true, color: X.white, align: 'center', valign: 'middle' });
  T(s, w.q, { x: x + 0.3, y: y + 0.1, w: WW - 0.36, h: 0.2, fontSize: 7, color: C.accent3 });
  const iy = y + 0.32;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.08, y: iy, w: WW - 0.16, h: 0.74, rectRadius: 0.03, fill: { color: 'FFFFFF' }, line: { color: X.line, width: 0.5 }, objectName: 'wall img' });
  if (w.img) fit(s, SH + w.img, x + 0.1, iy + 0.02, WW - 0.2, 0.7, w.h);
  if (w.tags) [['하중?', 0.06, 0.06], ['고정?', 0.06, 0.46], ['기준?', 0.6, 0.46]].forEach(g => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.08 + g[1], y: iy + g[2], w: 0.42, h: 0.2, rectRadius: 0.05, fill: { color: RD }, line: { color: X.white, width: 0.75 }, objectName: 'q tag' });
    T(s, g[0], { x: x + 0.08 + g[1], y: iy + g[2], w: 0.42, h: 0.2, fontSize: 7, bold: true, color: X.white, align: 'center', valign: 'middle' }); });
  if (w.prints) ['1차', '2차', '3차'].forEach((g, k) => { const px = x + 0.12 + k * 0.3, py = iy + 0.06 + k * 0.08;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: px, y: py, w: 0.42, h: 0.42, rectRadius: 0.03, fill: { color: 'FFFFFF' }, line: { color: X.line, width: 0.5 }, objectName: 'print' });
    fit(s, SH + ['v49_base.png', 'v38_L1_side.png', 'v38_L2_side.png'][k], px + 0.02, py + 0.02, 0.38, 0.38, '출력 ' + g);
    T(s, g, { x: px, y: py + 0.43, w: 0.42, h: 0.14, fontSize: 6.5, bold: true, color: k < 2 ? RD : C.accent3, align: 'center' });
    if (k < 2) T(s, '✕', { x: px + 0.26, y: py - 0.02, w: 0.16, h: 0.16, fontSize: 9, bold: true, color: RD, align: 'center', valign: 'middle' }); });
  else if (w.cal) { // 달력: 해석 결과를 기다리는 7일
    const cx = x + 0.14, cw = WW - 0.28, dw = cw / 7;
    s.addShape(pres.shapes.RECTANGLE, { x: cx, y: iy + 0.1, w: cw, h: 0.14, fill: { color: RD }, line: { color: RD }, objectName: 'cal head' });
    T(s, '해석 결과 대기', { x: cx, y: iy + 0.1, w: cw, h: 0.14, fontSize: 6.5, bold: true, color: X.white, align: 'center', valign: 'middle' });
    ['월', '화', '수', '목', '금', '토', '일'].forEach((d, k) => { const dx = cx + k * dw;
      s.addShape(pres.shapes.RECTANGLE, { x: dx, y: iy + 0.24, w: dw, h: 0.36, fill: { color: 'FFFFFF' }, line: { color: X.line, width: 0.5 }, objectName: 'day' });
      T(s, d, { x: dx, y: iy + 0.25, w: dw, h: 0.12, fontSize: 5, color: C.accent3, align: 'center' });
      T(s, '×', { x: dx, y: iy + 0.34, w: dw, h: 0.24, fontSize: 10, bold: true, color: RD, align: 'center', valign: 'middle' }); });
    T(s, '…  다음 주로', { x: cx, y: iy + 0.6, w: cw, h: 0.12, fontSize: 6.5, color: C.accent3, align: 'right' }); }
  else if (w.ic) s.addImage({ data: I4[w.ic], x: x + WW / 2 - 0.22, y: iy + 0.15, w: 0.44, h: 0.44 });
  if (!w.cal && !w.tags && !w.prints) s.addImage({ data: I4.x, x: x + 0.12, y: iy + 0.04, w: 0.16, h: 0.16 });
  T(s, w.h, { x: x + 0.08, y: iy + 0.8, w: WW - 0.16, h: 0.36, fontSize: 9, bold: true, color: C.text2 });
  if (w.big) T(s, [{ text: w.big }, { text: w.ref, options: { superscript: true, fontSize: 8 } }], { x: x + 0.08, y: y + H - 0.58, w: WW - 0.16, h: 0.28, fontSize: 12, bold: true, color: RD, valign: 'bottom' });
  T(s, w.e, { x: x + 0.08, y: y + H - 0.5, w: WW - 0.16, h: 0.42, fontSize: 8, color: RD, bold: true, valign: 'bottom' }); });
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
T(s, '해결 방향', { x: 0.64, y: BY2 + 0.1, w: 1.6, h: 0.26, fontSize: 10.5, bold: true, color: '9DB8FF' });
T(s, 'CAD · 해석 의뢰 없이, 아이디어 단계에서 성능 확인부터 제작 파일까지', { x: 0.64, y: BY2 + 0.4, w: 1.5, h: 0.52, fontSize: 7.5, color: C.accent4, valign: 'top' });
const ST = [['v17_sketch.png', '입력 (형태 무관)', [], '말 · 스케치 · 문서 · STEP'], ['v49_base.png', '설계 사양 + 3D 형상 생성', ['①', '②'], '직접 모델링 · 조건 설정 부담 감소'],
  ['v51_ai_c.png', '성능 해석 · 최적 설계', ['③'], '기준 충족까지 계산 · 최적 설계'], ['v47_use.png', '제작 파일 출력', ['④'], 'STL · STEP · 도면 · 리포트']];
const SX0 = 2.3, SW2 = 1.8, IW = 1.42;
ST.forEach((t, i) => { const x = SX0 + i * SW2;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: BY2 + 0.08, w: IW, h: 0.58, rectRadius: 0.03, fill: { color: 'FFFFFF' }, line: { color: 'FFFFFF' }, objectName: 'wish img' });
  fit(s, SH + t[0], x + 0.02, BY2 + 0.1, IW - 0.04, 0.54, t[1]);
  t[2].forEach((n, k) => { const ox = x - 0.07 + k * 0.24;
    s.addShape(pres.shapes.OVAL, { x: ox, y: BY2 + 0.02, w: 0.22, h: 0.22, fill: { color: X.teal }, line: { color: X.white, width: 0.75 }, objectName: 'solved' });
    T(s, n, { x: ox, y: BY2 + 0.02, w: 0.22, h: 0.22, fontSize: 7.5, bold: true, color: X.white, align: 'center', valign: 'middle' }); });
  if (i === 1) ['하중 ✓', '고정 ✓', '기준 ✓'].forEach((g, k) => {   // 벽②의 '?'가 '✓'로
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + IW - 0.5, y: BY2 + 0.12 + k * 0.17, w: 0.46, h: 0.15, rectRadius: 0.04, fill: { color: X.teal }, line: { color: X.white, width: 0.5 }, objectName: 'ok tag' });
    T(s, g, { x: x + IW - 0.5, y: BY2 + 0.12 + k * 0.17, w: 0.46, h: 0.15, fontSize: 6.5, bold: true, color: X.white, align: 'center', valign: 'middle' }); });
  T(s, t[1], { x: x - 0.1, y: BY2 + 0.68, w: IW + 0.2, h: 0.17, fontSize: 8.5, bold: true, color: i === 3 ? '9DB8FF' : X.white, align: 'center' });
  T(s, t[3], { x: x - 0.1, y: BY2 + 0.84, w: IW + 0.2, h: 0.13, fontSize: 7, color: C.accent4, align: 'center' });
  if (i < 3) s.addShape(pres.shapes.CHEVRON, { x: x + IW + 0.13, y: BY2 + 0.26, w: 0.11, h: 0.24, fill: { color: '9DB8FF' }, line: { color: '9DB8FF' }, objectName: 'arrow' }); });
// v145 제거: T(s, [{ text: '※ 인용 문구는 대표 상황 예시, 그림은 본 과제 실제 결과(색
}
s.addNotes('문제 정의. 구상은 쉬우나 성능 확인 과정의 네 가지 병목에서 대부분 제품으로 이어지지 못함. ① 스케치의 3D 변환에 CAD 숙련 필요. ② 성능 계산에 하중 · 고정 · 기준 설정 필요, 전문가 의뢰 후 대기(참고: engineering.com 2022 조사, 외주 해석 67%가 1주 이상). ③ 범용 AI는 외형은 타당하나 성능 미달 — 본 과제에서 LLM 자체 예측 1.3배 흔들림이 실제 6.6배. ④ 결국 해석 없이 출력 · 수정 반복(같은 조사 45%가 일정상 해석 생략). 해결 방향: 입력에서 설계 사양과 3D 형상 생성(①②), 계산 기반 성능 해석 · 최적 설계(③), 제작 파일 출력(④). [화면에서 뺀 주석] ※ 인용 문구는 대표 상황 예시, 그림은 본 과제 실제 결과(색 = 같은 해석기로 계산한 흔들림). 남색 번호 = 병목, 파란 번호 = 해당 병목의 해결 단계');

pres.addSection({ title: '2. 제안 아이디어' });
// ---------- 5. 기술 차별성: 파이프라인
// ===== v7: 프레임워크 아키텍처
const IC2 = {
  robot: await icon(fa.FaRobot, X.white), shape: await icon(fa.FaDraftingCompass, X.teal), atom: await icon(fa.FaAtom, X.teal),
  opt: await icon(fa.FaChartLine, X.teal), ver: await icon(fa.FaClipboardCheck, X.teal), stl: await icon(fa.FaCube, X.teal),
  drw: await icon(fa.FaRulerCombined, X.teal), rep: await icon(fa.FaFileAlt, X.teal), img: await icon(fa.FaImage, X.teal),
  book: await icon(fa.FaBook, X.amber), x: await icon(fa.FaTimesCircle, X.red), ok: await icon(fa.FaCheckCircle, X.green),
};
// ===== v77: 프레임워크 — 모듈 · 데이터 흐름 · 반복 고리 + 모듈별 작은 그림
const GEN = '4F6BD8';   // 생성 AI 색 (뒤 장에서도 사용)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 제안 아이디어' });
s.addText([{ text: 'AI가 ' }, { text: '설계하고, 성능을 계산하고, 스스로 고치는', options: { color: '1428A0' } }, { text: ' 자동 설계 흐름' }], { placeholder: 'title' });
T(s, '2. 해결 방안', { x: 0.5, y: 0.08, w: 4, h: 0.22, fontSize: 9, bold: true, color: '1428A0', margin: 0 });
{ // 2쪽과 같은 순서를 프레임워크 위에 — 단계 ↔ 담당 모듈
const SS = [['입력', '말 · 스케치 · 문서'], ['1 설계 사양', 'LLM + 근거 DB'], ['2 3D 형상 생성', '초기 설계'], ['3 성능 해석', '물리 AI · FEM'], ['4 최적 설계', '구조 최적화'], ['5 검증 · 출력', '불합격 시 4로']];
SS.forEach((p, i) => { const x = 0.5 + i * 1.5;
  s.addShape(i ? pres.shapes.CHEVRON : pres.shapes.PENTAGON, { x, y: 0.84, w: 1.56, h: 0.27, fill: { color: i ? X.ink : X.mute }, line: { color: X.white, width: 0.75 }, objectName: 'step' });
  T(s, [{ text: p[0] + '  ', options: { bold: true, color: i ? X.amber : X.white } }, { text: p[1], options: { color: 'E3E8F4' } }], { x: x + (i ? 0.16 : 0.06), y: 0.84, w: 1.3, h: 0.27, fontSize: 6.8, valign: 'middle' }); }); }
{
const PHY = X.teal, NUM = '46536A', CTL = '5B8DEF';
// 그림이 위, 글이 아래인 노드
const node = (x, y, w, h, title, sub, col, o = {}) => {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.06, fill: { color: o.fill || 'FFFFFF' }, line: { color: col, width: 1.25 }, objectName: 'node' });
  let ty = y, th = h;
  if (o.img || o.img === null) { const ih = o.ih || (o.img === null ? 0.72 : 0.5); if (o.img) fit(s, SH + o.img, x + 0.06, y + 0.06, w - 0.12, ih, title); ty = y + ih + 0.06; th = h - ih - 0.06; }
  if (o.no) { s.addShape(pres.shapes.OVAL, { x: x - 0.1, y: y - 0.1, w: 0.26, h: 0.26, fill: { color: X.red }, line: { color: X.white, width: 1 }, objectName: 'core' });
    T(s, o.no, { x: x - 0.1, y: y - 0.1, w: 0.26, h: 0.26, fontSize: 8.5, bold: true, color: X.white, align: 'center', valign: 'middle' }); }
  T(s, [{ text: title, options: { bold: true, color: o.tc || C.text2, breakLine: true } }, { text: sub, options: { fontSize: 7, color: o.sc || C.text1 } }], { x: x + 0.06, y: ty, w: w - 0.12, h: th, fontSize: 8.5, align: 'center', valign: 'middle' }); };
const ln = (x1, y1, x2, y2, o = {}) => s.addShape(pres.shapes.LINE, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1) || 0.001, h: Math.abs(y2 - y1) || 0.001,
  flipH: x2 < x1, flipV: y2 < y1, line: { color: o.c || '6B7780', width: o.w || 1.25, dashType: o.d || 'solid', endArrowType: o.noArrow ? undefined : 'triangle' }, objectName: 'edge' });
const lab = (t, x, y, w, o = {}) => T(s, t, { x, y, w, h: o.h || 0.16, fontSize: o.fs || 6.3, bold: !!o.b, color: o.c || C.accent3, align: o.al || 'center', valign: 'middle' });
const NY = 1.9, NH = 1.45, RY = NY + NH / 2;   // 주 노드 위치 · 흐름 높이
node(0.5, NY, 0.95, NH, '입력', '말 · 스케치\n문서 · STEP', X.mute, { img: 'v17_sketch.png', ih: 0.62 });
node(1.75, NY, 1.3, NH, '설계 사양 AI', 'LLM + 근거 DB\n말 → 계산 조건 · 출처', GEN, { no: 'A', tc: GEN, img: null });
{ const sx = 1.81, sw = 1.18, sy = NY + 0.08;
  s.addShape(pres.shapes.RECTANGLE, { x: sx, y: sy, w: sw, h: 0.66, fill: { color: 'EEF2FB' }, line: { color: 'C9D3EC', width: 0.5 } });
  T(s, '설계 사양', { x: sx + 0.04, y: sy + 0.01, w: sw - 0.08, h: 0.13, fontSize: 5.6, bold: true, color: '1428A0', margin: 0 });
  [['안 흔들리게', '진동수 95 Hz↑', '근거', '1428A0'], ['울퉁불퉁 길', '충격 48.5 g', '근거', '1428A0'], ['거치 각도', '35° 맞나요?', '질문', '8A949C']].forEach((r, k) => { const ry = sy + 0.15 + k * 0.165;
    T(s, r[0], { x: sx + 0.04, y: ry, w: 0.4, h: 0.15, fontSize: 5, bold: true, color: C.text2, margin: 0, valign: 'middle' });
    T(s, r[1], { x: sx + 0.44, y: ry, w: 0.5, h: 0.15, fontSize: 5, color: C.text1, margin: 0, valign: 'middle' });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: sx + 0.94, y: ry + 0.02, w: 0.21, h: 0.11, rectRadius: 0.05, fill: { color: r[3] }, line: { color: r[3] } });
    T(s, r[2], { x: sx + 0.94, y: ry + 0.02, w: 0.21, h: 0.11, fontSize: 4.3, bold: true, color: X.white, align: 'center', valign: 'middle', margin: 0 }); }); }
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 3.55, y: 1.68, w: 3.0, h: 2.38, rectRadius: 0.06, fill: { color: 'F2F5FC' }, line: { color: PHY, width: 1, dashType: 'dash' }, objectName: 'engine' });
s.addShape(pres.shapes.OVAL, { x: 3.45, y: 1.58, w: 0.26, h: 0.26, fill: { color: X.red }, line: { color: X.white, width: 1 } });
T(s, 'B', { x: 3.45, y: 1.58, w: 0.26, h: 0.26, fontSize: 8.5, bold: true, color: X.white, align: 'center', valign: 'middle' });
lab('최적 설계 AI: 형상 생성 ⇄ 물리 계산', 3.75, 1.7, 2.7, { b: true, c: PHY, al: 'left', fs: 7.5 });
node(3.7, 1.92, 1.12, 0.98, '형상 AI', '잠재 코드 → 3D 형상', GEN, { tc: GEN, img: 'v87_gen_grid.png', ih: 0.4 });
node(5.28, 1.92, 1.12, 0.98, '', '', PHY, { tc: PHY });
fit(s, SH + 'v125_phys_fields.png', 5.31, 1.95, 1.06, 0.32, 'physics AI fields');
['흔들림', '충격', '열'].forEach((l, k) => T(s, l, { x: 5.31 + k * 0.355, y: 2.27, w: 0.355, h: 0.12, fontSize: 5.5, color: C.accent3, align: 'center' }));
T(s, [{ text: '물리 AI', options: { bold: true, color: PHY, breakLine: true } }, { text: '형상 → 성능 값 · 분포\nFEM 대신 즉시 예측', options: { fontSize: 6.3, color: C.text1 } }], { x: 5.31, y: 2.4, w: 1.06, h: 0.48, fontSize: 8.5, align: 'center', valign: 'middle' });
ln(4.82, 2.25, 5.28, 2.25); ln(5.28, 2.55, 4.82, 2.55);
lab('형상', 4.82, 2.08, 0.46); lab('기울기', 4.82, 2.57, 0.46);
lab('미분으로 형상 조정, 빠른 후보 탐색', 3.7, 2.92, 2.7, { b: true, c: PHY });
node(3.7, 3.22, 2.7, 0.66, '', '', NUM);
fit(s, SH + 'v79_evo.png', 3.76, 3.26, 1.25, 0.58, 'topology evolution');
T(s, [{ text: '구조 최적화 + FEM', options: { bold: true, color: C.text2, breakLine: true } }, { text: '상위 후보만 정밀화\n제조 제약 준수', options: { fontSize: 7, color: C.text1 } }], { x: 5.04, y: 3.22, w: 1.32, h: 0.66, fontSize: 8, align: 'center', valign: 'middle' });
ln(4.26, 3.08, 4.26, 3.22); lab('후보', 4.3, 3.08, 0.4, { al: 'left' });
ln(6.05, 3.22, 6.05, 2.9, { d: 'dash', c: PHY }); lab('계산 결과 → 물리 AI 학습 데이터', 3.7, 3.9, 2.7, { c: PHY, al: 'right' });
node(7.05, NY, 1.2, NH, '자동 검증', '판정만 수행: 출력 STL\nFEM 재계산 → 합격 / 불합격', NUM, { no: 'C', tc: NUM, img: 'v74_verify.png', ih: 0.62 });
node(8.7, NY, 0.8, NH, '제작 파일', 'STL · STEP\n도면 · 리포트', X.ink, { fill: X.ink, tc: X.amber, sc: X.white, img: 'v25_asm.png', ih: 0.62 });
// 데이터 흐름
ln(1.45, RY, 1.75, RY); lab('요청', 1.42, RY - 0.2, 0.36);
ln(3.05, RY, 3.55, RY); lab('설계 사양\n(JSON)', 3.03, RY - 0.36, 0.54, { b: true, h: 0.32 });
fit(s, SH + 'v146_p_base.png', 3.08, RY + 0.06, 0.44, 0.38, 'first design'); lab('+ 초기 설계\n(템플릿 생성)', 2.92, RY + 0.44, 0.76, { b: true, h: 0.3, c: '46536A' });
ln(6.55, RY, 7.05, RY); lab('출력\nSTL', 6.53, RY - 0.36, 0.54, { b: true, h: 0.32 });
T(s, [{ text: '제작 형상', options: { bold: true, color: C.text2, breakLine: true } }, { text: '변환 (CAD)', options: { bold: true, color: C.text2, breakLine: true } }, { text: '표면 정리\n부품 합치기\n구멍 · 홈', options: { color: C.accent3 } }], { x: 6.48, y: RY + 0.06, w: 0.64, h: 0.7, fontSize: 6, align: 'center', valign: 'top' });
ln(8.25, RY, 8.7, RY); lab('합격', 8.25, RY - 0.2, 0.45, { b: true, c: X.green });
// 불합격 되돌림
ln(7.65, NY + NH, 7.65, 4.16, { c: X.red, d: 'dash', noArrow: true }); ln(7.65, 4.16, 5.05, 4.16, { c: X.red, d: 'dash', noArrow: true }); ln(5.05, 4.16, 5.05, 4.06, { c: X.red, d: 'dash' });
lab('불합격 시 미달 항목을 B로 되돌림 → B에서 최적 설계', 4.9, 4.18, 2.9, { b: true, c: X.red });
// 에이전트 (아래) — 모듈 호출 · 판정
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 1.75, y: 4.42, w: 6.5, h: 0.36, rectRadius: 0.06, fill: { color: X.ink }, line: { color: X.ink }, objectName: 'agent' });
T(s, [{ text: 'LLM 에이전트   ', options: { bold: true, color: X.amber } }, { text: '계획 → 모듈 호출 → 결과 · 기준 대조 → 다음 호출 · 최적 설계 지시', options: { color: X.white } }], { x: 1.85, y: 4.42, w: 6.3, h: 0.36, fontSize: 8, align: 'center', valign: 'middle' });
[[2.4, NY + NH], [4.3, 4.06], [7.35, NY + NH]].forEach(p => ln(p[0], 4.42, p[0], p[1], { c: CTL, d: 'sysDot', w: 1 }));
lab('호출 · 판정', 2.45, 4.24, 0.8, { c: CTL, al: 'left' });
// 바탕
const res = (x, w, t1, t2) => { s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.25, w, h: 0.26, rectRadius: 0.05, fill: { color: X.tint }, line: { color: 'B9C3D6', width: 0.75 }, objectName: 'res' });
  T(s, [{ text: t1 + '  ', options: { bold: true, color: C.text2 } }, { text: t2, options: { color: C.accent3 } }], { x, y: 1.25, w, h: 0.26, fontSize: 7, align: 'center', valign: 'middle' }); };
res(1.6, 1.6, '근거 DB', '규격 · 논문 · 데이터시트');
res(3.55, 4.7, '정밀 물리 시뮬레이션 (FEM)', '구조 · 진동 · 열 · 충격 · 제조 제약 — 최종 판정 · 학습 데이터 기준');
ln(2.4, 1.51, 2.4, NY, { c: X.mute, d: 'dash' });
ln(5.9, 1.51, 5.9, 1.68, { c: X.mute, d: 'dash' }); ln(7.65, 1.51, 7.65, NY, { c: X.mute, d: 'dash' });
// v145 제거: lab('실선 = 데이터 · 하늘색 점선 = 에이전트 호출(아래) · 진회색 점선 = 불합
}
s.addNotes('동작 구조. 에이전트의 A 설계 사양 AI 호출 → 요청과 근거 DB 기반 설계 사양(JSON) 생성. 명세는 B 최적 설계 AI의 입력: 형상 AI의 잠재 변수 기반 형상 생성, 물리 AI의 성능 · 기울기 즉시 예측으로 후보 탐색. 구조 최적화 + FEM이 제조 제약 준수 하에 정밀화, 계산 결과는 물리 AI 학습 데이터로 재활용. 최종 형상은 제작 형상 변환(CAD: 표면 정리 · CAD 고정 부품 합치기 · 구멍 · 홈) 후 STL로 C 자동 검증에 전달, 재격자화 · 재계산 · 기준 비교. 불합격 시 미달 항목과 함께 최적 설계 회귀, 합격 시 제작 파일 출력. [화면에서 뺀 주석] 실선 = 데이터 · 하늘색 점선 = 에이전트 호출(아래) · 진회색 점선 = 불합격 되돌림 · 파란 점선 = 계산 결과가 학습 데이터로 · 회색 점선 = 근거 · 정밀 시뮬레이션 사용');

s._slideObjects.forEach(o => { const op = o.options; if (op && typeof op.y === 'number' && op.y >= 0.8 && op.y < 5.2) op.y += 0.32; });
s.addText('기준에 못 미치는 부분은 자동으로 다시 최적 설계해 모든 기준을 통과할 때까지 반복', { placeholder: 'body' });
// ===== v134: 핵심 기술 — 구조도 중심 (기술명 · 아키텍처, 숫자 최소화)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 제안 아이디어' });
s.addText([{ text: '추측이 아닌 ' }, { text: '근거와 계산으로 성능을 확인', options: { color: '1428A0' } }, { text: '하는 세 가지 핵심 기술' }], { placeholder: 'title' });
T(s, '2. 해결 방안', { x: 0.5, y: 0.08, w: 4, h: 0.22, fontSize: 9, bold: true, color: '1428A0', margin: 0 });
s.addText('요구를 근거 있는 수치로 바꾸고, AI가 물리 법칙에 맞게 설계하며, 정밀 계산으로 최종 확인', { placeholder: 'body' });
{
const CW = 2.93, G = 0.1, Y = 1.2, H = 3.5, BL = '1428A0', SL = '46536A';
const card = (i, L, name, col) => { const x = 0.5 + i * (CW + G);
  box(s, x, Y, CW, H, 'FFFFFF', 'core');
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: Y, w: CW, h: H, rectRadius: 0.08, fill: { type: 'none' }, line: { color: col, width: 1.25 }, objectName: 'frame' });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.12, y: Y + 0.12, w: 0.34, h: 0.34, rectRadius: 0.06, fill: { color: col }, line: { color: col }, objectName: 'letter' });
  T(s, L, { x: x + 0.12, y: Y + 0.12, w: 0.34, h: 0.34, fontSize: 13, bold: true, color: X.white, align: 'center', valign: 'middle' });
  T(s, name, { x: x + 0.54, y: Y + 0.12, w: CW - 0.6, h: 0.34, fontSize: 12, bold: true, color: col, valign: 'middle' });
  return x; };
const IC5 = { llm: await icon(fa.FaBrain, '1428A0'), db: await icon(fa.FaDatabase, '1428A0'), chk: await icon(fa.FaClipboardCheck, '46536A') };
const blk = (x, y, w, h, t1, t2, col, o = {}) => {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.04, fill: { color: o.fill || 'FFFFFF' }, line: { color: col, width: o.lw || 1 }, objectName: 'blk' });
  let tx = x, tw = w;
  if (o.img) { fit(s, SH + o.img, x + 0.04, y + 0.03, o.iw, h - 0.06, t1); tx = x + o.iw + 0.06; tw = w - o.iw - 0.08; }
  if (o.icon) { s.addShape(pres.shapes.OVAL, { x: x + 0.1, y: y + (h - 0.32) / 2, w: 0.32, h: 0.32, fill: { color: 'EEF2FB' }, line: { color: 'EEF2FB' }, objectName: 'icbg' });
    s.addImage({ data: o.icon, x: x + 0.16, y: y + (h - 0.2) / 2, w: 0.2, h: 0.2 }); tx = x + 0.5; tw = w - 0.54; }
  T(s, [{ text: t1, options: { bold: true, color: o.tc || col, breakLine: !!t2 } }].concat(t2 ? [{ text: t2, options: { fontSize: 6.3, color: C.text1 } }] : []),
    { x: tx, y, w: tw, h, fontSize: o.fs || 8, align: (o.img || o.icon) ? 'left' : 'center', valign: 'middle' }); };
const dn = (x, y, h, col) => s.addShape(pres.shapes.LINE, { x, y, w: 0, h, line: { color: col || X.mute, width: 1.25, endArrowType: 'triangle' }, objectName: 'arr' });
const chips = (x, arr, col) => { let cx = x + 0.12; arr.forEach(c => { const w = 0.1 + c.length * 0.075;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx, y: Y + 2.86, w, h: 0.22, rectRadius: 0.11, fill: { color: col }, line: { color: col }, objectName: 'chip' });
  T(s, c, { x: cx, y: Y + 2.86, w, h: 0.22, fontSize: 6.8, bold: true, color: X.white, align: 'center', valign: 'middle' }); cx += w + 0.05; }); };
const eff = (x, t, col) => T(s, t, { x: x + 0.12, y: Y + 3.12, w: CW - 0.24, h: 0.3, fontSize: 8.5, bold: true, color: col, valign: 'middle' });
// A
let x = card(0, 'A', '설계 사양 AI', BL);
// 입력: 스케치 크게 + 요청 문장 (v141: 스케치 · 사양 가독성 개선)
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.15, y: Y + 0.56, w: CW - 0.3, h: 1.04, rectRadius: 0.04, fill: { color: 'FFFFFF' }, line: { color: SL, width: 1 }, objectName: 'in' });
fit(s, SH + 'v17_sketch.png', x + 0.19, Y + 0.6, 1.4, 0.96, 'sketch');
T(s, [{ text: '입력', options: { bold: true, color: SL, breakLine: true } }, { text: '스케치 +\n', options: { fontSize: 6.8, color: C.text1 } }, { text: '"울퉁불퉁한 길에서도\n안 흔들리게,\n최대한 가볍게"', options: { fontSize: 7, bold: true, color: C.text2 } }], { x: x + 1.62, y: Y + 0.56, w: CW - 1.8, h: 1.04, fontSize: 7.5, valign: 'middle' });
dn(x + CW / 2, Y + 1.6, 0.06);
// LLM + 근거 DB (한 줄)
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.15, y: Y + 1.66, w: CW - 0.3, h: 0.28, rectRadius: 0.04, fill: { color: 'FFFFFF' }, line: { color: BL, width: 1 }, objectName: 'ld' });
s.addImage({ data: IC5.llm, x: x + 0.22, y: Y + 1.7, w: 0.2, h: 0.2 });
T(s, [{ text: 'LLM ', options: { bold: true, color: BL } }, { text: '의미 해석', options: { color: C.text1 } }], { x: x + 0.45, y: Y + 1.66, w: 1.0, h: 0.28, fontSize: 7.3, valign: 'middle' });
T(s, '+', { x: x + 1.38, y: Y + 1.66, w: 0.14, h: 0.28, fontSize: 9, bold: true, color: BL, align: 'center', valign: 'middle' });
s.addImage({ data: IC5.db, x: x + 1.54, y: Y + 1.7, w: 0.2, h: 0.2 });
T(s, [{ text: '근거 DB ', options: { bold: true, color: BL } }, { text: '수치', options: { color: C.text1 } }], { x: x + 1.77, y: Y + 1.66, w: 0.95, h: 0.28, fontSize: 7.3, valign: 'middle' });
dn(x + CW / 2, Y + 1.94, 0.05);
// 설계 사양 (JSON) — 실제 변환 예시
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.15, y: Y + 1.99, w: CW - 0.3, h: 0.83, rectRadius: 0.04, fill: { color: 'EEF2FB' }, line: { color: BL, width: 1.5 }, objectName: 'spec' });
T(s, '설계 사양 (JSON) · 항목마다 출처', { x: x + 0.22, y: Y + 2.0, w: CW - 0.44, h: 0.19, fontSize: 7.6, bold: true, color: BL, valign: 'middle' });
[['"안 흔들리게"', '진동수 ≥ 95 Hz', '근거 DB', BL], ['"울퉁불퉁한 길"', '충격 48.5 g', '근거 DB', BL], ['스케치 각도', '거치 35°', '질문', '8A949C']].forEach((r, k) => { const ry = Y + 2.19 + k * 0.205;
  T(s, r[0], { x: x + 0.22, y: ry, w: 0.92, h: 0.21, fontSize: 7, bold: true, color: C.text2, valign: 'middle' });
  T(s, '→ ' + r[1], { x: x + 1.1, y: ry, w: 1.08, h: 0.21, fontSize: 7, color: C.text1, valign: 'middle' });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 2.2, y: ry + 0.025, w: 0.5, h: 0.16, rectRadius: 0.08, fill: { color: r[3] }, line: { color: r[3] } });
  T(s, r[2], { x: x + 2.2, y: ry + 0.025, w: 0.5, h: 0.16, fontSize: 6, bold: true, color: X.white, align: 'center', valign: 'middle' }); });
chips(x, ['LLM', '근거 DB 검색', 'JSON 스키마'], BL);
eff(x, '모든 수치에 출처, 근거가 없으면 묻는다', BL);
// B
x = card(1, 'B', '최적 설계 AI', BL);
// v150: 1차 설계 = B 의 출발점
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.15, y: Y + 0.55, w: CW - 0.3, h: 0.3, rectRadius: 0.04, fill: { color: 'F5F7FB' }, line: { color: SL, width: 1 }, objectName: 'first' });
fit(s, SH + 'v146_p_base.png', x + 0.18, Y + 0.565, 0.3, 0.27, 'first design');
T(s, [{ text: '초기 설계', options: { bold: true, color: SL } }, { text: '  → 성능 해석 → 미달 개선 · 전체 재확인', options: { fontSize: 6.5, color: C.text1 } }], { x: x + 0.52, y: Y + 0.55, w: CW - 0.7, h: 0.3, fontSize: 7.5, valign: 'middle' });
dn(x + CW / 2, Y + 0.85, 0.05);
blk(x + 0.15, Y + 0.9, 1.24, 0.72, '', '', '4F6BD8');
fit(s, SH + 'v87_gen_grid.png', x + 0.19, Y + 0.93, 1.16, 0.34, 'DeepSDF');
T(s, [{ text: '형상 AI', options: { bold: true, color: '4F6BD8', breakLine: true } }, { text: 'DeepSDF: 잠재 코드 → 3D', options: { fontSize: 6.3, color: C.text1 } }], { x: x + 0.15, y: Y + 1.27, w: 1.24, h: 0.34, fontSize: 8, align: 'center', valign: 'middle' });
blk(x + 1.54, Y + 0.9, 1.24, 0.72, '', '', BL);
fit(s, SH + 'v125_phys_fields.png', x + 1.58, Y + 0.93, 1.16, 0.28, 'neural operator');
T(s, [{ text: '물리 AI', options: { bold: true, color: BL, breakLine: true } }, { text: 'GINO · FNO: 형상 → 분포', options: { fontSize: 6.3, color: C.text1 } }], { x: x + 1.54, y: Y + 1.21, w: 1.24, h: 0.4, fontSize: 8, align: 'center', valign: 'middle' });
s.addShape(pres.shapes.LINE, { x: x + 1.39, y: Y + 1.12, w: 0.15, h: 0, line: { color: SL, width: 1, endArrowType: 'triangle' } });
s.addShape(pres.shapes.LINE, { x: x + 1.39, y: Y + 1.38, w: 0.15, h: 0, flipH: true, line: { color: SL, width: 1, endArrowType: 'triangle' } });
T(s, 'AI 탐색: 반복마다 형상이 바뀌고 물리 AI가 성능 예측', { x: x + 0.15, y: Y + 1.63, w: CW - 0.3, h: 0.16, fontSize: 6.5, bold: true, color: BL, align: 'center' });
['00', '09', '16', '28'].forEach((k, i) => { const fw = (CW - 0.3) / 4; fit(s, SH + 'v156_evo_' + k + '.png', x + 0.15 + i * fw, Y + 1.8, fw - 0.04, 0.5, 'evo ' + k);
  if (i < 3) s.addShape(pres.shapes.CHEVRON, { x: x + 0.15 + (i + 1) * fw - 0.06, y: Y + 2.0, w: 0.05, h: 0.08, fill: { color: BL }, line: { color: BL } }); });
dn(x + CW / 2, Y + 2.3, 0.05);
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.15, y: Y + 2.36, w: CW - 0.3, h: 0.46, rectRadius: 0.04, fill: { color: 'F5F7FB' }, line: { color: SL, width: 1 }, objectName: 'fem' });
T(s, [{ text: 'FEM 정밀화 · 검증', options: { bold: true, color: SL, breakLine: true } }, { text: '상위 후보 몇 개만 정밀 계산 · 제조 제약 반영', options: { fontSize: 6.3, color: C.text1 } }], { x: x + 0.22, y: Y + 2.36, w: CW - 0.44, h: 0.46, fontSize: 7.5, valign: 'middle' });
chips(x, ['DeepSDF', 'GINO · FNO', 'SIMP · MMA'], BL);
eff(x, '형상 생성 · 성능 예측 · 최적화를 미분으로 연결', BL);
// C
x = card(2, 'C', '자동 검증', SL);
[['v44_body.png', '① 출력 형상 (STL)'], ['v136_vox.png', '② 2 mm 재격자화'], ['v136_fem.png', '③ FEM 재계산']].forEach((p, k) => { const px = x + 0.15 + k * 0.9;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: px, y: Y + 0.6, w: 0.8, h: 0.66, rectRadius: 0.04, fill: { color: 'FFFFFF' }, line: { color: SL, width: 0.75 }, objectName: 'thumb' });
  fit(s, SH + p[0], px + 0.03, Y + 0.63, 0.74, 0.6, p[1]);
  T(s, p[1], { x: px - 0.05, y: Y + 1.27, w: 0.9, h: 0.15, fontSize: 6.3, bold: true, color: SL, align: 'center' });
  if (k < 2) s.addShape(pres.shapes.LINE, { x: px + 0.81, y: Y + 0.93, w: 0.08, h: 0, line: { color: SL, width: 1, endArrowType: 'triangle' } }); });
dn(x + CW / 2, Y + 1.43, 0.08);
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.15, y: Y + 1.52, w: CW - 0.3, h: 0.72, rectRadius: 0.04, fill: { color: 'F5F7FB' }, line: { color: SL, width: 1 }, objectName: 'judge' });
s.addImage({ data: IC5.chk, x: x + 0.22, y: Y + 1.58, w: 0.16, h: 0.16 });
T(s, '④ 자동 판정: 기준 · 연결성 · 중간 밀도', { x: x + 0.42, y: Y + 1.56, w: 2.3, h: 0.2, fontSize: 7, bold: true, color: SL, valign: 'middle' });
[['진동수', '168 Hz', '≥ 95'], ['폰 온도', '+20.8 °C', '≤ 21'], ['터치 처짐', '0.03 mm', '≤ 0.3'], ['층간 응력', '2.2 MPa', '≤ 10.9']].forEach((r, k) => { const cx = x + 0.22 + (k % 2) * 1.3, cy = Y + 1.8 + Math.floor(k / 2) * 0.2;
  T(s, [{ text: r[0] + ' ', options: { color: C.accent3 } }, { text: r[1] + ' ', options: { bold: true, color: C.text2 } }, { text: r[2] + ' ✓', options: { bold: true, color: BL } }], { x: cx, y: cy, w: 1.3, h: 0.2, fontSize: 6.8, valign: 'middle' }); });
dn(x + 0.75, Y + 2.24, 0.1, BL);
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.15, y: Y + 2.34, w: 1.22, h: 0.36, rectRadius: 0.05, fill: { color: BL }, line: { color: BL }, objectName: 'pass' });
T(s, '합격 → 제작 파일', { x: x + 0.15, y: Y + 2.34, w: 1.22, h: 0.36, fontSize: 7.5, bold: true, color: X.white, align: 'center', valign: 'middle' });
dn(x + 2.15, Y + 2.24, 0.1, SL);
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 1.48, y: Y + 2.34, w: 1.3, h: 0.36, rectRadius: 0.05, fill: { color: 'FFFFFF' }, line: { color: SL, width: 1, dashType: 'dash' }, objectName: 'fail' });
T(s, [{ text: '불합격 → B 최적 설계', options: { bold: true, breakLine: true } }, { text: '미달 항목만큼 목표 조정', options: { fontSize: 6 } }], { x: x + 1.48, y: Y + 2.34, w: 1.3, h: 0.36, fontSize: 7.5, color: SL, align: 'center', valign: 'middle' });
chips(x, ['FEM', '규칙 판정', '폐루프 최적 설계'], SL);
eff(x, '제작될 형상 그대로 판정, 합격만 출력', SL);
box(s, 0.5, 4.8, 9.0, 0.34, X.ink, 'sum');
T(s, [{ text: 'A 조건 → B 설계 → C 검증', options: { bold: true, color: X.white } }, { text: '   불합격이면 B로 자동 회귀, 모든 기준을 충족할 때까지 반복', options: { color: 'D9E1F5' } }], { x: 0.65, y: 4.8, w: 8.7, h: 0.34, fontSize: 8.5, valign: 'middle' });
// v145 제거: T(s, '※ 물리 AI: FNO(격자 입력) · GINO(메시 · STEP 입력). C 
}
s.addNotes('핵심 기술 A · B · C. A 설계 사양 AI: LLM이 표현의 의미를 물리량으로 해석하고, 수치는 근거 DB(규격 · 실측 논문 · 데이터시트)에서만 가져와 항목별 출처를 붙인 JSON 설계 사양을 만든다. 근거가 없으면 사용자에게 묻는다. B 최적 설계 AI: 형상 AI(DeepSDF)가 형상을 잠재 변수로 표현하고, 물리 AI(신경 연산자, FNO · GINO)가 형상에서 응력 · 온도 분포를 즉시 예측해 기울기를 준다. 미분으로 후보를 찾고 SIMP + MMA 구조 최적화가 제조 제약을 지키며 정밀화한다. C 자동 검증: 제작될 STL을 다시 격자화해 FEM으로 진동 · 열 · 충격 · 처짐을 계산하고, 기준 · 연결성 · 중간 밀도를 자동 판정한다. 불합격이면 미달 항목만큼 목표를 조여 B로 돌려보낸다. 물리 AI는 현재 FNO로 구현, GINO는 메시 · STEP 입력용 확장. 학습은 진행 중이며 구현 결과 결과는 구조 최적화 경로. [화면에서 뺀 주석] ※ 물리 AI: FNO(격자 입력) · GINO(메시 · STEP 입력). C 판정 값 = 최종 출력 몸체 기준');

pres.addSection({ title: '3. 구현 결과' });
const EV4 = JSON.parse(fs.readFileSync(__dirname + '/evo_v16.json', 'utf8'));
// ===== v156: 구현 결과 ① — 실제 동작 화면 (GUI) + AI 형상 탐색 과정
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '3. 구현 결과' });
s.addText([{ text: '말 한 줄과 스케치만으로 ' }, { text: '검증된 설계와 제작 파일까지', options: { color: '1428A0' } }, { text: ' 실제 구현' }], { placeholder: 'title' });
T(s, '3. 구현 결과', { x: 0.5, y: 0.08, w: 4, h: 0.22, fontSize: 9, bold: true, color: '1428A0', margin: 0 });
s.addText('자전거 폰 거치대를 예로 초기 설계부터 검증 통과까지 실제 동작 화면으로 확인', { placeholder: 'body' });
{
const SW = 4.42, SHh = SW * 9 / 16, SY = 1.22;
const badge = (x, y, n, t, w) => { s.addShape(pres.shapes.OVAL, { x, y, w: 0.26, h: 0.26, fill: { color: X.teal }, line: { color: 'FFFFFF', width: 1 }, objectName: 'badge' });
  T(s, String(n), { x, y, w: 0.26, h: 0.26, fontSize: 9.5, bold: true, color: X.white, align: 'center', valign: 'middle' });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.29, y: y + 0.01, w, h: 0.24, rectRadius: 0.05, fill: { color: X.ink, transparency: 8 }, line: { color: X.ink } });
  T(s, t, { x: x + 0.29, y: y + 0.01, w, h: 0.24, fontSize: 7.8, bold: true, color: X.white, align: 'center', valign: 'middle' }); };
[['v156_gui_first.png', 0.5, '초기 설계 직후'], ['v156_gui_final.png', 5.08, '최적화 완료 후']].forEach(([f, x, cap]) => {
  s.addImage({ path: SH + f, x, y: SY, w: SW, h: SHh, objectName: cap });
  s.addShape(pres.shapes.RECTANGLE, { x, y: SY, w: SW, h: SHh, fill: { type: 'none' }, line: { color: X.line, width: 0.75 }, objectName: 'frame' }); });
badge(0.56, SY + 0.62, 1, '말 · 스케치 → 설계 사양', 1.42);
badge(1.95, SY + 1.95, 2, '초기 설계 · 물리 분포', 1.25);
badge(3.3, SY + 0.95, 3, '판정: 미충족 5개', 1.0);
badge(6.1, SY + 0.62, 4, 'AI 탐색 → FEM 통과 (출력 변환 전)', 1.95);
badge(8.0, SY + 1.95, 5, '초기 → 최적 비교', 1.05);
// AI 형상 탐색 과정 (같은 화면의 재생 프레임)
const EY = SY + SHh + 0.12, EH = 5.02 - EY;
box(s, 0.5, EY, 9.0, EH, X.tint, 'evo');
T(s, [{ text: 'AI 형상 탐색', options: { bold: true, color: C.accent1, breakLine: true } }, { text: '초기 설계에서 출발,\n반복마다 물리 AI가\n성능 예측', options: { fontSize: 7.3, color: C.text1 } }], { x: 0.6, y: EY + 0.05, w: 1.2, h: EH - 0.1, fontSize: 9.5, valign: 'middle' });
const FR = [['00', '초기 설계'], ['09', '반복 27'], ['13', '반복 39'], ['16', '반복 48'], ['21', '반복 63'], ['28', 'FEM 검증 통과']];
const FW = (9.4 - 1.85) / 6;
FR.forEach(([k, t], i) => { const x = 1.85 + i * FW;
  fit(s, SH + 'v156_evo_' + k + '.png', x, EY + 0.04, FW - 0.1, EH - 0.3, t);
  T(s, t, { x: x - 0.05, y: EY + EH - 0.26, w: FW, h: 0.22, fontSize: 7.3, bold: i === 0 || i === 5, color: i === 5 ? C.accent1 : i === 0 ? C.accent5 : C.accent3, align: 'center' });
  if (i < 5) s.addShape(pres.shapes.CHEVRON, { x: x + FW - 0.1, y: EY + (EH - 0.3) / 2 - 0.04, w: 0.07, h: 0.1, fill: { color: X.mute }, line: { color: X.mute } }); });
}
s.addNotes('본 사례 입력: 요청 문장 1개 + 스케치. 요구를 출처 기반 설계 사양로 변환. 초기 설계(거치대 + 받침대)는 30.5 Hz 공진으로 최대 5.6배 흔들림, 폰 온도 32.6 °C 상승. 3D 구조 최적화로 재료 재배치 후 출력 형상 재계산, 통과 형상만 제작 파일로 출력. [화면에서 뺀 주석] ※ 수치 = 2 mm 격자 유한요소 해석(폰 + 고정 부품 311 g 강체, 감쇠비 3% · 발열 4 W 가정). 흔들림 = 핸들바 대비 폰 진동 배율, 두 방향 중 큰 값. 최종 형상 검증 = 출력용 몸체(81.3 g) 재해석 값. 본 사례는 구조 최적화(수치해석) 경로로 설계');

// ===== v154: 구현 결과 ② — 같은 조건 물리 분포 + 조립도
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '3. 구현 결과' });
s.addText([{ text: '같은 무게로 ' }, { text: '덜 흔들리고, 더 튼튼하고, 덜 뜨거운', options: { color: '1428A0' } }, { text: ' 거치대 완성' }], { placeholder: 'title' });
T(s, '3. 구현 결과', { x: 0.5, y: 0.08, w: 4, h: 0.22, fontSize: 9, bold: true, color: '1428A0', margin: 0 });
s.addText('초기 설계의 약점을 모두 해소하고 3D 프린터로 바로 출력할 수 있는 형태로 완성', { placeholder: 'body' });
{
const LX = 0.5, LW = 0.62, MW = 2.2, AX = 1.18, BX = 3.44, CBX = 5.7, RX = 6.06, RW = 3.44;
T(s, '초기 설계', { x: AX, y: 1.18, w: MW, h: 0.24, fontSize: 10, bold: true, color: C.accent5, align: 'center' });
T(s, 'FormProof 최적 설계', { x: BX, y: 1.18, w: MW, h: 0.24, fontSize: 10, bold: true, color: C.accent1, align: 'center' });
const PR = [
  { lab: '흔들림', sub: '길 진동', a: 'v179_Rbase_clean.png', b: 'v179_Rbody_clean.png', ta: '판 끝 공진 (30.5 Hz)', tb: '최대 흔들림 77% 감소 (168 Hz)', cb: 'v26_cb_R.png' },
  { lab: '충격', sub: '48.5 g', a: 'v28_Vbase.png', b: 'v51_Vbody.png', ta: '판 뿌리에 응력 집중 · 최대 14.7 MPa', tb: '프레임으로 분산 · 최대 2.9 MPa', cb: 'v26_cb_V.png' },
  { lab: '열', sub: '폰 4 W', a: 'v25_Tbase.png', b: 'v51_Tbody.png', ta: '뒷면을 덮어 온도 상승 32.6 °C', tb: '뒷면이 열려 온도 상승 20.8 °C', cb: 'v26_cb_T.png' }];
PR.forEach((r, i) => { const y = 1.44 + i * 1.2, H = 1.13;
  box(s, LX, y, LW, H, X.ink, 'row label');
  T(s, r.lab, { x: LX, y: y + 0.28, w: LW, h: 0.3, fontSize: 11, bold: true, color: C.background1, align: 'center' });
  T(s, r.sub, { x: LX, y: y + 0.6, w: LW, h: 0.24, fontSize: 7, color: C.accent4, align: 'center' });
  [[r.a, r.ta, AX, C.accent5], [r.b, r.tb, BX, C.accent1]].forEach(c => {
    box(s, c[2], y, MW, H, 'FFFFFF', 'map');
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: c[2], y, w: MW, h: H, rectRadius: 0.06, fill: { type: 'none' }, line: { color: X.line, width: 0.75 }, objectName: 'map frame' });
    fit(s, SH + c[0], c[2] + 0.04, y + 0.03, MW - 0.08, H - 0.33, r.lab);
    T(s, c[1], { x: c[2] + 0.05, y: y + H - 0.29, w: MW - 0.1, h: 0.26, fontSize: 8, bold: true, color: c[3], align: 'center', valign: 'middle' }); });
  s.addImage({ path: SH + 'v149_cbar.png', x: CBX + 0.02, y: y + 0.2, w: 0.09, h: H - 0.4, objectName: 'colorbar' });
  T(s, '큼', { x: CBX + 0.12, y: y + 0.12, w: 0.25, h: 0.16, fontSize: 6.5, color: C.text1 });
  T(s, '작음', { x: CBX + 0.12, y: y + H - 0.3, w: 0.3, h: 0.16, fontSize: 6.5, color: C.text1 }); });
// 오른쪽: 구조(부품 이름) + 조립도 + 부품
box(s, RX, 1.18, RW, 3.8, 'FFFFFF', 'build');
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: RX, y: 1.18, w: RW, h: 3.8, rectRadius: 0.06, fill: { type: 'none' }, line: { color: X.teal, width: 1.25 }, objectName: 'build frame' });
T(s, '그대로 제작: 출력 부품 4개 + 시판 부품', { x: RX + 0.12, y: 1.22, w: RW - 0.24, h: 0.26, fontSize: 10, bold: true, color: C.accent1, valign: 'middle' });
fit(s, SH + 'v25_labeled.png', RX + 0.05, 1.48, RW - 0.1, 1.72, 'labeled structure');
s.addShape(pres.shapes.LINE, { x: RX + 0.12, y: 3.24, w: RW - 0.24, h: 0, line: { color: X.line, width: 0.75 } });
fit(s, SH + 'v25_asm.png', RX + 0.05, 3.28, 2.1, 1.66, 'assembly drawing');
T(s, '조립도', { x: RX + 2.2, y: 3.3, w: 1.2, h: 0.22, fontSize: 8.5, bold: true, color: C.text2 });
[['출력', '몸체 81.3 g (성능 비교)\n집게 · 걸이 포함 96.8 g'], ['구매', '스프링 × 2\nM3 · M4 볼트']].forEach((r, i) => { const y = 3.56 + i * 0.66;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: RX + 2.2, y: y + 0.02, w: 0.42, h: 0.2, rectRadius: 0.1, fill: { color: r[0] === '출력' ? X.teal : X.amber }, line: { color: r[0] === '출력' ? X.teal : X.amber } });
  T(s, r[0], { x: RX + 2.2, y: y + 0.02, w: 0.42, h: 0.2, fontSize: 7, bold: true, color: X.white, align: 'center', valign: 'middle' });
  T(s, r[1], { x: RX + 2.2, y: y + 0.24, w: 1.2, h: 0.38, fontSize: 7.3, color: C.text2, valign: 'top' }); });
T(s, '출력 합계 96.8 g · PETG', { x: RX + 2.2, y: 4.72, w: 1.2, h: 0.2, fontSize: 6.8, color: C.accent3 });
}
s.addNotes('각 행은 두 설계에 동일 색 척도 적용, 빨강일수록 불리. 흔들림: 길 진동 10–100 Hz 동안 핸들바 대비 각 지점 진동 배율(RMS). 충격: 48.5 g 상하 충격 시 응력. 열: 폰 발열 4 W 시 온도 상승. 초기 설계는 1차 30.5 Hz가 길 진동 대역과 겹쳐 최대 5.6배 흔들림. AI 최적 설계(출력 몸체)는 1차 168 Hz로 길 진동 대역 밖, 최대 흔들림 1.27배. 초기 설계는 판이 폰 뒷면을 덮어 열 갇힘(+32.6 °C), AI 최적 설계는 뒷면 개방으로 방열(+20.8 °C). [화면에서 뺀 주석] ※ 같은 조건 해석(폰 + 고정 부품 311 g, 감쇠비 3%, 35°, 발열 4 W · 주행풍 가정). 각 줄은 두 설계에 같은 색 척도 적용. 응력은 99.9% 값 기준 최대');

pres.addSection({ title: '4. 기술 차별성' });
// ---------- 4. 기술 차별성: 단계 지도 (v64: 누가 · 얼마나 어렵게 하나)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '4. 기술 차별성' });
s.addText([{ text: '기존 도구는 ', options: { fontSize: 19 } }, { text: '일부 단계만', options: { color: '1428A0', fontSize: 19 } }, { text: ' 돕지만, FormProof는 ', options: { fontSize: 19 } }, { text: '처음부터 끝까지', options: { color: '1428A0', fontSize: 19 } }, { text: ' 자동 처리', options: { fontSize: 19 } }], { placeholder: 'title', fontSize: 19 });
T(s, '4. 기술 차별성', { x: 0.5, y: 0.08, w: 4, h: 0.22, fontSize: 9, bold: true, color: '1428A0', margin: 0 });
s.addText('다른 도구는 중간 단계마다 여전히 전문가의 손이 필요', { placeholder: 'body' });
{
const UI = { user: await icon(fa.FaUser, 'B8C0C6'), pro: await icon(fa.FaUserTie, '46536A'), ai: await icon(fa.FaRobot, X.white) };
// [단계, 사람이 할 때 필요한 일, 난이도(1–3), 3쪽 벽]
const STP = [['설계 사양', '목표 · 하중 · 기준 수치화', 3, '②'], ['3D 형상 생성', 'CAD 모델링', 2, '①'], ['성능 해석', '메쉬 · 시뮬레이션', 3, '③'],
  ['최적 설계', '최적화 · CAD 재구성 · 반복', 3, '④'], ['검증 · 제작', '출력 형상 재검증 · 도면', 2, '']];
// 1 = 도구가 자동, 3 = 전문가 수작업 필요, 4 = 추측(검증 없음), 0 = 지원 안 함 → 사람이 메움
const RW = [
  ['범용 LLM 단독', '대화형 AI (ChatGPT 등)', [1, 1, 4, 4, 4], '계산 없이 추정, 검증 시 불합격'],
  ['3D 생성 AI', '텍스트 · 이미지 → 3D (Meshy 등)', [0, 1, 0, 0, 0], '형상만 생성, 이후는 수작업'],
  ['생성형 설계 도구', '조건 → 최적 형상 (Fusion 360 등)', [0, 0, 1, 1, 0], '사람이 정한 틀 · 조건 안에서만'],
  ['해석 도구 (CAE)', '전문가용 (Ansys · Abaqus 등)', [3, 3, 1, 3, 3], '단계마다 전문가 설정 필요'],
  ['FormProof', '말 · 스케치부터 제작 파일까지', [1, 1, 1, 1, 1], '전 단계 자동 · 계산으로 검증']];
const LX = 0.5, LW = 1.7, SX = 2.3, CWs = 1.03, RX = SX + 5 * CWs + 0.12, RWd = 9.5 - RX, HY = 1.22, RY0 = 1.9, RH = 0.52, RG = 0.08;
STP.forEach((st, i) => { const x = SX + i * CWs;
  s.addShape(pres.shapes.CHEVRON, { x: x + 0.01, y: HY, w: CWs - 0.02, h: 0.3, fill: { color: X.ink }, line: { color: X.ink }, objectName: 'step' });
  T(s, st[0], { x: x + 0.1, y: HY, w: CWs - 0.2, h: 0.3, fontSize: st[0].length > 5 ? 6.8 : 7.5, bold: true, color: X.white, align: 'center', valign: 'middle' });
  T(s, st[1], { x: x + 0.02, y: HY + 0.33, w: CWs - 0.04, h: 0.26, fontSize: 6.5, color: C.text1, align: 'center' });
});
T(s, '사람이 할 때 하는 일', { x: LX, y: HY + 0.33, w: LW, h: 0.26, fontSize: 7, color: C.accent3, valign: 'middle' });
T(s, '한계', { x: RX, y: HY + 0.04, w: RWd, h: 0.24, fontSize: 9, bold: true, color: C.accent3 });
const cell = (st, x, y, w, h, fp, pg) => { if (st === 0) st = 3;   // 사람이 하는 칸은 하나로
  if (st === 1) { const c = fp ? X.teal : 'A7B3C2';
    s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: c }, line: { color: c }, objectName: 'auto' });
    if (fp) { s.addImage({ data: UI.ai, x: pg ? x + 0.1 : x + w / 2 - 0.08, y: y + h / 2 - 0.08, w: 0.16, h: 0.16 });
      if (pg) T(s, pg, { x: x + 0.3, y, w: w - 0.34, h, fontSize: 7.5, bold: true, color: X.white, valign: 'middle' }); } }
  else if (st === 3) { s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: 'E4E8EF' }, line: { color: 'E4E8EF' }, objectName: 'expert' });
    s.addImage({ data: UI.pro, x: x + w / 2 - 0.08, y: y + h / 2 - 0.08, w: 0.16, h: 0.16 }); }
  else if (st === 6 || st === 7) { s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: X.amber }, line: { color: X.amber }, objectName: 'expert text' });
    T(s, st === 6 ? '형상 틀은\n사람이' : '학습 때\n고정', { x, y, w, h, fontSize: 7, bold: true, color: X.white, align: 'center', valign: 'middle' }); }
  else if (st === 5) { s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: 'DDE5F7' }, line: { color: X.amber, width: 0.75, dashType: 'dash' }, objectName: 'setup' });
    if (w > 0.4) T(s, '구축 때', { x, y, w, h, fontSize: 7, bold: true, color: '5B8DEF', align: 'center', valign: 'middle' }); }
  else if (st === 4) { s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: 'F3F4F5' }, line: { color: X.red, width: 0.75, dashType: 'dash' }, objectName: 'guess' });
    T(s, '추측', { x, y, w, h, fontSize: 7, bold: true, color: X.red, align: 'center', valign: 'middle' }); }
  else { s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: 'FFFFFF' }, line: { color: 'D9DEE2', width: 0.75, dashType: 'dash' }, objectName: 'gap' });
    s.addImage({ data: UI.user, x: x + w / 2 - 0.07, y: y + h / 2 - 0.07, w: 0.14, h: 0.14 }); } };
RW.forEach((r, ri) => { const y = RY0 + ri * (RH + RG), fp = ri === 4;
  if (fp) box(s, LX - 0.08, y - 0.05, 9.08, RH + 0.1, 'EEF2FB', 'fp row');
  T(s, r[0], { x: LX, y: y + 0.01, w: LW, h: 0.24, fontSize: 9.5, bold: true, color: fp ? C.accent1 : C.text2 });
  T(s, r[1], { x: LX, y: y + 0.25, w: LW, h: 0.18, fontSize: 7, color: C.accent3 });
  const PG = [null, null, null, null, null];
  r[2].forEach((m, i) => cell(m, SX + i * CWs + 0.03, y + 0.06, CWs - 0.06, RH - 0.12, fp, fp ? PG[i] : null));
  const nH = r[2].filter(m => m === 0 || m === 3).length, nG = r[2].filter(m => m === 4).length;
  const tg = fp ? ['5단계 자동 연계', X.teal] : nG ? ['추측 ' + nG, X.red] : ['사용자 작업 ' + nH + '단계', '8A949C'];
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: RX, y: y + RH / 2 - 0.12, w: 0.92, h: 0.24, rectRadius: 0.12, fill: { color: tg[1] }, line: { color: tg[1] }, objectName: 'tally' });
  T(s, tg[0], { x: RX, y: y + RH / 2 - 0.12, w: 0.92, h: 0.24, fontSize: 7, bold: true, color: X.white, align: 'center', valign: 'middle' });
  T(s, r[3], { x: RX + 0.98, y, w: RWd - 0.98, h: RH, fontSize: 7, bold: fp, color: fp ? C.accent1 : C.text1, valign: 'middle' }); });
// 범례
const LG = 4.92;
[[1, '도구 · AI 자동'], [3, '전문가 수행 필요'], [4, '추측 (검증 없음)']].forEach((g, i) => { const x = SX + i * 1.75;
  cell(g[0], x, LG, 0.3, 0.16, false); T(s, g[1], { x: x + 0.36, y: LG - 0.01, w: 1.35, h: 0.18, fontSize: 7, color: C.accent3, valign: 'middle' }); });
T(s, '', { x: 7.6, y: LG - 0.01, w: 1.9, h: 0.18, fontSize: 7, color: C.accent3, align: 'right', valign: 'middle' });
}
s.addNotes('요구 정의 = 문제와 요구를 목표 · 제약 수치로 정리. 성능 해석 = 시뮬레이션. 최고 난도 단계: 물리 조건 설정, 해석, 최적 설계(최적화 결과의 CAD 재구성 및 반복). 해석 도구는 계산만 자동이며 전후 단계(모델링, 조건, 최적 설계, 재검증)는 전문가 수행. FormProof는 6단계 전체를 AI로 수행. [화면에서 뺀 주석] 해석 도구: 결과 확보 1주 이상 67% (engineering.com · Dassault 2022 설문). 범용 LLM: 같은 조건 독립 3회, 같은 해석기로 판정 → 3회 모두 불합격(9쪽). 비교는 범주별 일반 기능 기준.');

// ===== v162: 범용 LLM 단독 vs FormProof (같은 요청 · 같은 검증)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '4. 기술 차별성' });
s.addText([{ text: '같은 요청에도 ' }, { text: '일반 AI의 설계는 세 번 모두 기준 미달', options: { color: '1428A0' } }], { placeholder: 'title' });
T(s, '4. 기술 차별성', { x: 0.5, y: 0.08, w: 4, h: 0.22, fontSize: 9, bold: true, color: '1428A0', margin: 0 });
s.addText('계산 없이 그럴듯하게 만든 설계는 실제 성능을 보장하지 못함', { placeholder: 'body' });
{
const LL = [
  { name: 'LLM 단독 A', img: 'v38_L1.png', crit: '≥ 90 Hz', fr: '95 → 150.6 Hz', sh: true, t: 22.6, m: 87.7, ok: false, note: '폰 온도 기준 초과' },
  { name: 'LLM 단독 B', img: 'v38_L2.png', crit: '≥ 60 Hz', fr: '70 → 109.6 Hz', sh: false, t: 20.5, m: 79.8, ok: false, note: '진동수는 높지만 앞뒤 흔들림 초과' },
  { name: 'LLM 단독 C', img: 'v38_L3.png', crit: '≥ 80 Hz', fr: '85 → 89.7 Hz', sh: false, t: 20.6, m: 80.0, ok: false, note: '위쪽 레일 공진' },
  { name: 'FormProof', img: 'v163_Ropt_clean.png', crit: '근거 DB ≥ 95 Hz', fr: '계산 153.9 Hz', sh: true, t: 20.7, m: 77.1, ok: true, note: '전 기준 충족' }];
const LW = 2.12, Y0 = 1.25, CH = 3.75;
LL.forEach((d, i) => { const x = 0.5 + i * (LW + 0.15), fp = d.ok;
  box(s, x, Y0, LW, CH, fp ? 'EEF2FB' : X.tint, 'llm card');
  if (fp) s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: Y0, w: LW, h: CH, rectRadius: 0.08, fill: { type: 'none' }, line: { color: X.teal, width: 2 }, objectName: 'fp frame' });
  T(s, d.name, { x: x + 0.1, y: Y0 + 0.06, w: LW - 0.2, h: 0.26, fontSize: 11.5, bold: true, color: fp ? C.accent1 : C.text2 });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.06, y: Y0 + 0.36, w: LW - 0.12, h: 1.12, rectRadius: 0.04, fill: { color: 'FFFFFF' }, line: { color: X.line, width: 0.5 }, objectName: 'img' });
  fit(s, SH + d.img, x + 0.08, Y0 + 0.38, LW - 0.16, 1.08, d.name);
  const ok = (b) => b ? '✓' : '✕';
  const R = [['스스로 정한 기준', d.crit, C.text1], [fp ? '진동수 (참고)' : '진동수 예측 → FEM', d.fr, C.text1],
    ['흔들림 (공통 기준)', d.sh ? '통과 ✓' : '초과 ✕', d.sh ? (fp ? C.accent1 : C.text1) : '5E6B7D'],
    ['온도 상승 (≤ 21 °C)', `${d.t} °C ${ok(d.t <= 21)}`, d.t > 21 ? '5E6B7D' : (fp ? C.accent1 : C.text1)], ['무게 (출력 변환 전)', d.m + ' g', C.text1]];
  R.forEach((r, k) => { const y = Y0 + 1.56 + k * 0.32;
    s.addShape(pres.shapes.LINE, { x: x + 0.1, y: y + 0.3, w: LW - 0.2, h: 0, line: { color: 'DDE3F0', width: 0.5 } });
    T(s, r[0], { x: x + 0.1, y, w: 1.05, h: 0.3, fontSize: 7.5, color: C.accent3, valign: 'middle' });
    T(s, r[1], { x: x + 1.0, y, w: LW - 1.08, h: 0.3, fontSize: 9, bold: true, color: r[2], align: 'right', valign: 'middle' }); });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.1, y: Y0 + CH - 0.5, w: LW - 0.2, h: 0.4, rectRadius: 0.06, fill: { color: fp ? X.teal : 'E4E8EF' }, line: { color: fp ? X.teal : 'E4E8EF' }, objectName: 'verdict' });
  T(s, (fp ? '합격 · ' : '불합격 · ') + d.note, { x: x + 0.14, y: Y0 + CH - 0.5, w: LW - 0.28, h: 0.4, fontSize: 9, bold: true, color: fp ? C.background1 : '46536A', align: 'center', valign: 'middle' }); });
}
s.addNotes('동일 요청 · 동일 일체형 조건을 도구 없는 LLM 세션 3개에 입력. 3개 세션 모두 트러스 · 스파인 구조 제시, 진동 기준(60~90 Hz)과 흔들림 1.2~1.3배를 자체 예측. 동일 해석기 판정 결과: A는 흔들림 1.37배로 양호하나 폰 뒷면을 덮어 온도 기준(21 °C) 초과, 10 g 더 무거움. B는 앞뒤 2.95배, C는 위쪽 레일 공진으로 6.6배. 예측 진동수도 실제와 불일치. 결론: LLM 단독으로 양호한 안이 나올 수는 있으나 계산 없이는 판별 불가. FormProof는 전 기준을 계산으로 확인, 최경량 안 도출. [화면에서 뺀 주석] ※ LLM 단독 = 도구 · 계산 없이 같은 요청 · 같은 일체형 조건(35°, 같은 걸이 · 집게 · 레일, 311 g)을 받은 독립 세션 3회(Claude, 2026-11-15). 판정은 모두 같은 2 mm 격자 FEM · 감쇠비 3% · 발열 4 W. 흔들림 = 핸들바 대비 최대(10–100 Hz, 위아래 · 앞뒤 중 큰 값). 그림 색 = 같은 척도의 흔들림 분포. FormProof 값 = 출력 변환 전 최적화 결과(LLM 안과 같은 단계). 출력 몸체(81.3 g)도 재해석 통과');

pres.addSection({ title: '5. DX 기여 · 확장' });
// ===== v167: DX 기여 — 설계 방식 변화 + 같은 흐름으로 다른 제품 (AI 글래스 실제 화면)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '5. DX 기여 · 확장' });
s.addText([{ text: '성능 확인을 ' }, { text: '며칠에서 몇 초로', options: { color: '1428A0' } }, { text: ' 줄이고, ' }, { text: '사업부 제품 경쟁력', options: { color: '1428A0' } }, { text: '을 높임' }], { placeholder: 'title' });
T(s, '5. 기대 효과와 계획', { x: 0.5, y: 0.08, w: 4, h: 0.22, fontSize: 9, bold: true, color: '1428A0', margin: 0 });
s.addText('같은 방식을 AI 글래스, 폴더블, TV, 가전 개발에 그대로 적용', { placeholder: 'body' });
{
// 위: 핵심 메시지 띠
const BY = 1.2;
box(s, 0.5, BY, 9.0, 0.56, X.ink, 'hero');
T(s, [{ text: '성능 확인  ', options: { color: '9FB4EA', bold: true, fontSize: 10 } }, { text: '해석 의뢰 · 결과 대기 (며칠~몇 주)', options: { color: 'B8C2D6', fontSize: 11 } }, { text: '   →   ', options: { color: X.white, bold: true, fontSize: 13 } }, { text: '입력하면 몇 초 안에 초기 설계와 성능 판정', options: { color: X.white, bold: true, fontSize: 13 } }],
  { x: 0.7, y: BY, w: 8.6, h: 0.56, valign: 'middle' });
// 왼쪽: 지금 → 적용 4단계 (간결)
const stg = [['구상', '경험으로 형상 결정', '요구에서 설계안 자동 생성'], ['상세 설계', '해석 의뢰 · 결과 대기', '설계자가 직접 성능 확인'], ['개선', '수작업 수정 반복', 'AI가 최적 설계'], ['시제품', '출력 · 시험 · 실패 반복', '출력 전에 검증']];
const LY = 1.98, RH = 0.66, PW = 0.82, NW = 1.45, FW = 1.75;
T(s, '지금', { x: 0.5 + PW + 0.08, y: LY - 0.04, w: NW, h: 0.22, fontSize: 9, bold: true, color: C.accent3 });
T(s, 'FormProof', { x: 0.5 + PW + NW + 0.3, y: LY - 0.04, w: FW, h: 0.22, fontSize: 9, bold: true, color: C.accent1 });
stg.forEach((g, i) => { const y = LY + 0.22 + i * (RH + 0.08), x1 = 0.5 + PW + 0.08, x2 = x1 + NW + 0.22;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: y + 0.16, w: PW, h: 0.34, rectRadius: 0.17, fill: { color: X.ink }, line: { color: X.ink } });
  T(s, g[0], { x: 0.5, y: y + 0.16, w: PW, h: 0.34, fontSize: 9, bold: true, color: X.white, align: 'center', valign: 'middle' });
  box(s, x1, y, NW, RH, 'F1F3F6', 'now');
  T(s, g[1], { x: x1 + 0.08, y, w: NW - 0.14, h: RH, fontSize: 8.5, color: C.accent3, valign: 'middle' });
  s.addShape(pres.shapes.CHEVRON, { x: x1 + NW + 0.05, y: y + RH / 2 - 0.08, w: 0.11, h: 0.16, fill: { color: X.teal }, line: { color: X.teal } });
  box(s, x2, y, FW, RH, 'EEF2FB', 'fp');
  s.addShape(pres.shapes.RECTANGLE, { x: x2, y, w: 0.05, h: RH, fill: { color: X.teal }, line: { color: X.teal } });
  T(s, g[2], { x: x2 + 0.13, y, w: FW - 0.17, h: RH, fontSize: 8.8, bold: true, color: C.text2, valign: 'middle' }); });
// 오른쪽: 같은 흐름 → AI 글래스 (실제 화면)
const RX = 4.98, RW = 4.52, RY = LY - 0.04, RHh = 5.02 - RY;
box(s, RX, RY, RW, RHh, 'FFFFFF', 'glass');
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: RX, y: RY, w: RW, h: RHh, rectRadius: 0.06, fill: { type: 'none' }, line: { color: X.teal, width: 1.25 } });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: RX + 0.12, y: RY + 0.1, w: 0.46, h: 0.22, rectRadius: 0.11, fill: { color: X.teal }, line: { color: X.teal } });
T(s, 'MX', { x: RX + 0.12, y: RY + 0.1, w: 0.46, h: 0.22, fontSize: 8, bold: true, color: X.white, align: 'center', valign: 'middle' });
T(s, '같은 흐름으로 AI 글래스: 말 + 스케치 → 초기 설계 · 판정', { x: RX + 0.64, y: RY + 0.07, w: RW - 0.74, h: 0.28, fontSize: 9.5, bold: true, color: C.text2, valign: 'middle' });
const iy = RY + 0.4, ih = 1.25;
fit(s, SH + 'v167_glass_sketch.png', RX + 0.1, iy, 1.55, ih, 'glasses sketch');
s.addShape(pres.shapes.CHEVRON, { x: RX + 1.7, y: iy + ih / 2 - 0.08, w: 0.11, h: 0.16, fill: { color: X.teal }, line: { color: X.teal } });
fit(s, SH + 'v167_glass_3d.png', RX + 1.86, iy, RW - 1.96, ih, 'glasses 3d');
fit(s, SH + 'v167_glass_maps.png', RX + 0.1, iy + ih + 0.04, RW - 0.2, 0.74, 'glasses fields');
T(s, '착용 무게 · 조이는 힘 · 코 받침 응력까지 초기 설계와 판정 구현', { x: RX + 0.12, y: iy + ih + 0.8, w: RW - 0.24, h: 0.24, fontSize: 7.8, color: C.text1, valign: 'middle' });
[['VD', 'TV · 사이니지'], ['DA', '가전']].forEach((r, i) => { const x = RX + 0.12 + i * 2.18, y = RY + RHh - 0.38;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: y + 0.06, w: 0.42, h: 0.22, rectRadius: 0.11, fill: { color: X.teal }, line: { color: X.teal } });
  T(s, r[0], { x, y: y + 0.06, w: 0.42, h: 0.22, fontSize: 7.5, bold: true, color: X.white, align: 'center', valign: 'middle' });
  T(s, r[1], { x: x + 0.48, y, w: 1.66, h: 0.34, fontSize: 7.8, color: C.text2, valign: 'middle' }); });
}
s.addNotes('기여 대상은 방법론. 단계별 현행 방식과 적용 후 비교. 우측은 확장 예: MX AR 글래스 — 착용 무게 · 코 하중 · 발열 · 부품 배치를 설계 사양으로 정의해 같은 흐름으로 계산 · 최적 설계. [화면에서 뺀 주석] ※ 우측 · 하단 = 확장 적용 대상. 정량 효과(해석 의뢰 기간, 시제품 반복 횟수)는 담당자 확인 필요');

// ===== v164: 확장 · 향후 계획 — 로드맵 4단계 × 확장 3축
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '5. DX 기여 · 확장' });
s.addText([{ text: '해커톤에서 ', options: { fontSize: 19 } }, { text: '핵심 엔진과 대표 사례를 완성', options: { color: '1428A0', fontSize: 19 } }, { text: '하고, 이후 ', options: { fontSize: 19 } }, { text: '사업부 적용', options: { color: '1428A0', fontSize: 19 } }, { text: '으로 확대', options: { fontSize: 19 } }], { placeholder: 'title', fontSize: 19 });
T(s, '5. 기대 효과와 계획', { x: 0.5, y: 0.08, w: 4, h: 0.22, fontSize: 9, bold: true, color: '1428A0', margin: 0 });
s.addText('대상 제품과 계산 가능한 물리 현상을 단계적으로 넓혀 실제 개발에 투입', { placeholder: 'body' });
{
const LX = 0.5, LW = 1.15, SX = 1.75, W = (9.5 - SX) / 4, HY = 1.48, RY = 2.06, RH = 0.92, RG = 0.06;
const ST = [['1단계', '엔진 · 검증 · 사례 구현', '1428A0', true], ['2단계', 'AI 엔진 (대표 사례)', '1428A0', true], ['3단계', '입력 · 연동 확대', '6F86D6', false], ['4단계', '사업부 적용', '0F1B3D', false]];
s.addShape(pres.shapes.LINE, { x: SX, y: 1.4, w: 2 * W - 0.05, h: 0, line: { color: '1428A0', width: 1.5 } });
T(s, '해커톤 구현 범위 (완료)', { x: SX, y: 1.18, w: 2 * W, h: 0.2, fontSize: 8.5, bold: true, color: '1428A0', align: 'center' });
s.addShape(pres.shapes.LINE, { x: SX + 2 * W + 0.05, y: 1.4, w: 2 * W - 0.05, h: 0, line: { color: '8A949C', width: 1.5, dashType: 'dash' } });
T(s, '이후 확대 (계획)', { x: SX + 2 * W, y: 1.18, w: 2 * W, h: 0.2, fontSize: 8.5, bold: true, color: C.accent3, align: 'center' });
ST.forEach((p, i) => { const x = SX + i * W;
  s.addShape(i ? pres.shapes.CHEVRON : pres.shapes.PENTAGON, { x, y: HY, w: W + 0.1, h: 0.46, fill: { color: p[2] }, line: { color: X.white, width: 1 }, objectName: 'stage' });
  T(s, [{ text: p[0] + '  ', options: { color: 'D9E1F5', fontSize: 7.5 } }, { text: p[1], options: { bold: true, color: X.white } }], { x: x + (i ? 0.28 : 0.1), y: HY, w: W - 0.25, h: 0.46, fontSize: 9.5, valign: 'middle' }); });
const AX = [['설계 · AI', await icon(fa.FaCube, X.white)], ['물리 · 검증', await icon(fa.FaCogs, X.white)], ['입력 · 연동', await icon(fa.FaPlug, X.white)]];
const CELL = [
  ['자전거 폰 거치대\n말 + 스케치 → 제작 파일', '같은 사례 형상 AI ·\n물리 AI 학습 · 탐색', '실물 출력 · 실측 비교\n제품별 템플릿 · 근거 DB 확대', 'MX AR 글래스 · 폴더블 시범\n기존 설계 절차와 비교'],
  ['구조 · 진동 · 충격 · 열\nFEM 엔진 · 자동 판정', 'FEM 결과로\n물리 AI 학습', 'AI 예측 정확도 · 탐색 시간 검증\n제작성 검사 고도화', '낙하 · 피로 · 소음 · 전자기\n물리 모듈 추가'],
  ['LLM + 근거 DB\n→ 설계 사양', 'GUI 한 화면\n입력 → 검증 → 제작 파일', '문서 · 사진 · STEP 입력\n사내 특허 시스템 연동', '사내 설계 도구 · CAD 연계\n설계 데이터 누적']];
AX.forEach((a, r) => { const y = RY + r * (RH + RG);
  box(s, LX, y, LW, RH, X.ink, 'axis');
  s.addImage({ data: a[1], x: LX + LW / 2 - 0.13, y: y + 0.18, w: 0.26, h: 0.26 });
  T(s, a[0], { x: LX, y: y + 0.5, w: LW, h: 0.3, fontSize: 10, bold: true, color: X.white, align: 'center', valign: 'middle' });
  CELL[r].forEach((t, c) => { const x = SX + c * W + 0.03, done = c < 2;
    box(s, x, y, W - 0.06, RH, done ? 'EEF2FB' : X.tint, 'cell');
    if (done) s.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.05, h: RH, fill: { color: '1428A0' }, line: { color: '1428A0' } });
    T(s, (done ? [{ text: '✓ ', options: { bold: true, color: '1428A0' } }] : []).concat([{ text: t, options: { color: done ? C.text2 : C.text1, bold: done } }]), { x: x + 0.12, y, w: W - 0.22, h: RH, fontSize: 8.3, valign: 'middle' }); }); });
}
s.addNotes('확장과 향후 계획을 한 장으로. 1 · 2단계는 해커톤 구현 범위(완료): 설계 사양 AI(LLM + 근거 DB), FEM 엔진 · 자동 판정, 자전거 폰 거치대 사례 구현과 제작 파일, 같은 사례의 형상 AI(DeepSDF) · 물리 AI(GINO · FNO) 학습과 탐색, GUI. 3단계 입력 · 연동 확대: 문서 · 사진 · STEP 입력, 사내 특허 시스템 연동(청구항 효과를 같은 조건 FEM으로 계산 확인, 법적 유효성 판단 아님), 제작성 검사 고도화, 근거 리포트. 4단계 사업부 적용: MX AR 글래스 · 폴더블 시범 후 VD TV · DA 가전, 물리 모듈 확장(낙하 · 피로 · 소음 · 전자기), 사내 설계 도구 · CAD 연계와 데이터 누적.');

pres.addSection({ title: '마무리' });
// ---------- 9. 마무리
s = pres.addSlide({ masterName: 'DARK', sectionTitle: '마무리' });
T(s, '형상을\n성능으로 증명', { x: 0.6, y: 1.5, w: 5.0, h: 1.4, fontSize: 32, bold: true, color: C.background1 });
T(s, '모든 아이디어를 만들 수 있는 제품으로', { x: 0.6, y: 3.05, w: 5.0, h: 0.4, fontSize: 16, color: C.accent4 });
box(s, 5.9, 1.1, 3.7, 3.2, 'FFFFFF', 'final card');
fit(s, SH + 'v179_cover_phone.png', 6.0, 1.25, 3.5, 2.9, 'final design');

/* v177: 부록 전체 제외 — 내용은 build_v176.js 에 보존 */
await pres.writeFile({ fileName: OUT });
await applyTheme(OUT, THEME);
console.log('ok', OUT);
})();