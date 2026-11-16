// ===== v74: 대표 그림 — FormProof 프레임워크 (입력 → ①②③ 엔진 → 출력, 에이전트 · 바탕)
const GEN = '6B4FA0';   // 생성 AI 색 (뒤 장에서도 사용)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. FormProof 프레임워크 — 조건이 먼저, 형상은 계산으로', { placeholder: 'title' });
s.addText('아이디어를 받아 물리 조건을 세우고, 형상을 계산하고, 출력할 형상까지 검증해 제작 파일로 내놓는다', { placeholder: 'body' });
{
const PHY = X.teal, NUM = '5B6B78';
const Y0 = 1.62, H0 = 2.42;
// 에이전트 (위)
box(s, 2.05, 1.2, 6.0, 0.32, X.ink, 'agent');
T(s, [{ text: 'LLM 에이전트  ', options: { bold: true, color: X.amber } }, { text: '단계 실행 · 결과 판정 · 재설계 지시', options: { color: X.white } }], { x: 2.15, y: 1.2, w: 5.8, h: 0.32, fontSize: 8.5, align: 'center', valign: 'middle' });
// 입력
box(s, 0.5, Y0, 1.42, H0, 'FFFFFF', 'input');
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: Y0, w: 1.42, h: H0, rectRadius: 0.08, fill: { type: 'none' }, line: { color: X.line, width: 0.75 }, objectName: 'input frame' });
T(s, '입력', { x: 0.6, y: Y0 + 0.08, w: 1.2, h: 0.22, fontSize: 9, bold: true, color: C.accent3 });
fit(s, SH + 'v17_sketch.png', 0.58, Y0 + 0.36, 1.26, 0.9, 'sketch input');
T(s, '"울퉁불퉁한 길에서도 안 흔들리게, 가볍게"', { x: 0.6, y: Y0 + 1.3, w: 1.24, h: 0.5, fontSize: 7, italic: true, color: C.text2 });
T(s, '말 · 스케치 · 문서 · STEP', { x: 0.6, y: Y0 + 1.86, w: 1.24, h: 0.4, fontSize: 7, bold: true, color: C.text1 });
// 엔진 ①②③
const ENG = [
  ['①', '요구 → 물리 조건', '생성 AI + 근거 DB', GEN, 'v32_spec.png', '하중 · 기준 · 재료\n항목마다 출처 · 빠진 조건 질문'],
  ['②', '형상 생성 · 역설계', '형상 AI × 물리 AI → 수치해석', PHY, 'v32_evo.png', '물리 AI가 빠르게 찾고\n위상 최적화 · FEM이 정밀화'],
  ['③', '출력 형상 재검증', '수치해석 · 자동 검증 관문', NUM, 'v51_ai.png', '출력할 STL로 다시 계산\n기준 미달이면 불합격']];
const EX = [2.05, 4.1, 6.15], EW = 1.9;
ENG.forEach((e, i) => { const x = EX[i];
  box(s, x, Y0, EW, H0, X.tint, 'engine');
  s.addShape(pres.shapes.RECTANGLE, { x, y: Y0, w: EW, h: 0.06, fill: { color: e[3] }, line: { color: e[3] }, objectName: 'engine top' });
  s.addShape(pres.shapes.OVAL, { x: x + 0.1, y: Y0 + 0.14, w: 0.3, h: 0.3, fill: { color: X.red }, line: { color: X.white, width: 1 }, objectName: 'core' });
  T(s, e[0], { x: x + 0.1, y: Y0 + 0.14, w: 0.3, h: 0.3, fontSize: 10, bold: true, color: X.white, align: 'center', valign: 'middle' });
  T(s, e[1], { x: x + 0.46, y: Y0 + 0.12, w: EW - 0.5, h: 0.34, fontSize: 10, bold: true, color: C.text2, valign: 'middle' });
  T(s, e[2], { x: x + 0.1, y: Y0 + 0.5, w: EW - 0.2, h: 0.2, fontSize: 7, bold: true, color: e[3] });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.1, y: Y0 + 0.74, w: EW - 0.2, h: 0.95, rectRadius: 0.04, fill: { color: 'FFFFFF' }, line: { color: X.line, width: 0.5 }, objectName: 'thumb' });
  fit(s, SH + e[4], x + 0.12, Y0 + 0.76, EW - 0.24, 0.91, e[1]);
  T(s, e[5], { x: x + 0.1, y: Y0 + 1.74, w: EW - 0.2, h: 0.6, fontSize: 7.5, color: C.text1 }); });
// 출력
const OX = 8.2, OW = 1.3;
box(s, OX, Y0, OW, H0, X.ink, 'output');
T(s, '검증된 제작 파일', { x: OX + 0.08, y: Y0 + 0.08, w: OW - 0.16, h: 0.22, fontSize: 8.5, bold: true, color: X.amber });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: OX + 0.08, y: Y0 + 0.36, w: OW - 0.16, h: 0.9, rectRadius: 0.04, fill: { color: 'FFFFFF' }, line: { color: 'FFFFFF' }, objectName: 'out thumb' });
fit(s, SH + 'v47_use.png', OX + 0.1, Y0 + 0.38, OW - 0.2, 0.86, 'final design');
T(s, 'STL · STEP\n도면 · 조립 설명서\n근거 리포트', { x: OX + 0.08, y: Y0 + 1.34, w: OW - 0.16, h: 0.9, fontSize: 7.5, color: X.white });
// 화살표
[[1.92, 2.05], [3.95, 4.1], [6.05, 6.15], [8.05, 8.2]].forEach(a => s.addShape(pres.shapes.LINE, { x: a[0], y: Y0 + 1.2, w: a[1] - a[0], h: 0, line: { color: X.mute, width: 1.5, endArrowType: 'triangle' }, objectName: 'flow' }));
// ③ → ② 되돌림
const LYb = Y0 + H0 + 0.1;
s.addShape(pres.shapes.LINE, { x: EX[1] + EW / 2, y: LYb, w: EX[2] - EX[1], h: 0, line: { color: X.amber, width: 1.25, dashType: 'dash', beginArrowType: 'triangle' }, objectName: 'loop' });
[EX[1] + EW / 2, EX[2] + EW / 2].forEach(x => s.addShape(pres.shapes.LINE, { x, y: Y0 + H0, w: 0, h: 0.1, line: { color: X.amber, width: 1.25, dashType: 'dash' } }));
T(s, '불합격 → 재설계 (기준을 만족할 때까지)', { x: EX[1] + EW / 2, y: LYb + 0.02, w: EX[2] - EX[1], h: 0.16, fontSize: 6.5, bold: true, color: 'B07A1E', align: 'center' });
// 바탕
const BY = 4.4;
box(s, 2.05, BY, 2.95, 0.46, X.tint, 'db');
T(s, [{ text: '근거 DB  ', options: { bold: true, color: C.text2 } }, { text: '규격 · 측정 논문 · 재료 데이터시트', options: { color: C.text1 } }], { x: 2.15, y: BY, w: 2.8, h: 0.46, fontSize: 7.5, valign: 'middle' });
box(s, 5.1, BY, 2.95, 0.46, X.tint, 'phys');
T(s, [{ text: '물리 모듈  ', options: { bold: true, color: C.text2 } }, { text: '구조 · 진동 · 열 · 충격 · 제조 제약 → 낙하 · 피로 · 전자기', options: { color: C.text1 } }], { x: 5.2, y: BY, w: 2.8, h: 0.46, fontSize: 7.5, valign: 'middle' });
T(s, '여섯 단계 대응: ① 요구 정의 · 물리 조건  ② 3D 형상 생성 · 성능 해석 · 재설계  ③ 제작 파일 직전 재검증', { x: 0.5, y: 4.95, w: 9, h: 0.18, fontSize: 6.5, color: C.accent3 });
}
s.addNotes('대표 그림. 입력(말 · 스케치 · 문서 · STEP)을 받아 ① 생성 AI가 근거 DB로 물리 조건을 세우고, ② 형상 AI × 물리 AI가 빠르게 후보를 찾은 뒤 위상 최적화 · FEM이 정밀화하며, ③ 출력할 STL을 다시 계산해 기준 미달이면 재설계로 돌려보낸다. LLM 에이전트가 전 과정을 실행 · 판정하고, 근거 DB와 물리 모듈이 바탕이 된다.');

