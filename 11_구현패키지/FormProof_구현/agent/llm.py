"""LLM 교체 인터페이스. 사내 LLM 으로 바꿀 때는 이 파일만 고친다.

  ManualLLM        : 프롬프트를 파일로 쓰고, 사람이 붙여 넣은 응답 파일을 읽는다 (외부 API 불가 환경, 시연 · 디버그)
  OpenAICompatLLM  : OpenAI 호환 /v1/chat/completions 엔드포인트 (사내 vLLM · TGI 등). 환경 변수 LLM_BASE_URL, LLM_MODEL, LLM_API_KEY
"""
import json, os, time, urllib.request

class LLM:
    def complete(self, system: str, user: str) -> str: raise NotImplementedError

class ManualLLM(LLM):
    def __init__(self, workdir='runs/llm'): self.w = workdir; os.makedirs(workdir, exist_ok=True)
    def complete(self, system, user):
        k = int(time.time()); q = os.path.join(self.w, f'prompt_{k}.md'); a = os.path.join(self.w, f'answer_{k}.md')
        open(q, 'w').write(f'# SYSTEM\n{system}\n\n# USER\n{user}\n'); print(f'[ManualLLM] 프롬프트: {q}\n응답을 {a} 에 저장하면 계속합니다.')
        while not os.path.exists(a): time.sleep(2)
        return open(a).read()

class OpenAICompatLLM(LLM):
    def __init__(self, base_url=None, model=None, api_key=None, temperature=0.0):
        self.u = (base_url or os.environ['LLM_BASE_URL']).rstrip('/') + '/v1/chat/completions'
        self.m = model or os.environ.get('LLM_MODEL', 'default'); self.k = api_key or os.environ.get('LLM_API_KEY', ''); self.t = temperature
    def complete(self, system, user):
        body = json.dumps(dict(model=self.m, temperature=self.t, messages=[{'role': 'system', 'content': system}, {'role': 'user', 'content': user}])).encode()
        req = urllib.request.Request(self.u, body, {'Content-Type': 'application/json', 'Authorization': f'Bearer {self.k}'})
        return json.loads(urllib.request.urlopen(req, timeout=300).read())['choices'][0]['message']['content']

def get_llm(kind=None):
    kind = kind or os.environ.get('LLM_KIND', 'manual')
    return OpenAICompatLLM() if kind == 'openai' else ManualLLM()
