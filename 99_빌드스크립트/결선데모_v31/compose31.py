"""v29 결선 데모 (v28 압축 + GUI 구성 · 화면 흐름 구간) (1920×1080, 16:9 — PPT 삽입용).
v23 의 대사 맞춤 편집(무음 구간 없음)은 유지하고, v20 처럼 GUI 전체 화면 + 아래 자막 띠(단계 · 문장) + 주황 강조 상자 · 설명 카드를 다시 넣음.
강조 상자는 녹화 중이 아니라 편집에서 그림(녹화 때 기록한 요소 위치 rects 기준) — 화면 배치가 바뀌어도 어긋나지 않음.
출력: v29_자막.mp4(무음) · v29_음성.mp4. 사용: python3 compose24.py <서버 run 폴더>"""
import json, subprocess, sys, os, glob, asyncio
from urllib.parse import quote
from PIL import Image, ImageDraw, ImageFont, ImageChops
RUN = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/input-spec/10_입력_1차설계/app/runs/20261118-210926-53d995'
M = json.load(open('marks.json')); SEQ = json.load(open('seq.json')); PH = json.load(open('phr.json'))
RECT = M['rects']; OW, OH = 1920, 1080; CW, CH = 1707, 960; OX = (OW - CW) // 2; SC = CW / 1600; BAND_Y = 960
def ff(*a): subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *a], check=True)
ENC = ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', '30']
t = lambda k: M[k] + 0.7
FB = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'; FR = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
F = lambda p, s: ImageFont.truetype(p, s, index=1)
R = {r['k']: r for r in M['rows']}; m0, m1 = 94.9, float(M['mass_final']); dm = (m0 - m1) / m0 * 100
sh0, sh1 = R['shake']['v0'], R['shake']['v']
# ---------- 강조 상자 + 설명 카드 (출력 좌표, 1920×1080 RGBA)
def hl(name, rects, title='', body='', pos='r', dim=True, card=False):
    im = Image.new('RGBA', (OW, OH), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    bx = [(OX + x * SC, y * SC, OX + (x + w) * SC, (y + h) * SC) for x, y, w, h in rects]
    x0 = min(b[0] for b in bx) - 7; y0 = min(b[1] for b in bx) - 7; x1 = max(b[2] for b in bx) + 7; y1 = max(b[3] for b in bx) + 7
    y0 = max(y0, 4); y1 = min(y1, 872 * SC + 4)                        # 화면 밖(스크롤 아래)으로 나가지 않게
    if dim:
        m = Image.new('RGBA', (OW, BAND_Y), (8, 14, 28, 105)); md = ImageDraw.Draw(m); md.rounded_rectangle([x0, y0, x1, y1], radius=12, fill=(0, 0, 0, 0))
        im.alpha_composite(m)
    d.rounded_rectangle([x0, y0, x1, y1], radius=12, outline=(255, 176, 32, 255), width=5)
    if not card:
        im.save(f'hl_{name}.png'); return f'hl_{name}.png'
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
def hl_out(name, rect_out, title, body, pos='b'):        # 출력 좌표(1920×1080) 그대로
    x, y, w, h = rect_out; return hl(name, [((x - OX) / SC, y / SC, w / SC, h / SC)], title, body, pos, dim=True)
# ---------- 자막 띠 (v20 형식, 1920×120)
async def mk_bands(B):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': OW, 'height': 120})
        for k, (i, a, n, tg) in B.items():
            await pg.goto('file://' + os.path.abspath('nar.html') + f'?i={quote(i)}&a={quote(a)}&n={quote(n)}&t={quote(tg)}')
            await pg.wait_for_timeout(150); await pg.screenshot(path=f'band_{k}.png')
        await b.close()
SEG = []
def finish(name, src_args, base_vf, d, hls, band=True, bands=None):
    """src → 1600×900 기준 화면(base_vf) → 1707×960 → 1920×1080 바탕 · 강조(hls: [(png, a, b)]) · 자막 띠"""
    ins = list(src_args); n_in = 1
    fl = f'[0:v]{base_vf},scale={CW}:{CH}:flags=lanczos,pad={OW}:{OH}:{OX}:0:color=0x0b1220,fps=30[v0];'; k = 0
    for png, a, b in hls:
        ins += ['-loop', '1', '-t', f'{d:.2f}', '-i', png]
        fl += f"[v{k}][{n_in}:v]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[v{k + 1}];"; n_in += 1; k += 1
    for png, a, b in (bands or []):
        ins += ['-loop', '1', '-t', f'{d:.2f}', '-i', png]
        fl += f"[v{k}][{n_in}:v]overlay=0:{BAND_Y}:enable='between(t,{a:.2f},{b:.2f})'[v{k + 1}];"; n_in += 1; k += 1
    if band and not bands:
        ins += ['-loop', '1', '-t', f'{d:.2f}', '-i', f'band_{name}.png']; fl += f'[v{k}][{n_in}:v]overlay=0:{BAND_Y}[v{k + 1}];'; k += 1
    ff(*ins, '-filter_complex', fl.rstrip(';'), '-map', f'[v{k}]', '-t', f'{d:.2f}', '-an', *ENC, f'seg_{name}.mp4'); SEG.append((name, d))
def raw(a, b, d, maxsp=2.5):
    sp = min(maxsp, max(0.6, (b - a) / d))
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
LEAD, GAP, TAIL = 0.2, 0.15, 0.4
def timing(seg):
    """구간 길이와 구절 시작 시각 (구간 기준)"""
    st, x = [], LEAD
    for p in PH[seg]: st.append(x); x += p['dur'] + GAP
    return st, x - GAP + TAIL
def spans(seg, specs):
    """specs[i] = 구절 i 동안 켤 강조 png (None = 없음) → [(png, a, b)] (같은 png 가 이어지면 하나로)"""
    st, d = timing(seg); out = []
    for i, png in enumerate(specs):
        a = max(0, st[i] - 0.15); b = (st[i + 1] - 0.15) if i + 1 < len(st) else d
        if png is None: continue
        if out and out[-1][0] == png and abs(out[-1][2] - a) < 1e-6: out[-1] = (png, out[-1][1], b)
        else: out.append((png, a, b))
    return out, d
SEG = []; VO = []                                         # VO: (구간, 구절 i) → 전체 시각
def add_vo(seg):
    st, _ = timing(seg); VO.append((seg, st))
# ---------- 시작 카드
os.makedirs('hero26', exist_ok=True); fr = sorted(glob.glob('../hero/A3/*.png'))
_, d0 = timing('open')
for i, f in enumerate(fr):
    card(Image.open(f).convert('RGBA'), 'FormProof', ['자전거 폰 거치대 설계 시연'], [], min(1.0, i / 25)).save(f'hero26/{i:03d}.jpg', quality=93)
ff('-framerate', f'{len(fr) / d0:.4f}', '-i', 'hero26/%03d.jpg', '-vf', 'fps=30', '-t', f'{d0:.2f}', *ENC, 'seg_open.mp4'); SEG.append(('open', d0)); add_vo('open')
# ---------- 구절별 자막 띠 (단계 번호 · 이름은 구간마다 같고, 문장은 구절에 맞춰 바뀜)
RED = '<em style="color:#ff8a96">'
CAP = {
 'gui': ('★', 'GUI 구성 · 화면 흐름', ['위: 진행 단계 — 입력 → 설계 사양 → 초기 설계 → 물리 최적화 → 제작 파일', '① 입력 화면 — 왼쪽 입력(문장 · 스케치 · 설계 사양 표) · 오른쪽 요구 → 물리 조건', '② 설계 화면 — 3D 설계안 · 물리 분포(응력 · 흔들림 · 온도) · 성능 판정 · 계산 기록', '③ 결과 화면 — 초기 ↔ 최적 비교(같은 색 척도) · 도면 · 3D 프린트 파일'], ''),
 'A': ('1', '입력', ['요청을 한 문장으로 씁니다', '모양 · 위치 · 기울기는 스케치로 그립니다'], ''),
 'B': ('2', '설계 사양', ['[설계 사양] 버튼 → 요구가 물리 조건으로 — “안 흔들리게” → 떨림 주파수 ≥ 95 Hz', '수치마다 근거 · [확정] → [초기 설계 만들기]'], ''),
 'Csel': ('3', '초기 설계', ['미달 항목 선택 → [물리 기반 최적화 실행]'], ''),
 'C': ('3', '초기 설계', ['정밀 시뮬레이션 — 응력 · 흔들림 · 온도 분포 (빨강일수록 불리)', f'흔들림 {sh0:.2f}배 — 다섯 기준 중 {RED}네 개 미달</em>'], ''),
 'Dai': ('4', 'AI 탐색', ['형상 AI가 모양을 바꾸고, 물리 AI가 성능을 바로 예측 (노란 반투명 = 처음 형상)', '옆에서 본 모습 — 판과 보가 트러스 구조로 바뀜', 'AI 예측 성능 — 형상이 바뀔 때마다 기준별 값 예측'], '계산 기록 재생'),
 'Dpick': ('4', '후보 선택', ['AI 후보 31개를 정밀 시뮬레이션으로 확인 — ✓ 기준 통과 11개', '통과 후보 중 진동수 여유가 가장 큰 후보 (탐색 20회째 · 171 Hz)'], '계산 기록 재생'),
 'Dref': ('5', '정밀 최적화', ['고른 후보에서 출발 — 정밀 시뮬레이션으로 구조 최적화 120회', '3D 프린트 조건(45° 돌출)을 지키며 필요 없는 재료를 깎아 냄'], '계산 기록 재생'),
 'E': ('6', '검증', ['최종 형상을 다시 판정 — <em>다섯 기준 모두 충족</em>', f'최대 흔들림 {sh0:.2f}배 → <em>{sh1:.2f}배</em> (두 방향 중 큰 값) · 무게 <em>−{dm:.1f} %</em>'], ''),
 'draw': ('✓', '제작 파일', ['[도면] 버튼 → A3 제작 도면 자동 생성 (3면도 · 구멍 표 · 표제란)', '3D 프린트 파일(STL) — 바로 출력해 제품을 만들 수 있습니다'], ''),
}
asyncio.run(mk_bands({f'{k}_{j}': (v[0], v[1], n, v[3]) for k, v in CAP.items() for j, n in enumerate(v[2])}))
def bspans(seg):
    st, d = timing(seg); n = len(CAP[seg][2])
    return [(f'band_{seg}_{j}.png', 0 if j == 0 else st[j] - 0.15, (st[j + 1] - 0.15) if j + 1 < n else d) for j in range(n)]
# ---------- GUI 구성 · 화면 흐름 (실제 화면 3장, 구절마다 영역 상자 + 이름표)
RG = json.load(open('rects29.json'))
def grab(ts, out): ff('-ss', f'{ts:.2f}', '-i', 'raw.mp4', '-frames:v', '1', out); return out
g1, g2, g3 = grab(t('specshow') + 3.0, 'g1.png'), grab(t('rjudge') + 2.0, 'g2.png'), grab(t('cmp') + 2.0, 'g3.png')
def U(*rs):
    x0 = min(r[0] for r in rs); y0 = min(r[1] for r in rs); x1 = max(r[0] + r[2] for r in rs); y1 = max(r[1] + r[3] for r in rs); return (x0, y0, x1 - x0, y1 - y0)
def hlL(name, items):
    im = Image.new('RGBA', (OW, OH), (0, 0, 0, 0)); bx = []
    for (x, y, w, h), lab in items:
        x0 = OX + x * SC - 5; y0 = max(4, y * SC - 5); x1 = OX + (x + w) * SC + 5; y1 = min(872 * SC + 4, (y + h) * SC + 5); bx.append((x0, y0, x1, y1, lab))
    m = Image.new('RGBA', (OW, BAND_Y), (8, 14, 28, 120)); md = ImageDraw.Draw(m)
    for x0, y0, x1, y1, _ in bx: md.rounded_rectangle([x0, y0, x1, y1], radius=12, fill=(0, 0, 0, 0))
    im.alpha_composite(m); d = ImageDraw.Draw(im); fnt = F(FB, 26)
    for x0, y0, x1, y1, lab in bx:
        d.rounded_rectangle([x0, y0, x1, y1], radius=12, outline=(255, 176, 32, 255), width=5)
        if not lab: continue
        tw = d.textlength(lab, font=fnt); cx, cy = (x0 + 10, y0 + 10) if y1 - y0 > 90 else (x0, y1 + 8)     # 낮은 상자(진행 단계)는 이름표를 아래에
        d.rounded_rectangle([cx, cy, cx + tw + 24, cy + 40], radius=10, fill=(255, 176, 32, 245)); d.text((cx + 12, cy + 3), lab, font=fnt, fill=(17, 26, 43))
    im.save(f'hl_{name}.png'); return f'hl_{name}.png'
r1, r2 = RG['s1'], RG['s2']; rc, rd = RECT['cmp'], RECT['done']
G = [hlL('g0', [(r1['#steps'], '진행 단계')]),
     hlL('g1', [(U(r1['#text'], r1['#sketchBox'], r1['#specs']), '입력 · 설계 사양 표'), (r1['#reqMap'], '요구 → 물리 조건')]),
     hlL('g2', [(r2['#vMain'], '3D 설계안'), (U(r2['#vS0'], r2['#vS1'], r2['#vS2']), '물리 분포'), (U(r2['.cperf .kpis'], r2['#metrics']), '성능 판정'), (r2['#plog'], '계산 기록')]),
     hlL('g3', [(rc['#cmpOv'], '초기 ↔ 최적 비교'), (rd['.cperf'], '성능 · 제작 파일')])]
st_, d = timing('gui'); cut = [0, st_[2] - 0.15, st_[3] - 0.15, d]
open('gui.txt', 'w').write(''.join(f"file '{f}'\nduration {cut[i + 1] - cut[i]:.4f}\n" for i, f in enumerate([g1, g2, g3])) + f"file '{g3}'\n")
hs, d = spans('gui', G)
finish('gui', ['-f', 'concat', '-safe', '0', '-i', 'gui.txt'], 'scale=1600:900', d, hs, bands=bspans('gui')); add_vo('gui')
# ---------- 1 입력
st_, d = timing('A'); src, vf = raw(t('in') + 0.3, t('inend'), d, maxsp=4.5)
hs, d = spans('A', [hl('A1', [r_('in', '#text')]), hl('A2', [r_('in', '#sketchBox')])])
finish('A', src, vf, d, hs, bands=bspans('A')); add_vo('A')
# ---------- 2 설계 사양
st_, d = timing('B'); a_, b_ = t('tap_spec') - 0.9, t('tap_go') + 0.5; src, vf = raw(a_, b_, d)
sp_ = min(2.5, max(0.6, (b_ - a_) / d)); o_ = lambda k: (t(k) - a_) / sp_          # 녹화 시각 → 이 구간 안 시각
bt = hl('Bbtn', [r_('in', '#bSpec')]); rq = hl('B1', [r_('spec', '#reqMap .mr')]); sp2 = hl('B2', [r_('spec', '#specs')]); gb = hl('Bgo', [r_('spec', '#bConfirm'), r_('spec', '#go')])
x1 = max(st_[1] + 1.7, o_('tap_confirm') - 0.7)
hs = [(bt, 0.0, o_('specshow') - 0.5), (rq, o_('specshow') - 0.5, st_[1] - 0.15), (sp2, st_[1] - 0.15, x1), (gb, x1, d)]
finish('B', src, vf, d, hs, bands=bspans('B')); add_vo('B')
# ---------- 3 초기 설계
st_, d = timing('C'); src, vf = raw(t('rsim') - 0.4, t('selstart'), d)
hs, d = spans('C', [hl('C1', [r_('first', '#vS0'), r_('first', '#vS1'), r_('first', '#vS2')]), hl('C2', [r_('first', '.cperf .kpis, #metrics')])])
finish('C', src, vf, d, hs, bands=bspans('C')); add_vo('C')
# ---------- 3 미달 항목 선택 → 최적화 실행 (클릭 장면, 빠르게)
st_, d = timing('Csel')
cuts = [(t(f'tap_sel{k}') - 0.55, t(f'tap_sel{k}') + 0.35) for k in range(4)] + [(t('tap_opt') - 0.6, t('tap_opt') + 0.6)]
ff(*sum([['-ss', f'{a:.2f}', '-t', f'{b - a:.2f}', '-i', 'raw.mp4'] for a, b in cuts], []), '-filter_complex',
   ''.join(f'[{i}:v]setpts=PTS-STARTPTS[c{i}];' for i in range(len(cuts))) + ''.join(f'[c{i}]' for i in range(len(cuts))) + f'concat=n={len(cuts)}:v=1:a=0[o]',
   '-map', '[o]', '-an', *ENC, 'csel_src.mp4')
tot = sum(b - a for a, b in cuts); sp = max(1.0, tot / d)
src, vf = ['-i', 'csel_src.mp4'], f'setpts=PTS/{sp:.4f},tpad=stop_mode=clone:stop_duration=10'
hs, d = spans('Csel', [hl('Cs1', [r_('sel', '#metrics'), r_('sel', '#optimize')])])
finish('Csel', src, vf, d, hs, bands=bspans('Csel')); add_vo('Csel')
# ---------- 4 AI 탐색
ai = [s for s in SEQ if s['stage'] == 'ai']; pk = [s for s in SEQ if s['stage'] == 'pick']; rf = [s for s in SEQ if s['stage'] == 'refine']
fn = lambda s: f"st/{s['n']:04d}.jpg"; V3 = r_('pick', '#vMain')
st_, d = timing('Dai'); src, vf = steps('Dai', [(fn(s), 3.0 if s['it'] <= 40 else 1.0) for s in ai], d)
a1 = hl('Dai1', [V3], dim=False)
hs, d = spans('Dai', [a1, a1, hl('Dai3', [r_('pick', '#metrics')], dim=False)])
finish('Dai', src, vf, d, hs, bands=bspans('Dai')); add_vo('Dai')
# ---------- 4 후보 선택
st_, d = timing('Dpick'); src, vf = steps('Dpick', [(fn(pk[0]), 1.0)], d)
p1 = hl('Dpick1', [r_('pick', '#candP')])
hs, d = spans('Dpick', [p1, p1]); finish('Dpick', src, vf, d, hs, bands=bspans('Dpick')); add_vo('Dpick')
# ---------- 5 정밀 최적화
st_, d = timing('Dref'); src, vf = steps('Dref', [(fn(s), 2.0 if i < 6 else 1.0) for i, s in enumerate(rf[:-1])] + [(fn(rf[-2]), 3.0)], d)
r1 = hl('Dref1', [V3], dim=False)
hs, d = spans('Dref', [r1, r1]); finish('Dref', src, vf, d, hs, bands=bspans('Dref')); add_vo('Dref')
# ---------- 6 검증
st_, d = timing('E'); src, vf = raw(t('done') - 0.2, t('tap_draw') + 1.0, d)
PERF = r_('done', '.cperf')                                  # 오른쪽 성능 패널 전체 (두 구절 내내 같은 상자)
pf = hlL('E1', [(PERF, '')])
hs, d = spans('E', [pf, pf])
finish('E', src, vf, d, hs, bands=bspans('E')); add_vo('E')
# ---------- 제작 파일
im = Image.open(os.path.join(RUN, 'opt_final_drawing.png')).convert('RGB'); im.thumbnail((1580, 890), Image.LANCZOS)
pg_ = Image.new('RGB', (1600, 900), 'white'); ox, oy = (1600 - im.width) // 2, (900 - im.height) // 2; pg_.paste(im, (ox, oy)); pg_.save('dwg.png')
s_ = im.width / 420; P = lambda x, y: (ox + x * s_, oy + (297 - y) * s_)
def mmrect(x0, y0, x1, y1): a = P(x0, y1); b = P(x1, y0); return (a[0], a[1], b[0] - a[0], b[1] - a[1])
st_, d = timing('draw')
hs, d = spans('draw', [hl('dw1', [mmrect(20, 10, 410, 287)], dim=False), hl('dw2', [mmrect(283, 172, 412, 287)])])
finish('draw', ['-loop', '1', '-t', f'{d:.2f}', '-i', 'dwg.png'], 'scale=1600:900', d, hs, bands=bspans('draw')); add_vo('draw')
card(Image.open('../hero/C3/000.png').convert('RGBA'), 'FormProof', ['형상을 성능으로 증명'], [f'5 / 5 기준 충족 · 무게 −{dm:.1f} %', f'흔들림 {sh0:.1f}배 → {sh1:.1f}배']).save('end.png')
_, de = timing('end'); ff('-loop', '1', '-i', 'end.png', '-t', f'{de:.2f}', *ENC, 'seg_end.mp4'); SEG.append(('end', de)); add_vo('end')
open('cat.txt', 'w').write(''.join(f"file 'seg_{n}.mp4'\n" for n, _ in SEG))
ff('-f', 'concat', '-safe', '0', '-i', 'cat.txt', '-c', 'copy', 'v29_자막.mp4')
s0, acc = {}, 0.0
for n, d in SEG: s0[n] = acc; acc += d
items = [(PH[seg][j]['wav'], s0[seg] + st[j]) for seg, st in VO for j in range(len(st))]
a = ['ffmpeg', '-y', '-loglevel', 'error', '-i', 'v29_자막.mp4'] + sum([['-i', w] for w, _ in items], [])
fl = ''.join(f'[{i + 1}:a]aresample=48000,adelay={int(x * 1000)}|{int(x * 1000)},apad[a{i}];' for i, (_, x) in enumerate(items))
fl += ''.join(f'[a{i}]' for i in range(len(items))) + f'amix=inputs={len(items)}:normalize=0,loudnorm=I=-16:TP=-1.5,atrim=0:{acc:.2f}[o]'
subprocess.run(a + ['-filter_complex', fl, '-map', '0:v', '-map', '[o]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ac', '2', '-shortest', 'v29_음성.mp4'], check=True)
json.dump(dict(seg={n: round(d, 2) for n, d in SEG}, start={k: round(v, 2) for k, v in s0.items()}, vo=[(w, round(x, 2)) for w, x in items], total=round(acc, 2)),
          open('timeline.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(dict(total=round(acc, 1), seg={n: round(d, 1) for n, d in SEG}), ensure_ascii=False))
