"""GINO 검증 페이지 (HTML 한 파일, 그림은 data URI). FNO · 탐색 결과가 있으면 같은 표에 열로 추가."""
import json, base64, os, html
H = os.path.dirname(os.path.abspath(__file__))
V = json.load(open(H + '/viz.json')); MG = json.load(open(H + '/metrics_gino.json'))
MF = json.load(open(H + '/metrics_fno.json')) if os.path.exists(H + '/metrics_fno.json') else None
img = lambda p: 'data:image/png;base64,' + base64.b64encode(open(H + '/' + p, 'rb').read()).decode()
NM = {'f1_hz': ('진동수 1차', 'Hz'), 'f2_hz': ('진동수 2차', 'Hz'), 'phone_Tmax_rise_c': ('폰 온도', '°C'), 'touch_top_mm': ('휨 (위)', 'mm'), 'touch_bottom_mm': ('휨 (아래)', 'mm'), 'shock_vm999_mpa': ('충격 응력', 'MPa')}
pct = lambda v: f'{v * 100:.1f}%'
def cell(m, k, f): return f(m[k][f.__name__]) if False else ''
rows = ''
for k, (kr, u) in NM.items():
    g = MG[k]; f = MF[k] if MF else None
    def two(key, fmt):
        a = fmt(g[key]); b = fmt(f[key]) if f else '<span class="mut">학습 중</span>'
        return f'<td>{b}</td><td>{a}</td>'
    rows += f'<tr><th>{kr} <span class="mut">{u}</span></th>' + two('median', pct) + two('mape', pct) + two('relL2', pct) + two('r2', lambda v: f'{v:.3f}') + two('r2_log', lambda v: f'{v:.3f}') + '</tr>'
cards = ''
for c in V:
    t = ''
    for k, (kr, u) in [('f1_hz', ('진동수', 'Hz')), ('phone_Tmax_rise_c', ('폰 온도', '°C')), ('touch_top_mm', ('휨 (위)', 'mm')), ('shock_vm999_mpa', ('충격 응력', 'MPa'))]:
        s = c['scalars'][k]; fno = f"{s['fno']:.3g}" if 'fno' in s else '—'
        t += f"<tr><th>{kr} <span class='mut'>{u}</span></th><td>{s['true']:.3g}</td><td>{fno}</td><td>{s['gino']:.3g}</td></tr>"
    fe = c['field_relL2_vm']; ft = c['field_relL2_T']
    t += f"<tr><th>응력 분포 오차</th><td>—</td><td>{pct(fe['fno']) if 'fno' in fe else '—'}</td><td>{pct(fe['gino'])}</td></tr>"
    t += f"<tr><th>온도 분포 오차</th><td>—</td><td>{pct(ft['fno']) if 'fno' in ft else '—'}</td><td>{pct(ft['gino'])}</td></tr>"
    cards += f"""<article class="card"><header><h3>{html.escape(c['name'])}</h3><span class="mut">{c['mass']:.1f} g · 정답 진동수 {c['scalars']['f1_hz']['true']:.1f} Hz</span></header>
<div class="fig"><img src="{img(c['img'])}" alt="{html.escape(c['name'])} 응력 · 온도 지도"></div>
<div class="tw"><table class="mini"><thead><tr><th></th><th>정밀 시뮬레이션</th><th>FNO</th><th>GINO</th></tr></thead><tbody>{t}</tbody></table></div></article>"""
page = f"""<title>GINO 물리 AI 검증</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* 레이아웃: 한 줄 기사형 — 조건 → 지표표 → 산점도 → 형상 카드(지도 + 값) */
:root{{--bg:#F6F7F9;--fg:#18202B;--mut:#5E6B7A;--line:#D9DEE5;--card:#FFFFFF;--acc:#1D7F69;--fno:#6A60C9;--fig:#FFFFFF;
--sans:'Noto Sans KR',system-ui,sans-serif;--mono:'IBM Plex Mono',ui-monospace,monospace}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#11161D;--fg:#E6EAF0;--mut:#93A0B0;--line:#2A333F;--card:#18202A;--acc:#4CC3A3;--fno:#A39BF0;--fig:#F4F5F7;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#11161D;--fg:#E6EAF0;--mut:#93A0B0;--line:#2A333F;--card:#18202A;--acc:#4CC3A3;--fno:#A39BF0;--fig:#F4F5F7;color-scheme:dark}}
body{{background:var(--bg);color:var(--fg);font-family:var(--sans);line-height:1.6;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:28px 48px}}
main{{max-width:1040px;margin:0 auto;display:flex;flex-direction:column;gap:28px}}
h1{{font-size:26px;margin:0;text-wrap:balance}} h2{{font-size:18px;margin:0 0 10px}} h3{{font-size:15px;margin:0;font-family:var(--mono);font-weight:500}}
p{{margin:0;max-width:70ch}} .mut{{color:var(--mut);font-size:.88em}}
.facts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px}}
.facts div{{border:1px solid var(--line);border-radius:8px;padding:10px 12px;background:var(--card)}} .facts b{{display:block;font-size:13px;color:var(--mut);font-weight:500}}
.tw{{overflow-x:auto}} table{{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums;font-size:14px}}
th,td{{padding:7px 10px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap}} th:first-child{{text-align:left}}
thead th{{font-size:12px;color:var(--mut);font-weight:500}} .grp{{text-align:center}}
.fnoh{{color:var(--fno)}} .ginoh{{color:var(--acc)}}
.fig{{background:var(--fig);border-radius:8px;padding:6px}} .fig img{{display:block;width:100%;height:auto}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,480px),1fr));gap:16px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;display:flex;flex-direction:column;gap:10px;min-width:0}}
.card header{{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;align-items:baseline}}
.mini{{font-size:13px}} .notes li{{margin-bottom:6px}} ul{{margin:0;padding-left:20px}}
</style>
<main>
<header><h1>GINO 물리 AI 검증</h1><p class="mut">같은 형상 AI(DeepSDF)에 물리 AI 만 FNO → GINO 로 바꿔 끼운 실험 · 2026-11-19 · 정답 = 팀 엔진 정밀 시뮬레이션</p></header>
<section><h2>실험 조건</h2><div class="facts">
<div><b>데이터</b>형상 389개 (GUI FNO 와 같은 데이터)</div><div><b>분할</b>학습 331 · 검증 58 (두 모델 모두 검증 형상은 학습에 안 씀)</div>
<div><b>GINO 입력</b>표면 점(위치 · 법선) + 4 mm 계산 지점 44×10×19 의 재료 비율</div><div><b>GINO 학습</b>6,000단계 · 1시간 49분 · CPU · 파라미터 150만</div>
<div><b>FNO (비교 기준)</b>{'같은 분할로 새로 학습 완료' if MF else '같은 분할로 새로 학습 중 — 끝나면 열 추가'}</div><div><b>정답의 한계</b>엔진도 2 mm 칸 단위 → GINO 의 곡면 장점은 이 데이터로 확인 불가</div>
</div></section>
<section><h2>검증 58개 오차</h2><p class="mut">같은 예측값으로 지표 다섯 가지. 중앙값 · MAPE · 상대 L2 는 낮을수록, R² 는 1 에 가까울수록 좋음. R²(로그)는 크기가 수백 배 차이 나는 휨 · 응력을 로그로 본 값.</p>
<div class="tw"><table><thead><tr><th></th><th class="grp" colspan="2">중앙값 오차</th><th class="grp" colspan="2">MAPE</th><th class="grp" colspan="2">상대 L2</th><th class="grp" colspan="2">R²</th><th class="grp" colspan="2">R² (로그)</th></tr>
<tr><th></th>{'<th class="fnoh">FNO</th><th class="ginoh">GINO</th>' * 5}</tr></thead><tbody>{rows}</tbody></table></div>
<p class="mut">진동수를 설계 구간(50~200 Hz) 형상 {int(MG['f1_hz']['n'])}개만 보면 GINO MAPE {pct(MG['f1_hz']['mape_50_200'])}{(' · FNO ' + pct(MF['f1_hz']['mape_50_200'])) if MF else ''}. 분포 오차(검증 58개 평균 상대 L2): GINO 온도 6.6% · 응력 29.6%.</p></section>
<section><h2>정답 대비 예측 (검증 58개)</h2><div class="fig"><img src="{img('fig/scatter.png')}" alt="성능 4개 정답 대비 예측 산점도"></div>
<p class="mut">대각선에 붙을수록 정확. 로그 축.</p></section>
<section><h2>형상별 분포 지도</h2><p class="mut">옆에서 본 모습(앞뒤 방향 최댓값). 위 = 응력 log(1+MPa), 아래 = 온도 상승. 한 줄 안에서는 같은 색 척도. 진동수 낮은 형상부터 높은 형상까지 6개, 데모 기준(95 Hz)에 가까운 형상 포함.</p>
<div class="cards">{cards}</div></section>
<section><h2>읽는 법</h2><ul class="notes">
<li>폰 온도는 R² 0.995 로 거의 정확. 다만 검증 형상 대부분이 20.5~20.8 °C 로 값 자체가 거의 변하지 않음.</li>
<li>진동수는 R² 0.945, 설계 구간 오차 약 11% — 탐색 방향을 잡는 데 쓸 만한 수준.</li>
<li>휨은 MAPE 95% 지만 로그 R² 0.93: 크기 순서는 잘 맞히고, 아주 작은 값(0.002 mm 등)에서 상대오차가 커짐.</li>
<li>충격 응력이 가장 약함(로그 R² 0.62). 지도에서도 응력이 몰리는 위치는 맞지만 최댓값이 어긋나는 형상이 있음.</li>
<li>그래서 합격 판정은 AI 가 아니라 정밀 시뮬레이션이 함 (FormProof 구조 그대로).</li>
</ul></section>
</main>"""
open(H + '/gino_report.html', 'w').write(page); print(len(page) // 1024, 'KB')
