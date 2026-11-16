// ---------- 3. 문제 정의 (v40: 아이디어는 누구나, 검증된 설계는 전문가만)
pres.addSection({ title: '1. 문제 정의' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '1. 문제 정의' });
s.addText('1. 문제 정의 — 아이디어는 누구나 있지만, 검증된 설계는 전문가만 만든다', { placeholder: 'title' });
s.addText('구조 · 열 · 광학 · 회로 어느 분야든, 아이디어를 성능이 확인된 설계로 바꾸려면 전문 도구 · 숙련 · 시간이 필요하다', { placeholder: 'body' });
// 누가 (띠)
box(s, 0.5, 1.25, 9.0, 0.42, X.tint, 'who');
T(s, [{ text: '누가  ', options: { bold: true, color: C.accent1 } }, { text: '제품 · 패널 · 광학 · 회로 설계자,  특허 · 신사업 아이디어를 가진 직원,  만들어 보고 싶은 비전문가', options: { color: C.text1 } }],
  { x: 0.62, y: 1.25, w: 8.8, h: 0.42, fontSize: 10, valign: 'middle' });
const PC = [
  { no: '①', head: '검증은 전문가와 시간에 묶여 있다', sub: '업계 조사 — 전문 설계 조직에서도', big: [['67%', '외부 해석 결과까지 1주 이상'], ['45%', '일정 때문에 해석을 생략'], ['43%', '설계 시간 중 변경에 쓰는 비율']] },
  { no: '②', head: '생성 AI는 형상만 주고 성능은 모른다', sub: '같은 요청, 범용 LLM 단독 3회 (우리 실험)', img: 'v38_L3.png', big: [['3 / 3', '불합격'], ['6.6배', '흔들림 (예측 1.3배)']] },
  { no: '③', head: '그래서 아이디어는 검증 전에 멈춘다', sub: '비전문가는 확인할 길이 없고, 전문가도 반복한다', bul: ['CAD · 해석 도구를 다룰 줄 알아야 시작 가능', '하중 · 기준 같은 물리 조건을 스스로 정해야 함', '결과가 맞는지 판단하려면 다시 전문가가 필요', '특허 아이디어도 실제 성능은 확인하지 못한 채 제출'] }];
PC.forEach((c, i) => { const x = 0.5 + i * 3.05, y = 1.78, W = 2.9, H = 2.6;
  box(s, x, y, W, H, i === 1 ? X.tint : 'FFFFFF', 'prob card');
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: W, h: H, rectRadius: 0.08, fill: { type: 'none' }, line: { color: X.line, width: 0.75 }, objectName: 'prob frame' });
  T(s, c.no + ' ' + c.head, { x: x + 0.12, y: y + 0.08, w: W - 0.24, h: 0.42, fontSize: 10.5, bold: true, color: C.text2 });
  T(s, c.sub, { x: x + 0.12, y: y + 0.5, w: W - 0.24, h: 0.2, fontSize: 7.5, color: C.accent3 });
  if (c.img) {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.1, y: y + 0.74, w: W - 0.2, h: 1.0, rectRadius: 0.04, fill: { color: 'FFFFFF' }, line: { color: X.line, width: 0.5 }, objectName: 'img' });
    fit(s, SH + c.img, x + 0.12, y + 0.76, W - 0.24, 0.96, c.head);
    c.big.forEach((b, k) => { const bx = x + 0.12 + k * (W - 0.24) / 2;
      T(s, b[0], { x: bx, y: y + 1.82, w: (W - 0.24) / 2, h: 0.4, fontSize: 18, bold: true, color: C.accent5 });
      T(s, b[1], { x: bx, y: y + 2.22, w: (W - 0.24) / 2, h: 0.3, fontSize: 8, color: C.text1 }); });
  } else if (c.big) {
    c.big.forEach((b, k) => { const by = y + 0.82 + k * 0.58;
      T(s, b[0], { x: x + 0.12, y: by, w: 0.95, h: 0.5, fontSize: 20, bold: true, color: C.accent5, valign: 'middle' });
      T(s, b[1], { x: x + 1.1, y: by, w: W - 1.2, h: 0.5, fontSize: 9, color: C.text1, valign: 'middle' }); });
  } else {
    T(s, c.bul.map((t, k) => ({ text: t, options: { bullet: true, breakLine: k < c.bul.length - 1 } })), { x: x + 0.12, y: y + 0.8, w: W - 0.24, h: 1.7, fontSize: 9, color: C.text1, paraSpaceAfter: 6, valign: 'top' });
  } });
box(s, 0.5, 4.48, 9.0, 0.44, X.ink, 'need');
T(s, [{ text: '필요한 것  ', options: { bold: true, color: C.accent4 } }, { text: '누구나 아이디어를 넣으면, 물리로 검증된 · 바로 만들 수 있는 설계가 나오는 것', options: { color: C.background1 } }],
  { x: 0.65, y: 4.48, w: 8.7, h: 0.44, fontSize: 11, valign: 'middle' });
T(s, '※ ① engineering.com · Dassault 「State of Simulation, Prototyping and Validation」(엔지니어 268명, 연도 확인 필요), Tech-Clarity 「Revolutionizing Simulation for Design Engineers」 2019 — 해외 업계 조사 · 해석 SW사 후원. ② 도구 없이 같은 요청 · 같은 조건을 받은 독립 세션 3회, 같은 해석기로 판정(17쪽). ③ 정성 기술', { x: 0.5, y: 4.96, w: 9, h: 0.3, fontSize: 6.5, color: C.accent3 });
s.addNotes('문제는 한 문장: 아이디어는 누구나 있지만, 성능이 검증된 설계는 전문가만 만든다. 구조 · 열 · 광학 · 회로 어느 분야든 마찬가지다. ① 전문 설계 조직에서도 외부 해석 결과를 받는 데 67%가 1주 이상, 45%는 일정 때문에 해석을 생략하고, 설계 시간의 43%를 변경에 쓴다. ② 생성 AI는 형상은 빠르게 주지만 성능을 확인하지 않는다 — 같은 요청에 LLM 단독 3번 모두 불합격, 스스로 1.3배라 예측한 흔들림이 실제 6.6배. ③ 그래서 비전문가는 시작조차 어렵고, 특허 아이디어도 성능 확인 없이 제출된다. 필요한 것은 누구나 아이디어를 넣으면 물리로 검증된, 바로 만들 수 있는 설계가 나오는 것.');

