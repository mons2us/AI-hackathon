// 결선 발표 v9 (v8 기반 · 데모 영상 v31(검증 구간 상자 = 오른쪽 성능 패널 전체)) · v8 (v7 기반 · 데모 영상 v30(검증 구간 상자 = 성능 전체)) · v7 (v6 기반 · 데모 영상 v29(80초 · GUI 구성 · 화면 흐름)) · v6 (v5 기반 · 화면 문구에서 FEM 표기 제거 · 데모 영상 v28(버튼 조작 장면)) · v5 (v4 기반 · B = 계산하며 다듬기, C = 완성 형상 다시 계산해 확인 — 역할 구분) = 발표초안 v196 의 3쪽(문제 정의) · 4쪽(해결 방안 파이프라인) · 9쪽(기대 효과와 계획) 그대로 + 데모 영상 쪽
// 바꾼 곳: 4쪽 AI 탐색 그림 → 결선 데모(v27)와 같은 계산의 형상 4장, '상위 후보 몇 개만' → '후보 31개만'. 사용: node build_결선발표_v2.js <출력.pptx> <영상.mp4>
const pptxgen = require('pptxgenjs');
const fs = require('fs');
const React = require('react'), RDS = require('react-dom/server'), sharp = require('sharp');
const fa = require('react-icons/fa'), md = require('react-icons/md');
const { applyTheme } = require('/root/.claude/skills/synced/1e9abda0-994b-4505-92f0-2b787b374f9b_2a6ad69a-e73b-4fbf-b931-59083e82c013/pptx/scripts/apply_theme.js');
const OUT = process.argv[2];
const SH = __dirname + '/shots/';
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
pres.title = 'FormProof 결선 발표';
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

pres.addSection({ title: '1. 문제 정의' });
// ---------- 3. 문제 정의 (v50: 공감 + 시각화 — 떠오른다 → 막힌다 → 서랍 속으로 / 이게 된다면)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '1. 문제 정의' });
s.addText([{ text: '좋은 아이디어도 ' }, { text: '성능을 확인하기 어려워', options: { color: '1428A0' } }, { text: ' 제품이 되지 못하는 현실' }], { placeholder: 'title' });
T(s, '1. 문제 정의', { x: 0.5, y: 0.08, w: 4, h: 0.22, fontSize: 9, bold: true, color: '1428A0', margin: 0 });
s.addText('CAD · 해석 전문 지식 없이는 성능을 확인할 길이 없어, 많은 아이디어가 검증 전에 멈춤', { placeholder: 'body' });
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
  { img: 'v44_llm.png', q: 'AI에게 맡겨 보니', h: '겉보기엔 맞는데\n틀렸다', e: '맞는지\n알 길이 없다' },
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
const BY2 = 3.86, BH2 = 1.0;   // v3: '해결 방향' 띠 → ③의 근거(같은 요청 LLM 3회) + 필요한 것
box(s, 0.5, BY2, 9.0, BH2, X.ink, 'evidence');
T(s, '③ AI에 맡기면\n정말 안 될까?', { x: 0.64, y: BY2 + 0.1, w: 1.6, h: 0.44, fontSize: 10.5, bold: true, color: 'FFB4BC' });
T(s, '데모와 같은 요청 · 일반 LLM 3회\n같은 정밀 시뮬레이션으로 계산', { x: 0.64, y: BY2 + 0.58, w: 1.6, h: 0.36, fontSize: 7, color: C.accent4 });
[['v_fin_L1.png', 'LLM A', '폰 온도 22.6 °C'], ['v_fin_L2.png', 'LLM B', '흔들림 2.95배'], ['v_fin_L3.png', 'LLM C', '흔들림 6.6배']].forEach((e, i) => {
  const x = 2.28 + i * 1.56, w = 1.5;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: BY2 + 0.1, w, h: 0.8, rectRadius: 0.04, fill: { color: 'FFFFFF' }, line: { color: 'FFFFFF' }, objectName: 'llm card' });
  fit(s, SH + e[0], x + 0.04, BY2 + 0.14, 0.5, 0.72, e[1] + ' 설계');
  T(s, [{ text: e[1], options: { bold: true, fontSize: 9, color: X.ink, breakLine: true } }, { text: '자체 판단 통과', options: { fontSize: 7, color: C.accent3, breakLine: true } },
        { text: '계산 → 불합격', options: { fontSize: 8, bold: true, color: 'C8323F', breakLine: true } }, { text: e[2], options: { fontSize: 7.5, bold: true, color: 'C8323F' } }],
    { x: x + 0.58, y: BY2 + 0.14, w: w - 0.6, h: 0.72, valign: 'middle' }); });
s.addShape(pres.shapes.CHEVRON, { x: 6.98, y: BY2 + 0.38, w: 0.11, h: 0.24, fill: { color: '9DB8FF' }, line: { color: '9DB8FF' }, objectName: 'arrow' });
T(s, '필요한 것', { x: 7.18, y: BY2 + 0.1, w: 2.2, h: 0.2, fontSize: 8.5, bold: true, color: 'FFD166' });
T(s, '요구를 계산할 수 있는 조건으로 바꾸고, 물리 계산으로 성능을 확인하며 설계하는 AI', { x: 7.18, y: BY2 + 0.32, w: 2.22, h: 0.42, fontSize: 8.5, bold: true, color: X.white });
T(s, '→ FormProof', { x: 7.18, y: BY2 + 0.74, w: 2.22, h: 0.2, fontSize: 10, bold: true, color: '7CE0B5' });
// v145 제거: T(s, [{ text: '※ 인용 문구는 대표 상황 예시, 그림은 본 과제 실제 결과(색
}
s.addNotes('[v3] 아래 띠 = ③의 근거: 데모와 같은 요청을 일반 LLM 세션 3개(도구 없음)에 입력, 3개 모두 흔들림 1.2~1.3배로 자체 예측(통과)했으나 같은 2 mm FEM 계산 결과 A 폰 온도 22.6 °C(기준 21), B 흔들림 2.95배, C 6.6배(기준 1.5)로 모두 불합격(2026-11-15). 필요한 것 = 요구를 계산 가능한 조건으로 바꾸고 물리 계산으로 확인하며 설계하는 AI. ※ 아래 외부 조사 수치(engineering.com 2022)는 원문 미확인 — 발표에서 말하지 않음. 문제 정의. 구상은 쉬우나 성능 확인 과정의 네 가지 병목에서 대부분 제품으로 이어지지 못함. ① 스케치의 3D 변환에 CAD 숙련 필요. ② 성능 계산에 하중 · 고정 · 기준 설정 필요, 전문가 의뢰 후 대기(참고: engineering.com 2022 조사, 외주 해석 67%가 1주 이상). ③ 범용 AI는 외형은 타당하나 성능 미달 — 본 과제에서 LLM 자체 예측 1.3배 흔들림이 실제 6.6배. ④ 결국 해석 없이 출력 · 수정 반복(같은 조사 45%가 일정상 해석 생략). 해결 방향: 입력에서 설계 사양과 3D 형상 생성(①②), 계산 기반 성능 해석 · 최적 설계(③), 제작 파일 출력(④). [화면에서 뺀 주석] ※ 인용 문구는 대표 상황 예시, 그림은 본 과제 실제 결과(색 = 같은 해석기로 계산한 흔들림). 남색 번호 = 병목, 파란 번호 = 해당 병목의 해결 단계');

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
s.addText('사용자가 원하는 성능과 조건을 근거 있는 수치로 바꾸고, AI가 물리 법칙에 맞게 설계한 뒤 최종 형상으로 다시 확인', { placeholder: 'body' });
{ const SS = [['입력', '말 · 스케치 · 문서 · 3D', ''], ['1 설계 사양', '', 'A'], ['2 3D 형상 생성', '', 'B'], ['3 성능 해석', '', 'B'], ['4 최적 설계', '', 'B'], ['5 검증 · 출력', '', 'C']];
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
T(s, [{ text: '입력 예', options: { bold: true, color: SL, breakLine: true } }, { text: '스케치 +\n', options: { fontSize: 6.8, color: C.text1 } }, { text: '"울퉁불퉁한 길에서도\n안 흔들리게,\n최대한 가볍게"', options: { fontSize: 7, bold: true, color: C.text2 } }], { x: x + 1.62, y: Y + 0.56, w: CW - 1.8, h: 1.04, fontSize: 7.5, valign: 'middle' });
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
T(s, 'AI 탐색: 반복마다 형상이 바뀌고 물리 AI가 성능 예측', { x: x + 0.15, y: Y + 1.63, w: CW - 0.3, h: 0.16, fontSize: 6.5, bold: true, color: BL, align: 'center' });
['e0', 'e20', 'e300', 'r120'].forEach((k, i) => { const fw = (CW - 0.3) / 4; fit(s, SH + 'v_fin_evo_' + k + '.png', x + 0.15 + i * fw, Y + 1.8, fw - 0.04, 0.5, 'evo ' + k);
  if (i < 3) s.addShape(pres.shapes.CHEVRON, { x: x + 0.15 + (i + 1) * fw - 0.06, y: Y + 2.0, w: 0.05, h: 0.08, fill: { color: BL }, line: { color: BL } }); });
dn(x + CW / 2, Y + 2.3, 0.05);
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.15, y: Y + 2.36, w: CW - 0.3, h: 0.46, rectRadius: 0.04, fill: { color: 'F5F7FB' }, line: { color: SL, width: 1 }, objectName: 'fem' });
T(s, [{ text: '정밀 최적화 — 시뮬레이션으로 계산하며 다듬기', options: { bold: true, color: SL, breakLine: true } }, { text: 'AI 후보 31개 정밀 확인 → 구조 최적화 120회 · 3D 프린트 조건', options: { fontSize: 6.3, color: C.text1 } }], { x: x + 0.22, y: Y + 2.36, w: CW - 0.44, h: 0.46, fontSize: 7.5, valign: 'middle' });
eff(x, '형상 생성 · 성능 예측 · 최적화를 미분으로 연결', BL);
// C
x = card(2, 'C', '자동 검증', SL);
[['v_fin_shape.png', '① 최종 형상', '16223A'], ['v_fin_fem.png', '② 처음부터 다시 시뮬레이션', '1E2A40']].forEach((p, k) => { const pw = (CW - 0.4) / 2, px = x + 0.15 + k * (pw + 0.1);
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: px, y: Y + 0.6, w: pw, h: 0.66, rectRadius: 0.04, fill: { color: p[2] }, line: { color: SL, width: 0.75 }, objectName: 'thumb' });
  fit(s, SH + p[0], px + 0.03, Y + 0.63, pw - 0.06, 0.6, p[1]);
  T(s, p[1], { x: px - 0.05, y: Y + 1.27, w: pw + 0.1, h: 0.15, fontSize: 6.8, bold: true, color: SL, align: 'center' });
  if (k < 1) s.addShape(pres.shapes.LINE, { x: px + pw + 0.01, y: Y + 0.93, w: 0.08, h: 0, line: { color: SL, width: 1, endArrowType: 'triangle' } }); });
dn(x + CW / 2, Y + 1.43, 0.08);
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.15, y: Y + 1.52, w: CW - 0.3, h: 0.72, rectRadius: 0.04, fill: { color: 'F5F7FB' }, line: { color: SL, width: 1 }, objectName: 'judge' });
s.addImage({ data: IC5.chk, x: x + 0.22, y: Y + 1.6, w: 0.18, h: 0.18 });
T(s, '③ 자동 판정', { x: x + 0.45, y: Y + 1.58, w: 2.2, h: 0.22, fontSize: 8, bold: true, color: SL, valign: 'middle' });
T(s, '최적화와 별도로 완성 형상을 다시 계산해\n진동 · 충격 · 열 · 휨을 기준과 비교', { x: x + 0.22, y: Y + 1.82, w: CW - 0.44, h: 0.38, fontSize: 7.2, color: C.text1, valign: 'middle' });
dn(x + 0.75, Y + 2.24, 0.1, BL);
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.15, y: Y + 2.34, w: 1.22, h: 0.42, rectRadius: 0.05, fill: { color: BL }, line: { color: BL }, objectName: 'pass' });
T(s, '합격 → 제품 출력', { x: x + 0.15, y: Y + 2.34, w: 1.22, h: 0.42, fontSize: 7.8, bold: true, color: X.white, align: 'center', valign: 'middle' });
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
s.addNotes('[v5] B와 C 모두 FEM을 쓰지만 역할이 다름: B는 계산하며 형상을 고치는 단계(후보 31개 확인 + 구조 최적화 120회), C는 완성된 형상을 최적화와 별도로 처음부터 다시 계산해 기준 통과 여부만 판정하는 확인 단계. [v4] C 자동 검증 = 최종 형상을 다시 정밀 시뮬레이션(FEM)해 진동 · 충격 · 열 · 휨을 기준과 비교, 합격만 출력(데모: 5/5). 동작 흐름과 핵심 기술을 한 장으로. 에이전트가 A 설계 사양 AI를 호출: LLM이 표현의 의미를 물리량으로 해석하고, 수치는 근거 DB(규격 · 실측 논문 · 데이터시트)에서만 가져와 항목별 출처를 붙인 JSON 설계 사양을 만든다. 근거가 없으면 사용자에게 묻는다. 설계 사양과 템플릿으로 만든 초기 설계가 B 최적 설계 AI의 출발점: 형상 AI(DeepSDF)가 형상을 잠재 변수로 표현하고, 물리 AI(신경 연산자, FNO · GINO)가 형상에서 응력 · 온도 분포를 즉시 예측해 기울기를 준다. 미분으로 후보를 찾고, 상위 후보만 SIMP + MMA 구조 최적화 + FEM으로 제조 제약을 지키며 정밀화. 계산 결과는 물리 AI 학습 데이터로 재활용. 최종 형상은 제작 형상 변환(CAD: 표면 정리 · 고정 부품 합치기 · 구멍 · 홈) 후 STL로 C 자동 검증에 전달: 재격자화 · FEM 재계산 · 기준 · 연결성 · 중간 밀도 판정. 불합격이면 미달 항목만큼 목표를 조여 B로 회귀, 합격이면 제작 파일 출력. 판정 결과 수치는 3. 구현 결과(성능 개선 쪽) 참고. 물리 AI는 현재 FNO로 구현, GINO는 메시 · STEP 입력용 확장. 탐색 결과 중 상위 후보만 FEM으로 정밀화.');

pres.addSection({ title: '3. 데모' });
// ---------- 데모 영상 (결선 데모 v27)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '3. 데모' });
T(s, '3. 구현 결과 · 데모', { x: 0.5, y: 0.08, w: 4, h: 0.22, fontSize: 9, bold: true, color: '1428A0', margin: 0 });
s.addText('아이디어 입력부터 검증된 제품 설계까지, 실제 GUI 동작', { placeholder: 'title' });
s.addText('자전거 폰 거치대 · AI 탐색과 정밀 최적화 구간은 미리 계산한 기록 재생', { placeholder: 'body' });
{ const w = 7.4, h = w * 9 / 16, x = (10 - w) / 2, y = 1.2;
  if (process.argv[3]) s.addMedia({ type: 'video', path: process.argv[3], cover: pic(SH + 'v_fin_vcover.png'), x, y, w, h, objectName: 'demo video' });
  else s.addImage({ data: pic(SH + 'v_fin_vcover.png'), x, y, w, h, objectName: 'demo video placeholder', altText: '데모 영상 자리 (영상 삽입)' }); }
s.addNotes('[약 1분 20초] 데모 영상 v31(음성판). 발표자가 직접 설명하려면 FormProof_결선데모_v31_자막.mp4 로 교체. 영상 수치: 초기 설계 5개 기준 중 4개 미달(흔들림 5.58배) → 최종 5개 모두 충족(흔들림 1.41배), 무게 94.9 → 80.1 g(−15.6 %). AI 탐색 300회 → 후보 31개 정밀 시뮬레이션 → 정밀 최적화 120회(3D 프린트 조건). 실물 출력물은 같은 조건 정밀 최적화로 얻은 같은 계열 구조.');
pres.addSection({ title: '4. DX 기여 · 확장' });
// ===== v167: DX 기여 — 설계 방식 변화 + 같은 흐름으로 다른 제품 (AI 글래스 실제 화면)
// ===== v181: 기대 효과 + 확대 계획 통합
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '4. DX 기여 · 확장' });
s.addText([{ text: '성능 판정을 ' }, { text: '며칠에서 1초 이내로', options: { color: '1428A0' } }, { text: ' 줄이고, ' }, { text: '사업부 제품과 특허까지', options: { color: '1428A0' } }, { text: ' 확장' }], { placeholder: 'title' });
T(s, '4. 기대 효과와 계획', { x: 0.5, y: 0.08, w: 4, h: 0.22, fontSize: 9, bold: true, color: '1428A0', margin: 0 });
s.addText('제품 설계에 그대로 적용하고, 특허 문서 속 구조도 직접 만들어 성능을 검증하고 비교', { placeholder: 'body' });
{
const BY = 1.2;
box(s, 0.5, BY, 9.0, 0.48, X.ink, 'hero');
T(s, [{ text: '성능 확인  ', options: { color: '9FB4EA', bold: true, fontSize: 10 } }, { text: '해석 의뢰 · 결과 대기 (며칠~몇 주)', options: { color: 'B8C2D6', fontSize: 10.5 } }, { text: '   →   ', options: { color: X.white, bold: true, fontSize: 12 } }, { text: '입력하면 1초 이내에 초기 설계와 성능 판정', options: { color: X.white, bold: true, fontSize: 12.5 } }, { text: '  (초기 설계 기준)', options: { color: 'B8C2D6', fontSize: 9 } }],
  { x: 0.7, y: BY, w: 8.6, h: 0.48, valign: 'middle' });
// 가운데: 두 갈래 확장 — ① 사업부 제품 (AI 글래스) · ② 특허 검증
const LY = 1.8, PH = 1.95, PW2 = 4.45, PX1 = 0.5, PX2 = 5.05;
const head = (x, tag, tagW, title, col) => {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.1, y: LY + 0.09, w: tagW, h: 0.22, rectRadius: 0.11, fill: { color: col }, line: { color: col } });
  T(s, tag, { x: x + 0.1, y: LY + 0.09, w: tagW, h: 0.22, fontSize: 7.5, bold: true, color: X.white, align: 'center', valign: 'middle' });
  T(s, title, { x: x + tagW + 0.18, y: LY + 0.06, w: PW2 - tagW - 0.26, h: 0.28, fontSize: 9.5, bold: true, color: C.text2, valign: 'middle' }); };
[[PX1, X.teal], [PX2, X.ink]].forEach(([x, col]) => { box(s, x, LY, PW2, PH, 'FFFFFF', 'ext');
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: LY, w: PW2, h: PH, rectRadius: 0.06, fill: { type: 'none' }, line: { color: col, width: 1.5 } }); });
// ① 사업부 제품
head(PX1, '사업부 제품', 0.86, '같은 흐름으로 어떤 제품이든 설계하고 판정', X.teal);
{ const ey = LY + 0.4, eh = 0.7;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: PX1 + 0.1, y: ey, w: PW2 - 0.2, h: eh, rectRadius: 0.04, fill: { color: 'F5F7FB' }, line: { color: 'DDE3F0', width: 0.5 }, objectName: 'glass ex' });
  fit(s, SH + 'v167_glass_3d.png', PX1 + 0.14, ey + 0.04, 0.95, eh - 0.08, 'glasses 3d');
  fit(s, SH + 'v167_glass_maps.png', PX1 + 1.12, ey + 0.04, 1.75, eh - 0.08, 'glasses fields');
  T(s, [{ text: '구현 예: MX AR 글래스', options: { bold: true, color: X.teal, breakLine: true } }, { text: '착용 무게 · 조이는 힘 · 코 받침 응력까지 설계와 판정', options: { fontSize: 6.8, color: C.text1 } }], { x: PX1 + 2.92, y: ey, w: PW2 - 3.06, h: eh, fontSize: 7.8, valign: 'middle' });
  const PRD = [[await icon(fa.FaMobileAlt, X.white), 'MX', '폴더블', '힌지 응력 · 낙하'], [await icon(md.MdWatch, X.white), 'MX', '웨어러블', '착용 무게 · 발열'],
    [await icon(fa.FaTv, X.white), 'VD', 'TV · 사이니지', '슬림 구조 · 진동'], [await icon(md.MdKitchen, X.white), 'DA', '가전', '소음 · 방열']];
  const pw = (PW2 - 0.2 - 3 * 0.08) / 4, py = LY + 1.18, ph = 0.68;
  PRD.forEach((p, i) => { const x = PX1 + 0.1 + i * (pw + 0.08);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: py, w: pw, h: ph, rectRadius: 0.05, fill: { color: 'EEF2FB' }, line: { color: 'C9D3EC', width: 0.75 }, objectName: 'product' });
    s.addShape(pres.shapes.OVAL, { x: x + 0.07, y: py + 0.08, w: 0.26, h: 0.26, fill: { color: X.teal }, line: { color: X.teal } });
    s.addImage({ data: p[0], x: x + 0.13, y: py + 0.14, w: 0.14, h: 0.14 });
    T(s, p[1], { x: x + 0.36, y: py + 0.08, w: pw - 0.4, h: 0.26, fontSize: 7, bold: true, color: X.teal, valign: 'middle' });
    T(s, [{ text: p[2], options: { bold: true, color: C.text2, breakLine: true } }, { text: p[3], options: { fontSize: 6.3, color: C.accent3 } }], { x: x + 0.07, y: py + 0.36, w: pw - 0.1, h: 0.3, fontSize: 7.8, valign: 'middle' }); }); }
// ② 특허
head(PX2, '특허', 0.5, '사내 특허 시스템과 연계해 특허 구조를 직접 만들어 검증', X.ink);
{ const ICP = [await icon(fa.FaFileAlt, X.white), await icon(fa.FaCube, X.white), await icon(fa.FaCogs, X.white), await icon(fa.FaBalanceScale, X.white)];
  const FS = [['사내 특허 시스템', '청구항 · 도면 불러오기'], ['3D 재현', '구조 · 치수 추출'], ['성능 계산', '진동 · 충격 · 열'], ['검증 · 비교', '효과 확인 · 성능 차이']];
  const bw = 0.98, gap = 0.1, fy = LY + 0.42;
  FS.forEach((f, i) => { const x = PX2 + 0.12 + i * (bw + gap);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: fy, w: bw, h: 0.62, rectRadius: 0.05, fill: { color: i === 3 ? '1428A0' : 'EEF2FB' }, line: { color: i === 3 ? '1428A0' : 'C9D3EC', width: 0.75 }, objectName: 'pflow' });
    s.addShape(pres.shapes.OVAL, { x: x + bw / 2 - 0.13, y: fy + 0.05, w: 0.26, h: 0.26, fill: { color: i === 3 ? '5B8DEF' : X.ink }, line: { color: i === 3 ? '5B8DEF' : X.ink } });
    s.addImage({ data: ICP[i], x: x + bw / 2 - 0.07, y: fy + 0.11, w: 0.14, h: 0.14 });
    T(s, [{ text: f[0], options: { bold: true, color: i === 3 ? X.white : C.text2, breakLine: true } }, { text: f[1], options: { fontSize: 6.3, color: i === 3 ? 'D9E1F5' : C.accent3 } }], { x: x + 0.02, y: fy + 0.31, w: bw - 0.04, h: 0.3, fontSize: 7.6, align: 'center', valign: 'middle' });
    if (i < 3) s.addShape(pres.shapes.CHEVRON, { x: x + bw + 0.015, y: fy + 0.25, w: 0.07, h: 0.12, fill: { color: X.ink }, line: { color: X.ink } }); });
  const US = [['타사 선행 특허', '문서에 적힌 효과가 실제 계산에서도 나오는지 검증'], ['우리 출원', '선행 특허보다 얼마나 나은지 수치로 보여 근거 강화'], ['회피 설계', '청구 범위 밖 구조를 여러 개 만들고 성능 비교']];
  US.forEach((u, i) => { const y = LY + 1.13 + i * 0.26;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: PX2 + 0.12, y: y + 0.03, w: 0.95, h: 0.19, rectRadius: 0.09, fill: { color: X.ink }, line: { color: X.ink } });
    T(s, u[0], { x: PX2 + 0.12, y: y + 0.03, w: 0.95, h: 0.19, fontSize: 6.8, bold: true, color: X.white, align: 'center', valign: 'middle' });
    T(s, u[1], { x: PX2 + 1.14, y, w: PW2 - 1.24, h: 0.25, fontSize: 7.6, color: C.text2, valign: 'middle' }); }); }
// 아래: 로드맵 (1단계 완료 · 2단계 진행 중 · 3 · 4단계 계획)
const SX = 0.5, W = 9.0 / 4, HY = 4.1, CY = 4.49, CH = 0.62;
[[SX, 2 * W, '해커톤 구현 범위 (완료)', '1428A0', 'solid'], [SX + 2 * W, 2 * W, '이후 확대 (계획)', '8A949C', 'dash']].forEach(([x, w, t, col, d]) => {
  s.addShape(pres.shapes.LINE, { x: x + 0.04, y: 4.05, w: w - 0.08, h: 0, line: { color: col, width: 1.5, dashType: d } });
  T(s, t, { x, y: 3.86, w, h: 0.17, fontSize: 7.5, bold: true, color: col === '8A949C' ? C.accent3 : col, align: 'center' }); });
const ST = [['1단계', '엔진 · 검증 · 사례 구현', '1428A0', '자전거 폰 거치대\n아이디어 입력 → 검증된 제품', 'done'], ['2단계', 'AI 엔진 학습', '1428A0', '형상 AI · 물리 AI 학습 · 탐색\nGUI 한 화면으로 연결', 'done'],
  ['3단계', '특허 시스템 연계', '6F86D6', '사내 특허 시스템 연계\n특허 구조 3D 재현 → 효과 검증', ''], ['4단계', '사업부 적용', '0F1B3D', 'MX AR 글래스 · 폴더블 시범\nVD TV · DA 가전, 물리 모듈 확대', '']];
ST.forEach((p, i) => { const x = SX + i * W, done = p[4] === 'done', wip = p[4] === 'wip';
  s.addShape(i ? pres.shapes.CHEVRON : pres.shapes.PENTAGON, { x, y: HY, w: W + 0.1, h: 0.34, fill: { color: p[2] }, line: { color: X.white, width: 1 }, objectName: 'stage' });
  T(s, [{ text: p[0] + '  ', options: { color: 'D9E1F5', fontSize: 7 } }, { text: p[1], options: { bold: true, color: X.white } }], { x: x + (i ? 0.26 : 0.1), y: HY, w: W - 0.25, h: 0.34, fontSize: 8.5, valign: 'middle' });
  box(s, x + 0.03, CY, W - 0.06, CH, done ? 'EEF2FB' : X.tint, 'cell');
  if (done || wip) s.addShape(pres.shapes.RECTANGLE, { x: x + 0.03, y: CY, w: 0.05, h: CH, fill: { color: p[2] }, line: { color: p[2] } });
  T(s, (done ? [{ text: '✓ ', options: { bold: true, color: '1428A0' } }] : []).concat([{ text: p[3], options: { color: done ? C.text2 : C.text1, bold: done } }]), { x: x + 0.15, y: CY, w: W - 0.24, h: CH, fontSize: 7.8, valign: 'middle' }); });
}
s.addNotes('기대 효과와 확대 계획을 한 장으로. 기여 대상은 방법론: 성능 확인을 해석 의뢰 · 결과 대기에서 입력 즉시 판정으로. 몇 초 근거: GUI 파이프라인(말 → 설계 사양 → 템플릿 초기 설계 → 약 1,600 요소 FEM 고유진동 · 흔들림 판정)이 클라우드 환경에서 1초 이내(2026-11-17 측정, 0.6~0.8 s). 최적 설계는 별도 계산 시간 필요. 설계 방식 변화: 설계 초기에 설계자가 직접 성능 확인, 반복 설계와 제작 전 확인 자동화. 특허 확장: 특허 문서(청구항 · 도면)에서 구조 · 치수 · 효과 주장을 설계 사양으로 추출해 3D로 재현하고, 같은 하중 · 같은 기준 · 같은 FEM으로 계산해 검증 · 비교(같은 조건 = 같은 하중 · 같은 합격 기준 · 같은 해석기와 격자). 활용: 타사 선행 특허의 효과 주장 검증, 우리 출원의 선행 특허 대비 우위 수치화(출원 근거), 회피 설계 성능 비교, 포트폴리오 평가. 한계: 도면에 없는 치수 · 재료는 가정으로 표시하며 결과는 같은 조건 상대 비교. 침해 · 무효 등 법적 판단은 하지 않음. 현재 텍스트 · 스케치 입력까지 구현, 특허 문서 해석 · 사내 특허 시스템 연동은 3단계 계획. 제품 확장 예: MX AR 글래스 — 착용 무게 · 조이는 힘 · 코 받침 응력을 설계 사양으로 정의해 같은 흐름으로 초기 설계와 판정 구현. 로드맵: 1 · 2단계는 해커톤 구현 범위(완료) — 설계 사양 AI(LLM + 근거 DB), FEM 엔진 · 자동 판정, 자전거 폰 거치대 사례와 제작 파일, 같은 사례의 형상 AI(DeepSDF) · 물리 AI(GINO · FNO) 학습과 탐색, GUI. 3단계 입력 · 연동 확대: 문서 · 사진 · STEP 입력, 사내 특허 시스템 연동(특허 문서 → 3D 재현 → 같은 조건 비교, 법적 판단 아님), 실물 출력 · 실측 비교, 제품별 템플릿 · 근거 DB 확대, AI 예측 정확도 · 탐색 시간 검증, 제작성 검사 고도화. 4단계 사업부 적용: MX AR 글래스 · 폴더블 시범 후 기존 설계 절차와 비교, VD TV · DA 가전, 물리 모듈 확장(낙하 · 피로 · 소음 · 전자기), 사내 설계 도구 · CAD 연계와 데이터 누적. 정량 효과(해석 의뢰 기간, 시제품 반복 횟수)는 담당자 확인 필요.');


await pres.writeFile({ fileName: OUT });
await applyTheme(OUT, THEME);
console.log('ok', OUT);
})();