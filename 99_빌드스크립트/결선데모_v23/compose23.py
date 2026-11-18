"""v23 결선 데모: 도슨트 길이에 맞춰 구간 길이를 정함(무음 구간 없음) · 강조 상자/설명 카드 없음 · 필요한 곳만 확대 ·
짧은 자막(단계 + 한 구절). 출력: v23_자막.mp4(무음) · v23_음성.mp4. 사용: python3 compose23.py <서버 run 폴더>"""
import json, subprocess, sys, os, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter
RUN = sys.argv[1]
M = json.load(open('marks.json')); SEQ = json.load(open('seq.json')); CL = {c['k']: c for c in json.load(open('clips.json'))}
RECT = M['rects']; W, H = 1600, 900
def ff(*a): subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *a], check=True)
def dur(f): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))
ENC = ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', '30']
t = lambda k: M[k] + 0.7
if not os.path.exists('raw.mp4'): ff('-i', glob.glob('*.webm')[0], *ENC, 'raw.mp4')
FB = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'; FR = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
F = lambda p, s: ImageFont.truetype(p, s, index=1)
R = {r['k']: r for r in M['rows']}; m0, m1 = 94.9, float(M['mass_final']); dm = (m0 - m1) / m0 * 100
sh0, sh1 = R['shake']['v0'], R['shake']['v']
def box(*sels, tag=None, pad=24):                    # 요소들을 감싸는 16:9 확대 영역
    rs = [RECT[tag][s] for s in sels if s in RECT[tag] and RECT[tag][s][2] > 2]
    x0 = min(r[0] for r in rs) - pad; y0 = min(r[1] for r in rs) - pad; x1 = max(r[0] + r[2] for r in rs) + pad; y1 = max(r[1] + r[3] for r in rs) + pad
    w, h = x1 - x0, y1 - y0
    if w / h > 16 / 9: h = w * 9 / 16
    else: w = h * 16 / 9
    w, h = min(w, W), min(h, H); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    x = min(max(0, cx - w / 2), W - w); y = min(max(0, cy - h / 2), H - h)
    return f'crop={int(w)}:{int(h)}:{int(x)}:{int(y)},scale={W}:{H}:flags=lanczos'
FULL = f'scale={W}:{H}'
def caption(name, chip, text, tag=''):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if chip:
        fc, ft = F(FB, 26), F(FB, 34); cw = d.textlength(chip, font=fc) + 36; tw = d.textlength(text, font=ft)
        x, y = 48, H - 104; bw = cw + tw + 52
        d.rounded_rectangle([x, y, x + bw, y + 64], radius=32, fill=(10, 16, 30, 225))
        d.rounded_rectangle([x + 8, y + 8, x + 8 + cw, y + 56], radius=24, fill=(37, 99, 235, 255))
        d.text((x + 8 + 18, y + 13), chip, font=fc, fill=(255, 255, 255)); d.text((x + cw + 32, y + 9), text, font=ft, fill=(255, 255, 255))
    if tag:
        ft2 = F(FR, 20); tw2 = d.textlength(tag, font=ft2)
        d.rounded_rectangle([W - tw2 - 70, 24, W - 24, 62], radius=19, fill=(10, 16, 30, 200), outline=(255, 209, 102, 255), width=2)
        d.text((W - tw2 - 47, 29), tag, font=ft2, fill=(255, 209, 102))
    im.save(f'cap_{name}.png'); return f'cap_{name}.png'
SEG = []
def need(k, extra=0.7): return CL[k]['dur'] + extra
def from_raw(name, a, b, vf, d, cap):
    sp = min(2.5, max(0.6, (b - a) / d))
    ff('-ss', f'{a:.2f}', '-t', f'{b - a:.2f}', '-i', 'raw.mp4', '-loop', '1', '-i', cap, '-filter_complex',
       f'[0:v]setpts=(PTS-STARTPTS)/{sp:.4f},{vf},tpad=stop_mode=clone:stop_duration=10,fps=30[v];[v][1:v]overlay=0:0', '-t', f'{d:.2f}', '-an', *ENC, f'seg_{name}.mp4')
    SEG.append((name, d))
def from_still(name, img, d, cap, zoom=True):
    z = f"zoompan=z='min(1+0.0009*on,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(d * 30) + 5}:s={W}x{H}:fps=30" if zoom else f'scale={W}:{H}'
    ff('-loop', '1', '-i', img, '-loop', '1', '-i', cap, '-filter_complex', f'[0:v]scale={W}:{H},{z}[v];[v][1:v]overlay=0:0', '-t', f'{d:.2f}', *ENC, f'seg_{name}.mp4')
    SEG.append((name, d))
def from_steps(name, items, vf, cap, d):              # items: [(파일, 상대 비중)] → 합이 d 가 되게
    tot = sum(w for _, w in items); L = ''.join(f"file '{f}'\nduration {d * w / tot:.4f}\n" for f, w in items) + f"file '{items[-1][0]}'\n"
    open(f'{name}.txt', 'w').write(L)
    ff('-f', 'concat', '-safe', '0', '-i', f'{name}.txt', '-loop', '1', '-i', cap, '-filter_complex', f'[0:v]{vf},fps=30[v];[v][1:v]overlay=0:0', '-t', f'{d:.2f}', *ENC, f'seg_{name}.mp4')
    SEG.append((name, d))
# --- 시작 카드: 최종 형상을 돌려 보는 렌더(../hero/A2, 같은 GUI 장면을 별도 렌더러로) + 제목
HERO = '../hero'
def bgc():
    c = Image.new('RGB', (W, H), (9, 14, 26)); d = ImageDraw.Draw(c)
    for y in range(H): d.line([(0, y), (W, y)], fill=(9 + y * 8 // H, 14 + y * 10 // H, 26 + y * 14 // H))
    return c
def compose_card(render, big, subs, lines, alpha_txt=1.0):
    c = bgc().convert('RGBA'); r = render.copy(); r.thumbnail((1000, 750))
    m = Image.new('L', r.size, 0); md = ImageDraw.Draw(m)
    for i in range(r.width): md.line([(i, 0), (i, r.height)], fill=int(255 * min(1, i / 320) ** 1.5))
    from PIL import ImageChops; r.putalpha(ImageChops.multiply(r.getchannel('A'), m)); c.alpha_composite(r, (W - r.width - 10, (H - r.height) // 2))
    g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for i in range(640): gd.line([(i, 0), (i, H)], fill=(9, 14, 26, int(230 * max(0, 1 - i / 640) ** 0.8)))
    c.alpha_composite(g); d = ImageDraw.Draw(c); k = int(255 * alpha_txt); y = 300
    d.text((96, y), big, font=F(FB, 100), fill=(255, 255, 255, k)); y += 140
    for t_ in subs: d.text((100, y), t_, font=F(FB, 40), fill=(143, 179, 255, k)); y += 58
    y += 16
    for t_ in lines: d.text((100, y), t_, font=F(FR, 30), fill=(95, 211, 166, k)); y += 46
    return c.convert('RGB')
os.makedirs('hero_f', exist_ok=True)
fr = sorted(glob.glob(f'{HERO}/A3/*.png'))
for i, f in enumerate(fr):
    compose_card(Image.open(f).convert('RGBA'), 'FormProof', ['문장과 스케치에서', '검증된 3D 프린트 설계까지'], [], min(1.0, i / 25)).save(f'hero_f/{i:03d}.jpg', quality=93)
d_open = need('open', 1.0)
ff('-framerate', f'{len(fr) / d_open:.4f}', '-i', 'hero_f/%03d.jpg', '-vf', f'fps=30,scale={W}:{H}', '-t', f'{d_open:.2f}', *ENC, 'seg_open.mp4'); SEG.append(('open', d_open))
compose_card(Image.open(f'{HERO}/C3/000.png').convert('RGBA'), 'FormProof', ['형상을 성능으로 증명'],
             ['5 / 5 기준 충족', f'무게 −{dm:.1f} %  ·  흔들림 {sh0:.1f} → {sh1:.1f}배']).save('end.png')
# --- 입력 · 사양 · 초기 설계 (녹화 화면, 필요한 곳 확대)
from_raw('A', t('in') + 0.3, t('inend'), box('#text', '#sketchBox', tag='in'), need('A'), caption('A', '1  입력', '문장 한 줄 + 스케치'))
from_raw('B', t('specshow') - 0.4, t('go') - 0.8, box('#reqMap', tag='spec', pad=16), need('B'), caption('B', '2  설계 사양', '요구 → 물리 조건 + 근거'))
from_raw('C', t('first') + 2.0, t('opt'), FULL, need('C'), caption('C', '3  초기 설계', '기준 5개 중 4개 미달'))
# --- AI 탐색 · 후보 · 정밀 최적화 (한 장씩 캡처, 3D 창 확대)
VM = f'crop=1136:639:64:56,scale={W}:{H}:flags=lanczos'; TAG = '계산 기록 재생'
ai = [s for s in SEQ if s['stage'] == 'ai']; pk = [s for s in SEQ if s['stage'] == 'pick']; rf = [s for s in SEQ if s['stage'] == 'refine']
fn = lambda s: f"st/{s['n']:04d}.jpg"
from_steps('Dai', [(fn(s), 3.0 if s['it'] <= 40 else 1.0) for s in ai], VM, caption('Dai', '4  AI 탐색', '형상 AI × 물리 AI · 300회', TAG), need('Dai', 2.8))
from_steps('Dpick', [(fn(pk[0]), 1.0)], VM, caption('Dpick', '4  후보 선택', '후보 31개 정밀 계산(FEM)', TAG), need('Dpick', 0.4))
from_steps('Dref', [(fn(s), 2.0 if i < 6 else 1.0) for i, s in enumerate(rf[:-1])] + [(fn(rf[-2]), 4.0)], VM, caption('Dref', '5  정밀 최적화', 'FEM 120회 · 3D 프린트 조건', TAG), need('Dref', 1.6))
# --- 검증 · 비교
from_raw('E', t('done') - 0.2, t('draw') - 1.6, 'crop=1136:639:64:56,scale=1600:900:flags=lanczos', need('E'), caption('E', '6  검증', f'5 / 5 통과 · 무게 −{dm:.1f} %'))
from_still('draw', os.path.join(RUN, 'opt_final_drawing.png'), need('draw', 0.8), caption('draw', '7  제작 파일', 'A3 도면 · 3D 프린트 파일'))
from_still('end', 'end.png', need('end', 1.2), caption('end', '', ''), zoom=False)
open('cat.txt', 'w').write(''.join(f"file 'seg_{n}.mp4'\n" for n, _ in SEG))
ff('-f', 'concat', '-safe', '0', '-i', 'cat.txt', '-c', 'copy', 'v23_자막.mp4')
# --- 도슨트 배치 (구간 시작 + 0.25 초)
st, acc = {}, 0.0
for n, d in SEG: st[n] = acc; acc += d
order = [c['k'] for c in json.load(open('clips.json'))]
a = ['ffmpeg', '-y', '-loglevel', 'error', '-i', 'v23_자막.mp4'] + sum([['-i', f'clips/c{i:02d}.wav'] for i in range(len(order))], [])
fl = ''.join(f'[{i + 1}:a]aresample=48000,adelay={int((st[k] + 0.25) * 1000)}|{int((st[k] + 0.25) * 1000)},apad[a{i}];' for i, k in enumerate(order))
fl += ''.join(f'[a{i}]' for i in range(len(order))) + f'amix=inputs={len(order)}:normalize=0,loudnorm=I=-16:TP=-1.5,atrim=0:{acc:.2f}[o]'
subprocess.run(a + ['-filter_complex', fl, '-map', '0:v', '-map', '[o]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ac', '2', '-shortest', 'v23_음성.mp4'], check=True)
json.dump(dict(seg={n: round(d, 2) for n, d in SEG}, start={k: round(v, 2) for k, v in st.items()}, total=round(acc, 2)), open('timeline.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(dict(total=round(acc, 1), seg={n: round(d, 1) for n, d in SEG}), ensure_ascii=False))
