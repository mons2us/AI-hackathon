import json, os, sys, numpy as np, soundfile as sf, librosa
H = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [H + '/../docent2', H + '/..']
import asr, tts3
from lines23 import LINES
os.makedirs('clips', exist_ok=True)
def trim(src, dst):
    y, sr = sf.read(src); _, idx = librosa.effects.trim(y, top_db=40)
    y = y[max(0, idx[0] - int(.05 * sr)):min(len(y), idx[1] + int(.12 * sr))].copy(); f = int(.02 * sr)
    y[:f] *= np.linspace(0, 1, f); y[-f:] *= np.linspace(1, 0, f); sf.write(dst, y, sr); return len(y) / sr
def run(keys=None):
    prev = {c['k']: c for c in json.load(open('clips.json'))} if (keys and os.path.exists('clips.json')) else {}
    out = []
    for i, (k, txt) in enumerate(LINES):
        if keys and k not in keys: out.append(prev[k]); continue
        best = None
        for j in range(3):
            tts3.say(txt, f'clips/raw{i:02d}_{j}.wav', sid=0, steps=24, speed=1.0)
            tr = asr.tr(f'clips/raw{i:02d}_{j}.wav'); c = asr.cer(txt, tr)
            if best is None or c < best[0]: best = (c, j, tr)
        d = trim(f'clips/raw{i:02d}_{best[1]}.wav', f'clips/c{i:02d}.wav')
        out.append(dict(k=k, txt=txt, dur=round(d, 2), cer=round(best[0], 2), asr=best[2])); print(i, k, round(d, 1), round(best[0], 2), best[2], flush=True)
    json.dump(out, open('clips.json', 'w'), ensure_ascii=False, indent=1)
    
if __name__ == '__main__':
    run(sys.argv[1:] or None)
