"""하이브리드 경로 묶음 v3 — 결선 데모용. 기존 묶음(v2)은 그대로 두고 models/hybrid_p01_v3.json.gz 를 새로 만든다.

경로 = ① AI 탐색 (v2 묶음의 AI 프레임 그대로: 형상 AI × 물리 AI, 300회, 2회마다)
      → 후보 선택: 탐색 형상 31개(10회마다) FEM 결과 중 기준 통과(진동수 ≥ 95 Hz · 휨 ≤ 0.3 mm · 충격 ≤ 10.9 MPa) 형상에서
        진동수가 가장 높은(흔들림 여유가 가장 큰) 형상 = al3_020 (탐색 20회째, FEM 171.2 Hz)
      → ② 정밀 최적화: 그 후보에서 출발한 구조 최적화 + FEM 120회, 발표 최종 형상(int35f95g2)과 같은 조건
        (GRIP=2 NX=88 MSYS=0.311 AM=1 RF=8 ETAE=0.7 TILT=35 FT=95 TLIM=21 DLIM=0.3, β 1→32)
        기록: runs/ppt_from_al3_020/opt.log · snap_pal_XXX.npy(4회마다) · rprint_pal.npy · frfint_pal.json
화면 무게 = 반복 기록(opt.log)의 무게(최종 FEM 판정 무게와 같은 계산). 단 β=1 구간(0–16회: 후보 경계를 밀도로 풀어 다시 배치하는 중,
밀도가 회색이라 무게가 제품 무게가 아님)은 무게를 비우고 '밀도 정리 중'으로 표시. 정밀 계산 값 = 반복 기록의 FEM 값.
사용: python3 make_hybrid_pack_v3.py"""
import sys, os, json, gzip, re, base64, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(H)
sys.path.insert(0, os.path.join(ROOT, '10_입력_1차설계'))
from formproof_input import inverse as V
RUN = os.path.join(H, 'runs', 'ppt_from_al3_020'); TAG = 'pal'; PICK = 'al3_020'
CELL_G = 0.02032
src = os.path.join(ROOT, '10_입력_1차설계', 'models', 'hybrid_p01_e2.json.gz')
old = json.load(gzip.open(src, 'rt', encoding='utf-8'))
ai = [f for f in old['frames'] if f.get('stage') == 'ai']
AI_ITERS = old['ai_iters']; STEP = 6

# 후보 31개 (AI 예측 · FEM)
d = np.load(os.path.join(H, 'data/al/r3_src.npz')); names = [str(n) for n in d['names']]
R = np.unpackbits(d['r'], axis=1)[:, :int(d['ne'])].astype(bool)
fem = {c['name']: c for c in json.load(open(os.path.join(H, 'data/al/r3_pred_vs_fem.json')))}
pred = {p['it']: p for p in json.load(open(os.path.join(H, 'data/al/r3_pred.json')))}
ok = lambda c: c['fem_f1'] >= 95 and c['fem_touch'] <= 0.3 and c['fem_stress'] <= 10.9
cands = []
for n in sorted(fem, key=lambda s: int(s[4:])):
    c = fem[n]; it = int(n[4:])
    cands.append(dict(it=it, mass=round(float(R[names.index(n)].sum()) * CELL_G, 1), f1=round(c['fem_f1'], 1),
                      f1p=round(float(pred[it]['f1']), 1) if it in pred else None, ok=bool(ok(c)), pick=False))
best = max((c for c in cands if c['ok']), key=lambda c: c['f1']); best['pick'] = True
assert f"al3_{best['it']:03d}" == PICK, best
pk_it = best['it']
src_ai = next(f for f in ai if f['it'] == pk_it)
assert src_ai['sha'] == V._sha(R[names.index(PICK)]), '후보 형상 해시 다름'
c = fem[PICK]
pick = dict(src_ai, stage='pick', it=AI_ITERS + STEP, heat=None, cands=cands,
            cand_lim=dict(text='진동수 ≥ 95 Hz · 휨 ≤ 0.3 mm · 충격 ≤ 10.9 MPa'), cand_rule='흔들림 여유(진동수)가 가장 큰',
            note=f"AI 후보 {len(cands)}개 정밀 계산 → 기준 통과 {sum(x['ok'] for x in cands)}개 중 진동수 여유가 가장 큰 형상 (탐색 {pk_it}회째)",
            fem=dict(f1=c['fem_f1'], Tmax=c['fem_T'], touch=c['fem_touch'], stress=c['fem_stress']))

# 정밀 최적화 프레임
L = {r['it']: r for r in (json.loads(l) for l in open(os.path.join(RUN, 'opt.log')) if l.startswith('{"it"'))}
snaps = sorted(f for f in os.listdir(RUN) if re.fullmatch(rf'snap_{TAG}_\d+\.npy', f))
refine = []
for k, fn in enumerate(snaps):
    it = int(fn.split('_')[-1][:3]); r = L[it]
    full = np.load(os.path.join(RUN, fn)).ravel() > 0.5
    shown = V.attached(full)
    gray = r['beta'] == 1
    refine.append(dict(stage='refine', note=('후보 경계를 밀도로 풀어 재료를 다시 배치하는 중 (정밀 계산)' if gray else
                                             '후보에서 출발한 구조 최적화 + 정밀 시뮬레이션 · 3D 프린트 출력 조건(45°) 반영'),
                       rit=k + 1, oit=it, mass_g=None if gray else round(float(r['mass_g']), 2),
                       fem=dict(f1=round(float(r['f'][0]), 1), Tmax=round(float(r['Tmax']), 2), touch=round(float(max(r['touch'])), 3)),
                       mesh=V.mesh_payload(shown), it=AI_ITERS + STEP * (k + 2), pen=0.0, pred={}, heat=None, sha=None))
final = np.load(os.path.join(RUN, f'rprint_{TAG}.npy')).ravel() > 0.5
N = AI_ITERS + STEP * (len(refine) + 1) + STEP
for f in ai + [pick] + refine:
    f['iters'] = N
ev = json.load(open(os.path.join(RUN, f'frfint_{TAG}.json')))
pack = dict(old, version=3, pick_it=pk_it, frames=ai + [pick] + refine, refine_step=STEP,
            final_rho=base64.b64encode(np.packbits(final)).decode(), final_sha=V._sha(final),
            candidates=dict(checked=len(cands), passed=sum(x['ok'] for x in cands)),
            source=dict(ai='13_AI학습_일체형 능동 학습 3회차 탐색 (al3)', pick=f'{PICK} (기준 통과 중 진동수 최대)',
                        refine='13_AI학습_일체형/runs/ppt_from_al3_020 (발표 최종 형상 int35f95g2 와 같은 조건, 120회)',
                        final_fem=dict(mass_g=ev['mass_g'], f1=ev['f'][0], Tmax=ev['Tmax'], touch=ev['touch_mm'],
                                       shake=max(ev['fore']['peak'], ev['vert']['peak']))))
out = os.path.join(ROOT, '10_입력_1차설계', 'models', 'hybrid_p01_v4.json.gz')   # v4: 화면 문구에서 FEM 표기 제거 (경로 · 수치는 v3 와 같음)
with gzip.open(out, 'wt', encoding='utf-8') as fh:
    json.dump(pack, fh, ensure_ascii=False)
print(json.dumps(dict(saved=out, ai=len(ai), refine=len(refine), pick=pk_it, refine_mass=[f['mass_g'] for f in refine],
                      size_kb=os.path.getsize(out) // 1024), ensure_ascii=False))
