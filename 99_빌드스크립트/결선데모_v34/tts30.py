"""v34 음성: 구절마다 8개 후보 생성 → 후보별 발음 오류(ASR CER) · 음높이 중앙값 · 말 속도 · 끝 억양 측정 → cand30.json.
고르기는 pick30.py (음높이 · 속도를 전체 기준에 맞춤)."""
import json, os, sys, re, numpy as np, soundfile as sf, librosa
H = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [H + '/../docent2', H + '/..']
import asr, tts3
from phrases29 import P
N = int(os.environ.get('TRIES', '8')); os.makedirs('ph30', exist_ok=True)
def trim(y, sr):
    _, idx = librosa.effects.trim(y, top_db=40); return y[max(0, idx[0] - int(.04 * sr)):min(len(y), idx[1] + int(.10 * sr))].copy()
def meas(y, sr, txt):
    f0, v, _ = librosa.pyin(y, fmin=70, fmax=400, sr=sr, frame_length=1024); f = f0[v]
    idx = np.where(v)[0]; t = librosa.frames_to_time(idx, sr=sr, hop_length=256); tail = f0[idx[t > t[-1] - 0.4]]
    n = len(re.sub(r'[^가-힣]', '', txt)); return dict(med=float(np.median(f)), tail=float(12 * np.log2(np.median(tail) / np.median(f))), rate=n / (len(y) / sr),
                                                     db=float(20 * np.log10(np.sqrt(np.mean(y ** 2)) + 1e-9)))
C = json.load(open('cand30.json')) if os.path.exists('cand30.json') else {}
for seg, L in P.items():
    for j, txt in enumerate(L):
        k = f'{seg}_{j}'
        if k in C and C[k]['txt'] == txt and len(C[k]['c']) >= N: continue
        cs = []
        for i in range(N):
            fn = f'ph30/{k}_{i}.wav'; tts3.say(txt, fn, sid=0, steps=24, speed=1.06)
            y, sr = sf.read(fn); y = trim(y, sr); sf.write(fn, y, sr)
            tr = asr.tr(fn); cs.append(dict(wav=fn, cer=round(asr.cer(txt, tr), 3), asr=tr, dur=round(len(y) / sr, 2), **meas(y, sr, txt)))
        C[k] = dict(txt=txt, c=cs); json.dump(C, open('cand30.json', 'w'), ensure_ascii=False, indent=1)
        print(k, ' '.join(f"{c['cer']:.2f}/{c['med']:.0f}/{c['rate']:.1f}" for c in cs), flush=True)
print('done')
