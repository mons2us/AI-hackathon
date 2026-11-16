"""① 조건 생성기: 요청(말 · 스케치 설명) → 설계 명세 JSON (항목마다 출처, 빠진 조건은 질문).

계산은 하지 않는다. LLM 은 '무엇을 계산할지'를 정하고, 수치 근거는 근거 DB(spec/evidence_db.json)에서 고른다.
출력은 spec/schema.json 형식을 만족해야 하며, 만족하지 않으면 오류 내용을 붙여 다시 요청한다(최대 3회).
"""
import json, os, re, sys
from llm import get_llm

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYSTEM = """너는 기구 설계 명세 작성기다. 사용자의 요청을 계산 가능한 설계 명세 JSON 으로 바꾼다.
규칙: (1) 계산하지 말 것. (2) 모든 수치 항목에 source 를 단다: '텍스트', '스케치', '근거 DB:<id>', '가정'. (3) 요청 · 스케치 · 근거 DB 어디에도 없으면 questions_to_user 에 질문으로 남긴다.
(4) 출력은 JSON 하나만. 형식은 아래 예시와 같다."""

def validate(spec, schema):
    need = schema['required']; miss = [k for k in need if k not in spec]
    for sec in ('geometry', 'objectives', 'constraints'):
        for k, v in spec.get(sec, {}).items():
            if not (isinstance(v, dict) and 'value' in v and 'source' in v): miss.append(f'{sec}.{k}: value/source 필요')
    return miss

def generate(request_text, sketch_note='', llm=None):
    llm = llm or get_llm(); schema = json.load(open(os.path.join(ROOT, 'spec/schema.json')))
    example = open(os.path.join(ROOT, 'spec/bike_mount_spec.json')).read(); db = open(os.path.join(ROOT, 'spec/evidence_db.json')).read()
    user = f'## 요청\n{request_text}\n\n## 스케치에서 읽은 내용\n{sketch_note or "(없음)"}\n\n## 근거 DB\n{db}\n\n## 형식 예시 (자전거 거치대)\n{example}'
    for k in range(3):
        out = llm.complete(SYSTEM, user); m = re.search(r'\{.*\}', out, re.S)
        try: spec = json.loads(m.group(0)); err = validate(spec, schema)
        except Exception as e: spec, err = None, [f'JSON 파싱 실패: {e}']
        if not err: return spec
        user += f'\n\n## 이전 출력의 문제 (고쳐서 다시)\n' + '\n'.join(err)
    raise RuntimeError('설계 명세 생성 실패: ' + '; '.join(err))

if __name__ == '__main__':
    s = generate(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else ''); json.dump(s, open('runs/spec.json', 'w'), ensure_ascii=False, indent=1); print('runs/spec.json')
