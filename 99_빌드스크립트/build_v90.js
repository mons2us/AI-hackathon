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
s.addText([{ text: '아이디어를 바로 제품으로\n성능은 계산으로 증명', options: { breakLine: true } }, { text: ' ', options: { fontSize: 6, breakLine: true } }, { text: '입력 형태 무관 — 말 · 스케치 · 문서 · 이미지 · 3D 파일', options: { fontSize: 11, color: 'B8C7C9' } }], { placeholder: 'body' });
T(s, '물리 기반 생성형 AI  ·  팀원 A · B · C', { x: 0.6, y: 4.6, w: 5, h: 0.3, fontSize: 11, color: C.accent4 });
box(s, 5.9, 0.9, 3.7, 3.8, 'FFFFFF', 'hero card');
fit(s, SH + 'v17_hero.png', 6.0, 1.0, 3.5, 2.75, 'optimized phone mount on bicycle');
T(s, '자전거 폰 거치대 — FormProof가 설계한 일체형', { x: 6.05, y: 3.85, w: 3.4, h: 0.3, fontSize: 11, bold: true, color: C.text2, align: 'center' });
T(s, '최대 흔들림 5.6배 → 1.3배 · 몸체 81.3 g', { x: 6.05, y: 4.15, w: 3.4, h: 0.3, fontSize: 10, color: C.accent1, align: 'center' });
s.addNotes('FormProof = Form + Proof, 형상을 성능으로 증명. 오른쪽: 계산으로 도출한 일체형 거치대(출력용 STL, 폰 4면 고정).');

pres.addSection({ title: '요약' });
// ---------- 2. 한 장 요약 (v31: 흐름(위) → 증거 + DX(아래))
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '요약' });
s.addText('아이디어를 바로 제품으로 — 성능은 계산으로 증명', { placeholder: 'title' });
s.addText('요구 입력 → 물리 조건 → 3D 형상 · 해석 · 재설계 → 제작 파일, 전 과정 AI 수행', { placeholder: 'body' });
// ① 흐름 + 핵심 기술
const FY = 1.2;
box(s, 0.5, FY, 9.0, 1.05, X.tint, 'flow');
const FLW = [['v17_sketch.png', 0.92, '요구 정의', '말 · 스케치 · 문서\n이미지 · STEP'], ['v32_spec.png', 0.92, '설계 명세', '물리 조건 · 기준\n항목별 출처'], ['v79_evo.png', 1.85, '3D 형상', '해석하며 재설계\n(재료 배치 반복)'], ['v25_asm.png', 0.92, '제작 파일', '조립도 · STL\n설명서']];
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
T(s, '대표 사례 — 자전거 폰 거치대 (이 사례의 입력: 말 + 스케치)', { x: 0.62, y: PY + 0.05, w: 5.8, h: 0.24, fontSize: 10, bold: true, color: C.accent1 });
[['처음 설계 (판 + 기둥)', 'v28_Rbase.png', C.accent5, 0.6], ['FormProof 재설계 (출력 몸체)', 'v51_Rbody.png', C.accent1, 3.08]].forEach(c => {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: c[3], y: PY + 0.33, w: 2.4, h: 1.2, rectRadius: 0.05, fill: { color: 'FFFFFF' }, line: { color: X.line, width: 0.5 }, objectName: 'pair' });
  fit(s, SH + c[1], c[3] + 0.03, PY + 0.35, 2.34, 1.16, c[0]);
  T(s, c[0], { x: c[3], y: PY + 1.55, w: 2.4, h: 0.2, fontSize: 9, bold: true, color: c[2], align: 'center' }); });
s.addImage({ path: SH + 'v30_cb.png', x: 5.55, y: PY + 0.31, w: 0.62, h: 1.24, objectName: 'legend' });
T(s, '두 설계 같은 척도', { x: 5.5, y: PY + 1.58, w: 0.95, h: 0.3, fontSize: 6.3, color: C.accent3 });
const KP = [['폰 흔들림', '77% 감소', '울퉁불퉁한 길 · 5.6 → 1.3배'], ['충격 부담', '80% 감소', '내부 응력 14.7 → 2.9 MPa'], ['폰 온도', '12 °C 저감', '내비게이션 사용 시 32.6 → 20.8 °C'], ['무게', '84 → 81 g', '출력 몸체 84.0 → 81.3 g'], ['범용 LLM 단독 3회', '3/3 불합격', '공진 2 · 온도 초과 1']];
KP.forEach((k, i) => { const x = 0.6 + i * 1.17, y = PY + 1.82, bad = i === 4;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 1.1, h: 0.66, rectRadius: 0.06, fill: { color: bad ? 'FBECEA' : 'FFFFFF' }, line: { color: bad ? X.red : X.teal, width: 1 }, objectName: 'kpi card' });
  T(s, k[0], { x: x + 0.07, y: y + 0.04, w: 1.0, h: 0.17, fontSize: 7, bold: true, color: bad ? C.accent5 : C.text2, valign: 'middle' });
  T(s, k[1], { x: x + 0.07, y: y + 0.21, w: 1.0, h: 0.25, fontSize: 12, bold: true, color: bad ? C.accent5 : C.accent1, valign: 'middle' });
  T(s, k[2], { x: x + 0.07, y: y + 0.46, w: 1.02, h: 0.17, fontSize: 5.6, color: C.accent3, valign: 'middle' }); });
// ③ DX 제품 경쟁력 — 같은 방법론(입력 → 형상 → 물리 판정 → 제작 파일)을 제품에
box(s, 6.65, PY, 2.85, 2.6, X.ink, 'dx panel');
T(s, 'DX 제품 경쟁력 적용', { x: 6.78, y: PY + 0.07, w: 2.6, h: 0.26, fontSize: 11, bold: true, color: C.background1 });
T(s, '설계 요구 입력만으로 검증된 개선안 도출', { x: 6.78, y: PY + 0.33, w: 2.62, h: 0.2, fontSize: 7, color: C.accent4 });
const DX = [
  ['VD', 'TV 스탠드 · 벽걸이', '외형 유지 · 경량화', '실증: 다리 무게 −69%', true],
  ['MX', '폰 · 폴더블 내부 브래킷', '박형화 · 열 확산', '구조 · 열 + 낙하', false],
  ['DA', '세탁기 · 에어컨 모터 마운트', '진동 · 소음 저감', '진동 + 음향', false],
  ['공통', '기존 부품 STEP 입력', '같은 성능 · 재료 절감', '형상 유지 경량화', false]];
DX.forEach((d, i) => { const y = PY + 0.6 + i * 0.44;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.76, y: y + 0.03, w: 0.46, h: 0.22, rectRadius: 0.11, fill: { color: X.teal }, line: { color: X.teal }, objectName: 'dx tag' });
  T(s, d[0], { x: 6.76, y: y + 0.03, w: 0.46, h: 0.22, fontSize: 7.5, bold: true, color: C.background1, align: 'center', valign: 'middle' });
  T(s, d[1], { x: 7.28, y, w: 2.15, h: 0.2, fontSize: 8, bold: true, color: C.background1 });
  T(s, [{ text: d[2], options: { color: 'D5E4E6' } }, { text: '   ' + d[3], options: { color: d[4] ? '7FD3D0' : 'F2C27B', bold: true } }], { x: 7.28, y: y + 0.2, w: 2.18, h: 0.18, fontSize: 6.3 }); });
T(s, '물리는 제품별 모듈 추가, 전체 흐름 동일', { x: 6.78, y: PY + 2.38, w: 2.65, h: 0.18, fontSize: 6, color: 'A9B8BC' });
T(s, '※ 처음 설계 대비 같은 조건 해석(폰 + 고정 부품 311 g, 감쇠비 3%, 35°, 발열 4 W, 길 진동 10–100 Hz). DX 항목은 적용 후보, 효과는 사업부 확인 필요', { x: 0.5, y: 5.05, w: 9, h: 0.18, fontSize: 6.5, color: C.accent3 });
s.addNotes('한 장 요약. 상단: 입력 형태 무관(말 · 스케치 · 문서 · 이미지 · STEP) → 생성 AI의 출처 기반 설계 조건 작성 → 형상 AI · 물리 AI · 수치해석으로 계산 · 재설계 → 조립도 · STL · 설명서 출력. 좌하단: 동일 요청의 처음 설계와 AI 재설계를 동일 색 척도로 비교. 처음 설계는 판 끝 최대 3.5배 흔들림, AI 재설계는 1.2배 이하. 핵심 수치: 최대 흔들림, 충격 응력, 폰 온도, 무게. 우측: 동일 엔진의 DX 제품 적용 후보.');

pres.addSection({ title: '1. 문제 정의' });
// ---------- 3. 문제 정의 (v50: 공감 + 시각화 — 떠오른다 → 막힌다 → 서랍 속으로 / 이게 된다면)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '1. 문제 정의' });
s.addText('1. 문제 정의 — 아이디어는 많으나, 성능 검증 단계에서 중단', { placeholder: 'title' });
s.addText('구상은 누구나 가능하나, "실제로 성립하는지" 확인하는 과정의 네 가지 장벽에서 대부분 중단', { placeholder: 'body' });
{
const AM = 'B07A1E';
const I4 = { bike: await icon(fa.FaBicycle, X.white), bulb: await icon(fa.FaLightbulb, X.white), pen: await icon(fa.FaPencilRuler, X.white),
  clock: await icon(fa.FaHourglassHalf, X.red), redo: await icon(fa.FaRedoAlt, X.red), x: await icon(fa.FaTimesCircle, X.red),
  arch: await icon(fa.FaArchive, '8A949C'), bulbG: await icon(fa.FaLightbulb, 'C9CED2'), bulbY: await icon(fa.FaLightbulb, X.amber) };
const Y0 = 1.22, HH = 2.56;
const tag = (x, y, t, c) => { box(s, x, y, 0.95, 0.24, c, 'tag'); T(s, t, { x, y, w: 0.95, h: 0.24, fontSize: 8, bold: true, color: X.white, align: 'center', valign: 'middle' }); };
// A. 떠오른다: 손 스케치 + 한마디
box(s, 0.5, Y0, 2.5, HH, 'FDF6EA', 'idea');
tag(0.62, Y0 + 0.1, '구상', X.amber);
s.addImage({ data: I4.bulbY, x: 2.62, y: Y0 + 0.08, w: 0.26, h: 0.26 });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.62, y: Y0 + 0.42, w: 2.26, h: 1.08, rectRadius: 0.04, fill: { color: 'FFFFFF' }, line: { color: 'F0D9AE', width: 0.5 }, objectName: 'sketch' });
fit(s, SH + 'v17_sketch.png', 0.64, Y0 + 0.44, 2.22, 1.04, '손 스케치');
[[I4.bike, '폰이 떨려 지도가 안 보여. 만들어 볼까?'], [I4.bulb, '더 튼튼할 텐데, 증명할 방법이 없네'], [I4.pen, '더 얇게 하고 싶은데, 이 두께로 버틸까?']].forEach((q, i) => { const y = Y0 + 1.58 + i * 0.32;
  s.addShape(pres.shapes.OVAL, { x: 0.62, y: y + 0.02, w: 0.24, h: 0.24, fill: { color: X.amber }, line: { color: X.amber }, objectName: 'p' });
  s.addImage({ data: q[0], x: 0.67, y: y + 0.07, w: 0.14, h: 0.14 });
  T(s, '"' + q[1] + '"', { x: 0.92, y, w: 2.0, h: 0.28, fontSize: 7.5, italic: true, color: C.text2, valign: 'middle' }); });
// B. 그런데 현실은: 4개의 벽 (내려가는 계단)
T(s, '현실의 장벽', { x: 3.15, y: Y0 + 0.06, w: 2, h: 0.26, fontSize: 10.5, bold: true, color: C.accent5 });
const WL = [
  { img: 'v47_cad.png', q: '3D 모델링', h: 'CAD 숙련 필요', e: '스케치 단계에서 중단' },
  { img: 'v48_base.png', tags: true, q: '성능 확인', h: '해석 조건 설정 난해', big: '67%', ref: '1', e: '해석 의뢰 시 1주 이상 대기' },
  { img: 'v44_llm.png', q: 'AI 활용', h: '외형은 타당, 성능은 미달', big: '6.6배', ref: '2', e: '흔들림 (AI 예측 1.3배)' },
  { prints: true, q: '시행착오 제작', h: '출력 · 수정 반복', big: '45%', ref: '1', e: '일정상 해석 생략' }];
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
T(s, '아이디어\n사장(死藏)', { x: DX + 0.12, y: Y0 + 2.0, w: 9.5 - DX - 0.12, h: 0.46, fontSize: 9, bold: true, color: C.accent3, align: 'center', valign: 'middle' });
// D. 이게 해결된다면: 벽 ①~④에 하나씩 답 (형상 + 조건 → 물리 → 제작 파일)
const BY2 = 3.86, BH2 = 1.0;
box(s, 0.5, BY2, 9.0, BH2, X.ink, 'wish');
T(s, '해결 방향', { x: 0.64, y: BY2 + 0.1, w: 1.6, h: 0.26, fontSize: 10.5, bold: true, color: X.amber });
T(s, '특허 아이디어는 계산된 성능 근거로, 제품 아이디어는 대기 없이 검증', { x: 0.64, y: BY2 + 0.4, w: 1.5, h: 0.52, fontSize: 7.5, color: C.accent4, valign: 'top' });
const ST = [['v17_sketch.png', '요구 (형태 무관)', [], '말 · 스케치 · 문서 · STEP'], ['v49_base.png', '형상 + 물리 조건 생성', ['①', '②'], 'CAD · 조건 설정 불필요'],
  ['v51_ai.png', '물리 검증 · 재설계', ['③'], '기준 통과까지 계산 · 재설계'], ['v47_use.png', '제작 파일로 출력', ['④'], '도면 · STL · 설명서']];
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
  { text: '2', options: { superscript: true } }, { text: ' 범용 LLM 단독 독립 3회, 같은 해석기로 판정', options: { breakLine: true } },
  { text: '※ 인용 문구는 대표 상황 예시. 그림은 본 과제 실제 결과(스케치 · 처음 설계 · LLM 형상 · AI 설계 · 최종 설계, 색 = 같은 해석기로 계산한 흔들림). 초록 번호 = 각 장벽의 해결 단계' }], { x: 0.5, y: 4.92, w: 9, h: 0.3, fontSize: 6.5, color: C.accent3 });
}
s.addNotes('문제 정의. 구상은 쉬우나 성능 확인 과정의 네 가지 장벽에서 대부분 중단. ① 스케치의 3D 변환에 CAD 숙련 필요. ② 성능 계산에 하중 · 고정 · 기준 설정 필요, 해석 의뢰 시 67%가 1주 이상 대기. ③ 범용 AI 활용 시 외형은 타당하나 성능 미달 — 자체 예측 1.3배 흔들림이 실제 6.6배. ④ 결과적으로 45%는 해석 없이 출력 · 수정 반복. 해결 방향: 요구 입력에서 형상과 물리 조건 동시 생성(①②), 계산 기반 검증 · 재설계(③), 제작 파일 출력(④).');

pres.addSection({ title: '2. 기술 차별성' });
// ---------- 4. 기술 차별성: 단계 지도 (v64: 누가 · 얼마나 어렵게 하나)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 기술 차별성 — 난도 높은 단계는 여전히 전문가 의존', { placeholder: 'title' });
s.addText('기존 기술은 일부 단계만 자동화, 나머지는 전문가 수작업 — FormProof는 6단계 전체를 AI로 연결', { placeholder: 'body' });
{
const UI = { user: await icon(fa.FaUser, 'B8C0C6'), pro: await icon(fa.FaUserTie, X.white), ai: await icon(fa.FaRobot, X.white) };
// [단계, 사람이 할 때 필요한 일, 난이도(1–3), 3쪽 벽]
const STP = [['요구 정의', '목표 · 제약을 수치로 정리', 2, ''], ['3D 형상 생성', 'CAD 모델링 · 설계', 2, '①'], ['물리 조건', '하중 · 경계조건 설정', 3, '②'],
  ['성능 해석', '시뮬레이션 (메쉬 · 해석)', 3, '③'], ['재설계', '최적화 + CAD 재구성 · 반복', 3, ''], ['제작 파일', '도면 · 출력 형상 재검증', 2, '④']];
// 1 = 도구가 자동, 3 = 전문가 수작업 필요, 4 = 추측(검증 없음), 0 = 지원 안 함 → 사람이 메움
const RW = [
  ['범용 LLM 단독', '대화형 생성 AI', [1, 1, 4, 4, 4, 4], '계산 없는 추정 — 동일 조건 3회 모두 불합격²'],
  ['3D 생성 AI', '텍스트 · 이미지 → 3D', [0, 1, 0, 0, 0, 0], '형상 생성만 — 이후 단계 수작업'],
  ['물리 AI', '목표 → 최적 설계 (역설계)', [0, 0, 0, 1, 1, 0], '사람이 정한 설계 틀 · 조건 내에서만 최적화'],
  ['해석 · 최적화 도구', '전문가용 CAE', [0, 3, 3, 1, 3, 3], '계산만 자동 — 결과 확보 1주 이상 67%¹'],
  ['FormProof', '요구부터 제작 파일까지', [1, 1, 1, 1, 1, 1], '형상 AI + 물리 AI + 수치해석']];
const LX = 0.5, LW = 1.7, SX = 2.3, CWs = 0.86, RX = SX + 6 * CWs + 0.12, RWd = 9.5 - RX, HY = 1.22, RY0 = 2.02, RH = 0.46, RG = 0.07;
STP.forEach((st, i) => { const x = SX + i * CWs;
  s.addShape(pres.shapes.CHEVRON, { x: x + 0.01, y: HY, w: CWs - 0.02, h: 0.3, fill: { color: X.ink }, line: { color: X.ink }, objectName: 'step' });
  T(s, st[0], { x: x + 0.1, y: HY, w: CWs - 0.2, h: 0.3, fontSize: st[0].length > 5 ? 6.8 : 7.5, bold: true, color: X.white, align: 'center', valign: 'middle' });
  T(s, st[1], { x: x + 0.02, y: HY + 0.33, w: CWs - 0.04, h: 0.26, fontSize: 6, color: C.text1, align: 'center' });
  T(s, '●'.repeat(st[2]) + '○'.repeat(3 - st[2]), { x, y: HY + 0.56, w: CWs, h: 0.18, fontSize: 9, color: st[2] === 3 ? X.red : X.amber, align: 'center' });
  if (st[3]) { s.addShape(pres.shapes.OVAL, { x: x + CWs - 0.2, y: HY - 0.1, w: 0.18, h: 0.18, fill: { color: X.red }, line: { color: X.white, width: 0.75 }, objectName: 'wall no' });
    T(s, st[3], { x: x + CWs - 0.2, y: HY - 0.1, w: 0.18, h: 0.18, fontSize: 6.5, bold: true, color: X.white, align: 'center', valign: 'middle' }); } });
T(s, '수작업 시\n필요 작업 · 난이도', { x: LX, y: HY + 0.3, w: LW, h: 0.44, fontSize: 7, color: C.accent3, valign: 'middle' });
T(s, '한계', { x: RX, y: HY + 0.04, w: RWd, h: 0.24, fontSize: 9, bold: true, color: C.accent3 });
const cell = (st, x, y, w, h, fp, pg) => { if (st === 0) st = 3;   // 사람이 하는 칸은 하나로
  if (st === 1) { const c = fp ? X.teal : '7C8B96';
    s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: c }, line: { color: c }, objectName: 'auto' });
    if (fp) { s.addImage({ data: UI.ai, x: pg ? x + 0.1 : x + w / 2 - 0.08, y: y + h / 2 - 0.08, w: 0.16, h: 0.16 });
      if (pg) T(s, pg, { x: x + 0.3, y, w: w - 0.34, h, fontSize: 7.5, bold: true, color: X.white, valign: 'middle' }); } }
  else if (st === 3) { s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: X.amber }, line: { color: X.amber }, objectName: 'expert' });
    s.addImage({ data: UI.pro, x: x + w / 2 - 0.08, y: y + h / 2 - 0.08, w: 0.16, h: 0.16 }); }
  else if (st === 6 || st === 7) { s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: X.amber }, line: { color: X.amber }, objectName: 'expert text' });
    T(s, st === 6 ? '형상 틀은\n사람이' : '학습 때\n고정', { x, y, w, h, fontSize: 6.5, bold: true, color: X.white, align: 'center', valign: 'middle' }); }
  else if (st === 5) { s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: 'F8E3BF' }, line: { color: X.amber, width: 0.75, dashType: 'dash' }, objectName: 'setup' });
    if (w > 0.4) T(s, '구축 때', { x, y, w, h, fontSize: 7, bold: true, color: 'B07A1E', align: 'center', valign: 'middle' }); }
  else if (st === 4) { s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: 'FBF1EF' }, line: { color: X.red, width: 0.75, dashType: 'dash' }, objectName: 'guess' });
    T(s, '추측', { x, y, w, h, fontSize: 7, bold: true, color: X.red, align: 'center', valign: 'middle' }); }
  else { s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: 'FFFFFF' }, line: { color: 'D9DEE2', width: 0.75, dashType: 'dash' }, objectName: 'gap' });
    s.addImage({ data: UI.user, x: x + w / 2 - 0.07, y: y + h / 2 - 0.07, w: 0.14, h: 0.14 }); } };
RW.forEach((r, ri) => { const y = RY0 + ri * (RH + RG), fp = ri === 4;
  if (fp) box(s, LX - 0.08, y - 0.05, 9.08, RH + 0.1, 'E3F0EF', 'fp row');
  T(s, r[0], { x: LX, y: y + 0.01, w: LW, h: 0.24, fontSize: 9.5, bold: true, color: fp ? C.accent1 : C.text2 });
  T(s, r[1], { x: LX, y: y + 0.25, w: LW, h: 0.18, fontSize: 7, color: C.accent3 });
  const PG = [null, null, null, null, null, null];
  r[2].forEach((m, i) => cell(m, SX + i * CWs + 0.03, y + 0.06, CWs - 0.06, RH - 0.12, fp, fp ? PG[i] : null));
  const nH = r[2].filter(m => m === 0 || m === 3).length, nG = r[2].filter(m => m === 4).length;
  const tg = fp ? ['AI 6 / 6', X.teal] : nG ? ['추측 ' + nG, X.red] : ['사람 ' + nH, X.amber];
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: RX, y: y + RH / 2 - 0.12, w: 0.62, h: 0.24, rectRadius: 0.12, fill: { color: tg[1] }, line: { color: tg[1] }, objectName: 'tally' });
  T(s, tg[0], { x: RX, y: y + RH / 2 - 0.12, w: 0.62, h: 0.24, fontSize: 7.5, bold: true, color: X.white, align: 'center', valign: 'middle' });
  T(s, r[3], { x: RX + 0.68, y, w: RWd - 0.68, h: RH, fontSize: 7, bold: fp, color: fp ? C.accent1 : C.text1, valign: 'middle' }); });
// 범례
const LG = 4.7;
[[1, '도구 · AI 자동'], [3, '전문가 수행 필요'], [4, '추측 (검증 없음)']].forEach((g, i) => { const x = SX + i * 1.75;
  cell(g[0], x, LG, 0.3, 0.16, false); T(s, g[1], { x: x + 0.36, y: LG - 0.01, w: 1.35, h: 0.18, fontSize: 6.5, color: C.accent3, valign: 'middle' }); });
T(s, '빨간 번호 = 문제 정의의 벽 ①~④', { x: 7.6, y: LG - 0.01, w: 1.9, h: 0.18, fontSize: 6.5, color: C.accent3, align: 'right', valign: 'middle' });
T(s, [{ text: '1', options: { superscript: true } }, { text: ' engineering.com · Dassault 2022 설문   ' }, { text: '2', options: { superscript: true } }, { text: ' 같은 조건 독립 3회, 같은 해석기로 판정.  난이도 = 사람이 직접 할 때 필요한 전문성(팀 판단). 비교는 범주별 일반 기능 기준' }],
  { x: 0.5, y: 4.92, w: 9, h: 0.3, fontSize: 6.5, color: C.accent3 });
}
s.addNotes('요구 정의 = 문제와 요구를 목표 · 제약 수치로 정리. 성능 해석 = 시뮬레이션. 최고 난도 단계: 물리 조건 설정, 해석, 재설계(최적화 결과의 CAD 재구성 및 반복). 해석 도구는 계산만 자동이며 전후 단계(모델링, 조건, 재설계, 재검증)는 전문가 수행. FormProof는 6단계 전체를 AI로 수행.');

// ---------- 5. 기술 차별성: 파이프라인
// ===== v7: 프레임워크 아키텍처
const IC2 = {
  robot: await icon(fa.FaRobot, X.white), shape: await icon(fa.FaDraftingCompass, X.teal), atom: await icon(fa.FaAtom, X.teal),
  opt: await icon(fa.FaChartLine, X.teal), ver: await icon(fa.FaClipboardCheck, X.teal), stl: await icon(fa.FaCube, X.teal),
  drw: await icon(fa.FaRulerCombined, X.teal), rep: await icon(fa.FaFileAlt, X.teal), img: await icon(fa.FaImage, X.teal),
  book: await icon(fa.FaBook, X.amber), x: await icon(fa.FaTimesCircle, X.red), ok: await icon(fa.FaCheckCircle, X.green),
};
// ===== v77: 프레임워크 — 모듈 · 데이터 흐름 · 반복 고리 + 모듈별 작은 그림
const GEN = '6B4FA0';   // 생성 AI 색 (뒤 장에서도 사용)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. FormProof 프레임워크 — 모듈 · 데이터 연결 구조와 재설계 순환', { placeholder: 'title' });
s.addText('에이전트의 모듈 호출 → 모듈 출력의 다음 모듈 입력 연계 → 검증 불합격 시 재설계 회귀', { placeholder: 'body' });
{
const PHY = X.teal, NUM = '5B6B78', CTL = 'B07A1E';
// 그림이 위, 글이 아래인 노드
const node = (x, y, w, h, title, sub, col, o = {}) => {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.06, fill: { color: o.fill || 'FFFFFF' }, line: { color: col, width: 1.25 }, objectName: 'node' });
  let ty = y, th = h;
  if (o.img) { const ih = o.ih || 0.5; fit(s, SH + o.img, x + 0.06, y + 0.06, w - 0.12, ih, title); ty = y + ih + 0.06; th = h - ih - 0.06; }
  if (o.no) { s.addShape(pres.shapes.OVAL, { x: x - 0.1, y: y - 0.1, w: 0.26, h: 0.26, fill: { color: X.red }, line: { color: X.white, width: 1 }, objectName: 'core' });
    T(s, o.no, { x: x - 0.1, y: y - 0.1, w: 0.26, h: 0.26, fontSize: 8.5, bold: true, color: X.white, align: 'center', valign: 'middle' }); }
  T(s, [{ text: title, options: { bold: true, color: o.tc || C.text2, breakLine: true } }, { text: sub, options: { fontSize: 6.5, color: o.sc || C.text1 } }], { x: x + 0.06, y: ty, w: w - 0.12, h: th, fontSize: 8.5, align: 'center', valign: 'middle' }); };
const ln = (x1, y1, x2, y2, o = {}) => s.addShape(pres.shapes.LINE, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1) || 0.001, h: Math.abs(y2 - y1) || 0.001,
  flipH: x2 < x1, flipV: y2 < y1, line: { color: o.c || '6B7780', width: o.w || 1.25, dashType: o.d || 'solid', endArrowType: o.noArrow ? undefined : 'triangle' }, objectName: 'edge' });
const lab = (t, x, y, w, o = {}) => T(s, t, { x, y, w, h: o.h || 0.16, fontSize: o.fs || 6.3, bold: !!o.b, color: o.c || C.accent3, align: o.al || 'center', valign: 'middle' });
// 에이전트
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 1.75, y: 1.15, w: 6.5, h: 0.34, rectRadius: 0.06, fill: { color: X.ink }, line: { color: X.ink }, objectName: 'agent' });
T(s, [{ text: 'LLM 에이전트   ', options: { bold: true, color: X.amber } }, { text: '계획 → 모듈 호출 → 결과 · 기준 대조 → 다음 호출 · 재설계 지시', options: { color: X.white } }], { x: 1.85, y: 1.15, w: 6.3, h: 0.34, fontSize: 8, align: 'center', valign: 'middle' });
const NY = 1.9, NH = 1.45, RY = NY + NH / 2;   // 주 노드 위치 · 흐름 높이
node(0.5, NY, 0.95, NH, '입력', '말 · 스케치\n문서 · STEP', X.mute, { img: 'v17_sketch.png', ih: 0.62 });
node(1.75, NY, 1.3, NH, '조건 생성기', 'LLM + 근거 DB\n요구 → 하중 · 기준 · 재료', GEN, { no: 'A', tc: GEN, img: 'v32_spec.png', ih: 0.62 });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 3.55, y: 1.68, w: 3.0, h: 2.38, rectRadius: 0.06, fill: { color: 'EEF6F5' }, line: { color: PHY, width: 1, dashType: 'dash' }, objectName: 'engine' });
s.addShape(pres.shapes.OVAL, { x: 3.45, y: 1.58, w: 0.26, h: 0.26, fill: { color: X.red }, line: { color: X.white, width: 1 } });
T(s, 'B', { x: 3.45, y: 1.58, w: 0.26, h: 0.26, fontSize: 8.5, bold: true, color: X.white, align: 'center', valign: 'middle' });
lab('역설계 엔진 — 형상 생성 ⇄ 물리 계산', 3.75, 1.7, 2.7, { b: true, c: PHY, al: 'left', fs: 7.5 });
node(3.7, 1.92, 1.12, 0.98, '형상 AI', '잠재 변수 z → 3D 형상', GEN, { tc: GEN, img: 'v87_gen_grid.png', ih: 0.4 });
node(5.28, 1.92, 1.12, 0.98, '물리 AI', '형상 → 질량 · 진동\n열 · 응력 (분포까지)\nFEM 대신 즉시 예측', PHY, { tc: PHY });
ln(4.82, 2.25, 5.28, 2.25); ln(5.28, 2.55, 4.82, 2.55);
lab('형상', 4.82, 2.08, 0.46); lab('기울기', 4.82, 2.57, 0.46);
lab('미분으로 z 조정 — 빠른 후보 탐색', 3.7, 2.92, 2.7, { b: true, c: PHY });
node(3.7, 3.22, 2.7, 0.66, '', '', NUM);
fit(s, SH + 'v79_evo.png', 3.76, 3.26, 1.25, 0.58, 'topology evolution');
T(s, [{ text: '위상 최적화 + FEM', options: { bold: true, color: C.text2, breakLine: true } }, { text: '조건 · 제조 제약 준수\n재료 배치 반복 (정밀화)', options: { fontSize: 6.5, color: C.text1 } }], { x: 5.04, y: 3.22, w: 1.32, h: 0.66, fontSize: 8, align: 'center', valign: 'middle' });
ln(4.26, 3.08, 4.26, 3.22); lab('후보', 4.3, 3.08, 0.4, { al: 'left' });
ln(6.05, 3.22, 6.05, 2.9, { d: 'dash', c: PHY }); lab('계산 결과 → 물리 AI 학습 데이터', 3.7, 3.9, 2.7, { c: PHY, al: 'right' });
node(7.05, NY, 1.2, NH, '검증 관문', '출력 STL 재격자화\n→ FEM 재계산 → 기준 비교', NUM, { no: 'C', tc: NUM, img: 'v74_verify.png', ih: 0.62 });
node(8.7, NY, 0.8, NH, '제작 파일', 'STL · STEP\n도면 · 리포트', X.ink, { fill: X.ink, tc: X.amber, sc: X.white, img: 'v25_asm.png', ih: 0.62 });
// 데이터 흐름
ln(1.45, RY, 1.75, RY); lab('요청', 1.42, RY - 0.2, 0.36);
ln(3.05, RY, 3.55, RY); lab('설계 명세\n(JSON)', 3.03, RY - 0.36, 0.54, { b: true, h: 0.32 });
ln(6.55, RY, 7.05, RY); lab('출력\nSTL', 6.53, RY - 0.36, 0.54, { b: true, h: 0.32 });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.58, y: RY + 0.07, w: 0.44, h: 0.62, rectRadius: 0.04, fill: { color: 'FFF6E8' }, line: { color: X.amber, width: 0.75 }, objectName: 'cad' });
T(s, [{ text: 'CAD 결합', options: { bold: true, color: C.text2, breakLine: true } }, { text: '매끈한 면\n고정 부품\n구멍 · 수밀', options: { color: C.text1 } }], { x: 6.58, y: RY + 0.07, w: 0.44, h: 0.62, fontSize: 5.3, align: 'center', valign: 'middle' });
ln(8.25, RY, 8.7, RY); lab('합격', 8.25, RY - 0.2, 0.45, { b: true, c: X.green });
// 불합격 되돌림
ln(7.65, NY + NH, 7.65, 4.16, { c: X.red, d: 'dash', noArrow: true }); ln(7.65, 4.16, 5.05, 4.16, { c: X.red, d: 'dash', noArrow: true }); ln(5.05, 4.16, 5.05, 4.06, { c: X.red, d: 'dash' });
lab('불합격 + 미달 항목 → 재설계', 5.2, 4.18, 2.3, { b: true, c: X.red });
// 에이전트 제어선
[[2.4, NY], [5.05, 1.68], [7.65, NY]].forEach(p => ln(p[0], 1.49, p[0], p[1], { c: CTL, d: 'sysDot', w: 1 }));
lab('호출 · 판정', 2.45, 1.56, 0.8, { c: CTL, al: 'left' });
// 바탕
node(1.75, 4.4, 1.3, 0.44, '근거 DB', '규격 · 측정 논문 · 데이터시트', X.mute, { fill: X.tint });
ln(2.4, 4.4, 2.4, NY + NH, { c: X.mute, d: 'dash' });
node(3.55, 4.4, 4.7, 0.44, '물리 모듈', '구조 · 진동 · 열 · 충격 · 제조 제약 → 낙하 · 피로 · 전자기', X.mute, { fill: X.tint });
ln(3.95, 4.4, 3.95, 4.06, { c: X.mute, d: 'dash' }); ln(8.0, 4.4, 8.0, NY + NH, { c: X.mute, d: 'dash' });
lab('실선 = 데이터 · 갈색 점선 = 에이전트 호출 · 빨간 점선 = 불합격 되돌림 · 청록 점선 = 계산 결과가 학습 데이터로 · 회색 점선 = 근거 · 물리 모듈 사용', 0.5, 4.94, 9.0, { fs: 6.3, al: 'left' });
}
s.addNotes('동작 구조. 에이전트의 A 조건 생성기 호출 → 요청과 근거 DB 기반 설계 명세(JSON) 생성. 명세는 B 역설계 엔진의 입력: 형상 AI의 잠재 변수 기반 형상 생성, 물리 AI의 성능 · 기울기 즉시 예측으로 후보 탐색. 위상 최적화 + FEM이 제조 제약 준수 하에 정밀화, 계산 결과는 물리 AI 학습 데이터로 재활용. 최종 형상은 CAD 결합(매끈한 면 · 고정 부품 · 구멍 · 수밀 처리) 후 STL로 C 검증 관문에 전달, 재격자화 · 재계산 · 기준 비교. 불합격 시 미달 항목과 함께 재설계 회귀, 합격 시 제작 파일 출력.');

// ===== v84: 핵심 기술 A · B · C — 한 장 (작동 방식 + 실제 사례 숫자, 상세는 부록)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 핵심 기술 — 전문가 의존 3개 단계를 AI · 계산으로 대체', { placeholder: 'title' });
s.addText('A 조건 설정 · B 형상 생성 · 재설계 · C 출력 형상 검증 — 요구부터 제작 파일까지 단절 없는 연결', { placeholder: 'body' });
{
const CW = 2.93, G = 0.1, Y = 1.2, H = 3.48;
const card = (i, L, name, col, fills) => { const x = 0.5 + i * (CW + G);
  box(s, x, Y, CW, H, 'FFFFFF', 'core');
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: Y, w: CW, h: H, rectRadius: 0.08, fill: { type: 'none' }, line: { color: col, width: 1.25 }, objectName: 'frame' });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.12, y: Y + 0.12, w: 0.34, h: 0.34, rectRadius: 0.06, fill: { color: col }, line: { color: col }, objectName: 'letter' });
  T(s, L, { x: x + 0.12, y: Y + 0.12, w: 0.34, h: 0.34, fontSize: 13, bold: true, color: X.white, align: 'center', valign: 'middle' });
  T(s, name, { x: x + 0.54, y: Y + 0.08, w: CW - 0.6, h: 0.28, fontSize: 11.5, bold: true, color: col, valign: 'middle' });
  T(s, '대체 단계: ' + fills, { x: x + 0.54, y: Y + 0.34, w: CW - 0.6, h: 0.18, fontSize: 7, color: C.accent3 });
  return x; };
const how = (x, lines, col) => lines.forEach((h, k) => T(s, [{ text: '▸ ', options: { color: col, bold: true } }, { text: h }], { x: x + 0.12, y: Y + 1.92 + k * 0.26, w: CW - 0.24, h: 0.26, fontSize: 7.6, color: C.text1, valign: 'middle' }));
const ev = (x, big, desc, col) => { s.addShape(pres.shapes.LINE, { x: x + 0.12, y: Y + 2.76, w: CW - 0.24, h: 0, line: { color: X.line, width: 0.75 } });
  T(s, big, { x: x + 0.12, y: Y + 2.8, w: 1.1, h: 0.6, fontSize: 19, bold: true, color: col, valign: 'middle' });
  T(s, desc, { x: x + 1.24, y: Y + 2.8, w: CW - 1.36, h: 0.6, fontSize: 7.3, color: C.text1, valign: 'middle' }); };
const pane = (x) => s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.12, y: Y + 0.6, w: CW - 0.24, h: 1.26, rectRadius: 0.04, fill: { color: X.tint }, line: { color: X.tint }, objectName: 'pane' });
// A: 말 → 조건 (변환 예시를 그대로 보여 줌)
let x = card(0, 'A', '요구 → 물리 조건', GEN, '물리 조건 (요구 정의 포함)'); pane(x);
[['"안 흔들리게"', '1차 진동수 ≥ 95 Hz', '근거 DB', X.teal], ['"울퉁불퉁한 길"', '충격 48.5 g · ≤ 26 MPa', '근거 DB', X.teal], ['스케치 "35°쯤"', '거치 35°', '질문', X.red]].forEach((r, k) => { const y = Y + 0.68 + k * 0.39;
  T(s, r[0], { x: x + 0.18, y, w: 0.95, h: 0.32, fontSize: 7.5, bold: true, color: C.text2, valign: 'middle' });
  s.addShape(pres.shapes.LINE, { x: x + 1.12, y: y + 0.16, w: 0.14, h: 0, line: { color: GEN, width: 1, endArrowType: 'triangle' } });
  T(s, r[1], { x: x + 1.3, y, w: 0.98, h: 0.32, fontSize: 7, color: C.text1, valign: 'middle' });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 2.28, y: y + 0.08, w: 0.48, h: 0.16, rectRadius: 0.08, fill: { color: r[3] }, line: { color: r[3] } });
  T(s, r[2], { x: x + 2.28, y: y + 0.08, w: 0.48, h: 0.16, fontSize: 5.8, bold: true, color: X.white, align: 'center', valign: 'middle' }); });
how(x, ['LLM은 의미 해석만 수행, 수치 계산 배제', '수치는 근거 DB에서만, 항목마다 출처', '근거 부재 시 사용자 확인 요청'], GEN);
ev(x, '6.6배', '범용 LLM 자체 예측(1.3배) 대비 실제 흔들림 — 근거 기반 조건 설정으로 원천 차단', GEN);
// B: 형상 AI × 물리 AI
x = card(1, 'B', '형상 AI × 물리 AI 역설계', X.teal, '3D 형상 생성 · 성능 해석 · 재설계'); pane(x);
T(s, '학습 형상 — 생성기가 자동으로 2,000개 (그중 6개)', { x: x + 0.18, y: Y + 0.62, w: 2.55, h: 0.14, fontSize: 6, bold: true, color: GEN });
fit(s, SH + 'v87_gen_grid.png', x + 0.14, Y + 0.76, 1.16, 0.56, 'training shapes');
s.addShape(pres.shapes.LINE, { x: x + 1.32, y: Y + 1.04, w: 0.12, h: 0, line: { color: GEN, width: 1, endArrowType: 'triangle' } });
T(s, [{ text: '형상 AI', options: { bold: true, color: GEN, breakLine: true } }, { text: '잠재 공간 z로 압축', options: { breakLine: true } }, { text: '물리 AI', options: { bold: true, color: X.teal, breakLine: true } }, { text: 'z별 성능 예측 → 목표 방향 이동', options: {} }], { x: x + 1.47, y: Y + 0.76, w: 1.32, h: 0.56, fontSize: 6.3, color: C.text1, valign: 'middle' });
T(s, '위상 최적화 정밀화 (설계 공간 → 120회)', { x: x + 0.18, y: Y + 1.33, w: 2.55, h: 0.14, fontSize: 6, bold: true, color: X.teal });
fit(s, SH + 'v79_evo.png', x + 0.14, Y + 1.47, 2.65, 0.38, 'topology evolution');
how(x, ['형상 AI(DeepSDF): 일체형 형상의 잠재 변수 표현', '물리 AI: 형상별 진동 · 열 · 응력 즉시 예측', '미분 기반 후보 탐색 → 위상 최적화로 정밀화'], X.teal);
ev(x, '5.5배', '처음 설계(판 + 기둥)와 같은 무게(94.9 → 93.9 g)에서 1차 진동수 30.5 → 168 Hz', X.teal);
// C: 출력 형상 재검증 (실제로 걸러낸 사례)
x = card(2, 'C', '출력 형상 재검증', '5B6B78', '제작 파일 직전 검증'); pane(x);
[['1차 일체형 결과', '폰 고정 형상 부재', C.text2], ['고정력 재계산', '이탈 79 N > 고정 11 N → 미달', X.red], ['4면 고정 재설계', '168 Hz · 충격 통과 → 합격', X.green]].forEach((r, k) => { const y = Y + 0.68 + k * 0.39;
  T(s, r[0], { x: x + 0.18, y, w: 1.0, h: 0.32, fontSize: 7.5, bold: true, color: C.text2, valign: 'middle' });
  T(s, r[1], { x: x + 1.12, y, w: 1.68, h: 0.32, fontSize: 7.5, bold: true, color: r[2], valign: 'middle' });
  if (k < 2) s.addShape(pres.shapes.LINE, { x: x + 0.5, y: y + 0.32, w: 0, h: 0.07, line: { color: X.mute, width: 1, endArrowType: 'triangle' } }); });
how(x, ['제조 조건(최소 두께 · 층간 · 고정 부품) 반영 계산', '출력 STL 재격자화 후 FEM 재계산', '미달 시 미달 항목과 함께 재설계 회귀'], '5B6B78');
ev(x, '4건', '외형상 타당하나 재계산에서 불합격 판정 후 재설계한 건수', '5B6B78');
box(s, 0.5, 4.78, 9.0, 0.36, X.ink, 'sum');
T(s, [{ text: 'A 조건 설정 → B 형상 탐색 → C 출력 형상 판정  ', options: { bold: true, color: X.white } }, { text: '— 세 기술이 없는 범용 LLM 단독은 동일 조건 3회 모두 불합격', options: { color: C.accent4 } }],
  { x: 0.65, y: 4.78, w: 8.7, h: 0.36, fontSize: 8.5, valign: 'middle' });
T(s, '※ 30.5 · 168 Hz = 처음 설계 · 출력 몸체를 같은 조건(폰 311 g 강체, 2 mm 격자 FEM)으로 계산. 이탈 · 고정력 = 48.5 g 충격 시 폰', { x: 0.5, y: 5.16, w: 9, h: 0.14, fontSize: 6, color: C.accent3 });
}
s.addNotes('핵심 기술 A · B · C. A 요구 → 물리 조건: 입력 표현별 판정 지표와 근거 부여, 근거 부재 시 사용자 확인. 범용 LLM은 조건을 자체 설정 · 어림 계산하여 흔들림 1.3배로 예측, 실제 6.6배. B 형상 AI × 물리 AI: 형상 AI의 잠재 변수 기반 형상 생성, 물리 AI의 즉시 성능 예측으로 후보 탐색, 위상 최적화로 정밀화. 처음 설계와 동일 무게에서 1차 진동수 30.5 → 168 Hz(5.5배). C 출력 형상 재검증: 1차 일체형 결과는 폰 고정 형상 부재로 충격 시 이탈력 79 N이 고정력 11 N 초과, 4면 고정 재설계 몸체는 168 Hz · 충격 기준 충족. 상세는 부록.');

pres.addSection({ title: '3. 실증' });
// ===== v14: 말 한 줄에서 제작 파일까지 (6단계)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '3. 실증' });
s.addText('3. 실증 — 자전거 거치대: 요구 입력부터 제작 파일까지 전 과정 수행', { placeholder: 'title' });
s.addText('각 단계 산출물이 다음 단계 입력으로 연결', { placeholder: 'body' });
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
T(s, '※ 수치 = 2 mm 격자 유한요소 해석(폰 + 고정 부품 311 g 강체, 감쇠비 3% · 발열 4 W 가정). 흔들림 = 핸들바 대비 폰 진동 배율, 두 방향 중 큰 값. 최종 형상 검증 = 출력용 몸체(81.3 g) 재해석 값. 본 사례는 위상 최적화(수치해석) 경로로 설계', { x: 0.5, y: 4.98, w: 9, h: 0.22, fontSize: 7.5, color: C.accent3 });
s.addNotes('본 사례 입력: 요청 문장 1개 + 스케치. 요구를 출처 기반 설계 명세로 변환. 처음 설계(판 + 기둥)는 30.5 Hz 공진으로 최대 5.6배 흔들림, 폰 온도 32.6 °C 상승. 3D 위상 최적화로 재료 재배치 후 출력 형상 재계산, 통과 형상만 제작 파일로 출력.');

// ===== v24: 물리로 본 차이 (분포)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '3. 실증' });
s.addText('3. 실증 — 동일 조건 물리 분포 비교: 처음 설계의 취약부 해소', { placeholder: 'title' });
s.addText('두 설계에 동일 색 척도 적용(빨강일수록 불리) — 처음 설계의 공진 · 응력 집중 · 열 갇힘 부위가 재설계에서 해소', { placeholder: 'body' });
T(s, '처음 설계 (판 + 기둥)', { x: 1.45, y: 1.22, w: 3.6, h: 0.26, fontSize: 11, bold: true, color: C.accent5, align: 'center' });
T(s, 'FormProof 재설계 (출력 몸체)', { x: 5.15, y: 1.22, w: 3.6, h: 0.26, fontSize: 11, bold: true, color: C.accent1, align: 'center' });
const PR = [
  { lab: '흔들림', sub: '길 진동 10–100 Hz\n핸들바 대비 배율', a: 'v28_Rbase.png', b: 'v51_Rbody.png', ta: '30.5 Hz 공진 — 판 끝 3.5배', tb: '168 Hz — 전체 1.2배 이하', cb: 'v26_cb_R.png' },
  { lab: '충격', sub: '48.5 g 위아래\nvon Mises 응력', a: 'v28_Vbase.png', b: 'v51_Vbody.png', ta: '판 뿌리 응력 집중 — 최대 14.7 MPa', tb: '분산 — 최대 2.9 MPa', cb: 'v26_cb_V.png' },
  { lab: '열', sub: '폰 발열 4 W\n온도 상승', a: 'v25_Tbase.png', b: 'v51_Tbody.png', ta: '폰 뒷면 덮개 구조 +32.6 °C', tb: '뒷면 개방 구조 +20.8 °C', cb: 'v26_cb_T.png' }];
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
s.addNotes('각 행은 두 설계에 동일 색 척도 적용, 빨강일수록 불리. 흔들림: 길 진동 10–100 Hz 동안 핸들바 대비 각 지점 진동 배율(RMS). 충격: 48.5 g 상하 충격 시 응력. 열: 폰 발열 4 W 시 온도 상승. 처음 설계는 1차 30.5 Hz가 길 진동 대역과 겹쳐 최대 5.6배 흔들림. AI 재설계(출력 몸체)는 1차 168 Hz로 길 진동 대역 밖, 최대 흔들림 1.27배. 처음 설계는 판이 폰 뒷면을 덮어 열 갇힘(+32.6 °C), AI 재설계는 뒷면 개방으로 방열(+20.8 °C).');

// ===== v25: 구조 — 무엇이 폰을 잡나 + 조립도
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '3. 실증' });
s.addText('3. 실증 — 제작 가능성: 구조 · 조립도 · 부품 구성', { placeholder: 'title' });
s.addText('폰 4면 고정부는 고정 영역, 그 사이 삼각 프레임은 계산으로 생성 — 출력 부품 4개 + 시판 부품으로 조립', { placeholder: 'body' });
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
s.addNotes('좌측: 최종 거치대 각 부위의 기능. 아래 걸이는 폰 하단, 스프링 집게는 양옆, 위쪽 걸이는 상단 고정, 위쪽 받침은 뒷면 지지. 해당 부위는 제작 조건으로 고정, 클램프와 받침부를 잇는 삼각 프레임만 계산으로 생성. 우측: 조립도(3면도, 부품 번호, 부품표, 표제란).');

// ===== v38: 범용 LLM 단독 vs FormProof (일체형 · 같은 조건)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '3. 실증' });
s.addText('3. 실증 — 범용 LLM 단독 vs FormProof: 동일 요청 · 동일 검증', { placeholder: 'title' });
s.addText('LLM 단독 3개 안 모두 불합격, 자체 예측도 실제와 불일치 — 계산 없이는 안의 적합성 판단 불가', { placeholder: 'body' });
const LL = [
  { name: 'LLM 단독 A', img: 'v38_L1.png', crit: '≥ 90 Hz', pf: 95, f: 150.6, ps: 1.2, pk: 1.37, m: 87.7, t: 22.6, ok: false, note: '폰 온도 초과' },
  { name: 'LLM 단독 B', img: 'v38_L2.png', crit: '≥ 60 Hz', pf: 70, f: 109.6, ps: 1.25, pk: 2.95, m: 79.8, t: 20.5, ok: false, note: '앞뒤 흔들림 2.95배' },
  { name: 'LLM 단독 C', img: 'v38_L3.png', crit: '≥ 80 Hz', pf: 85, f: 89.7, ps: 1.3, pk: 6.57, m: 80.0, t: 20.6, ok: false, note: '위쪽 레일 공진 6.6배' },
  { name: 'FormProof', img: 'v28_Ropt.png', crit: '계산으로 판정', pf: null, f: 153.9, ps: null, pk: 1.39, m: 77.1, t: 20.7, ok: true, note: '전 기준 충족 (설계 단계)' }];
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
  T(s, (fp ? '합격 — ' : '불합격 — ') + d.note, { x: x + 0.14, y: 4.06, w: LW - 0.28, h: 0.5, fontSize: 8.5, bold: true, color: fp ? C.background1 : C.accent5, align: 'center', valign: 'middle' }); });
T(s, '※ LLM 단독 = 도구 · 계산 없이 같은 요청 · 같은 일체형 조건(35°, 같은 걸이 · 집게 · 레일, 311 g)을 받은 독립 세션 3회(Claude, 2026-11-15). 판정은 모두 같은 2 mm 격자 FEM · 감쇠비 3% · 발열 4 W. 흔들림 = 핸들바 대비 최대(10–100 Hz, 위아래 · 앞뒤 중 큰 값). 그림 색 = 같은 척도의 흔들림 분포. FormProof 값 = 출력 변환 전 최적화 결과(LLM 안과 같은 단계). 출력 몸체(81.3 g)도 재해석 통과', { x: 0.5, y: 4.74, w: 9, h: 0.4, fontSize: 7, color: C.accent3 });
s.addNotes('동일 요청 · 동일 일체형 조건을 도구 없는 LLM 세션 3개에 입력. 3개 세션 모두 트러스 · 스파인 구조 제시, 진동 기준(60~90 Hz)과 흔들림 1.2~1.3배를 자체 예측. 동일 해석기 판정 결과: A는 흔들림 1.37배로 양호하나 폰 뒷면을 덮어 온도 기준(21 °C) 초과, 10 g 더 무거움. B는 앞뒤 2.95배, C는 위쪽 레일 공진으로 6.6배. 예측 진동수도 실제와 불일치. 결론: LLM 단독으로 양호한 안이 나올 수는 있으나 계산 없이는 판별 불가. FormProof는 전 기준을 계산으로 확인, 최경량 안 도출.');

pres.addSection({ title: '4. DX 기여 · 확장' });
// ---------- 7. 사업·조직 기여
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '4. DX 기여 · 확장' });
s.addText('4. DX 기여 — 설계 전 단계에서 누구나 성능 확인 · 개선 가능', { placeholder: 'title' });
s.addText('기여 대상은 개별 제품이 아닌 방법론 — 설계자 · 기획자 · 특허 제안자 공통 활용', { placeholder: 'body' });
const stg = [['구상', '경험 기반 형상 결정', '요구 조건에서 설계안 자동 생성'],
  ['상세 설계', '해석 의뢰 · 결과 대기', '설계자가 직접 성능 확인 (근거 포함)'],
  ['개선', '해석 결과 기반 수작업 수정', '계산으로 재설계 (경량화 · 보강)'],
  ['시제품', '출력 · 시험 → 실패 → 수정', '출력 전 제작 형상까지 검증']];
T(s, '현행', { x: 1.5, y: 1.26, w: 1.9, h: 0.24, fontSize: 10, bold: true, color: C.accent3 });
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
T(s, 'TV 스탠드 다리 — 외형 유지', { x: 6.42, y: 1.66, w: 3.0, h: 0.22, fontSize: 9.5, bold: true, color: C.text2 });
fit(s, SH + 'v6_c_tv_foot_base_S.png', 6.42, 1.92, 1.4, 0.95, 'solid foot');
fit(s, SH + 'v6_c_tv_foot_opt_S.png', 7.98, 1.92, 1.4, 0.95, 'AI foot');
T(s, '꽉 찬 판 400 g', { x: 6.42, y: 2.87, w: 1.4, h: 0.18, fontSize: 7.5, color: C.accent3, align: 'center' });
T(s, 'AI 설계 124 g', { x: 7.98, y: 2.87, w: 1.4, h: 0.18, fontSize: 7.5, bold: true, color: C.accent1, align: 'center' });
T(s, [{ text: '−69%', options: { fontSize: 18, bold: true, color: C.accent1 } }, { text: '  다리 무게 · 흔들림 0.23 mm · 넘어짐 통과', options: { fontSize: 7.5, color: C.text1 } }], { x: 6.42, y: 3.1, w: 3.0, h: 0.56, valign: 'middle' });
// 적용 대상
T(s, '적용 대상 — 동일 엔진, 하중 · 재료 · 기준만 변경', { x: 0.5, y: 3.88, w: 6, h: 0.24, fontSize: 10, bold: true, color: C.text2 });
[['VD', 'TV 스탠드 · 벽걸이', '실증 −69%', X.green], ['MX', '폰 · 폴더블 내부 브래킷', '구조 · 열 · 낙하', X.teal], ['DA', '세탁기 · 에어컨 모터 마운트', '진동 · 음향', X.teal], ['공통', '특허 아이디어 · 기존 부품(STEP)', '성능 근거 · 경량화', X.ink]].forEach((t, i) => { const x = 0.5 + i * 2.27;
  pill(s, x, 4.16, 0.6, t[0], t[3], X.white);
  T(s, [{ text: t[1], options: { bold: true, color: C.text2, breakLine: true } }, { text: t[2], options: { color: C.accent3 } }], { x: x + 0.66, y: 4.12, w: 1.58, h: 0.5, fontSize: 8 }); });
T(s, '※ TV 스탠드: 65형 · 알루미늄 10 mm 판재 · 외곽 고정, 출력 형상 3D 재계산(부록 상세). MX · DA 항목은 적용 후보로 사업부 확인 필요. 정량 효과(해석 의뢰 기간, 시제품 반복 횟수)는 담당자 확인 필요', { x: 0.5, y: 4.78, w: 9, h: 0.36, fontSize: 7, color: C.accent3 });
s.addNotes('기여 대상은 방법론. 단계별 현행 방식과 적용 후 비교, VD TV 스탠드에서 외형 유지 상태로 다리 무게 69% 절감 실증. MX · DA는 동일 엔진의 적용 후보.');

// ---------- 8. 확장성·파급 효과
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '4. DX 기여 · 확장' });
s.addText('4. 확장성 · 파급 효과 — 제품은 동일 엔진, 물리는 모듈 추가로 확장', { placeholder: 'title' });
s.addText('동일 흐름(입력 → 설계 명세 → 계산 → 재설계 → 검증 → 출력) 유지, 적용 범위 확대', { placeholder: 'body' });
// two axes
box(s, 0.5, 1.3, 4.35, 2.55, X.tint, 'product axis');
T(s, '제품 확장 — 같은 물리(구조), 다른 제품', { x: 0.65, y: 1.4, w: 4.1, h: 0.3, fontSize: 12, bold: true, color: C.text2 });
pill(s, 3.75, 1.42, 0.95, '입증', X.green, X.white);
[['TV 스탠드', '정적 강성 · 넘어짐', 'v6_c_tv_foot_opt.png'], ['자전거 거치대', '진동 · 열 · 충격', 'v47_use.png']].forEach((p, i) => {
  const x = 0.65 + i * 2.1;
  box(s, x, 1.8, 1.95, 1.4, X.white, 'case');
  fit(s, SH + p[2], x + 0.05, 1.85, 1.85, 1.0, p[0]);
  T(s, p[0], { x, y: 2.85, w: 1.95, h: 0.2, fontSize: 9.5, bold: true, color: C.text2, align: 'center' });
  T(s, p[1], { x, y: 3.03, w: 1.95, h: 0.18, fontSize: 8.5, color: C.accent3, align: 'center' });
});
T(s, '하중 · 재료 · 고정 위치 · 판정 기준 변경만으로 다른 설계 문제 해결', { x: 0.65, y: 3.35, w: 4.1, h: 0.4, fontSize: 10, color: C.text1 });
box(s, 5.15, 1.3, 4.35, 2.55, X.tint, 'physics axis');
T(s, '물리 확장 — 방정식 모듈 추가', { x: 5.3, y: 1.4, w: 4.1, h: 0.3, fontSize: 12, bold: true, color: C.text2 });
const ph = [['구조 (탄성)', '정적 · 진동', '입증', X.green], ['+ 열 (열전도)', '무선충전 스탠드: 방열판 배치', '입증', X.green], ['+ 낙하 · 피로 · 소음', '폰 · 가전 기구 부품 신뢰성', '다음 단계', X.mute], ['+ 전자기', '무선충전 금속 금지 구역 계산', '다음 단계', X.mute]];
ph.forEach((p, i) => {
  const y = 1.82 + i * 0.5;
  s.addImage({ data: [IC.cogs, IC.heat, IC.bulb, IC.bolt][i], x: 5.3, y: y + 0.07, w: 0.3, h: 0.3 });
  T(s, p[0], { x: 5.7, y, w: 1.45, h: 0.44, fontSize: 10.5, bold: true, color: C.text2, valign: 'middle' });
  T(s, p[1], { x: 7.15, y, w: 1.4, h: 0.44, fontSize: 8.5, color: C.text1, valign: 'middle' });
  pill(s, 8.55, y + 0.08, 0.85, p[2], p[3], X.white);
});
T(s, '향후 계획', { x: 0.5, y: 3.98, w: 2, h: 0.26, fontSize: 11, bold: true, color: C.accent1 });
[['입력 확장', '문서 · 특허 · STEP 입력'], ['자동 실행', '에이전트가 단계 실행 · 검증 리포트'], ['물리 모듈', '낙하 · 피로 → 전자기'], ['시범 적용', 'VD 스탠드 실제 설계 과제']].forEach((r, i) => { const x = 0.5 + i * 2.27;
  box(s, x, 4.28, 2.15, 0.58, X.tint, 'road');
  T(s, [{ text: (i + 1) + '  ' + r[0], options: { bold: true, color: C.text2, breakLine: true } }, { text: r[1], options: { color: C.text1 } }], { x: x + 0.1, y: 4.3, w: 1.98, h: 0.54, fontSize: 8.5, valign: 'middle' });
  if (i < 3) s.addShape(pres.shapes.CHEVRON, { x: x + 2.16, y: 4.48, w: 0.09, h: 0.18, fill: { color: X.amber }, line: { color: X.amber } }); });
T(s, '파급: 생성형 AI 결과의 물리 검증 관문 — 타 생성형 AI 과제에 재사용 가능 · 설계 데이터 누적에 따라 물리 AI 정확도 향상, 계산 시간 단축', { x: 0.5, y: 4.92, w: 9, h: 0.24, fontSize: 7.5, color: C.accent3 });
s.addNotes('확장 2축. 제품 확장: 2개 사례로 입증(동일 구조 방정식, 상이한 하중 · 재료 · 기준). 물리 확장: 방정식 모듈 추가 구조, 열은 무선충전 스탠드와 거치대(폰 온도 제약)로 입증. 낙하 · 피로 · 소음 · 전자기는 다음 단계.');

pres.addSection({ title: '마무리' });
// ---------- 9. 마무리
s = pres.addSlide({ masterName: 'DARK', sectionTitle: '마무리' });
T(s, '형상을\n성능으로 증명', { x: 0.6, y: 1.5, w: 5.0, h: 1.4, fontSize: 32, bold: true, color: C.background1 });
T(s, '아이디어에서 제품까지, 성능은 계산으로', { x: 0.6, y: 3.05, w: 5.0, h: 0.4, fontSize: 16, color: C.accent4 });
box(s, 5.9, 1.1, 3.7, 3.2, 'FFFFFF', 'final card');
fit(s, SH + 'v17_hero.png', 6.0, 1.25, 3.5, 2.9, 'final design');

pres.addSection({ title: '부록' });
// ===== v82: 핵심 기술 ① — 요청 → 물리 조건 (과정 + 출처 추적)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '부록' });
s.addText('부록. 핵심 기술 A 상세 — 요구를 계산할 수 있는 물리 조건으로', { placeholder: 'title' });
s.addText('LLM은 계산 배제 — 의미 해석, 수치는 근거 DB에서만 선택, 출처 부재 시 확인 요청', { placeholder: 'body' });
{
// 과정 띠
const PS = [['요구 입력', '말 · 스케치 · 문서 · STEP', X.mute], ['뜻 해석', 'LLM: 표현 → 물리량', GEN], ['근거 검색', '근거 DB에서 수치 선택', GEN], ['설계 명세', '값마다 출처 · 형식 검사', GEN], ['빠진 조건 질문', '출처 부재 시 확인 요청', X.amber], ['계산 기준', '엔진 입력 (JSON)', X.ink]];
const PW = 1.44, PG = 0.08;
PS.forEach((p, i) => { const x = 0.5 + i * (PW + PG);
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.2, w: PW, h: 0.5, rectRadius: 0.06, fill: { color: i === 5 ? X.ink : 'FFFFFF' }, line: { color: p[2], width: 1.25 }, objectName: 'proc' });
  T(s, [{ text: p[0], options: { bold: true, color: i === 5 ? X.amber : p[2], breakLine: true } }, { text: p[1], options: { fontSize: 6.8, color: i === 5 ? X.white : C.text1 } }], { x, y: 1.2, w: PW, h: 0.5, fontSize: 8.5, align: 'center', valign: 'middle' });
  if (i < 5) s.addShape(pres.shapes.LINE, { x: x + PW, y: 1.45, w: PG, h: 0, line: { color: X.mute, width: 1.25, endArrowType: 'triangle' } }); });
// 요청 카드
box(s, 0.5, 1.86, 2.15, 2.62, X.ink, 'request');
T(s, '이 사례의 요청', { x: 0.62, y: 1.95, w: 1.9, h: 0.22, fontSize: 8.5, bold: true, color: C.accent4 });
T(s, '"울퉁불퉁한 길에서도 폰이 안 흔들리게, 최대한 가볍게. 3D 프린터로 뽑을 거야"', { x: 0.62, y: 2.18, w: 1.95, h: 1.1, fontSize: 11, italic: true, bold: true, color: C.background1 });
fit(s, SH + 'v17_sketch.png', 0.6, 3.36, 1.95, 1.08, 'input sketch');
// 결과 표: 출처 종류 칩
const SRC = { 텍스트: '6B4FA0', 스케치: '6B4FA0', 'DB': X.teal, 가정: X.amber, 질문: X.red };
const RQ = [
  ['"안 흔들리게"', '핸들바 → 폰 진동 전달 최소', '1차 진동수 ≥ 95 Hz', [['DB', '조약돌길 실측 ISBS 2020']]],
  ['"울퉁불퉁한 길"', '충격 시 파손 방지', '48.5 g 충격 · 응력 ≤ 26 MPa', [['DB', '같은 실측 · PETG 39 MPa ÷ 1.5']]],
  ['"최대한 가볍게"', '무게 최소', '출력 몸체 무게 (g)', [['텍스트', '요청 문장']]],
  ['"모든 폰"', '폭 64–90 · 두께 6–14 mm · ≤ 290 g', '4면 고정 · 폰 + 부품 311 g 강체', [['DB', '시판 폰 범위']]],
  ['스케치 "35°쯤"', '거치 각도', '35°', [['스케치', '근사값'], ['질문', '맞나요?']]],
  ['"열 안 갇히게"', '폰 발열 방출 확보', '폰 온도 상승 ≤ 21 °C', [['가정', '발열 4 W'], ['질문', '맞나요?']]]];
const RX = [2.82, 4.0, 5.62, 7.42], RW = [1.15, 1.6, 1.78, 2.08], RY = 1.86, RH = 0.36;
['표현', '물리 해석', '판정 지표', '출처'].forEach((h, k) => T(s, h, { x: RX[k], y: RY, w: RW[k], h: 0.22, fontSize: 8.5, bold: true, color: C.accent1 }));
RQ.forEach((r, i) => { const y = RY + 0.26 + i * (RH + 0.03);
  box(s, 2.76, y, 6.74, RH, i % 2 ? 'FFFFFF' : X.tint, 'row');
  [0, 1, 2].forEach(k => T(s, r[k], { x: RX[k], y, w: RW[k] - 0.06, h: RH, fontSize: k === 0 ? 8.5 : 7.5, bold: k === 0, color: C.text1, valign: 'middle' }));
  let cx = RX[3]; r[3].forEach(([kind, txt]) => { const pw = 0.42;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx, y: y + RH / 2 - 0.085, w: pw, h: 0.17, rectRadius: 0.085, fill: { color: SRC[kind] }, line: { color: SRC[kind] }, objectName: 'src' });
    T(s, kind === 'DB' ? '근거 DB' : kind, { x: cx, y: y + RH / 2 - 0.085, w: pw, h: 0.17, fontSize: 5.8, bold: true, color: X.white, align: 'center', valign: 'middle' });
    const tw = r[3].length > 1 ? 0.55 : 1.6; T(s, txt, { x: cx + pw + 0.04, y, w: tw, h: RH, fontSize: 6.8, color: C.accent3, valign: 'middle' }); cx += pw + 0.04 + tw + 0.04; }); });
// 아래: 제작 조건 + 질문
box(s, 0.5, 4.64, 4.45, 0.46, 'FFF6E8', 'make');
T(s, [{ text: '제작 조건  ', options: { bold: true, color: C.accent2 } }, { text: '"3D 프린터" → 요구가 아닌 설계 제약: 출력 방향 · 층간 강도 · 최소 두께를 계산에 반영', options: { color: C.text1 } }], { x: 0.6, y: 4.64, w: 4.3, h: 0.46, fontSize: 7.5, valign: 'middle' });
box(s, 5.05, 4.64, 4.45, 0.46, X.tint, 'q');
T(s, [{ text: '사용자 확인 요청  ', options: { bold: true, color: X.red } }, { text: '"핸들바 지름 31.8 mm 맞나요?" · "35°로 계산할까요?" · "발열 4 W로 둘까요?"', options: { color: C.text1 } }], { x: 5.15, y: 4.64, w: 4.3, h: 0.46, fontSize: 7.5, valign: 'middle' });
}
s.addNotes('핵심 기술 A. LLM은 요청 의미를 물리량으로 해석하되 수치 생성은 배제. 수치는 근거 DB(실측 논문 · 규격 · 데이터시트)에서만 선택, 모든 값에 출처 유형(텍스트 · 스케치 · 근거 DB · 가정) 표기. 근거 부재 시 사용자 확인 요청. 결과는 형식 검사를 통과한 JSON으로 계산 엔진에 전달. 범용 LLM 단독의 실패 원인(자체 기준 설정 · 어림 계산)을 구조적으로 차단.');

// ===== v85: 핵심 기술 B 상세 — 일체형 기준
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '부록' });
s.addText('부록. 핵심 기술 B 상세 — 형상 AI × 물리 AI × 위상 최적화', { placeholder: 'title' });
s.addText('형상 AI의 후보 생성 · 물리 AI의 즉시 평가 · 미분 기반 탐색 → 위상 최적화로 제약 준수 정밀화', { placeholder: 'body' });
{
const CW = 2.9, cardY = 1.28, cardH = 2.62;
const card = (i, t, kind, kc) => { const x = 0.5 + i * (CW + 0.15); box(s, x, cardY, CW, cardH, X.tint, 'ai card');
  T(s, t, { x: x + 0.12, y: cardY + 0.07, w: CW - 0.24, h: 0.26, fontSize: 11, bold: true, color: C.text2 });
  T(s, kind, { x: x + 0.12, y: cardY + 0.33, w: CW - 0.24, h: 0.2, fontSize: 8, bold: true, color: kc }); return x; };
const lines = (x, arr) => T(s, arr.map((a, k) => ({ text: a[0], options: { bold: !!a[1], color: a[1] ? C.text1 : C.accent3, breakLine: k < arr.length - 1 } })), { x: x + 0.12, y: cardY + 1.42, w: CW - 0.24, h: 1.12, fontSize: 8.5, paraSpaceAfter: 2 });
let cx = card(0, '형상 AI — 형상을 잠재 변수로', 'DeepSDF (잠재 변수 32개 → SDF → 3D)', GEN);
fit(s, SH + 'v87_gen_grid.png', cx + 0.08, cardY + 0.58, CW - 0.16, 0.8, 'training shapes');
lines(cx, [['학습 형상: 생성기 자동 생성 2,000개 + 위상 최적화 이력 245개', 1], ['그림은 생성기 형상 6개 — 생성기는 형상 계열 전반, 이력은 최종 설계 인근 담당', 0], ['합격 기준: 학습 형상 재구성 IoU ≥ 0.8', 1], ['입력 격자 88 × 20 × 37 (2 mm 간격)', 0]]);
cx = card(1, '물리 AI — 형상 → 성능과 분포', '3D 신경 연산자 (FNO) · 기준 모델 3D CNN', C.accent1);
// 입출력 도식
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx + 0.14, y: cardY + 0.66, w: 0.78, h: 0.62, rectRadius: 0.04, fill: { color: 'FFFFFF' }, line: { color: GEN, width: 1 } });
T(s, [{ text: '형상', options: { bold: true, color: GEN, breakLine: true } }, { text: '격자 점유\n65,120칸', options: { fontSize: 6.3, color: C.text1 } }], { x: cx + 0.14, y: cardY + 0.66, w: 0.78, h: 0.62, fontSize: 8, align: 'center', valign: 'middle' });
s.addShape(pres.shapes.LINE, { x: cx + 0.94, y: cardY + 0.97, w: 0.22, h: 0, line: { color: C.accent1, width: 1.25, endArrowType: 'triangle' } });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx + 1.18, y: cardY + 0.62, w: 1.6, h: 0.7, rectRadius: 0.04, fill: { color: 'FFFFFF' }, line: { color: X.teal, width: 1 } });
T(s, [{ text: '값 7개', options: { bold: true, color: X.teal, breakLine: true } }, { text: '질량 · 1 · 2차 진동수 · 폰 온도 상승\n터치 처짐(위 · 아래) · 충격 응력', options: { fontSize: 6, color: C.text1, breakLine: true } }, { text: '분포 2개  ', options: { bold: true, color: X.teal } }, { text: '온도 · 응력', options: { fontSize: 6, color: C.text1 } }], { x: cx + 1.22, y: cardY + 0.62, w: 1.54, h: 0.7, fontSize: 7.5, valign: 'middle' });
lines(cx, [['학습 라벨 = 같은 FEM 엔진이 계산한 값 · 분포', 1], ['진동 · 열 · 처짐 · 충격 동시 예측, 기울기 제공', 0], ['고정 인터페이스: predict(형상) → 값, 분포', 1], ['STEP · 비정형 메시 입력: GINO로 확장', 0]]);
cx = card(2, '결합 탐색 → 위상 최적화', '미분으로 잠재 변수 조정 → 정밀화', C.accent1);
fit(s, SH + 'v79_evo.png', cx + 0.08, cardY + 0.66, CW - 0.16, 0.62, 'topology evolution');
lines(cx, [['목표 미달 · 질량 벌점 기반 z 조정 (Adam)', 1], ['후보 활용: 위상 최적화 시작점 또는 직접 검증', 0], ['위상 최적화: 진동 · 열 · 처짐 제약 + 출력 방향 · 최소 두께', 1], ['계산 결과는 물리 AI 학습 데이터로 재활용', 0]]);
// 결과 줄
const FL = [['처음 설계 (판 + 기둥)', '94.9 g · 30.5 Hz', X.mute], ['위상 최적화 120회', '진동 · 열 · 처짐 제약', X.teal], ['출력 몸체', '93.9 g · 168 Hz', GEN], ['출력 형상 재검증', '충격 · 열 · 처짐 합격', X.green]];
FL.forEach((f, i) => { const x = 0.5 + i * 2.32;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 4.02, w: 2.05, h: 0.62, rectRadius: 0.06, fill: { color: 'FFFFFF' }, line: { color: f[2], width: 1.5 }, objectName: 'flow box' });
  T(s, f[0], { x: x + 0.08, y: 4.06, w: 1.9, h: 0.24, fontSize: 8.5, color: C.accent3, align: 'center' });
  T(s, f[1], { x: x + 0.08, y: 4.3, w: 1.9, h: 0.3, fontSize: 11, bold: true, color: f[2], align: 'center' });
  if (i < 3) arrow(s, x + 2.08, 4.2, 0.2, 0.26); });
T(s, '※ 같은 조건(폰 311 g 강체, 2 mm 격자 FEM, 3% 감쇠)으로 계산. 출력 몸체 93.9 g은 계산 격자 기준, 출력 STL은 81.3 g', { x: 0.5, y: 4.72, w: 9, h: 0.3, fontSize: 7.5, color: C.accent3 });
}
s.addNotes('형상 AI(DeepSDF): 생성기 형상과 위상 최적화 이력으로 학습, 형상을 잠재 변수 32개로 표현. 물리 AI: 동일 FEM 엔진이 생성한 라벨로 학습, 형상별 질량 · 진동수 · 온도 · 처짐 · 충격 응력 및 온도 · 응력 분포 예측, 기울기 제공. 두 모델 결합으로 잠재 변수를 미분 기반 조정하여 후보 탐색, 위상 최적화로 제약 준수 정밀화. 처음 설계 94.9 g · 30.5 Hz → 출력 몸체 93.9 g · 168 Hz.');

// ===== v7: 검증 관문이 걸러낸 사례
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '부록' });
s.addText('부록. 핵심 기술 C 상세 — 출력 형상 재계산으로 불합격 설계 차단', { placeholder: 'title' });
s.addText('제조 조건 반영 계산 후 출력 형상 재판정 — 본 과제 수행 중 차단 4건', { placeholder: 'body' });
const fails = [
  ['자전거 거치대', '폰 질점 가정 진동 모델', '자체 점검: 폰 회전 관성 누락\n→ 진동수 과대 (178 → 실제 98.5 Hz)', '폰을 관성 포함 강체로 재모델링\n→ 전 설계 재평가 · 재최적화'],
  ['TV 스탠드 다리', '3D 격자 위상최적화', '격자보다 가는 부재 · 중간 밀도 잔존\n→ 출력 형상 재검증 3회 불합격', '판재 평면 최적화로 전환\n→ 124 g · 흔들림 0.23 mm 통과'],
  ['무선충전 방열판', '내부 방열 구조 최적화 v1', '중간 밀도(회색) 형상\n→ 실제 제작 불가 판정', '실제 제품 구조 기준 재정의\n→ 알루미늄 판금 2장 형상'],
  ['자전거 거치대 일체형', '1차 일체형 결과 (검토에서 발견)', '폰 고정 형상 부재\n→ 충격 시 이탈력 79 N > 고정력 11 N', '4면 고정(걸이 · 집게 · 잠금)\n→ 재최적화 · 출력 몸체 재검증 통과']];
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
T(s, '검증 부재 시 4건 모두 그대로 제작 파일로 출력되었을 사안 — 길 진동 자료 오독(자갈길 최대값 → 조약돌길 중앙값)도 동일 점검에서 정정', { x: 0.5, y: 4.55, w: 9, h: 0.28, fontSize: 10.5, bold: true, color: C.accent1 });
s.addNotes('실제 작업 기록 기준. 검증 모듈의 출력 형상 재계산 · 제작 가능성 판정으로 불합격 처리, 에이전트가 방식 변경 후 재설계.');

// ===== v70: 파이프라인 — 기술(가로줄) × 단계(세로칸) 지도
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '부록' });
s.addText('부록. 프레임워크 상세 — 단계별 담당 기술', { placeholder: 'title' });
s.addText('연결 기반: 핵심 기술 3종 — A 요구 → 물리 조건 · B 형상 AI × 물리 AI 역설계 · C 출력 형상 재검증', { placeholder: 'body' });
{
const PHY = X.teal, NUM = '5B6B78', OUT = X.ink;
const STEPS = ['요구 정의', '물리 조건', '3D 형상 생성', '성능 해석', '재설계', '제작 파일'];
// 가로줄 = 맡는 기술
const LANES = [[GEN, '생성 AI', 'LLM · 형상 AI'], [PHY, '물리 AI', '빠른 예측 · 역설계'], [NUM, '수치해석', '정밀 계산 · 최적화'], [OUT, '출력', '제작 · 기록']];
// [줄, 칸, 제목, 설명, 상태 0 개발 중 / 1 시연 / 2 시연 · 분리형]
const CARDS = [
  [0, 0, '요구 → 목표 · 제약', '말 · 스케치 · 문서 · STEP', 1],
  [0, 1, '설계 명세', '하중 · 기준 · 재료, 항목마다 출처', 1, 'A'],
  [0, 2, '형상 AI 후보', '고정 부품 · 설계 공간 코드', 1, 'B'],
  [1, 3, '성능 예측', '진동 · 열 · 응력 즉시 예측', 1],
  [1, 4, '잠재 공간 최적화', '미분으로 후보 탐색', 1, 'B'],
  [2, 3, 'FEM 해석', '진동 · 충격 · 열 · 터치', 1],
  [2, 2, '위상 최적화', '조건 · 제조 제약에서 형상 계산', 1, 'C'],
  [2, 4, '위상 최적화 반복', '기준 충족 시까지', 1],
  [2, 5, '출력 형상 재검증', '출력 STL로 재판정', 1, 'C'],
  [3, 5, 'STL · STEP · 도면', '조립 설명서 포함', 1],
  [3, 4, '근거 리포트', '성능 · 출처 · 미확인 항목', 1]];
const LX = 0.5, LW = 1.15, SX = 1.72, CWp = 1.28, GP = 0.02, HY = 1.22, LY0 = 1.58, LH = 0.54, LG = 0.05;
const STT = [['개발 중', 'FFFFFF', NUM], ['시연', X.green, X.white], ['시연 · 분리형', X.amber, X.white]];
STEPS.forEach((st, i) => { const x = SX + i * (CWp + GP);
  s.addShape(pres.shapes.CHEVRON, { x, y: HY, w: CWp + 0.04, h: 0.3, fill: { color: X.ink }, line: { color: X.ink }, objectName: 'step' });
  T(s, st, { x: x + 0.12, y: HY, w: CWp - 0.2, h: 0.3, fontSize: 7.5, bold: true, color: X.white, align: 'center', valign: 'middle' }); });
LANES.forEach((l, r) => { const y = LY0 + r * (LH + LG);
  s.addShape(pres.shapes.RECTANGLE, { x: LX, y, w: 9.0, h: LH, fill: { color: r % 2 ? 'FFFFFF' : 'F6F7F8' }, line: { color: 'E1E5E8', width: 0.5 }, objectName: 'lane' });
  s.addShape(pres.shapes.RECTANGLE, { x: LX, y, w: 0.07, h: LH, fill: { color: l[0] }, line: { color: l[0] }, objectName: 'lane bar' });
  T(s, [{ text: l[1], options: { bold: true, color: l[0], breakLine: true } }, { text: l[2], options: { fontSize: 6.5, color: C.accent3 } }], { x: LX + 0.14, y, w: LW, h: LH, fontSize: 9, valign: 'middle' }); });
CARDS.forEach(c => { const [r, i, ti, de, stv, bd] = c, x = SX + i * (CWp + GP) + 0.04, y = LY0 + r * (LH + LG) + 0.05, w = CWp - 0.08, h = LH - 0.1, dev = stv === 0, col = LANES[r][0];
  s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: dev ? 'FFFFFF' : col, transparency: dev ? 0 : 85 }, line: { color: dev ? 'C9CED2' : col, width: 0.75, dashType: dev ? 'dash' : 'solid' }, objectName: 'card' });
  T(s, ti, { x: x + 0.06, y: y + 0.03, w: w - 0.1, h: 0.2, fontSize: 7.5, bold: true, color: dev ? C.accent3 : C.text2 });
  T(s, de, { x: x + 0.06, y: y + 0.22, w: w - 0.1, h: 0.2, fontSize: 6.5, color: C.text1 });
  if (bd) { s.addShape(pres.shapes.OVAL, { x: x + w - 0.22, y: y - 0.06, w: 0.24, h: 0.24, fill: { color: X.red }, line: { color: X.white, width: 1 }, objectName: 'core' });
    T(s, bd, { x: x + w - 0.22, y: y - 0.06, w: 0.24, h: 0.24, fontSize: 8, bold: true, color: X.white, align: 'center', valign: 'middle' }); }
  });
// 흐름 화살표 (카드 → 카드)
const cc = (r, i) => ({ x: SX + i * (CWp + GP) + 0.04, y: LY0 + r * (LH + LG) + 0.05, w: CWp - 0.08, h: LH - 0.1 });
const arr = (a, b) => { const A = cc(...a), B = cc(...b);
  let x1, y1, x2, y2;
  if (a[0] === b[0]) { x1 = A.x + A.w; y1 = A.y + A.h / 2; x2 = B.x; y2 = y1; }
  else if (a[1] === b[1]) { x1 = A.x + A.w / 2; y1 = b[0] > a[0] ? A.y + A.h : A.y; x2 = x1; y2 = b[0] > a[0] ? B.y : B.y + B.h; }
  else { x1 = A.x + A.w; y1 = A.y + A.h / 2; x2 = B.x; y2 = B.y + B.h / 2; }
  s.addShape(pres.shapes.LINE, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1) || 0.001, h: Math.abs(y2 - y1) || 0.001, flipV: (y2 < y1) !== (x2 < x1), line: { color: '8A949C', width: 1, endArrowType: 'triangle' }, objectName: 'flow' }); };
[[[0, 0], [0, 1]], [[0, 1], [0, 2]], [[0, 1], [2, 2]], [[0, 2], [1, 3]], [[2, 2], [2, 3]], [[1, 3], [1, 4]], [[2, 3], [2, 4]], [[2, 4], [2, 5]], [[2, 5], [3, 5]], [[2, 4], [3, 4]]].forEach(p => arr(p[0], p[1]));
// 반복 고리 (재검증 불합격 → 재설계)
const cx = i => SX + i * (CWp + GP) + CWp / 2, ry = LY0 + 2 * (LH + LG) + 0.035;
s.addShape(pres.shapes.LINE, { x: cx(4), y: ry, w: cx(5) - cx(4), h: 0, line: { color: X.amber, width: 1.25, dashType: 'dash', beginArrowType: 'triangle' } });
T(s, '불합격 → 재설계', { x: cx(4) + 0.1, y: ry - 0.15, w: 1.1, h: 0.14, fontSize: 6, bold: true, color: 'B07A1E', align: 'center' });
// LLM 에이전트: 모든 단계를 잇는 줄
const AY = LY0 + 4 * (LH + LG) + 0.02;
box(s, LX, AY, 9.0, 0.38, X.ink, 'agent');
T(s, [{ text: 'LLM 에이전트', options: { bold: true, color: X.amber } }, { text: '   6단계 순차 실행, 결과 · 기준 대조 후 다음 단계 · 재설계 지시', options: { color: X.white } }],
  { x: LX + 0.14, y: AY, w: 8.75, h: 0.38, fontSize: 8, valign: 'middle' });
[['근거 DB', '규격 · 측정 논문 · 재료 데이터시트 — 조건마다 출처'], ['자동 검증 관문', '전 단계 결과의 코드 판정 — 외형상 타당해도 미달 시 불합격'], ['물리 모듈', '구조 · 진동 · 열 · 제조 제약 — 낙하 · 피로 · 전자기로 확장']].forEach((b, i) => { const x = 0.5 + i * 3.03;
  box(s, x, AY + 0.45, 2.94, 0.46, X.tint, 'base');
  T(s, [{ text: b[0], options: { bold: true, color: C.text2, breakLine: true } }, { text: b[1], options: { color: C.text1 } }], { x: x + 0.12, y: AY + 0.45, w: 2.75, h: 0.46, fontSize: 7.5, valign: 'middle' }); });
T(s, '빨간 표시 = 핵심 기술 A · B · C · 빈 칸 = 해당 기술 미관여 단계 · 회색 화살표 = 결과 전달 방향', { x: 0.5, y: AY + 0.95, w: 9, h: 0.16, fontSize: 6.5, color: C.accent3 });
}
s.addNotes('가로축: 담당 기술, 세로축: 6단계. 생성 AI는 요구 · 조건 정리와 형상 후보 생성, 물리 AI는 고속 예측 · 탐색, 수치해석은 정밀 계산 · 최적화 · 재검증 담당. LLM 에이전트가 단계를 순차 실행.');

// ---------- 6b. TV 스탠드 실증 (보조: 제품 설계)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '부록' });
s.addText('부록. TV 스탠드 — 외형 유지, 다리 무게 1/3로 경량화', { placeholder: 'title' });
s.addText('65형 TV · 알루미늄 10 mm 판재 다리 · 외곽선 · 5 mm 테두리 고정, 내부 형상만 AI 결정', { placeholder: 'body' });
box(s, 0.5, 1.3, 4.2, 3.45, X.tint, 'tv card');
fit(s, SH + 'v6_c_tv_full.png', 0.6, 1.38, 4.0, 2.55, 'TV on optimized feet');
T(s, '실제 판매 스탠드(동일 모델): 약 1.0 kg, 깊이 279 mm — 무게만 비교 가능, 실제 기준·형상은 확인 필요', { x: 0.65, y: 4.0, w: 3.9, h: 0.65, fontSize: 9, color: C.text2 });
box(s, 4.9, 1.3, 2.25, 2.35, X.tint, 'before'); pill(s, 5.0, 1.38, 1.6, '동일 외형, 꽉 찬 판', X.mute, X.white);
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
s.addNotes('제품 설계 기여 예시: 디자이너가 정한 외형은 유지, 내부만 경량화. 꽉 찬 판은 대부분 저응력(파랑)으로 재료 낭비. AI는 하중 경로인 테두리 · V자 기둥 · 아치만 유지. 실제 판매 스탠드(약 1.0 kg)는 설계 기준 미확인으로 무게만 참고.');

// ---------- 2b. 입력
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '부록' });
s.addText('부록. 입력 → 설계 명세 — 입력 형태와 무관한 공통 명세 형식', { placeholder: 'title' });
s.addText('말 · 특허 문서 · 기존 제품 3D 파일까지 동일 과정으로 처리', { placeholder: 'body' });
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
const spec = [['형상', '지킬 곳 · 비울 곳 · 바꿀 곳'], ['물리 조건', '하중 · 고정 위치 · 재료'], ['판정 기준', '강도 · 진동 · 처짐 + 출처'], ['빠진 조건', 'AI의 사용자 확인 요청']];
spec.forEach((q, i) => {
  const y = 2.1 + i * 0.56;
  T(s, q[0], { x: 6.55, y, w: 1.0, h: 0.45, fontSize: 11, bold: true, color: C.accent2, valign: 'middle' });
  T(s, q[1], { x: 7.55, y, w: 1.9, h: 0.45, fontSize: 10.5, color: C.background1, valign: 'middle' });
});
T(s, '※ 사례별 입력: 자전거 거치대 = 스케치 + 텍스트, TV 스탠드 = 텍스트', { x: 0.5, y: 4.6, w: 9, h: 0.3, fontSize: 9, color: C.accent3 });
s.addNotes('입력 형태 무관. 모든 입력을 공통 형식인 설계 명세(형상 + 물리 조건 + 판정 기준 + 근거)로 변환하면 이후 계산 · 재설계 · 검증은 동일. 특허 문서는 청구항 · 도면에서 구조 · 기능 요구를 추출하여 형상 후보로 변환.');

// ===== v14: 형상이 만들어지는 과정
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '부록' });
s.addText('부록. 자전거 거치대 — 계산 기반 형상 생성 (최적화 과정)', { placeholder: 'title' });
s.addText('설계 공간 전체를 재료로 채운 후, 매 반복 진동 · 폰 온도 · 터치 처짐 계산 → 제약 범위 내 재료 제거', { placeholder: 'body' });
const FW4 = 1.43;
EV4.frames.forEach((f, i) => { const x = 0.5 + i * (FW4 + 0.08), last = i === EV4.frames.length - 1;
  box(s, x, 1.3, FW4, 1.78, last ? 'E3F1F0' : X.tint, 'frame');
  fit(s, SH + f.img, x + 0.05, 1.36, FW4 - 0.1, 1.05, 'iteration ' + f.it);
  T(s, i === 0 ? '시작' : last ? `최종 (${f.it + 1}회)` : `${f.it}회`, { x: x + 0.08, y: 2.43, w: FW4 - 0.16, h: 0.22, fontSize: 9.5, bold: true, color: C.text2 });
  T(s, `${f.mass} g · ${f.f1} Hz`, { x: x + 0.08, y: 2.67, w: FW4 - 0.16, h: 0.22, fontSize: 9, bold: true, color: last ? C.accent1 : C.accent3 });
  if (!last) arrow(s, x + FW4 - 0.02, 1.85, 0.11, 0.18); });
s.addChart(pres.charts.LINE, [{ name: '무게 (g)', labels: EV4.it.map(String), values: EV4.mass }], {
  x: 0.45, y: 3.15, w: 4.5, h: 1.75, chartColors: [X.teal], lineSize: 2, lineDataSymbol: 'none', showLegend: false, showTitle: true, title: '무게 (g) — 반복에 따른 감소', titleFontSize: 9, titleColor: X.ink, titleFontFace: '+mn-lt',
  catAxisLabelColor: X.mute, valAxisLabelColor: X.mute, catAxisLabelFontSize: 7, valAxisLabelFontSize: 7, catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt',
  valGridLine: { color: 'DDE5E4', size: 0.5 }, catGridLine: { style: 'none' }, catAxisLabelFrequency: 5, catAxisLabelRotate: 0, valAxisMinVal: 0 });
s.addChart(pres.charts.LINE, [{ name: '1차 진동수', labels: EV4.it.map(String), values: EV4.f1 }, { name: '하한', labels: EV4.it.map(String), values: EV4.it.map(() => 95) }], {
  x: 4.95, y: 3.15, w: 2.6, h: 1.75, chartColors: [X.amber, X.red], lineSize: 2, lineDataSymbol: 'none', showLegend: false, showTitle: true, title: '1차 진동수 (Hz) — 목표 95 (축소 형상 기준)', titleFontSize: 9, titleColor: X.ink, titleFontFace: '+mn-lt',
  catAxisLabelColor: X.mute, valAxisLabelColor: X.mute, catAxisLabelFontSize: 7, valAxisLabelFontSize: 7, catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt',
  valGridLine: { color: 'DDE5E4', size: 0.5 }, catGridLine: { style: 'none' }, catAxisLabelFrequency: 10, catAxisLabelRotate: 0, valAxisMinVal: 60, valAxisMaxVal: 180 });
[['1', '설계 공간', '클램프 · 걸이 · 집게 하우징 · 레일은 고정'], ['2', '매 반복 계산', '폰을 관성 포함 강체로 반영, 진동 모드 · 민감도 계산'], ['3', '재료 재배치', '진동 · 온도 · 터치 제약 하 무게 최소화'], ['4', '두께 제약', '제작 오차만큼 축소해도 성능 유지']].forEach((h, i) => { const y = 3.2 + i * 0.43;
  disc(s, 7.68, y + 0.02, 0.26, X.teal, null, 'step');
  T(s, h[0], { x: 7.68, y: y + 0.02, w: 0.26, h: 0.26, fontSize: 9, bold: true, color: C.background1, align: 'center', valign: 'middle' });
  T(s, h[1], { x: 8.02, y, w: 1.55, h: 0.18, fontSize: 8.5, bold: true, color: C.text2 });
  T(s, h[2], { x: 8.02, y: y + 0.18, w: 1.55, h: 0.24, fontSize: 7, color: C.accent3 }); });
T(s, `※ 그림 = 재료 밀도 0.45 이상 영역, 수치 = 최적화 중 2 mm 격자 값(폰 + 고정 부품 311 g, 진동수는 제작 오차만큼 축소한 형상 기준). 출력용 몸체 81.3 g. CPU 2코어 약 ${EV4.minutes}분`, { x: 0.5, y: 4.95, w: 9, h: 0.22, fontSize: 7.5, color: C.accent3 });
s.addNotes('사전에 정한 형상이 아닌, 계산으로 재료를 제거하며 도출한 형상. 매 반복 폰의 무게 · 회전 관성을 포함해 진동 계산, 1차 진동수를 길 진동(중앙 34.6~45.6 Hz)보다 높게, 폰 온도 상승 21 °C 이하, 터치 처짐 0.3 mm 이하로 유지하며 기여도 낮은 재료 제거. 폰 고정부(걸이 · 집게 하우징 · 레일)는 고정, 그 사이를 잇는 삼각 프레임이 잔존. 진동수 곡선은 제작 오차만큼 축소한 형상 기준으로, 실제 출력 형상은 154–168 Hz.');

// ===== v15: 일체형 — 물리 검증이 쓸 수 없는 형상을 걸러냄
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '부록' });
s.addText('부록. 자전거 거치대 — 검토 발견 문제의 계산 확인 및 재설계', { placeholder: 'title' });
s.addText('1차 결과에 폰 고정 형상이 없음을 검토에서 발견 → 충격 계산으로 확인 → 4면 고정 재설계 · 검증 항목에 추가', { placeholder: 'body' });
box(s, 0.5, 1.28, 3.0, 3.3, X.tint, 'nogrip card');
pill(s, 0.62, 1.36, 1.05, '1차 결과', X.mute, X.white);
fit(s, SH + 'v15_nogrip.png', 0.6, 1.72, 2.8, 2.2, 'no grip');
T(s, '폰이 판에 부착된 것으로 가정 —\n옆면 · 앞면 고정 형상 부재', { x: 0.62, y: 3.98, w: 2.76, h: 0.5, fontSize: 9, color: C.text1, align: 'center' });
box(s, 3.65, 1.28, 2.7, 3.3, 'FFFFFF', 'force card');
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 3.65, y: 1.28, w: 2.7, h: 3.3, rectRadius: 0.08, fill: { type: 'none' }, line: { color: X.line, width: 1 } });
T(s, '충격 시 폰 상향 이탈력', { x: 3.77, y: 1.38, w: 2.46, h: 0.26, fontSize: 10, bold: true, color: C.text2 });
const FB = [['이탈력 (상향)', 79, X.red], ['집게 마찰 고정력', 11, X.mute]];
FB.forEach((f, i) => { const y = 1.78 + i * 0.62, bw = 2.2 * f[1] / 85;
  T(s, f[0], { x: 3.77, y, w: 2.4, h: 0.22, fontSize: 8.5, color: C.accent3 });
  s.addShape(pres.shapes.RECTANGLE, { x: 3.77, y: y + 0.24, w: bw, h: 0.2, fill: { color: f[2] }, line: { color: f[2] } });
  T(s, i ? '3 ~ 11 N' : '79 N', { x: 3.82 + bw, y: y + 0.22, w: 0.9, h: 0.24, fontSize: 10, bold: true, color: f[2], valign: 'middle' }); });
T(s, '→ 집게만으로는 폰 상향 이탈\n→ 화면 방향 113 N 작용', { x: 3.77, y: 3.1, w: 2.5, h: 0.5, fontSize: 9, bold: true, color: C.accent1 });
T(s, '해결: 위 · 아래 걸이로 길이 방향 구속, 집게는 잠금 나사로 고정', { x: 3.77, y: 3.72, w: 2.5, h: 0.6, fontSize: 9, color: C.text1 });
box(s, 6.5, 1.28, 3.0, 3.3, 'E3F1F0', 'grip card');
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.5, y: 1.28, w: 3.0, h: 3.3, rectRadius: 0.08, fill: { type: 'none' }, line: { color: X.teal, width: 2 } });
pill(s, 6.62, 1.36, 1.05, '재설계', X.teal, X.white);
fit(s, SH + 'v15_grip.png', 6.6, 1.72, 2.8, 2.2, 'grip');
T(s, '아래 · 위 걸이 + 양옆 스프링 집게\n+ 잠금 나사 — 4면 고정', { x: 6.62, y: 3.98, w: 2.76, h: 0.5, fontSize: 9, bold: true, color: C.accent1, align: 'center' });
T(s, '※ 충격 48.5 g(ISBS 2020 조약돌길) × 폰 290 g = 138 N을 35° 기울기로 나눔: 위쪽 79 N, 화면 쪽 113 N. 버티는 힘 = 마찰계수 0.3 × 스프링 힘 5–18 N × 양쪽 — 마찰계수 · 스프링 힘은 가정(확인 필요)', { x: 0.5, y: 4.68, w: 9, h: 0.4, fontSize: 7.5, color: C.accent3 });
s.addNotes('1차 일체형 결과는 계산상 폰을 판에 부착된 것으로 가정하여 폰 고정 형상 부재. 자동 검증이 아닌 결과 검토 과정에서 발견, 이후 폰 고정 점검을 검증 항목에 추가. 충격 하중의 기울기 방향 분해 시 폰 상향 이탈력 79 N, 스프링 집게 마찰 고정력 3~11 N. 대책: 아래 · 위 걸이로 길이 방향 구속, 양옆 집게 잠금 나사 고정(4면 고정), 해당 부품을 고정 영역으로 반영해 몸체 재최적화.');

// ===== v15: 제작형 결과 — 초기 설계 대비 (같은 걸이 · 집게 · 레일)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '부록' });
s.addText('부록. 자전거 거치대 결과 — 유사 무게에서 흔들림 77% 감소', { placeholder: 'title' });
s.addText('폰 고정 부품 포함 동일 조건에서 초기 설계와 비교 — 출력용 몸체 기준', { placeholder: 'body' });
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
s.addNotes('폰 고정 부품(걸이 · 집게 · 레일) 포함 동일 조건에서 초기 설계와 비교. 초기 설계: 30.5 Hz 공진, 최대 5.6배 흔들림, 폰 온도 32.6 °C 상승. 출력용 몸체: 81.3 g(처음 설계 84.0 g과 유사), 최대 흔들림 1.27배, 온도 상승 20.8 °C, 충격 층간 응력 2.2 MPa. 강도 점검에서 걸이 · 집게 연결부 3곳 보강, 보강 후 전 항목 허용치 이내.');

// ===== v15: 제작 구성
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '부록' });
s.addText('부록. 자전거 거치대 제작 구성 — 출력 4개 + 시판 부품', { placeholder: 'title' });
s.addText('몸체는 최적화 형상 · 레일 · 걸이 일체 출력, 폰 크기 차이는 슬라이드 부품으로 흡수', { placeholder: 'body' });
box(s, 0.5, 1.28, 4.6, 1.75, 'FFFFFF', 'side');
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 1.28, w: 4.6, h: 3.6, rectRadius: 0.06, fill: { type: 'none' }, line: { color: X.line, width: 1 } });
fit(s, SH + 'v15_grip_side.png', 0.6, 1.33, 2.0, 3.5, 'side view');
fit(s, SH + 'v15_jaw.png', 2.65, 1.6, 2.4, 3.0, 'jaw detail');
T(s, '측면', { x: 0.6, y: 4.6, w: 2.0, h: 0.22, fontSize: 8, color: C.accent3, align: 'center' });
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
s.addNotes('출력 부품 4개(몸체 1, 슬라이드 집게 2, 위쪽 걸이 1), 합계 96.8 g. 몸체는 최적화 형상 · 집게 하우징 · 위쪽 레일 · 아래 걸이 일체. 폰 폭 차이는 스프링 집게, 길이 차이는 위쪽 슬라이드 걸이로 흡수. 시판 부품은 스프링 2개와 M3 · M4 나사. 해석과 동일하게 채움 100% 출력. 145 mm 미만 폰은 미대응.');
// ---------- 6c. 무선충전 스탠드 (보조: 물리 확장 — 열)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '부록' });
s.addText('부록. 확장 근거 — 열 물리: 무선충전 스탠드 방열판', { placeholder: 'title' });
s.addText('실제 제품 구조(코일 2개 · 페라이트 · 회로기판) 고정, 알루미늄 방열판 2장 형상만 AI 결정', { placeholder: 'body' });
box(s, 0.5, 1.3, 2.9, 3.5, X.tint, 'product');
fit(s, SH + 'v6_c_wc2_product.png', 0.55, 1.35, 1.4, 2.4, 'stand with phone');
fit(s, SH + 'v6_c_wc2_cut_opt.png', 1.95, 1.35, 1.4, 2.4, 'cutaway');
T(s, '왼쪽: 폰 거치 · 오른쪽: 하우징 투명 처리, 방열판 2장과 회로기판', { x: 0.6, y: 3.8, w: 2.7, h: 0.45, fontSize: 8.5, color: C.text2 });
T(s, '발열(가정): 코일 2.0 W + 구동 소자 1.5 W', { x: 0.6, y: 4.3, w: 2.7, h: 0.4, fontSize: 8.5, bold: true, color: C.accent2 });
box(s, 3.55, 1.3, 2.6, 3.5, X.tint, 'layers');
fit(s, SH + 'v6_wc2_layers.png', 3.6, 1.35, 2.5, 3.0, 'optimized sheets');
T(s, '판 A: 코일 열 → 옆벽 · 판 B: 소자 열 → 뒷벽 전체', { x: 3.65, y: 4.38, w: 2.45, h: 0.38, fontSize: 8.5, color: C.text2 });
fit(s, SH + 'v6_wc2_bars.png', 6.3, 1.3, 3.2, 1.75, 'temperature comparison');
const wk = [['동일 무게 ~25 g', '평판 1장은 한쪽만 냉각(131~147 °C) → AI 배치는 두 곳 모두 70 °C 이하'], ['평판 2장 대비 무게 절반', '코일 쪽 66.5 vs 65.2 °C, 회로 쪽 59.8 vs 44.1 °C']];
wk.forEach((k, i) => { T(s, k[0], { x: 6.35, y: 3.15 + i * 0.75, w: 3.1, h: 0.3, fontSize: 12, bold: true, color: C.accent1 }); T(s, k[1], { x: 6.35, y: 3.45 + i * 0.75, w: 3.1, h: 0.42, fontSize: 8.5, color: C.text1 }); });
T(s, '※ 팬 없는 밀폐 하우징으로는 어떤 배치든 폰 쪽 48 °C 기준 미달 → 실제 제품이 팬을 쓰는 이유와 일치. 주장은 "같은 무게에서 배치 효과". 발열량·열물성·대류 계수 15 W/m²K는 가정, 와전류 미해석', { x: 0.5, y: 4.9, w: 9, h: 0.35, fontSize: 8, color: C.accent3 });
s.addNotes('물리 확장 실증: 구조 방정식 대신 열전도 방정식을 동일 흐름(설계 명세 → 계산 → 최적화 → 검증)에 적용. 절대 온도는 가정에 민감하므로 동일 무게 평판 대비 배치 효과로 주장.');

await pres.writeFile({ fileName: OUT });
await applyTheme(OUT, THEME);
console.log('ok', OUT);
})();