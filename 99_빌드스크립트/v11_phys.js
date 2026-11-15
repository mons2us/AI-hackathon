// ===== v11: 생성 AI × 물리 AI 실제 학습 결과
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
const AI = JSON.parse(fs.readFileSync(__dirname + '/ai_v11.json', 'utf8'));
s.addText('2. 생성 AI × 물리 AI — 거치대 계열로 실제 학습한 결과', { placeholder: 'title' });
s.addText(`두 AI가 약 ${AI.search_s}초 만에 데이터보다 ${Math.round((1 - AI.cand_m / AI.start_m) * 100)}% 가벼운 후보를 찾고, 정밀화와 최종 판정은 수치해석이 맡는다`, { placeholder: 'body' });
const CW = 2.9, cardY = 1.28, cardH = 2.62;
const card = (i, t, kind, kc) => { const x = 0.5 + i * (CW + 0.15); box(s, x, cardY, CW, cardH, X.tint, 'ai card');
  T(s, t, { x: x + 0.12, y: cardY + 0.07, w: CW - 0.24, h: 0.26, fontSize: 11, bold: true, color: C.text2 });
  T(s, kind, { x: x + 0.12, y: cardY + 0.33, w: CW - 0.24, h: 0.2, fontSize: 8, bold: true, color: kc }); return x; };
let cx = card(0, '① 형상 AI — 형상을 잠재 변수로', 'DeepSDF 방식 생성 모델', GEN);
['v11_c_D1.png', 'v11_c_D0.png', 'v11_c_D474.png'].forEach((f, k) => fit(s, SH + f, cx + 0.08 + k * 0.92, cardY + 0.6, 0.9, 0.75, 'sample'));
T(s, [{ text: `거치대 계열 형상 ${AI.n_data}개`, options: { bold: true, breakLine: true } }, { text: '각 형상을 FEM으로 계산해 학습 데이터로 사용', options: { color: C.accent3, breakLine: true } }, { text: '잠재 변수 16개로 형상 표현 · 보간', options: { bold: true, breakLine: true } }, { text: `학습 형상 재구성 IoU ${AI.iou}`, options: { color: C.accent3 } }], { x: cx + 0.12, y: cardY + 1.45, w: CW - 0.24, h: 1.1, fontSize: 9, color: C.text1, paraSpaceAfter: 2 });
cx = card(1, '② 물리 AI — 형상 → 1차 진동수', '3D 합성곱 신경망', C.accent1);
s.addChart(pres.charts.SCATTER, [{ name: 'FEM', values: AI.scat_t }, { name: '물리 AI 예측', values: AI.scat_p }, { name: '일치선', values: AI.scat_t }], {
  x: cx + 0.02, y: cardY + 0.52, w: CW - 0.04, h: 1.42, chartColors: [X.teal, X.mute], lineSize: 0, lineDataSymbolSize: 4, showLegend: false,
  valAxisMinVal: 0, valAxisMaxVal: 180, catAxisMinVal: 0, catAxisMaxVal: 180, valAxisLabelFontSize: 7, catAxisLabelFontSize: 7, valAxisLabelColor: X.mute, catAxisLabelColor: X.mute,
  valAxisLabelFontFace: '+mn-lt', catAxisLabelFontFace: '+mn-lt', valGridLine: { color: 'DDE5E4', size: 0.5 }, catGridLine: { style: 'none' },
  showValAxisTitle: true, valAxisTitle: '예측 (Hz)', valAxisTitleFontSize: 7, valAxisTitleColor: X.mute, showCatAxisTitle: true, catAxisTitle: 'FEM (Hz)', catAxisTitleFontSize: 7, catAxisTitleColor: X.mute });
T(s, [{ text: `오차 평균 ${AI.err50}%`, options: { bold: true, color: C.accent1, fontSize: 12 } }, { text: `  ≥ 50 Hz 구간 ${AI.test_n50}개`, options: { color: C.accent3 } }], { x: cx + 0.12, y: cardY + 1.98, w: CW - 0.24, h: 0.26, fontSize: 8.5, valign: 'middle' });
T(s, `1회 예측 약 ${AI.infer_s}초 (같은 형상 FEM 약 2초)`, { x: cx + 0.12, y: cardY + 2.26, w: CW - 0.24, h: 0.24, fontSize: 8.5, color: C.text1 });
cx = card(2, '③ 잠재 공간 탐색 — 형상 AI × 물리 AI', '미분으로 잠재 변수 조정', C.accent1);
fit(s, SH + 'v11_c_C1.png', cx + 0.1, cardY + 0.58, 1.3, 0.95, 'candidate');
T(s, [{ text: `${AI.start_m} → ${AI.cand_m} g`, options: { bold: true, color: GEN, fontSize: 13, breakLine: true } }, { text: '데이터 최선 → AI 후보', options: { color: C.accent3, fontSize: 8 } }], { x: cx + 1.45, y: cardY + 0.68, w: 1.4, h: 0.7 });
T(s, [{ text: `예측 ${AI.pred_f} Hz · FEM ${AI.fem_f} Hz`, options: { bold: true, breakLine: true } }, { text: `후보 1개 약 ${AI.search_s}초 · ${AI.ncand}개 중 ${AI.npass}개 FEM 통과`, options: { breakLine: true } }, { text: '(진동 기준 91 Hz)', options: { color: C.accent3 } }], { x: cx + 0.12, y: cardY + 1.62, w: CW - 0.24, h: 0.9, fontSize: 9, color: C.text1 });
// flow strip
const FL = [[`데이터 최선`, `${AI.start_m} g`, X.mute], [`AI 탐색 후보 (${AI.search_s}초)`, `${AI.cand_m} g · ${AI.fem_f} Hz`, GEN], ['출력 형상 재검증', `${AI.cand_out_f} Hz → 미달`, X.red], ['자유 형상 정밀화 (약 25분)', `${BK.ai_m} g · ${BK.ai_f} Hz 통과`, X.green]];
FL.forEach((f, i) => { const x = 0.5 + i * 2.32;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 4.02, w: 2.05, h: 0.62, rectRadius: 0.06, fill: { color: 'FFFFFF' }, line: { color: f[2], width: 1.5 }, objectName: 'flow box' });
  T(s, f[0], { x: x + 0.08, y: 4.06, w: 1.9, h: 0.24, fontSize: 8.5, color: C.accent3, align: 'center' });
  T(s, f[1], { x: x + 0.08, y: 4.3, w: 1.9, h: 0.3, fontSize: 11, bold: true, color: f[2], align: 'center' });
  if (i < 3) arrow(s, x + 2.08, 4.2, 0.2, 0.26); });
T(s, '※ CPU 2코어 · GPU 없음. 탐색 단계 질량 · 진동수는 2 mm 격자 FEM(폰+거치부 250 g), 최종 설계는 출력 형상 1 mm 재해석(254 g). 정밀화는 같은 조건의 3D 위상 최적화(출력 방향 제약)로 별도 실행', { x: 0.5, y: 4.72, w: 9, h: 0.4, fontSize: 7.5, color: C.accent3 });
s.addNotes('형상 AI는 거치대 계열 형상을 잠재 변수 16개로 압축하고, 물리 AI는 형상에서 1차 진동수를 0.2초에 예측한다(사용 구간 오차 평균 약 7%). 둘을 이어 잠재 변수를 미분으로 조정하면 데이터에 있던 가장 가벼운 합격 설계보다 11% 가벼운 후보가 약 40초에 나온다. 다만 출력 형상으로 다시 계산하면 86 Hz로 미달이라, 자유 형상 정밀화가 41.7 g · 93.7 Hz로 마무리한다. AI는 빠른 탐색, 판정은 수치해석.');
