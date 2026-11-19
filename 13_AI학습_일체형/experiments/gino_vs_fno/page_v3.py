"""v3 페이지: 데이터 389 → 734 재학습 비교 (FNO · GINO), 검증 지표 + AI 탐색 → 정밀 시뮬레이션 판정. 출력 gino_report_v3.html"""
import json, base64, os
H = os.path.dirname(os.path.abspath(__file__))
A, B = json.load(open(H + '/cmp_eval_389.json')), json.load(open(H + '/cmp_eval_734.json'))
img = lambda p: 'data:image/png;base64,' + base64.b64encode(open(H + '/' + p, 'rb').read()).decode()
pct = lambda v: f'{v * 100:.1f}%'; r3 = lambda v: f'{v:.2f}'
COLS = [('fno', A, 'FNO 389'), ('fno', B, 'FNO 734'), ('gino', A, 'GINO 389'), ('gino', B, 'GINO 734')]
MET = [('진동수 MAPE · 50~200 Hz', lambda d, m: d['relerr'][m]['scalars']['f1_hz']['mape_50_200'], pct, -1),
       ('진동수 R²', lambda d, m: d['relerr'][m]['scalars']['f1_hz']['r2'], r3, 1),
       ('충격 응력 R² (로그)', lambda d, m: d['relerr'][m]['scalars']['shock_vm999_mpa']['r2_log'], r3, 1),
       ('폰 온도 R²', lambda d, m: d['relerr'][m]['scalars']['phone_Tmax_rise_c']['r2'], lambda v: f'{v:.3f}', 1),
       ('휨 (위) R² (로그)', lambda d, m: d['relerr'][m]['scalars']['touch_top_mm']['r2_log'], r3, 1),
       ('휨 (아래) R² (로그)', lambda d, m: d['relerr'][m]['scalars']['touch_bottom_mm']['r2_log'], r3, 1),
       ('온도 분포 오차', lambda d, m: d['relerr'][m]['field_T'], pct, -1),
       ('응력 분포 오차', lambda d, m: d['relerr'][m]['field_vm'], pct, -1)]
rows = ''
for lab, get, fmt, sgn in MET:
    rows += f'<tr><th>{lab}</th>'
    for i, (m, d, _) in enumerate(COLS):
        v = get(d, m); c = ''
        if d is B:
            dv = (v - get(A, m)) * sgn; c = ' class="up"' if dv > 1e-9 else (' class="dn"' if dv < -1e-9 else '')
        rows += f'<td{c}>{fmt(v)}</td>'
    rows += '</tr>'
RUN = [('gino', 'GINO 389'), ('gino734', 'GINO 734'), ('fno', 'FNO 389'), ('fno734', 'FNO 734')]
PIECE = {'gino': '끊김 (805칸 덩어리 · 고정 부품 1개 분리)', 'gino734': '거의 붙음 (작은 조각 71칸 이하)', 'fno': '거의 붙음 (작은 조각 44칸 이하)', 'fno734': '붙음 (3칸 조각 1개)'}
LIMS = [('무게', 'g', '최소화', 'mass', 'mass_g', None, lambda v: f'{v:.1f}'), ('진동수 1차', 'Hz', '≥ 95', 'f1', 'f1', lambda v: v >= 95, lambda v: f'{v:.1f}'),
        ('폰 온도', '°C', '≤ 21', 'Tmax', 'Tmax', lambda v: v <= 21, lambda v: f'{v:.2f}'), ('휨 (위·아래 큰 값)', 'mm', '≤ 0.3', 'touch', 'touch', lambda v: v <= 0.3, lambda v: f'{v:.3g}')]
srows = ''
for lab, u, lim, kp, kf, ok, fmt in LIMS:
    srows += f'<tr><th>{lab} <span class="mut">{u}</span></th><td class="mut">{lim}</td>'
    for n, _ in RUN:
        p = json.load(open(f'{H}/search_{n}.json'))['trace'][-1][kp]; f = json.load(open(f'{H}/fem_{n}.json'))['keep'][kf]
        f = max(f) if isinstance(f, list) else f
        j = '' if ok is None else (' <span class="ok">합격</span>' if ok(f) else ' <span class="ng">불합격</span>')
        srows += f'<td class="mut">{fmt(p)}</td><td><b>{fmt(f)}</b>{j}</td>'
    srows += '</tr>'
srows += '<tr><th>형상 연결</th><td class="mut">초기 설계: 한 덩어리</td>' + ''.join(f'<td colspan="2" class="sm">{PIECE[n]}</td>' for n, _ in RUN) + '</tr>'
fa, fb = A['relerr'], B['relerr']
page = f"""<title>GINO 물리 AI 검증 v3</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{{--bg:#F6F7F9;--fg:#18202B;--mut:#5E6B7A;--line:#D9DEE5;--card:#FFFFFF;--acc:#1D7F69;--fno:#6A60C9;--fig:#FFFFFF;--ng:#C8453B;--upbg:#E3F3EE;--dnbg:#FBE9E7;
--sans:'Noto Sans KR',system-ui,sans-serif;--mono:'IBM Plex Mono',ui-monospace,monospace}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#11161D;--fg:#E6EAF0;--mut:#93A0B0;--line:#2A333F;--card:#18202A;--acc:#4CC3A3;--fno:#A39BF0;--fig:#F4F5F7;--ng:#F07A6E;--upbg:#173A31;--dnbg:#3F2120;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#11161D;--fg:#E6EAF0;--mut:#93A0B0;--line:#2A333F;--card:#18202A;--acc:#4CC3A3;--fno:#A39BF0;--fig:#F4F5F7;--ng:#F07A6E;--upbg:#173A31;--dnbg:#3F2120;color-scheme:dark}}
body{{background:var(--bg);color:var(--fg);font-family:var(--sans);line-height:1.6;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:28px 48px}}
main{{max-width:1040px;margin:0 auto;display:flex;flex-direction:column;gap:28px}}
h1{{font-size:26px;margin:0;text-wrap:balance}} h2{{font-size:18px;margin:0 0 10px}}
p{{margin:0;max-width:72ch}} .mut{{color:var(--mut);font-size:.88em}} .sm{{font-size:12px;text-align:left;white-space:normal}}
.facts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px}}
.facts div{{border:1px solid var(--line);border-radius:8px;padding:10px 12px;background:var(--card)}} .facts b{{display:block;font-size:13px;color:var(--mut);font-weight:500}}
.key{{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--ng);border-radius:8px;padding:14px 16px}} .key li{{margin-bottom:6px}}
.tw{{overflow-x:auto}} table{{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums;font-size:14px}}
th,td{{padding:7px 10px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap}} th:first-child{{text-align:left}}
thead th{{font-size:12px;color:var(--mut);font-weight:500}} .grp{{text-align:center}} .fnoh{{color:var(--fno)}} .ginoh{{color:var(--acc)}}
td.up{{background:var(--upbg)}} td.dn{{background:var(--dnbg)}}
.fig{{background:var(--fig);border-radius:8px;padding:6px}} .fig img{{display:block;width:100%;height:auto}}
.ok{{color:var(--acc);font-weight:500;font-size:12px}} .ng{{color:var(--ng);font-weight:500;font-size:12px}} ul{{margin:0;padding-left:20px}} .notes li{{margin-bottom:6px}}
</style>
<main>
<header><h1>GINO 물리 AI 검증 v3 — 데이터 389 → 734</h1><p class="mut">FNO · GINO 를 데이터 734개로 다시 학습해 389개 결과와 비교 · 2026-11-20 · 정답 = 팀 엔진 정밀 시뮬레이션 · 이전 판(v2) 은 별도 링크로 유지</p></header>
<section class="key"><h2>요약</h2><ul>
<li><b>데이터를 늘려도 탐색 결과는 4개 모두 정밀 판정 불합격.</b> 가장 큰 원인은 진동수 과대평가 (AI 94~103 Hz → 정밀 2~40 Hz).</li>
<li>검증 58개 지표는 엇갈림: 충격 응력 · 온도 · 휨(아래)은 좋아졌지만, 진동수와 분포 오차는 두 모델 모두 나빠짐.</li>
<li>GINO 734 탐색은 수렴하지 못함 (무게가 402 g 까지 늘고 기준 위반 벌점이 끝까지 큼). FNO 734 는 AI 기준으론 거의 맞췄지만(94 Hz) 정밀 24 Hz.</li>
</ul></section>
<section><h2>실험 조건</h2><div class="facts">
<div><b>데이터</b>389개 → 734개 (저장소 샤드 17개 전체)</div>
<div><b>검증</b>389개 때와 같은 58개 형상 고정 · 학습 331 → 676</div>
<div><b>학습 설정</b>389개 때와 같음 — FNO 2,000단계 × 16개 · GINO 6,000단계 × 1개 → 형상 하나당 학습 횟수는 약 절반</div>
<div><b>탐색</b>같은 형상 AI · 시작점(94.9 g) · 목적식 · 300회, 물리 AI 만 교체</div>
</div></section>
<section><h2>검증 58개 지표</h2><p class="mut">초록 = 389 보다 좋아짐 · 빨강 = 나빠짐 (734 열에만 표시). 389 값은 v2 와 같은 코드로 다시 계산해 일치 확인.</p>
<div class="tw"><table><thead><tr><th></th><th class="fnoh">FNO 389</th><th class="fnoh">FNO 734</th><th class="ginoh">GINO 389</th><th class="ginoh">GINO 734</th></tr></thead><tbody>{rows}</tbody></table></div></section>
<section><h2>AI 탐색 결과 → 정밀 시뮬레이션 판정</h2><p class="mut">각 모델 두 칸: 회색 = 탐색 끝에서 AI 가 본 값, 굵게 = 같은 형상을 정밀 시뮬레이션으로 계산한 값.</p>
<div class="tw"><table><thead><tr><th></th><th>기준</th>{''.join(f'<th class="grp {"ginoh" if "GINO" in l else "fnoh"}" colspan="2">{l}</th>' for _, l in RUN)}</tr>
<tr><th></th><th></th>{'<th>AI</th><th>정밀</th>' * 4}</tr></thead><tbody>{srows}</tbody></table></div>
<p class="mut" style="margin-top:8px">형상 연결 = 재료 칸(고정 부품 포함)이 면으로 이어진 덩어리 수로 계산. GINO 389 형상이 끊겼는지는 v2 에서 "확인 필요"였고, 이번에 끊김으로 확인.</p></section>
<section><h2>탐색 경로</h2><div class="fig"><img src="{img('fig/search_v3.png')}" alt="반복에 따른 AI 예측 진동수와 무게, 끝점의 정밀 진동수"></div>
<p class="mut">실선 389 · 점선 734. 왼쪽 그림 300회 위치의 점(동그라미 = 389 · 네모 = 734)이 정밀 결과 — 선과 점의 간격이 AI 오차. 네 경우 모두 점이 기준선(95 Hz) 아래.</p></section>
<section><h2>탐색이 끝난 형상</h2><div class="fig"><img src="{img('fig/shapes_v3.png')}" alt="초기 설계와 탐색 형상 4개의 옆모습"></div></section>
<section><h2>읽는 법 · 다음</h2><ul class="notes">
<li>FNO 734 형상은 끊김이 없는데도 정밀 진동수 24 Hz → 불합격 원인이 "끊긴 형상" 만은 아님.</li>
<li>추가 345개가 검증 58개와 분포가 다른지, 학습 횟수 절반이 원인인지는 확인 필요 → 734개로 단계 수를 늘린 학습으로 분리 가능.</li>
<li>평균 오차를 줄이는 것만으로는 탐색이 AI 의 약점을 찾아가는 문제가 남음. GUI FNO(80.1 g 합격)는 데이터 389개 전체로 학습한 모델.</li>
<li>다음 후보: (1) 734개 · 단계 수 2배 재학습 (2) 탐색 형상을 정밀 계산해 학습에 다시 넣는 반복(능동학습) (3) 구조 비교(3D U-Net · Transolver) — 순서는 결정 필요.</li>
</ul></section>
</main>"""
open(H + '/gino_report_v3.html', 'w').write(page); print(len(page) // 1024, 'KB')
