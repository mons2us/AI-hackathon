// ===== v134: 핵심 기술 — 구조도 중심 (기술명 · 아키텍처, 숫자 최소화)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 제안 아이디어' });
s.addText('2. 핵심 기술 — 조건 정의 · 역설계 · 자동 검증 루프', { placeholder: 'title' });
s.addText('LLM + 근거 DB  ·  DeepSDF + 신경 연산자 + 위상 최적화  ·  FEM 자동 판정 폐루프', { placeholder: 'body' });
{
const CW = 2.93, G = 0.1, Y = 1.2, H = 3.5, BL = '1428A0', SL = '46536A';
const card = (i, L, name, col) => { const x = 0.5 + i * (CW + G);
  box(s, x, Y, CW, H, 'FFFFFF', 'core');
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: Y, w: CW, h: H, rectRadius: 0.08, fill: { type: 'none' }, line: { color: col, width: 1.25 }, objectName: 'frame' });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.12, y: Y + 0.12, w: 0.34, h: 0.34, rectRadius: 0.06, fill: { color: col }, line: { color: col }, objectName: 'letter' });
  T(s, L, { x: x + 0.12, y: Y + 0.12, w: 0.34, h: 0.34, fontSize: 13, bold: true, color: X.white, align: 'center', valign: 'middle' });
  T(s, name, { x: x + 0.54, y: Y + 0.12, w: CW - 0.6, h: 0.34, fontSize: 12, bold: true, color: col, valign: 'middle' });
  return x; };
const blk = (x, y, w, h, t1, t2, col, o = {}) => {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.04, fill: { color: o.fill || 'FFFFFF' }, line: { color: col, width: o.lw || 1 }, objectName: 'blk' });
  let tx = x, tw = w;
  if (o.img) { fit(s, SH + o.img, x + 0.04, y + 0.03, o.iw, h - 0.06, t1); tx = x + o.iw + 0.06; tw = w - o.iw - 0.08; }
  T(s, [{ text: t1, options: { bold: true, color: o.tc || col, breakLine: !!t2 } }].concat(t2 ? [{ text: t2, options: { fontSize: 6.3, color: C.text1 } }] : []),
    { x: tx, y, w: tw, h, fontSize: o.fs || 8, align: o.img ? 'left' : 'center', valign: 'middle' }); };
const dn = (x, y, h, col) => s.addShape(pres.shapes.LINE, { x, y, w: 0, h, line: { color: col || X.mute, width: 1.25, endArrowType: 'triangle' }, objectName: 'arr' });
const chips = (x, arr, col) => { let cx = x + 0.12; arr.forEach(c => { const w = 0.1 + c.length * 0.075;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx, y: Y + 2.86, w, h: 0.22, rectRadius: 0.11, fill: { color: col }, line: { color: col }, objectName: 'chip' });
  T(s, c, { x: cx, y: Y + 2.86, w, h: 0.22, fontSize: 6.8, bold: true, color: X.white, align: 'center', valign: 'middle' }); cx += w + 0.05; }); };
const eff = (x, t, col) => T(s, t, { x: x + 0.12, y: Y + 3.12, w: CW - 0.24, h: 0.3, fontSize: 8.5, bold: true, color: col, valign: 'middle' });
// A
let x = card(0, 'A', '근거 기반 물리 조건 정의', BL);
blk(x + 0.15, Y + 0.6, CW - 0.3, 0.44, '입력', '"안 흔들리게, 최대한 가볍게" + 스케치', SL, { img: 'v17_sketch.png', iw: 0.62 });
dn(x + CW / 2, Y + 1.04, 0.1);
blk(x + 0.15, Y + 1.14, CW - 0.3, 0.42, 'LLM — 의미 해석', '표현 → 물리량 (수치 계산은 하지 않음)', BL);
dn(x + CW / 2, Y + 1.56, 0.1);
blk(x + 0.15, Y + 1.66, CW - 0.3, 0.42, '근거 DB 검색', '규격 · 실측 논문 · 재료 데이터시트', BL);
dn(x + CW / 2, Y + 2.08, 0.1);
blk(x + 0.15, Y + 2.18, CW - 0.3, 0.52, '설계 사양 (JSON)', '하중 · 기준 · 재료, 항목별 출처\n스키마 검증 · 빠진 값은 사용자에게 질문', BL, { fill: 'EEF2FB', lw: 1.5 });
chips(x, ['LLM', '근거 DB 검색', 'JSON 스키마'], BL);
eff(x, '모든 수치에 출처 — 근거가 없으면 묻는다', BL);
// B
x = card(1, 'B', '물리 기반 역설계 엔진', BL);
blk(x + 0.15, Y + 0.6, 1.24, 0.98, '', '', '4F6BD8');
fit(s, SH + 'v87_gen_grid.png', x + 0.19, Y + 0.64, 1.16, 0.5, 'DeepSDF');
T(s, [{ text: '형상 AI', options: { bold: true, color: '4F6BD8', breakLine: true } }, { text: 'DeepSDF: z → SDF → 3D', options: { fontSize: 6.3, color: C.text1 } }], { x: x + 0.15, y: Y + 1.14, w: 1.24, h: 0.42, fontSize: 8, align: 'center', valign: 'middle' });
blk(x + 1.54, Y + 0.6, 1.24, 0.98, '', '', BL);
fit(s, SH + 'v125_phys_fields.png', x + 1.58, Y + 0.64, 1.16, 0.36, 'neural operator');
T(s, [{ text: '물리 AI', options: { bold: true, color: BL, breakLine: true } }, { text: '신경 연산자 (GINO · FNO)\n형상 → 응력 · 온도 분포', options: { fontSize: 6.3, color: C.text1 } }], { x: x + 1.54, y: Y + 1.0, w: 1.24, h: 0.56, fontSize: 8, align: 'center', valign: 'middle' });
s.addShape(pres.shapes.LINE, { x: x + 1.39, y: Y + 0.86, w: 0.15, h: 0, line: { color: SL, width: 1, endArrowType: 'triangle' } });
s.addShape(pres.shapes.LINE, { x: x + 1.39, y: Y + 1.18, w: 0.15, h: 0, flipH: true, line: { color: SL, width: 1, endArrowType: 'triangle' } });
T(s, '형상', { x: x + 1.3, y: Y + 0.7, w: 0.33, h: 0.13, fontSize: 5.8, color: C.accent3, align: 'center' });
T(s, '기울기', { x: x + 1.27, y: Y + 1.21, w: 0.4, h: 0.13, fontSize: 5.8, color: C.accent3, align: 'center' });
T(s, '미분으로 잠재 변수 z 탐색 → 후보', { x: x + 0.15, y: Y + 1.6, w: CW - 0.3, h: 0.16, fontSize: 6.5, bold: true, color: BL, align: 'center' });
dn(x + CW / 2, Y + 1.76, 0.1);
blk(x + 0.15, Y + 1.86, CW - 0.3, 0.84, '위상 최적화', 'SIMP + MMA · 제조 제약\n(출력 방향 · 최소 두께)', SL, { img: 'v79_evo.png', iw: 1.45, fill: 'F5F7FB' });
chips(x, ['DeepSDF', 'GINO · FNO', 'SIMP · MMA'], BL);
eff(x, '형상 생성 · 성능 예측 · 최적화를 미분으로 연결', BL);
// C
x = card(2, 'C', '자동 검증 · 재설계 루프', SL);
blk(x + 0.15, Y + 0.6, CW - 0.3, 0.6, '출력 형상 (STL)', '제작될 형상 그대로', SL, { img: 'v74_verify.png', iw: 0.8 });
dn(x + CW / 2, Y + 1.2, 0.1);
blk(x + 0.15, Y + 1.3, CW - 0.3, 0.42, '재격자화 → FEM', '진동 · 열 · 충격 · 터치 처짐', SL);
dn(x + CW / 2, Y + 1.72, 0.1);
blk(x + 0.15, Y + 1.82, CW - 0.3, 0.42, '자동 판정', '기준 · 연결성 · 중간 밀도 · 제조 조건', SL);
dn(x + 0.75, Y + 2.24, 0.1, BL);
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.15, y: Y + 2.34, w: 1.22, h: 0.36, rectRadius: 0.05, fill: { color: BL }, line: { color: BL }, objectName: 'pass' });
T(s, '합격 → 제작 파일', { x: x + 0.15, y: Y + 2.34, w: 1.22, h: 0.36, fontSize: 7.5, bold: true, color: X.white, align: 'center', valign: 'middle' });
dn(x + 2.15, Y + 2.24, 0.1, SL);
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 1.48, y: Y + 2.34, w: 1.3, h: 0.36, rectRadius: 0.05, fill: { color: 'FFFFFF' }, line: { color: SL, width: 1, dashType: 'dash' }, objectName: 'fail' });
T(s, [{ text: '불합격 → B 재설계', options: { bold: true, breakLine: true } }, { text: '미달 항목만큼 목표 조정', options: { fontSize: 6 } }], { x: x + 1.48, y: Y + 2.34, w: 1.3, h: 0.36, fontSize: 7.5, color: SL, align: 'center', valign: 'middle' });
chips(x, ['FEM', '규칙 판정', '폐루프 재설계'], SL);
eff(x, '제작될 형상 그대로 판정 — 합격만 출력', SL);
box(s, 0.5, 4.8, 9.0, 0.34, X.ink, 'sum');
T(s, [{ text: 'A 조건 → B 설계 → C 검증', options: { bold: true, color: X.white } }, { text: '   불합격이면 B로 자동 회귀 — 사람 개입 없이 기준 충족까지 반복', options: { color: 'D9E1F5' } }], { x: 0.65, y: 4.8, w: 8.7, h: 0.34, fontSize: 8.5, valign: 'middle' });
T(s, '※ 물리 AI: 현재 구현 FNO(격자 입력) · GINO(메시 · STEP 입력) 확장, 형상 AI · 물리 AI 학습 진행 중. 실증 사례 결과는 위상 최적화 경로', { x: 0.5, y: 5.16, w: 9, h: 0.14, fontSize: 6.5, color: C.accent3 });
}
s.addNotes('핵심 기술 A · B · C. A 근거 기반 물리 조건 정의: LLM이 표현의 의미를 물리량으로 해석하고, 수치는 근거 DB(규격 · 실측 논문 · 데이터시트)에서만 가져와 항목별 출처를 붙인 JSON 설계 사양을 만든다. 근거가 없으면 사용자에게 묻는다. B 물리 기반 역설계 엔진: 형상 AI(DeepSDF)가 형상을 잠재 변수로 표현하고, 물리 AI(신경 연산자, FNO · GINO)가 형상에서 응력 · 온도 분포를 즉시 예측해 기울기를 준다. 미분으로 후보를 찾고 SIMP + MMA 위상 최적화가 제조 제약을 지키며 정밀화한다. C 자동 검증 · 재설계 루프: 제작될 STL을 다시 격자화해 FEM으로 진동 · 열 · 충격 · 처짐을 계산하고, 기준 · 연결성 · 중간 밀도를 자동 판정한다. 불합격이면 미달 항목만큼 목표를 조여 B로 돌려보낸다. 물리 AI는 현재 FNO로 구현, GINO는 메시 · STEP 입력용 확장. 학습은 진행 중이며 실증 결과는 위상 최적화 경로.');

