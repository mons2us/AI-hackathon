// ---------- 4. 기술 차별성: 단계 지도 (v60: 누가 · 얼마나 어렵게 하나)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 기술 차별성 — 어려운 단계는 여전히 전문가 손에 있다', { placeholder: 'title' });
s.addText('해석 도구도 계산은 하지만 조건 설정 · 재설계 · 재검증은 전문가가 한다 — FormProof는 여섯 단계를 AI가 잇는다', { placeholder: 'body' });
{
const UI = { user: await icon(fa.FaUser, 'B8C0C6'), pro: await icon(fa.FaUserTie, X.white), ai: await icon(fa.FaRobot, X.white) };
// [단계, 사람이 할 때 필요한 일, 난이도(1–3), 3쪽 벽]
const STP = [['요구 정의', '목표 · 제약을 수치로 정리', 2, ''], ['3D 형상 생성', 'CAD 모델링 · 설계', 2, '①'], ['물리 조건', '하중 · 경계조건 설정', 3, '②'],
  ['성능 해석', '시뮬레이션 (메쉬 · 해석)', 3, '③'], ['재설계', '최적화 + CAD 재구성 · 반복', 3, ''], ['제작 파일', '도면 · 출력 형상 재검증', 2, '④']];
// 1 = 도구가 자동, 3 = 전문가 수작업 필요, 4 = 추측(검증 없음), 0 = 지원 안 함 → 사람이 메움
const RW = [
  ['범용 LLM 단독', '대화형 생성 AI', [1, 1, 4, 4, 0, 4], '조건 · 성능을 계산 없이 어림 — 같은 조건 3회 모두 불합격²'],
  ['3D 생성 AI', '텍스트 · 이미지 → 3D', [0, 1, 0, 0, 0, 0], '형상만 — 성능 · 재설계는 비어 있다'],
  ['물리 AI', '목표 → 최적 설계 (역설계)', [0, 6, 7, 1, 1, 0], '형상 틀 안에서 목표만 넣으면 최적 설계 — 틀 · 조건 · 학습 데이터는 사람이 준비'],
  ['해석 · 최적화 도구', '전문가용 CAE', [0, 3, 3, 1, 3, 3], '계산만 자동, 나머지는 전문가 손 — 결과까지 1주+ 67%¹'],
  ['FormProof', '요구부터 제작 파일까지', [1, 1, 1, 1, 1, 1], '형상 AI + 물리 AI + 수치해석이 여섯 단계를 자동으로 (6쪽)']];
const LX = 0.5, LW = 1.7, SX = 2.3, CWs = 0.86, RX = SX + 6 * CWs + 0.12, RWd = 9.5 - RX, HY = 1.22, RY0 = 2.02, RH = 0.46, RG = 0.07;
STP.forEach((st, i) => { const x = SX + i * CWs;
  s.addShape(pres.shapes.CHEVRON, { x: x + 0.01, y: HY, w: CWs - 0.02, h: 0.3, fill: { color: X.ink }, line: { color: X.ink }, objectName: 'step' });
  T(s, st[0], { x: x + 0.1, y: HY, w: CWs - 0.2, h: 0.3, fontSize: st[0].length > 5 ? 6.8 : 7.5, bold: true, color: X.white, align: 'center', valign: 'middle' });
  T(s, st[1], { x: x + 0.02, y: HY + 0.33, w: CWs - 0.04, h: 0.26, fontSize: 6, color: C.text1, align: 'center' });
  T(s, '●'.repeat(st[2]) + '○'.repeat(3 - st[2]), { x, y: HY + 0.58, w: CWs, h: 0.14, fontSize: 7, color: st[2] === 3 ? X.red : X.amber, align: 'center' });
  if (st[3]) { s.addShape(pres.shapes.OVAL, { x: x + CWs - 0.2, y: HY - 0.1, w: 0.18, h: 0.18, fill: { color: X.red }, line: { color: X.white, width: 0.75 }, objectName: 'wall no' });
    T(s, st[3], { x: x + CWs - 0.2, y: HY - 0.1, w: 0.18, h: 0.18, fontSize: 6.5, bold: true, color: X.white, align: 'center', valign: 'middle' }); } });
T(s, '사람이 할 때\n필요한 일 · 난이도', { x: LX, y: HY + 0.3, w: LW, h: 0.44, fontSize: 7, color: C.accent3, valign: 'middle' });
T(s, '한계', { x: RX, y: HY + 0.04, w: RWd, h: 0.24, fontSize: 9, bold: true, color: C.accent3 });
const cell = (st, x, y, w, h, fp) => {
  if (st === 1) { const c = fp ? X.teal : '7C8B96';
    s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: c }, line: { color: c }, objectName: 'auto' });
    if (fp) s.addImage({ data: UI.ai, x: x + w / 2 - 0.08, y: y + h / 2 - 0.08, w: 0.16, h: 0.16 }); }
  else if (st === 3) { s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: X.amber }, line: { color: X.amber }, objectName: 'expert' });
    s.addImage({ data: UI.pro, x: x + w / 2 - 0.08, y: y + h / 2 - 0.08, w: 0.16, h: 0.16 }); }
  else if (st === 6 || st === 7) { s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: X.amber }, line: { color: X.amber }, objectName: 'expert text' });
    T(s, st === 6 ? '형상 틀은\n사람이' : '학습 때\n고정', { x, y, w, h, fontSize: 6.5, bold: true, color: X.white, align: 'center', valign: 'middle' }); }
  else if (st === 5) { s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: 'F8E3BF' }, line: { color: X.amber, width: 0.75, dashType: 'dash' }, objectName: 'setup' });
    if (w > 0.4) T(s, '구축 때', { x, y, w, h, fontSize: 7, bold: true, color: 'B07A1E', align: 'center', valign: 'middle' }); }
  else if (st === 4) { s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: 'FBF1EF' }, line: { color: X.red, width: 0.75, dashType: 'dash' }, objectName: 'guess' });
    T(s, '추측', { x, y, w, h, fontSize: 7, bold: true, color: X.red, align: 'center', valign: 'middle' }); }
  else { s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: 'FFFFFF' }, line: { color: 'D9DEE2', width: 0.75, dashType: 'dash' }, objectName: 'gap' });
    s.addImage({ data: UI.user, x: x + w / 2 - 0.07, y: y + h / 2 - 0.07, w: 0.14, h: 0.14 }); } };
RW.forEach((r, ri) => { const y = RY0 + ri * (RH + RG), fp = ri === 4;
  if (fp) box(s, LX - 0.08, y - 0.05, 9.08, RH + 0.1, 'E3F0EF', 'fp row');
  T(s, r[0], { x: LX, y: y + 0.01, w: LW, h: 0.24, fontSize: 9.5, bold: true, color: fp ? C.accent1 : C.text2 });
  T(s, r[1], { x: LX, y: y + 0.25, w: LW, h: 0.18, fontSize: 7, color: C.accent3 });
  r[2].forEach((m, i) => cell(m, SX + i * CWs + 0.03, y + 0.06, CWs - 0.06, RH - 0.12, fp));
  T(s, r[3], { x: RX, y, w: RWd, h: RH, fontSize: 7.5, bold: fp, color: fp ? C.accent1 : C.text1, valign: 'middle' }); });
// 범례
const LG = 4.7;
[[1, '도구가 자동'], [3, '전문가 손 필요'], [4, '추측 (검증 없음)'], [0, '사람이 메움']].forEach((g, i) => { const x = SX + i * 1.32;
  cell(g[0], x, LG, 0.3, 0.16, false); T(s, g[1], { x: x + 0.36, y: LG - 0.01, w: 0.95, h: 0.18, fontSize: 6.5, color: C.accent3, valign: 'middle' }); });
T(s, '빨간 번호 = 3쪽의 벽', { x: 7.6, y: LG - 0.01, w: 1.9, h: 0.18, fontSize: 6.5, color: C.accent3, align: 'right', valign: 'middle' });
T(s, [{ text: '1', options: { superscript: true } }, { text: ' engineering.com · Dassault 2022 설문(3쪽)   ' }, { text: '2', options: { superscript: true } }, { text: ' 같은 조건 독립 3회, 같은 해석기로 판정(11쪽).  난이도 = 사람이 직접 할 때 필요한 전문성(팀 판단). 범주별 일반 기능 기준(상용 제품별 비교는 확인 필요). FormProof: 요구는 말 · 스케치 입력만 시연, 형상 AI는 분리형 거치대 계열로 학습 · 일체형 최종 형상은 수치 최적화, 단계 연결 자동 실행은 개발 중' }],
  { x: 0.5, y: 4.92, w: 9, h: 0.3, fontSize: 6.5, color: C.accent3 });
}
s.addNotes('요구 정의 = 문제와 요구를 목표 · 제약 수치로 정리. 성능 해석 = 시뮬레이션. 가장 어려운 단계는 물리 조건 설정, 해석, 재설계(최적화 결과를 다시 CAD로 만들고 반복). 해석 도구는 계산 자체는 자동이지만 그 앞뒤(모델링, 조건, 재설계, 재검증)는 전문가가 한다. FormProof는 여섯 단계를 AI가 수행한다.');

