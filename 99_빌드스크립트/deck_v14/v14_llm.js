// ===== v14: 범용 LLM 단독 vs FormProof
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 범용 LLM 단독 vs FormProof — 같은 요청, 같은 검증', { placeholder: 'title' });
s.addText('도구 없는 LLM은 기준을 근거 없이 정하고 진동수를 어림했다 — 같은 해석기로 재니 더 무겁고 2~3배 흔들림', { placeholder: 'body' });
const LL4 = [
  { name: 'LLM 단독 A', desc: '공간 트러스', img: 'v11_c_L1.png', crit: '≥ 40 Hz', pred: '50 Hz', f1: 47.6, pk: 2.06, rms: 1.18, m: 43.1 },
  { name: 'LLM 단독 B', desc: '삼각 트러스', img: 'v11_c_L2.png', crit: '≥ 60 Hz', pred: '75 Hz', f1: 42.7, pk: 2.91, rms: 1.48, m: 40.7 },
  { name: 'LLM 단독 C', desc: '사각 박스 빔', img: 'v11_c_L3.png', crit: '≥ 40 Hz', pred: '60 Hz', f1: 54.9, pk: 2.93, rms: 1.28, m: 38.8 },
  { name: 'FormProof', desc: '3D 최적화 · 받침대 없이 출력', img: 'v14_e_159.png', crit: '실측 근거', pred: '계산으로 확인', f1: 98.5, pk: 1.11, rms: 1.03, m: 30.6, fp: true }];
const LW4 = 2.12;
LL4.forEach((d, i) => { const x = 0.5 + i * (LW4 + 0.15), fp = d.fp;
  box(s, x, 1.3, LW4, 3.25, fp ? 'E3F1F0' : X.tint, 'llm card');
  if (fp) s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.3, w: LW4, h: 3.25, rectRadius: 0.08, fill: { type: 'none' }, line: { color: X.teal, width: 2 }, objectName: 'fp frame' });
  T(s, d.name, { x: x + 0.1, y: 1.36, w: LW4 - 0.2, h: 0.26, fontSize: 11, bold: true, color: fp ? C.accent1 : C.text2 });
  T(s, d.desc, { x: x + 0.1, y: 1.6, w: LW4 - 0.2, h: 0.22, fontSize: 8, color: C.accent3 });
  fit(s, SH + d.img, x + 0.08, 1.85, LW4 - 0.16, 1.05, 'design ' + d.name);
  const inBand = d.f1 >= 34.6 && d.f1 <= 45.6;
  [['정한 기준', d.crit, fp ? C.accent1 : C.text1], ['스스로 예측', d.pred, C.text1], ['실제 1차', d.f1 + (inBand ? ' Hz *' : ' Hz'), fp ? X.green : C.accent5], ['최대 흔들림', d.pk.toFixed(1) + '배', fp ? X.green : C.accent5], ['무게', d.m + ' g', fp ? X.green : C.text1]].forEach((r, k) => { const y = 2.98 + k * 0.255;
    T(s, r[0], { x: x + 0.1, y, w: 0.85, h: 0.24, fontSize: 8, color: C.accent3, valign: 'middle' });
    T(s, r[1], { x: x + 0.9, y, w: LW4 - 0.98, h: 0.24, fontSize: k === 2 || k === 3 ? 9.5 : 8, bold: k >= 2, color: r[2], align: 'right', valign: 'middle' }); });
  T(s, `평균 흔들림 ${d.rms.toFixed(2)}배`, { x: x + 0.1, y: 4.26, w: LW4 - 0.2, h: 0.24, fontSize: 9.5, bold: true, color: fp ? X.green : C.accent5, align: 'center', valign: 'middle' }); });
T(s, '※ LLM 단독 = 대화 맥락 · 도구 없이 같은 요청 · 좌표계만 받은 독립 세션 3회(Claude). 판정은 모두 같은 1 mm FEM · 폰+받침대 340 g 강체 · 감쇠비 3% 가정. 흔들림 = 핸들바 대비 폰 진동 배율(10–100 Hz, 평균 = RMS). 스스로 예측 대비 실제 오차 +5 ~ +76%. * 노면 진동 중앙 대역(34.6–45.6 Hz) 안', { x: 0.5, y: 4.62, w: 9, h: 0.5, fontSize: 7.5, color: C.accent3 });
s.addNotes('같은 요청을 도구 없는 LLM에 세 번 줬다. 세 번 모두 진동 기준을 40~60 Hz로 스스로 정했는데, 조약돌길 노면 진동 중앙값이 34.6~45.6 Hz라 공진을 피하는 기준이 못 된다. B는 실제 1차가 42.7 Hz로 노면 대역 안이다. 스스로 예측한 진동수도 실제보다 5~76% 높았다. FormProof 설계는 30.6 g으로 가장 가볍고 최대 흔들림 1.1배.');
