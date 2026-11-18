"""입력 단계(10_입력_1차설계)의 '화면 각도 자유(free_angle)' 금지 공간(keepout)을 08 격자 마스크로 저장.

폰이 360° 회전 + 기울기 −30~+60° 로 지나가는 공간(+3 mm 여유) = 거치대 재료가 있으면 안 되는 칸.
사용: python experiments/make_keepout.py <10_입력_1차설계 폴더> [템플릿 ID=T01] [08 그룹=bike_pad80_free] [폰 기둥 높이 mm=60] [설계 영역 아래 끝 z mm=없음]
결과: fp08/assets/keepout_<그룹>.npz (mask: 요소별 bool, 08 격자 순서) — 10 코드를 08 실행 때 부르지 않도록 미리 저장
검사: 10 의 요소 라벨이 08 그룹과 완전히 같을 때만 저장 (격자·순서가 같다는 확인)
"""
import os, sys, json, subprocess
import numpy as np

src = os.path.abspath(sys.argv[1])
tid = sys.argv[2] if len(sys.argv) > 2 else 'T01'
grp = sys.argv[3] if len(sys.argv) > 3 else 'bike_pad80_free'
post_h = float(sys.argv[4]) if len(sys.argv) > 4 else 60.0
zmin = float(sys.argv[5]) if len(sys.argv) > 5 else None
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, src); sys.path.insert(0, ROOT)
from formproof_input.templates import bike_mount, library
from formproof_input.compile import Problem as P10
from fp08 import problems

params = dict(library.BY_ID[tid]['params'], requirements=('free_angle',), domain_z_min=zmin, post_h=post_h)
spec = bike_mount.build_spec(params, tid)
P = P10(spec)
p = problems.BikeMount(float(params['pad_x0']), float(params['pad_z0']), z_min=zmin, post_h=post_h)
lab10 = np.asarray(P.label)
assert lab10.shape == p.label.shape and (lab10 == p.label).all(), '10 과 08 의 격자·라벨이 다름 → 저장 안 함'
k = np.asarray(P.keepout, bool)
clash = int((k & np.isin(p.label, [1, 3])).sum())
ko = [c for c in spec['constraints'] if c.get('requirement') == 'free_angle']
rev = os.environ.get('SRC_REV')
try:
    rev = rev or subprocess.check_output(['git', '-C', src, 'log', '-1', '--format=%h %ad', '--date=short'], text=True).strip()
except Exception:
    rev = 'unknown'
meta = dict(source='10_입력_1차설계 formproof_input.templates.bike_mount (free_angle keepout "phone_sweep")', rev=rev,
            template=tid, params={k_: params[k_] for k_ in ('pad_x0', 'pad_z0', 'arm', 'domain_z_min', 'post_h')},
            tilt_deg=list(bike_mount.DEFAULT['angle_tilt']), rotate_deg=360, margin_mm=bike_mount.DEFAULT['angle_margin'],
            n_keepout=int(k.sum()), n_keepout_design=int((k & (p.label == 0)).sum()), n_design=int((p.label == 0).sum()),
            clash_fixed=clash, constraints=ko)
out = os.path.join(ROOT, 'fp08', 'assets', f'keepout_{grp}.npz')
np.savez_compressed(out, mask=np.packbits(k), n=len(k), meta=json.dumps(meta, ensure_ascii=False))
print(json.dumps({k_: v for k_, v in meta.items() if k_ != 'constraints'}, ensure_ascii=False))
print('저장', out)
