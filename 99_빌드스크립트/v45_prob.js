// ---------- 3. 문제 정의 (v45: 공감 + 시각화 — 떠오른다 → 막힌다 → 서랍 속으로 / 이게 된다면)
pres.addSection({ title: '1. 문제 정의' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '1. 문제 정의' });
s.addText('1. 문제 정의 — 좋은 아이디어, 바로 만들어 보고 싶었던 적 없나요?', { placeholder: 'title' });
s.addText('떠올리는 건 누구나 한다. 그런데 "정말 되는지" 확인하는 길에서 대부분의 아이디어가 멈춘다', { placeholder: 'body' });
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
  { img: 'v44_cad.png', q: '3D로 옮기려니', h: 'CAD를 다룰 줄 모른다', e: '도면 · 치수부터 막힘' },
  { ic: 'clock', q: '버틸지 확인하려니', h: '해석은 전문가 몫', big: '67%', ref: '1', e: '결과까지 1주 이상' },
  { img: 'v44_llm.png', q: 'AI에게 맡겨 보니', h: '그럴듯한데 틀렸다', big: '6.6배', ref: '2', e: '흔들림 (AI 예측 1.3배)' },
  { ic: 'redo', q: '그냥 만들어 보니', h: '깨지고 다시 만든다', big: '45%', ref: '1', e: '일정 때문에 해석 생략' }];
const WX = 3.15, WW = 1.17, WG = 0.07;
WL.forEach((w, i) => { const x = WX + i * (WW + WG), y = Y0 + 0.38 + i * 0.07, H = HH - 0.38 - i * 0.07;
  box(s, x, y, WW, H, i === 2 ? 'FBF1EF' : 'F3F4F5', 'wall');
  s.addShape(pres.shapes.RECTANGLE, { x, y, w: WW, h: 0.05, fill: { color: X.red }, line: { color: X.red }, objectName: 'wall top' });
  T(s, w.q, { x: x + 0.08, y: y + 0.1, w: WW - 0.16, h: 0.2, fontSize: 7, color: C.accent3 });
  const iy = y + 0.32;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.08, y: iy, w: WW - 0.16, h: 0.74, rectRadius: 0.03, fill: { color: 'FFFFFF' }, line: { color: X.line, width: 0.5 }, objectName: 'wall img' });
  if (w.img) fit(s, SH + w.img, x + 0.1, iy + 0.02, WW - 0.2, 0.7, w.h);
  else s.addImage({ data: I4[w.ic], x: x + WW / 2 - 0.22, y: iy + 0.15, w: 0.44, h: 0.44 });
  s.addImage({ data: I4.x, x: x + WW - 0.3, y: iy + 0.04, w: 0.18, h: 0.18 });
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
// D. 이게 해결된다면: 스케치 → 물리로 확인된 설계 → 출력
const BY2 = 3.88, BH2 = 0.98;
box(s, 0.5, BY2, 9.0, BH2, X.ink, 'wish');
T(s, '이게 해결된다면', { x: 0.66, y: BY2 + 0.1, w: 2.2, h: 0.26, fontSize: 10.5, bold: true, color: X.amber });
T(s, '특허 아이디어는 "될 것 같다"가 아니라 계산된 성능으로, 제품 아이디어는 기다림 없이 그 자리에서', { x: 0.66, y: BY2 + 0.38, w: 2.4, h: 0.54, fontSize: 8, color: C.accent4, valign: 'top' });
const ST = [['v17_sketch.png', '말 한 줄 · 스케치 한 장'], ['v44_ai.png', '물리로 확인된 설계'], ['v44_body.png', '오늘 출력해서 써 본다']];
ST.forEach((t, i) => { const x = 3.2 + i * 2.1;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: BY2 + 0.1, w: 0.95, h: 0.78, rectRadius: 0.04, fill: { color: 'FFFFFF' }, line: { color: 'FFFFFF' }, objectName: 'wish img' });
  fit(s, SH + t[0], x + 0.03, BY2 + 0.12, 0.89, 0.74, t[1]);
  T(s, t[1], { x: x + 1.0, y: BY2 + 0.1, w: 0.82, h: 0.78, fontSize: 9, bold: true, color: i === 2 ? X.amber : X.white, valign: 'middle' });
  if (i < 2) s.addShape(pres.shapes.CHEVRON, { x: x + 1.88, y: BY2 + 0.36, w: 0.12, h: 0.26, fill: { color: X.amber }, line: { color: X.amber }, objectName: 'arrow' }); });
T(s, [{ text: '1', options: { superscript: true } }, { text: ' engineering.com · Dassault 「State of Simulation, Prototyping and Validation」 2022, 엔지니어 268명 (해석 SW사 후원)     ' },
  { text: '2', options: { superscript: true } }, { text: ' 범용 LLM 단독 독립 3회, 같은 해석기로 판정 (17쪽)', options: { breakLine: true } },
  { text: '※ 한마디는 흔히 겪는 상황의 예시. 그림은 이번 과제의 실제 입력 스케치 · AI 설계(흔들림 분포) · 출력용 몸체' }], { x: 0.5, y: 4.92, w: 9, h: 0.3, fontSize: 6.5, color: C.accent3 });
}
s.addNotes('질문으로 시작한다 — 좋은 아이디어, 바로 만들어 보고 싶었던 적 없나요? 출퇴근길 폰이 떨려 지도가 안 보일 때, 특허 아이디어의 효과를 보여 주고 싶을 때, 더 얇게 만들고 싶은데 버틸지 모를 때. 그런데 현실은 — CAD를 몰라서 막히고, 해석은 전문가에게 맡겨 기다려야 하고(67%가 1주 이상), AI에게 맡기면 그럴듯하지만 틀린다(흔들림 1.3배라더니 실제 6.6배). 결국 만들어 보고 깨지고 다시 만들거나, 아이디어는 서랍 속으로 들어간다. 이게 해결된다면 — 스케치 한 장으로 물리로 확인된 설계를 받아 오늘 바로 출력해 본다. 그걸 만든 것이 FormProof다.');
