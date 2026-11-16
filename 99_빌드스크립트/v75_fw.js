// ===== v75: 프레임워크 — 모듈 · 데이터 흐름 · 반복 고리 (동작 구조도)
const GEN = '6B4FA0';   // 생성 AI 색 (뒤 장에서도 사용)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. FormProof 프레임워크 — 모듈과 데이터가 이렇게 이어져 돈다', { placeholder: 'title' });
s.addText('에이전트가 모듈을 호출하고, 한 모듈의 결과가 다음 모듈의 입력이 되며, 검증에서 떨어지면 재설계로 되돌아간다', { placeholder: 'body' });
{
const PHY = X.teal, NUM = '5B6B78', CTL = 'B07A1E';
const node = (x, y, w, h, title, sub, col, o = {}) => {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.06, fill: { color: o.fill || 'FFFFFF' }, line: { color: col, width: 1.25 }, objectName: 'node' });
  if (o.no) { s.addShape(pres.shapes.OVAL, { x: x - 0.1, y: y - 0.1, w: 0.26, h: 0.26, fill: { color: X.red }, line: { color: X.white, width: 1 }, objectName: 'core' });
    T(s, o.no, { x: x - 0.1, y: y - 0.1, w: 0.26, h: 0.26, fontSize: 8.5, bold: true, color: X.white, align: 'center', valign: 'middle' }); }
  T(s, [{ text: title, options: { bold: true, color: o.tc || C.text2, breakLine: true } }, { text: sub, options: { fontSize: 6.8, color: o.sc || C.text1 } }], { x: x + 0.08, y, w: w - 0.16, h, fontSize: 8.5, align: 'center', valign: 'middle' }); };
const ln = (x1, y1, x2, y2, o = {}) => s.addShape(pres.shapes.LINE, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1) || 0.001, h: Math.abs(y2 - y1) || 0.001,
  flipH: x2 < x1, flipV: y2 < y1, line: { color: o.c || '6B7780', width: o.w || 1.25, dashType: o.d || 'solid', endArrowType: o.noArrow ? undefined : 'triangle', beginArrowType: o.both ? 'triangle' : undefined }, objectName: 'edge' });
const lab = (t, x, y, w, o = {}) => T(s, t, { x, y, w, h: o.h || 0.16, fontSize: o.fs || 6.3, bold: !!o.b, color: o.c || C.accent3, align: o.al || 'center', valign: 'middle' });
// 에이전트
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 1.75, y: 1.17, w: 6.5, h: 0.36, rectRadius: 0.06, fill: { color: X.ink }, line: { color: X.ink }, objectName: 'agent' });
T(s, [{ text: 'LLM 에이전트   ', options: { bold: true, color: X.amber } }, { text: '계획 → 모듈 호출 → 결과를 기준과 대조 → 다음 호출 · 재설계 지시', options: { color: X.white } }], { x: 1.85, y: 1.17, w: 6.3, h: 0.36, fontSize: 8, align: 'center', valign: 'middle' });
const RY = 2.63;   // 주 흐름 높이
node(0.5, 2.18, 0.95, 0.9, '입력', '말 · 스케치\n문서 · STEP', X.mute);
node(1.75, 2.08, 1.3, 1.1, '조건 생성기', 'LLM + 근거 DB\n요구 → 하중 · 기준 · 재료', GEN, { no: '①', tc: GEN });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 3.55, y: 1.78, w: 3.0, h: 2.2, rectRadius: 0.06, fill: { color: 'EEF6F5' }, line: { color: PHY, width: 1, dashType: 'dash' }, objectName: 'engine' });
s.addShape(pres.shapes.OVAL, { x: 3.45, y: 1.68, w: 0.26, h: 0.26, fill: { color: X.red }, line: { color: X.white, width: 1 } });
T(s, '②', { x: 3.45, y: 1.68, w: 0.26, h: 0.26, fontSize: 8.5, bold: true, color: X.white, align: 'center', valign: 'middle' });
lab('형상 엔진', 3.75, 1.8, 1.0, { b: true, c: PHY, al: 'left', fs: 7.5 });
node(3.7, 2.02, 1.12, 0.62, '형상 AI', '잠재 변수 z → 3D 형상', GEN, { tc: GEN });
node(5.28, 2.02, 1.12, 0.62, '물리 AI', '형상 → 성능 0.2초', PHY, { tc: PHY });
ln(4.82, 2.2, 5.28, 2.2); ln(5.28, 2.46, 4.82, 2.46);
lab('형상', 4.82, 2.03, 0.46); lab('기울기', 4.82, 2.48, 0.46);
lab('미분으로 z 조정 — 빠른 후보 탐색', 3.7, 2.67, 2.7, { b: true, c: PHY });
node(3.7, 3.04, 2.7, 0.6, '위상 최적화 + FEM', '조건 · 제조 제약을 지키며 재료 배치 반복 (정밀화)', NUM);
ln(4.26, 2.84, 4.26, 3.04); lab('후보 형상', 4.31, 2.86, 0.7, { al: 'left' });
ln(6.05, 3.04, 6.05, 2.64, { d: 'dash', c: PHY }); lab('계산 결과 → 물리 AI 학습 데이터', 4.4, 3.7, 2.1, { c: PHY, al: 'right' });
node(7.05, 2.08, 1.2, 1.1, '검증 관문', '출력 STL 재격자화\n→ FEM 재계산\n→ 기준 비교', NUM, { no: '③', tc: NUM });
node(8.7, 2.18, 0.8, 0.9, '제작 파일', 'STL · STEP\n도면 · 리포트', X.ink, { fill: X.ink, tc: X.amber, sc: X.white });
// 데이터 흐름 (라벨은 화살표 위, 두 줄)
ln(1.45, RY, 1.75, RY); lab('요청', 1.42, RY - 0.2, 0.36);
ln(3.05, RY, 3.55, RY); lab('설계 명세\n(JSON)', 3.03, RY - 0.36, 0.54, { b: true, h: 0.32 });
ln(6.55, RY, 7.05, RY); lab('출력\nSTL', 6.53, RY - 0.36, 0.54, { b: true, h: 0.32 });
ln(8.25, RY, 8.7, RY); lab('합격', 8.25, RY - 0.2, 0.45, { b: true, c: X.green });
// 불합격 되돌림
ln(7.65, 3.18, 7.65, 4.08, { c: X.red, d: 'dash', noArrow: true }); ln(7.65, 4.08, 5.05, 4.08, { c: X.red, d: 'dash', noArrow: true }); ln(5.05, 4.08, 5.05, 3.98, { c: X.red, d: 'dash' });
lab('불합격 + 미달 항목 → 재설계', 5.2, 4.1, 2.3, { b: true, c: X.red });
// 에이전트 제어선
[[2.4, 2.08], [5.05, 1.78], [7.65, 2.08]].forEach(p => ln(p[0], 1.53, p[0], p[1], { c: CTL, d: 'sysDot', w: 1 }));
lab('호출 · 판정', 2.45, 1.6, 0.8, { c: CTL, al: 'left' });
// 바탕 + 연결
node(1.75, 4.34, 1.3, 0.48, '근거 DB', '규격 · 측정 논문 · 데이터시트', X.mute, { fill: X.tint });
ln(2.4, 4.34, 2.4, 3.18, { c: X.mute, d: 'dash' });
node(3.55, 4.34, 4.7, 0.48, '물리 모듈', '구조 · 진동 · 열 · 충격 · 제조 제약 → 낙하 · 피로 · 전자기', X.mute, { fill: X.tint });
ln(3.95, 4.34, 3.95, 3.98, { c: X.mute, d: 'dash' }); ln(8.0, 4.34, 8.0, 3.18, { c: X.mute, d: 'dash' });
lab('실선 = 데이터 · 갈색 점선 = 에이전트 호출 · 빨간 점선 = 불합격 되돌림 · 청록 점선 = 계산 결과가 학습 데이터로 · 회색 점선 = 근거 · 물리 모듈 사용', 0.5, 4.93, 9.0, { fs: 6.3, al: 'left' });
}
s.addNotes('동작 구조. 에이전트가 ① 조건 생성기를 호출하면 요청과 근거 DB로 설계 명세(JSON)가 나온다. 명세는 ② 형상 엔진의 입력: 형상 AI가 잠재 변수에서 형상을 만들고 물리 AI가 0.2초에 성능과 기울기를 돌려주어 후보를 빠르게 찾는다. 후보는 위상 최적화 + FEM이 제조 제약을 지키며 정밀화하고, 그 계산 결과는 다시 물리 AI의 학습 데이터가 된다. 최종 형상은 STL로 ③ 검증 관문에 넘어가 재격자화 · 재계산 · 기준 비교를 거치고, 불합격이면 미달 항목과 함께 재설계로 돌아간다. 합격하면 제작 파일이 나온다.');

