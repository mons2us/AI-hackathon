"""학습 모델 · 계산 결과를 10 GUI(입력 단계 앱) 새 폴더로 옮기기 (11-17 추가, 회사 PC · Windows 용)

새 GUI 를 ZIP 으로 받을 때마다 손으로 하던 5가지를 한 번에:
  ① models\\ (results_fp11.zip · grid_meta.npz · fp11\\z0_*.npy 번역 결과) 복사
  ② formproof_input\\templates\\db\\precomputed\\ (미리 계산한 결과 DB) 복사
  ③ Windows 버그 수정: integral.fields() 가 npz 를 닫지 않고 임시 폴더를 지워 PermissionError(WinError 32)
  ④ 'DB 다 채움' 표시 파일 — 서버가 켜질 때 뒤에서 DB 를 채우다 학습 모델 최적화와 같이 멈추던 문제 피하기
  ⑤ run_gui.bat 만들기 — 기존 .venv 의 python 으로 실행 (새 폴더에서 setup.bat · PyTorch 재설치 안 함)

사용 (cmd, 기존 GUI 폴더의 .venv python 으로):
  1) 지금 쓰던 GUI 폴더 → 운반 폴더로 저장 (한 번)
     "<기존>\\.venv\\Scripts\\python.exe" carry_to_gui.py save  --gui "<기존>\\10_입력_1차설계" --carry C:\\work\\fp_carry
  2) 새 GUI 폴더에 적용 (새로 받을 때마다)
     "<기존>\\.venv\\Scripts\\python.exe" carry_to_gui.py apply --gui "<새>\\10_입력_1차설계"  --carry C:\\work\\fp_carry
  3) "<새>\\10_입력_1차설계\\run_gui.bat"  더블클릭 (또는 run_gui.bat 20 → 찾아가기 20걸음)

vimp 학습 결과로 바꾸려면: 서버에서 만든 results_fp11.zip · grid_meta.npz 를 운반 폴더 models\\ 에 넣고
  models\\fp11\\ 폴더를 지운 뒤 apply (모델이 바뀌면 번역 결과 z0 를 처음 한 번 다시 계산 — CPU 로 오래 걸림).
"""
import argparse, glob, os, shutil, subprocess, sys

DB_REL = os.path.join('formproof_input', 'templates', 'db', 'precomputed')
FIX_OLD = '''        d = np.load(os.path.join(td, f"field_{tag}.npz"))
        out = {k: np.asarray(d[k], np.float32) for k in FIELD_KEYS}
        out["f1"] = float(d["f1"])'''
FIX_NEW = '''        with np.load(os.path.join(td, f"field_{tag}.npz")) as d:   # Windows: 닫고 나서 임시 폴더 삭제 (carry_to_gui 수정)
            out = {k: np.asarray(d[k], np.float32) for k in FIELD_KEYS}
            out["f1"] = float(d["f1"])'''


def copytree(src, dst):
    """src 안의 파일을 dst 로 (있으면 덮어씀, dst 에만 있는 파일은 그대로). 복사한 파일 수"""
    n = 0
    for root, _, files in os.walk(src):
        t = os.path.join(dst, os.path.relpath(root, src)); os.makedirs(t, exist_ok=True)
        for f in files:
            shutil.copy2(os.path.join(root, f), os.path.join(t, f)); n += 1
    return n


def check_gui(gui):
    ok = os.path.isfile(os.path.join(gui, 'app', 'server.py')) and os.path.isdir(os.path.join(gui, 'formproof_input'))
    if not ok: sys.exit(f'GUI 폴더가 아님 (app\\server.py · formproof_input 없음): {gui}\n  → "...\\10_입력_1차설계" 를 주세요')


def save(a):
    check_gui(a.gui); os.makedirs(a.carry, exist_ok=True)
    m = os.path.join(a.gui, 'models')
    print('① models →', copytree(m, os.path.join(a.carry, 'models')), '파일')
    d = os.path.join(a.gui, DB_REL)
    print('② 결과 DB →', copytree(d, os.path.join(a.carry, 'precomputed')) if os.path.isdir(d) else 0, '파일')
    for f in ('results_fp11.zip', 'grid_meta.npz'):
        print('   ', f, '있음' if os.path.exists(os.path.join(a.carry, 'models', f)) else '없음 ← 넣어야 학습 모델로 돔')
    print('저장 끝:', a.carry)


def apply(a):
    check_gui(a.gui); assert os.path.isdir(a.carry), f'운반 폴더 없음: {a.carry}'
    print('① models ←', copytree(os.path.join(a.carry, 'models'), os.path.join(a.gui, 'models')), '파일')
    pc = os.path.join(a.carry, 'precomputed')
    print('② 결과 DB ←', copytree(pc, os.path.join(a.gui, DB_REL)) if os.path.isdir(pc) else 0, '파일')
    p = os.path.join(a.gui, 'formproof_input', 'integral.py'); s = open(p, encoding='utf-8').read()
    if FIX_NEW.splitlines()[0].split('#')[0].rstrip() in s or 'with np.load(os.path.join(td, f"field_{tag}.npz")) as d' in s: print('③ Windows 버그: 이미 고쳐져 있음')
    elif FIX_OLD in s: open(p, 'w', encoding='utf-8').write(s.replace(FIX_OLD, FIX_NEW)); print('③ Windows 버그: 고침 (integral.py fields)')
    else: print('③ Windows 버그: 해당 코드를 못 찾음 — GUI 버전이 달라 그대로 둠 (PermissionError 가 나면 알려 주세요)')
    r = subprocess.run([sys.executable, '-c', 'from formproof_input import memo; p=memo.marker(); open(p,"w").close(); print(p)'],
                       cwd=a.gui, capture_output=True, text=True, encoding='utf-8', errors='replace', env=dict(os.environ, PYTHONUTF8='1'))
    print('④ DB 다 채움 표시:', r.stdout.strip() if r.returncode == 0 else '실패 — ' + (r.stderr or '')[-300:])
    bat = os.path.join(a.gui, 'run_gui.bat')
    with open(bat, 'w', encoding='utf-8') as f:
        f.write('@echo off\r\nchcp 65001 >nul\r\ncd /d "%~dp0"\r\nset PYTHONUTF8=1\r\n'
                'if "%1"=="" (set FP11_ITERS=10) else (set FP11_ITERS=%1)\r\nset FP11_EVERY=1\r\n'
                'echo 찾아가기 %FP11_ITERS% 걸음 · 매 걸음 화면 저장\r\n'
                f'"{sys.executable}" app\\server.py\r\npause\r\n')
    print('⑤ 실행 파일:', bat, '(이 python 으로 실행:', sys.executable, ')')
    z = glob.glob(os.path.join(a.gui, 'models', 'fp11', 'z0_*.npy'))
    print('번역 결과(z0):', ', '.join(os.path.basename(x) for x in z) if z else '없음 → 처음 최적화 때 다시 계산 (CPU 로 오래 걸림)')
    print('\n끝. run_gui.bat 더블클릭 → 브라우저 http://localhost:8765 → 예시 "폰 거치대"')


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('cmd', choices=['save', 'apply'])
    p.add_argument('--gui', required=True, help='...\\10_입력_1차설계'); p.add_argument('--carry', default=r'C:\work\fp_carry')
    a = p.parse_args(); a.gui = os.path.abspath(a.gui); a.carry = os.path.abspath(a.carry)
    save(a) if a.cmd == 'save' else apply(a)
