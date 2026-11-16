// ---------- 3. 문제 정의 (v43: 공감 — 바로 만들어 보고 싶었던 적 없나요?)
pres.addSection({ title: '1. 문제 정의' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '1. 문제 정의' });
s.addText('1. 문제 정의 — 좋은 아이디어, 바로 만들어 보고 싶었던 적 없나요?', { placeholder: 'title' });
s.addText('떠올리는 건 누구나 한다. 그런데 "정말 되는지" 확인하는 길에서 대부분의 아이디어가 멈춘다', { placeholder: 'body' });
{
const I3 = { bike: await icon(fa.FaBicycle, X.white), bulb: await icon(fa.FaLightbulb, X.white), pen: await icon(fa.FaPencilRuler, X.white),
  wall: await icon(fa.FaTimesCircle, X.red), box: await icon(fa.FaArchive, X.mute) };
// ① 떠오른다 — 말풍선 3개
const BB = [
  [I3.bike, '자전거 타는 직원', '"길이 울퉁불퉁하면 폰이 떨려서 지도가 안 보여. 차라리 내가 만들어 볼까?"'],
  [I3.bulb, '특허 아이디어가 있는 연구원', '"이 구조면 분명 더 튼튼할 것 같은데, 효과가 있다는 걸 보여 줄 방법이 없네"'],
  [I3.pen, '제품을 기획하는 사람', '"더 얇게 하고 싶은데, 이 두께로 버틸까? 해석 결과는 다음 주에나 나온대"']];
BB.forEach((b, i) => { const x = 0.5 + i * 3.05, y = 1.24, W = 2.9;
  s.addShape(pres.shapes.OVAL, { x, y: y + 0.08, w: 0.44, h: 0.44, fill: { color: X.amber }, line: { color: X.amber }, objectName: 'persona' });
  s.addImage({ data: b[0], x: x + 0.1, y: y + 0.18, w: 0.24, h: 0.24 });
  s.addShape(pres.shapes.WEDGE_ROUND_RECT_CALLOUT || pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.56, y, w: W - 0.56, h: 0.8, fill: { color: 'FDF6EA' }, line: { color: 'F0D9AE', width: 0.75 }, rectRadius: 0.08, objectName: 'bubble' });
  T(s, b[1], { x: x + 0.66, y: y + 0.06, w: W - 0.74, h: 0.2, fontSize: 7, bold: true, color: 'B07A1E' });
  T(s, b[2], { x: x + 0.66, y: y + 0.26, w: W - 0.74, h: 0.5, fontSize: 8.5, italic: true, color: C.text2, valign: 'middle' }); });
// ② 그런데 현실은 — 계단식 벽
T(s, '그런데 현실은', { x: 0.5, y: 2.16, w: 3, h: 0.26, fontSize: 10.5, bold: true, color: C.accent5 });
const WL = [
  ['3D로 옮기려니', 'CAD를 다룰 줄 모른다', ''],
  ['버틸지 확인하려니', '해석은 전문가 몫, 기다려야 한다', '67%  외부 해석 결과까지 1주 이상'],
  ['AI에게 맡겨 보니', '그럴듯한 형상, 그런데 틀렸다', '1.3배라더니 실제 6.6배 흔들림'],
  ['그냥 만들어 보니', '깨지고, 흔들리고, 다시 만든다', '45%  일정 때문에 해석 생략']];
WL.forEach((w, i) => { const x = 0.5 + i * 1.98, y = 2.46 + i * 0.1, W = 1.88, H = 1.28 - i * 0.1;
  box(s, x, y, W, H, i === 2 ? 'FBF1EF' : 'F4F5F6', 'wall');
  s.addImage({ data: I3.wall, x: x + 0.1, y: y + 0.1, w: 0.2, h: 0.2 });
  T(s, w[0], { x: x + 0.36, y: y + 0.08, w: W - 0.42, h: 0.24, fontSize: 8, color: C.accent3, valign: 'middle' });
  T(s, w[1], { x: x + 0.1, y: y + 0.36, w: W - 0.2, h: 0.42, fontSize: 9.5, bold: true, color: C.text2 });
  if (w[2]) T(s, w[2], { x: x + 0.1, y: y + H - 0.4, w: W - 0.2, h: 0.32, fontSize: 7.5, bold: true, color: C.accent5, valign: 'bottom' }); });
// 끝: 서랍 속으로
box(s, 8.44, 2.86, 1.06, 0.78, 'E9EBED', 'drawer');
s.addImage({ data: I3.box, x: 8.82, y: 2.92, w: 0.3, h: 0.3 });
T(s, '아이디어는\n서랍 속으로', { x: 8.44, y: 3.22, w: 1.06, h: 0.4, fontSize: 8, bold: true, color: C.accent3, align: 'center' });
// ③ 이게 해결된다면
box(s, 0.5, 3.92, 9.0, 0.9, X.ink, 'wish');
T(s, '이게 해결된다면', { x: 0.68, y: 3.98, w: 3, h: 0.26, fontSize: 10, bold: true, color: C.accent4 });
T(s, [{ text: '말 한 줄 · 스케치 한 장', options: { bold: true, color: X.white } }, { text: '  →  ', options: { color: C.accent4 } },
  { text: '버티는지 · 흔들리지 않는지 확인된 설계', options: { bold: true, color: X.white } }, { text: '  →  ', options: { color: C.accent4 } },
  { text: '오늘 바로 출력해서 써 본다', options: { bold: true, color: X.amber } }], { x: 0.68, y: 4.24, w: 8.7, h: 0.3, fontSize: 12.5, valign: 'middle' });
T(s, '특허 아이디어는 "될 것 같다"가 아니라 계산된 성능으로, 제품 아이디어는 기다림 없이 그 자리에서 확인한다', { x: 0.68, y: 4.54, w: 8.7, h: 0.24, fontSize: 9, color: C.accent4 });
T(s, '※ 말풍선은 흔히 겪는 상황을 보여 주는 예시. 6.6배 · 1.3배: 범용 LLM 단독 독립 3회를 같은 해석기로 판정(17쪽). 67% · 45%: engineering.com · Dassault 「State of Simulation, Prototyping and Validation」(엔지니어 268명, 연도 확인 필요, 해석 SW사 후원)', { x: 0.5, y: 4.88, w: 9, h: 0.3, fontSize: 6.5, color: C.accent3 });
}
s.addNotes('질문으로 시작한다 — 좋은 아이디어, 바로 만들어 보고 싶었던 적 없나요? 출퇴근길 폰이 떨려 지도가 안 보일 때, 특허 아이디어의 효과를 보여 주고 싶을 때, 더 얇게 만들고 싶은데 버틸지 모를 때. 그런데 현실은 — CAD를 몰라서 막히고, 해석은 전문가에게 맡겨 기다려야 하고(67%가 1주 이상), AI에게 맡기면 그럴듯하지만 틀린다(흔들림 1.3배라더니 실제 6.6배). 결국 만들어 보고 깨지고 다시 만들거나, 아이디어는 서랍 속으로 들어간다. 이게 해결된다면 — 말 한 줄, 스케치 한 장으로 버티는지 확인된 설계를 받아 오늘 바로 출력해 본다. 그걸 만든 것이 FormProof다.');
