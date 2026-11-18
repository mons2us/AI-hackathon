"""근거 리포트: 설계 사양(출처 포함) + 출력 형상 판정표 + (선택) 특허 효과 판정 → 한 장짜리 HTML.

  make_report(out_html, spec=None, ev=None, checks=None, mfg=None, patent=None, title='FormProof 근거 리포트')
    spec   : 조건 생성기 출력 (geometry · objectives · constraints 항목마다 value · source)
    ev     : 엔진 eval 결과 (frfint_<tag>.json)
    checks : pipeline.gate() 의 판정표 {항목: (값, 부등호, 기준)}
    mfg    : pipeline.mfg_check() 결과
    patent : patent.judge() 결과 목록
구현 상태: 완료 (2026-11-16). 그림 삽입(형상 · 분포)은 TODO — render 스크립트 결과 PNG 를 <img> 로 넣으면 된다.
"""
import html, json, datetime

CSS = """body{font-family:'Malgun Gothic',sans-serif;margin:24px;color:#1A1F2B}h1{color:#1428A0;font-size:20px}h2{font-size:15px;color:#0F1B3D;border-bottom:2px solid #1428A0;padding-bottom:4px;margin-top:22px}
table{border-collapse:collapse;width:100%;font-size:13px}td,th{border:1px solid #D3DBEE;padding:5px 8px;text-align:left}th{background:#F0F3FA}.ok{color:#1428A0;font-weight:700}.ng{color:#B3261E;font-weight:700}.mute{color:#5E6B7D;font-size:12px}"""

def _row(cells, th=False):
    t = 'th' if th else 'td'; return '<tr>' + ''.join(f'<{t}>{c}</{t}>' for c in cells) + '</tr>'

def make_report(out_html, spec=None, ev=None, checks=None, mfg=None, patent=None, title='FormProof 근거 리포트'):
    e = html.escape; H = [f'<!doctype html><meta charset="utf-8"><title>{e(title)}</title><style>{CSS}</style><h1>{e(title)}</h1>',
                         f'<p class="mute">생성 {datetime.datetime.now():%Y-%m-%d %H:%M} · 수치는 FEM 계산값, 출처 표기 없는 값 없음</p>']
    if spec:
        H.append('<h2>1. 설계 사양 (항목별 출처)</h2><table>' + _row(['구분', '항목', '값', '출처'], True))
        for sec in ('geometry', 'objectives', 'constraints'):
            for k, v in spec.get(sec, {}).items():
                H.append(_row([sec, e(k), e(json.dumps(v.get('value'), ensure_ascii=False)), e(str(v.get('source')))]))
        H.append('</table>')
        if spec.get('questions_to_user'): H.append('<p><b>사용자 확인 필요</b>: ' + ' · '.join(e(q) for q in spec['questions_to_user']) + '</p>')
    if checks:
        H.append('<h2>2. 출력 형상 판정</h2><table>' + _row(['항목', '값', '기준', '판정'], True))
        for k, (v, op, lim) in checks.items():
            ok = v >= lim if op == '>=' else v <= lim
            H.append(_row([e(k), f'{v:g}', f'{op} {lim:g}', f'<span class="{"ok" if ok else "ng"}">{"합격" if ok else "불합격"}</span>']))
        H.append('</table>')
    if mfg:
        H.append('<h2>3. 제작성 검사</h2><table>' + _row(['항목', '값', '설명'], True))
        for k, v in mfg.items(): H.append(_row([e(k), e(str(v.get('value'))), e(v.get('note', ''))]))
        H.append('</table>')
    if ev:
        H.append(f'<p class="mute">계산 요약: 무게 {ev["mass_g"]} g · 1차 {ev["f"][0]} Hz · 2차 {ev["f"][1]} Hz · 최고 온도 상승 {ev["Tmax"]} °C</p>')
    if patent:
        H.append('<h2>4. 특허 효과 검증 (기준 구조 대비)</h2><table>' + _row(['주장 효과', '지표', '특허 구조', '기준 구조', '개선', '판정', '원문 근거'], True))
        for p in patent:
            cls = 'ok' if p['verdict'] == '확인' else ('ng' if p['verdict'] == '반대' else '')
            H.append(_row([e(p['claim']), e(p['metric']), p['patent'], p['baseline'], f"{p['gain_pct']} %", f'<span class="{cls}">{e(p["verdict"])}</span>', f'<span class="mute">{e(p["quote"])}</span>']))
        H.append('</table><p class="mute">특허의 법적 유효성 판단이 아니라, 주장된 기술적 효과의 계산 확인</p>')
    open(out_html, 'w', encoding='utf-8').write('\n'.join(H)); return out_html
