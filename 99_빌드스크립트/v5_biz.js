// ---------- 7. 사업·조직 기여
pres.addSection({ title: '3. 사업·조직 기여' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '3. 사업·조직 기여' });
s.addText('3. 사업·조직 기여 — DX 제품 설계 과정에 직접 들어간다', { placeholder: 'title' });
s.addText('기여하는 것은 사례 제품이 아니라 방법론: VD·MX·DA 기구 설계자가 설계 단계마다 직접 사용', { placeholder: 'body' });
const stg = [['구상', '경험으로 형상 결정', '요구 조건에서 기준을 만족하는 설계안 자동 생성'],
  ['상세 설계', '해석 부서 의뢰 · 결과 대기', '설계자가 직접 성능 확인 (근거 · 검증 포함)'],
  ['개선', '해석 결과 보고 수작업 수정', '최적화로 재설계 (경량화 · 보강)'],
  ['시제품', '출력 · 시험 → 실패 → 수정 반복', '출력 전 제작 형상까지 검증']];
T(s, '지금', { x: 2.0, y: 1.3, w: 3.2, h: 0.28, fontSize: 11, bold: true, color: C.accent3 });
T(s, 'FormProof 적용', { x: 5.6, y: 1.3, w: 3.9, h: 0.28, fontSize: 11, bold: true, color: C.accent1 });
stg.forEach((g, i) => {
  const y = 1.62 + i * 0.6;
  pill(s, 0.5, y + 0.12, 1.3, g[0], X.ink, X.white);
  box(s, 2.0, y, 3.2, 0.5, 'F3F4F5', 'now');
  T(s, g[1], { x: 2.12, y, w: 3.0, h: 0.5, fontSize: 10.5, color: C.accent3, valign: 'middle' });
  arrow(s, 5.25, y + 0.12, 0.3, 0.26);
  box(s, 5.6, y, 3.9, 0.5, X.tint, 'formproof');
  T(s, g[2], { x: 5.72, y, w: 3.7, h: 0.5, fontSize: 10.5, bold: true, color: C.text2, valign: 'middle' });
});
const tasks = [['지지 구조물 · 브래킷', '강성 · 넘어짐 안정성', 'TV 스탠드'], ['진동이 문제인 부품', '공진 회피', '자전거 거치대'], ['발열 부품 주변 구조', '방열 + 강성', '무선충전 스탠드 (진행 예정)'], ['기존 부품 개선', '경량화 · 보강', 'STEP 입력']];
T(s, '적용 설계 업무 (부품 유형)  ·  실증 사례', { x: 0.5, y: 4.08, w: 9, h: 0.25, fontSize: 10, bold: true, color: C.text2 });
tasks.forEach((t, i) => {
  const x = 0.5 + i * 2.27;
  T(s, [{ text: t[0], options: { bold: true, color: C.accent1, breakLine: true } }, { text: t[1] + '  ·  ' + t[2], options: { color: C.text1 } }], { x, y: 4.34, w: 2.2, h: 0.5, fontSize: 9 });
});
T(s, '※ 정량 효과(해석 의뢰~결과 기간, 시제품 반복 횟수)는 사내 기구 · 해석 담당자 확인 필요', { x: 0.5, y: 4.95, w: 9, h: 0.25, fontSize: 8.5, color: C.accent3 });
s.addNotes('사업 기여의 주체는 방법론. 사례 제품은 증거. 왼쪽 단계별로 지금 방식과 적용 후를 비교. 아래는 어떤 유형의 설계 업무에 쓰는지와 그 유형을 입증한 사례. 정량 효과는 담당자 인터뷰로 채울 예정.');

