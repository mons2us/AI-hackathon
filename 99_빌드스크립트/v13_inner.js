// ===== v13: 속 구조와 출력 방법
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '2. 기술 차별성' });
s.addText('2. 실증 ① 자전거 거치대 — 속은 비어 있고, 그대로 출력된다', { placeholder: 'title' });
s.addText('덩어리가 아니라 윗판 · 옆벽 · 대각 보강재로 된 ㄱ자 얇은 벽 구조 — 출력 방향까지 계산에 넣어 받침대 없이 쌓인다', { placeholder: 'body' });
box(s, 0.5, 1.3, 5.0, 3.6, 'FFFFFF', 'sections');
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 1.3, w: 5.0, h: 3.6, rectRadius: 0.06, fill: { type: 'none' }, line: { color: X.line, width: 1 } });
fit(s, SH + 'v13_sections.png', 0.55, 1.33, 4.9, 3.54, 'cross sections');
box(s, 5.65, 1.3, 3.85, 1.85, X.tint, 'print pose');
fit(s, SH + 'v13_c_print_iso.png', 5.7, 1.35, 3.75, 1.5, 'print orientation');
T(s, '출력 자세 — 옆벽을 바닥에 두고 눕혀서', { x: 5.75, y: 2.86, w: 3.7, h: 0.24, fontSize: 9, bold: true, color: C.text2, align: 'center' });
const pr = [['클램프 링', '세로 원통으로 쌓여 받침대 불필요'], ['속 빈 공간', '위로 열려 있음 · 갇힌 빈 공간 0개'], ['돌출부', '45° 넘는 돌출 0개 (2 mm 격자 검사)'], ['층간 강도', `층 사이 응력 ${BK.ai_il} MPa ≤ 허용 10.9 MPa`], ['권장 설정', 'PETG · 층 0.2 mm · 벽 4겹']];
pr.forEach((r, i) => { const y = 3.27 + i * 0.32;
  s.addImage({ data: IC2.ok, x: 5.7, y: y + 0.04, w: 0.18, h: 0.18 });
  T(s, r[0], { x: 5.95, y, w: 0.9, h: 0.27, fontSize: 9, bold: true, color: C.text2, valign: 'middle' });
  T(s, r[1], { x: 6.85, y, w: 2.65, h: 0.27, fontSize: 8.5, color: C.text1, valign: 'middle' }); });
T(s, '※ 단면 = 출력용 STL 기준(청록 = 재료). 받침대 여부는 2 mm 격자 45° 규칙으로 판정, 매끄럽게 다듬은 STL의 최종 확인은 슬라이서 미리보기로 필요', { x: 0.5, y: 4.95, w: 9, h: 0.22, fontSize: 7.5, color: C.accent3 });
s.addNotes('잘라 보면 속이 꽉 찬 덩어리가 아니다. 위에 약 4 mm 판, 출력 바닥 쪽에 세로 벽, 반대쪽에 대각 보강재가 있고 나머지는 비어 있다. 같은 무게면 재료를 테두리에 둬야 굽힘에 강하다(I빔 원리). 옆벽이 바닥면 쪽에 생긴 것은 출력 방향 제약 때문이다. 눕혀서 출력하면 링은 세로 원통으로, 빈 공간은 위로 열린 채 쌓여 받침대가 필요 없다.');
