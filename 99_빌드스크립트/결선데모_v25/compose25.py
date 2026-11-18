"""v25 결선 데모 (1920×1080, 16:9 — PPT 삽입용).
v23 의 대사 맞춤 편집(무음 구간 없음)은 유지하고, v20 처럼 GUI 전체 화면 + 아래 자막 띠(단계 · 문장) + 주황 강조 상자 · 설명 카드를 다시 넣음.
강조 상자는 녹화 중이 아니라 편집에서 그림(녹화 때 기록한 요소 위치 rects 기준) — 화면 배치가 바뀌어도 어긋나지 않음.
출력: v25_자막.mp4(무음) · v25_음성.mp4. 사용: python3 compose24.py <서버 run 폴더>"""
import json, subprocess, sys, os, glob, asyncio
from urllib.parse import quote
from PIL import Image, ImageDraw, ImageFont, ImageChops
RUN = sys.argv[1]
M = json.load(open('marks.json')); SEQ = json.load(open('seq.json')); CL = {c['k']: c for c in json.load(open('clips.json'))}
RECT = M['rects']; OW, OH = 1920, 1080; CW, CH = 1707, 960; OX = (OW - CW) // 2; SC = CW / 1600; BAND_Y = 960
def ff(*a): subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *a], check=True)
ENC = ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', '30']
t = lambda k: M[k] + 0.7
FB = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'; FR = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
F = lambda p, s: ImageFont.truetype(p, s, index=1)
R = {r['k']: r for r in M['rows']}; m0, m1 = 94.9, float(M['mass_final']); dm = (m0 - m1) / m0 * 100
sh0, sh1 = R['shake']['v0'], R['shake']['v']
need = lambda k, extra=0.7: CL[k]['dur'] + extra
# ---------- 강조 상자 + 설명 카드 (출력 좌표, 1920×1080 RGBA)
def hl(name, rects, title, body, pos='r', dim=True):
    im = Image.new('RGBA', (OW, OH), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    bx = [(OX + x * SC, y * SC, OX + (x + w) * SC, (y + h) * SC) for x, y, w, h in rects]
    x0 = min(b[0] for b in bx) - 7; y0 = min(b[1] for b in bx) - 7; x1 = max(b[2] for b in bx) + 7; y1 = max(b[3] for b in bx) + 7
    if dim:
        m = Image.new('RGBA', (OW, BAND_Y), (8, 14, 28, 105)); md = ImageDraw.Draw(m); md.rounded_rectangle([x0, y0, x1, y1], radius=12, fill=(0, 0, 0, 0))
        im.alpha_composite(m)
    d.rounded_rectangle([x0, y0, x1, y1], radius=12, outline=(255, 176, 32, 255), width=5)
    ft, fb_ = F(FB, 29), F(FR, 23); L = body.split('\n')
    cw = max(d.textlength(title, font=ft), *[d.textlength(l, font=fb_) for l in L]) + 44; ch = 58 + 34 * len(L)
    if pos == 'r': cx, cy = x1 + 18, y0
    elif pos == 'l': cx, cy = x0 - 18 - cw, y0
    elif pos == 'b': cx, cy = x0, y1 + 16
    elif pos == 't': cx, cy = x0, y0 - 16 - ch
    else: cx, cy = x0 + 24, y0 + 24                      # 안쪽
    cx = max(10, min(OW - cw - 10, cx)); cy = max(10, min(BAND_Y - ch - 10, cy))
    d.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=14, fill=(17, 26, 43, 245), outline=(255, 176, 32, 255), width=2)
    d.text((cx + 22, cy + 10), title, font=ft, fill=(255, 209, 102))
    for i, l in enumerate(L): d.text((cx + 22, cy + 52 + 34 * i), l, font=fb_, fill=(255, 255, 255))
    im.save(f'hl_{name}.png'); return f'hl_{name}.png'
r_ = lambda tag, s: RECT[tag][s]
# ---------- 자막 띠 (v20 형식, 1920×120)
async def mk_bands(B):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': OW, 'height': 120})
        for k, (i, a, n, tg) in B.items():
            await pg.goto('file://' + os.path.abspath('nar.html') + f'?i={quote(i)}&a={quote(a)}&n={quote(n)}&t={quote(tg)}')
            await pg.wait_for_timeout(150); await pg.screenshot(path=f'band_{k}.png')
        await b.close()
TAG = '계산 기록 재생'
BANDS = {
    'A': ('1', '입력', '만들고 싶은 제품을 문장으로 쓰고, 모양은 스케치로 그립니다', ''),
    'B': ('2', '설계 사양', '요구를 진동 · 열 · 무게 같은 물리 조건으로 바꾸고, 수치마다 근거를 붙입니다', ''),
    'C': ('3', '초기 설계', '기본형 초기 설계를 정밀 시뮬레이션으로 판정 — 다섯 기준 중 <em style="color:#ff8a96">네 개 미달</em>', ''),
    'Dai': ('4', 'AI 탐색', '형상 AI가 모양을 바꾸고, 물리 AI가 성능을 바로 예측합니다 — 300회', TAG),
    'Dpick': ('4', '후보 선택', 'AI 후보 31개를 정밀 계산(FEM)으로 확인 → 진동에 가장 강한 후보', TAG),
    'Dref': ('5', '정밀 최적화', '후보에서 출발해 3D 프린트 조건(45°)을 지키며 재료를 깎아 냅니다', TAG),
    'E': ('6', '검증', f'최종 형상을 다시 판정 — <em>다섯 기준 모두 충족</em> · 무게 <em>{dm:.1f} % 감소</em>', ''),
    'draw': ('✓', '제작 파일', 'A3 도면과 3D 프린트 파일 자동 생성 — 바로 출력해 제품을 만들 수 있습니다', ''),
}
asyncio.run(mk_bands(BANDS))
SEG = []
def finish(name, src_args, base_vf, d, hls, band=True):
    """src → 1600×900 기준 화면(base_vf) → 1707×960 → 1920×1080 바탕 · 강조(hls: [(png, a, b)]) · 자막 띠"""
    ins = list(src_args); n_in = 1
    fl = f'[0:v]{base_vf},scale={CW}:{CH}:flags=lanczos,pad={OW}:{OH}:{OX}:0:color=0x0b1220,fps=30[v0];'; k = 0
    for png, a, b in hls:
        ins += ['-loop', '1', '-t', f'{d:.2f}', '-i', png]
        fl += f"[v{k}][{n_in}:v]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[v{k + 1}];"; n_in += 1; k += 1
    if band:
        ins += ['-loop', '1', '-t', f'{d:.2f}', '-i', f'band_{name}.png']; fl += f'[v{k}][{n_in}:v]overlay=0:{BAND_Y}[v{k + 1}];'; k += 1
    ff(*ins, '-filter_complex', fl.rstrip(';'), '-map', f'[v{k}]', '-t', f'{d:.2f}', '-an', *ENC, f'seg_{name}.mp4'); SEG.append((name, d))
def raw(a, b, d):
    sp = min(2.5, max(0.6, (b - a) / d))
    return ['-ss', f'{a:.2f}', '-t', f'{b - a:.2f}', '-i', 'raw.mp4'], f'setpts=(PTS-STARTPTS)/{sp:.4f},tpad=stop_mode=clone:stop_duration=10'
def steps(name, items, d):
    tot = sum(w for _, w in items); L = ''.join(f"file '{f}'\nduration {d * w / tot:.4f}\n" for f, w in items) + f"file '{items[-1][0]}'\n"
    open(f'{name}.txt', 'w').write(L); return ['-f', 'concat', '-safe', '0', '-i', f'{name}.txt'], 'scale=1600:900'
# ---------- 시작 · 끝 카드 (최종 형상 회전 렌더)
def bgc():
    c = Image.new('RGB', (OW, OH), (9, 14, 26)); d = ImageDraw.Draw(c)
    for y in range(OH): d.line([(0, y), (OW, y)], fill=(9 + y * 8 // OH, 14 + y * 10 // OH, 26 + y * 14 // OH))
    return c
def card(render, big, subs, lines, a=1.0):
    c = bgc().convert('RGBA'); r = render.copy(); r.thumbnail((1220, 915))
    m = Image.new('L', r.size, 0); md = ImageDraw.Draw(m)
    for i in range(r.width): md.line([(i, 0), (i, r.height)], fill=int(255 * min(1, i / 380) ** 1.5))
    r.putalpha(ImageChops.multiply(r.getchannel('A'), m)); c.alpha_composite(r, (OW - r.width - 10, (OH - r.height) // 2))
    d = ImageDraw.Draw(c); k = int(255 * a); y = 380
    d.text((120, y), big, font=F(FB, 120), fill=(255, 255, 255, k)); y += 165
    for s_ in subs: d.text((124, y), s_, font=F(FB, 46), fill=(143, 179, 255, k)); y += 66
    y += 14
    for s_ in lines: d.text((124, y), s_, font=F(FR, 34), fill=(95, 211, 166, k)); y += 52
    return c.convert('RGB')
os.makedirs('hero24', exist_ok=True); fr = sorted(glob.glob('../hero/A3/*.png'))
for i, f in enumerate(fr):
    card(Image.open(f).convert('RGBA'), 'FormProof', ['자전거 폰 거치대 설계 시연'], [], min(1.0, i / 25)).save(f'hero24/{i:03d}.jpg', quality=93)
d0 = need('open', 1.0)
ff('-framerate', f'{len(fr) / d0:.4f}', '-i', 'hero24/%03d.jpg', '-vf', 'fps=30', '-t', f'{d0:.2f}', *ENC, 'seg_open.mp4'); SEG.append(('open', d0))
# ---------- 화면 흐름 (GUI 화면 구성: 단계마다 배치가 바뀜) — 이번 녹화 화면에서 뽑은 3장
def grab(tt, fn): ff('-ss', f'{tt:.2f}', '-i', 'raw.mp4', '-frames:v', '1', fn); return Image.open(fn).convert('RGB')
th = [grab(t('inend') - 0.3, 'fl0.png'), grab(t('rjudge') + 1.0, 'fl1.png'), grab(t('cmp') + 1.0, 'fl2.png')]
fc = bgc(); d_ = ImageDraw.Draw(fc)
d_.text((110, 90), '화면 흐름', font=F(FB, 54), fill=(255, 255, 255))
d_.text((112, 168), '단계가 진행되면 화면 배치가 바뀝니다 — 지금 단계에 필요한 것만 크게', font=F(FR, 28), fill=(154, 166, 189))
TX = [('①②', '입력 · 설계 사양', ['왼쪽: 입력(문장 · 스케치 · 사진 · 문서 · CAD)', '오른쪽: 요구 → 물리 조건 · 설계 사양 표']),
      ('③④', '초기 설계 · 물리 최적화', ['가운데 3D 설계안 · 옆 물리 분포', '오른쪽 성능 판정 · 아래 계산 기록']),
      ('⑤', '결과 · 제작 파일', ['초기 ↔ 최적 비교 (같은 색 척도)', '도면 · 3D 프린트 파일'])]
for i, (im_, (no, ttl, ls)) in enumerate(zip(th, TX)):
    x = 110 + i * 590; w = 520; im2 = im_.resize((w, int(w * 9 / 16)), Image.LANCZOS)
    fc.paste(im2, (x, 260)); d_.rounded_rectangle([x - 3, 257, x + w + 3, 260 + im2.height + 3], radius=10, outline=(255, 176, 32), width=4)
    if i < 2: d_.text((x + w + 18, 260 + im2.height // 2 - 30), '▶', font=F(FB, 44), fill=(255, 176, 32))
    y = 260 + im2.height + 34
    d_.rounded_rectangle([x, y, x + 24 + d_.textlength(no, font=F(FB, 24)) + 4, y + 42], radius=21, fill=(37, 99, 235))
    d_.text((x + 14, y + 4), no, font=F(FB, 24), fill=(255, 255, 255))
    d_.text((x + 24 + d_.textlength(no, font=F(FB, 24)) + 22, y), ttl, font=F(FB, 32), fill=(255, 255, 255))
    for j, l in enumerate(ls): d_.text((x, y + 62 + 40 * j), l, font=F(FR, 24), fill=(154, 166, 189))
fc.crop((0, 0, OW, BAND_Y)).save('flow_c.png')
BANDS['flow'] = ('★', '화면 흐름', '단계가 진행되면 화면이 입력 → 설계 · 최적화 → 결과 순으로 바뀝니다', '')
asyncio.run(mk_bands({'flow': BANDS['flow']}))
d = need('flow', 0.8)
fl_img = Image.new('RGB', (OW, OH), (11, 18, 32)); fl_img.paste(Image.open('flow_c.png'), (0, 0)); fl_img.paste(Image.open('band_flow.png').convert('RGB'), (0, BAND_Y)); fl_img.save('flow_full.png')
ff('-loop', '1', '-i', 'flow_full.png', '-t', f'{d:.2f}', *ENC, 'seg_flow.mp4'); SEG.append(('flow', d))
# ---------- 1 입력
d = need('A'); src, vf = raw(t('in') + 0.3, t('inend'), d)
finish('A', src, vf, d, [(hl('A', [r_('in', '#text'), r_('in', '#sketchBox')], '아이디어 입력', '요청은 문장으로\n모양은 손 스케치로'), 0, d)])
# ---------- 2 설계 사양
d = need('B'); src, vf = raw(t('specshow') - 0.4, t('go') - 0.8, d); rq = r_('spec', '#reqMap')
finish('B', src, vf, d, [(hl('B', [rq], '요구 → 물리 조건', '“안 흔들리게” → 떨림 주파수 ≥ 95 Hz\n수치마다 근거 (실측 · 규격)', 'in'), 0.3, d)])
# ---------- 3 초기 설계
d = need('C'); src, vf = raw(t('rsim') - 0.4, t('opt'), d)
finish('C', src, vf, d, [(hl('C1', [r_('first', '#vS0'), r_('first', '#vS1'), r_('first', '#vS2')], '정밀 시뮬레이션', '응력 · 흔들림 · 온도 분포\n빨강일수록 불리', 'l'), 0.3, d * 0.5),
                         (hl('C2', [r_('first', '.cperf')], '성능 판정', '흔들림 5.58배 · 기준 5개 중 4개 미달', 'l'), d * 0.5, d)])
# ---------- 4 AI 탐색 · 후보 · 5 정밀 최적화 (한 장씩 캡처, 옆면 시점)
ai = [s for s in SEQ if s['stage'] == 'ai']; pk = [s for s in SEQ if s['stage'] == 'pick']; rf = [s for s in SEQ if s['stage'] == 'refine']
fn = lambda s: f"st/{s['n']:04d}.jpg"; V3 = r_('pick', '#vMain')
d = need('Dai', 2.8); src, vf = steps('Dai', [(fn(s), 3.0 if s['it'] <= 40 else 1.0) for s in ai], d)
finish('Dai', src, vf, d, [(hl('Dai1', [V3], 'AI 탐색', '형상 AI가 모양을 바꾸고 물리 AI가 성능을 바로 예측\n옆에서 본 모습 · 노란 반투명 = 처음 형상', 'r', dim=False), 0, d * 0.6),
                           (hl('Dai2', [r_('pick', '#metrics')], 'AI 예측 성능', '형상이 바뀔 때마다 기준별 값을 바로 예측', 'l', dim=False), d * 0.6, d)])
d = need('Dpick', 0.4); src, vf = steps('Dpick', [(fn(pk[0]), 1.0)], d)
finish('Dpick', src, vf, d, [(hl('Dpick', [r_('pick', '#candP')], '후보 선택', 'AI 후보 31개를 정밀 계산(FEM)으로 확인\n통과 11개 중 진동수 여유가 가장 큰 후보', 't'), 0, d)])
d = need('Dref', 1.6); src, vf = steps('Dref', [(fn(s), 2.0 if i < 6 else 1.0) for i, s in enumerate(rf[:-1])] + [(fn(rf[-2]), 4.0)], d)
finish('Dref', src, vf, d, [(hl('Dref', [V3], '정밀 최적화', '후보에서 출발 · FEM 120회 · 3D 프린트 조건(45°)\n필요 없는 재료를 깎아 냄', 'r', dim=False), 0, d)])
# ---------- 6 검증
d = need('E'); src, vf = raw(t('done') - 0.2, t('draw') - 1.6, d)
finish('E', src, vf, d, [(hl('E1', [r_('done', '#resBar')], '검증 통과', '최종 형상을 정밀 시뮬레이션으로 다시 판정', 'b'), 0.2, d * 0.45),
                         (hl('E2', [r_('cmp', '#cmpOv .cc[data-k="shake"]')], '흔들림 비교', f'같은 색 척도 · 빨강일수록 불리\n최대 {sh0:.2f}배 → {sh1:.2f}배 (두 방향 중 큰 값)', 'r'), d * 0.45, d)])
# ---------- 제작 파일 (도면 이미지)
im = Image.open(os.path.join(RUN, 'opt_final_drawing.png')).convert('RGB'); im.thumbnail((1580, 890), Image.LANCZOS)
pg_ = Image.new('RGB', (1600, 900), 'white'); ox, oy = (1600 - im.width) // 2, (900 - im.height) // 2; pg_.paste(im, (ox, oy)); pg_.save('dwg.png')
s_ = im.width / 420; P = lambda x, y: (ox + x * s_, oy + (297 - y) * s_)
def mmrect(x0, y0, x1, y1): a = P(x0, y1); b = P(x1, y0); return (a[0], a[1], b[0] - a[0], b[1] - a[1])
d = need('draw', 0.8)
finish('draw', ['-loop', '1', '-t', f'{d:.2f}', '-i', 'dwg.png'], 'scale=1600:900', d,
       [(hl('dw1', [mmrect(20, 10, 410, 287)], '제작 도면 자동 생성', f'3면도 · 등각도 · 구멍 표 · 표제란 ({M["dw"]["seconds"]:.0f}초)', 'in', dim=False), 0.2, d * 0.5),
        (hl('dw2', [mmrect(270, 10, 410, 58.6)], '표제란', f'재질 PETG · 질량 {M["dw"]["mass_g"]} g · 척도 1:1', 't'), d * 0.5, d)])
card(Image.open('../hero/C3/000.png').convert('RGBA'), 'FormProof', ['형상을 성능으로 증명'], [f'5 / 5 기준 충족 · 무게 −{dm:.1f} %', f'흔들림 {sh0:.1f}배 → {sh1:.1f}배']).save('end.png')
de = need('end', 1.2); ff('-loop', '1', '-i', 'end.png', '-t', f'{de:.2f}', *ENC, 'seg_end.mp4'); SEG.append(('end', de))
open('cat.txt', 'w').write(''.join(f"file 'seg_{n}.mp4'\n" for n, _ in SEG))
ff('-f', 'concat', '-safe', '0', '-i', 'cat.txt', '-c', 'copy', 'v25_자막.mp4')
st, acc = {}, 0.0
for n, d in SEG: st[n] = acc; acc += d
order = [c['k'] for c in json.load(open('clips.json'))]
a = ['ffmpeg', '-y', '-loglevel', 'error', '-i', 'v25_자막.mp4'] + sum([['-i', f'clips/c{i:02d}.wav'] for i in range(len(order))], [])
fl = ''.join(f'[{i + 1}:a]aresample=48000,adelay={int((st[k] + 0.25) * 1000)}|{int((st[k] + 0.25) * 1000)},apad[a{i}];' for i, k in enumerate(order))
fl += ''.join(f'[a{i}]' for i in range(len(order))) + f'amix=inputs={len(order)}:normalize=0,loudnorm=I=-16:TP=-1.5,atrim=0:{acc:.2f}[o]'
subprocess.run(a + ['-filter_complex', fl, '-map', '0:v', '-map', '[o]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ac', '2', '-shortest', 'v25_음성.mp4'], check=True)
json.dump(dict(seg={n: round(d, 2) for n, d in SEG}, start={k: round(v, 2) for k, v in st.items()}, total=round(acc, 2)), open('timeline.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(dict(total=round(acc, 1), seg={n: round(d, 1) for n, d in SEG}), ensure_ascii=False))
