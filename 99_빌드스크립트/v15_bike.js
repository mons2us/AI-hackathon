// ===== v14: 요청 한 줄 → 설계 명세 (메인 사례)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 실증 ① 자전거 거치대 — 요청 한 줄을 물리 조건으로', { placeholder: 'title' });
s.addText('말의 뜻을 계산할 수 있는 지표로 바꾸고, 각 수치에 출처를 붙인다', { placeholder: 'body' });
box(s, 0.5, 1.3, 2.35, 2.55, X.ink, 'request');
T(s, '처음 요청', { x: 0.65, y: 1.42, w: 2.1, h: 0.24, fontSize: 9.5, bold: true, color: C.accent4 });
T(s, '"울퉁불퉁한 길에서도 폰이 안 흔들리게, 최대한 가볍게. 3D 프린터로 뽑을 거야"', { x: 0.65, y: 1.7, w: 2.1, h: 1.15, fontSize: 12.5, italic: true, bold: true, color: C.background1 });
T(s, '추가 요청', { x: 0.65, y: 2.95, w: 2.1, h: 0.22, fontSize: 9.5, bold: true, color: C.accent4 });
T(s, '받침대도 설계 · 모든 폰을 잡을 것 · 방열', { x: 0.65, y: 3.17, w: 2.1, h: 0.55, fontSize: 9.5, color: C.background1 });
arrow(s, 2.92, 2.4, 0.26, 0.34);
const RQ = [
  ['"안 흔들리게"', '핸들바 → 폰 진동 전달 최소', '10–100 Hz 평균 전달률 · 최대 공진 배율', '조약돌길 실측, 중앙 진동수 34.6–45.6 Hz (ISBS 2020)'],
  ['"울퉁불퉁한 길"', '충격 48.5 g에도 안 부러짐', '응력 ≤ 26 MPa · 층간 ≤ 10.9 MPa', '같은 실측 · PETG 항복 39 MPa ÷ 1.5'],
  ['"최대한 가볍게"', '무게 최소', '거치대 g · 받침대 ≤ 60 g', '—'],
  ['"모든 폰"', '폭 64–90 · 두께 6–14 mm · ≤ 290 g', '좌우 스프링 집게 + 아래 받침 턱', '케이스 포함 시판 범위 (폴더블 펼침 제외)'],
  ['"방열"', '폰 발열이 받침대에 갇히지 않게', '폰 뒷면 온도 상승', '발열 4 W · 주행풍 가정 (확인 필요)']];
const RX = [3.28, 4.45, 6.0, 7.7], RW = [1.15, 1.53, 1.68, 1.82];
['표현', '물리 해석', '판정 지표', '근거'].forEach((h, k) => T(s, h, { x: RX[k], y: 1.3, w: RW[k], h: 0.24, fontSize: 9, bold: true, color: C.accent1 }));
RQ.forEach((r, i) => { const y = 1.58 + i * 0.47;
  box(s, 3.22, y, 6.28, 0.42, i % 2 ? 'FFFFFF' : X.tint, 'req row');
  r.forEach((c, k) => T(s, c, { x: RX[k], y: y + 0.02, w: RW[k] - 0.05, h: 0.38, fontSize: k === 0 ? 9.5 : 8, bold: k === 0, color: k === 3 ? C.accent3 : C.text1, valign: 'middle' })); });
box(s, 0.5, 4.08, 9.0, 0.62, 'FFF6E8', 'make cond');
T(s, [{ text: '제작 조건 (요구사항이 아니라 설계 제약)  ', options: { bold: true, color: C.accent2 } }, { text: '3D 프린터 · PETG · 받침대 없이 출력 → 45° 넘는 돌출 금지, 출력 방향 층간 강도를 계산에 포함', options: { color: C.text1 } }], { x: 0.65, y: 4.12, w: 8.7, h: 0.27, fontSize: 9.5, valign: 'middle' });
T(s, '모델 가정: 폰+받침대 340 g를 크기 · 관성이 있는 강체(165×80×15 mm)로, 감쇠비 3% — 실측으로 교체 예정 항목', { x: 0.65, y: 4.4, w: 8.7, h: 0.25, fontSize: 8.5, color: C.accent3, valign: 'middle' });
s.addNotes('출발점은 사용자의 말 한 줄. "안 흔들리게"는 흔들림을 최소화하라는 뜻이므로 핸들바에서 폰으로 가는 진동 전달률을 지표로 삼았다. 노면 진동 근거는 ISBS 2020 조약돌길 실측. 3D 프린터는 요구가 아니라 제작 조건이라 설계 제약(45° 돌출 금지, 층간 강도)으로 넣었다. 감쇠비 · 폰 크기 등은 가정이며 팀 측정으로 교체한다.');

// ===== v14: 말 한 줄에서 제작 파일까지 (6단계)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 실증 ① 자전거 거치대 — 말 한 줄에서 제작 파일까지', { placeholder: 'title' });
s.addText('각 단계의 산출물이 다음 단계의 입력이 된다', { placeholder: 'body' });
const QW = 2.9, QH = 1.72;
const qcard = (i, title, tag) => {
  const x = 0.5 + (i % 3) * (QW + 0.15), y = 1.3 + Math.floor(i / 3) * (QH + 0.12);
  box(s, x, y, QW, QH, X.tint, 'step card');
  disc(s, x + 0.1, y + 0.1, 0.3, X.teal, null, 'num');
  T(s, String(i + 1), { x: x + 0.1, y: y + 0.1, w: 0.3, h: 0.3, fontSize: 11, bold: true, color: C.background1, align: 'center', valign: 'middle' });
  T(s, title, { x: x + 0.48, y: y + 0.1, w: QW - 0.55, h: 0.3, fontSize: 11.5, bold: true, color: C.text2, valign: 'middle' });
  if (tag) T(s, tag, { x: x + QW - 1.15, y: y + 0.1, w: 1.05, h: 0.3, fontSize: 8, color: C.accent3, align: 'right', valign: 'middle' });
  return [x, y]; };
let [qx, qy] = qcard(0, '입력', '말 한 줄');
T(s, '"울퉁불퉁한 길에서도 폰이 안 흔들리게, 최대한 가볍게. 3D 프린터로 뽑을 거야"', { x: qx + 0.15, y: qy + 0.55, w: QW - 0.3, h: 0.75, fontSize: 11, italic: true, color: C.text2 });
T(s, '+ 핸들바 Ø31.8 mm · 폭 64–90 mm 모든 폰', { x: qx + 0.15, y: qy + 1.32, w: QW - 0.3, h: 0.28, fontSize: 9, color: C.accent3 });
[qx, qy] = qcard(1, '설계 명세', 'AI 작성 · 출처 포함');
[['하중', '폰+받침대 340 g · 관성 포함 강체'], ['흔들림', '10–100 Hz 전달률 최소 (ISBS 2020)'], ['충격', '48.5 g (같은 실측)'], ['재료', 'PETG 39 MPa ÷ 1.5 → 26 MPa'], ['제작', '받침대 없이 출력 · 층간 강도']].forEach((r, i) => {
  T(s, r[0], { x: qx + 0.15, y: qy + 0.5 + i * 0.235, w: 0.5, h: 0.23, fontSize: 9, bold: true, color: C.accent1 });
  T(s, r[1], { x: qx + 0.65, y: qy + 0.5 + i * 0.235, w: QW - 0.75, h: 0.23, fontSize: 9, color: C.text1 }); });
[qx, qy] = qcard(2, '처음 설계 계산', '판정: 미달');
fit(s, SH + 'v6_c_bike_base_stress.png', qx + 0.08, qy + 0.45, 1.45, 1.2, 'base');
T(s, [{ text: '11.2배', options: { bold: true, color: C.accent5, fontSize: 15, breakLine: true } }, { text: '최대 흔들림 (17.8 Hz 공진)', options: { fontSize: 8, color: C.accent3, breakLine: true } }, { text: '43.1 MPa', options: { bold: true, color: C.accent5, fontSize: 15, breakLine: true } }, { text: '충격 응력 > 26', options: { fontSize: 8, color: C.accent3 } }], { x: qx + 1.58, y: qy + 0.48, w: 1.3, h: 1.2 });
[qx, qy] = qcard(3, '3D 위상최적화', '반복 계산');
const EV4 = JSON.parse(fs.readFileSync(__dirname + '/evo_v14.json', 'utf8'));
s.addChart(pres.charts.LINE, [{ name: '무게', labels: EV4.it.map(String), values: EV4.mass }], {
  x: qx + 0.05, y: qy + 0.42, w: QW - 0.1, h: 1.05, chartColors: [X.teal], lineSize: 2, lineDataSymbol: 'none',
  catAxisLabelColor: X.mute, valAxisLabelColor: X.mute, catAxisLabelFontSize: 7, valAxisLabelFontSize: 7, catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt',
  valGridLine: { color: 'DDE5E4', size: 0.5 }, catGridLine: { style: 'none' }, showLegend: false, catAxisLabelFrequency: 10, catAxisLabelRotate: 0, valAxisMinVal: 0 });
T(s, `무게 ${EV4.mass[0]} → ${EV4.mass[EV4.mass.length - 1]} g (격자) · 1차 ≥ 95 Hz 유지`, { x: qx + 0.15, y: qy + 1.45, w: QW - 0.3, h: 0.24, fontSize: 8.5, color: C.accent3 });
[qx, qy] = qcard(4, '출력 형상 재검증', '판정: 통과');
fit(s, SH + 'v14_e_159.png', qx + 0.08, qy + 0.45, 1.45, 1.2, 'final');
[['1.1배', '최대 흔들림'], ['9.4 MPa', '충격 ≤ 26'], ['층간 2.9', '≤ 10.9 MPa']].forEach((r, i) => {
  s.addImage({ data: IC2.ok, x: qx + 1.6, y: qy + 0.55 + i * 0.37, w: 0.18, h: 0.18 });
  T(s, [{ text: r[0], options: { bold: true, color: C.green, breakLine: true } }, { text: r[1], options: { fontSize: 8, color: C.accent3 } }], { x: qx + 1.83, y: qy + 0.5 + i * 0.37, w: 1.05, h: 0.36, fontSize: 10.5 }); });
[qx, qy] = qcard(5, '제작 파일', '');
fit(s, SH + 'v14_join.png', qx + 0.1, qy + 0.45, QW - 0.2, 0.95, 'mount and cradle');
T(s, '거치대 STL 30.6 g · 받침대 STL 3종', { x: qx + 0.15, y: qy + 1.42, w: QW - 0.3, h: 0.24, fontSize: 9, bold: true, color: C.accent1 });
T(s, '※ 3단계 이후 수치 = 출력 형상 1 mm 유한요소 재해석(실측 전). 흔들림 = 핸들바 대비 폰 진동 배율, 감쇠비 3% 가정. 불합격이면 에이전트가 조건 · 설정을 고쳐 다시 계산', { x: 0.5, y: 4.98, w: 9, h: 0.22, fontSize: 7.5, color: C.accent3 });
s.addNotes('말 한 줄이 출처 있는 설계 명세가 되고, 처음 설계를 계산하면 17.8 Hz에서 공진해 흔들림이 최대 11.2배로 커지고 충격 응력도 허용치를 넘는다. 3D 위상최적화로 재료를 재배치한 뒤 출력 형상을 다시 계산해 통과한 것만 제작 파일로 내보낸다.');

// ===== v14: 형상이 만들어지는 과정
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 실증 ① 자전거 거치대 — 형상은 계산이 만든다', { placeholder: 'title' });
s.addText('설계 공간을 재료로 채운 뒤, 매 반복 진동을 계산해 공진을 노면 대역 밖에 두는 한도에서 재료를 덜어낸다', { placeholder: 'body' });
const FW4 = 1.43;
EV4.frames.forEach((f, i) => { const x = 0.5 + i * (FW4 + 0.08), last = i === EV4.frames.length - 1;
  box(s, x, 1.3, FW4, 1.78, last ? 'E3F1F0' : X.tint, 'frame');
  fit(s, SH + f.img, x + 0.05, 1.36, FW4 - 0.1, 1.05, 'iteration ' + f.it);
  T(s, i === 0 ? '시작' : last ? `최종 (${f.it + 1}회)` : `${f.it}회`, { x: x + 0.08, y: 2.43, w: FW4 - 0.16, h: 0.22, fontSize: 9.5, bold: true, color: C.text2 });
  T(s, `${f.mass} g · ${f.f1} Hz`, { x: x + 0.08, y: 2.67, w: FW4 - 0.16, h: 0.22, fontSize: 9, bold: true, color: last ? C.accent1 : C.accent3 });
  if (!last) arrow(s, x + FW4 - 0.02, 1.85, 0.11, 0.18); });
s.addChart(pres.charts.LINE, [{ name: '무게 (g)', labels: EV4.it.map(String), values: EV4.mass }], {
  x: 0.45, y: 3.15, w: 4.5, h: 1.75, chartColors: [X.teal], lineSize: 2, lineDataSymbol: 'none', showLegend: false, showTitle: true, title: '무게 (g) — 반복할수록 감소', titleFontSize: 9, titleColor: X.ink, titleFontFace: '+mn-lt',
  catAxisLabelColor: X.mute, valAxisLabelColor: X.mute, catAxisLabelFontSize: 7, valAxisLabelFontSize: 7, catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt',
  valGridLine: { color: 'DDE5E4', size: 0.5 }, catGridLine: { style: 'none' }, catAxisLabelFrequency: 5, catAxisLabelRotate: 0, valAxisMinVal: 0 });
s.addChart(pres.charts.LINE, [{ name: '1차 진동수', labels: EV4.it.map(String), values: EV4.f1 }, { name: '하한', labels: EV4.it.map(String), values: EV4.it.map(() => 95) }], {
  x: 4.95, y: 3.15, w: 2.6, h: 1.75, chartColors: [X.amber, X.red], lineSize: 2, lineDataSymbol: 'none', showLegend: false, showTitle: true, title: '1차 진동수 (Hz) — 95 이상 유지', titleFontSize: 9, titleColor: X.ink, titleFontFace: '+mn-lt',
  catAxisLabelColor: X.mute, valAxisLabelColor: X.mute, catAxisLabelFontSize: 7, valAxisLabelFontSize: 7, catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt',
  valGridLine: { color: 'DDE5E4', size: 0.5 }, catGridLine: { style: 'none' }, catAxisLabelFrequency: 10, catAxisLabelRotate: 0, valAxisMinVal: 40, valAxisMaxVal: 120 });
[['1', '설계 공간', '클램프 · 받침판은 고정, 나머지를 재료 밀도 변수로'], ['2', '매 반복 계산', '폰을 관성 있는 강체로 넣고 진동 모드 · 민감도 계산'], ['3', '재료 재배치', '공진을 노면 대역 위에 두며 무게 최소화 (MMA)'], ['4', '출력 제약', '아래가 비어 45°를 넘는 재료 금지']].forEach((h, i) => { const y = 3.2 + i * 0.43;
  disc(s, 7.68, y + 0.02, 0.26, X.teal, null, 'step');
  T(s, h[0], { x: 7.68, y: y + 0.02, w: 0.26, h: 0.26, fontSize: 9, bold: true, color: C.background1, align: 'center', valign: 'middle' });
  T(s, h[1], { x: 8.02, y, w: 1.55, h: 0.18, fontSize: 8.5, bold: true, color: C.text2 });
  T(s, h[2], { x: 8.02, y: y + 0.18, w: 1.55, h: 0.24, fontSize: 7, color: C.accent3 }); });
T(s, `※ 그림 = 재료 밀도 0.5 이상 영역, 수치 = 최적화 중 2 mm 격자 값(폰+받침대 340 g 강체). 최종 출력 형상 재해석: 30.6 g · 98.5 Hz. CPU 2코어 약 ${EV4.minutes}분`, { x: 0.5, y: 4.95, w: 9, h: 0.22, fontSize: 7.5, color: C.accent3 });
s.addNotes('모양을 미리 정해 둔 것이 아니라, 계산이 재료를 덜어내며 만든 형상이다. 반복마다 폰의 무게와 회전 관성까지 넣어 진동을 계산하고, 1차 진동수를 노면 진동(중앙 34.6~45.6 Hz)보다 충분히 높은 95 Hz 이상에 둔 채 기여가 작은 재료를 줄인다. 초반 블록이 클램프와 짧은 팔만 남은 형상으로 줄어든다.');

// ===== v14: 무게 ↔ 흔들림
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 실증 ① 자전거 거치대 — 가벼우면서 덜 흔들리게', { placeholder: 'title' });
s.addText('같은 위치에서는 무게와 흔들림이 맞바뀌지만, 폰 받침 위치를 핸들바 쪽으로 당기니 둘 다 좋아졌다', { placeholder: 'body' });
box(s, 0.5, 1.28, 9.0, 3.5, 'FFFFFF', 'pareto');
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 1.28, w: 9.0, h: 3.5, rectRadius: 0.06, fill: { type: 'none' }, line: { color: X.line, width: 1 } });
fit(s, SH + 'v14_pareto.png', 0.55, 1.32, 8.9, 3.42, 'transmissibility and pareto');
T(s, '※ 흔들림 = 핸들바 대비 폰 진동 배율(위아래, 감쇠비 3% 가정). 모든 안을 같은 해석기 · 같은 하중(폰+받침대 340 g 강체)으로 계산. 평균 = 10–100 Hz RMS', { x: 0.5, y: 4.88, w: 9, h: 0.3, fontSize: 8, color: C.accent3 });
s.addNotes('왼쪽: 처음 설계는 18 Hz와 77 Hz에서 공진해 최대 11배 흔들린다. 최적화한 설계는 10–100 Hz 전체에서 1배 근처로 평평하다. 오른쪽: 받침 90 mm 위치에서는 진동수 목표를 올릴수록 덜 흔들리지만 무거워진다(맞바꿈). 받침을 40 mm로 당기니 30.6 g에 평균 1.03배로, 곡선 자체가 아래로 내려갔다.');

// ===== v14: 결과 — 처음 설계 대비
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 실증 ① 자전거 거치대 — 32% 가볍고, 공진은 사라졌다', { placeholder: 'title' });
s.addText('받침 위치 비교: 같은 조건에서 계산이 고른 형상 (오른쪽이 최종)', { placeholder: 'body' });
box(s, 0.5, 1.28, 9.0, 2.55, X.tint, 'arm compare');
fit(s, SH + 'v14_arm.png', 0.6, 1.33, 8.8, 2.45, 'pad position comparison');
const MET4 = [['무게', 44.7, 30.6, 'g', null, '처음 설계와 같은 클램프'], ['최대 흔들림', 11.2, 1.1, '배', null, '10–100 Hz 중 최대'], ['충격 응력', 43.1, 9.4, 'MPa', 26, '기준 ≤ 26 MPa']];
MET4.forEach((m, i) => { const x = 0.5 + i * 3.05, y = 3.98, W = 2.85, mx = Math.max(m[1], m[2], m[4] || 0) * 1.1;
  T(s, m[0] + '  ' + m[5], { x, y, w: W, h: 0.24, fontSize: 10, bold: true, color: C.text2 });
  [[m[1], X.mute, '처음'], [m[2], X.teal, 'AI']].forEach((b, k) => { const by = y + 0.28 + k * 0.27, bw = Math.max((W - 0.95) * b[0] / mx, 0.02);
    T(s, b[2], { x, y: by, w: 0.3, h: 0.22, fontSize: 9, color: C.accent3, valign: 'middle' });
    s.addShape(pres.shapes.RECTANGLE, { x: x + 0.32, y: by + 0.03, w: bw, h: 0.16, fill: { color: b[1] }, line: { color: b[1] } });
    T(s, `${b[0]} ${m[3]}`, { x: x + 0.36 + bw, y: by, w: 0.75, h: 0.22, fontSize: 9, bold: true, color: b[1] === X.teal ? C.accent1 : C.accent3, valign: 'middle' }); });
  if (m[4]) { const lx = x + 0.32 + (W - 0.95) * m[4] / mx; s.addShape(pres.shapes.LINE, { x: lx, y: y + 0.26, w: 0, h: 0.56, line: { color: X.red, width: 1.25, dashType: 'dash' } }); } });
T(s, '※ 출력 형상 1 mm 재해석, 폰+받침대 340 g. 응력은 99.9% 값(48.5 g 충격, 두 방향 중 큰 값), 층간 응력 2.9 MPa ≤ 10.9. 받침대 없이 출력(45° 규칙, 격자 기준). 앞뒤 방향 최대 흔들림은 2.6배(98 Hz) — 개선 대상', { x: 0.5, y: 4.9, w: 9, h: 0.3, fontSize: 7.5, color: C.accent3 });
s.addNotes('받침 위치를 핸들바 앞 90 mm에 두면 79.3 g이 필요했지만, 40 mm로 당기니 30.6 g으로 더 덜 흔들린다. 처음 설계 대비 무게 32% 감소, 최대 흔들림 11.2배 → 1.1배, 충격 응력 43.1 → 9.4 MPa. 앞뒤 방향은 98 Hz에서 2.6배가 남아 있어 다음 개선 대상으로 표시.');

// ===== v14: 복합물리 받침대
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 실증 ① 범용 폰 받침대 — 구조와 열을 한 번에', { placeholder: 'title' });
s.addText('충격 강성과 폰 발열을 동시에 계산해 재료를 배치 — 평판과 같은 처짐을 27% 가볍게, 온도 상승은 37 → 20 °C', { placeholder: 'body' });
box(s, 0.5, 1.28, 4.65, 3.6, 'FFFFFF', 'cradle cmp');
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 1.28, w: 4.65, h: 3.6, rectRadius: 0.06, fill: { type: 'none' }, line: { color: X.line, width: 1 } });
fit(s, SH + 'v14_cradle_cmp.png', 0.55, 1.32, 4.55, 3.52, 'cradle comparison');
box(s, 5.3, 1.28, 4.2, 2.2, X.tint, 'cradle asm');
fit(s, SH + 'v14_cradle_asm.png', 5.35, 1.32, 4.1, 2.12, 'cradle assembly');
const CR = [['폰 범위', '폭 64–90 · 두께 6–14 mm · ≤ 290 g (케이스 포함)'], ['잡는 방식', '좌우 스프링 집게 + 아래 받침 턱 · 해제 레버'], ['무게', '뼈대 28.0 g · 집게 · 레버 · 스프링 포함 약 46 g (≤ 60 g)'], ['열', '폰 뒷면을 비워 주행풍에 노출 (윗층 빈 곳 = 냉각면)'], ['결합', '거치대와 1/4 회전 잠금']];
CR.forEach((r, i) => { const y = 3.58 + i * 0.26;
  T(s, r[0], { x: 5.35, y, w: 0.85, h: 0.25, fontSize: 8.5, bold: true, color: C.accent1, valign: 'middle' });
  T(s, r[1], { x: 6.2, y, w: 3.3, h: 0.25, fontSize: 8.5, color: C.text1, valign: 'middle' }); });
T(s, '※ 구조 + 정상 열전도 연성 해석(2 mm 격자), 설계 의존 대류 · 민감도는 차분으로 검증. 충격 138 N(폰 290 g × 48.5 g), 발열 4 W · PETG 열전도 0.2 W/m·K · 주행풍 23 W/m²K는 가정. 스프링 무게는 확인 필요', { x: 0.5, y: 4.95, w: 9, h: 0.25, fontSize: 7.5, color: C.accent3 });
s.addNotes('받침대는 폰을 잡는 강성과 폰 열을 빼는 일이 동시에 걸린다. 평판은 폰 뒷면을 덮어 열이 갇히고(+37 °C), 구조만 최적화하면 강성은 좋지만 무게가 그대로다. 구조와 열을 같이 최적화하니 평판과 같은 처짐(0.25 mm)을 29.9 g으로 내면서 온도 상승을 20 °C로 낮췄다. 흔히 쓰는 정형 형태(X자 · H자 · 구멍 판 등 6가지)와도 같은 무게 · 같은 조건으로 비교해 확인했다.');

// ===== v15: 일체형 — 물리 검증이 쓸 수 없는 형상을 걸러냄
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 실증 ① 일체형 — 물리 검증이 "쓸 수 없는 형상"을 걸러냈다', { placeholder: 'title' });
s.addText('35° 일체형 1차 결과에는 폰을 잡는 형상이 없었다 — 충격 계산으로 이탈을 확인, 4면 고정으로 재설계', { placeholder: 'body' });
box(s, 0.5, 1.28, 3.0, 3.3, X.tint, 'nogrip card');
pill(s, 0.62, 1.36, 1.05, '1차 결과', X.mute, X.white);
fit(s, SH + 'v15_nogrip.png', 0.6, 1.72, 2.8, 2.2, 'no grip');
T(s, '폰을 판에 붙어 있다고 가정 —\n옆면 · 앞면을 잡는 형상 없음', { x: 0.62, y: 3.98, w: 2.76, h: 0.5, fontSize: 9, color: C.text1, align: 'center' });
box(s, 3.65, 1.28, 2.7, 3.3, 'FFFFFF', 'force card');
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 3.65, y: 1.28, w: 2.7, h: 3.3, rectRadius: 0.08, fill: { type: 'none' }, line: { color: X.line, width: 1 } });
T(s, '충격 순간 폰이 위로 빠지는 힘', { x: 3.77, y: 1.38, w: 2.46, h: 0.26, fontSize: 10, bold: true, color: C.text2 });
const FB = [['빠지는 힘 (위쪽)', 79, X.red], ['집게 마찰로 버티는 힘', 11, X.mute]];
FB.forEach((f, i) => { const y = 1.78 + i * 0.62, bw = 2.2 * f[1] / 85;
  T(s, f[0], { x: 3.77, y, w: 2.4, h: 0.22, fontSize: 8.5, color: C.accent3 });
  s.addShape(pres.shapes.RECTANGLE, { x: 3.77, y: y + 0.24, w: bw, h: 0.2, fill: { color: f[2] }, line: { color: f[2] } });
  T(s, i ? '3 ~ 11 N' : '79 N', { x: 3.82 + bw, y: y + 0.22, w: 0.9, h: 0.24, fontSize: 10, bold: true, color: f[2], valign: 'middle' }); });
T(s, '→ 집게만으로는 폰이 위로 미끄러져 빠짐\n→ 화면 쪽으로도 113 N이 걸림', { x: 3.77, y: 3.1, w: 2.5, h: 0.5, fontSize: 9, bold: true, color: C.accent1 });
T(s, '해결: 위 · 아래 걸이로 길이 방향을 막고, 집게는 잠금 나사로 고정', { x: 3.77, y: 3.72, w: 2.5, h: 0.6, fontSize: 9, color: C.text1 });
box(s, 6.5, 1.28, 3.0, 3.3, 'E3F1F0', 'grip card');
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.5, y: 1.28, w: 3.0, h: 3.3, rectRadius: 0.08, fill: { type: 'none' }, line: { color: X.teal, width: 2 } });
pill(s, 6.62, 1.36, 1.05, '재설계', X.teal, X.white);
fit(s, SH + 'v15_grip.png', 6.6, 1.72, 2.8, 2.2, 'grip');
T(s, '아래 · 위 걸이 + 양옆 스프링 집게\n+ 잠금 나사 — 4면 고정', { x: 6.62, y: 3.98, w: 2.76, h: 0.5, fontSize: 9, bold: true, color: C.accent1, align: 'center' });
T(s, '※ 충격 48.5 g(ISBS 2020 조약돌길) × 폰 290 g = 138 N을 35° 기울기로 나눔: 위쪽 79 N, 화면 쪽 113 N. 버티는 힘 = 마찰계수 0.3 × 스프링 힘 5–18 N × 양쪽 — 마찰계수 · 스프링 힘은 가정(확인 필요)', { x: 0.5, y: 4.68, w: 9, h: 0.4, fontSize: 7.5, color: C.accent3 });
s.addNotes('1차 일체형 결과는 계산상 폰을 판에 붙어 있다고 놓았기 때문에, 실제로 폰을 잡는 형상이 없었다. 충격 하중을 기울기 방향으로 나눠 보면 폰이 위로 빠지려는 힘이 79 N인데, 스프링 집게 마찰로는 3~11 N밖에 버티지 못한다. 그래서 아래 · 위 걸이로 길이 방향을 막고 양옆 집게는 잠금 나사로 고정하는 4면 고정으로 바꾸고, 이 부품들을 고정 영역으로 넣어 몸체를 다시 최적화했다.');

// ===== v15: 제작형 결과 — 초기 설계 대비 (같은 걸이 · 집게 · 레일)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 실증 ① 일체형 결과 — 14% 가볍고, 공진은 사라졌다', { placeholder: 'title' });
s.addText('폰을 잡는 부품까지 넣은 같은 조건에서 초기 설계와 비교 — 출력용 몸체 기준', { placeholder: 'body' });
box(s, 0.5, 1.28, 4.7, 3.6, 'FFFFFF', 'result img');
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 1.28, w: 4.7, h: 3.6, rectRadius: 0.06, fill: { type: 'none' }, line: { color: X.line, width: 1 } });
fit(s, SH + 'v15_result.png', 0.6, 1.36, 4.5, 3.15, 'initial vs optimized');
T(s, '초기 설계', { x: 0.6, y: 4.55, w: 2.1, h: 0.25, fontSize: 9, color: C.accent3, align: 'center' });
T(s, '최적화 → 출력용 몸체', { x: 2.85, y: 4.55, w: 2.3, h: 0.25, fontSize: 9, bold: true, color: C.accent1, align: 'center' });
const MET5 = [['무게', 94.9, 81.3, 'g', null, '출력 몸체'], ['최대 흔들림', 5.6, 1.4, '배', null, '10–100 Hz · 두 방향 중 큰 값'], ['폰 온도 상승', 32.6, 20.7, '°C', 21, '제한 21 °C'], ['충격 층간 응력', 17.5, 3.9, 'MPa', 10.9, '허용 10.9 MPa']];
MET5.forEach((m, i) => { const x = 5.4, y = 1.28 + i * 0.9, W = 4.1, mx = Math.max(m[1], m[2], m[4] || 0) * 1.1;
  T(s, m[0] + '  ', { x, y, w: W, h: 0.24, fontSize: 10, bold: true, color: C.text2 });
  T(s, m[5], { x: x + 1.5, y, w: W - 1.5, h: 0.24, fontSize: 8, color: C.accent3, align: 'right' });
  [[m[1], X.mute, '처음'], [m[2], X.teal, 'AI']].forEach((b, k) => { const by = y + 0.28 + k * 0.27, bw = Math.max((W - 1.0) * b[0] / mx, 0.02);
    T(s, b[2], { x, y: by, w: 0.3, h: 0.22, fontSize: 9, color: C.accent3, valign: 'middle' });
    s.addShape(pres.shapes.RECTANGLE, { x: x + 0.32, y: by + 0.03, w: bw, h: 0.16, fill: { color: b[1] }, line: { color: b[1] } });
    T(s, `${b[0]} ${m[3]}`, { x: x + 0.36 + bw, y: by, w: 0.75, h: 0.22, fontSize: 9, bold: true, color: b[1] === X.teal ? C.accent1 : C.accent3, valign: 'middle' }); });
  if (m[4]) { const lx = x + 0.32 + (W - 1.0) * m[4] / mx; s.addShape(pres.shapes.LINE, { x: lx, y: y + 0.26, w: 0, h: 0.56, line: { color: X.red, width: 1.25, dashType: 'dash' } }); } });
T(s, '※ 폰 + 집게 · 걸이 · 스프링 · 나사 311 g 강체, 감쇠비 3%, 거치 35°, 발열 4 W 가정. 무게 = 출력용 STL 부피 × PETG 1.27 g/cm³ (최적화 결과 77.1 g + 정밀 하우징 · 걸이 보강). 흔들림 · 응력 = 최적화 결과 2 mm 격자 해석(출력 형상 재해석 최대 1.27배). 평균 흔들림 1.19 → 1.12배', { x: 0.5, y: 4.95, w: 9, h: 0.3, fontSize: 7.5, color: C.accent3 });
s.addNotes('폰을 잡는 걸이 · 집게 · 레일을 같은 조건으로 넣고 초기 설계와 비교했다. 초기 설계는 30.5 Hz에서 공진해 최대 5.6배 흔들리고 폰 온도가 32.6 °C 오른다. 최적화한 몸체는 81.3 g으로 14% 가볍고, 최대 흔들림 1.4배, 온도 상승 20.7 °C, 충격 층간 응력 3.9 MPa. 강도 점검에서 걸이 · 집게 연결부 3곳이 약해 보강했고, 보강 후 모두 허용치 이내다.');

// ===== v15: 제작 구성
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 실증 ① 제작 구성 — 출력 4개 + 시판 부품', { placeholder: 'title' });
s.addText('몸체는 최적화 형상과 레일 · 걸이를 한 덩어리로 출력, 폰 크기 차이는 슬라이드 부품이 흡수', { placeholder: 'body' });
box(s, 0.5, 1.28, 4.6, 1.75, 'FFFFFF', 'side');
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 1.28, w: 4.6, h: 3.6, rectRadius: 0.06, fill: { type: 'none' }, line: { color: X.line, width: 1 } });
fit(s, SH + 'v15_grip_side.png', 0.6, 1.33, 2.0, 3.5, 'side view');
fit(s, SH + 'v15_jaw.png', 2.65, 1.6, 2.4, 3.0, 'jaw detail');
T(s, '옆에서', { x: 0.6, y: 4.6, w: 2.0, h: 0.22, fontSize: 8, color: C.accent3, align: 'center' });
T(s, '집게부 (주황 = 출력 슬라이드 부품)', { x: 2.65, y: 4.6, w: 2.4, h: 0.22, fontSize: 8, color: C.accent3, align: 'center' });
const BOM = [['출력', '몸체 × 1', '최적화 형상 + 집게 하우징 + 위쪽 레일 + 아래 걸이 (일체)'], ['출력', '슬라이드 집게 × 2', '3.6 g씩 · 스프링 포켓 · 안쪽 면 기울여 화면 쪽 이탈 방지'], ['출력', '위쪽 슬라이드 걸이 × 1', '8.3 g · 25 mm 이동 · M3 나사로 잠금'],
  ['구매', '압축 스프링 × 2', '바깥지름 5 mm, 자유 길이 약 28 mm (사양 확인 필요)'], ['구매', 'M3 볼트 · 너트', '스프링 멈춤 핀 2 + 잠금 나사 3'], ['구매', 'M4 볼트 · 너트 × 1', '핸들바 조임']];
BOM.forEach((r, i) => { const y = 1.28 + i * 0.42;
  pill(s, 5.3, y + 0.05, 0.55, r[0], r[0] === '출력' ? X.teal : X.amber, X.white);
  T(s, r[1], { x: 5.95, y, w: 3.55, h: 0.2, fontSize: 9.5, bold: true, color: C.text2 });
  T(s, r[2], { x: 5.95, y: y + 0.2, w: 3.55, h: 0.2, fontSize: 8, color: C.text1 }); });
box(s, 5.3, 3.86, 4.2, 1.02, X.tint, 'fit range');
[['대응 폰', '폭 64–90 · 두께 6–14 · 길이 145–170 mm · ≤ 290 g'], ['핸들바', '지름 31.8 mm'], ['출력', 'PETG · 채움 100% (해석 가정과 동일)']].forEach((r, i) => { const y = 3.93 + i * 0.3;
  T(s, r[0], { x: 5.42, y, w: 0.8, h: 0.28, fontSize: 9, bold: true, color: C.accent1, valign: 'middle' });
  T(s, r[1], { x: 6.2, y, w: 3.25, h: 0.28, fontSize: 9, color: C.text1, valign: 'middle' }); });
s.addNotes('출력 부품은 몸체, 슬라이드 집게 2개, 위쪽 걸이 4개다. 몸체에는 최적화 형상과 집게 하우징, 위쪽 레일, 아래 걸이가 한 덩어리로 들어간다. 폰 폭 차이는 스프링 집게가, 길이 차이는 위쪽 슬라이드 걸이가 흡수한다. 시판 부품은 스프링 2개와 M3 · M4 나사뿐이다. 해석은 채움 100%로 했으므로 출력도 채움 100%로 한다. 145 mm보다 짧은 폰은 대응하지 않는다.');
