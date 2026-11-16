// ===== v7: 프레임워크 아키텍처
const IC2 = {
  robot: await icon(fa.FaRobot, X.white), shape: await icon(fa.FaDraftingCompass, X.teal), atom: await icon(fa.FaAtom, X.teal),
  opt: await icon(fa.FaChartLine, X.teal), ver: await icon(fa.FaClipboardCheck, X.teal), stl: await icon(fa.FaCube, X.teal),
  drw: await icon(fa.FaRulerCombined, X.teal), rep: await icon(fa.FaFileAlt, X.teal), img: await icon(fa.FaImage, X.teal),
  book: await icon(fa.FaBook, X.amber), x: await icon(fa.FaTimesCircle, X.red), ok: await icon(fa.FaCheckCircle, X.green),
};
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 기술 차별성 — FormProof 프레임워크', { placeholder: 'title' });
s.addText('AI 에이전트가 근거를 찾아 설계 명세를 만들고, 물리 도구를 직접 돌려 검증을 통과할 때까지 고친다', { placeholder: 'body' });
// input column
box(s, 0.5, 1.3, 1.55, 3.65, X.tint, 'input col');
T(s, '입력', { x: 0.5, y: 1.36, w: 1.55, h: 0.3, fontSize: 12, bold: true, color: C.accent1, align: 'center' });
[['말 · 텍스트', IC.mic], ['스케치', IC.pen], ['사진', IC.cam], ['문서 · PPT', IC.doc], ['특허 아이디어', IC.pat], ['3D 파일(STEP)', IC.step]].forEach((r, i) => {
  const y = 1.75 + i * 0.52;
  s.addImage({ data: r[1], x: 0.65, y: y + 0.04, w: 0.26, h: 0.26 });
  T(s, r[0], { x: 1.0, y, w: 1.05, h: 0.34, fontSize: 10, color: C.text2, valign: 'middle' });
});
arrow(s, 2.1, 2.0, 0.3, 0.32);
// agent box
box(s, 2.45, 1.3, 4.7, 1.55, X.ink, 'agent');
disc(s, 2.6, 1.4, 0.42, X.teal, IC2.robot, 'agent icon');
T(s, 'AI 설계 에이전트 (LLM)', { x: 3.1, y: 1.43, w: 3.9, h: 0.36, fontSize: 14, bold: true, color: C.background1, valign: 'middle' });
[['① 요구 해석', '자료 조사 → 하중·기준·재료를\n출처와 함께 설계 명세로'], ['② 도구 실행', '해석·최적화 설정과\n코드를 만들어 직접 실행'], ['③ 판정 · 수정', '기준 대비 합격 판정,\n불합격이면 수정 지시']].forEach((a, i) => {
  const x = 2.6 + i * 1.53;
  T(s, a[0], { x, y: 1.9, w: 1.45, h: 0.28, fontSize: 10.5, bold: true, color: C.accent2 });
  T(s, a[1], { x, y: 2.18, w: 1.47, h: 0.6, fontSize: 8.5, color: C.accent4 });
});
// down arrows + loop
s.addShape(pres.shapes.DOWN_ARROW, { x: 3.55, y: 2.9, w: 0.3, h: 0.28, fill: { color: C.accent2 }, line: { color: C.accent2 }, objectName: 'call' });
T(s, '도구 호출', { x: 3.9, y: 2.9, w: 1.0, h: 0.28, fontSize: 9, bold: true, color: C.accent2, valign: 'middle' });
s.addShape(pres.shapes.UP_ARROW, { x: 6.2, y: 2.9, w: 0.3, h: 0.28, fill: { color: C.accent5 }, line: { color: C.accent5 }, objectName: 'loop' });
T(s, '결과 · 불합격 사유', { x: 4.7, y: 2.9, w: 1.45, h: 0.28, fontSize: 9, bold: true, color: C.accent5, align: 'right', valign: 'middle' });
// tool row
const tools = [['형상 모듈', IC2.shape, '설계 영역 · 고정부\n· 비울 곳 3D 생성'], ['물리 엔진', IC2.atom, '유한요소 해석\n구조 · 진동 · 열'], ['최적화 엔진', IC2.opt, '3D 위상최적화\n+ 제조 제약'], ['검증 모듈', IC2.ver, '출력 형상 1 mm\n재해석 · 기준 판정']];
tools.forEach((t, i) => {
  const x = 2.45 + i * 1.19;
  box(s, x, 3.25, 1.1, 1.15, X.tint, 'tool');
  s.addImage({ data: t[1], x: x + 0.08, y: 3.33, w: 0.24, h: 0.24 });
  T(s, t[0], { x: x + 0.36, y: 3.31, w: 0.74, h: 0.3, fontSize: 9.5, bold: true, color: C.text2, valign: 'middle' });
  T(s, t[2], { x: x + 0.08, y: 3.66, w: 1.0, h: 0.66, fontSize: 8, color: C.text1 });
});
// planned strip
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 2.45, y: 4.5, w: 4.7, h: 0.45, rectRadius: 0.06, fill: { color: X.white }, line: { color: C.accent3, width: 1, dashType: 'dash' }, objectName: 'planned' });
T(s, [{ text: '계획  ', options: { bold: true, color: C.accent3 } }, { text: '물리 AI 대리모델(신경 연산자)로 계산 가속 · 형상 AI로 초기안 제안', options: { color: C.accent3 } }], { x: 2.6, y: 4.5, w: 4.5, h: 0.45, fontSize: 9, valign: 'middle' });
arrow(s, 7.2, 2.0, 0.3, 0.32);
// output col
box(s, 7.55, 1.3, 1.95, 3.65, X.tint, 'output col');
T(s, '출력', { x: 7.55, y: 1.36, w: 1.95, h: 0.3, fontSize: 12, bold: true, color: C.accent1, align: 'center' });
[['STL (출력용)', IC2.stl], ['도면', IC2.drw], ['근거 · 검증 리포트', IC2.rep], ['렌더링', IC2.img]].forEach((r, i) => {
  const y = 1.75 + i * 0.52;
  s.addImage({ data: r[1], x: 7.7, y: y + 0.04, w: 0.26, h: 0.26 });
  T(s, r[0], { x: 8.05, y, w: 1.4, h: 0.34, fontSize: 10, color: C.text2, valign: 'middle' });
});
s.addImage({ data: IC2.book, x: 7.7, y: 3.95, w: 0.24, h: 0.24 });
T(s, '근거 자료\n규격 · 재료 · 제품 분해 자료', { x: 8.0, y: 3.88, w: 1.45, h: 0.5, fontSize: 8.5, color: C.text1 });
T(s, '사람은 의도 입력과 최종 승인만', { x: 7.6, y: 4.5, w: 1.85, h: 0.45, fontSize: 9, bold: true, color: C.accent1, align: 'center', valign: 'middle' });
s.addNotes('구조: 입력 → AI 에이전트(요구 해석·도구 실행·판정) ↔ 물리 도구 4종 → 출력. 실선 박스는 이번 사례에 실제 사용한 모듈, 점선은 계획. 핵심은 에이전트가 계산 결과로 스스로 판정하고 고치는 폐루프.');

// ===== v7: 파이프라인 상세 (자전거 거치대 실제 산출물)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 파이프라인 — 자전거 거치대가 실제로 거친 6단계', { placeholder: 'title' });
s.addText('각 단계의 산출물이 다음 단계의 입력이 된다', { placeholder: 'body' });
const PW = 2.9, PH = 1.72;
const pcard = (i, title, tag) => {
  const x = 0.5 + (i % 3) * (PW + 0.15), y = 1.3 + Math.floor(i / 3) * (PH + 0.12);
  box(s, x, y, PW, PH, X.tint, 'step card');
  disc(s, x + 0.1, y + 0.1, 0.3, X.teal, null, 'num');
  T(s, String(i + 1), { x: x + 0.1, y: y + 0.1, w: 0.3, h: 0.3, fontSize: 11, bold: true, color: C.background1, align: 'center', valign: 'middle' });
  T(s, title, { x: x + 0.48, y: y + 0.1, w: PW - 0.55, h: 0.3, fontSize: 11.5, bold: true, color: C.text2, valign: 'middle' });
  if (tag) T(s, tag, { x: x + PW - 1.15, y: y + 0.1, w: 1.05, h: 0.3, fontSize: 8, color: C.accent3, align: 'right', valign: 'middle' });
  return [x, y];
};
let [px, py] = pcard(0, '입력', '말 한 줄');
T(s, '"울퉁불퉁한 길에서도 폰이 안 흔들리게, 최대한 가볍게. 3D 프린터로 뽑을 거야"', { x: px + 0.15, y: py + 0.55, w: PW - 0.3, h: 0.75, fontSize: 11, italic: true, color: C.text2 });
T(s, '+ 핸들바 Ø31.8 mm · 폰 갤럭시 S26 울트라', { x: px + 0.15, y: py + 1.32, w: PW - 0.3, h: 0.28, fontSize: 9, color: C.accent3 });
[px, py] = pcard(1, '설계 명세', 'AI 작성 · 출처 포함');
const spec = [['하중', '254 g (폰 214 + 거치부 40)'], ['진동', '1차 ≥ 91 Hz (노면 최대 45.6 Hz × 2)'], ['충격', '48.5 g (ISBS 2020 실측)'], ['재료', 'PETG 39 MPa ÷ 1.5 → 26 MPa'], ['제조', 'FDM 출력, 층간 강도 별도 확인']];
spec.forEach((r, i) => {
  T(s, r[0], { x: px + 0.15, y: py + 0.5 + i * 0.235, w: 0.45, h: 0.23, fontSize: 9, bold: true, color: C.accent1 });
  T(s, r[1], { x: px + 0.6, y: py + 0.5 + i * 0.235, w: PW - 0.7, h: 0.23, fontSize: 9, color: C.text1 });
});
[px, py] = pcard(2, '처음 설계 계산', '판정: 미달');
fit(s, SH + 'v6_c_bike_base_stress.png', px + 0.08, py + 0.45, 1.45, 1.2, 'base');
T(s, [{ text: `${BK.base_f} Hz`, options: { bold: true, color: C.accent5, fontSize: 15, breakLine: true } }, { text: '기준 91 Hz ✗', options: { fontSize: 8.5, color: C.accent3, breakLine: true } }, { text: `${BK.base_s} MPa`, options: { bold: true, color: C.accent5, fontSize: 15, breakLine: true } }, { text: '기준 26 MPa ✗', options: { fontSize: 8.5, color: C.accent3 } }], { x: px + 1.6, y: py + 0.5, w: 1.25, h: 1.15 });
[px, py] = pcard(3, '3D 위상최적화', '반복 계산');
const LG = fs.readFileSync(__dirname + '/../opt/' + (BK.log || 'd') + '.log', 'utf8').split('\n').filter(l => l.startsWith('{')).map(JSON.parse).filter((d, i) => i % 5 === 0);
s.addChart(pres.charts.LINE, [{ name: '질량', labels: LG.map(d => String(d.it)), values: LG.map(d => d.mass_g) }], {
  x: px + 0.05, y: py + 0.42, w: PW - 0.1, h: 1.05, chartColors: [X.teal], lineSize: 2, lineDataSymbol: 'none',
  catAxisLabelColor: X.mute, valAxisLabelColor: X.mute, catAxisLabelFontSize: 7, valAxisLabelFontSize: 7, catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt',
  valGridLine: { color: 'DDE5E4', size: 0.5 }, catGridLine: { style: 'none' }, showLegend: false, catAxisLabelFrequency: 8, valAxisMinVal: 0,
  showValAxisTitle: false, showCatAxisTitle: false });
T(s, `질량 ${LG[0].mass_g} → ${LG[LG.length - 1].mass_g} g (격자 기준) · 진동 기준 유지`, { x: px + 0.15, y: py + 1.45, w: PW - 0.3, h: 0.24, fontSize: 8.5, color: C.accent3 });
[px, py] = pcard(4, '출력 형상 재검증', '판정: 통과');
fit(s, SH + BK.ai_img, px + 0.08, py + 0.45, 1.45, 1.2, 'final');
[[`${BK.ai_f} Hz`, '≥ 91'], [`${BK.ai_s} MPa`, '≤ 26'], [`층간 ${BK.ai_il || 7.8}`, '≤ 10.9 MPa']].forEach((r, i) => {
  s.addImage({ data: IC2.ok, x: px + 1.6, y: py + 0.55 + i * 0.37, w: 0.18, h: 0.18 });
  T(s, [{ text: r[0], options: { bold: true, color: C.green, breakLine: true } }, { text: r[1], options: { fontSize: 8, color: C.accent3 } }], { x: px + 1.83, y: py + 0.5 + i * 0.37, w: 1.05, h: 0.36, fontSize: 10.5 });
});
[px, py] = pcard(5, '제작 파일', '');
fit(s, SH + 'v7_drw_front.png', px + 0.1, py + 0.45, PW - 0.2, 0.95, 'drawing');
T(s, `STL ${BK.ai_m} g · 도면 · 근거 리포트`, { x: px + 0.15, y: py + 1.42, w: PW - 0.3, h: 0.24, fontSize: 9, bold: true, color: C.accent1 });
T(s, '※ 2 → 5 사이에서 불합격이면 에이전트가 조건·설정을 고쳐 다시 계산. 3단계 이후 수치는 출력 형상 기준 유한요소 해석값(실측 전)', { x: 0.5, y: 4.98, w: 9, h: 0.22, fontSize: 8, color: C.accent3 });
s.addNotes('말 한 줄이 출처 있는 설계 명세가 되고, 처음 설계를 계산해 미달을 확인한 뒤, 3D 최적화로 재료를 재배치하고, 출력 형상을 다시 계산해 통과한 것만 제작 파일로 내보낸다. 실측은 데모 영상에서 다룸.');

// ===== v7: 검증 관문이 걸러낸 사례
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 기술 차별성 — 그럴듯한 형상을 검증이 걸러낸다', { placeholder: 'title' });
s.addText('이번 사례 작업 중 실제로 불합격 처리되어 다시 설계한 결과 3건', { placeholder: 'body' });
const fails = [
  ['자전거 거치대', '폭 20 mm 압출형 최적화', '출력 형상 재해석\n1차 진동 85 Hz < 기준 91 Hz', '3D 자유 형상으로 재설계\n→ 95.9 Hz 통과'],
  ['TV 스탠드 다리', '3D 격자 위상최적화', '격자보다 가는 부재 · 중간 밀도 잔존\n→ 출력 형상 재검증 3회 불합격', '판재 평면 최적화로 전환\n→ 124 g · 흔들림 0.23 mm 통과'],
  ['무선충전 방열판', '내부 방열 구조 최적화 v1', '중간 밀도(회색) 형상\n→ 실제 제작 불가 판정', '실제 제품 구조 기준 재정의\n→ 알루미늄 판금 2장 형상']];
fails.forEach((f, i) => {
  const x = 0.5 + i * 3.05;
  box(s, x, 1.3, 2.85, 3.5, X.tint, 'fail card');
  T(s, f[0], { x: x + 0.15, y: 1.4, w: 2.55, h: 0.32, fontSize: 13, bold: true, color: C.text2 });
  T(s, f[1], { x: x + 0.15, y: 1.72, w: 2.55, h: 0.28, fontSize: 9.5, color: C.accent3 });
  T(s, '계산상 그럴듯한 결과', { x: x + 0.15, y: 2.1, w: 2.55, h: 0.26, fontSize: 9, bold: true, color: C.accent3 });
  s.addImage({ data: IC2.x, x: x + 0.15, y: 2.48, w: 0.28, h: 0.28 });
  T(s, '검증 불합격', { x: x + 0.5, y: 2.47, w: 2.2, h: 0.3, fontSize: 12, bold: true, color: C.accent5, valign: 'middle' });
  T(s, f[2], { x: x + 0.15, y: 2.85, w: 2.6, h: 0.65, fontSize: 9.5, color: C.text1 });
  s.addShape(pres.shapes.DOWN_ARROW, { x: x + 1.27, y: 3.52, w: 0.3, h: 0.25, fill: { color: C.accent2 }, line: { color: C.accent2 } });
  s.addImage({ data: IC2.ok, x: x + 0.15, y: 3.88, w: 0.24, h: 0.24 });
  T(s, f[3], { x: x + 0.47, y: 3.85, w: 2.3, h: 0.7, fontSize: 9.5, bold: true, color: C.green });
});
T(s, '검증 관문이 없었다면 세 결과 모두 그대로 제작 파일이 됐을 것 — 범용 생성 AI와의 핵심 차이', { x: 0.5, y: 4.9, w: 9, h: 0.28, fontSize: 10.5, bold: true, color: C.accent1 });
s.addNotes('실제 작업 로그 기준. 검증 모듈이 출력 형상을 다시 계산하거나 제작 가능성을 판정해 불합격을 냈고, 에이전트가 방식을 바꿔 재설계했다.');
