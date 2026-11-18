// ---------- 6b. TV 스탠드 실증
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 실증 사례 ② — TV 스탠드: 더 가볍고, 덜 흔들리게', { placeholder: 'title' });
s.addText('65형 TV(20.8 kg) · 알루미늄 판재 다리 · IEC 62368-1 안정성 조건(총중량 13% 수평력)', { placeholder: 'body' });
box(s, 0.5, 1.3, 3.9, 3.0, X.tint, 'tv card');
fit(s, SH + 'tv_tv_full_c.png', 0.6, 1.4, 3.7, 2.15, 'TV on optimized feet');
fit(s, SH + 'tv_tv_foot_c.png', 0.6, 3.55, 1.8, 0.7, 'foot close-up');
T(s, '알루미늄 10 mm 판재를 잘라 만드는 다리 — 제조 방식에 맞춘 설계 공간', { x: 2.45, y: 3.58, w: 1.9, h: 0.68, fontSize: 9, color: C.text2, valign: 'middle' });
// before / after 2D stress under front-back push
box(s, 4.6, 1.3, 2.4, 2.1, X.tint, 'before'); pill(s, 4.72, 1.38, 1.5, '단순 ㅗ자 다리', X.mute, X.white);
fit(s, SH + 'tv2d_T_web40.png', 4.68, 1.75, 2.24, 1.1, 'baseline foot stress');
T(s, '200 g · 상단 흔들림 2.2 mm ✗', { x: 4.68, y: 2.95, w: 2.24, h: 0.3, fontSize: 10, bold: true, color: C.accent5, align: 'center' });
box(s, 7.1, 1.3, 2.4, 2.1, X.tint, 'after'); pill(s, 7.22, 1.38, 1.3, 'AI 재설계', X.teal, X.white);
fit(s, SH + 'tv2d_c.png', 7.18, 1.75, 2.24, 1.1, 'optimized foot stress');
T(s, '146 g · 상단 흔들림 0.25 mm ✓', { x: 7.18, y: 2.95, w: 2.24, h: 0.3, fontSize: 10, bold: true, color: C.accent1, align: 'center' });
fit(s, SH + 'tv_cbar.png', 5.6, 3.42, 2.6, 0.38, 'stress colorbar'); T(s, '응력 (MPa), 앞뒤 수평력', { x: 8.25, y: 3.47, w: 1.3, h: 0.2, fontSize: 8, color: C.accent3 });
const tvk = [['−27%', '다리 무게', '200 → 146 g (1개)'], ['9배 ↓', 'TV 상단 흔들림', '2.2 → 0.25 mm (기준 ≤ 1 mm)'], ['통과', '넘어짐 안정성', '10° 기울임 · 13% 수평력']];
tvk.forEach((k, i) => {
  const x = 4.6 + i * 1.65;
  T(s, k[0], { x, y: 3.85, w: 1.6, h: 0.42, fontSize: 20, bold: true, color: C.accent1 });
  T(s, k[1], { x, y: 4.25, w: 1.6, h: 0.22, fontSize: 10, bold: true, color: C.text2 });
  T(s, k[2], { x, y: 4.47, w: 1.6, h: 0.35, fontSize: 8.5, color: C.accent3 });
});
T(s, '※ 실제 출력 형상을 3D로 재계산(판 수직 방향 수평력 포함): 상단 흔들림 0.25 mm, 최대 응력 8 MPa(허용 184 MPa). 넘어짐 안전계수 1.05~1.21로 여유 작음. 흔들림 기준·다리 간격 1.2 m·비교 형상은 설계 가정(확인 필요)', { x: 0.5, y: 4.88, w: 9, h: 0.36, fontSize: 8, color: C.accent3 });
s.addNotes('TV 스탠드: 처음에는 3D 덩어리로 최적화했지만 알루미늄이 너무 단단해 부재가 격자보다 얇아지는 문제가 반복됨. 제조 방식(판재 가공)에 맞게 설계 공간을 바꾸자 1 mm 격자에서 뚜렷한 형상이 나옴. 이것 자체가 "제조 조건을 반영한 설계"의 예시. 같은 물리(구조)지만 거치대는 진동, TV 스탠드는 정적 강성·안정성.');

