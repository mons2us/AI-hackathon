"""v17 합성: 녹화(raw.mp4) + 마커 → 로딩 구간 잘라냄 · 자막 띠 · 도면 강조 · 카드 · 도슨트 음성."""
import json, subprocess, sys, os, asyncio
from urllib.parse import quote
from PIL import Image, ImageDraw, ImageFont
from plan import BANDS, DOCENT
RUN = sys.argv[1]                                    # 서버 run 폴더 (opt_final_drawing.png)
M = json.load(open('marks.json')); dw = M['dw']
def ff(*a): subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *a], check=True)
def dur(f): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))
o = -0.7; t = lambda k: max(0, M[k] - o)
c0 = t('opt') + 1.2; c1 = t('stepend')
SEQ = json.load(open('seq.json'))
# 한 장씩 캡처한 AI 탐색 · 정밀 최적화 → GUI 의도 속도 (AI 7 장/초 · 정밀 3 장/초, 강조 바뀔 때 0.9 초 멈춤)
lines, vt, cur, prev = [], {}, 0.0, 'x'
for s in SEQ:
    d = 1 / 7 if s['stage'] == 'ai' else 1 / 3
    if s['stage'] == 'pick': d += 7.0                                   # 후보 31개 비교 화면을 읽을 시간
    if s['hl'] != prev:
        key = {'ai': 'aiplay', None: 'aiwatch', 'graph': 'aigraph', 'pick': 'refine', 'ref': 'refine2'}[s['hl']]
        vt.setdefault(key, cur); d += 0.9; prev = s['hl']
    lines.append(f"file 'st/{s['n']:04d}.jpg'\nduration {d:.4f}\n"); cur += d
lines.append(f"file 'st/{SEQ[-1]['n']:04d}.jpg'\n")
DSTEP = cur
def T(key):
    k, _, plus = key.partition('+'); p = float(plus) if plus else 0
    if k in vt: return c0 + vt[k] + p
    v = t(k) + p
    return v if v <= c0 else c0 + DSTEP + (v - c1)
if not os.path.exists('main.mp4'):
    open('stl.txt', 'w').write(''.join(lines))
    ff('-f', 'concat', '-safe', '0', '-i', 'stl.txt', '-vf', 'fps=30,scale=1600:900', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', 'pst.mp4')
    ff('-i', 'raw.mp4', '-t', f'{c0:.2f}', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', '30', 'pa.mp4')
    ff('-ss', f'{c1:.2f}', '-i', 'raw.mp4', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', '30', 'pb.mp4')
    open('lc.txt', 'w').write("file pa.mp4\nfile pst.mp4\nfile pb.mp4\n")
    ff('-f', 'concat', '-safe', '0', '-i', 'lc.txt', '-c', 'copy', 'main.mp4')
cut = (c1 - c0) - DSTEP
D = dur('main.mp4') + 6
# 2) 자막 띠 PNG
async def bands():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1600, 'height': 110})
        for j, (k, i, a, n, tg) in enumerate(BANDS):
            await pg.goto('file://' + os.path.abspath('nar.html') + f'?i={quote(i)}&a={quote(a)}&n={quote(n)}&t={quote(tg)}')
            await pg.wait_for_timeout(150); await pg.screenshot(path=f'b_{j:02d}.png')
        await b.close()
asyncio.run(bands())
ev = [(f'b_{j:02d}.png', T(k), (T(BANDS[j + 1][0]) if j + 1 < len(BANDS) else D)) for j, (k, *_) in enumerate(BANDS)]
# 3) 도면 강조 프레임
im = Image.open(os.path.join(RUN, 'opt_final_drawing.png')).convert('RGB'); im.thumbnail((1580, 890), Image.LANCZOS)
w, h = im.size; ox, oy = (1600 - w) // 2, (900 - h) // 2; s = w / 420; P = lambda x, y: (ox + x * s, oy + (297 - y) * s)
FB = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'; FR = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
fb = ImageFont.truetype(FB, 24, index=1); fr = ImageFont.truetype(FR, 19, index=1)
def frame(boxes, title, body, cpos):
    S = Image.new('RGB', (1600, 900), 'white'); S.paste(im, (ox, oy))
    ov = Image.new('RGBA', (1600, 900), (8, 14, 28, 105)); md = ImageDraw.Draw(ov)
    for (x0, y0, x1, y1) in boxes: a = P(x0, y1); b = P(x1, y0); md.rectangle([a[0] - 6, a[1] - 6, b[0] + 6, b[1] + 6], fill=(0, 0, 0, 0))
    S = Image.alpha_composite(S.convert('RGBA'), ov); d = ImageDraw.Draw(S)
    for (x0, y0, x1, y1) in boxes: a = P(x0, y1); b = P(x1, y0); d.rounded_rectangle([a[0] - 6, a[1] - 6, b[0] + 6, b[1] + 6], radius=10, outline=(255, 176, 32), width=4)
    L = body.split('\n'); bw = max(d.textlength(title, font=fb), *[d.textlength(l, font=fr) for l in L]) + 48; bh = 50 + 30 * len(L)
    x, y = cpos; d.rounded_rectangle([x, y, x + bw, y + bh], radius=14, fill=(17, 26, 43), outline=(255, 176, 32), width=2)
    d.text((x + 22, y + 12), title, font=fb, fill=(255, 209, 102))
    for i, l in enumerate(L): d.text((x + 22, y + 50 + 30 * i), l, font=fr, fill=(255, 255, 255))
    return S.convert('RGB')
frame([(20, 10, 410, 287)], '제작 도면 자동 생성', f'최적 설계가 나오면 A3 도면을 자동으로 만듦\n이번 생성 시간 {dw["seconds"]:.0f}초 (3면도 · 등각도 · 구멍 표 · 표제란)', P(100, 150)).save('dC.png')
frame([(270, 10, 410, 58.6)], '표제란', f'도명 · 도번 · 재질 PETG · 질량 {dw["mass_g"]} g\n척도 1:1 · 3각법 · 단위 mm', P(150, 108)).save('dA.png')
frame([(24, 27, 150, 66), (40, 85, 240, 175)], '정면도 + 구멍 표', '볼트 · 나사 구멍의 지름 · 위치 · 수량', P(250, 140)).save('dB.png')
d0 = T('draw') + 1.5; dseq = [('dC.png', d0, d0 + 3.8), ('dA.png', d0 + 3.8, d0 + 7.6), ('dB.png', d0 + 7.6, 999)]
CP = T('refine') + 0.9; cseq = [('cand.png', CP, CP + 7.2)]
inp = ['-i', 'main.mp4'] + sum([['-i', f] for f, _, _ in ev + dseq + cseq], [])
fl = '[0:v]tpad=stop_mode=clone:stop_duration=6,pad=1600:1010:0:0:color=0x111a2b[v0];'; n = 0
for i, (f, a, b) in enumerate(ev): fl += f"[v{n}][{i + 1}:v]overlay=0:900:enable='between(t,{a:.2f},{b:.2f})'[v{n + 1}];"; n += 1
for j, (f, a, b) in enumerate(dseq): fl += f"[v{n}][{len(ev) + 1 + j}:v]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[v{n + 1}];"; n += 1
for j, (f, a, b) in enumerate(cseq): fl += f"[v{n}][{len(ev) + len(dseq) + 1 + j}:v]overlay=248:560:enable='between(t,{a:.2f},{b:.2f})'[v{n + 1}];"; n += 1
ff(*inp, '-filter_complex', fl.rstrip(';'), '-map', f'[v{n}]', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', '30', 'mainc.mp4')
open('l.txt', 'w').write("file '../vid11/card_in.mp4'\nfile 'flow.mp4'\nfile 'mainc.mp4'\nfile 'card_out.mp4'\n")
subprocess.run(['python3', 'cards.py', RUN], check=True)
ff('-f', 'concat', '-safe', '0', '-i', 'l.txt', '-c', 'copy', 'silent.mp4')
# 4) 도슨트 시각
OFF = 10.0; DM = dur('mainc.mp4'); TOT = dur('silent.mp4')
times = [(off if k == 'abs' else OFF + DM + off if k == 'out' else OFF + T(k) + off, txt) for k, off, txt in DOCENT]
json.dump(dict(times=times, total=TOT, bands=[(f, OFF + a, OFF + b) for f, a, b in ev], cut=cut), open('timeline.json', 'w'), ensure_ascii=False, indent=0)
print('cut', round(cut, 1), 'total', round(TOT, 1))
