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
