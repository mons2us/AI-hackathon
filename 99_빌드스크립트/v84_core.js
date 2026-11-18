// ===== v84: 핵심 기술 A · B · C — 한 장 (작동 방식 + 실제 사례 숫자, 상세는 부록)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 핵심 기술 — 사람이 메우던 세 칸을 AI와 계산이 맡는다', { placeholder: 'title' });
s.addText('A 조건 설정 · B 형상 생성과 재설계 · C 출력 형상 검증 — 셋이 이어져 요구에서 제작 파일까지 끊기지 않는다', { placeholder: 'body' });
{
const CW = 2.93, G = 0.1, Y = 1.2, H = 3.48;
const card = (i, L, name, col, fills) => { const x = 0.5 + i * (CW + G);
  box(s, x, Y, CW, H, 'FFFFFF', 'core');
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: Y, w: CW, h: H, rectRadius: 0.08, fill: { type: 'none' }, line: { color: col, width: 1.25 }, objectName: 'frame' });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.12, y: Y + 0.12, w: 0.34, h: 0.34, rectRadius: 0.06, fill: { color: col }, line: { color: col }, objectName: 'letter' });
  T(s, L, { x: x + 0.12, y: Y + 0.12, w: 0.34, h: 0.34, fontSize: 13, bold: true, color: X.white, align: 'center', valign: 'middle' });
  T(s, name, { x: x + 0.54, y: Y + 0.08, w: CW - 0.6, h: 0.28, fontSize: 11.5, bold: true, color: col, valign: 'middle' });
  T(s, '메우는 칸: ' + fills, { x: x + 0.54, y: Y + 0.34, w: CW - 0.6, h: 0.18, fontSize: 7, color: C.accent3 });
  return x; };
const how = (x, lines, col) => lines.forEach((h, k) => T(s, [{ text: '▸ ', options: { color: col, bold: true } }, { text: h }], { x: x + 0.12, y: Y + 1.92 + k * 0.26, w: CW - 0.24, h: 0.26, fontSize: 7.6, color: C.text1, valign: 'middle' }));
const ev = (x, big, desc, col) => { s.addShape(pres.shapes.LINE, { x: x + 0.12, y: Y + 2.76, w: CW - 0.24, h: 0, line: { color: X.line, width: 0.75 } });
  T(s, big, { x: x + 0.12, y: Y + 2.8, w: 1.1, h: 0.6, fontSize: 19, bold: true, color: col, valign: 'middle' });
  T(s, desc, { x: x + 1.24, y: Y + 2.8, w: CW - 1.36, h: 0.6, fontSize: 7.3, color: C.text1, valign: 'middle' }); };
const pane = (x) => s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.12, y: Y + 0.6, w: CW - 0.24, h: 1.26, rectRadius: 0.04, fill: { color: X.tint }, line: { color: X.tint }, objectName: 'pane' });
// A: 말 → 조건 (변환 예시를 그대로 보여 줌)
let x = card(0, 'A', '말 → 물리 조건', GEN, '물리 조건 (요구 정의 포함)'); pane(x);
[['"안 흔들리게"', '1차 진동수 ≥ 95 Hz', '근거 DB', X.teal], ['"울퉁불퉁한 길"', '충격 48.5 g · ≤ 26 MPa', '근거 DB', X.teal], ['스케치 "35°쯤"', '거치 35°', '질문', X.red]].forEach((r, k) => { const y = Y + 0.68 + k * 0.39;
  T(s, r[0], { x: x + 0.18, y, w: 0.95, h: 0.32, fontSize: 7.5, bold: true, color: C.text2, valign: 'middle' });
  s.addShape(pres.shapes.LINE, { x: x + 1.12, y: y + 0.16, w: 0.14, h: 0, line: { color: GEN, width: 1, endArrowType: 'triangle' } });
  T(s, r[1], { x: x + 1.3, y, w: 0.98, h: 0.32, fontSize: 7, color: C.text1, valign: 'middle' });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 2.28, y: y + 0.08, w: 0.48, h: 0.16, rectRadius: 0.08, fill: { color: r[3] }, line: { color: r[3] } });
  T(s, r[2], { x: x + 2.28, y: y + 0.08, w: 0.48, h: 0.16, fontSize: 5.8, bold: true, color: X.white, align: 'center', valign: 'middle' }); });
how(x, ['LLM은 뜻만 해석, 계산하지 않는다', '수치는 근거 DB에서만, 항목마다 출처', '근거가 없으면 사용자에게 묻는다'], GEN);
ev(x, '6.6배', '조건을 스스로 정한 범용 LLM이 1.3배라 한 흐름림의 실제값 — 이 오류를 구조적으로 막는다', GEN);
// B: 형상 AI × 물리 AI
x = card(1, 'B', '형상 AI × 물리 AI 역설계', X.teal, '3D 형상 생성 · 성능 해석 · 재설계'); pane(x);
fit(s, SH + 'v11_c_C1.png', x + 0.16, Y + 0.64, 1.42, 1.18, 'AI candidate');
fit(s, SH + 'v77_parity.png', x + 1.6, Y + 0.64, 1.17, 1.18, 'parity');
how(x, ['형상 AI(DeepSDF)가 형상을 잠재 변수로 표현', '물리 AI가 0.2초에 성능 · 기울기 (FEM의 1/10)', '미분으로 목표 쪽 탐색 → 위상 최적화가 정밀화'], X.teal);
ev(x, '39초', '데이터 최선 58.3 g보다 11% 가벼운 후보 51.9 g 탐색 (물리 AI 오차 6.9%)', X.teal);
// C: 출력 형상 재검증 (실제로 걸러낸 사례)
x = card(2, 'C', '출력 형상 재검증', '5B6B78', '제작 파일 직전 검증'); pane(x);
[['AI 후보', '물리 AI 예측 91 Hz', C.text2], ['출력 형상 재계산', 'FEM 86 Hz → 미달', X.red], ['재설계 후 출력 몸체', 'FEM 168 Hz → 합격', X.green]].forEach((r, k) => { const y = Y + 0.68 + k * 0.39;
  T(s, r[0], { x: x + 0.18, y, w: 1.15, h: 0.32, fontSize: 7.5, bold: true, color: C.text2, valign: 'middle' });
  T(s, r[1], { x: x + 1.34, y, w: 1.42, h: 0.32, fontSize: 7.5, bold: true, color: r[2], valign: 'middle' });
  if (k < 2) s.addShape(pres.shapes.LINE, { x: x + 0.5, y: y + 0.32, w: 0, h: 0.07, line: { color: X.mute, width: 1, endArrowType: 'triangle' } }); });
how(x, ['제조 조건(최소 두께 · 층간 · 고정 부품)을 넣어 계산', '출력할 STL을 다시 격자화해 FEM으로 재계산', '미달이면 미달 항목과 함께 재설계로 되돌림'], '5B6B78');
ev(x, '4건', '그럴듯해 보였지만 재계산에서 걸러 다시 설계한 결과', '5B6B78');
box(s, 0.5, 4.78, 9.0, 0.36, X.ink, 'sum');
T(s, [{ text: 'A가 조건을 세우면 B가 형상을 찾고 C가 출력 형상으로 판정한다  ', options: { bold: true, color: X.white } }, { text: '— 범용 LLM 단독은 이 셋이 없어 같은 조건 3회 모두 불합격', options: { color: C.accent4 } }],
  { x: 0.65, y: 4.78, w: 8.7, h: 0.36, fontSize: 8.5, valign: 'middle' });
T(s, '※ B의 39초 · 11% · 6.9% · 91/86 Hz = 거치대 계열 학습 · 탐색 결과. 168 Hz = 최종 출력 몸체(폰 311 g) 재계산', { x: 0.5, y: 5.16, w: 9, h: 0.14, fontSize: 6, color: C.accent3 });
}
s.addNotes('핵심 기술 A · B · C. A 말을 물리 조건으로: 표현마다 판정 지표와 근거를 붙이고 근거가 없으면 묻는다. 범용 LLM은 조건을 스스로 정하고 어림해 흔들림을 1.3배로 예측했지만 실제는 6.6배였다. B 형상 AI × 물리 AI: 형상 AI가 형상을 잠재 변수로, 물리 AI가 0.2초에 성능과 기울기를 주어 39초 만에 데이터 최선보다 11% 가벼운 후보를 찾았다. C 출력 형상 재검증: 그 AI 후보는 물리 AI가 91 Hz로 예측했지만 출력 형상 재계산에서 86 Hz로 미달 판정되어 재설계했다. 최종 출력 몸체는 168 Hz로 합격. 세부는 부록.');

