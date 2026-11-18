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
  [Rr, T1, 'v180_cover_base.png', '2 초기 설계 · 해석', '판 끝 공진 · 기준 미달', C.accent5],
  [Rr, T2, 'v180_cover_body.png', '3 AI 최적 설계', '흔들림 77% 감소 · 폰 장착', C.accent1],
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
  ['2. 3D 형상 생성', '초기 설계 (초기안)', 'v146_p_base.png'], ['3. 성능 해석', '진동 · 충격 · 열 판정 → 미달', 'v146_c_base.png'], ['4. 최적 설계', '구조 최적화 → FEM 정밀화', 'v79_evo.png'], ['5. 검증 · 제작 파일', '출력 형상 재판정 → STL · 도면', 'v25_asm.png']];
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
// ===== v181: 해결 방안 — 동작 흐름(4쪽) + 핵심 기술(5쪽) 통합
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 제안 아이디어' });
s.addText([{ text: 'AI가 ' }, { text: '설계하고, 성능을 계산하고, 스스로 고치는', options: { color: '1428A0' } }, { text: ' 자동 설계 흐름' }], { placeholder: 'title' });
T(s, '2. 해결 방안', { x: 0.5, y: 0.08, w: 4, h: 0.22, fontSize: 9, bold: true, color: '1428A0', margin: 0 });
s.addText('요구를 근거 있는 수치로 바꾸고, 물리 계산으로 형상을 최적화한 뒤 제작 형상으로 다시 확인', { placeholder: 'body' });
{ const SS = [['입력', '말 · 스케치 · 문서', ''], ['1 설계 사양', '', 'A'], ['2 3D 형상 생성', '', 'B'], ['3 성능 해석', '', 'B'], ['4 최적 설계', '', 'B'], ['5 검증 · 출력', '', 'C']];
SS.forEach((p, i) => { const x = 0.5 + i * 1.5;
  s.addShape(i ? pres.shapes.CHEVRON : pres.shapes.PENTAGON, { x, y: 1.2, w: 1.56, h: 0.25, fill: { color: i ? X.ink : X.mute }, line: { color: X.white, width: 0.75 }, objectName: 'step' });
  const runs = [{ text: p[0] + (p[1] ? '  ' : ''), options: { bold: true, color: X.white } }];
  if (p[1]) runs.push({ text: p[1], options: { color: 'E3E8F4' } });
  if (p[2]) runs.push({ text: '   ' + p[2], options: { bold: true, color: X.amber } });
  T(s, runs, { x: x + (i ? 0.18 : 0.06), y: 1.2, w: 1.28, h: 0.25, fontSize: 7, valign: 'middle', align: i ? 'center' : 'left' }); }); }
{
const CW = 2.93, G = 0.1, Y = 1.53, H = 3.17, BL = '1428A0', SL = '46536A';
const card = (i, L, name, col) => { const x = 0.5 + i * (CW + G);
  box(s, x, Y, CW, H, 'FFFFFF', 'core');
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: Y, w: CW, h: H, rectRadius: 0.08, fill: { type: 'none' }, line: { color: col, width: 1.25 }, objectName: 'frame' });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.12, y: Y + 0.12, w: 0.34, h: 0.34, rectRadius: 0.06, fill: { color: col }, line: { color: col }, objectName: 'letter' });
  T(s, L, { x: x + 0.12, y: Y + 0.12, w: 0.34, h: 0.34, fontSize: 13, bold: true, color: X.white, align: 'center', valign: 'middle' });
  T(s, name, { x: x + 0.54, y: Y + 0.12, w: CW - 0.6, h: 0.34, fontSize: 12, bold: true, color: col, valign: 'middle' });
  return x; };
const IC5 = { llm: await icon(fa.FaBrain, '1428A0'), db: await icon(fa.FaDatabase, '1428A0'), chk: await icon(fa.FaClipboardCheck, '46536A') };
const blk = (x, y, w, h, col) => s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.04, fill: { color: 'FFFFFF' }, line: { color: col, width: 1 }, objectName: 'blk' });
const dn = (x, y, h, col) => s.addShape(pres.shapes.LINE, { x, y, w: 0, h, line: { color: col || X.mute, width: 1.25, endArrowType: 'triangle' }, objectName: 'arr' });
const eff = (x, t, col) => T(s, t, { x: x + 0.12, y: Y + 2.86, w: CW - 0.24, h: 0.28, fontSize: 8.5, bold: true, color: col, valign: 'middle' });
// A
let x = card(0, 'A', '설계 사양 AI', BL);
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.15, y: Y + 0.56, w: CW - 0.3, h: 1.04, rectRadius: 0.04, fill: { color: 'FFFFFF' }, line: { color: SL, width: 1 }, objectName: 'in' });
fit(s, SH + 'v17_sketch.png', x + 0.19, Y + 0.6, 1.4, 0.96, 'sketch');
T(s, [{ text: '입력', options: { bold: true, color: SL, breakLine: true } }, { text: '스케치 +\n', options: { fontSize: 6.8, color: C.text1 } }, { text: '"울퉁불퉁한 길에서도\n안 흔들리게,\n최대한 가볍게"', options: { fontSize: 7, bold: true, color: C.text2 } }], { x: x + 1.62, y: Y + 0.56, w: CW - 1.8, h: 1.04, fontSize: 7.5, valign: 'middle' });
dn(x + CW / 2, Y + 1.6, 0.06);
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.15, y: Y + 1.66, w: CW - 0.3, h: 0.28, rectRadius: 0.04, fill: { color: 'FFFFFF' }, line: { color: BL, width: 1 }, objectName: 'ld' });
s.addImage({ data: IC5.llm, x: x + 0.22, y: Y + 1.7, w: 0.2, h: 0.2 });
T(s, [{ text: 'LLM ', options: { bold: true, color: BL } }, { text: '의미 해석', options: { color: C.text1 } }], { x: x + 0.45, y: Y + 1.66, w: 1.0, h: 0.28, fontSize: 7.3, valign: 'middle' });
T(s, '+', { x: x + 1.38, y: Y + 1.66, w: 0.14, h: 0.28, fontSize: 9, bold: true, color: BL, align: 'center', valign: 'middle' });
s.addImage({ data: IC5.db, x: x + 1.54, y: Y + 1.7, w: 0.2, h: 0.2 });
T(s, [{ text: '근거 DB ', options: { bold: true, color: BL } }, { text: '수치', options: { color: C.text1 } }], { x: x + 1.77, y: Y + 1.66, w: 0.95, h: 0.28, fontSize: 7.3, valign: 'middle' });
dn(x + CW / 2, Y + 1.94, 0.05);
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.15, y: Y + 1.99, w: CW - 0.3, h: 0.83, rectRadius: 0.04, fill: { color: 'EEF2FB' }, line: { color: BL, width: 1.5 }, objectName: 'spec' });
T(s, '설계 사양 (JSON) · 항목마다 출처', { x: x + 0.22, y: Y + 2.0, w: CW - 0.44, h: 0.19, fontSize: 7.6, bold: true, color: BL, valign: 'middle' });
[['"안 흔들리게"', '진동수 ≥ 95 Hz', '근거 DB', BL], ['"울퉁불퉁한 길"', '충격 48.5 g', '근거 DB', BL], ['스케치 각도', '거치 35°', '질문', '8A949C']].forEach((r, k) => { const ry = Y + 2.19 + k * 0.205;
  T(s, r[0], { x: x + 0.22, y: ry, w: 0.92, h: 0.21, fontSize: 7, bold: true, color: C.text2, valign: 'middle' });
  T(s, '→ ' + r[1], { x: x + 1.1, y: ry, w: 1.08, h: 0.21, fontSize: 7, color: C.text1, valign: 'middle' });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 2.2, y: ry + 0.025, w: 0.5, h: 0.16, rectRadius: 0.08, fill: { color: r[3] }, line: { color: r[3] } });
  T(s, r[2], { x: x + 2.2, y: ry + 0.025, w: 0.5, h: 0.16, fontSize: 6, bold: true, color: X.white, align: 'center', valign: 'middle' }); });
eff(x, '모든 수치에 출처, 근거가 없으면 묻는다', BL);
// B
x = card(1, 'B', '최적 설계 AI', BL);
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.15, y: Y + 0.55, w: CW - 0.3, h: 0.3, rectRadius: 0.04, fill: { color: 'F5F7FB' }, line: { color: SL, width: 1 }, objectName: 'first' });
fit(s, SH + 'v146_p_base.png', x + 0.18, Y + 0.565, 0.3, 0.27, 'first design');
T(s, [{ text: '초기 설계', options: { bold: true, color: SL } }, { text: '  설계 사양 + 템플릿으로 형상 생성', options: { fontSize: 6.5, color: C.text1 } }], { x: x + 0.52, y: Y + 0.55, w: CW - 0.7, h: 0.3, fontSize: 7.5, valign: 'middle' });
dn(x + CW / 2, Y + 0.85, 0.05);
blk(x + 0.15, Y + 0.9, 1.24, 0.72, '4F6BD8');
fit(s, SH + 'v87_gen_grid.png', x + 0.19, Y + 0.93, 1.16, 0.34, 'DeepSDF');
T(s, [{ text: '형상 AI', options: { bold: true, color: '4F6BD8', breakLine: true } }, { text: '잠재 코드 → 3D 형상', options: { fontSize: 6.3, color: C.text1 } }], { x: x + 0.15, y: Y + 1.27, w: 1.24, h: 0.34, fontSize: 8, align: 'center', valign: 'middle' });
blk(x + 1.54, Y + 0.9, 1.24, 0.72, BL);
fit(s, SH + 'v125_phys_fields.png', x + 1.58, Y + 0.93, 1.16, 0.28, 'neural operator');
T(s, [{ text: '물리 AI', options: { bold: true, color: BL, breakLine: true } }, { text: '형상 → 성능 분포 즉시 예측', options: { fontSize: 6.3, color: C.text1 } }], { x: x + 1.54, y: Y + 1.21, w: 1.24, h: 0.4, fontSize: 8, align: 'center', valign: 'middle' });
s.addShape(pres.shapes.LINE, { x: x + 1.39, y: Y + 1.12, w: 0.15, h: 0, line: { color: SL, width: 1, endArrowType: 'triangle' } });
s.addShape(pres.shapes.LINE, { x: x + 1.39, y: Y + 1.38, w: 0.15, h: 0, flipH: true, line: { color: SL, width: 1, endArrowType: 'triangle' } });
T(s, '최적화: 반복마다 형상을 고치며 성능 개선', { x: x + 0.15, y: Y + 1.63, w: CW - 0.3, h: 0.16, fontSize: 6.5, bold: true, color: BL, align: 'center' });
['00', '09', '16', '28'].forEach((k, i) => { const fw = (CW - 0.3) / 4; fit(s, SH + 'v156_evo_' + k + '.png', x + 0.15 + i * fw, Y + 1.8, fw - 0.04, 0.5, 'evo ' + k);
  if (i < 3) s.addShape(pres.shapes.CHEVRON, { x: x + 0.15 + (i + 1) * fw - 0.06, y: Y + 2.0, w: 0.05, h: 0.08, fill: { color: BL }, line: { color: BL } }); });
dn(x + CW / 2, Y + 2.3, 0.05);
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.15, y: Y + 2.36, w: CW - 0.3, h: 0.46, rectRadius: 0.04, fill: { color: 'F5F7FB' }, line: { color: SL, width: 1 }, objectName: 'fem' });
T(s, [{ text: '구조 최적화 + FEM 정밀화', options: { bold: true, color: SL, breakLine: true } }, { text: '상위 후보 몇 개만 정밀 계산 · 제조 제약 반영', options: { fontSize: 6.3, color: C.text1 } }], { x: x + 0.22, y: Y + 2.36, w: CW - 0.44, h: 0.46, fontSize: 7.5, valign: 'middle' });
eff(x, '형상 생성 · 성능 예측 · 최적화를 미분으로 연결', BL);
// C
x = card(2, 'C', '자동 검증', SL);
[['v44_body.png', '① 제작 형상 변환'], ['v136_vox.png', '② 2 mm 재격자화'], ['v136_fem.png', '③ FEM 재계산']].forEach((p, k) => { const px = x + 0.15 + k * 0.9;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: px, y: Y + 0.6, w: 0.8, h: 0.66, rectRadius: 0.04, fill: { color: 'FFFFFF' }, line: { color: SL, width: 0.75 }, objectName: 'thumb' });
  fit(s, SH + p[0], px + 0.03, Y + 0.63, 0.74, 0.6, p[1]);
  T(s, p[1], { x: px - 0.05, y: Y + 1.27, w: 0.9, h: 0.15, fontSize: 6.3, bold: true, color: SL, align: 'center' });
  if (k < 2) s.addShape(pres.shapes.LINE, { x: px + 0.81, y: Y + 0.93, w: 0.08, h: 0, line: { color: SL, width: 1, endArrowType: 'triangle' } }); });
dn(x + CW / 2, Y + 1.43, 0.08);
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.15, y: Y + 1.52, w: CW - 0.3, h: 0.72, rectRadius: 0.04, fill: { color: 'F5F7FB' }, line: { color: SL, width: 1 }, objectName: 'judge' });
s.addImage({ data: IC5.chk, x: x + 0.22, y: Y + 1.6, w: 0.18, h: 0.18 });
T(s, '④ 자동 판정', { x: x + 0.45, y: Y + 1.58, w: 2.2, h: 0.22, fontSize: 8, bold: true, color: SL, valign: 'middle' });
T(s, '진동 · 열 · 충격 · 처짐을 기준과 비교\n연결성 · 중간 밀도까지 확인', { x: x + 0.22, y: Y + 1.82, w: CW - 0.44, h: 0.38, fontSize: 7.2, color: C.text1, valign: 'middle' });
dn(x + 0.75, Y + 2.24, 0.1, BL);
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.15, y: Y + 2.34, w: 1.22, h: 0.42, rectRadius: 0.05, fill: { color: BL }, line: { color: BL }, objectName: 'pass' });
T(s, '합격 → 제작 파일', { x: x + 0.15, y: Y + 2.34, w: 1.22, h: 0.42, fontSize: 7.8, bold: true, color: X.white, align: 'center', valign: 'middle' });
dn(x + 2.15, Y + 2.24, 0.1, SL);
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 1.48, y: Y + 2.34, w: 1.3, h: 0.42, rectRadius: 0.05, fill: { color: 'FFFFFF' }, line: { color: SL, width: 1, dashType: 'dash' }, objectName: 'fail' });
T(s, [{ text: '불합격 → B 최적 설계', options: { bold: true, breakLine: true } }, { text: '미달 항목만큼 목표 조정', options: { fontSize: 6.2 } }], { x: x + 1.48, y: Y + 2.34, w: 1.3, h: 0.42, fontSize: 7.5, color: SL, align: 'center', valign: 'middle' });
eff(x, '제작될 형상 그대로 판정, 합격만 출력', SL);
// 카드 사이 흐름 화살표
[0.5 + CW + G / 2, 0.5 + 2 * (CW + G) - G / 2].forEach(cx => s.addShape(pres.shapes.RIGHT_ARROW, { x: cx - 0.11, y: Y + 0.18, w: 0.22, h: 0.22, fill: { color: X.amber }, line: { color: X.white, width: 1 }, objectName: 'flow' }));
// 아래: LLM 에이전트
box(s, 0.5, 4.78, 9.0, 0.36, X.ink, 'agent');
T(s, [{ text: 'LLM 에이전트   ', options: { bold: true, color: X.amber } }, { text: 'A → B → C를 차례로 호출하고 결과를 기준과 대조, 미달 항목을 반영해 재설계와 재검증', options: { color: X.white } }], { x: 0.65, y: 4.78, w: 8.7, h: 0.36, fontSize: 8.5, valign: 'middle' });
}
s.addNotes('동작 흐름과 핵심 기술을 한 장으로. 에이전트가 A 설계 사양 AI를 호출: LLM이 표현의 의미를 물리량으로 해석하고, 수치는 근거 DB(규격 · 실측 논문 · 데이터시트)에서만 가져와 항목별 출처를 붙인 JSON 설계 사양을 만든다. 근거가 없으면 사용자에게 묻는다. 설계 사양과 템플릿으로 만든 초기 설계가 B 최적 설계 AI의 출발점: 형상 AI(DeepSDF)가 형상을 잠재 변수로 표현하고, 물리 AI(신경 연산자, FNO · GINO)가 형상에서 응력 · 온도 분포를 즉시 예측해 기울기를 준다. 미분으로 후보를 찾고, 상위 후보만 SIMP + MMA 구조 최적화 + FEM으로 제조 제약을 지키며 정밀화. 계산 결과는 물리 AI 학습 데이터로 재활용. 최종 형상은 제작 형상 변환(CAD: 표면 정리 · 고정 부품 합치기 · 구멍 · 홈) 후 STL로 C 자동 검증에 전달: 재격자화 · FEM 재계산 · 기준 · 연결성 · 중간 밀도 판정. 불합격이면 미달 항목만큼 목표를 조여 B로 회귀, 합격이면 제작 파일 출력. 판정 결과 수치는 3. 구현 결과(성능 개선 쪽) 참고. 물리 AI는 현재 FNO로 구현, GINO는 메시 · STEP 입력용 확장. 학습은 진행 중이며 구현 결과는 구조 최적화 경로.');

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
badge(6.1, SY + 0.62, 4, '최적 설계 → FEM 통과 (출력 변환 전)', 2.05);
badge(8.0, SY + 1.95, 5, '초기 → 최적 비교', 1.05);
// AI 형상 탐색 과정 (같은 화면의 재생 프레임)
const EY = SY + SHh + 0.12, EH = 5.02 - EY;
box(s, 0.5, EY, 9.0, EH, X.tint, 'evo');
T(s, [{ text: '최적 설계 과정', options: { bold: true, color: C.accent1, breakLine: true } }, { text: '초기 설계에서 출발,\n반복마다 형상을\n고치며 성능 개선', options: { fontSize: 7.3, color: C.text1 } }], { x: 0.6, y: EY + 0.05, w: 1.2, h: EH - 0.1, fontSize: 9.5, valign: 'middle' });
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
s.addText('같은 조건 FEM 비교에서 진동, 충격, 열 성능을 개선하고 바로 출력할 수 있는 형태로 완성', { placeholder: 'body' });
{
const LX = 0.5, LW = 0.62, MW = 2.2, AX = 1.18, BX = 3.44, CBX = 5.7, RX = 6.06, RW = 3.44;
T(s, '초기 설계', { x: AX, y: 1.18, w: MW, h: 0.24, fontSize: 10, bold: true, color: C.accent5, align: 'center' });
T(s, 'FormProof 최적 설계', { x: BX, y: 1.18, w: MW, h: 0.24, fontSize: 10, bold: true, color: C.accent1, align: 'center' });
const PR = [
  { lab: '흔들림', sub: '길 진동', a: 'v179_Rbase_clean.png', b: 'v179_Rbody_clean.png', ta: '판 끝 공진 (30.5 Hz)', tb: '최대 흔들림 77% 감소 (168 Hz)', cb: 'v26_cb_R.png' },
  { lab: '충격', sub: '48.5 g', a: 'v28_Vbase.png', b: 'v51_Vbody.png', ta: '판 뿌리에 응력 집중', tb: '충격 응력 80% 감소 (14.7 → 2.9 MPa)', cb: 'v26_cb_V.png' },
  { lab: '열', sub: '폰 4 W', a: 'v25_Tbase.png', b: 'v51_Tbody.png', ta: '뒷면을 덮어 열이 갇힘', tb: '온도 상승 12 °C 저감 (32.6 → 20.8 °C)', cb: 'v26_cb_T.png' }];
PR.forEach((r, i) => { const y = 1.44 + i * 1.2, H = 1.13;
  box(s, LX, y, LW, H, X.ink, 'row label');
  T(s, r.lab, { x: LX, y: y + 0.28, w: LW, h: 0.3, fontSize: 11, bold: true, color: C.background1, align: 'center' });
  T(s, r.sub, { x: LX, y: y + 0.6, w: LW, h: 0.24, fontSize: 7, color: C.accent4, align: 'center' });
  [[r.a, r.ta, AX, C.accent5], [r.b, r.tb, BX, C.accent1]].forEach(c => {
    box(s, c[2], y, MW, H, 'FFFFFF', 'map');
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: c[2], y, w: MW, h: H, rectRadius: 0.06, fill: { type: 'none' }, line: { color: X.line, width: 0.75 }, objectName: 'map frame' });
    fit(s, SH + c[0], c[2] + 0.04, y + 0.03, MW - 0.08, H - 0.33, r.lab);
    T(s, c[1], { x: c[2] + 0.03, y: y + H - 0.29, w: MW - 0.06, h: 0.26, fontSize: 7.8, bold: true, color: c[3], align: 'center', valign: 'middle' }); });
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
  ['생성형 설계 도구', '조건 → 최적 형상 (Fusion 360 등)', [0, 0, 1, 1, 0], '조건 준비 · 도구 연결은 사용자 몫'],
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
s.addNotes('요구 정의 = 문제와 요구를 목표 · 제약 수치로 정리. 성능 해석 = 시뮬레이션. 최고 난도 단계: 물리 조건 설정, 해석, 최적 설계(최적화 결과의 CAD 재구성 및 반복). 해석 도구는 계산만 자동이며 전후 단계(모델링, 조건, 최적 설계, 재검증)는 전문가 수행. FormProof는 6단계 전체를 AI로 수행. [화면에서 뺀 주석] 해석 도구: 결과 확보 1주 이상 67% (engineering.com · Dassault 2022 설문). 범용 LLM: 같은 조건 독립 3회, 같은 해석기로 판정 → 3회 모두 불합격(8쪽). 비교는 범주별 일반 기능 기준.');

// ===== v162: 범용 LLM 단독 vs FormProof (같은 요청 · 같은 검증)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '4. 기술 차별성' });
s.addText([{ text: '같은 요청에도 ' }, { text: '일반 AI의 설계는 세 번 모두 기준 미달', options: { color: '1428A0' } }], { placeholder: 'title' });
T(s, '4. 기술 차별성', { x: 0.5, y: 0.08, w: 4, h: 0.22, fontSize: 9, bold: true, color: '1428A0', margin: 0 });
s.addText('같은 요청과 같은 FEM 평가에서, 계산 없이 만든 설계는 성능을 보장하지 못함', { placeholder: 'body' });
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
    ['흔들림 (핸들바의 1.5배 이하)', d.sh ? '통과 ✓' : '초과 ✕', d.sh ? (fp ? C.accent1 : C.text1) : '5E6B7D'],
    ['온도 상승 (≤ 21 °C)', `${d.t} °C ${ok(d.t <= 21)}`, d.t > 21 ? '5E6B7D' : (fp ? C.accent1 : C.text1)], ['무게 (출력 변환 전)', d.m + ' g', C.text1]];
  R.forEach((r, k) => { const y = Y0 + 1.56 + k * 0.32;
    s.addShape(pres.shapes.LINE, { x: x + 0.1, y: y + 0.3, w: LW - 0.2, h: 0, line: { color: 'DDE3F0', width: 0.5 } });
    T(s, r[0], { x: x + 0.1, y, w: r[0].startsWith('흔들림') ? 1.45 : 1.05, h: 0.3, fontSize: r[0].startsWith('흔들림') ? 7 : 7.5, color: C.accent3, valign: 'middle' });
    T(s, r[1], { x: x + 1.0, y, w: LW - 1.08, h: 0.3, fontSize: 9, bold: true, color: r[2], align: 'right', valign: 'middle' }); });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.1, y: Y0 + CH - 0.5, w: LW - 0.2, h: 0.4, rectRadius: 0.06, fill: { color: fp ? X.teal : 'E4E8EF' }, line: { color: fp ? X.teal : 'E4E8EF' }, objectName: 'verdict' });
  T(s, (fp ? '합격 · ' : '불합격 · ') + d.note, { x: x + 0.14, y: Y0 + CH - 0.5, w: LW - 0.28, h: 0.4, fontSize: 9, bold: true, color: fp ? C.background1 : '46536A', align: 'center', valign: 'middle' }); });
}
s.addNotes('동일 요청 · 동일 일체형 조건을 도구 없는 LLM 세션 3개에 입력. 3개 세션 모두 트러스 · 스파인 구조 제시, 진동 기준(60~90 Hz)과 흔들림 1.2~1.3배를 자체 예측. 동일 해석기 판정 결과: A는 흔들림 1.37배로 양호하나 폰 뒷면을 덮어 온도 기준(21 °C) 초과, 10 g 더 무거움. B는 앞뒤 2.95배, C는 위쪽 레일 공진으로 6.6배. 예측 진동수도 실제와 불일치. 결론: LLM 단독으로 양호한 안이 나올 수는 있으나 계산 없이는 판별 불가. FormProof는 전 기준을 계산으로 확인, 최경량 안 도출. [화면에서 뺀 주석] ※ LLM 단독 = 도구 · 계산 없이 같은 요청 · 같은 일체형 조건(35°, 같은 걸이 · 집게 · 레일, 311 g)을 받은 독립 세션 3회(Claude, 2026-11-15). 판정은 모두 같은 2 mm 격자 FEM · 감쇠비 3% · 발열 4 W. 흔들림 = 핸들바 대비 최대(10–100 Hz, 위아래 · 앞뒤 중 큰 값). 그림 색 = 같은 척도의 흔들림 분포. FormProof 값 = 출력 변환 전 최적화 결과(LLM 안과 같은 단계). 출력 몸체(81.3 g)도 재해석 통과');

pres.addSection({ title: '5. DX 기여 · 확장' });
// ===== v167: DX 기여 — 설계 방식 변화 + 같은 흐름으로 다른 제품 (AI 글래스 실제 화면)
// ===== v181: 기대 효과 + 확대 계획 통합
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '5. DX 기여 · 확장' });
s.addText([{ text: '성능 확인을 ' }, { text: '며칠에서 몇 초로', options: { color: '1428A0' } }, { text: ' 줄이고, 단계적으로 ' }, { text: '사업부 제품에 적용', options: { color: '1428A0' } }], { placeholder: 'title' });
T(s, '5. 기대 효과와 계획', { x: 0.5, y: 0.08, w: 4, h: 0.22, fontSize: 9, bold: true, color: '1428A0', margin: 0 });
s.addText('자전거 폰 거치대로 핵심 엔진을 완성했고, 같은 방식을 AI 글래스, 폴더블, TV, 가전 개발로 넓힘', { placeholder: 'body' });
{
const BY = 1.2;
box(s, 0.5, BY, 9.0, 0.48, X.ink, 'hero');
T(s, [{ text: '성능 확인  ', options: { color: '9FB4EA', bold: true, fontSize: 10 } }, { text: '해석 의뢰 · 결과 대기 (며칠~몇 주)', options: { color: 'B8C2D6', fontSize: 10.5 } }, { text: '   →   ', options: { color: X.white, bold: true, fontSize: 12 } }, { text: '입력하면 몇 초 안에 초기 설계와 성능 판정', options: { color: X.white, bold: true, fontSize: 12.5 } }],
  { x: 0.7, y: BY, w: 8.6, h: 0.48, valign: 'middle' });
// 왼쪽: 설계 방식 변화 (2줄)
const LY = 1.8, LW2 = 3.3;
T(s, '설계 방식이 바뀌는 점', { x: 0.5, y: LY, w: LW2, h: 0.22, fontSize: 9, bold: true, color: C.accent1 });
[['설계 초기', '설계자가 직접 성능 확인', '해석 의뢰와 결과 대기 없이 바로 판정'], ['반복 · 시제품', '반복 설계와 제작 전 확인 자동화', '미달 항목만 고치고 출력 전에 검증']].forEach((g, i) => { const y = LY + 0.3 + i * 0.82, H = 0.72;
  box(s, 0.5, y, LW2, H, 'EEF2FB', 'fp');
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y, w: 0.05, h: H, fill: { color: X.teal }, line: { color: X.teal } });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.68, y: y + 0.11, w: 0.9, h: 0.24, rectRadius: 0.12, fill: { color: X.ink }, line: { color: X.ink } });
  T(s, g[0], { x: 0.68, y: y + 0.11, w: 0.9, h: 0.24, fontSize: 7.8, bold: true, color: X.white, align: 'center', valign: 'middle' });
  T(s, g[1], { x: 1.66, y: y + 0.08, w: LW2 - 1.24, h: 0.3, fontSize: 9.5, bold: true, color: C.text2, valign: 'middle' });
  T(s, g[2], { x: 0.68, y: y + 0.4, w: LW2 - 0.3, h: 0.24, fontSize: 8, color: C.text1, valign: 'middle' }); });
// 오른쪽: AI 글래스 확장 예 (크게)
const RX = 3.95, RW = 5.55, RY = LY, RHh = 1.9;
box(s, RX, RY, RW, RHh, 'FFFFFF', 'glass');
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: RX, y: RY, w: RW, h: RHh, rectRadius: 0.06, fill: { type: 'none' }, line: { color: X.teal, width: 1.25 } });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: RX + 0.1, y: RY + 0.08, w: 0.42, h: 0.2, rectRadius: 0.1, fill: { color: X.teal }, line: { color: X.teal } });
T(s, 'MX', { x: RX + 0.1, y: RY + 0.08, w: 0.42, h: 0.2, fontSize: 7.5, bold: true, color: X.white, align: 'center', valign: 'middle' });
T(s, '같은 흐름으로 AI 글래스: 말 + 스케치 → 초기 설계 · 판정', { x: RX + 0.58, y: RY + 0.05, w: RW - 0.66, h: 0.26, fontSize: 9, bold: true, color: C.text2, valign: 'middle' });
const iy = RY + 0.36, ih = 1.0;
fit(s, SH + 'v167_glass_sketch.png', RX + 0.08, iy, 1.45, ih, 'glasses sketch');
s.addShape(pres.shapes.CHEVRON, { x: RX + 1.57, y: iy + ih / 2 - 0.07, w: 0.1, h: 0.14, fill: { color: X.teal }, line: { color: X.teal } });
fit(s, SH + 'v167_glass_3d.png', RX + 1.71, iy, 1.4, ih, 'glasses 3d');
fit(s, SH + 'v167_glass_maps.png', RX + 3.17, iy, RW - 3.25, ih, 'glasses fields');
T(s, '착용 무게 · 조이는 힘 · 코 받침 응력까지 초기 설계와 판정 구현', { x: RX + 0.12, y: iy + ih + 0.05, w: RW - 0.24, h: 0.2, fontSize: 7.8, color: C.text1, valign: 'middle' });
T(s, '폴더블 · TV · 가전도 제품별 설계 사양과 물리 모델을 확장해 같은 흐름 적용', { x: RX + 0.12, y: iy + ih + 0.26, w: RW - 0.24, h: 0.2, fontSize: 7.8, bold: true, color: X.teal, valign: 'middle' });
// 아래: 로드맵 (1단계 완료 · 2단계 진행 중 · 3 · 4단계 계획)
const SX = 0.5, W = 9.0 / 4, HY = 4.1, CY = 4.49, CH = 0.62;
[[SX, W, '해커톤 구현 (완료)', '1428A0', 'solid'], [SX + W, W, 'AI 엔진 학습 (진행 중)', '5B73C8', 'solid'], [SX + 2 * W, 2 * W, '이후 확대 (계획)', '8A949C', 'dash']].forEach(([x, w, t, col, d]) => {
  s.addShape(pres.shapes.LINE, { x: x + 0.04, y: 4.05, w: w - 0.08, h: 0, line: { color: col, width: 1.5, dashType: d } });
  T(s, t, { x, y: 3.86, w, h: 0.17, fontSize: 7.5, bold: true, color: col === '8A949C' ? C.accent3 : col, align: 'center' }); });
const ST = [['1단계', '엔진 · 검증 · 사례 구현', '1428A0', '자전거 폰 거치대, GUI 한 화면\n말 + 스케치 → 검증된 제작 파일', 'done'], ['2단계', 'AI 엔진 학습', '5B73C8', '형상 AI · 물리 AI 학습\n탐색 속도 · 정확도 검증', 'wip'],
  ['3단계', '입력 · 연동 확대', '6F86D6', '문서 · 사진 · STEP 입력\n실물 출력 · 실측 비교', ''], ['4단계', '사업부 적용', '0F1B3D', 'MX AR 글래스 · 폴더블 시범\nVD TV · DA 가전, 물리 모듈 확대', '']];
ST.forEach((p, i) => { const x = SX + i * W, done = p[4] === 'done', wip = p[4] === 'wip';
  s.addShape(i ? pres.shapes.CHEVRON : pres.shapes.PENTAGON, { x, y: HY, w: W + 0.1, h: 0.34, fill: { color: p[2] }, line: { color: X.white, width: 1 }, objectName: 'stage' });
  T(s, [{ text: p[0] + '  ', options: { color: 'D9E1F5', fontSize: 7 } }, { text: p[1], options: { bold: true, color: X.white } }], { x: x + (i ? 0.26 : 0.1), y: HY, w: W - 0.25, h: 0.34, fontSize: 8.5, valign: 'middle' });
  box(s, x + 0.03, CY, W - 0.06, CH, done ? 'EEF2FB' : X.tint, 'cell');
  if (done || wip) s.addShape(pres.shapes.RECTANGLE, { x: x + 0.03, y: CY, w: 0.05, h: CH, fill: { color: p[2] }, line: { color: p[2] } });
  T(s, (done ? [{ text: '✓ ', options: { bold: true, color: '1428A0' } }] : []).concat([{ text: p[3], options: { color: done ? C.text2 : C.text1, bold: done } }]), { x: x + 0.15, y: CY, w: W - 0.24, h: CH, fontSize: 7.8, valign: 'middle' }); });
}
s.addNotes('기대 효과와 확대 계획을 한 장으로. 기여 대상은 방법론: 성능 확인을 해석 의뢰 · 결과 대기에서 입력 즉시 판정으로. 몇 초 근거: GUI 파이프라인(말 → 설계 사양 → 템플릿 초기 설계 → 약 1,600 요소 FEM 고유진동 · 흔들림 판정)이 클라우드 환경에서 1초 이내(2026-11-17 측정, 0.6~0.8 s). 최적 설계는 별도 계산 시간 필요. 설계 방식 변화: 설계 초기에 설계자가 직접 성능 확인, 반복 설계와 제작 전 확인 자동화. 확장 예: MX AR 글래스 — 착용 무게 · 조이는 힘 · 코 받침 응력을 설계 사양으로 정의해 같은 흐름으로 초기 설계와 판정 구현. 로드맵: 1단계 해커톤 구현(완료) — 설계 사양 AI(LLM + 근거 DB), FEM 엔진 · 자동 판정, 구조 최적화, 자전거 폰 거치대 사례와 제작 파일, GUI. 2단계 AI 엔진 학습(진행 중) — 같은 사례의 형상 AI(DeepSDF) · 물리 AI(GINO · FNO) 학습과 탐색, 예측 정확도 · 탐색 시간 검증. 3단계 입력 · 연동 확대: 문서 · 사진 · STEP 입력, 사내 특허 시스템 연동(청구항 효과를 같은 조건 FEM으로 계산 확인, 법적 유효성 판단 아님), 실물 출력 · 실측 비교, 제품별 템플릿 · 근거 DB 확대, 제작성 검사 고도화. 4단계 사업부 적용: MX AR 글래스 · 폴더블 시범 후 기존 설계 절차와 비교, VD TV · DA 가전, 물리 모듈 확장(낙하 · 피로 · 소음 · 전자기), 사내 설계 도구 · CAD 연계와 데이터 누적. 정량 효과(해석 의뢰 기간, 시제품 반복 횟수)는 담당자 확인 필요.');

pres.addSection({ title: '마무리' });
// ---------- 9. 마무리
s = pres.addSlide({ masterName: 'DARK', sectionTitle: '마무리' });
T(s, '형상을\n성능으로 증명', { x: 0.6, y: 1.5, w: 5.0, h: 1.4, fontSize: 32, bold: true, color: C.background1 });
T(s, '모든 아이디어를 만들 수 있는 제품으로', { x: 0.6, y: 3.05, w: 5.0, h: 0.4, fontSize: 16, color: C.accent4 });
box(s, 5.9, 1.1, 3.7, 3.2, 'FFFFFF', 'final card');
fit(s, SH + 'v180_cover_solid.png', 6.0, 1.25, 3.5, 2.9, 'final design');

/* v177: 부록 전체 제외 — 내용은 build_v176.js 에 보존 */
await pres.writeFile({ fileName: OUT });
await applyTheme(OUT, THEME);
console.log('ok', OUT);
})();