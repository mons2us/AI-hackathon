"""개선 실험 결과 비교 · 최선 선택 (11-16 추가, step4_improve.sh 마지막 단계)

판정 규칙 (사람이 바꾸지 않는 한 이 순서):
  1) 조합(형상 AI × 물리 AI)마다 후보를 FEM 으로 다시 계산한 값(frfint_*.json)으로 판정 — AI 예측값은 판정에 안 씀
     통과 = f1 ≥ f1_min · 폰 온도 ≤ 한도 · 터치 ≤ 한도 · 충격 응력 ≤ 한도 · 층간 ≤ 한도 (spec/bike_mount_targets.json)
  2) 통과 후보가 있는 조합 중 **가장 가벼운 통과 후보**를 가진 조합이 1등
  3) 무게가 0.5 g 이내로 같으면 공통 시험 셋 f1 오차(기준 근처 80–120 Hz)가 작은 쪽
  통과 후보가 하나도 없으면 "선택 없음" — 기준을 낮추지 않음.
출력: <out>/report.md, <out>/choice.json, <best>/ (고른 조합의 sdf.pt · 물리 AI · 후보 · FEM 결과 복사)
"""
import argparse, glob, json, os, shutil

p = argparse.ArgumentParser()
p.add_argument('--spec', required=True); p.add_argument('--eval', required=True); p.add_argument('--out', required=True); p.add_argument('--best', required=True)
p.add_argument('--combo', action='append', default=[], help='이름|sdf.pt|물리AI.pt|물리AI 채점 이름|후보 폴더(cand_*.npy)|FEM 결과 폴더(frfint_*.json)')
a = p.parse_args()
tg = json.load(open(a.spec)); ev = {r['name']: r for r in json.load(open(a.eval))} if os.path.exists(a.eval) else {}

def judge(d):
    f1 = d['f'][0]; T = d['Tmax']; tc = max(d['touch_mm']); sh = max(d['shock'][k]['vm999'] for k in ('vert', 'fore'))
    il = max(d['shock'][k]['interlayer999'] for k in ('vert', 'fore')); shake = max(d['vert']['peak'], d['fore']['peak'])
    chk = dict(f1=f1 >= tg['f1_min_hz'], T=T <= tg['phone_Tmax_rise_max_c'], touch=tc <= tg['touch_max_mm'], shock=sh <= tg['shock_vm_max_mpa'],
               interlayer=il <= tg.get('shock_interlayer_max_mpa', 1e9))
    return dict(mass_g=d['mass_g'], f1=f1, Tmax=T, touch=tc, shock=sh, interlayer=il, shake=shake, ok=all(chk.values()), fail=[k for k, v in chk.items() if not v])

rows = []
for c in a.combo:
    name, sdf, phys, ename, ldir, gdir = c.split('|')
    cands = []
    for f in sorted(glob.glob(os.path.join(gdir, 'frfint_*.json'))):
        try: cands.append(dict(file=f, **judge(json.load(open(f)))))
        except Exception as e: cands.append(dict(file=f, ok=False, fail=[f'읽기 실패 {e}']))
    ok = [x for x in cands if x['ok']]; best = min(ok, key=lambda x: x['mass_g']) if ok else None
    e = ev.get(ename, {})
    rows.append(dict(name=name, sdf=sdf, phys=phys, ldir=ldir, n=len(cands), n_ok=len(ok), best=best, f1_err=e.get('mean_f1_hz'), f1_band=e.get('f1_band_mean'),
                     T_err=e.get('mean_phone_Tmax_rise_c'), fT=e.get('field_L2_T'), cands=cands))
win = [r for r in rows if r['best']]
win.sort(key=lambda r: (round(r['best']['mass_g'] / 0.5), r['f1_band'] if r['f1_band'] is not None else 9))
choice = win[0] if win else None
pct = lambda v: '-' if v is None else f'{100 * v:.1f}%'
L = ['# 개선 실험 비교 (FEM 재계산으로 판정)', '',
     f"기준: f1 ≥ {tg['f1_min_hz']} Hz · 폰 온도 ≤ {tg['phone_Tmax_rise_max_c']} °C · 터치 ≤ {tg['touch_max_mm']} mm · 충격 ≤ {tg['shock_vm_max_mpa']} MPa · 층간 ≤ {tg.get('shock_interlayer_max_mpa', '-')} MPa", '',
     '## 물리 AI 채점 (같은 시험 셋, 학습에 안 쓴 형상)', '', '| 모델 | 종류 | 학습 수 | f1 오차 평균 | f1 오차 (80–120 Hz) | f1 ±5% 이내 | 폰 온도 오차 | 온도 분포 L2 | 응력 분포 L2(log) |', '|---|---|---|---|---|---|---|---|---|']
for r in ev.values():
    L.append(f"| {r['name']} | {r['kind']} | {r.get('n_train') or '-'} | {pct(r['mean_f1_hz'])} | {pct(r.get('f1_band_mean'))} | {pct(r['f1_within5pct'])} | {pct(r['mean_phone_Tmax_rise_c'])} | {pct(r.get('field_L2_T'))} | {pct(r.get('field_L2_vm_log'))} |")
L += ['', '## 조합별 최적화 → FEM 검증', '', '| 조합 | 후보 | FEM 통과 | 가장 가벼운 통과 | f1 | 폰 온도 | 터치 | 충격 | 층간 | 흔들림 최대 |', '|---|---|---|---|---|---|---|---|---|---|']
for r in rows:
    b = r['best']
    if b: L.append(f"| {'**' if r is choice else ''}{r['name']}{'** ← 선택' if r is choice else ''} | {r['n']} | {r['n_ok']} | {b['mass_g']:.1f} g | {b['f1']:.1f} Hz | {b['Tmax']:.1f} °C | {b['touch']:.3f} mm | {b['shock']:.1f} MPa | {b['interlayer']:.1f} MPa | {b['shake']:.2f}배 |")
    else:
        fails = sorted({f for x in r['cands'] for f in x.get('fail', [])}); L.append(f"| {r['name']} | {r['n']} | 0 | 통과 없음 (미달: {', '.join(fails) or '-'}) | | | | | | |")
L += ['', '## 선택', '']
if choice:
    L.append(f"**{choice['name']}** — FEM 통과 후보 중 가장 가벼운 {choice['best']['mass_g']:.1f} g (`{choice['best']['file']}`)")
else:
    L.append('**선택 없음** — 어느 조합도 FEM 검증을 통과한 후보가 없음. 기준은 낮추지 않음. 데이터 · 학습을 더 늘리거나 위상 최적화(START_RHO)로 정밀화')
L += ['', '판정 규칙: FEM 통과 → 가장 가벼움 → (0.5 g 이내 같으면) 기준 근처 f1 오차 작은 쪽. AI 예측값은 판정에 쓰지 않음.']
os.makedirs(a.out, exist_ok=True); open(os.path.join(a.out, 'report.md'), 'w', encoding='utf-8').write('\n'.join(L)); print('\n'.join(L))
json.dump(dict(choice=choice and {k: v for k, v in choice.items() if k != 'cands'}, rows=rows), open(os.path.join(a.out, 'choice.json'), 'w'), indent=1, ensure_ascii=False)
if choice:
    os.makedirs(a.best, exist_ok=True); bf = choice['best']['file']; tag = os.path.basename(bf)[len('frfint_'):-len('.json')]
    for src, dst in ((choice['sdf'], 'sdf.pt'), (choice['phys'], 'phys.pt'), (bf, 'fem_best.json')):
        shutil.copy(src, os.path.join(a.best, dst))
    cf = os.path.join(choice['ldir'], tag + '.npy')
    if os.path.exists(cf): shutil.copy(cf, os.path.join(a.best, 'cand_best.npy'))
    json.dump(dict(choice=choice['name'], mass_g=choice['best']['mass_g'], sdf=choice['sdf'], phys=choice['phys'], fem=bf), open(os.path.join(a.best, 'choice.json'), 'w'), indent=1, ensure_ascii=False)
    print('최선 →', a.best)
