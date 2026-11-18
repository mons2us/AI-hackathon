"""v17 도슨트: timeline.json 대사 → 클립(같은 대사는 v16 클립 재사용, 새 대사는 Supertonic 3 두 번 만들어 ASR 오류 적은 것) → 배치 · 혼합."""
import json, os, sys, subprocess, numpy as np, soundfile as sf, librosa
H = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [H + '/../docent2', H + '/..']
import asr
TL = json.load(open('timeline.json')); os.makedirs('clips', exist_ok=True)
old = {txt: f'../docent2/t4/c{i:02d}.wav' for i, (_, txt) in enumerate(json.load(open('../docent2/script_final.json')))}
def trim(src, dst):
    y, sr = sf.read(src); _, idx = librosa.effects.trim(y, top_db=40)
    y = y[max(0, idx[0] - int(.05 * sr)):min(len(y), idx[1] + int(.12 * sr))].copy(); f = int(.02 * sr)
    y[:f] *= np.linspace(0, 1, f); y[-f:] *= np.linspace(1, 0, f); sf.write(dst, y, sr); return len(y) / sr
tts3 = None; rows = []
for i, (t, txt) in enumerate(TL['times']):
    dst = f'clips/c{i:02d}.wav'
    if txt in old:
        d = trim(old[txt], dst); c = None
    else:
        if tts3 is None:
            import tts3
        best = None
        for k in range(2):
            tts3.say(txt, f'clips/raw{i:02d}_{k}.wav', sid=0, steps=20, speed=1.05)
            cc = asr.cer(txt, asr.tr(f'clips/raw{i:02d}_{k}.wav'))
            if best is None or cc < best[0]: best = (cc, k)
        c = best[0]; d = trim(f'clips/raw{i:02d}_{best[1]}.wav', dst)
    rows.append([t, d, txt, c]); print(i, f'{t:6.1f}+{d:4.1f}', '' if c is None else f'CER={c:.2f}', txt, flush=True)
# 겹치면 뒤로 밀기
prev = 0
for r in rows:
    if r[0] < prev + 0.25: print(f'  밀림 {r[2][:14]}… {r[0]:.1f} → {prev + .25:.1f}'); r[0] = prev + 0.25
    prev = r[0] + r[1]
json.dump(rows, open('docent_final.json', 'w'), ensure_ascii=False, indent=0)
a = ['ffmpeg', '-y', '-loglevel', 'error', '-i', 'silent.mp4'] + sum([['-i', f'clips/c{i:02d}.wav'] for i in range(len(rows))], [])
fl = ''.join(f'[{i + 1}:a]aresample=48000,adelay={int(r[0] * 1000)}|{int(r[0] * 1000)},apad[a{i}];' for i, r in enumerate(rows))
fl += ''.join(f'[a{i}]' for i in range(len(rows))) + f'amix=inputs={len(rows)}:normalize=0,loudnorm=I=-16:TP=-1.5,atrim=0:{TL["total"]:.2f}[o]'
subprocess.run(a + ['-filter_complex', fl, '-map', '0:v', '-map', '[o]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ac', '2', '-shortest', 'v17.mp4'], check=True)
print('total', TL['total'], 'last end', round(prev, 1))
