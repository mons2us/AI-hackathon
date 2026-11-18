"""하이브리드 경로 묶음 v2 — AI 탐색 프레임을 2회마다(151장)로 촘촘하게 · 분포(응력 · 온도)도 매 프레임.
기존 묶음(models/hybrid_p01.json.gz)의 후보 선택 · 정밀 최적화 프레임은 그대로 쓰고, AI 탐색만 GUI 코드(TorchBackend.trace)로 다시 만든다.
검증: 10회마다의 형상 해시가 기존 묶음(=능동 학습 3회차 기록과 해시로 확인된 경로)과 모두 같아야 저장.
사용: python3 make_hybrid_pack_v2.py [every=2]"""
import sys, os, json, gzip, time
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(H)
sys.path.insert(0, os.path.join(ROOT, '10_입력_1차설계'))
from formproof_input import inverse as V
EVERY = int(sys.argv[1]) if len(sys.argv) > 1 else 2
P = os.path.join(ROOT, '10_입력_1차설계', 'models', 'hybrid_p01.json.gz')
old = json.load(gzip.open(P, 'rt', encoding='utf-8'))
old_ai = {f['it']: f for f in old['frames'] if f.get('stage') == 'ai'}
N = old_ai[0]['iters']
B = V.backend()
lim = V.limits(); lim.update({k: tuple(v) for k, v in old['limits_used'].items()})
sel = sorted(old['selection'])
z0, fit = B.fit(V.start_shape())
t0 = time.time(); ai = []
for fr in B.trace(z0, sel, lim, iters=old['ai_iters'], every=EVERY):
    full = V.attached(fr.pop('full')); pred = fr['pred']
    f = dict(it=fr['it'], iters=N, stage='ai', mass_g=round(float(pred['mass']), 2), pen=round(float(fr['pen']), 4),
             pred={k: (None if pred.get(k) is None else round(float(pred[k]), 4)) for k in V.KEYS},
             mesh=V.mesh_payload(full, fr.get('soft')), heat=V.heat_payload(full, fr.get('fields')), sha=V._sha(full))
    if f['it'] in old_ai and old_ai[f['it']]['sha'] != f['sha']:
        raise SystemExit(f"형상 해시 다름 it={f['it']} — 기존 경로와 다름, 저장 안 함")
    ai.append(f)
    if f['it'] % 20 == 0:
        print(f"it {f['it']} {time.time()-t0:.0f}s mass {f['mass_g']}", flush=True)
rest = [f for f in old['frames'] if f.get('stage') != 'ai']
pack = dict(old, frames=ai + rest, ai_every=EVERY, version=2)
out = P.replace('.json.gz', f'_e{EVERY}.json.gz')
with gzip.open(out, 'wt', encoding='utf-8') as fh:
    json.dump(pack, fh, ensure_ascii=False)
print(json.dumps(dict(saved=out, ai_frames=len(ai), checked=sum(1 for f in ai if f['it'] in old_ai), size_kb=os.path.getsize(out) // 1024, s=round(time.time()-t0))))
