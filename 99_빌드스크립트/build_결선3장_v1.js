// FormProof 결선 발표 (문제 정의 → 핵심 기술 → 데모 영상 → 사업부 적용 · 계획) — 발표초안 v196 양식(맑은 고딕 · 삼성 블루 · CONTENT 레이아웃)
// 수치 = 결선 데모 영상 v27 과 같은 계산(GUI 판정) · LLM 비교 = 발표초안 v196 8쪽과 같은 실험
// 사용: node build_결선3장_v1.js <출력.pptx> <이미지 폴더> <데모 영상.mp4>
const pptxgen = require('pptxgenjs');
const fs = require('fs');
const { applyTheme } = require('/root/.claude/skills/synced/1e9abda0-994b-4505-92f0-2b787b374f9b_2a6ad69a-e73b-4fbf-b931-59083e82c013/pptx/scripts/apply_theme.js');
const [OUT, IMG, VID] = process.argv.slice(2);
const P = f => IMG + '/' + f;
const pic = p => 'image/png;base64,' + fs.readFileSync(p).toString('base64');
const size = p => { const b = fs.readFileSync(p); return [b.readUInt32BE(16), b.readUInt32BE(20)]; };
function fit(s, f, x, y, w, h, name) {
  const [iw, ih] = size(P(f)); const r = Math.min(w / iw, h / ih); const W = iw * r, H = ih * r;
  s.addImage({ data: pic(P(f)), x: x + (w - W) / 2, y: y + (h - H) / 2, w: W, h: H, objectName: name, altText: name });
}
function cover(s, f, x, y, w, h, name) {   // 상자를 꽉 채우고 넘치는 부분은 잘라냄
  const [iw, ih] = size(P(f));
  s.addImage({ data: pic(P(f)), x, y, w, h, sizing: { type: 'cover', w, h }, objectName: name, altText: name });
}
const THEME = { name: 'FormProof', headFontFace: '맑은 고딕', bodyFontFace: '맑은 고딕',
  colors: { dk1: '1A1F2B', lt1: 'FFFFFF', dk2: '0F1B3D', lt2: 'F0F3FA', accent1: '1428A0', accent2: '5B8DEF',
    accent3: '46536A', accent4: 'D3DBEE', accent5: '5E6B7D', accent6: '1428A0', hlink: '1428A0', folHlink: '46536A' } };
const RED = 'C8323F', GRN = '0E8A5F', ORG = 'E08A00';

const pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = 'FormProof 결선 발표';
const C = pres.SchemeColor;
pres.defineSlideMaster({ title: 'CONTENT', background: { color: C.background1 },
  objects: [{ placeholder: { options: { name: 'title', type: 'title', x: 0.45, y: 0.28, w: 9.1, h: 0.5, fontSize: 21, bold: true, color: C.text2, align: 'left', valign: 'middle', margin: 0 }, text: '' } },
            { placeholder: { options: { name: 'body', type: 'body', x: 0.45, y: 0.78, w: 9.1, h: 0.3, fontSize: 12, color: C.accent3, align: 'left', valign: 'top', margin: 0 }, text: '' } },
            { text: { text: 'FormProof', options: { x: 0.45, y: 5.33, w: 5, h: 0.2, fontSize: 8, color: C.accent3, margin: 0 } } }],
  slideNumber: { x: 9.05, y: 5.33, w: 0.5, h: 0.2, fontSize: 8, color: C.accent3, align: 'right' } });
const T = (s, text, o) => s.addText(text, { margin: 0, isTextBox: true, valign: 'top', color: C.text1, fontSize: 11, ...o });
const rr = (s, x, y, w, h, fill, line, name, lw) => s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.06, fill: { color: fill }, line: { color: line || fill, width: lw || 0.75 }, objectName: name || 'box' });
const rect = (s, x, y, w, h, fill, name) => s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: fill }, objectName: name || 'bar' });
const pill = (s, x, y, w, h, text, fill, col, fs) => { s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: h / 2, fill: { color: fill }, line: { color: fill }, objectName: 'pill' }); T(s, text, { x, y, w, h, fontSize: fs || 9, bold: true, color: col, align: 'center', valign: 'middle' }); };
const arrowR = (s, x, y, w, h, col) => s.addShape(pres.shapes.RIGHT_ARROW, { x, y, w, h, fill: { color: col }, line: { color: col }, objectName: 'arrow' });

// ---------------- 1. 문제 정의
pres.addSection({ title: '문제 정의' });
let s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '문제 정의' });
s.addText([{ text: '아이디어는 많지만, ' }, { text: '성능을 확인하는 길', options: { color: RED } }, { text: '이 막혀 제품이 되지 못합니다' }], { placeholder: 'title' });
s.addText('“폰이 떨려서 지도가 안 보여. 안 흔들리는 거치대를 만들어 볼까?” — 이 한 문장이 제품이 되기까지', { placeholder: 'body' });
const PB = [['png_v47_cad.png', '1', '3D로 옮기기', 'CAD를 다룰 줄 알아야 함 → 스케치에서 멈춤'],
  ['png_v48_base.png', '2', '성능 확인', '하중 · 고정 · 기준을 정해 해석 → 전문가 의뢰 · 대기'],
  ['png_v44_llm.png', '3', 'AI에 맡기기', '그럴듯한 형상, 계산 없는 추정 → 맞는지 알 수 없음'],
  [null, '4', '그냥 만들기', '출력하고 고치기 반복 → 시간 · 재료 낭비']];
PB.forEach((p, i) => { const x = 0.45 + i * 2.31, y = 1.2, w = 2.16, h = 2.62;
  rr(s, x, y, w, h, 'FFFFFF', 'D3DBEE', 'bottleneck card');
  if (p[0]) fit(s, p[0], x + 0.06, y + 0.06, w - 0.12, 1.55, p[2]);
  else T(s, '출력 ↻ 수정', { x, y: y + 0.55, w, h: 0.5, fontSize: 20, bold: true, color: 'B8C1D3', align: 'center', valign: 'middle' });
  rect(s, x, y + 1.67, w, 0.04, RED, 'red rule');
  s.addShape(pres.shapes.OVAL, { x: x + 0.12, y: y + 1.82, w: 0.26, h: 0.26, fill: { color: C.text2 }, line: { color: C.text2 } });
  T(s, p[1], { x: x + 0.12, y: y + 1.82, w: 0.26, h: 0.26, fontSize: 10, bold: true, color: C.background1, align: 'center', valign: 'middle' });
  T(s, p[2], { x: x + 0.46, y: y + 1.81, w: w - 0.55, h: 0.3, fontSize: 13, bold: true, color: C.text2, valign: 'middle' });
  T(s, p[3], { x: x + 0.12, y: y + 2.17, w: w - 0.22, h: 0.4, fontSize: 9, color: C.accent3 }); });
// 근거: 같은 요청 LLM 3회
rr(s, 0.45, 3.95, 9.1, 0.72, 'FDF2F3', 'F1C4C9', 'evidence');
T(s, '③ AI에 맡기면 정말 안 될까?', { x: 0.6, y: 4.02, w: 2.4, h: 0.26, fontSize: 11.5, bold: true, color: RED });
T(s, '데모와 같은 요청을 일반 LLM에 3번 맡기고, 같은 해석기(2 mm FEM)로 계산', { x: 0.6, y: 4.29, w: 2.45, h: 0.34, fontSize: 8, color: C.accent3 });
[['png_v38_L1_b.png', 'LLM A', '불합격 · 22.6 °C'], ['png_v38_L2_b.png', 'LLM B', '불합격 · 2.95배'], ['png_v38_L3_b.png', 'LLM C', '불합격 · 6.6배']].forEach((e, i) => {
  const x = 3.15 + i * 2.15; rr(s, x, 4.03, 2.05, 0.56, 'FFFFFF', 'FFFFFF', 'llm card'); cover(s, e[0], x + 0.05, 4.07, 0.62, 0.48, e[1] + ' 설계');
  T(s, [{ text: e[1], options: { bold: true, breakLine: true } }, { text: '자체 판단 통과 → 계산', options: { fontSize: 7.5, color: C.accent3, breakLine: true } }, { text: e[2], options: { bold: true, color: RED, fontSize: 8.5 } }], { x: x + 0.74, y: 4.06, w: 1.3, h: 0.5, fontSize: 9.5, color: C.text2 }); });
rr(s, 0.45, 4.77, 9.1, 0.46, C.text2, C.text2, 'need');
T(s, '필요한 것', { x: 0.62, y: 4.77, w: 0.9, h: 0.46, fontSize: 9.5, bold: true, color: 'FFD166', valign: 'middle' });
T(s, '요구를 계산할 수 있는 조건으로 바꾸고, 물리 계산으로 성능을 확인하며 설계하는 AI', { x: 1.45, y: 4.77, w: 6.6, h: 0.46, fontSize: 12.5, bold: true, color: C.background1, valign: 'middle' });
T(s, '→ FormProof', { x: 7.9, y: 4.77, w: 1.5, h: 0.46, fontSize: 13.5, bold: true, color: '7CE0B5', align: 'right', valign: 'middle' });
s.addNotes('[약 50초] 폰이 떨려 지도가 안 보여 거치대를 만들어 보려는 상황. 아이디어가 제품이 되려면 네 군데서 막힌다. ① 3D로 옮기려면 CAD가 필요하고, ② 버틸지 확인하려면 하중 · 고정 · 기준을 정해 해석을 맡기고 기다려야 하고, ③ AI에 맡기면 그럴듯한 형상은 나오지만 계산이 없다 — 실제로 같은 요청을 일반 LLM에 세 번 맡겼더니 세 번 모두 스스로 통과라고 했지만, 같은 해석기로 계산하면 모두 불합격(폰 온도 22.6 °C, 흔들림 2.95배 · 6.6배, 기준 1.5배 · 21 °C). ④ 그래서 결국 출력하고 고치기를 반복한다. 필요한 것은 요구를 계산할 수 있는 조건으로 바꾸고, 물리 계산으로 성능을 확인하며 설계하는 AI — FormProof. [근거] LLM 비교 = 같은 요청 · 같은 일체형 조건, Claude 독립 세션 3회(2026-11-15), 2 mm 격자 FEM · 감쇠비 3% · 발열 4 W. LLM 3안은 흔들림 1.2~1.3배로 자체 예측.');

// ---------------- 2. 핵심 기술
pres.addSection({ title: '핵심 기술' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '핵심 기술' });
s.addText([{ text: 'AI는 빠르게 찾고, ' }, { text: '물리 계산이 확인', options: { color: GRN } }, { text: '합니다' }], { placeholder: 'title' });
s.addText('FormProof 파이프라인 — 설계 에이전트가 A → B → C를 차례로 실행하고 기준과 대조, 미달이면 재설계 · 재검증', { placeholder: 'body' });
const ST = [['입력', '말 · 스케치 · 문서 · CAD', 'D3DBEE'], ['A 설계 사양', '요구 → 물리 조건', C.accent1], ['B 초기 설계 · 해석', '3D 형상 · 정밀 시뮬레이션', ORG], ['B 최적 설계', 'AI 탐색 + 정밀 최적화', ORG], ['C 검증 · 출력', '미달 → 재설계 · 합격만 출력', GRN]];
ST.forEach((p, i) => { const x = 0.45 + i * 1.86, w = 1.66;
  rr(s, x, 1.17, w, 0.5, 'F0F3FA', 'F0F3FA', 'stage'); rect(s, x, 1.17, w, 0.05, p[2], 'stage rule');
  T(s, [{ text: p[0], options: { bold: true, fontSize: 10, breakLine: true, color: C.text2 } }, { text: p[1], options: { fontSize: 7.8, color: C.accent3 } }], { x: x + 0.08, y: 1.25, w: w - 0.12, h: 0.4 });
  if (i < 4) arrowR(s, x + w + 0.04, 1.35, 0.13, 0.14, '9AA4B6'); });
// A
rr(s, 0.45, 1.8, 1.98, 2.85, 'FFFFFF', 'D3DBEE', 'module A');
pill(s, 0.57, 1.9, 0.3, 0.3, 'A', C.accent1, C.background1, 11);
T(s, '요구를 계산할 수 있게', { x: 0.93, y: 1.9, w: 1.45, h: 0.3, fontSize: 10, bold: true, color: C.text2, valign: 'middle' });
T(s, '수치마다 근거', { x: 0.57, y: 2.27, w: 1.8, h: 0.32, fontSize: 15, bold: true, color: C.text2 });
T(s, '예: 안 흔들리게 → 95 Hz 이상\n근거가 없으면 사용자에게 질문', { x: 0.57, y: 2.6, w: 1.8, h: 0.42, fontSize: 7.8, color: C.accent3 });
fit(s, 'png_v17_sketch.png', 0.55, 3.05, 1.78, 1.52, '입력 스케치');
// B
rr(s, 2.53, 1.8, 4.94, 2.85, 'FFF8EC', ORG, 'module B', 1.5);
pill(s, 2.65, 1.9, 0.3, 0.3, 'B', ORG, '1B1300', 11);
T(s, '하이브리드 최적 설계 — AI 탐색 + 정밀 계산', { x: 3.01, y: 1.9, w: 4.3, h: 0.3, fontSize: 10.5, bold: true, color: C.text2, valign: 'middle' });
[['png_e0.png', '초기 설계'], ['png_e20.png', 'AI 탐색'], ['png_e300.png', '300회'], ['png_e300.png', ''], ['png_r120.png', '정밀 최적화']].filter(v => v[1]).forEach((e, i) => {
  const x = 2.65 + i * 1.19; rr(s, x, 2.28, 1.13, 1.08, '16223A', '16223A', 'evo frame'); fit(s, e[0], x + 0.02, 2.3, 1.09, 1.04, e[1]);
  pill(s, x + 0.05, 2.32, 0.72, 0.18, e[1], '000000', C.background1, 7); });
[['300개', '형상 AI(DeepSDF) × 물리 AI(FNO)\n탐색 · 성능 즉시 예측'], ['31개만', '정밀 계산(FEM)\n전부 계산 대비 약 1/10'], ['120회', '구조 최적화 + FEM\n3D 프린트 조건']].forEach((b, i) => {
  const x = 2.65 + i * 1.6; rr(s, x, 3.45, 1.4, 1.1, 'FFFFFF', 'FFFFFF', 'number box');
  T(s, b[0], { x, y: 3.5, w: 1.4, h: 0.4, fontSize: 18, bold: true, color: C.text2, align: 'center' });
  T(s, b[1], { x, y: 3.92, w: 1.4, h: 0.55, fontSize: 7.5, color: C.accent3, align: 'center' });
  if (i < 2) arrowR(s, x + 1.43, 3.93, 0.13, 0.14, '9AA4B6'); });
// C
rr(s, 7.57, 1.8, 1.98, 2.85, 'FFFFFF', 'D3DBEE', 'module C');
pill(s, 7.69, 1.9, 0.3, 0.3, 'C', GRN, C.background1, 11);
T(s, '최종 형상을 다시 계산', { x: 8.05, y: 1.9, w: 1.45, h: 0.3, fontSize: 10, bold: true, color: C.text2, valign: 'middle' });
T(s, '5 / 5 통과만', { x: 7.69, y: 2.27, w: 1.8, h: 0.32, fontSize: 15, bold: true, color: C.text2 });
T(s, '제작 형상 그대로 FEM 재판정\n미달이면 목표 조정 후 재설계', { x: 7.69, y: 2.6, w: 1.8, h: 0.42, fontSize: 7.8, color: C.accent3 });
fit(s, 'png_p6_dwg.png', 7.65, 3.05, 1.82, 1.52, '자동 생성 A3 도면');
rr(s, 0.45, 4.75, 9.1, 0.46, C.text2, C.text2, 'demo bar');
T(s, '이 과정 그대로 — 자전거 폰 거치대를 실제 GUI로', { x: 0.65, y: 4.75, w: 6, h: 0.46, fontSize: 12, color: C.background1, valign: 'middle' });
pill(s, 7.45, 4.84, 1.95, 0.28, '▶ 데모 영상 1분 25초', 'F59E0B', '1B1300', 10);
s.addNotes('[약 1분] FormProof는 세 가지로 동작. A 설계 사양: "안 흔들리게" 같은 말을 떨림 주파수 95 Hz 이상 같은 계산 가능한 조건으로 바꾸고, 수치마다 근거(규격 · 실측)를 붙이며, 근거가 없으면 묻는다. B 하이브리드 최적 설계(핵심): 형상 AI(DeepSDF)가 모양을 바꾸고 물리 AI(FNO)가 성능을 바로 예측해 300개 형상을 탐색, 그중 후보 31개만 정밀 계산(FEM)으로 확인해 진동 여유가 가장 큰 후보를 고르고, 그 후보에서 구조 최적화 + FEM 120회로 3D 프린트 조건을 지키며 다듬는다. 탐색 단계의 정밀 계산은 300개 전부 대비 약 1/10(31/300, 정밀 최적화 120회는 별도). C 자동 검증: 최종 형상을 제작 형상 그대로 다시 계산해 기준을 모두 통과한 것만 도면 · STL로 출력, 미달이면 목표를 조정해 재설계. 이 과정을 데모로 보겠습니다. [질문 대비] 데모 GUI의 설계 사양 단계는 사내 LLM 대신 규칙 + 근거 DB로 실행(LLM 연결부는 팀 패키지에 구현). 전체 소요 시간은 측정 전 — 확인된 값: 초기 설계 판정 1초 이내(2026-11-17).');

// ---------------- 3. 데모 영상
pres.addSection({ title: '데모' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '데모' });
s.addText('데모 — 자전거 폰 거치대, 아이디어에서 검증된 설계까지', { placeholder: 'title' });
s.addText('실제 GUI 화면 · AI 탐색과 정밀 최적화 구간은 미리 계산한 기록 재생', { placeholder: 'body' });
{ const w = 7.6, h = w * 9 / 16, x = (10 - w) / 2, y = 1.15;
  s.addMedia({ type: 'video', path: VID, cover: pic(P('png_vcover.png')), x, y, w, h, objectName: 'demo video' }); }
s.addNotes('[1분 25초] 데모 영상 재생(음성판). 발표자가 직접 설명하려면 자막판(FormProof_결선데모_v27_자막.mp4)으로 교체. 영상 수치: 초기 설계 5개 기준 중 4개 미달(흔들림 5.58배) → 최종 5개 모두 충족, 흔들림 1.41배, 무게 94.9 → 80.1 g(−15.6 %).');

// ---------------- 4. 사업부 적용 · 계획
pres.addSection({ title: '적용 · 계획' });
s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: '적용 · 계획' });
s.addText('같은 흐름으로, 사업부 제품과 특허까지', { placeholder: 'title' });
s.addText('입력만 바꾸면 같은 파이프라인 — 제품 설계에 적용하고, 특허 문서 속 구조도 직접 만들어 성능을 비교', { placeholder: 'body' });
rr(s, 0.45, 1.17, 5.1, 3.5, 'FFFFFF', 'D3DBEE', 'case card');
T(s, '구현 예 · MX AR 글래스', { x: 0.6, y: 1.24, w: 3, h: 0.3, fontSize: 11, bold: true, color: C.text2, valign: 'middle' });
pill(s, 4.0, 1.27, 1.42, 0.24, '같은 GUI에서 동작', GRN, C.background1, 8);
fit(s, 'png_glass_gui.png', 0.55, 1.6, 4.9, 2.55, 'AR 글래스 설계 화면');
T(s, '“하루 종일 써도 가볍고 안 흘러내리게” → 총무게 · 조이는 힘 · 다리 표면 온도를 근거와 함께 조건으로 → 3D 설계 · 판정', { x: 0.6, y: 4.2, w: 4.85, h: 0.42, fontSize: 8, color: C.accent3 });
const RD = [['완료', GRN, '해커톤 구현', '입력 → 설계 사양 → AI 탐색 · 정밀 최적화 → 검증 → 도면 · STL · 3D 프린트'],
  ['다음', C.accent1, '사내 특허 시스템 연계', '청구항 · 도면 → 3D 재현 → 같은 조건 계산으로 효과 검증 · 회피 설계 비교'],
  ['확대', C.accent1, '사업부 시범', 'MX AR 글래스 · 폴더블 → VD TV · DA 가전 (무게 · 방열 · 진동 · 슬림)']];
RD.forEach((r, i) => { const y = 1.17 + i * 0.66; rr(s, 5.7, y, 3.85, 0.58, 'F0F3FA', 'F0F3FA', 'roadmap');
  pill(s, 5.8, y + 0.15, 0.6, 0.26, r[0], r[1], C.background1, 8.5);
  T(s, [{ text: r[2], options: { bold: true, fontSize: 10.5, breakLine: true, color: C.text2 } }, { text: r[3], options: { fontSize: 7.8, color: C.accent3 } }], { x: 6.5, y: y + 0.06, w: 3.0, h: 0.5 }); });
T(s, '사람이 직접 해야 하는 단계', { x: 5.7, y: 3.12, w: 3.8, h: 0.24, fontSize: 9.5, bold: true, color: C.text2 });
const TB = [['해석 도구 (CAE)', '4단계'], ['3D 생성 AI', '4단계'], ['생성형 설계 도구', '3단계'], ['범용 LLM 단독', '검증 없음'], ['FormProof', '0단계']];
s.addTable(TB.map((r, i) => [{ text: r[0], options: { bold: i === 4, color: i === 4 ? GRN : '1A1F2B' } }, { text: r[1], options: { bold: true, align: 'right', color: i === 4 ? GRN : (i === 3 ? RED : '1A1F2B') } }]),
  { x: 5.7, y: 3.36, w: 3.85, colW: [2.6, 1.25], rowH: 0.23, fontSize: 8.5, fontFace: '맑은 고딕', border: { type: 'solid', pt: 0.5, color: 'D3DBEE' }, fill: { color: 'FFFFFF' } });
rr(s, 0.45, 4.77, 9.1, 0.46, C.text2, C.text2, 'closing');
T(s, 'FormProof — 형상을 성능으로 증명', { x: 0.65, y: 4.77, w: 4.6, h: 0.46, fontSize: 15, bold: true, color: C.background1, valign: 'middle' });
T(s, '머릿속 아이디어를, 성능이 확인된 제품으로', { x: 5.0, y: 4.77, w: 2.8, h: 0.46, fontSize: 9.5, color: 'C9D3E6', valign: 'middle' });
pill(s, 7.95, 4.86, 1.45, 0.28, '실물 출력물 제시', 'F59E0B', '1B1300', 9.5);
s.addNotes('[약 1분] 같은 흐름은 입력만 바꾸면 다른 제품에도 적용된다 — 이미 같은 GUI에서 AR 글래스(총무게 · 조이는 힘 · 다리 표면 온도)를 설계 사양 · 3D 설계 · 판정까지 구현. 다음 단계는 사내 특허 시스템 연계: 청구항 · 도면에서 구조를 3D로 재현해 같은 조건으로 계산, 효과 주장 검증과 회피 설계 비교(법적 판단은 하지 않음). 이후 MX AR 글래스 · 폴더블 시범, VD TV · DA 가전으로 확대. 기존 도구는 사람이 3~4단계를 직접 해야 하지만 FormProof는 전 단계를 계산으로 연결. (실물을 들고) 이것이 이 흐름으로 설계해 3D 프린트로 출력한 거치대 — 같은 조건 정밀 최적화로 얻은 같은 계열 구조, PETG. 형상을 성능으로 증명, FormProof였습니다. [주의] 사람 작업 단계 수는 범주별 일반 기능 기준(발표초안 v196 7쪽과 같음).');

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log('saved', OUT);
})();
