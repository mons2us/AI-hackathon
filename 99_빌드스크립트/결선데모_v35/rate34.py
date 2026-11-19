"""속도 고르기: 기준(6.5 음절/s)의 −10 % 보다 느린 구절만 PSOLA 로 길이를 줄임(최대 10 %, 음높이 유지). phr.json 의 dur 갱신."""
import json, re, numpy as np, soundfile as sf, parselmouth
from parselmouth.praat import call
P = json.load(open('phr.json')); R = 6.5
for seg, L in P.items():
    for p in L:
        n = len(re.sub(r'[^가-힣]', '', p['txt'])); y, sr = sf.read(p['wav']); r = n / (len(y) / sr)
        if r < 0.9 * R and any(x in p['wav'] for x in ('B_0',)):   # 발음 확인 후 이 구절만 (다른 구절은 줄이면 발음이 뭉개짐)
            f = max(0.90, r / (0.9 * R))                       # 길이 배율 (0.90 = 10 % 짧게)
            snd = parselmouth.Sound(p['wav']); man = call(snd, 'To Manipulation', 0.01, 70, 400)
            dt = call(man, 'Extract duration tier'); call(dt, 'Add point', snd.xmin, f); call(dt, 'Add point', snd.xmax, f)
            call([man, dt], 'Replace duration tier'); call(man, 'Get resynthesis (overlap-add)').save(p['wav'], 'WAV')
            y2, _ = sf.read(p['wav']); p['dur'] = round(len(y2) / sr, 2)
            print(f"{p['wav']:22s} {r:.1f} → {n / p['dur']:.1f} 음절/s (×{f:.2f})")
json.dump(P, open('phr.json', 'w'), ensure_ascii=False, indent=1)
