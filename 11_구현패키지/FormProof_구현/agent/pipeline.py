"""LLM 에이전트 실행기: 여섯 단계를 차례로 실행하고, 검증 관문에서 떨어지면 재설계로 되돌린다.

  ① 설계 명세(spec JSON)  →  ② 역설계(위상 최적화, 선택: 형상 AI 후보를 시작점으로)  →  CAD 결합(STL)
  →  ③ 검증 관문(출력 STL 재격자화 → FEM 재계산 → 기준 비교)  →  제작 파일(도면) + 근거 리포트

각 단계는 '입력 파일 → 출력 파일' 계약을 지키는 외부 명령이다 (아래 STAGES). 결과는 runs/<run>/state.json 에 누적된다.
불합격이면 미달 항목에 따라 목표를 조이고(예: f1 미달 → FT +5 %) 재설계, 최대 MAX_LOOP 회.

사용:  python agent/pipeline.py --spec spec/bike_mount_targets.json --run runs/r1           (조건 생성기 결과를 쓰려면 --spec runs/spec_targets.json)
"""
import argparse, json, os, subprocess, sys, time, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_ENV = dict(GRIP='2', NX='88', AM='1', RF='5', ETAE='0.6', TILT='35', ITERS='120',
                SCHED='{"0":1,"20":2,"40":4,"60":8,"80":16,"100":32}')
MAX_LOOP = 3

def sh(cmd, cwd, env=None, log=None):
    t0 = time.time(); e = dict(os.environ, **(env or {}))
    with open(log, 'w') if log else open(os.devnull, 'w') as f: p = subprocess.run(cmd, cwd=cwd, env=e, shell=True, stdout=f, stderr=subprocess.STDOUT)
    if p.returncode: raise RuntimeError(f'실패({p.returncode}): {cmd}  로그: {log}')
    return round(time.time() - t0, 1)

def connectivity(rho_path):
    """출력 형상 연결성: 면(face)으로 이어진 덩어리 수와 본체에서 떨어진 요소 수.
    모서리 · 꼭짓점으로만 닿은 요소는 FEM에서는 강성을 갖는 것처럼 계산되지만 실제 출력물에서는 끊긴 부재다."""
    import numpy as np
    from scipy import ndimage
    M = np.load(os.path.join(ROOT, 'data', 'grid_meta.npz')); nx, ny, nz = int(M['nx']), int(M['ny']), int(M['nz'])
    rv = np.load(rho_path); r = rv.reshape(nz, ny, nx) > 0.5; lab, n = ndimage.label(r); sz = np.bincount(lab.ravel())[1:]
    gray = float(((rv > 0.05) & (rv < 0.95)).sum() / max((rv > 0.5).sum(), 1))   # 중간 밀도 비율: 0/1로 수렴하지 않은 정도
    return dict(components=int(n), detached_cells=int(sz.sum() - sz.max()) if n else 0, gray_ratio=round(gray, 3))

def mfg_check(rho_path, build_axis='z', min_feat_cells=2, overhang_limit=0.15):
    """제작성 검사 (3D 프린팅 기준, 2026-11-16 추가 · 임계값은 잠정 — 확인 필요)
    thin_ratio     : 두께가 min_feat_cells(×2 mm) 미만인 요소 비율 — 열림 연산(opening)으로 사라지는 요소 / 전체
    overhang_ratio : 출력 방향 기준 바로 아래와 대각 아래가 모두 비어 있는 요소 비율 (서포트 필요 후보)
    gate() 에서 MFG_GATE=1 일 때만 불합격 조건으로 쓴다(기본은 리포트 표시만)."""
    import numpy as np
    from scipy import ndimage
    M = np.load(os.path.join(ROOT, 'data', 'grid_meta.npz')); nx, ny, nz = int(M['nx']), int(M['ny']), int(M['nz'])
    r = np.load(rho_path).reshape(nz, ny, nx) > 0.5; n = max(int(r.sum()), 1)
    st = ndimage.generate_binary_structure(3, 1); op = ndimage.binary_opening(r, st, iterations=max(min_feat_cells - 1, 1))
    thin = float((r & ~op).sum() / n)
    below = np.zeros_like(r); below[1:] = r[:-1]
    diag = np.zeros_like(r)
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)): diag[1:] |= np.roll(np.roll(r[:-1], dy, 1), dx, 2)
    over = r & ~below & ~diag; over[0] = False
    return dict(thin_ratio=dict(value=round(thin, 3), note=f'두께 < {2*min_feat_cells} mm 요소 비율'),
                overhang_ratio=dict(value=round(float(over.sum() / n), 3), note=f'출력 방향 {build_axis} 기준 서포트 필요 후보 비율 (잠정 한계 {overhang_limit})'))

def gate(ev, tg, rho_path=None):
    """C 검증 관문: 출력 형상 재계산 결과를 기준과 비교 → (합격 여부, 판정표, 미달 항목). rho_path 가 있으면 연결성도 판정"""
    chk = {'f1_hz': (ev['f'][0], '>=', tg['f1_min_hz']), 'phone_Tmax_rise_c': (ev['Tmax'], '<=', tg['phone_Tmax_rise_max_c']),
           'touch_mm': (max(ev['touch_mm']), '<=', tg['touch_max_mm']),
           'shock_vm_mpa': (max(ev['shock']['vert']['vm999'], ev['shock']['fore']['vm999']), '<=', tg['shock_vm_max_mpa']),
           'shock_interlayer_mpa': (max(ev['shock']['vert']['interlayer999'], ev['shock']['fore']['interlayer999']), '<=', tg['shock_interlayer_max_mpa'])}
    if rho_path:
        c = connectivity(rho_path); chk['detached_cells'] = (c['detached_cells'], '<=', 0); chk['gray_ratio'] = (c['gray_ratio'], '<=', 0.05)
        if os.environ.get('MFG_GATE') == '1':
            m = mfg_check(rho_path); chk['overhang_ratio'] = (m['overhang_ratio']['value'], '<=', 0.15)
    fails = {k: v for k, v in chk.items() if not (v[0] >= v[2] if v[1] == '>=' else v[0] <= v[2])}
    return not fails, chk, fails

def run(a):
    run = os.path.abspath(a.run); os.makedirs(run, exist_ok=True); tg = json.load(open(a.spec)); st = dict(spec=tg, loops=[], t={})
    eng, cad = os.path.join(ROOT, 'engine'), os.path.join(ROOT, 'cad'); FT = tg['f1_min_hz']; TL = tg['phone_Tmax_rise_max_c']
    for loop in range(MAX_LOOP):
        tag = f'{os.path.basename(run)}_L{loop}'; env = dict(BASE_ENV, TAG=tag, FT=str(FT), TLIM=str(TL), DLIM=str(tg['touch_max_mm']))
        if a.start: env.update(START_RHO=a.start)
        rec = dict(loop=loop, FT=FT, TLIM=TL)
        rec['t_opt'] = sh('python3 opt_int.py', eng, env, f'{run}/{tag}_opt.log')                          # ② 역설계
        rec['t_cad'] = sh(f'python3 build_body.py {tag} {run}/{tag}_body', cad, None, f'{run}/{tag}_cad.log')   # CAD 결합
        rec['t_vox'] = sh(f'python3 vox.py {run}/{tag}_body_phoneframe.stl {run}/{tag}_rho.npy 88', cad, None, f'{run}/{tag}_vox.log')
        rec['t_eval'] = sh('python3 opt_int.py', eng, dict(BASE_ENV, MODE='eval', RHO=f'{run}/{tag}_rho.npy', TAG=tag), f'{run}/{tag}_eval.log')  # ③
        ev = json.load(open(os.path.join(eng, f'frfint_{tag}.json'))); ok, chk, fails = gate(ev, tg, f'{run}/{tag}_rho.npy')
        rec.update(passed=ok, checks=chk, fails=fails, mass_g=ev['mass_g']); st['loops'].append(rec); json.dump(st, open(f'{run}/state.json', 'w'), ensure_ascii=False, indent=1)
        print(json.dumps(dict(loop=loop, passed=ok, fails=fails, mass_g=ev['mass_g'])), flush=True)
        if ok: break
        if 'f1_hz' in fails: FT *= 1.05                    # 재설계 지시: 미달 항목에 따라 목표를 조인다
        if 'phone_Tmax_rise_c' in fails: TL -= 0.5
        if 'touch_mm' in fails: tg = dict(tg, touch_max_mm=tg['touch_max_mm'])   # 판정 기준은 그대로, 최적화 목표만 조인다
        DL_opt = float(env.get('DLIM', tg['touch_max_mm'])) * (0.9 if 'touch_mm' in fails else 1.0)
        if 'shock_vm_mpa' in fails or 'shock_interlayer_mpa' in fails: FT *= 1.05   # 응력 제약은 최적화에 없음 → 강성 상향으로 대응 (TODO: 응력 제약 추가)
    st['result'] = 'pass' if ok else 'fail'; shutil.copy(f'{run}/{tag}_body_world.stl', f'{run}/final_body.stl') if ok else None
    json.dump(st, open(f'{run}/state.json', 'w'), ensure_ascii=False, indent=1); print('결과', st['result'], f'{run}/state.json')

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--spec', required=True); p.add_argument('--run', required=True); p.add_argument('--start', default=None, help='형상 AI 후보(cand_k.npy)를 시작 형상으로')
    run(p.parse_args())
