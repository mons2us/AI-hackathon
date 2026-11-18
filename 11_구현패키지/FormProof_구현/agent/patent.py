"""특허 효과 검증: 특허 문서(청구항 · 상세 설명) → 구조 · 효과 주장 추출 → 계산 가능한 비교 항목 → 판정.

목적: 특허의 '법적 유효성'이 아니라, 청구항이 주장하는 기술적 효과(강성 · 진동 · 방열 · 처짐 등)가
      같은 조건의 기준 구조 대비 실제로 나오는지 계산으로 확인해 근거 리포트를 만든다.

흐름
  1. inputs.load_input(pdf)            → 본문 텍스트
  2. extract(text, llm)                → {"structure": ..., "baseline": ..., "effects": [...] }   (LLM, 계산 금지)
  3. effects_to_checks(effects)        → 엔진 지표 비교 목록   (규칙, 아래 METRIC)
  4. (담당자) 특허 구조 · 기준 구조를 형상으로 만들기 → engine MODE=eval 로 각각 계산 → frfint_<tag>.json
  5. judge(ev_patent, ev_base, checks) → 효과별 확인 / 미확인 / 반대
  6. report.make_report(...)           → HTML 근거 리포트

구현 상태 (2026-11-16)
  2 · 3 · 5 : 완료 (프롬프트 · 매핑 규칙 · 판정 로직)
  4         : TODO(형상 담당) — 청구항 구조 → 엔진 격자 형상. 우선 단순 형상(판 · 리브 · 브래킷)은 규칙 생성기,
              복잡한 형상은 STEP 입력(inputs.py) 또는 형상 AI 사용
  사내 특허 시스템 연동 : TODO(확장) — 제안서 등록 시 PDF 를 받아 1~6 실행, 리포트를 제안서에 첨부
"""
import json, re

SYSTEM = """너는 특허 문서 분석기다. 특허 본문에서 (1) 보호하려는 구조, (2) 비교 대상인 종래 구조, (3) 주장하는 기술적 효과를 뽑아 JSON 으로만 답한다.
규칙: 계산하지 말 것. 효과마다 원문 근거 문장(quote)을 그대로 붙일 것. 정량값이 원문에 없으면 null.
metric 은 다음 중 하나: stiffness(강성 · 처짐 감소), frequency(고유진동수 · 흔들림), stress(응력 · 파손), thermal(온도 · 방열), mass(경량화), other.
형식: {"title": "", "structure": "보호 구조 요약", "baseline": "종래 구조 요약",
       "effects": [{"claim": "효과 요약", "metric": "stiffness", "direction": "decrease|increase", "target_value": null, "quote": "원문"}],
       "questions": ["형상 · 하중 · 재료 중 문서에 없는 것"]}"""

# 엔진 출력(frfint_<tag>.json) 지표와의 대응. better: 기준 대비 좋아지는 방향
METRIC = {
    'stiffness': dict(key=lambda e: max(e['touch_mm']), better='lower', label='터치 · 하중 처짐 (mm)'),
    'frequency': dict(key=lambda e: e['f'][0], better='higher', label='1차 고유진동수 (Hz)'),
    'stress':    dict(key=lambda e: max(e['shock']['vert']['vm999'], e['shock']['fore']['vm999']), better='lower', label='충격 응력 (MPa)'),
    'thermal':   dict(key=lambda e: e['Tmax'], better='lower', label='최고 온도 상승 (°C)'),
    'mass':      dict(key=lambda e: e['mass_g'], better='lower', label='무게 (g)'),
}

def extract(text, llm, max_chars=30000):
    out = llm.complete(SYSTEM, text[:max_chars]); m = re.search(r'\{.*\}', out, re.S)
    return json.loads(m.group(0))

def effects_to_checks(effects):
    chk, skip = [], []
    for e in effects:
        (chk if e.get('metric') in METRIC else skip).append(e)
    return chk, skip

def judge(ev_patent, ev_base, checks, tol=0.02):
    """효과별 판정. tol: 기준 대비 2 % 미만 차이는 '차이 없음'"""
    res = []
    for e in checks:
        M = METRIC[e['metric']]; p, b = M['key'](ev_patent), M['key'](ev_base)
        gain = (b - p) / abs(b) if M['better'] == 'lower' else (p - b) / abs(b)
        verdict = '확인' if gain > tol else ('반대' if gain < -tol else '차이 없음')
        if verdict == '확인' and e.get('target_value') is not None:
            tv = float(e['target_value']); verdict = '확인' if (p <= tv if M['better'] == 'lower' else p >= tv) else '부분 확인'
        res.append(dict(claim=e['claim'], metric=M['label'], patent=round(p, 3), baseline=round(b, 3), gain_pct=round(100 * gain, 1), verdict=verdict, quote=e.get('quote', '')))
    return res

if __name__ == '__main__':   # 판정 로직 자체 시험: 처음 설계(base) 대비 최종 몸체(body)를 '특허 구조'로 가정
    import sys, os
    R = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'reference')
    body = json.load(open(os.path.join(R, 'frfint_body_v3.json'))); base = json.load(open(os.path.join(R, 'frfint_base35g3.json')))
    eff = [dict(claim='진동 감소(고유진동수 상승)', metric='frequency', direction='increase', target_value=95, quote='(시험)'),
           dict(claim='방열 개선', metric='thermal', direction='decrease', target_value=None, quote='(시험)'),
           dict(claim='경량화', metric='mass', direction='decrease', target_value=None, quote='(시험)')]
    print(json.dumps(judge(body, base, effects_to_checks(eff)[0]), ensure_ascii=False, indent=1))
