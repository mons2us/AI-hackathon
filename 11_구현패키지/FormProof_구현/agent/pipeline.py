"""LLM 에이전트 실행기: 여섯 단계를 차례로 실행하고, 검증 관문에서 떨어지면 재설계로 되돌린다.

  ① 설계 명세(spec JSON)  →  ② 역설계(위상 최적화, 선택: 형상 AI 후보를 시작점으로)  →  CAD 결합(STL)
  →  ③ 검증 관문(출력 STL 재격자화 → FEM 재계산 → 기준 비교)  →  제작 파일(도면) + 근거 리포트

각 단계는 '입력 파일 → 출력 파일' 계약을 지키는 외부 명령이다 (아래 STAGES). 결과는 runs/<run>/state.json 에 누적된다.
불합격이면 미달 항목에 따라 목표를 조이고(예: f1 미달 → FT +5 %) 재설계, 최대 MAX_LOOP 회.

사용:  python agent/pipeline.py --spec spec/bike_mount_targets.json --run runs/r1           (조건 생성기 결과를 쓰려면 --spec runs/spec_targets.json)
"""
import argparse, json, os, subprocess, sys, time, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_ENV = dict(GRIP='2', NX='88', MSYS='0.311', AM='1', RF='8', ETAE='0.7', TILT='35', ITERS='120',
                SCHED='{"0":1,"20":2,"40":4,"60":8,"80":16,"100":32}')
MAX_LOOP = 3

def sh(cmd, cwd, env=None, log=None):
    t0 = time.time(); e = dict(os.environ, **(env or {}))
    with open(log, 'w') if log else open(os.devnull, 'w') as f: p = subprocess.run(cmd, cwd=cwd, env=e, shell=True, stdout=f, stderr=subprocess.STDOUT)
    if p.returncode: raise RuntimeError(f'실패({p.returncode}): {cmd}  로그: {log}')
    return round(time.time() - t0, 1)

def gate(ev, tg):
    """③ 검증 관문: 출력 형상 재계산 결과를 기준과 비교 → (합격 여부, 미달 항목)"""
    chk = {'f1_hz': (ev['f'][0], '>=', tg['f1_min_hz']), 'phone_Tmax_rise_c': (ev['Tmax'], '<=', tg['phone_Tmax_rise_max_c']),
           'touch_mm': (max(ev['touch_mm']), '<=', tg['touch_max_mm']),
           'shock_vm_mpa': (max(ev['shock']['vert']['vm999'], ev['shock']['fore']['vm999']), '<=', tg['shock_vm_max_mpa']),
           'shock_interlayer_mpa': (max(ev['shock']['vert']['interlayer999'], ev['shock']['fore']['interlayer999']), '<=', tg['shock_interlayer_max_mpa'])}
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
        ev = json.load(open(os.path.join(eng, f'frfint_{tag}.json'))); ok, chk, fails = gate(ev, tg)
        rec.update(passed=ok, checks=chk, fails=fails, mass_g=ev['mass_g']); st['loops'].append(rec); json.dump(st, open(f'{run}/state.json', 'w'), ensure_ascii=False, indent=1)
        print(json.dumps(dict(loop=loop, passed=ok, fails=fails, mass_g=ev['mass_g'])), flush=True)
        if ok: break
        if 'f1_hz' in fails: FT *= 1.05                    # 재설계 지시: 미달 항목에 따라 목표를 조인다
        if 'phone_Tmax_rise_c' in fails: TL -= 0.5
    st['result'] = 'pass' if ok else 'fail'; shutil.copy(f'{run}/{tag}_body_world.stl', f'{run}/final_body.stl') if ok else None
    json.dump(st, open(f'{run}/state.json', 'w'), ensure_ascii=False, indent=1); print('결과', st['result'], f'{run}/state.json')

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--spec', required=True); p.add_argument('--run', required=True); p.add_argument('--start', default=None, help='형상 AI 후보(cand_k.npy)를 시작 형상으로')
    run(p.parse_args())
