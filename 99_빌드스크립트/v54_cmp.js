// ---------- 4. 기술 차별성: 단계 지도 (v54: 체크표 → 누가 어느 단계를 맡나 막대)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 기술 차별성 — 기존 기술은 한 단계씩, 잇는 일은 사람 몫', { placeholder: 'title' });
s.addText('기존 기술이 비워 둔 단계는 지금 사람이 메운다 — FormProof는 여섯 단계를 처음부터 끝까지 잇는다', { placeholder: 'body' });
{
const UI = { user: await icon(fa.FaUser, 'B8C0C6') };
const STP = [['입력', '말 · 스케치 · 문서', ''], ['물리 조건', '하중 · 고정 · 기준', '②'], ['형상 생성', '3D 형상', '①'], ['성능 판정', '계산으로 확인', '③'], ['형상 개선', '재설계', ''], ['제작 파일', '재검증 · 도면 · STL', '④']];
const RW = [ // 0 = 비어 있음(사람이 메움), 1 = 함, 2 = 일부
  ['범용 LLM 단독', '대화형 생성 AI', [1, 2, 1, 0, 0, 2], '계산 없이 어림 → 같은 조건 3회 모두 불합격²', X.mute],
  ['3D 생성 AI', '텍스트 · 이미지 → 3D', [2, 0, 1, 0, 0, 0], '형상만 만들고 성능은 모른다', X.mute],
  ['물리 AI (대리 모델)', '성능을 빠르게 예측', [0, 0, 0, 1, 2, 0], '형상과 조건이 주어져야 예측한다', X.mute],
  ['해석 · 최적화 도구', '전문가용 CAE', [2, 0, 2, 1, 1, 2], '정확하지만 조건 설정 · 판정은 전문가 몫 (67%: 결과까지 1주+¹)', X.mute],
  ['FormProof', '요구부터 제작 파일까지', [2, 1, 1, 1, 1, 1], '여섯 단계를 한 흐름으로 — 이번 시연에서 실제 수행', X.teal]];
const LX = 0.5, LW = 1.75, SX = 2.35, CWs = 0.84, RX = SX + 6 * CWs + 0.12, RWd = 9.5 - RX, HY = 1.22, RY0 = 1.78, RH = 0.5, RG = 0.08;
// 단계 머리
STP.forEach((st, i) => { const x = SX + i * CWs;
  s.addShape(pres.shapes.CHEVRON, { x: x + 0.01, y: HY, w: CWs - 0.02, h: 0.3, fill: { color: X.ink }, line: { color: X.ink }, objectName: 'step' });
  T(s, st[0], { x: x + 0.12, y: HY, w: CWs - 0.24, h: 0.3, fontSize: 7.5, bold: true, color: X.white, align: 'center', valign: 'middle' });
  T(s, st[1], { x, y: HY + 0.32, w: CWs, h: 0.16, fontSize: 6, color: C.accent3, align: 'center' });
  if (st[2]) { s.addShape(pres.shapes.OVAL, { x: x + CWs - 0.2, y: HY - 0.1, w: 0.18, h: 0.18, fill: { color: X.red }, line: { color: X.white, width: 0.75 }, objectName: 'wall no' });
    T(s, st[2], { x: x + CWs - 0.2, y: HY - 0.1, w: 0.18, h: 0.18, fontSize: 6.5, bold: true, color: X.white, align: 'center', valign: 'middle' }); } });
T(s, '한계', { x: RX, y: HY + 0.04, w: RWd, h: 0.24, fontSize: 9, bold: true, color: C.accent3 });
// 행
RW.forEach((r, ri) => { const y = RY0 + ri * (RH + RG), fp = ri === 4, col = fp ? X.teal : '7C8B96';
  if (fp) box(s, LX - 0.08, y - 0.06, 9.08, RH + 0.12, 'E3F0EF', 'fp row');
  T(s, r[0], { x: LX, y: y + 0.02, w: LW, h: 0.26, fontSize: 9.5, bold: true, color: fp ? C.accent1 : C.text2 });
  T(s, r[1], { x: LX, y: y + 0.27, w: LW, h: 0.2, fontSize: 7, color: C.accent3 });
  r[2].forEach((m, i) => { const x = SX + i * CWs + 0.03, w = CWs - 0.06;
    if (m === 1) s.addShape(pres.shapes.RECTANGLE, { x, y: y + 0.08, w, h: RH - 0.16, fill: { color: col }, line: { color: col }, objectName: 'does' });
    else if (m === 2) s.addShape(pres.shapes.RECTANGLE, { x, y: y + 0.08, w, h: RH - 0.16, fill: { color: col, transparency: 65 }, line: { color: col, width: 0.75, dashType: 'dash' }, objectName: 'partly' });
    else { s.addShape(pres.shapes.RECTANGLE, { x, y: y + 0.08, w, h: RH - 0.16, fill: { color: 'FFFFFF' }, line: { color: 'D9DEE2', width: 0.75, dashType: 'dash' }, objectName: 'gap' });
      s.addImage({ data: UI.user, x: x + w / 2 - 0.08, y: y + RH / 2 - 0.09, w: 0.16, h: 0.16 }); } });
  T(s, r[3], { x: RX, y, w: RWd, h: RH, fontSize: 8, bold: fp, color: fp ? C.accent1 : C.text1, valign: 'middle' }); });
// 범례
const LG = 4.72;
[['함', 1], ['일부', 2], ['비어 있음 → 사람이 메움', 0]].forEach((g, i) => { const x = SX + i * 1.25;
  if (g[1] === 1) s.addShape(pres.shapes.RECTANGLE, { x, y: LG, w: 0.3, h: 0.14, fill: { color: '7C8B96' }, line: { color: '7C8B96' } });
  else if (g[1] === 2) s.addShape(pres.shapes.RECTANGLE, { x, y: LG, w: 0.3, h: 0.14, fill: { color: '7C8B96', transparency: 65 }, line: { color: '7C8B96', width: 0.75, dashType: 'dash' } });
  else { s.addShape(pres.shapes.RECTANGLE, { x, y: LG, w: 0.3, h: 0.14, fill: { color: 'FFFFFF' }, line: { color: 'D9DEE2', width: 0.75, dashType: 'dash' } }); s.addImage({ data: UI.user, x: x + 0.09, y: LG + 0.01, w: 0.12, h: 0.12 }); }
  T(s, g[0], { x: x + 0.36, y: LG - 0.02, w: 1.6, h: 0.18, fontSize: 7, color: C.accent3, valign: 'middle' }); });
T(s, '빨간 번호 = 3쪽의 벽', { x: 7.0, y: LG - 0.02, w: 2.5, h: 0.18, fontSize: 7, color: C.accent3, align: 'right', valign: 'middle' });
T(s, [{ text: '1', options: { superscript: true } }, { text: ' engineering.com · Dassault 2022 설문(3쪽)   ' }, { text: '2', options: { superscript: true } }, { text: ' 같은 조건 독립 3회, 같은 해석기로 판정(11쪽).  범주별 일반 기능 기준(상용 제품별 비교는 확인 필요). FormProof 입력은 말 · 스케치만 시연' }],
  { x: 0.5, y: 4.94, w: 9, h: 0.28, fontSize: 6.5, color: C.accent3 });
}
s.addNotes('여섯 단계 중 각 기술이 맡는 칸만 칠했다. 빈 칸은 지금 사람이 메운다 — 형상을 CAD로 옮기고, 조건을 정하고, 결과를 보고 고친다. FormProof는 여섯 칸을 한 흐름으로 잇는다. 입력은 말 · 스케치만 시연해 일부로 표시했다.');

