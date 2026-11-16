"""결과 요약 (데이터 · 학습 · 최적화 · FEM 검증) → runs/report.md, runs/report.html

python3 scripts/report_frame.py [패키지 폴더]     (기본: 이 파일의 상위 폴더)
서버 단계 끝(step2)과 회사 PC 보기(step3)에서 같은 스크립트를 씀. 있는 것만 요약하고 없는 것은 '없음'으로 표시.
"""
import glob, html, json, os, sys
import numpy as np

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(ROOT, 'runs')
os.makedirs(R, exist_ok=True)
TG = json.load(open(os.path.join(ROOT, 'spec', 'bike_mount_targets.json'), encoding='utf-8'))
FT, TL, DL, SL, IL = TG['f1_min_hz'], TG['phone_Tmax_rise_max_c'], TG['touch_max_mm'], TG['shock_vm_max_mpa'], TG['shock_interlayer_max_mpa']
FAM_KO = {'straight': '곧은 팔', 'truss': '트러스', 'vee': 'V자', 'arch': '아치', 'spine': '척추', 'yfork': 'Y자', 'plate': '판형'}
out = []
w = out.append


def table(head, rows):
    w('| ' + ' | '.join(head) + ' |')
    w('|' + '---|' * len(head))
    for r in rows:
        w('| ' + ' | '.join(str(x) for x in r) + ' |')
    w('')


def rng_(v):
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    return f'{v.min():.3g} – {np.median(v):.3g} – {v.max():.3g}' if len(v) else '-'


w('# FormProof 11 · 프레임 생성기 → FEM → 물리 AI → 최적화 결과 요약')
w('')
w(f'기준 (spec/bike_mount_targets.json): f1 ≥ {FT} Hz · 폰 온도 상승 ≤ {TL} °C · 터치 ≤ {DL} mm · 충격 응력 ≤ {SL} MPa · 층간 ≤ {IL} MPa')
w('')
# ---------------------------------------------------------------- 데이터
w('## 1. 학습 데이터')
A = sorted(glob.glob(os.path.join(ROOT, 'data', 'shards_frame', '*.npz')))
B = sorted(glob.glob(os.path.join(ROOT, 'data', 'shards_thermal', '*.npz')))
if A:
    lab, ext, prm, names = [], [], [], []
    for f in A:
        d = np.load(f, allow_pickle=True)
        if len(d['occ']) == 0:
            continue
        lab.append(d['lab']); ext.append(d['lab_ext']); names += list(d['names']); prm += [json.loads(p) if p else {} for p in d['prm']]
    lab, ext = np.concatenate(lab), np.concatenate(ext)
    en = list(np.load(A[0], allow_pickle=True)['ext_names'])
    gen = np.array([n.startswith('frame_') for n in names])
    ok = (lab[:, 1] >= FT) & (lab[:, 3] <= TL) & (lab[:, 4] <= DL) & (lab[:, 6] <= SL) & (ext[:, en.index('interlayer999_vert_mpa')] <= IL)
    w(f'A 구조 + 열: **{len(lab)}개** (프레임 생성기 {gen.sum()} · 위상 최적화 기록 {(~gen).sum()}), 샤드 {len(A)}개. 모든 기준 통과 {ok.sum()}개 ({ok.mean() * 100:.1f}%)')
    w('')
    table(['값', '최소 – 중앙 – 최대'], [['전체 질량 g', rng_(lab[:, 0])], ['f1 Hz', rng_(lab[:, 1])], ['폰 온도 상승 °C', rng_(lab[:, 3])],
                                      ['터치 위 mm', rng_(lab[:, 4])], ['충격 응력 MPa', rng_(lab[:, 6])],
                                      ['흔들림 대역 최대(위아래)', rng_(ext[:, en.index('band_vert')])],
                                      ['층간 응력(위아래) MPa', rng_(ext[:, en.index('interlayer999_vert_mpa')])]])
    rows = []
    for fam, ko in FAM_KO.items():
        m = np.array([p.get('family') == fam for p in prm])
        if m.any():
            rows.append([ko, m.sum(), rng_(lab[m, 1]), f'{(lab[m, 1] >= FT).mean() * 100:.0f}%', f'{ok[m].mean() * 100:.0f}%', rng_(lab[m, 0])])
    if rows:
        w('계열별 (프레임 생성기)')
        w('')
        table(['계열', '개수', 'f1 Hz', 'f1 ≥ 기준', '모든 기준', '질량 g'], rows)
else:
    w('A: 없음 (data/shards_frame)')
    w('')
if B:
    Y = np.concatenate([np.load(f)['Tmax'] for f in B])
    w(f'B 열 전용: 받침판 패턴 **{len(Y)}개**, 폰 온도 상승 {rng_(Y)} °C, 기준({TL} °C) 이하 {(Y <= TL).mean() * 100:.0f}%')
else:
    w('B: 없음 (data/shards_thermal)')
w('')
# ---------------------------------------------------------------- 학습
w('## 2. 학습')
sf = os.path.join(R, 'sdf_fit.json')
if os.path.exists(sf):
    j = json.load(open(sf))
    w(f'- 형상 AI(DeepSDF) 기준 구조 복원 IoU **{j["IoU"]:.3f}** (통과 기준 0.8 → {"통과" if j["pass"] else "미달"}). '
      f'주의: 기준 구조는 위상 최적화 기록의 마지막 형상이라 학습에 포함되어 있음 — 처음 보는 형상 복원 시험이 아님')
else:
    w('- 형상 AI: 결과 없음 (runs/sdf_fit.json)')
for m in ('cnn', 'fno'):
    f = os.path.join(R, f'{m}.json')
    if os.path.exists(f):
        fin = json.load(open(f))['final']
        items = [(k.replace('relerr_', ''), v) for k, v in fin.items() if k.startswith('relerr_')]
        w(f'- 물리 AI {m.upper()} 시험 셋(15%) 상대 오차: ' + ', '.join(f'{k} {v * 100:.1f}%' for k, v in items)
          + (f', 분포 상대 L2 온도 {fin["field_relL2_T"]:.3f} · 응력 {fin["field_relL2_vm"]:.3f}' if 'field_relL2_T' in fin else ''))
    else:
        w(f'- 물리 AI {m.upper()}: 결과 없음')
w('')
# ---------------------------------------------------------------- 최적화 + 검증
w('## 3. 최적화 후보와 FEM 검증 관문')
ls = os.path.join(R, 'latent', 'latent_search.json')
if os.path.exists(ls):
    rows = []
    for c in json.load(open(ls)):
        t = os.path.splitext(os.path.basename(c['cand']))[0]
        g = os.path.join(R, 'gate', f'frfint_{t}.json')
        p = c['pred']
        if os.path.exists(g):
            e = json.load(open(g))
            f1 = e['f'][0]; tm = e['Tmax']; tc = max(e['touch_mm'][:2]); sv = e['shock']['vert']['vm999']; il = e['shock']['vert']['interlayer999']
            ok = f1 >= FT and tm <= TL and tc <= DL and sv <= SL and il <= IL
            rows.append([t, c['start'], f'{p["mass_g"]:.1f} / {e["mass_g"]:.1f}', f'{p["f1_hz"]:.1f} / {f1:.1f}', f'{p["Tmax"]:.2f} / {tm:.2f}',
                         f'{p["touch_top"]:.3f} / {tc:.3f}', f'{p["shock_vm"]:.1f} / {sv:.1f}', f'{il:.1f}', '✅' if ok else '❌'])
        else:
            rows.append([t, c['start'], f'{p["mass_g"]:.1f} / -', f'{p["f1_hz"]:.1f} / -', f'{p["Tmax"]:.2f} / -', f'{p["touch_top"]:.3f} / -',
                         f'{p["shock_vm"]:.1f} / -', '-', 'FEM 안 함'])
    w('값 = 물리 AI 예측 / FEM 재계산')
    w('')
    table(['후보', '시작 형상', '질량 g', 'f1 Hz', '폰 온도 °C', '터치 mm', '충격 MPa', '층간 MPa', '판정'], rows)
else:
    w('최적화 결과 없음 (runs/latent/latent_search.json)')
w('')
w('## 4. 아직 없는 것 (다음 작업)')
w('- 열 전용 데이터(B)로 학습하는 열 모델, 물리 손실(PINO), lab_ext(흔들림 · 층간) 학습')
w('- 형상 생성기 변수 + 물리 AI 최적화, 형상 AI + 물리 AI 와의 비교')
md = '\n'.join(out)
open(os.path.join(R, 'report.md'), 'w', encoding='utf-8').write(md)


def to_html(md):
    body, intab = [], False
    for line in md.split('\n'):
        if line.startswith('|'):
            cells = [html.escape(c.strip()) for c in line.strip('|').split('|')]
            if set(''.join(cells)) <= set('-'):
                continue
            if not intab:
                body.append('<table>'); intab = True; tag = 'th'
            else:
                tag = 'td'
            body.append('<tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in cells) + '</tr>')
            continue
        if intab:
            body.append('</table>'); intab = False
        t = html.escape(line).replace('**', '')
        if line.startswith('# '):
            body.append(f'<h1>{t[2:]}</h1>')
        elif line.startswith('## '):
            body.append(f'<h2>{t[3:]}</h2>')
        elif line.startswith('- '):
            body.append(f'<li>{t[2:]}</li>')
        elif t:
            body.append(f'<p>{t}</p>')
    if intab:
        body.append('</table>')
    css = ('body{font-family:"Malgun Gothic","Apple SD Gothic Neo",sans-serif;max-width:1100px;margin:24px auto;padding:0 16px;color:#111827}'
           'table{border-collapse:collapse;margin:8px 0 16px}td,th{border:1px solid #e3e7ee;padding:5px 9px;font-size:13px}th{background:#f4f6f9}'
           'h2{border-bottom:2px solid #e3e7ee;padding-bottom:4px;margin-top:28px}li{margin:4px 0}')
    return f'<!doctype html><html lang="ko"><meta charset="utf-8"><title>FormProof 11 결과</title><style>{css}</style><body>' + '\n'.join(body) + '</body></html>'


open(os.path.join(R, 'report.html'), 'w', encoding='utf-8').write(to_html(md))
print(md)
