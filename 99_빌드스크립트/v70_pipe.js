// ===== v70: 파이프라인 — 기술(가로줄) × 단계(세로칸) 지도
const GEN = '6B4FA0';   // 생성 AI 색 (다음 장에서도 사용)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 기술 차별성 — 물리 조건을 먼저 정하고, 형상은 계산이 만든다', { placeholder: 'title' });
s.addText('사람은 형상을 그린 뒤 확인하지만, FormProof는 조건에서 형상을 계산한다 — 단계마다 맡는 AI가 정해져 있다', { placeholder: 'body' });
{
const PHY = X.teal, NUM = '5B6B78', OUT = X.ink;
const STEPS = ['요구 정의', '물리 조건', '3D 형상 생성', '성능 해석', '재설계', '제작 파일'];
// 가로줄 = 맡는 기술
const LANES = [[GEN, '생성 AI', 'LLM · 형상 AI'], [PHY, '물리 AI', '빠른 예측 · 역설계'], [NUM, '수치해석', '정밀 계산 · 최적화'], [OUT, '출력', '제작 · 기록']];
// [줄, 칸, 제목, 설명, 상태 0 개발 중 / 1 시연 / 2 시연 · 분리형]
const CARDS = [
  [0, 0, '요구 → 목표 · 제약', '말 · 스케치 요청을 수치로', 1],
  [0, 1, '설계 명세', '하중 · 기준 · 재료, 항목마다 출처', 1],
  [0, 2, '형상 AI 후보 · 형상 코드', '고정 부품 · 설계 공간', 2],
  [1, 3, '성능 예측', '형상 → 진동수 0.2초', 2],
  [1, 4, '잠재 공간 최적화', '미분으로 후보 탐색 약 40초', 2],
  [2, 3, 'FEM 해석', '진동 · 충격 · 열 · 터치', 1],
  [2, 4, '위상 최적화', '조건을 지키며 재료 배치 반복', 1],
  [2, 5, '출력 형상 재검증', '기준 대비 합격 판정', 1],
  [3, 5, 'STL · STEP · 도면', '조립 설명서 포함', 1],
  [3, 0, '입력 확장', '문서 · 특허 · 사진 · STEP', 0]];
const LX = 0.5, LW = 1.15, SX = 1.72, CWp = 1.28, GP = 0.02, HY = 1.22, LY0 = 1.6, LH = 0.6, LG = 0.06;
const STT = [['개발 중', 'FFFFFF', NUM], ['시연', X.green, X.white], ['시연 · 분리형', X.amber, X.white]];
STEPS.forEach((st, i) => { const x = SX + i * (CWp + GP);
  s.addShape(pres.shapes.CHEVRON, { x, y: HY, w: CWp + 0.04, h: 0.3, fill: { color: X.ink }, line: { color: X.ink }, objectName: 'step' });
  T(s, st, { x: x + 0.12, y: HY, w: CWp - 0.2, h: 0.3, fontSize: 7.5, bold: true, color: X.white, align: 'center', valign: 'middle' }); });
LANES.forEach((l, r) => { const y = LY0 + r * (LH + LG);
  s.addShape(pres.shapes.RECTANGLE, { x: LX, y, w: 9.0, h: LH, fill: { color: r % 2 ? 'FFFFFF' : 'F6F7F8' }, line: { color: 'E1E5E8', width: 0.5 }, objectName: 'lane' });
  s.addShape(pres.shapes.RECTANGLE, { x: LX, y, w: 0.07, h: LH, fill: { color: l[0] }, line: { color: l[0] }, objectName: 'lane bar' });
  T(s, [{ text: l[1], options: { bold: true, color: l[0], breakLine: true } }, { text: l[2], options: { fontSize: 6.5, color: C.accent3 } }], { x: LX + 0.14, y, w: LW, h: LH, fontSize: 9, valign: 'middle' }); });
CARDS.forEach(c => { const [r, i, ti, de, stv] = c, x = SX + i * (CWp + GP) + 0.04, y = LY0 + r * (LH + LG) + 0.05, w = CWp - 0.08, h = LH - 0.1, dev = stv === 0, col = LANES[r][0];
  s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: dev ? 'FFFFFF' : col, transparency: dev ? 0 : 85 }, line: { color: dev ? 'C9CED2' : col, width: 0.75, dashType: dev ? 'dash' : 'solid' }, objectName: 'card' });
  T(s, ti, { x: x + 0.06, y: y + 0.03, w: w - 0.1, h: 0.2, fontSize: 7.5, bold: true, color: dev ? C.accent3 : C.text2 });
  T(s, de, { x: x + 0.06, y: y + 0.22, w: w - 0.1, h: 0.16, fontSize: 6, color: C.text1 });
  const st = STT[stv], pw = stv === 2 ? 0.72 : 0.42;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + w - pw - 0.04, y: y + h - 0.17, w: pw, h: 0.14, rectRadius: 0.07, fill: { color: st[1] }, line: { color: stv === 0 ? NUM : st[1], width: 0.5 }, objectName: 'status' });
  T(s, st[0], { x: x + w - pw - 0.04, y: y + h - 0.17, w: pw, h: 0.14, fontSize: 5.5, bold: true, color: st[2], align: 'center', valign: 'middle' }); });
// 반복 고리 (재검증 불합격 → 재설계)
const cx = i => SX + i * (CWp + GP) + CWp / 2, ry = LY0 + 2 * (LH + LG) + LH - 0.02;
s.addShape(pres.shapes.LINE, { x: cx(4), y: ry, w: cx(5) - cx(4), h: 0, line: { color: X.amber, width: 1.25, dashType: 'dash', beginArrowType: 'triangle' } });
T(s, '불합격 → 재설계', { x: cx(4) + 0.1, y: ry - 0.01, w: 1.1, h: 0.14, fontSize: 6, bold: true, color: 'B07A1E', align: 'center' });
// LLM 에이전트: 모든 단계를 잇는 줄
const AY = LY0 + 4 * (LH + LG) + 0.02;
box(s, LX, AY, 9.0, 0.42, X.ink, 'agent');
T(s, [{ text: 'LLM 에이전트', options: { bold: true, color: X.amber } }, { text: '   여섯 단계를 차례로 실행하고, 결과를 기준과 대조해 다음 단계 · 재설계를 지시 (단계 자동 연결은 개발 중)', options: { color: X.white } }],
  { x: LX + 0.14, y: AY, w: 8.75, h: 0.42, fontSize: 8, valign: 'middle' });
T(s, '바탕: 근거 DB(규격 · 측정 논문 · 재료 데이터시트) · 자동 검증 관문(모든 결과를 코드로 판정) · 물리 모듈(구조 · 진동 · 열 · 제조 제약 → 다음: 낙하 · 피로 · 전자기)', { x: 0.5, y: AY + 0.47, w: 9, h: 0.18, fontSize: 6.5, color: C.text1 });
T(s, '시연 = 이번 과제에서 실제 수행 · 시연 · 분리형 = 분리형 거치대 계열로 학습 · 시연(일체형 적용 진행 중) · 개발 중 = 해커톤 이후. 빈 칸 = 그 기술이 맡지 않는 단계', { x: 0.5, y: AY + 0.66, w: 9, h: 0.18, fontSize: 6.5, color: C.accent3 });
}
s.addNotes('가로줄은 맡는 기술, 세로칸은 4쪽과 같은 여섯 단계. 생성 AI가 요구와 조건을 정리하고 형상 후보를 만들며, 물리 AI가 빠르게 예측 · 탐색하고, 수치해석이 정밀 계산 · 최적화 · 재검증을 맡는다. LLM 에이전트가 이 단계를 차례로 실행한다.');

