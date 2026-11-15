// ===== v12: 형상이 만들어지는 과정 (위상 최적화 반복)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
const EV = JSON.parse(fs.readFileSync(__dirname + '/evo_v12.json', 'utf8'));
s.addText('2. 실증 ① 자전거 거치대 — 형상은 계산이 만든다', { placeholder: 'title' });
s.addText('설계 공간을 재료로 채운 뒤, 매 반복 진동을 계산해 기준을 지키는 한도에서 덜 필요한 재료를 덜어낸다', { placeholder: 'body' });
const FW = 1.43;
EV.frames.forEach((f, i) => {
  const x = 0.5 + i * (FW + 0.08);
  box(s, x, 1.3, FW, 1.78, i === EV.frames.length - 1 ? 'E3F1F0' : X.tint, 'frame');
  fit(s, SH + f.img, x + 0.05, 1.36, FW - 0.1, 1.05, 'iteration ' + f.it);
  T(s, i === 0 ? '시작' : i === EV.frames.length - 1 ? `최종 (${f.it + 1}회)` : `${f.it}회`, { x: x + 0.08, y: 2.43, w: FW - 0.16, h: 0.22, fontSize: 9.5, bold: true, color: C.text2 });
  T(s, `${f.mass} g · ${f.f1} Hz`, { x: x + 0.08, y: 2.67, w: FW - 0.16, h: 0.22, fontSize: 9, bold: true, color: i === EV.frames.length - 1 ? C.accent1 : C.accent3 });
  if (i < EV.frames.length - 1) arrow(s, x + FW - 0.02, 1.85, 0.11, 0.18);
});
// 질량 · 진동 곡선
s.addChart(pres.charts.LINE, [{ name: '무게 (g)', labels: EV.it.map(String), values: EV.mass }], {
  x: 0.45, y: 3.15, w: 4.5, h: 1.75, chartColors: [X.teal], lineSize: 2, lineDataSymbol: 'none', showLegend: false, showTitle: true, title: '무게 (g) — 반복할수록 감소', titleFontSize: 9, titleColor: X.ink, titleFontFace: '+mn-lt',
  catAxisLabelColor: X.mute, valAxisLabelColor: X.mute, catAxisLabelFontSize: 7, valAxisLabelFontSize: 7, catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt',
  valGridLine: { color: 'DDE5E4', size: 0.5 }, catGridLine: { style: 'none' }, catAxisLabelFrequency: 5, catAxisLabelRotate: 0, valAxisMinVal: 0 });
s.addChart(pres.charts.LINE, [{ name: '1차 진동수', labels: EV.it.map(String), values: EV.f1 }, { name: '기준', labels: EV.it.map(String), values: EV.it.map(() => 91) }], {
  x: 4.95, y: 3.15, w: 2.6, h: 1.75, chartColors: [X.amber, X.red], lineSize: 2, lineDataSymbol: 'none', showLegend: false, showTitle: true, title: '1차 진동수 (Hz) — 기준 91 유지', titleFontSize: 9, titleColor: X.ink, titleFontFace: '+mn-lt',
  catAxisLabelColor: X.mute, valAxisLabelColor: X.mute, catAxisLabelFontSize: 7, valAxisLabelFontSize: 7, catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt',
  valGridLine: { color: 'DDE5E4', size: 0.5 }, catGridLine: { style: 'none' }, catAxisLabelFrequency: 10, catAxisLabelRotate: 0, valAxisMinVal: 60, valAxisMaxVal: 120 });
const how = [['1', '설계 공간', '클램프 · 받침판은 고정, 나머지를 재료 밀도 변수로'], ['2', '매 반복 계산', 'FEM으로 진동 모드와 민감도 계산'], ['3', '재료 재배치', '진동 기준을 지키며 무게 최소화 (MMA)'], ['4', '출력 제약', '아래가 비어 45°를 넘는 재료 금지']];
how.forEach((h, i) => { const y = 3.2 + i * 0.43;
  disc(s, 7.68, y + 0.02, 0.26, X.teal, null, 'step');
  T(s, h[0], { x: 7.68, y: y + 0.02, w: 0.26, h: 0.26, fontSize: 9, bold: true, color: C.background1, align: 'center', valign: 'middle' });
  T(s, h[1], { x: 8.02, y, w: 1.55, h: 0.18, fontSize: 8.5, bold: true, color: C.text2 });
  T(s, h[2], { x: 8.02, y: y + 0.18, w: 1.55, h: 0.24, fontSize: 7, color: C.accent3 }); });
T(s, `※ 그림 = 재료 밀도 0.5 이상 영역, 수치 = 최적화 중 2 mm 격자 값(폰+거치부 254 g). 최종 출력 형상 재해석: ${BK.ai_m} g · ${BK.ai_f} Hz. CPU 2코어 약 ${EV.minutes}분`, { x: 0.5, y: 4.95, w: 9, h: 0.22, fontSize: 7.5, color: C.accent3 });
s.addNotes('사람이 모양을 그린 것이 아니라, 계산이 재료를 덜어내며 만든 형상이다. 처음에는 설계 공간 전체가 재료로 차 있고, 반복할 때마다 FEM으로 진동을 계산해 진동 기준(91 Hz)을 지키는 한도에서 기여가 작은 재료를 줄인다. 출력 방향 제약 때문에 아래가 비어 있는 재료는 생기지 않는다.');

// ===== v12: 결과 — 장착 모습과 도면
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 실증 ① 자전거 거치대 — 장착 모습과 제작 도면', { placeholder: 'title' });
s.addText('핸들바 클램프 + 폰 거치부 체결 구조까지 포함한 출력용 형상, 도면은 자동 생성', { placeholder: 'body' });
box(s, 0.5, 1.3, 3.4, 2.4, X.tint, 'side');
fit(s, SH + 'v12_c_mnt_side.png', 0.6, 1.38, 3.2, 2.24, 'mount side view');
box(s, 0.5, 3.8, 3.4, 1.35, X.tint, 'bike');
fit(s, SH + 'v12_c_mnt_bike.png', 0.6, 3.85, 1.7, 1.25, 'on bike');
T(s, [{ text: `${BK.ai_m} g`, options: { bold: true, color: C.accent1, fontSize: 16, breakLine: true } }, { text: 'PETG · 옆으로 눕혀 출력', options: { fontSize: 8.5, color: C.accent3, breakLine: true } }, { text: '받침대 없음 (45° 규칙)', options: { fontSize: 8.5, color: C.accent3 } }], { x: 2.35, y: 3.98, w: 1.5, h: 1.0 });
box(s, 4.05, 1.3, 5.45, 3.85, 'FFFFFF', 'drawing frame');
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 4.05, y: 1.3, w: 5.45, h: 3.85, rectRadius: 0.06, fill: { type: 'none' }, line: { color: X.line, width: 1 } });
fit(s, '/tmp/claude-0/-home-claude/e964ed80-ee1b-5f91-abd3-3081682a3ad7/scratchpad/out/FormProof_자전거거치대_도면_v4.png', 4.1, 1.35, 5.35, 3.75, 'drawing');
s.addNotes('왼쪽 위: 핸들바 클램프에 거치대가 물리고, 그 위 받침판에 폰 거치부가 체결된다. 왼쪽 아래: 자전거 장착 모습. 오른쪽: 자동 생성 도면(정면 · 평면 · 우측면, 클램프 Ø32.2, M4 볼트 2조, 폰 클램프 인서트 Ø8). 자유 형상부 치수는 STL 기준.');
