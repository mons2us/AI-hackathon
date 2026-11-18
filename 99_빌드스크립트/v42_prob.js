// ---------- 3. 문제 정의 (v42: 왜 이 과제를 했나 — 배경 → 문제 → 그래서)
pres.addSection({ title: '1. 문제 정의' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '1. 문제 정의' });
s.addText('1. 문제 정의 — 형상은 AI가 만들지만, 작동하는지는 확인되지 않는다', { placeholder: 'title' });
s.addText('제품이 되려면 성능 검증을 통과해야 하는데, 이 관문은 여전히 전문가 몫이고 생성 AI는 대신하지 못한다', { placeholder: 'body' });
{ const PY = 1.3, PH = 3.42;
const panel = (x, w, tag, tagc, head, fill, line) => {
  box(s, x, PY, w, PH, fill, 'panel');
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: PY, w, h: PH, rectRadius: 0.08, fill: { type: 'none' }, line: { color: line, width: 0.75 }, objectName: 'panel frame' });
  box(s, x + 0.14, PY + 0.14, 0.78, 0.26, tagc, 'tag');
  T(s, tag, { x: x + 0.14, y: PY + 0.14, w: 0.78, h: 0.26, fontSize: 8.5, bold: true, color: X.white, align: 'center', valign: 'middle' });
  T(s, head, { x: x + 0.14, y: PY + 0.46, w: w - 0.28, h: 0.62, fontSize: 11.5, bold: true, color: C.text2, valign: 'top' }); };
const arrow = x => s.addShape(pres.shapes.CHEVRON, { x: x - 0.01, y: PY + PH / 2 - 0.15, w: 0.14, h: 0.3, fill: { color: X.mute }, line: { color: X.mute }, objectName: 'arrow' });
// A. 지금 (배경)
const AX = 0.5, AW = 2.55;
panel(AX, AW, '지금', X.mute, '말 한 줄이면 생성 AI가 3D 형상을 바로 그려 준다', 'FFFFFF', X.line);
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: AX + 0.14, y: PY + 1.14, w: AW - 0.28, h: 1.0, rectRadius: 0.04, fill: { color: 'FFFFFF' }, line: { color: X.line, width: 0.5 }, objectName: 'img' });
fit(s, SH + 'v38_L3.png', AX + 0.16, PY + 1.16, AW - 0.32, 0.96, '범용 LLM이 그린 거치대');
T(s, '"울퉁불퉁한 길에서도 안 흔들리게, 가볍게" → 범용 LLM이 바로 설계한 자전거 폰 거치대', { x: AX + 0.14, y: PY + 2.2, w: AW - 0.28, h: 0.44, fontSize: 8, color: C.accent3 });
T(s, '아이디어를 형상으로 바꾸는 일은 이미 쉬워졌다', { x: AX + 0.14, y: PY + 2.8, w: AW - 0.28, h: 0.5, fontSize: 9.5, bold: true, color: C.text2, valign: 'middle' });
arrow(AX + AW + 0.02);
// B. 문제
const BX = AX + AW + 0.15, BW2 = 3.6;
panel(BX, BW2, '문제', X.red, '그 형상이 버티는지 · 흔들리지 않는지는 모른 채 나온다', 'FBF1EF', 'E5B8B2');
const EV = [
  { k: '생성 AI', big: '1.3배 → 6.6배', d: '스스로 예측한 흔들림 vs 실제 계산\n같은 요청 3회 모두 불합격, 틀려도 그대로 제시' },
  { k: '기존 방식', big: '67% · 45%', d: '외부 해석 결과까지 1주 이상 · 일정 때문에 해석 생략\n검증은 전문가와 시간이 있어야 가능' }];
EV.forEach((e, i) => { const y = PY + 1.12 + i * 0.86;
  box(s, BX + 0.14, y, BW2 - 0.28, 0.78, 'FFFFFF', 'ev');
  T(s, e.k, { x: BX + 0.24, y: y + 0.06, w: 0.9, h: 0.22, fontSize: 8, bold: true, color: C.accent3 });
  T(s, e.big, { x: BX + 0.24, y: y + 0.28, w: 1.5, h: 0.42, fontSize: 13.5, bold: true, color: C.accent5, valign: 'middle' });
  T(s, e.d, { x: BX + 1.78, y: y + 0.08, w: BW2 - 1.98, h: 0.64, fontSize: 7.5, color: C.text1, valign: 'middle' }); });
T(s, '결과: 만들어 보고 고치기를 반복하거나, 확인할 방법이 없어 아이디어 단계에서 멈춘다', { x: BX + 0.14, y: PY + 2.88, w: BW2 - 0.28, h: 0.44, fontSize: 9.5, bold: true, color: C.accent5, valign: 'middle' });
arrow(BX + BW2 + 0.02);
// C. 그래서 (해결 방향)
const CX = BX + BW2 + 0.15, CWd = 2.55;
panel(CX, CWd, '그래서', X.teal, '형상을 만드는 그 자리에서 물리로 확인하고 고친다', X.tint, X.line);
['요청을 하중 · 고정 · 목표 같은 물리 조건으로 바꾼다', '계산으로 판정하고, 기준 미달이면 형상을 다시 짠다', '통과한 설계만 도면 · 제작 파일로 내보낸다'].forEach((t, i) => { const y = PY + 1.14 + i * 0.52;
  s.addShape(pres.shapes.OVAL, { x: CX + 0.16, y: y + 0.06, w: 0.24, h: 0.24, fill: { color: X.teal }, line: { color: X.teal }, objectName: 'n' });
  T(s, String(i + 1), { x: CX + 0.16, y: y + 0.06, w: 0.24, h: 0.24, fontSize: 8.5, bold: true, color: X.white, align: 'center', valign: 'middle' });
  T(s, t, { x: CX + 0.48, y, w: CWd - 0.6, h: 0.46, fontSize: 8.5, color: C.text1, valign: 'middle' }); });
box(s, CX + 0.14, PY + 2.82, CWd - 0.28, 0.5, X.ink, 'fp');
T(s, [{ text: 'FormProof', options: { bold: true, color: C.accent4 } }, { text: '  성능이 확인된 · 만들 수 있는 설계까지', options: { color: X.white } }], { x: CX + 0.2, y: PY + 2.82, w: CWd - 0.4, h: 0.5, fontSize: 9, valign: 'middle' });
T(s, '※ 생성 AI: 도구 없이 같은 요청 · 같은 조건을 받은 독립 세션 3회를 같은 해석기로 판정(17쪽). 기존 방식: engineering.com · Dassault 「State of Simulation, Prototyping and Validation」(엔지니어 268명, 연도 확인 필요) — 해외 업계 조사 · 해석 SW사 후원', { x: 0.5, y: 4.82, w: 9, h: 0.3, fontSize: 6.5, color: C.accent3 });
}
s.addNotes('이 과제를 시작한 이유. 지금은 말 한 줄이면 생성 AI가 3D 형상을 그려 준다 — 실제로 범용 LLM에게 자전거 폰 거치대를 요청하면 그럴듯한 형상이 바로 나온다. 문제는 그 형상이 실제로 버티는지, 흔들리지 않는지 모른 채 나온다는 것. LLM은 흔들림이 1.3배일 거라 했지만 실제 계산은 6.6배였고, 3번 모두 기준 미달이었는데 틀렸다는 표시 없이 그대로 제시됐다. 이걸 확인하는 기존 방식은 전문가의 해석인데, 전문 조직에서도 67%가 결과를 1주 넘게 기다리고 45%는 일정 때문에 생략한다. 그래서 만들어 보고 고치기를 반복하거나, 확인할 방법이 없어 아이디어에서 멈춘다. 그래서 우리는 형상을 만드는 그 자리에서 물리로 확인하고 고치는 방법, FormProof를 만들었다.');
