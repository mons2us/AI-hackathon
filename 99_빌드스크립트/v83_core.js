// ===== v83: 핵심 기술 3가지 — 한 장 (상세는 부록)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 핵심 기술 — 세 가지가 있어 처음부터 끝까지 AI가 잇는다', { placeholder: 'title' });
s.addText('기존 기술이 사람에게 넘기던 어려운 칸(조건 설정 · 재설계 · 재검증)을 각각 하나씩 맡는다', { placeholder: 'body' });
{
const CO = [
  { no: '①', name: '말 → 물리 조건', col: GEN, img: 'v32_spec.png', before: '조건 설정은 전문가 몫, 범용 LLM은 기준을 스스로 지어냄',
    how: ['LLM은 뜻만 해석, 계산하지 않음', '수치는 근거 DB에서만 · 항목마다 출처', '근거가 없으면 사용자에게 질문'],
    big: '0개', bigd: '출처 없는 수치 — 근거 DB · 요청 · 가정 · 질문 중 하나로 표시' },
  { no: '②', name: '형상 AI × 물리 AI 역설계', col: X.teal, img: 'v80_shapes.png', img2: 'v77_parity.png', before: '형상은 사람이 그리고, 물리 AI는 주어진 틀 안에서만 최적화',
    how: ['형상 AI(DeepSDF)가 형상을 잠재 변수로 표현', '물리 AI가 0.2초에 성능 · 기울기 예측', '미분으로 목표 성능 쪽 형상을 탐색 → 수치해석이 정밀화'],
    big: '39초', bigd: '데이터 최선보다 11% 가벼운 후보 (물리 AI 오차 6.9%)' },
  { no: '③', name: '출력 형상 재검증', col: '5B6B78', img: 'v74_verify.png', before: '최적화 결과와 실제 출력 형상이 달라도 확인하지 않음',
    how: ['제조 조건(최소 두께 · 층간 · 고정 부품)을 넣어 계산', '출력할 STL을 다시 격자화해 FEM 재계산', '기준 미달이면 미달 항목과 함께 재설계로'],
    big: '4건', bigd: '그럴듯해 보였지만 걸러내 다시 설계한 결과' }];
const CW = 2.93, G = 0.1, Y = 1.2, H = 3.5;
CO.forEach((c, i) => { const x = 0.5 + i * (CW + G);
  box(s, x, Y, CW, H, 'FFFFFF', 'core card');
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: Y, w: CW, h: H, rectRadius: 0.08, fill: { type: 'none' }, line: { color: c.col, width: 1.25 }, objectName: 'frame' });
  s.addShape(pres.shapes.OVAL, { x: x + 0.12, y: Y + 0.12, w: 0.34, h: 0.34, fill: { color: X.red }, line: { color: X.white, width: 1 }, objectName: 'no' });
  T(s, c.no, { x: x + 0.12, y: Y + 0.12, w: 0.34, h: 0.34, fontSize: 11, bold: true, color: X.white, align: 'center', valign: 'middle' });
  T(s, c.name, { x: x + 0.52, y: Y + 0.1, w: CW - 0.6, h: 0.38, fontSize: 11.5, bold: true, color: c.col, valign: 'middle' });
  T(s, [{ text: '기존  ', options: { bold: true, color: X.red } }, { text: c.before, options: { color: C.accent3 } }], { x: x + 0.12, y: Y + 0.52, w: CW - 0.24, h: 0.36, fontSize: 7.5 });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.12, y: Y + 0.92, w: CW - 0.24, h: 0.82, rectRadius: 0.04, fill: { color: X.tint }, line: { color: X.tint }, objectName: 'img' });
  if (c.img2) { fit(s, SH + c.img, x + 0.16, Y + 0.95, (CW - 0.32) * 0.6, 0.76, c.name); fit(s, SH + c.img2, x + 0.16 + (CW - 0.32) * 0.6, Y + 0.95, (CW - 0.32) * 0.4, 0.76, 'parity'); }
  else fit(s, SH + c.img, x + 0.16, Y + 0.95, CW - 0.32, 0.76, c.name);
  c.how.forEach((h, k) => T(s, [{ text: '▸ ', options: { color: c.col, bold: true } }, { text: h }], { x: x + 0.12, y: Y + 1.82 + k * 0.3, w: CW - 0.24, h: 0.3, fontSize: 7.8, color: C.text1, valign: 'middle' }));
  s.addShape(pres.shapes.LINE, { x: x + 0.12, y: Y + 2.78, w: CW - 0.24, h: 0, line: { color: X.line, width: 0.75 } });
  T(s, c.big, { x: x + 0.12, y: Y + 2.82, w: 1.15, h: 0.6, fontSize: 20, bold: true, color: c.col, valign: 'middle' });
  T(s, c.bigd, { x: x + 1.28, y: Y + 2.82, w: CW - 1.4, h: 0.6, fontSize: 7.5, color: C.text1, valign: 'middle' }); });
box(s, 0.5, 4.8, 9.0, 0.36, X.ink, 'sum');
T(s, [{ text: '①이 조건을 세우면 ②가 형상을 찾고 ③이 출력 형상으로 판정한다  ', options: { bold: true, color: X.white } }, { text: '— 범용 LLM 단독은 이 셋이 없어 같은 조건 3회 모두 불합격', options: { color: C.accent4 } }],
  { x: 0.65, y: 4.8, w: 8.7, h: 0.36, fontSize: 8.5, valign: 'middle' });
}
s.addNotes('핵심 기술 세 가지를 한 장에. ① 말을 물리 조건으로: LLM은 뜻만 해석하고 수치는 근거 DB에서만, 출처가 없으면 묻는다. ② 형상 AI × 물리 AI 역설계: 형상 AI가 형상을 잠재 변수로, 물리 AI가 0.2초에 성능과 기울기를 주어 미분으로 탐색, 39초 만에 데이터 최선보다 11% 가벼운 후보(거치대 계열 학습 결과). ③ 출력 형상 재검증: 출력할 STL을 다시 계산해 기준 미달을 걸러낸다(이번 작업에서 4건). 세부 내용은 부록.');

