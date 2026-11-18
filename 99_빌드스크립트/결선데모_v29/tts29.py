"""구절마다 Supertonic 3 세 번 생성 → ASR 오류가 가장 적은 것 · 앞뒤 무음 정리. 결과 phr.json. 인자로 구간 이름을 주면 그 구간만 다시."""
import json, os, sys, numpy as np, soundfile as sf, librosa
H = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [H + '/../docent2', H + '/..']
import asr, tts3
from phrases29 import P
def trim(src, dst):
    y, sr = sf.read(src); _, idx = librosa.effects.trim(y, top_db=40)
    y = y[max(0, idx[0] - int(.04 * sr)):min(len(y), idx[1] + int(.10 * sr))].copy(); f = int(.02 * sr)
    y[:f] *= np.linspace(0, 1, f); y[-f:] *= np.linspace(1, 0, f); sf.write(dst, y, sr); return len(y) / sr
SPEED = float(os.environ.get('SPEED', '1.06'))
os.makedirs('ph', exist_ok=True)
old = json.load(open('phr.json')) if os.path.exists('phr.json') else {}
only = set(sys.argv[1:])
out = {}
for seg, L in P.items():
    if only and seg not in only and seg in old and len(old[seg]) == len(L): out[seg] = old[seg]; continue
    out[seg] = []
    for j, txt in enumerate(L):
        best = None
        for k in range(int(os.environ.get('TRIES', '3'))):
            fn = f'ph/{seg}_{j}_{k}.wav'; tts3.say(txt, fn, sid=0, steps=24, speed=SPEED)
            tr = asr.tr(fn); c = asr.cer(txt, tr)
            if best is None or c < best[0]: best = (c, fn, tr)
        d = trim(best[1], f'ph/{seg}_{j}.wav')
        out[seg].append(dict(txt=txt, wav=f'ph/{seg}_{j}.wav', dur=round(d, 2), cer=round(best[0], 2), asr=best[2]))
        print(seg, j, round(d, 1), round(best[0], 2), best[2], flush=True)
json.dump(out, open('phr.json', 'w'), ensure_ascii=False, indent=1)
