// ===== v85: 핵심 기술 B 상세 — 일체형 기준
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '부록' });
s.addText('부록. 핵심 기술 B 상세 — 형상 AI × 물리 AI × 위상 최적화', { placeholder: 'title' });
s.addText('형상 AI가 일체형 후보를 만들고 물리 AI가 즉시 평가해 미분으로 탐색, 위상 최적화가 제약을 지키며 정밀화한다', { placeholder: 'body' });
{
const CW = 2.9, cardY = 1.28, cardH = 2.62;
const card = (i, t, kind, kc) => { const x = 0.5 + i * (CW + 0.15); box(s, x, cardY, CW, cardH, X.tint, 'ai card');
  T(s, t, { x: x + 0.12, y: cardY + 0.07, w: CW - 0.24, h: 0.26, fontSize: 11, bold: true, color: C.text2 });
  T(s, kind, { x: x + 0.12, y: cardY + 0.33, w: CW - 0.24, h: 0.2, fontSize: 8, bold: true, color: kc }); return x; };
const lines = (x, arr) => T(s, arr.map((a, k) => ({ text: a[0], options: { bold: !!a[1], color: a[1] ? C.text1 : C.accent3, breakLine: k < arr.length - 1 } })), { x: x + 0.12, y: cardY + 1.42, w: CW - 0.24, h: 1.12, fontSize: 8.5, paraSpaceAfter: 2 });
let cx = card(0, '형상 AI — 형상을 잠재 변수로', 'DeepSDF (잠재 변수 32개 → SDF → 3D)', GEN);
fit(s, SH + 'v80_shapes.png', cx + 0.08, cardY + 0.62, CW - 0.16, 0.72, 'shape AI');
lines(cx, [['학습 형상: 일체형 형상 생성기 + 위상 최적화 이력 245개', 1], ['생성기는 규칙으로 계열을 넓히고, 이력은 최종 설계 근처를 채운다', 0], ['합격 기준: 학습 형상 재구성 IoU ≥ 0.8', 1], ['입력 격자 88 × 20 × 37 (2 mm, 폰 기준 35° 좌표)', 0]]);
cx = card(1, '물리 AI — 형상 → 성능과 분포', '3D 신경 연산자 (FNO) · 기준 모델 3D CNN', C.accent1);
// 입출력 도식
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx + 0.14, y: cardY + 0.66, w: 0.78, h: 0.62, rectRadius: 0.04, fill: { color: 'FFFFFF' }, line: { color: GEN, width: 1 } });
T(s, [{ text: '형상', options: { bold: true, color: GEN, breakLine: true } }, { text: '격자 점유\n65,120칸', options: { fontSize: 6.3, color: C.text1 } }], { x: cx + 0.14, y: cardY + 0.66, w: 0.78, h: 0.62, fontSize: 8, align: 'center', valign: 'middle' });
s.addShape(pres.shapes.LINE, { x: cx + 0.94, y: cardY + 0.97, w: 0.22, h: 0, line: { color: C.accent1, width: 1.25, endArrowType: 'triangle' } });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx + 1.18, y: cardY + 0.62, w: 1.6, h: 0.7, rectRadius: 0.04, fill: { color: 'FFFFFF' }, line: { color: X.teal, width: 1 } });
T(s, [{ text: '값 7개', options: { bold: true, color: X.teal, breakLine: true } }, { text: '질량 · 1 · 2차 진동수 · 폰 온도 상승\n터치 처짐(위 · 아래) · 충격 응력', options: { fontSize: 6, color: C.text1, breakLine: true } }, { text: '분포 2개  ', options: { bold: true, color: X.teal } }, { text: '온도 · 응력', options: { fontSize: 6, color: C.text1 } }], { x: cx + 1.22, y: cardY + 0.62, w: 1.54, h: 0.7, fontSize: 7.5, valign: 'middle' });
lines(cx, [['학습 라벨 = 같은 FEM 엔진이 계산한 값 · 분포', 1], ['진동 · 열 · 처짐 · 충격을 한 번에 예측해 기울기 제공', 0], ['고정 인터페이스: predict(형상) → 값, 분포', 1], ['STEP · 비정형 메시 입력은 GINO로 확장', 0]]);
cx = card(2, '결합 탐색 → 위상 최적화', '미분으로 잠재 변수 조정 → 정밀화', C.accent1);
fit(s, SH + 'v79_evo.png', cx + 0.08, cardY + 0.66, CW - 0.16, 0.62, 'topology evolution');
lines(cx, [['목표 미달 · 질량을 벌점으로 z를 조정 (Adam)', 1], ['후보는 위상 최적화의 시작점 또는 바로 검증으로', 0], ['위상 최적화: 진동 · 열 · 처짐 제약 + 출력 방향 · 최소 두께', 1], ['결과는 다시 물리 AI 학습 데이터로', 0]]);
// 결과 줄
const FL = [['처음 설계 (판 + 기둥)', '94.9 g · 30.5 Hz', X.mute], ['위상 최적화 120회', '진동 · 열 · 처짐 제약', X.teal], ['출력 몸체', '93.9 g · 168 Hz', GEN], ['출력 형상 재검증', '충격 · 열 · 처짐 합격', X.green]];
FL.forEach((f, i) => { const x = 0.5 + i * 2.32;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 4.02, w: 2.05, h: 0.62, rectRadius: 0.06, fill: { color: 'FFFFFF' }, line: { color: f[2], width: 1.5 }, objectName: 'flow box' });
  T(s, f[0], { x: x + 0.08, y: 4.06, w: 1.9, h: 0.24, fontSize: 8.5, color: C.accent3, align: 'center' });
  T(s, f[1], { x: x + 0.08, y: 4.3, w: 1.9, h: 0.3, fontSize: 11, bold: true, color: f[2], align: 'center' });
  if (i < 3) arrow(s, x + 2.08, 4.2, 0.2, 0.26); });
T(s, '※ 같은 조건(폰 311 g 강체, 2 mm 격자 FEM, 3% 감쇠)으로 계산. 출력 몸체 93.9 g은 계산 격자 기준, 출력 STL은 81.3 g', { x: 0.5, y: 4.72, w: 9, h: 0.3, fontSize: 7.5, color: C.accent3 });
}
s.addNotes('형상 AI(DeepSDF)는 일체형 형상 생성기 형상과 위상 최적화 이력 245개로 학습해 형상을 잠재 변수 32개로 표현한다. 물리 AI는 같은 FEM 엔진이 만든 라벨로 학습해 형상에서 질량 · 진동수 · 온도 · 처짐 · 충격 응력과 온도 · 응력 분포를 예측하고 기울기를 준다. 둘을 이어 잠재 변수를 미분으로 조정해 후보를 찾고, 위상 최적화가 제약을 지키며 정밀화한다. 처음 설계 94.9 g · 30.5 Hz에서 출력 몸체 93.9 g · 168 Hz.');
