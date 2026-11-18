"""v18 카드: 화면 흐름(flow.mp4, 6초) · 결과(card_out.mp4, 7초) — '초기 설계' 표기, 값은 이번 녹화의 GUI 값(marks.json rows)."""
import json, os, sys, subprocess, asyncio, base64
M = json.load(open('marks.json')); o = -0.7
def ff(*a): subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *a], check=True)
# 흐름 카드 썸네일: 녹화 화면에서
shots = []
for i, (k, dt) in enumerate((('spectable', 2.0), ('STEP', 0), ('cmp', 2.5))):
    if k == 'STEP': ff('-i', 'st/0110.jpg', '-vf', 'scale=800:-1', f'th{i}.png')
    else: ff('-ss', f'{M[k] - o + dt:.2f}', '-i', 'raw.mp4', '-frames:v', '1', '-vf', 'scale=800:-1', f'th{i}.png')
    shots.append('data:image/png;base64,' + base64.b64encode(open(f'th{i}.png', 'rb').read()).decode())
R = {r['k']: r for r in M['rows']}
def num(v, d=1):
    return f'{v:.{d}f}'
rows = [('목표 충족', '1 / 5', M['resbar'].split('\n')[0].strip())]
mass0, mass1 = 94.9, float(M['mass_final'])
rows.append(('무게 (해석 격자 기준)', f'{mass0} g', f'{mass1:.1f} g'))
for k, name, unit, d in (('shake', '흔들림 (길 진동)', '배', 2), ('f1', '떨림 주파수', 'Hz', 1), ('Tmax', '폰 온도 상승', '°C', 2), ('touch', '화면 누를 때 휨', 'mm', 3)):
    r = R[k]; rows.append((name, f"{num(r['v0'], d)} {unit}".replace(' 배', '배'), f"{num(r['v'], d)} {unit}".replace(' 배', '배')))
CSS = """<style>body{margin:0;width:1600px;height:1010px;background:#111a2b;font-family:"Noto Sans CJK KR",sans-serif;color:#fff;overflow:hidden}
.w{padding:96px 150px}.k{color:#8fb3ff;font-size:20px;font-weight:700}.h{font-size:52px;font-weight:800;margin:10px 0 34px}
table{border-collapse:collapse;width:1300px;font-size:30px}td{padding:16px 10px;border-bottom:1px solid #26324a}td.a{color:#9aa6bd;text-align:right;width:230px}td.r{color:#9aa6bd;width:80px;text-align:center}
td.b{color:#5fd3a6;font-weight:800;text-align:right;width:230px}.f{margin-top:30px;color:#ffd166;font-size:24px}
.fl{padding:70px 70px 0}.fl h1{font-size:40px;margin:0}.fl p{color:#9aa6bd;font-size:22px;margin:8px 0 40px}.row{display:flex;align-items:flex-start;gap:26px}
.c{width:450px}.c img{width:450px;border:3px solid #ffb020;border-radius:12px;display:block}.ar{color:#ffb020;font-size:44px;margin-top:100px}
.c b{display:flex;align-items:center;gap:12px;font-size:26px;margin:18px 0 8px}.c b i{font-style:normal;background:#2563eb;border-radius:999px;padding:2px 14px;font-size:20px}
.c span{display:block;color:#9aa6bd;font-size:19px;line-height:1.55}</style>"""
out_html = CSS + f"""<div class="w"><div class="k">결과 · 같은 조건 정밀 시뮬레이션</div><div class="h">초기 설계 → 최적 설계</div><table>
{''.join(f'<tr><td>{a}</td><td class="a">{b}</td><td class="r">→</td><td class="b">{c}</td></tr>' for a, b, c in rows)}</table>
<div class="f">AI가 형상 300회 탐색, 정밀 계산은 후보 31개만 · A3 제작 도면 · 3D 프린트 파일 자동 출력</div></div>"""
flow_html = CSS + f"""<div class="fl"><h1>화면 흐름</h1><p>단계가 진행되면 화면 배치가 바뀝니다 — 지금 단계에 필요한 것만 크게</p><div class="row">
<div class="c"><img src="{shots[0]}"><b><i>①②</i>입력 · 설계 사양</b><span>왼쪽: 입력과 설계 사양 표<br>오른쪽: AI가 읽은 요구 → 물리 조건</span></div><div class="ar">▶</div>
<div class="c"><img src="{shots[1]}"><b><i>③④</i>초기 설계 · 물리 최적화</b><span>입력 패널은 왼쪽 막대로 접힘<br>3D 설계안 · 물리 분포 · 성능 판정</span></div><div class="ar">▶</div>
<div class="c"><img src="{shots[2]}"><b><i>⑤</i>결과 · 제작 파일</b><span>초기 ↔ 최적 비교 (같은 색 척도)<br>결과 띠 · 계산 기록 · 도면</span></div></div></div>"""
async def shoot():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1600, 'height': 1010})
        for name, h in (('card_out', out_html), ('flow_bg', flow_html)):
            await pg.set_content('<meta charset="utf-8">' + h); await pg.wait_for_timeout(300); await pg.screenshot(path=name + '.png')
        from urllib.parse import quote
        await pg.set_viewport_size({'width': 1600, 'height': 110})
        await pg.goto('file://' + os.path.abspath('nar.html') + '?i=' + quote('★') + '&a=' + quote('화면 흐름') + '&n=' + quote('단계가 진행되면 화면이 입력 → 설계 · 최적화 → 결과 순으로 바뀝니다'))
        await pg.wait_for_timeout(200); await pg.screenshot(path='flow_band.png'); await b.close()
asyncio.run(shoot())
ff('-loop', '1', '-i', 'flow_bg.png', '-i', 'flow_band.png', '-filter_complex', '[0:v][1:v]overlay=0:900', '-t', '6', '-r', '30', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', 'flow.mp4')
ff('-loop', '1', '-i', 'card_out.png', '-t', '7', '-r', '30', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', 'card_out.mp4')
print('cards ok', rows)
