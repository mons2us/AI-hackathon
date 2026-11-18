"""v22 결선 데모(약 90초) 합성: 녹화(raw) + 한 장씩 캡처(st/) → 구간 잘라 붙이기 · 자막 띠 · 도면 강조 · 시작/끝 카드.
출력: silent.mp4 (자막판, 소리 없음) · timeline.json (도슨트 시각). 사용: python3 compose21.py <서버 run 폴더>"""
import json, subprocess, sys, os, asyncio, glob
from urllib.parse import quote
from PIL import Image, ImageDraw, ImageFont
import plan22 as plan21
RUN = sys.argv[1]
M = json.load(open('marks.json')); SEQ = json.load(open('seq.json')); dw = M['dw']
def ff(*a): subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *a], check=True)
def dur(f): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))
ENC = ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', '30']
OF = 0.7; t = lambda k: M[k] + OF                                      # 마커 → 녹화 영상 시각
if not os.path.exists('raw.mp4'):
    ff('-i', glob.glob('*.webm')[0], *ENC, 'raw.mp4')
R = {r['k']: r for r in M['rows']}
m0, m1 = 94.9, float(M['mass_final']); dm = (m0 - m1) / m0 * 100
sh0, sh1 = R['shake']['v0'], R['shake']['v']
fail0 = M.get('fail0', 4)
def ko(x, d=1):
    D = '영일이삼사오육칠팔구'
    def intk(n):
        if n == 0: return '영'
        s = ''; 
        for v, u in ((1000, '천'), (100, '백'), (10, '십')):
            q, n = divmod(n, v)
            if q: s += ('' if q == 1 else D[q]) + u
        return s + (D[n] if n else '')
    a = f'{x:.{d}f}'; i, _, f = a.partition('.')
    f = f.rstrip('0')
    return intk(int(i)) + (' 점 ' + ''.join(D[int(c)] for c in f) if f else '')
NUMK = {1: '한', 2: '두', 3: '세', 4: '네', 5: '다섯'}
V = dict(fail0=fail0, dm=dm, sh0=sh0, sh1=sh1, say=dict(fail0=NUMK[fail0], dm=ko(dm), sh0=ko(sh0), sh1=ko(sh1, 2)))
# 1) 구간
SEG = []                                                                # (이름, 파일, 길이)
def cut(name, a, b, speed=1.0):
    ff('-ss', f'{a:.2f}', '-t', f'{b - a:.2f}', '-i', 'raw.mp4', '-vf', f'setpts=PTS/{speed}', '-an', *ENC, f'seg_{name}.mp4')
    SEG.append((name, f'seg_{name}.mp4', dur(f'seg_{name}.mp4')))
# 단계 캡처 → 영상 (AI 12 장/초, 후보 화면 5초, 정밀 최적화 2.5 장/초, 강조 바뀔 때 0.7초)
lines, vt, prev, cur = [], {}, 'x', 0.0
SEQ0 = next(s['n'] for s in SEQ if s['stage'] == 'refine')
for s in SEQ:
    d = (1 / 4 if s['it'] <= 40 else 1 / 12) if s['stage'] == 'ai' else (5.0 if s['stage'] == 'pick' else (1 / 2 if s['n'] - SEQ0 <= 6 else 1 / 3))
    key = {'ai': 'Dai', 'graph': None, 'pick': 'Dpick', 'ref': 'Dref'}[s['hl']]
    if s['hl'] != prev:
        if key: vt.setdefault(key, cur)
        d += 0.7; prev = s['hl']
    lines.append(f"file 'st/{s['n']:04d}.jpg'\nduration {d:.4f}\n"); cur += d
lines.append(f"duration 0.8\nfile 'st/{SEQ[-1]['n']:04d}.jpg'\n")
open('st.txt', 'w').write(''.join(lines))
# 시작 카드: 결과 화면 위에 큰 제목
ff('-ss', f"{t('done') + 2.0:.2f}", '-i', 'raw.mp4', '-frames:v', '1', 'open_bg.png')
FB = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'; FR = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
def card_open():
    im = Image.open('open_bg.png').convert('RGBA').resize((1600, 900))
    ov = Image.new('RGBA', (1600, 900), (8, 12, 24, 150)); im = Image.alpha_composite(im, ov); d = ImageDraw.Draw(im)
    d.text((90, 300), 'FormProof', font=ImageFont.truetype(FB, 96, index=1), fill=(255, 255, 255))
    d.text((94, 430), '문장 한 줄 + 스케치  →  검증된 3D 프린트 설계', font=ImageFont.truetype(FB, 46, index=1), fill=(255, 209, 102))
    d.text((94, 510), f'다섯 기준 모두 충족 · 무게 {dm:.1f} % 감소 · 흔들림 {sh0:.1f}배 → {sh1:.2f}배', font=ImageFont.truetype(FR, 32, index=1), fill=(95, 211, 166))
    c = Image.new('RGB', (1600, 1010), (17, 26, 43)); c.paste(im.convert('RGB'), (0, 0)); c.save('open.png')
def card_end():
    c = Image.new('RGB', (1600, 1010), (11, 15, 25)); d = ImageDraw.Draw(c)
    d.text((120, 300), 'FormProof', font=ImageFont.truetype(FB, 110, index=1), fill=(255, 255, 255))
    d.text((126, 450), '형상을 성능으로 증명', font=ImageFont.truetype(FB, 44, index=1), fill=(143, 179, 255))
    d.text((126, 560), 'AI 형상 탐색 300  →  후보 31 정밀 계산(FEM)  →  정밀 최적화 120회  →  5 / 5 충족  →  도면 · STL',
           font=ImageFont.truetype(FR, 30, index=1), fill=(154, 166, 189))
    c.save('end.png')
card_open(); card_end()
ff('-loop', '1', '-i', 'open.png', '-t', '4.5', *ENC, 'seg_open.mp4'); SEG.append(('open', 'seg_open.mp4', 4.5))
SEG_F = []
cut('A', t('in') + 0.3, t('inend'), 1.7)
cut('B', t('spec'), t('go'))
cut('C', t('first') + 0.4, t('opt'))
ff('-f', 'concat', '-safe', '0', '-i', 'st.txt', '-vf', 'fps=30,scale=1600:900', *ENC, 'seg_D.mp4'); SEG.append(('D', 'seg_D.mp4', dur('seg_D.mp4')))
cut('E', t('done') - 0.2, t('end'))
ff('-loop', '1', '-i', 'end.png', '-t', '3.5', *ENC, 'seg_end.mp4'); SEG.append(('end', 'seg_end.mp4', 3.5))
# 시작 시각
start, acc = {}, 0.0
for n, f, d in SEG: start[n] = acc; acc += d
TOT = acc
K = dict(open=0.0, A=start['A'], B=start['B'], C=start['C'], Dai=start['D'] + vt['Dai'], Dpick=start['D'] + vt['Dpick'], Dref=start['D'] + vt['Dref'],
         Edone=start['E'], Ecmp=start['E'] + (M['cmp'] - M['done']) + 0.2, Edraw=start['E'] + (M['draw'] - M['done']) + 0.2, end=start['end'])
# 2) 자막 띠
B = plan21.bands(V)
async def mkbands():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1600, 'height': 110})
        for j, (k, i, a, n, tg) in enumerate(B):
            await pg.goto('file://' + os.path.abspath('nar.html') + f'?i={quote(i)}&a={quote(a)}&n={quote(n)}&t={quote(tg)}')
            await pg.wait_for_timeout(150); await pg.screenshot(path=f'b_{j:02d}.png')
        await b.close()
asyncio.run(mkbands())
ev = [(f'b_{j:02d}.png', K[k], K[B[j + 1][0]] if j + 1 < len(B) else K['end']) for j, (k, *_) in enumerate(B)]
# 3) 도면 강조
im = Image.open(os.path.join(RUN, 'opt_final_drawing.png')).convert('RGB'); im.thumbnail((1580, 890), Image.LANCZOS)
w, h = im.size; ox, oy = (1600 - w) // 2, (900 - h) // 2; s = w / 420; P = lambda x, y: (ox + x * s, oy + (297 - y) * s)
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
frame([(20, 10, 410, 287)], '제작 도면 자동 생성', f'최적 설계 → A3 도면 자동 생성 ({dw["seconds"]:.0f}초)\n3면도 · 등각도 · 구멍 표 · 표제란', P(100, 150)).save('dC.png')
frame([(270, 10, 410, 58.6)], '표제란', f'재질 PETG · 질량 {dw["mass_g"]} g · 척도 1:1 · 3각법', P(150, 108)).save('dA.png')
d0 = K['Edraw'] + 1.0; dseq = [('dC.png', d0, d0 + 3.0), ('dA.png', d0 + 3.0, K['end'])]
order = ['open', 'A', 'B', 'C', 'D', 'E', 'end']
open('cat.txt', 'w').write(''.join(f"file '{f}'\n" for n in order for (nn, f, d) in SEG if nn == n))
ff('-f', 'concat', '-safe', '0', '-i', 'cat.txt', '-c', 'copy', 'joined.mp4')
inp = ['-i', 'joined.mp4'] + sum([['-loop', '1', '-t', f'{TOT:.2f}', '-i', f] for f, _, _ in ev + dseq], [])
fl = '[0:v]pad=1600:1010:0:0:color=0x111a2b[v0];'; n = 0
for i, (f, a, b) in enumerate(ev): fl += f"[v{n}][{i + 1}:v]overlay=0:900:enable='between(t,{a:.2f},{b:.2f})'[v{n + 1}];"; n += 1
for j, (f, a, b) in enumerate(dseq): fl += f"[v{n}][{len(ev) + 1 + j}:v]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[v{n + 1}];"; n += 1
ff(*inp, '-filter_complex', fl.rstrip(';'), '-map', f'[v{n}]', '-t', f'{TOT:.2f}', *ENC, 'silent.mp4')
DOC = [(K[k] + off, txt) for k, off, txt in plan21.docent(V)]
json.dump(dict(times=DOC, total=dur('silent.mp4'), K=K, V={k: v for k, v in V.items() if k != 'say'}, seg={n: round(d, 2) for n, f, d in SEG}),
          open('timeline.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(dict(total=round(dur('silent.mp4'), 1), seg={n: round(d, 1) for n, f, d in SEG}), ensure_ascii=False))
