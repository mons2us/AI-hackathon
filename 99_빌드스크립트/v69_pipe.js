// ===== v69: 파이프라인 — 여섯 단계를 누가 맡나 (4쪽과 같은 단계 이름)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 기술 차별성 — 물리 조건을 먼저 정하고, 형상은 계산이 만든다', { placeholder: 'title' });
s.addText('사람은 형상을 그린 뒤 확인하지만(4쪽), FormProof는 조건에서 형상을 계산 — 생성 AI · 물리 AI · 수치해석이 나눠 맡고 LLM 에이전트가 잇는다', { placeholder: 'body' });
{
const GEN = '6B4FA0', PHY = X.teal, NUM = '5B6B78', OUT = X.ink;
const COLS = [
  ['요구 정의', [[GEN, '요구 → 목표 · 제약', '생성 AI (LLM)', '말 · 스케치 요청을 목표 수치로', 1], [GEN, '입력 확장', '생성 AI (LLM)', '문서 · 특허 · 사진 · STEP', 0]]],
  ['물리 조건', [[GEN, '설계 명세', '생성 AI + 근거 DB', '하중 · 기준 · 재료\n항목마다 출처', 1]]],
  ['3D 형상 생성', [[GEN, '고정 부품 · 설계 공간', 'LLM → 형상 코드', '지킬 곳 · 비울 곳', 1], [GEN, '형상 AI', 'DeepSDF 방식', '잠재 공간에서 후보 생성', 2]]],
  ['성능 해석', [[PHY, '물리 AI', '3D 합성곱 신경망', '형상 → 진동수 0.2초 예측', 2], [NUM, '수치해석 (FEM)', '2 mm 격자', '진동 · 충격 · 열 · 터치', 1]]],
  ['재설계', [[PHY, '잠재 공간 최적화', '형상 AI × 물리 AI', '미분으로 후보 탐색 약 40초', 2], [NUM, '위상 최적화', 'FEM 미분 + 제조 제약', '조건을 지키며 재료 배치 반복', 1]]],
  ['제작 파일', [[NUM, '출력 형상 재검증', '수치해석', '기준 대비 합격 판정', 1], [OUT, '제작 파일', 'STL · STEP · 도면', '조립 설명서 포함', 1], [OUT, '근거 리포트', '성능 · 출처 · 미확인', '', 0]]]];
const X0 = 0.5, CWp = 1.45, GP = 0.06, HY = 1.22, CY = 1.62, CH = 2.3;
const STT = [['개발 중', 'FFFFFF', NUM], ['시연', X.green, X.white], ['시연 · 분리형', X.amber, X.white]];
COLS.forEach((c, i) => { const x = X0 + i * (CWp + GP);
  s.addShape(pres.shapes.CHEVRON, { x, y: HY, w: CWp + 0.04, h: 0.3, fill: { color: X.ink }, line: { color: X.ink }, objectName: 'step' });
  T(s, c[0], { x: x + 0.12, y: HY, w: CWp - 0.2, h: 0.3, fontSize: 8, bold: true, color: X.white, align: 'center', valign: 'middle' });
  const n = c[1].length, h = (CH - (n - 1) * 0.08) / n;
  c[1].forEach((k, j) => { const y = CY + j * (h + 0.08), dev = k[4] === 0;
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: CWp, h, fill: { color: dev ? 'FFFFFF' : 'F6F7F8' }, line: { color: dev ? 'C9CED2' : 'E1E5E8', width: 0.75, dashType: dev ? 'dash' : 'solid' }, objectName: 'comp' });
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.06, h, fill: { color: k[0] }, line: { color: k[0] }, objectName: 'kind bar' });
    T(s, k[1], { x: x + 0.12, y: y + 0.05, w: CWp - 0.16, h: 0.2, fontSize: 8, bold: true, color: dev ? C.accent3 : C.text2 });
    T(s, k[2], { x: x + 0.12, y: y + 0.25, w: CWp - 0.16, h: 0.16, fontSize: 6.5, bold: true, color: dev ? C.accent3 : k[0] });
    if (k[3]) T(s, k[3], { x: x + 0.12, y: y + 0.42, w: CWp - 0.16, h: Math.max(0.2, h - 0.68), fontSize: 6.5, color: C.text1 });
    const st = STT[k[4]], pw = k[4] === 2 ? 0.78 : 0.48;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + CWp - pw - 0.05, y: y + h - 0.21, w: pw, h: 0.16, rectRadius: 0.08, fill: { color: st[1] }, line: { color: k[4] === 0 ? NUM : st[1], width: 0.5 }, objectName: 'status' });
    T(s, st[0], { x: x + CWp - pw - 0.05, y: y + h - 0.21, w: pw, h: 0.16, fontSize: 5.8, bold: true, color: st[2], align: 'center', valign: 'middle' }); }); });
// 반복 고리: 재검증 불합격 → 재설계, 해석 ⇄ 재설계
const xc = i => X0 + i * (CWp + GP) + CWp / 2, LY = CY + CH + 0.13;
s.addShape(pres.shapes.LINE, { x: xc(3), y: LY, w: xc(5) - xc(3), h: 0, line: { color: X.amber, width: 1.25, dashType: 'dash' } });
[3, 4, 5].forEach(i => s.addShape(pres.shapes.LINE, { x: xc(i), y: CY + CH, w: 0, h: 0.13, line: { color: X.amber, width: 1.25, dashType: 'dash' } }));
T(s, '불합격이면 재설계로 되돌아가 기준을 만족할 때까지 반복 (해석 ⇄ 재설계 ⇄ 재검증)', { x: xc(3), y: LY + 0.02, w: xc(5) - xc(3), h: 0.18, fontSize: 6.5, bold: true, color: 'B07A1E', align: 'center' });
// 바탕 층
const BL = [['LLM 에이전트', '단계 실행 · 결과 판정 · 재설계 지시 (자동 연결은 개발 중)'], ['근거 DB', '규격 · 측정 논문 · 재료 데이터시트'], ['자동 검증 관문', '모든 단계 결과를 코드로 판정'], ['물리 모듈', '구조 · 진동 · 열 · 제조 제약 → 다음: 낙하 · 피로 · 전자기']];
BL.forEach((b, i) => { const x = 0.5 + i * 2.27;
  box(s, x, 4.38, 2.18, 0.5, X.tint, 'base');
  T(s, [{ text: b[0], options: { bold: true, color: C.text2, breakLine: true } }, { text: b[1], options: { color: C.text1 } }], { x: x + 0.1, y: 4.4, w: 2.0, h: 0.46, fontSize: 7, valign: 'middle' }); });
// 범례
const LY2 = 4.95;
[[GEN, '생성 AI'], [PHY, '물리 AI'], [NUM, '수치해석']].forEach((l, i) => { const x = 0.5 + i * 0.85;
  s.addShape(pres.shapes.RECTANGLE, { x, y: LY2 + 0.03, w: 0.06, h: 0.13, fill: { color: l[0] }, line: { color: l[0] } });
  T(s, l[1], { x: x + 0.1, y: LY2, w: 0.7, h: 0.18, fontSize: 6.5, color: C.accent3, valign: 'middle' }); });
T(s, '시연 = 이번 과제에서 실제 수행 · 시연 · 분리형 = 분리형 거치대 계열로 학습 · 시연(6쪽, 일체형 적용 진행 중) · 개발 중 = 해커톤 이후', { x: 3.1, y: LY2, w: 6.4, h: 0.18, fontSize: 6.5, color: C.accent3, valign: 'middle' });
}
s.addNotes('4쪽과 같은 여섯 단계 이름으로, 각 단계를 어떤 기술이 맡는지 보였다. 사람은 형상을 먼저 그리고 조건을 걸어 확인하지만, FormProof는 요구에서 물리 조건을 먼저 정하고 형상을 계산으로 만든다. 성능 해석과 재설계는 물리 AI(빠른 탐색)와 수치해석(정밀화)이 함께 맡고, 출력 형상을 다시 계산해 불합격이면 재설계로 돌아간다. 각 칸의 상태 표시로 이번에 실제 수행한 것과 개발 중인 것을 구분했다.');

