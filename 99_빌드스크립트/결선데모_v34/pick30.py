"""cand30.json 에서 구절마다 하나 고르기: 발음 오류가 그 구절 최저 + 0.08 이내인 후보 중
전체 기준 음높이 · 말 속도에 가장 가깝고(문장 끝 '다.' 는 끝이 내려가는 것) → 음량은 구절 사이 같게(RMS) → phr.json."""
import json, os, re, sys, numpy as np, soundfile as sf
_H = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [_H + '/../docent2', _H + '/..']
import asr, parselmouth
from parselmouth.praat import call
def norm(t):                                   # ASR 가 숫자 · 영문으로 쓴 것을 대사 표기로 (발음 오류만 남기게)
    for a, b in (('AI', '에이아이'), ('3D', '쓰리디'), ('1.4', '일 점 사'), ('15. 6', '십오 점 육'), ('15.6', '십오 점 육'), ('5 기준', '다섯 기준')): t = t.replace(a, b)
    return t
C0 = json.load(open('cand30.json'))
for k, v in C0.items():
    for c in v['c']: c['cer'] = round(asr.cer(v['txt'], norm(c['asr'])), 3)
json.dump(C0, open('cand30.json', 'w'), ensure_ascii=False, indent=1)
C = json.load(open('cand30.json'))
st = lambda a, b: 12 * np.log2(a / b)
ok = {k: [c for c in v['c'] if c['cer'] <= min(x['cer'] for x in v['c']) + 0.06] for k, v in C.items()}
T = np.median([c['med'] for L in ok.values() for c in L]); R = np.median([c['rate'] for L in ok.values() for c in L])
def cost(k, c):
    fin = C[k]['txt'].rstrip().endswith('다.')
    return abs(st(c['med'], T)) + 12 * abs(c['rate'] / R - 1) + (2.0 if fin and c['tail'] > -4 else 0) + 20 * (c['cer'] - min(x['cer'] for x in C[k]['c']))
for _ in range(3):
    pick = {k: min(L, key=lambda c: cost(k, c)) for k, L in ok.items()}
    T = np.median([c['med'] for c in pick.values()]); R = np.median([c['rate'] for c in pick.values()])
D = np.median([c['db'] for c in pick.values()])
os.makedirs('ph34', exist_ok=True); out = {}
print(f'기준 음높이 {T:.0f} Hz · 속도 {R:.1f} 음절/s')
for k, c in pick.items():
    fn = f'ph34/{k}.wav'; d = st(c['med'], T); sh = 0.0
    if abs(d) > 1.0:                           # 남은 차이가 1 반음 넘으면 억양 모양은 그대로 두고 전체 음높이만 이동 (PSOLA)
        snd = parselmouth.Sound(c['wav']); man = call(snd, 'To Manipulation', 0.01, 70, 400); pt = call(man, 'Extract pitch tier')
        call(pt, 'Shift frequencies', snd.xmin, snd.xmax, -d, 'semitones'); call([pt, man], 'Replace pitch tier')
        call(man, 'Get resynthesis (overlap-add)').save(fn, 'WAV'); sh = -d; src = fn
    else: src = c['wav']
    y, sr = sf.read(src); y = y * 10 ** ((D - c['db']) / 20); sf.write(fn, y, sr); c['shift'] = sh
    seg, j = k.rsplit('_', 1); out.setdefault(seg, []).append(dict(txt=C[k]['txt'], wav=fn, dur=c['dur'], cer=c['cer'], asr=c['asr']))
    print(f"{k:8s} {st(c['med'], T):+5.1f}st 보정{c['shift']:+4.1f} {c['rate']:4.1f}음절/s 끝{c['tail']:+5.1f} cer {c['cer']:.2f}  {c['asr']}")
order = list(json.load(open('phr29.json')).keys())
json.dump({s: out[s] for s in order}, open('phr.json', 'w'), ensure_ascii=False, indent=1)
