// ===== v11: 범용 LLM 단독 vs FormProof
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 범용 LLM 단독 vs FormProof — 같은 요청, 같은 검증', { placeholder: 'title' });
s.addText('도구 없이 설계한 LLM 3회는 기준부터 낮게 잡았고, 같은 해석기로 계산하니 3건 모두 근거 기준 미달', { placeholder: 'body' });
const LL = JSON.parse(fs.readFileSync(__dirname + '/llm_v11.json', 'utf8'));
const LW = 2.12;
LL.forEach((d, i) => {
  const x = 0.5 + i * (LW + 0.15), fp = d.fp;
  box(s, x, 1.3, LW, 3.25, fp ? 'E3F1F0' : X.tint, 'llm card');
  if (fp) s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.3, w: LW, h: 3.25, rectRadius: 0.08, fill: { type: 'none' }, line: { color: X.teal, width: 2 }, objectName: 'fp frame' });
  T(s, d.name, { x: x + 0.1, y: 1.36, w: LW - 0.2, h: 0.26, fontSize: 11, bold: true, color: fp ? C.accent1 : C.text2 });
  T(s, d.desc, { x: x + 0.1, y: 1.6, w: LW - 0.2, h: 0.22, fontSize: 8, color: C.accent3 });
  fit(s, SH + d.img, x + 0.08, 1.85, LW - 0.16, 1.05, 'design ' + d.name);
  const rows = [['진동 기준', d.crit, fp ? C.accent1 : C.text1], ['스스로 예측', d.pred, C.text1], ['FEM 실제 1차', d.f1 + ' Hz', fp ? X.green : C.accent5], ['자갈길 진동 증폭', d.amp + '배', fp ? X.green : C.accent5], ['무게', d.m + ' g', C.text1]];
  rows.forEach((r, k) => {
    const y = 2.98 + k * 0.255;
    T(s, r[0], { x: x + 0.1, y, w: 0.95, h: 0.24, fontSize: 8, color: C.accent3, valign: 'middle' });
    T(s, r[1], { x: x + 1.0, y, w: LW - 1.08, h: 0.24, fontSize: k === 2 || k === 3 ? 10 : 8.5, bold: k === 2 || k === 3, color: r[2], align: 'right', valign: 'middle' });
  });
  s.addImage({ data: fp ? IC2.ok : IC2.x, x: x + LW / 2 - 0.5, y: 4.27, w: 0.2, h: 0.2 });
  T(s, fp ? '근거 기준 통과' : '근거 기준 미달', { x: x + LW / 2 - 0.26, y: 4.24, w: 1.0, h: 0.26, fontSize: 9.5, bold: true, color: fp ? X.green : C.accent5, valign: 'middle' });
});
T(s, '※ LLM 단독 = 대화 맥락 · 도구 없이 같은 요청 · 좌표계만 받은 독립 세션 3회(Claude). 판정 기준: 1차 진동 ≥ 91 Hz(자갈길 실측 최대 45.6 Hz × 2, ISBS 2020). 증폭 = 45.6 Hz 가진 시 비감쇠 1/(1−r²). 해석은 같은 1 mm FEM, 폰+거치부 254 g. LLM C의 1.6 mm 벽은 1 mm 격자 표현 한계로 무게가 자체 추정(33 g)보다 큼', { x: 0.5, y: 4.62, w: 9, h: 0.5, fontSize: 7.5, color: C.accent3 });
s.addNotes('같은 요청을 도구 없는 LLM에 세 번 줬다. 세 번 모두 진동 기준을 40~60 Hz로 잡았는데, 자갈길 실측 진동이 최대 45.6 Hz라 이 기준으로는 공진을 피할 수 없다. 스스로 예측한 진동수도 실제와 −17~+42% 어긋났다. FormProof는 근거로 91 Hz 기준을 세우고 계산으로 통과를 확인했다.');
