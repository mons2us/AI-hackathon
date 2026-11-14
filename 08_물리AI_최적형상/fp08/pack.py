"""서버 업로드/다운로드용 묶기·풀기 (Windows·Linux 공통, 파이썬 표준 zipfile 만 사용)

python -m fp08.pack code  upload_code.zip            # 코드: fp08/ experiments/ handoff/ *.md *.bat *.sh *.txt
python -m fp08.pack data  data  upload_data.zip      # 데이터 폴더 통째 (형상·FEM 정답)
python -m fp08.pack runs  runs/main  results.zip     # 학습 결과: 체크포인트·state.json·report.html·로그·demo 결과
python -m fp08.pack unpack results.zip  .            # 풀기 (zip 안의 폴더 구조 그대로)
python -m fp08.pack check data                       # 데이터 폴더 점검: 그룹별 형상·FEM 개수
python -m fp08.pack report runs/main                 # 학습 결과 한눈에: DeepSDF IoU·표면오차, PINO 관문, 시연
"""
import os, sys, json, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def _add_tree(z, src, arc_root, skip=('__pycache__', '.tmp')):
    n = 0
    for dp, dn, fn in os.walk(src, followlinks=True):
        dn[:] = [d for d in dn if d not in skip]
        for f in fn:
            if any(s in f for s in skip):
                continue
            full = os.path.join(dp, f)
            arc = os.path.join(arc_root, os.path.relpath(full, src)).replace('\\', '/')
            comp = zipfile.ZIP_STORED if f.endswith(('.npz', '.pt', '.png', '.zip')) else zipfile.ZIP_DEFLATED
            z.write(full, arc, compress_type=comp)
            n += 1
    return n


def pack_code(out):
    with zipfile.ZipFile(out, 'w') as z:
        n = _add_tree(z, os.path.join(ROOT, 'fp08'), 'fp08')
        n += _add_tree(z, os.path.join(ROOT, 'experiments'), 'experiments')
        n += _add_tree(z, os.path.join(ROOT, 'handoff'), 'handoff')
        for f in os.listdir(ROOT):
            if f.endswith(('.md', '.bat', '.sh', '.txt')) or f == '.clinerules':
                z.write(os.path.join(ROOT, f), f); n += 1
    print(f'코드 {n}개 파일 → {out} ({os.path.getsize(out) / 1e6:.1f} MB)')


def pack_dir(src, out, arc_root=None):
    arc_root = arc_root or os.path.basename(os.path.normpath(src))
    with zipfile.ZipFile(out, 'w', allowZip64=True) as z:
        n = _add_tree(z, src, arc_root)
    print(f'{src} {n}개 파일 → {out} ({os.path.getsize(out) / 1e6:.1f} MB)')


def unpack(zp, dest):
    with zipfile.ZipFile(zp) as z:
        z.extractall(dest)
        print(f'{zp} → {dest} ({len(z.namelist())}개 파일)')


def check(data):
    from . import datagen, problems
    print(f'{"그룹":14s} {"형상":>7s} {"ESO":>6s} {"FEM":>6s} {"능동학습 FEM":>12s}')
    for g in problems.GROUPS:
        d = os.path.join(data, g)
        if not os.path.isdir(d):
            print(f'{g:14s}   (없음)'); continue
        fs = os.listdir(d)
        ns = sum(len(__import__('numpy').load(os.path.join(d, f))['idx']) for f in fs if f.startswith('shapes_') and f.endswith('.npz') and 'shapes_e' not in f)
        ne = sum(len(__import__('numpy').load(os.path.join(d, f))['idx']) for f in fs if f.startswith('shapes_e') and f.endswith('.npz'))
        nf = sum(len(__import__('numpy').load(os.path.join(d, f))['idx']) for f in fs if f.startswith('fem_') and f.endswith('.npz'))
        na = sum(len(__import__('numpy').load(os.path.join(d, f))['idx']) for f in fs if f.startswith('femal') and f.endswith('.npz'))
        print(f'{g:14s} {ns:7d} {ne:6d} {nf:6d} {na:12d}')


def report(run):
    import torch
    print('== DeepSDF (목표 제안: IoU_val >= 0.90, 표면오차 <= 0.5칸) ==')
    sd = os.path.join(run, 'sdf')
    for g in sorted(os.listdir(sd)) if os.path.isdir(sd) else []:
        ck = os.path.join(sd, g, 'ckpt.pt')
        if os.path.exists(ck):
            c = torch.load(ck, map_location='cpu', weights_only=False)
            h = c['hist'][-1] if c['hist'] else {}
            print(f"  {g:13s} step {c['step']:6d}  cfg {c.get('cfg')}  " + '  '.join(f'{k} {v:.3f}' for k, v in h.items() if k.startswith(('iou', 'surf'))))
    sf = os.path.join(run, 'state.json')
    if not os.path.exists(sf):
        print('state.json 없음'); return
    st = json.load(open(sf))
    for kind, d in st.get('sweep', {}).items():
        print(f'== 학습 방법 고르기 ({kind}) — 검증 점수, 작을수록 좋음 ==')
        for u, v in d.items():
            print(f"  {u:13s} 선택 {v.get('chosen', '-'):12s} 1차 {json.dumps({k: round(a, 3) for k, a in v.get('screen', {}).items()})}")
    for g, m in st.get('sdf_test', {}).items():
        if g == list(st['sdf_test'])[0]:
            print('== DeepSDF 시험 셋 (고르는 데 안 쓴 10%) ==')
        print(f"  {g:13s} IoU {m['iou_test']:.3f} (하위10% {m['iou_test_p10']:.3f})  표면오차 {m['surf_err_mm_test']:.3f} mm = {m['surf_err_cell_test']:.2f}칸")
    print('== 단계 ==')
    for k, v in st.get('stages', {}).items():
        print(f"  {k:24s} {'완료' if v.get('done') else '-'} {v.get('at', '')}")
    print('== PINO 품질 관문 (시험 셋, fp08/loop.py GATE) ==')
    for r, res in st.get('gate', {}).items():
        for g, v in res.items():
            print(f"  {r} {g:13s} {'합격' if v['passed'] else '불합격: ' + ', '.join(v['why'])}")
    print('== 시연 ==')
    for r, res in st.get('demo', {}).items():
        for g, L in res.items():
            for d in L:
                print(f"  {r} {g:13s} {d['cond']} {d['status']} 질량 {(d['best'] or {}).get('mass_g', '-')}")


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit(0)
    if a[0] == 'code':
        pack_code(a[1])
    elif a[0] in ('data', 'runs'):
        pack_dir(a[1], a[2])
    elif a[0] == 'unpack':
        unpack(a[1], a[2] if len(a) > 2 else '.')
    elif a[0] == 'report':
        report(a[1])
    elif a[0] == 'check':
        check(a[1])
    else:
        print(__doc__)
