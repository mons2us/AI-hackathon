// ---------- 3. 문제 정의 (v41: 제안서의 네 장벽을 '아이디어 → 제작' 경로 위에 배치)
pres.addSection({ title: '1. 문제 정의' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '1. 문제 정의' });
s.addText('1. 문제 정의 — 아이디어가 검증된 설계가 되기까지, 네 곳에서 막힌다', { placeholder: 'title' });
s.addText('막히는 곳마다 필요한 도구와 전문가가 다르다 — 구조 · 열 · 광학 · 회로, 분야가 바뀌어도 같은 길이다', { placeholder: 'body' });
// 경로 띠: 아이디어 → 3D 설계 → 성능 확인 → 개선 → 제작
const STEP = ['아이디어\n말 · 스케치 · 특허', '3D 설계', '성능 확인', '더 나은 구조', '제작'];
const SW = 1.72, SG = 0.1;
STEP.forEach((t, i) => { const x = 0.5 + i * (SW + SG);
  s.addShape(i === 0 ? pres.shapes.PENTAGON : pres.shapes.CHEVRON, { x, y: 1.24, w: SW, h: 0.46, fill: { color: i === 0 ? X.ink : X.tint }, line: { color: i === 0 ? X.ink : X.line, width: 0.5 }, objectName: 'path step' });
  T(s, t, { x: x + 0.2, y: 1.24, w: SW - 0.4, h: 0.46, fontSize: i === 0 ? 8.5 : 10, bold: true, color: i === 0 ? X.white : C.text2, align: 'center', valign: 'middle' }); });
['①', '②', '③'].forEach((n, k) => { const x = 0.5 + (k + 1) * (SW + SG) + SW - 0.42;
  s.addShape(pres.shapes.OVAL, { x, y: 1.15, w: 0.22, h: 0.22, fill: { color: X.red }, line: { color: X.white, width: 1 }, objectName: 'path barrier' });
  T(s, n, { x, y: 1.15, w: 0.22, h: 0.22, fontSize: 8, bold: true, color: X.white, align: 'center', valign: 'middle' }); });
// 장벽 카드 4개 (①②③은 경로의 각 단계 아래, ④는 경로를 건너뛰려는 지름길)
const BC = [
  { no: '①', head: '말 · 스케치를 3D 설계로 옮기기', sub: '치수 측정 · CAD 도구 숙련이 있어야 시작', img: 'v17_sketch.png', foot: '머릿속 형태로는 계산할 수 없다' },
  { no: '②', head: '만들기 전에 성능 확인', sub: '분야마다 다른 해석 도구 · 조건 설정', big: [['67%', '외부 해석 결과까지 1주 이상'], ['45%', '일정 때문에 해석 생략']], foot: '대개 만들어 보고 고치기를 반복' },
  { no: '③', head: '성능을 지키며 더 나은 구조로', sub: '해석 · 최적화 전문 지식과 시간', big: [['43%', '설계 시간 중 변경에 쓰는 비율']], note: '가볍게 하면 약해지고, 보강하면 무거워진다 — 그 균형점을 찾는 것이 최적화', foot: '전문 조직에서도 개선은 사람이 반복' },
  { no: '④', head: '지름길: 범용 LLM 단독', sub: '같은 요청, 도구 없이 독립 3회 (우리 실험)', img: 'v38_L3.png', big: [['3 / 3', '불합격'], ['6.6배', '흔들림 (스스로 예측 1.3배)']], foot: '틀려도 그대로 제시, 판별 어려움' }];
const BW = 2.16, BG = 0.12, BY = 1.86, BH = 2.5;
BC.forEach((c, i) => { const x = 0.5 + i * (BW + BG), last = i === 3;
  box(s, x, BY, BW, BH, last ? 'FBF1EF' : 'FFFFFF', 'barrier card');
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: BY, w: BW, h: BH, rectRadius: 0.08, fill: { type: 'none' }, line: { color: last ? 'E5B8B2' : X.line, width: 0.75, dashType: last ? 'dash' : 'solid' }, objectName: 'barrier frame' });
  s.addShape(pres.shapes.OVAL, { x: x + 0.1, y: BY + 0.1, w: 0.3, h: 0.3, fill: { color: X.red }, line: { color: X.red }, objectName: 'barrier no' });
  T(s, c.no, { x: x + 0.1, y: BY + 0.1, w: 0.3, h: 0.3, fontSize: 10, bold: true, color: X.white, align: 'center', valign: 'middle' });
  T(s, c.head, { x: x + 0.46, y: BY + 0.06, w: BW - 0.54, h: 0.4, fontSize: 9.5, bold: true, color: C.text2, valign: 'middle' });
  T(s, c.sub, { x: x + 0.1, y: BY + 0.5, w: BW - 0.2, h: 0.2, fontSize: 7.5, color: C.accent3 });
  let y = BY + 0.74;
  if (c.img) { const ih = c.big ? 0.72 : 1.3;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.1, y, w: BW - 0.2, h: ih, rectRadius: 0.04, fill: { color: 'FFFFFF' }, line: { color: X.line, width: 0.5 }, objectName: 'img' });
    fit(s, SH + c.img, x + 0.12, y + 0.02, BW - 0.24, ih - 0.04, c.head); y += ih + 0.06; }
  if (c.big) {
    if (c.img) { c.big.forEach((b, k) => { const bx = x + 0.1 + k * (BW - 0.2) / 2, bw = (BW - 0.2) / 2;
        T(s, b[0], { x: bx, y, w: bw, h: 0.34, fontSize: 16, bold: true, color: C.accent5 });
        T(s, b[1], { x: bx, y: y + 0.34, w: bw - 0.04, h: 0.3, fontSize: 7, color: C.text1 }); }); }
    else { c.big.forEach((b, k) => { const by = y + k * 0.62;
        T(s, b[0], { x: x + 0.1, y: by, w: BW - 0.2, h: 0.36, fontSize: 20, bold: true, color: C.accent5 });
        T(s, b[1], { x: x + 0.1, y: by + 0.36, w: BW - 0.2, h: 0.22, fontSize: 8, color: C.text1 }); }); }
  }
  if (c.note) { box(s, x + 0.1, y + 0.7, BW - 0.2, 0.6, X.tint, 'note');
    T(s, c.note, { x: x + 0.18, y: y + 0.7, w: BW - 0.36, h: 0.6, fontSize: 8, color: C.text2, valign: 'middle' }); }
  s.addShape(pres.shapes.LINE, { x: x + 0.1, y: BY + BH - 0.42, w: BW - 0.2, h: 0, line: { color: X.line, width: 0.5 } });
  T(s, c.foot, { x: x + 0.1, y: BY + BH - 0.38, w: BW - 0.2, h: 0.32, fontSize: 8, bold: true, color: last ? C.accent5 : C.text2, valign: 'middle' }); });
// 공통 원인 → 다음 쪽
box(s, 0.5, 4.46, 9.0, 0.44, X.ink, 'cause');
T(s, [{ text: '공통 원인  ', options: { bold: true, color: C.accent4 } }, { text: '단계마다 도구 · 전문가가 나뉘어 있고, 아이디어에서 검증된 제작 파일까지 한 번에 이어 주는 것이 없다', options: { color: C.background1 } }],
  { x: 0.65, y: 4.46, w: 8.7, h: 0.44, fontSize: 10.5, valign: 'middle' });
T(s, '※ ②③ engineering.com · Dassault 「State of Simulation, Prototyping and Validation」(엔지니어 268명, 연도 확인 필요), Tech-Clarity 「Revolutionizing Simulation for Design Engineers」 2019 — 해외 업계 조사 · 해석 SW사 후원. ④ 같은 요청 · 같은 조건을 받은 독립 세션 3회를 같은 해석기로 판정(17쪽). ① 정성 기술 · 그림은 이번 과제의 입력 스케치', { x: 0.5, y: 4.96, w: 9, h: 0.3, fontSize: 6.5, color: C.accent3 });
s.addNotes('제안서에서 정의한 네 장벽을 아이디어에서 제작까지의 경로 위에 놓았다. ① 말이나 스케치로는 계산을 할 수 없어서, 치수를 재고 CAD로 옮기는 것부터 숙련이 필요하다. ② 만들기 전 성능 확인은 분야마다 다른 해석 도구와 조건 설정이 필요하고, 전문 조직에서도 67%가 외부 해석 결과를 1주 넘게 기다리며 45%는 일정 때문에 생략한다. ③ 성능을 지키며 더 나은 구조로 바꾸는 것도 전문 지식의 영역이고, 설계 시간의 43%가 변경에 쓰인다. ④ 범용 LLM에게 통째로 맡기면 빠르지만, 같은 요청 3번 모두 불합격이었고 스스로 1.3배라 예측한 흔들림이 실제 6.6배였다. 틀려도 그대로 제시되므로 비전문가는 판별할 수 없다. 공통 원인은 단계마다 도구와 전문가가 나뉘어 있다는 것 — 다음 쪽에서 기존 기술이 각각 어느 단계만 맡는지 비교한다.');
