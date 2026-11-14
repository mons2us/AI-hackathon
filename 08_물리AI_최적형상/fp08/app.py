"""통합 시연 화면 — 10(입력·1차 설계) → 08(대리 모델 → 최적화 → FEM 검증) 결과를 한 화면에 (파일 하나, 인터넷 불필요)

python -m fp08.app --results results --run runs/main                       # demo 결과 폴더로 화면 만들기
python -m fp08.app --results results --run runs/main --input ..\\10_입력_1차설계\\out   # 10 의 1차 설계(STL·report.json)도 같이
옵션: --no-stress (응력 색 계산 생략, FEM 다시 안 풂)

두 경로 공통: fp08.fem_opt (지금: 수식 형상 + FEM 직접 최적화) / fp08.demo (나중: DeepSDF·PINO 대리 모델).
결과 JSON 의 method 값('formula_fem' / 'surrogate')에 따라 화면 문구·그래프가 바뀜.

만드는 것: results/app.html — 브라우저로 더블클릭해서 열기.
  - 3D: 최적 형상(드래그 회전·휠 확대), 응력 색(FEM 재계산 값), 고정부품·설계 공간 유령, 전·후 비교
  - 판정: FEM 값 vs 기준(막대), 대리 모델 예측값 표시, 상태(ok / fallback)
  - 흐름: 시작점 후보 → 대리 모델 최적화 → FEM 검증 순서 (detail/opt_<tag>.json)
  - 품질 관문: runs/main/state.json 의 마지막 관문 결과 (있으면)
수치는 전부 결과 파일과 이 스크립트의 FEM 재계산에서 나옴. 화면에서 지어낸 값 없음.
"""
import os, sys, json, glob, base64, argparse, time
import numpy as np
from scipy import ndimage
from skimage import measure
from . import problems, labels, fem, loop

HERE = os.path.dirname(os.path.abspath(__file__))

PRODUCT_TEXT = {
    'bike_mount': dict(name='자전거 휴대폰 거치대',
                       request='자갈길에서도 휴대폰이 흔들리지 않게, 최대한 가볍게 (3D 프린트, PETG)',
                       icon='🚲'),
    'tv_feet': dict(name='TV 양발 스탠드', request='65" TV(20.8 kg)를 받치는 양발 스탠드, 기울여도 안 넘어지고 최대한 가볍게 (Al 6061-T6)',
                    icon='📺'),
    'tv_pedestal': dict(name='TV 중앙 스탠드', request='65" TV(20.8 kg)를 받치는 중앙형 스탠드, 기울여도 안 넘어지고 최대한 가볍게 (Al 6061-T6)',
                        icon='📺'),
}
COND_TEXT = {'phone_mass_g': ('휴대폰 질량', 'g'), 'phone_angle_deg': ('화면 기울기', '°'),
             'tv_mass_kg': ('TV 질량', 'kg'), 'leg_span_mm': ('양발 간격', 'mm')}
GROUP_TEXT = {'bike_pad80_free': '받침 80 mm 앞 · 화면 각도 자유(기둥 60 mm)', 'bike_pad50': '받침 50 mm 앞', 'bike_pad80': '받침 80 mm 앞', 'bike_pad120': '받침 120 mm 앞',
              'tvfeet_L300': '발 길이 300 mm · 다리 하나', 'tvfeet_L220': '발 길이 220 mm · 다리 하나', 'tvped': '중앙형'}


# ----------------------------------------------------------------------------- 형상·응력
def _grid_field(p, F):
    """요소 값 (ne,) → 대칭 복원한 (z, y, x) 배열 + 2칸 패딩"""
    A = p.grid.eshape(F).astype(np.float32)
    if p.sym_axis is not None:
        ax = 2 - p.sym_axis
        A = np.concatenate([np.flip(A, ax), A], ax)
    return np.pad(A, 2)


def mesh_of(p, mask, field=None, up=2):
    """요소 마스크 → 다듬은 표면 (V mm (n,3), F (m,3), 꼭짓점 값 (n,) 또는 None). demo.full_mesh 와 같은 좌표."""
    g = p.grid
    if not mask.any():
        return None
    A = _grid_field(p, mask.astype(float))
    A = ndimage.zoom(ndimage.gaussian_filter(A, 0.7), up, order=1)
    v, f, _, _ = measure.marching_cubes(A, 0.5)
    v = v / up
    val = None
    if field is not None:
        B = _grid_field(p, np.where(mask, field, 0.0))
        B = ndimage.grey_dilation(B, size=3)               # 표면 밖 빈 칸에도 이웃 재료 칸 값이 닿게
        idx = np.clip(np.floor(v).astype(int), 0, np.array(B.shape) - 1)
        val = B[idx[:, 0], idx[:, 1], idx[:, 2]]
    v = (v - 2) * g.h
    o = g.origin.copy(); n = [g.nx, g.ny, g.nz]
    if p.sym_axis is not None:
        o[p.sym_axis] -= n[p.sym_axis] * g.h
    V = np.stack([v[:, 2] + o[0], v[:, 1] + o[1], v[:, 0] + o[2]], 1)
    return V, f, val


def element_vm(p, occ, cond):
    """FEM 다시 풀어 요소별 미세스 응력 (하중 경우 중 최대, MPa) + 판정값. problems.*.evaluate 와 같은 하중 조합."""
    r = labels.fem_label(p, occ, cond)
    g = p.grid
    U = r['U']
    if p.product == 'bike_mount':
        pk = p.conditions['formula']['peak_g']
        cases = [U[n] * pk for n in ('shock_z', 'shock_y')]
    else:
        cases = []
        for case, coef in p.loads(cond).items():
            u = np.zeros(3 * g.nn)
            for b, c in coef.items():
                if b in U:
                    u += c * U[b]
            cases.append(u)
    vm = np.max([fem.von_mises(fem.element_stress(g, p.C, p.B0, u)) for u in cases], 0)
    return vm, r['eval'], r['t']


def pack_mesh(m, scale=None):
    """메쉬 → base64 (꼭짓점 uint16 양자화, 면 uint32, 값 uint8 = 응력비 0~2 → 0~255)"""
    if m is None:
        return None
    V, F, val = m
    lo, hi = V.min(0), V.max(0)
    q = np.round((V - lo) / np.maximum(hi - lo, 1e-9) * 65535).astype('<u2')
    fi = '<u2' if len(V) < 65536 else '<u4'           # 면 번호: 꼭짓점이 65,536개 미만이면 16비트
    out = dict(n=int(len(V)), m=int(len(F)), lo=lo.round(4).tolist(), hi=hi.round(4).tolist(), fb=2 if fi == '<u2' else 4,
               v=base64.b64encode(q.tobytes()).decode(), f=base64.b64encode(F.astype(fi).tobytes()).decode())
    if val is not None and scale:
        s = np.clip(val / scale / 2.0 * 255, 0, 255).astype('u1')
        out['s'] = base64.b64encode(s.tobytes()).decode()
    return out


def read_stl(path):
    """이진 STL → (V, F) (같은 꼭짓점 합침)"""
    b = open(path, 'rb').read()
    n = int(np.frombuffer(b[80:84], '<u4')[0])
    rec = np.frombuffer(b[84:84 + n * 50], dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')])
    P = rec['v'].reshape(-1, 3).astype(np.float64)
    V, inv = np.unique(np.round(P, 4), axis=0, return_inverse=True)
    return V, inv.reshape(-1, 3), None


# ----------------------------------------------------------------------------- 데이터 모으기
def criteria_rows(p, fem_eval, pred):
    rows = []
    for c in p.criteria:
        if c['op'] not in ('<=', '>='):
            continue
        k = c['id']
        ev = fem_eval or {}
        v = ev.get(k)
        if k == 'tip':                                  # 넘어짐 여유 = tip_margin_fb (+ tip_margin_lat) 중 작은 값
            tv = [ev[q] for q in ('tip_margin_fb', 'tip_margin_lat') if q in ev]
            v = min(tv) if tv else None
        rows.append(dict(id=k, label=c['quantity'], op=c['op'], lim=c['value'], src=c.get('source', ''),
                         fem=None if v is None else float(v), pred=None if not pred or k not in pred else float(pred[k])))
    return rows


def gate_info(run):
    sf = os.path.join(run, 'state.json') if run else None
    if not sf or not os.path.exists(sf):
        return None
    st = json.load(open(sf))
    G = st.get('gate', {})
    if not G:
        return dict(stages=list(st.get('stages', {}).keys()) if isinstance(st.get('stages'), dict) else None)
    last = G[sorted(G)[-1]]
    out = {}
    for g, v in last.items():
        if isinstance(v, dict):
            m = v.get('metrics', {})
            out[g] = dict(passed=v.get('passed'), reasons=v.get('why'),
                          relL2=m.get('relL2_mean'), freq5=m.get('freq_within5_frac'),
                          judge=m.get('judge_abs_p90'))
    return dict(gate=out, sdf_test=st.get('sdf_test'), limits=loop.GATE)


def input_info(inp):
    """10 의 결과 폴더(report.json, spec.json, design_1st.stl) — 있으면 읽기"""
    if not inp or not os.path.isdir(inp):
        return None, None
    info = {}
    for nm in ('report.json', 'spec.json'):
        f = os.path.join(inp, nm)
        if os.path.exists(f):
            try:
                info[nm[:-5]] = json.load(open(f, encoding='utf-8'))
            except Exception as e:
                info[nm[:-5] + '_error'] = str(e)
    stl = os.path.join(inp, 'design_1st.stl')
    mesh = read_stl(stl) if os.path.exists(stl) else None
    return info, mesh


def collect(results, run, inp=None, stress=True, log=print):
    cases, base_cache = [], {}
    in_info, in_mesh = input_info(inp)
    for jf in sorted(glob.glob(os.path.join(results, '*.json'))):
        rec = json.load(open(jf, encoding='utf-8'))
        if 'group' not in rec or 'status' not in rec:
            continue
        g, cond = rec['group'], rec['cond']
        p = problems.get(g)
        tag = os.path.basename(jf)[:-5]
        det = os.path.join(results, 'detail', f'opt_{tag}.json')
        detj = json.load(open(det, encoding='utf-8')) if os.path.exists(det) else {}
        tried = detj.get('tried', [])
        method = rec.get('method') or detj.get('method') or 'surrogate'
        occf = os.path.join(results, 'detail', f'opt_{tag}.npy')
        crit = {c['id']: c for c in p.criteria}
        vm_lim = crit['vm']['value']
        t0 = time.time()
        # 설계 공간 메쉬 (FEM 없음 — 꽉 채운 설계 공간 FEM 은 행렬이 커서 CPU 로 1분 이상)
        if g not in base_cache:
            design, fixed = p.label == 0, p.label == 1
            base_cache[g] = dict(space=pack_mesh(mesh_of(p, design, up=1)), fixed=pack_mesh(mesh_of(p, fixed)),
                                 rigid=pack_mesh(mesh_of(p, p.label == 3, up=1)),   # 강체 대역 (TV 블록 등, 질량 제외)
                                 full=pack_mesh(mesh_of(p, design | fixed, up=1)), full_mass=p.mass_g(np.ones(p.grid.ne)))
        b = base_cache[g]

        def shape_mesh(occ):
            vm = element_vm(p, occ, cond)[0] if stress else None
            return pack_mesh(mesh_of(p, (occ & (p.label == 0)) | (p.label == 1), vm), vm_lim)
        opt, start, start_eval = None, None, None
        if rec['status'] == 'ok' and os.path.exists(occf):
            opt = shape_mesh(np.load(occf) > 0.5)
        elif rec['status'] == 'ok' and os.path.exists(os.path.join(results, tag + '.stl')):
            opt = pack_mesh(read_stl(os.path.join(results, tag + '.stl')))
        stf = os.path.join(results, 'detail', f'start_{tag}.npy')
        if os.path.exists(stf):                       # FEM 직접 경로: 다듬기 전 형상
            st_occ = np.load(stf) > 0.5
            start = shape_mesh(st_occ)
            start_eval = next((t['fem'] for t in tried if t.get('idx') == detj.get('best_idx') and t.get('fem')), None)
        # 합격 형상이 없을 때 보여줄 값: 기준에 가장 가까운 후보의 FEM 값
        from .fem_opt import shape_independent_fails
        infeasible = detj.get('infeasible')
        if infeasible is None:
            infeasible = shape_independent_fails(p, [t['fem'] for t in tried if t.get('fem')])
        near_eval = None
        if rec['status'] != 'ok':
            from .fem_opt import violation
            ev = [t['fem'] for t in tried if t.get('fem')]
            near_eval = min(ev, key=lambda e: violation(p, e)) if ev else None
        png = os.path.join(results, tag + '.png')
        thumb = 'data:image/png;base64,' + base64.b64encode(open(png, 'rb').read()).decode() if os.path.exists(png) else None
        key = 'tv_feet' if g.startswith('tvfeet') else 'tv_pedestal' if g.startswith('tvped') else p.product
        pt = PRODUCT_TEXT.get(key, dict(name=p.product, request='', icon=''))
        cases.append(dict(
            tag=tag, group=g, product=p.product, product_name=pt['name'], icon=pt['icon'], request=pt['request'],
            group_text=GROUP_TEXT.get(g, g), status=rec['status'], sec=rec.get('sec'), method=method,
            t_search=detj.get('t_search'), best_idx=detj.get('best_idx'),
            fixes=[dict(idx=x['idx'], kind=x['kind'], start=x.get('start_mass_g'),
                        hist=[dict(m=h['mass_g'], ok=h['passed']) for h in x.get('hist', [])]) for x in detj.get('fixes', [])],
            cond=[dict(k=k, label=COND_TEXT.get(k, (k, ''))[0], unit=COND_TEXT.get(k, ('', ''))[1], v=v) for k, v in cond.items()],
            material=p.material, grid_h=p.grid.h, crit=criteria_rows(p, rec.get('fem'), rec.get('pred')),
            near_crit=criteria_rows(p, near_eval, None) if near_eval else None, infeasible=infeasible,
            start_mass=(start_eval or {}).get('mass_g'),
            mass=(rec.get('fem') or {}).get('mass_g'), full_mass=b['full_mass'], vm_lim=vm_lim,
            uplift=(rec.get('fem') or {}).get('uplift'),
            tried=[dict(pred_mass=t.get('pred_mass_g'), connected=t.get('connected'), idx=t.get('idx'), family=t.get('family'),
                        fem_pass=(t.get('fem') or {}).get('pass'), fem_mass=(t.get('fem') or {}).get('mass_g')) for t in tried],
            assumptions=getattr(p, 'assumptions', []), margins=rec.get('margins', {}),
            files=[f for f in (tag + '.stl', tag + '.json', tag + '.png') if os.path.exists(os.path.join(results, f))],
            mesh=dict(opt=opt, start=start),
            thumb=thumb))
        log(f'[app] {tag}: {rec["status"]} (화면 데이터 {time.time() - t0:.1f} s)')
    first = None
    if in_mesh is not None:
        first = pack_mesh(in_mesh)
    base = {g: dict(space=b['space'], fixed=b['fixed'], full=b['full'], rigid=b['rigid']) for g, b in base_cache.items()}   # 그룹별 한 번만
    return dict(cases=cases, base=base, gate=gate_info(run), input=in_info, input_mesh=first,
                made=time.strftime('%Y-%m-%d %H:%M'), stress=stress)


# ----------------------------------------------------------------------------- HTML
def build(results, run=None, inp=None, stress=True, out=None, log=print):
    D = collect(results, run, inp, stress, log)
    tpl = open(os.path.join(HERE, 'app_template.html'), encoding='utf-8').read()
    vend = ''.join(open(os.path.join(HERE, 'vendor', f), encoding='utf-8').read() + '\n' for f in ('three.min.js', 'OrbitControls.js'))
    data = json.dumps(D, ensure_ascii=False, default=float).replace('</', '<\\/')
    html = tpl.replace('/*__VENDOR__*/', vend).replace('/*__DATA__*/null', data)
    out = out or os.path.join(results, 'app.html')
    open(out, 'w', encoding='utf-8').write(html)
    log(f'[app] 화면: {out} ({os.path.getsize(out) / 1e6:.1f} MB, 사례 {len(D["cases"])}개)')
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--results', default='results'); ap.add_argument('--run', default='runs/main')
    ap.add_argument('--input', default=None, help='10 의 결과 폴더 (report.json, design_1st.stl)')
    ap.add_argument('--no-stress', action='store_true'); ap.add_argument('--out', default=None)
    a = ap.parse_args()
    build(a.results, a.run, a.input, not a.no_stress, a.out)


if __name__ == '__main__':
    main()
