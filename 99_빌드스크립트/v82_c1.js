// ===== v82: 핵심 기술 ① — 요청 → 물리 조건 (과정 + 출처 추적)
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 핵심 기술 ① — 말을 계산할 수 있는 물리 조건으로', { placeholder: 'title' });
s.addText('LLM은 계산하지 않는다 — 뜻을 해석하고, 수치는 근거 DB에서만 고르며, 출처가 없으면 묻는다', { placeholder: 'body' });
{
// 과정 띠
const PS = [['요청 + 스케치', '말 한 줄 · 손 그림', X.mute], ['뜻 해석', 'LLM: 표현 → 물리량', GEN], ['근거 검색', '근거 DB에서 수치 선택', GEN], ['설계 명세', '값마다 출처 · 형식 검사', GEN], ['빠진 조건 질문', '출처 없으면 묻기', X.amber], ['계산 기준', '엔진 입력 (JSON)', X.ink]];
const PW = 1.44, PG = 0.08;
PS.forEach((p, i) => { const x = 0.5 + i * (PW + PG);
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.2, w: PW, h: 0.5, rectRadius: 0.06, fill: { color: i === 5 ? X.ink : 'FFFFFF' }, line: { color: p[2], width: 1.25 }, objectName: 'proc' });
  T(s, [{ text: p[0], options: { bold: true, color: i === 5 ? X.amber : p[2], breakLine: true } }, { text: p[1], options: { fontSize: 6.8, color: i === 5 ? X.white : C.text1 } }], { x, y: 1.2, w: PW, h: 0.5, fontSize: 8.5, align: 'center', valign: 'middle' });
  if (i < 5) s.addShape(pres.shapes.LINE, { x: x + PW, y: 1.45, w: PG, h: 0, line: { color: X.mute, width: 1.25, endArrowType: 'triangle' } }); });
// 요청 카드
box(s, 0.5, 1.88, 2.15, 2.62, X.ink, 'request');
T(s, '처음 요청', { x: 0.62, y: 1.95, w: 1.9, h: 0.22, fontSize: 8.5, bold: true, color: C.accent4 });
T(s, '"울퉁불퉁한 길에서도 폰이 안 흔들리게, 최대한 가볍게. 3D 프린터로 뽑을 거야"', { x: 0.62, y: 2.18, w: 1.95, h: 1.1, fontSize: 11, italic: true, bold: true, color: C.background1 });
fit(s, SH + 'v17_sketch.png', 0.6, 3.36, 1.95, 1.08, 'input sketch');
// 결과 표: 출처 종류 칩
const SRC = { 텍스트: '6B4FA0', 스케치: '6B4FA0', 'DB': X.teal, 가정: X.amber, 질문: X.red };
const RQ = [
  ['"안 흔들리게"', '핸들바 → 폰 진동 전달 최소', '10–100 Hz 전달률 · 1차 진동수 ≥ 95 Hz', [['DB', '조약돌길 실측 ISBS 2020']]],
  ['"울퉁불퉁한 길"', '충격에도 안 부러짐', '48.5 g 충격 · 응력 ≤ 26 MPa', [['DB', '같은 실측 · PETG 39 MPa ÷ 1.5']]],
  ['"최대한 가볍게"', '무게 최소', '출력 몸체 무게 (g)', [['텍스트', '요청 문장']]],
  ['"모든 폰"', '폭 64–90 · 두께 6–14 mm · ≤ 290 g', '4면 고정 · 폰 + 부품 311 g 강체', [['DB', '시판 폰 범위']]],
  ['스케치 "35°쯤"', '거치 각도', '35°', [['스케치', '근사값'], ['질문', '맞나요?']]],
  ['"열 안 갇히게"', '폰 발열이 갇히지 않게', '폰 온도 상승 ≤ 21 °C', [['가정', '발열 4 W'], ['질문', '맞나요?']]]];
const RX = [2.82, 4.0, 5.62, 7.42], RW = [1.15, 1.6, 1.78, 2.08], RY = 1.88, RH = 0.4;
['표현', '물리 해석', '판정 지표', '출처'].forEach((h, k) => T(s, h, { x: RX[k], y: RY, w: RW[k], h: 0.22, fontSize: 8.5, bold: true, color: C.accent1 }));
RQ.forEach((r, i) => { const y = RY + 0.26 + i * (RH + 0.03);
  box(s, 2.76, y, 6.74, RH, i % 2 ? 'FFFFFF' : X.tint, 'row');
  [0, 1, 2].forEach(k => T(s, r[k], { x: RX[k], y, w: RW[k] - 0.06, h: RH, fontSize: k === 0 ? 8.5 : 7.5, bold: k === 0, color: C.text1, valign: 'middle' }));
  let cx = RX[3]; r[3].forEach(([kind, txt]) => { const pw = 0.42;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx, y: y + RH / 2 - 0.085, w: pw, h: 0.17, rectRadius: 0.085, fill: { color: SRC[kind] }, line: { color: SRC[kind] }, objectName: 'src' });
    T(s, kind === 'DB' ? '근거 DB' : kind, { x: cx, y: y + RH / 2 - 0.085, w: pw, h: 0.17, fontSize: 5.8, bold: true, color: X.white, align: 'center', valign: 'middle' });
    const tw = r[3].length > 1 ? 0.55 : 1.6; T(s, txt, { x: cx + pw + 0.04, y, w: tw, h: RH, fontSize: 6.8, color: C.accent3, valign: 'middle' }); cx += pw + 0.04 + tw + 0.04; }); });
// 아래: 제작 조건 + 질문
box(s, 0.5, 4.62, 4.45, 0.5, 'FFF6E8', 'make');
T(s, [{ text: '제작 조건  ', options: { bold: true, color: C.accent2 } }, { text: '"3D 프린터" → 요구가 아니라 설계 제약: 출력 방향 · 층간 강도 · 최소 두께를 계산에 포함', options: { color: C.text1 } }], { x: 0.6, y: 4.62, w: 4.3, h: 0.5, fontSize: 7.5, valign: 'middle' });
box(s, 5.05, 4.62, 4.45, 0.5, X.tint, 'q');
T(s, [{ text: '사용자에게 묻는다  ', options: { bold: true, color: X.red } }, { text: '"핸들바 지름 31.8 mm 맞나요?" · "35°로 계산할까요?" · "발열 4 W로 둘까요?"', options: { color: C.text1 } }], { x: 5.15, y: 4.62, w: 4.3, h: 0.5, fontSize: 7.5, valign: 'middle' });
}
s.addNotes('핵심 기술 ①. LLM은 요청의 뜻을 물리량으로 해석하지만 수치를 만들어 내지 않는다. 수치는 근거 DB(실측 논문 · 규격 · 데이터시트)에서만 고르고, 모든 값에 출처 종류(텍스트 · 스케치 · 근거 DB · 가정)를 붙인다. 근거가 없으면 사용자에게 묻는다. 결과는 형식 검사를 통과한 JSON으로 계산 엔진에 넘어간다. 범용 LLM 단독이 틀린 이유(스스로 정한 기준 · 어림 계산)를 구조적으로 막는 부분이다.');

