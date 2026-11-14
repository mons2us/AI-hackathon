"""학습 방법 여러 개 → 최선 자동 선택 (sweep)

흐름 (모델마다: DeepSDF 는 그룹 6개, PINO 는 제품 3개)
  1) 1차 거르기: 후보 4개를 전체 스텝의 SCREEN_FRAC(20%)까지만 학습 (학습률 일정은 전체 스텝 기준 → 나중에 그대로 이어감)
  2) 검증 셋 점수로 상위 top-k 만 끝까지 이어서 학습
  3) 검증 점수가 가장 좋은 것을 '정식 모델' 위치(runs/main/sdf/<그룹>/, runs/main/pino/<제품>/)로 복사
     → 그 뒤 단계(관문·능동학습·시연)는 sweep 이 없을 때와 똑같이 동작
  4) 최종 성적은 고르는 데 쓰지 않은 '시험 셋'(10%)으로 따로 계산해 state.json·report.html 에 기록 (선택 편향 방지)

후보를 바꾸려면 아래 SDF_CANDS / PINO_CANDS 만 고치면 됨 (이름은 폴더 이름으로 쓰임).
"""
import os, shutil, json
import numpy as np

SCREEN_FRAC = 0.2

# DeepSDF: 11-14 비교에서 8층×256 이 4층×128 보다 좋았음(IoU 0.73 vs 0.70) → 기준으로 두고 크기·점 수·학습률을 흔듦
SDF_CANDS = {
    'base_8x256':  dict(width=256, depth=8, npts=1024, lr=5e-4, zdim=32),
    'wide_8x512':  dict(width=512, depth=8, npts=1024, lr=5e-4, zdim=32),
    'pts2048':     dict(width=256, depth=8, npts=2048, lr=5e-4, zdim=32),
    'z64':         dict(width=256, depth=8, npts=1024, lr=5e-4, zdim=64),   # 번호표 z 를 32 → 64차원 (형상 수가 많아 32로 모자랄 때)
}
# PINO: 폭, 푸리에 모드 수, 물리 손실 가중치
PINO_CANDS = {
    'base_w24':    dict(width=24, modes_scale=1.0, w_phys=0.1),
    'wide_w32':    dict(width=32, modes_scale=1.0, w_phys=0.1),
    'phys0.3':     dict(width=24, modes_scale=1.0, w_phys=0.3),
    'modes1.5':    dict(width=24, modes_scale=1.5, w_phys=0.1),
}


def sdf_args(c):
    return ['--width', str(c['width']), '--depth', str(c['depth']), '--npts', str(c['npts']), '--lr', str(c['lr']),
            '--zdim', str(c.get('zdim', 32))]


def pino_args(c):
    return ['--width', str(c['width']), '--modes-scale', str(c['modes_scale']), '--w-phys', str(c['w_phys'])]


def sdf_score(hist):
    """작을수록 좋음: −IoU_val (+ 표면 오차 칸 단위 × 0.05 를 동점 깨기로). 마지막 평가 기준"""
    if not hist or 'iou_val' not in hist[-1]:
        return float('inf')
    h = hist[-1]
    return -h['iou_val'] + 0.05 * h.get('surf_err_mm', 0) / 2.0


def pino_score(hist, stress_keys=('vm', 'interlayer')):
    """작을수록 좋음: 그룹 평균 [변위장 L2 + 판정값 오차 p90 평균(응력은 /3, 관문 기준이 15% vs 5% 라서) + (1 − 진동수 ±5% 비율)]"""
    if not hist:
        return float('inf')
    sc = []
    for g, m in hist[-1]['val'].items():
        s = m['relL2_mean'] if m.get('relL2_mean') is not None else 10.0
        j = [v / 3 if q in stress_keys else v for q, v in m.get('judge_abs_p90', {}).items()
             if q not in ('mass_g', 'tip_margin_fb', 'tip_margin_lat')]
        s += float(np.mean(j)) if j else 0.0
        if 'freq_within5_frac' in m:
            s += 1 - m['freq_within5_frac']
        sc.append(s)
    return float(np.mean(sc))


def pick(scores, k):
    """scores: {이름: 점수} → 점수 작은 순 상위 k 개 이름 (inf 제외, 최소 1개)"""
    ok = sorted((v, n) for n, v in scores.items() if np.isfinite(v))
    return [n for _, n in ok[:max(1, k)]] or list(scores)[:1]


def promote(src_dir, dst_dir):
    """고른 후보의 체크포인트를 정식 위치로 복사 (덮어씀)"""
    os.makedirs(dst_dir, exist_ok=True)
    shutil.copy2(os.path.join(src_dir, 'ckpt.pt'), os.path.join(dst_dir, 'ckpt.pt.tmp'))
    os.replace(os.path.join(dst_dir, 'ckpt.pt.tmp'), os.path.join(dst_dir, 'ckpt.pt'))
    with open(os.path.join(dst_dir, 'chosen.json'), 'w', encoding='utf-8') as f:
        json.dump(dict(from_=src_dir), f)
