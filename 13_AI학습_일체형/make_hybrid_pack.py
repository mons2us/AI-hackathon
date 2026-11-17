"""GUI 용 '하이브리드 최적화 경로' 묶음 만들기 → 10_입력_1차설계/models/hybrid_p01.json.gz

경로 = ① AI 탐색 (GUI TorchBackend.trace 그대로 — 형상 AI sdf.pt × 물리 AI fno.pt(능동 학습 2회 후), 300회)
      → 후보 선택 (탐색 형상 31개를 정밀 계산(FEM)한 결과 중 진동수 · 휨 · 충격 기준을 통과한 가장 가벼운 형상, it=120)
      → ② 정밀 최적화 (그 후보에서 출발한 구조 최적화 + FEM: 진동수 목표 95 Hz 60회 → 150 Hz 40회 — 흔들림 대응)
      → 최종 형상 (rprint_hyb2) — GUI 의 검증 관문(gate)이 FEM 으로 다시 판정.
AI 탐색 프레임은 GUI 코드(run)로 다시 만들고, 후보(it=120) 형상이 능동 학습 3회차 기록(al3_120)과 같은지 해시로 확인한다.
사용: python3 make_hybrid_pack.py <hybrid 결과 폴더(runs/hybrid)>"""
import sys, os, json, gzip, re, base64, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(H)
sys.path.insert(0, os.path.join(ROOT, '10_입력_1차설계'))
from formproof_input import integral as I
from formproof_input import inverse as V
HY = sys.argv[1] if len(sys.argv) > 1 else os.path.join(H, 'runs', 'hybrid')
AI_ITERS, PICK_IT = 300, 120
SEL = sorted(V.DEFAULT_SELECTIONS[0])
LIM21 = {'Tmax': ('<=', 21.0)}                       # 능동 학습 당시 기준 (폰 온도 상승 21 °C) — 발표 자료와 같음

# ① AI 탐색 — GUI run() 그대로 (결과 DB 캐시는 쓰지 않음)
res = V.run(SEL, use_cache=False, iters=AI_ITERS, lim_override=LIM21)
ai = res['frames']
d = np.load(os.path.join(H, 'data/al/r3_src.npz')); names = [str(n) for n in d['names']]
R = np.unpackbits(d['r'], axis=1)[:, :int(d['ne'])].astype(bool)
want = V._sha(R[names.index(f'al3_{PICK_IT:03d}')])
got = next(f['sha'] for f in ai if f['it'] == PICK_IT)
print(json.dumps(dict(ai_frames=len(ai), backend=res['backend'], pick_sha_match=(want == got))), flush=True)
assert want == got, '후보 형상이 능동 학습 기록과 다름 (모델 · z0 · 기준 확인)'
fem = {c['name']: c for c in json.load(open(os.path.join(H, 'data/al/r3_pred_vs_fem.json')))}
c = fem[f'al3_{PICK_IT:03d}']
checked = [dict(it=int(n[4:]), f1=v['fem_f1'], Tmax=v['fem_T'], touch=v['fem_touch'], stress=v['fem_stress'])
           for n, v in fem.items()]
pas = [x for x in checked if x['f1'] >= 95 and x['touch'] <= 0.3 and x['stress'] <= 10.9]

# ② 정밀 최적화 — 엔진 기록(반복마다 FEM 값) + 4회마다 저장한 형상
def log(fn):
    return [json.loads(l) for l in open(os.path.join(HY, fn)) if l.startswith('{"it"')]
refine, k = [], 0
for tag, fn, note in (('hyb', 'opt.log', '구조 최적화 + 정밀 계산 · 진동수 목표 95 Hz'), ('hyb2', 'opt2.log', '흔들림 대응 · 진동수 목표 150 Hz')):
    L = {r['it']: r for r in log(fn)}
    snaps = sorted(f for f in os.listdir(HY) if re.fullmatch(rf'snap_{tag}_\d+\.npy', f))
    for f in snaps:
        it = int(f.split('_')[-1][:3]); r = L[it]; full = np.load(os.path.join(HY, f)).ravel() > 0.5
        k += 1
        refine.append(dict(stage='refine', note=note, rit=k, mass_g=round(float(r['mass_g']), 2),
                           fem=dict(f1=round(float(r['f'][0]), 1), Tmax=round(float(r['Tmax']), 2), touch=round(float(max(r['touch'])), 3)),
                           mesh=V.mesh_payload(V.attached(full))))
final = np.load(os.path.join(HY, 'rprint_hyb2.npy')).ravel() > 0.5
N = AI_ITERS + 6 * len(refine) + 6                       # 화면 x 축: AI 300회 + 후보 선택 + 정밀 최적화 (프레임당 6칸)
for f in ai:
    f['iters'] = N; f['stage'] = 'ai'
pick = dict(ai[[f['it'] for f in ai].index(PICK_IT)])
pick.update(stage='pick', it=AI_ITERS + 6, iters=N, heat=None,
            note=f'AI 후보 {len(checked)}개 정밀 계산 → 기준 통과 {len(pas)}개 중 가장 가벼운 형상 (탐색 {PICK_IT}회째)',
            fem=dict(f1=c['fem_f1'], Tmax=c['fem_T'], touch=c['fem_touch'], stress=c['fem_stress']))
for j, f in enumerate(refine):
    f.update(it=AI_ITERS + 6 * (j + 2), iters=N, pen=0.0, pred={}, heat=None, sha=None)
pack = dict(version=1, backend=res['backend'], selection=SEL, ai_iters=AI_ITERS, pick_it=PICK_IT, limits_used=res['limits'],
            frames=ai + [pick] + refine, final_rho=base64.b64encode(np.packbits(final)).decode(), final_sha=V._sha(final),
            candidates=dict(checked=len(checked), passed=len(pas)), fit=res['fit'],
            source=dict(ai='13_AI학습_일체형 능동 학습 3회차 탐색 (al3)', refine='13_AI학습_일체형/run_hybrid.sh + FT=150 40회',
                        final_fem='runs/hybrid/frfint_hyb2.json'))
out = os.path.join(ROOT, '10_입력_1차설계', 'models', 'hybrid_p01.json.gz')
with gzip.open(out, 'wt', encoding='utf-8') as fh:
    json.dump(pack, fh, ensure_ascii=False)
print(json.dumps(dict(saved=out, frames=len(pack['frames']), refine=len(refine), size_kb=os.path.getsize(out) // 1024)))
