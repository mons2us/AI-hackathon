"""문제 정의 3종 — 07 problem.npz 형식을 확장한 공통 형식.

공통 요소 라벨: 0 설계 영역 / 1 고정부품(항상 재료) / 2 빈 곳 / 3 강체
추가 항목(설계 결정 2번): 고정부 덩어리 구분(fixed_groups), 물리 모듈(physics),
바뀌는 조건(conditions), 판정 기준과 계산 방법(criteria, evaluate()).

단위: mm, t(톤), N, MPa, s.  1 kg = 1e-3 t,  g = 9810 mm/s^2
출처
- 거치대: 07 templates/bike_mount.py, 03 code_3D/opt3d.py (영역·지지·질량 절점·하중 정의를 그대로 옮김)
- TV 양발형: 04 plate_v2/plate.py (체결 블록·발 패드·하중 3종·처짐 측정 방식) 를 3D 다리로 확장
- TV 중앙형: 04 pedestal/ped.py (TV 블록 강체 x100·패드·하중·측정 방식), 설계 영역은 목+바닥 전체(5 mm)
"""
import json
import numpy as np
from scipy import ndimage
from . import fem

G = 9810.0


def _snap(v, h, mode='near'):
    q = v / h
    if mode == 'down':
        return h * np.floor(q + 1e-9)
    if mode == 'up':
        return h * np.ceil(q - 1e-9)
    return h * np.round(q)


class Problem:
    """격자·라벨·지지·대칭·하중·질량·판정 기준을 담는 공통 문제 객체."""
    product = ''
    material = {}
    physics = ('static',)
    modes = None            # {'S': k, 'A': k}
    sym_axis = None         # 0:x 1:y 2:z — 대칭면 법선 방향
    k_rigid = 20.0
    EMIN = 1e-6

    def finalize(self):
        g = self.grid
        lab = self.label
        self.design = lab == 0
        self.active = lab != 2
        used = np.zeros(g.nn, bool)
        used[g.en[self.active].ravel()] = True
        self.used = used
        fixed = (lab == 1) | (lab == 3)
        comp, n = ndimage.label(g.eshape(fixed))
        self.fixed_comp = comp.ravel()          # 0 = 아님, 1..n = 고정부 덩어리 번호
        self.n_fixed = n
        mat = self.material
        self.KE, self.C, self.B0 = fem.hex8_KB(mat['E'], mat['nu'], g.h)
        self.me0 = mat['rho'] * g.h ** 3
        self.supports = np.where(used & self.support_nodes())[0]
        self.plane = np.where(used & self.plane_nodes())[0] if self.sym_axis is not None else np.array([], int)
        self.free = {bc: self._free(bc) for bc in ('S', 'A')}

    def _free(self, bc):
        s = self.supports
        fd = [3 * s, 3 * s + 1, 3 * s + 2]
        if self.sym_axis is not None:
            a = self.sym_axis
            if bc == 'S':
                fd.append(3 * self.plane + a)                       # 면을 가로지르는 변위 = 0
            else:
                fd += [3 * self.plane + b for b in range(3) if b != a]   # 면을 따라 미끄러지는 변위 = 0
        fd = np.unique(np.concatenate(fd))
        dof = np.where(np.repeat(self.used, 3))[0]
        return np.setdiff1d(dof, fd)

    # ----- 형상 → 강성·질량 배율
    def kscale(self, occ_design):
        """occ_design: (ne,) bool/0~1, 설계 영역에서만 의미. SIMP p=3, EMIN."""
        lab = self.label
        k = np.zeros(self.grid.ne)
        r = np.asarray(occ_design, float)
        k[lab == 0] = self.EMIN + (1 - self.EMIN) * r[lab == 0] ** 3
        k[lab == 1] = 1.0
        k[lab == 3] = self.k_rigid
        return k

    def emass(self, occ_design):
        lab = self.label
        m = np.zeros(self.grid.ne)
        r = np.asarray(occ_design, float)
        m[lab == 0] = r[lab == 0]
        m[lab == 1] = 1.0
        return m * self.me0

    def mass_g(self, occ_design):
        """전체 모델(대칭 복원) 질량 g — 강체 제외"""
        f = 2 if self.sym_axis is not None else 1
        return float(self.emass(occ_design).sum() * f * 1e6)

    # ----- 하위 클래스가 정의
    def support_nodes(self): raise NotImplementedError
    def plane_nodes(self): raise NotImplementedError
    def node_mass(self, cond): return np.zeros(self.grid.nn)
    def basis(self, cond): raise NotImplementedError       # [(name, bc, F(3nn,))]
    def evaluate(self, res, cond): raise NotImplementedError
    def sample_cond(self, rng): return dict(self.default_cond)

    def spec(self):
        """spec.json 형태 (설계 결정 2번: 07 형식 + 4가지 추가)"""
        g = self.grid
        return dict(schema='formproof.spec/0.2-08', product=self.product, group=self.name,
                    grid=dict(h=g.h, origin=g.origin.tolist(), shape=[g.nx, g.ny, g.nz],
                              symmetry=None if self.sym_axis is None else dict(axis='xyz'[self.sym_axis], cases=['S', 'A'])),
                    material=self.material, physics=list(self.physics), modes=self.modes,
                    fixed_groups=int(self.n_fixed), conditions=self.conditions, criteria=self.criteria,
                    elements=dict(design=int((self.label == 0).sum()), solid=int((self.label == 1).sum()),
                                  void=int((self.label == 2).sum()), rigid=int((self.label == 3).sum())),
                    assumptions=self.assumptions)

    def save_npz(self, path):
        g = self.grid
        np.savez_compressed(path, h=g.h, origin=g.origin, shape=np.array([g.nx, g.ny, g.nz]), label=self.label,
                            fixed_comp=self.fixed_comp, supports=self.supports, plane=self.plane,
                            sym_axis=-1 if self.sym_axis is None else self.sym_axis, used_nodes=np.where(self.used)[0])


# =====================================================================================
class BikeMount(Problem):
    """자전거 폰 거치대 — 받침 위치(pad_x0, pad_z0)별 형상 그룹. 절반 모델(y>=55), 대칭면 y=55."""
    product = 'bike_mount'
    physics = ('static', 'modal')
    modes = {'S': 2, 'A': 2}
    sym_axis = 1
    k_rigid = 20.0
    material = dict(name='PETG', E=1700.0, nu=0.38, rho=1.27e-9, yield_mpa=39.0, interlayer_mpa=16.4,
                    source='Prusament PETG TDS (팀 v7)')

    def __init__(self, pad_x0=80.0, pad_z0=16.0, h=2.0):
        self.name = f'bike_pad{int(pad_x0)}_{int(pad_z0)}'
        Y = 55.0
        bore, ro = 16.1, 20.6
        yw, ypost = Y + 10.0, Y + 6.0
        x0 = _snap(-(ro + 2.0), h, 'down')
        ear_top = _snap(-bore + 2.0, h)
        ear_bot = ear_top - 20.0
        z0 = _snap(min(ear_bot, -ro) - 2.0, h, 'down')
        px0, px1 = _snap(pad_x0, h), _snap(pad_x0 + 20.0, h)
        pz0, pz1 = _snap(pad_z0, h), _snap(pad_z0 + 4.0, h)
        qx0, qx1 = _snap(px0 + 6.0, h), _snap(px0 + 16.0, h)
        z_above = max(pz1 + 4.0, _snap(ro + 2.0, h, 'up'))
        z_top = max(_snap(pz1 + 22.0, h), z_above + 2 * h)
        nx = int(round((px1 - x0) / h)); ny = 10; nz = int(round((z_top - z0) / h))
        g = self.grid = fem.Grid((nx, ny, nz), h, (x0, Y, z0))
        xc, yc, zc = g.xc, g.yc, g.zc
        rr = np.sqrt(xc ** 2 + zc ** 2)
        bore_m = rr < bore
        contact = (rr >= bore) & (rr < ro) & (yc < yw)
        slit = (np.abs(xc) <= 1) & (zc < 0) & (rr < ro + 5.4)
        ears = (np.abs(xc) > 1) & (np.abs(xc) < 9) & (zc > ear_bot) & (zc < ear_top) & (yc < yw)
        pad = (xc > px0) & (xc < px1) & (zc > pz0) & (zc < pz1) & (yc < yw)
        post = (xc > qx0) & (xc < qx1) & (zc > pz1) & (yc < ypost)
        holder = (xc > px0 - 2.0) & (zc > pz1) & ~post
        above = (zc > z_above) & ~post
        void = bore_m | slit | holder | above
        lab = np.zeros(g.ne, np.int8)
        lab[(contact | ears | pad) & ~void] = 1
        lab[post & ~void] = 3
        lab[void] = 2
        self.label = lab
        self._geo = dict(bore=bore, qx=(qx0, qx1), ypost=ypost, z_top=z_top)
        self.conditions = dict(
            shape_group=dict(pad_x0=pad_x0, pad_z0=pad_z0),
            model_input=dict(phone_mass_g=[160.0, 220.0], phone_angle_deg=[0.0, 15.0]),
            formula=dict(peak_g=48.5, road_hz=[34.6, 45.6]))
        self.default_cond = dict(phone_mass_g=200.0, phone_angle_deg=0.0)
        self.criteria = [
            dict(id='f_min', quantity='S·A 모드 4개 중 최저 고유진동수 [Hz]', op='>=', value=91.2,
                 how='FEM 고유값 (S 2개 + A 2개)', source='ISBS 2020 자갈길 45.6 Hz, 전달률 ≤ 4/3 → 45.6/√(1-3/4)'),
            dict(id='vm', quantity='충격 시 폰 미세스 응력 상위 0.5% [MPa]', op='<=', value=26.0,
                 how='위아래·옆 48.5 g 충격(공식 환산), 재료 칸, 클램프 안쪽(r<19 mm) 제외', source='항복 39 / 안전율 1.5'),
            dict(id='interlayer', quantity='적층 방향(y) 인장 수직응력 상위 0.5% [MPa]', op='<=', value=10.9,
                 how='위아래·옆 충격', source='층간 16.4 / 1.5, 옆으로 눕혀 출력 가정'),
            dict(id='mass', quantity='질량 [g]', op='min', how='재료 칸 수 × 밀도 (대칭 복원)')]
        self.assumptions = ['클램프 내면 핸들바 완전 고정', '폰 + 홀더 질량은 폰 기둥 꼭대기 집중(홀더 50 g)',
                            '폰 각도는 기둥 꼭대기 질량 무게중심을 앞뒤로 이동(22 mm × sinθ, 기둥 폭 안으로 제한)',
                            '앞뒤(x) 방향 충격 미포함', '거치대 자체 관성 미포함(팀 v7과 동일)']
        self.finalize()
        gx, gz = g.nxc, g.nzc
        q0, q1 = self._geo['qx']
        self.mass_nodes = np.where(self.used & (g.gk == g.nz) & (gx >= q0) & (gx <= q1)
                                   & (g.nyc <= ypost + 1e-6))[0]

    def support_nodes(self):
        g = self.grid
        return np.sqrt(g.nxc ** 2 + g.nzc ** 2) <= self._geo['bore'] + 0.6

    def plane_nodes(self):
        return self.grid.gj == 0

    def node_mass(self, cond):
        g = self.grid
        mn = self.mass_nodes
        w = np.where(g.nyc[mn] == g.origin[1], 0.5, 1.0)
        x = g.nxc[mn]
        xc = (w * x).sum() / w.sum()
        var = (w * (x - xc) ** 2).sum() / w.sum()
        half_range = 0.45 * (x.max() - x.min())
        dx = -22.0 * np.sin(np.radians(cond.get('phone_angle_deg', 0.0)))
        dx = float(np.clip(dx, -half_range, half_range))
        w = w * (1 + dx * (x - xc) / var)
        w = np.maximum(w, 0)
        MP = (cond.get('phone_mass_g', 200.0) + 50.0) * 1e-6       # t, 폰 + 홀더
        m = np.zeros(g.nn)
        m[mn] = MP / 2 * w / w.sum()                                  # 절반 모델
        return m

    def basis(self, cond):
        """단위 가속도(1 g) 관성 하중: 위아래(S), 옆(A). 실제 충격 = × peak_g (공식 환산)"""
        m = self.node_mass(cond)
        F1 = np.zeros(3 * self.grid.nn); F1[2::3] = -m * G
        F2 = np.zeros(3 * self.grid.nn); F2[1::3] = m * G
        return [('shock_z', 'S', F1), ('shock_y', 'A', F2)]

    def evaluate(self, res, cond, occ_design=None):
        """res: labels.fem_label() 결과. 판정값 계산."""
        g = self.grid
        pk = self.conditions['formula']['peak_g']
        on = (self.label == 1) | ((self.label == 0) & (np.asarray(res['occ']) > 0.5))
        rr = np.sqrt(g.xc ** 2 + g.zc ** 2)
        ok = on & (rr > 19.0)
        vm, syy = [], []
        for name in ('shock_z', 'shock_y'):
            u = res['U'][name] * pk
            s = fem.element_stress(g, self.C, self.B0, u)
            vm.append(np.percentile(fem.von_mises(s)[ok], 99.5) if ok.any() else np.inf)
            syy.append(np.percentile(np.maximum(s[ok, 1], 0), 99.5) if ok.any() else np.inf)
        f = np.concatenate([res['freq']['S'], res['freq']['A']])
        out = dict(f=f.tolist(), f_min=float(f.min()), vm=float(max(vm)), interlayer=float(max(syy)),
                   mass_g=self.mass_g(res['occ']))
        out['pass'] = bool(out['f_min'] >= 91.2 and out['vm'] <= 26.0 and out['interlayer'] <= 10.9)
        return out


# =====================================================================================
class _TVBase(Problem):
    product = 'tv_stand'
    physics = ('static',)
    sym_axis = 0                    # 대칭면 x = 0
    material = dict(name='Al 6061-T6', E=68900.0, nu=0.33, rho=2.7e-9, yield_mpa=276.0,
                    source='E·ν·밀도 = 팀 plate.py/ped.py, 항복 276 MPa = 일반 공칭값(확인 필요)')
    TV = dict(mass_kg=20.8, size='65"', top_above_bottom_mm=832.0, cg_above_bottom_mm=416.0)

    def basis(self, cond=None):
        """기본 하중 5가지 — 전체 구조에 단위 하중(1 N, 1 N·mm)이 걸릴 때 (절반 모델에는 절반)."""
        g = self.grid
        n = self.load_nodes
        w = np.where(g.nxc[n] == 0.0, 0.5, 1.0); w = w / w.sum()
        F = []
        def vec():
            return np.zeros(3 * g.nn)
        f = vec(); f[3 * n + 2] = -0.5 * w; F.append(('Fz', 'S', f))
        f = vec(); f[3 * n + 1] = 0.5 * w; F.append(('Fy', 'S', f))
        d = g.nyc[n] - (w * g.nyc[n]).sum()
        f = vec(); f[3 * n + 2] = -0.5 * w * d / (w * d ** 2).sum(); F.append(('Mx', 'S', f))
        f = vec(); f[3 * n + 0] = 0.5 * w; F.append(('Fx', 'A', f))
        d = g.nxc[n]
        if (w * d ** 2).sum() > 0:
            f = vec(); f[3 * n + 2] = -0.5 * w * d / (w * d ** 2).sum(); F.append(('My', 'A', f))
        return F

    def _tip(self, u, axis_coord, hor):
        g = self.grid
        n = self.load_nodes
        w = np.where(g.nxc[n] == 0.0, 0.5, 1.0); w = w / w.sum()
        d = axis_coord[n] - (w * axis_coord[n]).sum()
        den = (w * d ** 2).sum()
        th = -((u[3 * n + 2] * w * d).sum() / den) if den > 0 else 0.0
        return float(u[3 * n + hor] @ w + th * self.lever)

    def pad_min_N(self, res, coef, with_gravity):
        """하중 조합의 발 패드별 수직 반력 중 최솟값 [N] (전체 구조 기준).
        S 성분은 거울쪽도 같고, A 성분은 거울쪽이 반대 부호 → 최솟값 = R_S - |R_A|. 음수면 패드가 들림(인장)."""
        bcs = {n: bc for n, bc, _ in self.basis()}
        coef = dict(coef)
        if with_gravity:
            for b, c in self.loads_cache['gravity'].items():
                coef[b] = coef.get(b, 0) + c
        g = self.grid
        uS = sum((c * res['U'][b] for b, c in coef.items() if bcs.get(b) == 'S'), np.zeros(3 * g.nn))
        uA = sum((c * res['U'][b] for b, c in coef.items() if bcs.get(b) == 'A'), np.zeros(3 * g.nn))
        RS = np.array(self.reactions_z(res, uS)) * 2
        RA = np.array(self.reactions_z(res, uA)) * 2
        return float((RS - np.abs(RA)).min())

    def reactions_z(self, res, u):
        """발 패드 지지 절점의 수직 반력 합 (덩어리별). 양수 = 책상을 누름, 음수 = 잡아당김(들림)."""
        g = self.grid
        K = res['_K']
        r = K @ u
        rz = r[3 * self.supports + 2]
        comp = self.support_comp
        return [float(rz[comp == c].sum()) for c in np.unique(comp)]


class TVFeet(_TVBase):
    """TV 양발형 — 다리 하나. 앞뒤 발끝 길이 L(형상 그룹). x = 두께(절반, 대칭면 x=0), y = 앞뒤, z = 위."""

    def __init__(self, L=300.0, h=2.5, half_thick=20.0, H=120.0, span=1200.0):
        self.name = f'tvfeet_L{int(L)}'
        self.span = span
        nx, ny, nz = int(round(half_thick / h)), int(round(L / h)), int(round(H / h))
        g = self.grid = fem.Grid((nx, ny, nz), h, (0.0, -L / 2, 0.0))
        xc, yc, zc = g.xc, g.yc, g.zc
        attach = (np.abs(yc) <= 20.0) & (zc >= H - 12.0) & (xc <= 10.0)
        top = zc >= H - 12.0
        pads = (zc <= 6.0) & (np.abs(np.abs(yc) - (L / 2 - 20.0)) <= 20.0)
        lab = np.zeros(g.ne, np.int8)
        lab[top & ~attach] = 2
        lab[attach | pads] = 1
        self.label = lab
        self.H = H
        self.lever = self.TV['top_above_bottom_mm']
        self.conditions = dict(shape_group=dict(foot_length_mm=L),
                               model_input={},
                               formula=dict(tv_mass_kg=[10.0, 35.0], leg_span_mm=[800.0, 1400.0],
                                            push_ratio=0.13, tv_top_above_bottom_mm=832.0))
        self.default_cond = dict(tv_mass_kg=20.8, leg_span_mm=span)
        self.criteria = [
            dict(id='sag', quantity='자중 처짐: 체결부 평균 수직 변위 [mm]', op='<=', value=0.10,
                 how='Fz = W/2 (다리 하나)', source='팀 plate.py 기본값 SAG=0.10 (README 1 mm와 불일치, 확인 필요)'),
            dict(id='utop_fb', quantity='앞뒤 13% 밀기 시 TV 위쪽 변위 [mm]', op='<=', value=1.0,
                 how='체결부 변위 + 회전 × 832 mm', source='팀 plate.py 기본값 UTOP=1.0 (확인 필요)'),
            dict(id='sag_lat', quantity='옆 밀기 시 반대쪽 다리 처짐 [mm]', op='<=', value=0.15,
                 how='Fz 추가 = F13·ZT/간격, + 옆 힘 F13/2', source='팀 plate.py: SAG×1.5'),
            dict(id='vm', quantity='응력 상위 0.5% [MPa]', op='<=', value=184.0, how='세 하중 경우 최대',
                 source='항복 276 / 1.5 (가정)'),
            dict(id='tip', quantity='넘어짐 여유(앞뒤)', op='>=', value=1.0, how='해석식 (L/2)/(0.13×TV 위쪽 높이)', source='IEC 62368-1 8.6 (13%·미끄럼 없음)'),
            dict(id='uplift', quantity='발 패드 최소 반력 [N]', op='info', how='자중+밀기, 음수면 패드 들림 경고(고정 가정 깨짐)'),
            dict(id='mass', quantity='질량 [g]', op='min', how='다리 하나, 대칭 복원')]
        self.assumptions = ['바닥은 미끄러지지 않음(IEC 62368-1 시험 조건)', '발 패드 바닥 완전 고정(들림은 반력으로 별도 판정)',
                            '옆 밀기의 전도 모멘트는 두 다리의 수직력으로 전달(plate.py와 동일)', 'TV 위쪽 높이 832 mm(65")']
        self.finalize()
        self.load_nodes = np.where(self.used & (g.gk == g.nz) & (np.abs(g.nyc) <= 20.0) & (g.nxc <= 10.0))[0]
        s = self.supports
        self.support_comp = np.sign(g.nyc[s]).astype(int)

    def support_nodes(self):
        g = self.grid
        L = g.ny * g.h
        return (g.gk == 0) & (np.abs(np.abs(g.nyc) - (L / 2 - 20.0)) <= 20.0 + 1e-6)

    def plane_nodes(self):
        return self.grid.gi == 0

    def loads(self, cond):
        """공식 환산: 기본 하중 5가지의 계수 (하중 경우별)."""
        mt = cond.get('tv_mass_kg', 20.8)
        W = (mt + 1.2) * 9.81                    # N, TV + 다리 2개(1.2 kg, plate.py 가정)
        F13 = 0.13 * W
        span = cond.get('leg_span_mm', self.span)
        ZT = self.TV['top_above_bottom_mm'] + self.H
        return dict(gravity=dict(Fz=W / 2),
                    push_fb=dict(Fy=F13 / 2, Mx=F13 / 2 * self.lever),
                    push_lat=dict(Fx=F13 / 2, Fz=W / 2 + F13 * ZT / span))

    def evaluate(self, res, cond, occ_design=None):
        g = self.grid
        U = {k: v for k, v in res['U'].items()}
        L = self.loads(cond)
        comb = {}
        for case, coef in L.items():
            u = np.zeros(3 * g.nn)
            for b, c in coef.items():
                if b in U:
                    u += c * U[b]
            comb[case] = u
        n = self.load_nodes
        w = np.where(g.nxc[n] == 0.0, 0.5, 1.0); w = w / w.sum()
        sag = float(-(comb['gravity'][3 * n + 2] @ w))
        ufb = self._tip(comb['push_fb'], g.nyc, 1)
        slat = float(-(comb['push_lat'][3 * n + 2] @ w))
        on = (self.label == 1) | ((self.label == 0) & (np.asarray(res['occ']) > 0.5))
        vm = max(np.percentile(fem.von_mises(fem.element_stress(g, self.C, self.B0, u))[on], 99.5) for u in comb.values())
        self.loads_cache = self.loads(cond)
        pad = {case: self.pad_min_N(res, coef, case != 'gravity') for case, coef in self.loads_cache.items()} \
            if '_K' in res else {}      # 밀기는 자중과 함께 작용
        ZT = self.TV['top_above_bottom_mm'] + self.H
        Ltot = g.ny * g.h
        tip_fb = (Ltot / 2) / (0.13 * ZT)   # 넘어짐 여유(앞뒤): 무게×(L/2) ÷ (13%무게×TV 위쪽 높이), ≥1 이면 안 넘어짐
        out = dict(sag=sag, utop_fb=ufb, sag_lat=slat, vm=float(vm), pad_min_N=pad, tip_margin_fb=float(tip_fb),
                   mass_g=self.mass_g(res['occ']))
        out['uplift'] = bool(pad and min(pad.values()) < 0)        # 경고: 고정 패드 가정이 깨짐(정보용)
        out['pass'] = bool(sag <= 0.10 and ufb <= 1.0 and slat <= 0.15 and vm <= 184.0 and tip_fb >= 1.0)
        return out


class TVPedestal(_TVBase):
    """TV 중앙형 — 목 + 바닥 전체를 설계. 절반 모델 x>=0 (대칭면 x=0), 5 mm 격자."""
    k_rigid = 100.0          # ped.py: TV 바닥 블록 강성 ×100

    def __init__(self, h=5.0, BX=200.0, BY=150.0, ZN=80.0):
        self.name = 'tvped'
        nx, ny, nz = int(round(BX / h)), int(round(2 * BY / h)), int(round((ZN + 20.0) / h))
        g = self.grid = fem.Grid((nx, ny, nz), h, (0.0, -BY, 0.0))
        xc, yc, zc = g.xc, g.yc, g.zc
        tvb = (zc >= ZN) & (xc < 150.0) & (np.abs(yc) < 15.0)
        pads = (zc < 10.0) & (xc >= BX - 30.0) & (np.abs(yc) >= BY - 30.0)
        lab = np.zeros(g.ne, np.int8)
        lab[zc >= ZN] = 2
        lab[tvb] = 3
        lab[pads] = 1
        self.label = lab
        self.ZN, self.BX, self.BY = ZN, BX, BY
        self.lever = self.TV['top_above_bottom_mm']
        self.conditions = dict(shape_group=dict(base_mm=[2 * BX, 2 * BY], neck_top_mm=ZN), model_input={},
                               formula=dict(tv_mass_kg=[10.0, 35.0], push_ratio=0.13, tv_top_above_bottom_mm=832.0))
        self.default_cond = dict(tv_mass_kg=20.8)
        self.criteria = [
            dict(id='sag', quantity='자중 처짐: TV 블록 평균 수직 변위 [mm]', op='<=', value=0.10, how='Fz = W',
                 source='팀 ped.py 기본값 SAG=0.1 (확인 필요)'),
            dict(id='utop_fb', quantity='앞뒤 13% 밀기 시 TV 위쪽 변위 [mm]', op='<=', value=1.0,
                 how='변위 + 회전 × 832 mm', source='팀 ped.py UTOP=1.0 (확인 필요)'),
            dict(id='utop_lat', quantity='옆 13% 밀기 시 TV 위쪽 변위 [mm]', op='<=', value=1.0, how='동일',
                 source='팀 ped.py'),
            dict(id='vm', quantity='응력 상위 0.5% [MPa]', op='<=', value=184.0, how='세 하중 경우 최대',
                 source='항복 276 / 1.5 (가정)'),
            dict(id='tip', quantity='넘어짐 여유(앞뒤·좌우)', op='>=', value=1.0, how='해석식', source='IEC 62368-1 8.6'),
            dict(id='uplift', quantity='패드 최소 반력 [N]', op='info', how='자중+밀기, 음수면 들림 경고'),
            dict(id='mass', quantity='질량 [g]', op='min', how='대칭 복원, TV 블록 제외')]
        self.assumptions = ['바닥은 미끄러지지 않음(IEC 62368-1 시험 조건)', '패드 바닥 완전 고정(들림은 반력으로 판정)',
                            'TV 바닥 블록은 강체(×100, ped.py와 동일)', '목 위쪽(z≥80) TV 블록 밖은 빈 곳', '5 mm 격자(최소 부재 10 mm)']
        self.finalize()
        tvn = np.unique(g.en[lab == 3].ravel())
        self.load_nodes = tvn[self.used[tvn]]
        s = self.supports
        self.support_comp = np.sign(g.nyc[s]).astype(int)

    def support_nodes(self):
        g = self.grid
        return (g.gk == 0) & (g.nxc >= self.BX - 30.0 - 1e-6) & (np.abs(g.nyc) >= self.BY - 30.0 - 1e-6)

    def plane_nodes(self):
        return self.grid.gi == 0

    def loads(self, cond):
        mt = cond.get('tv_mass_kg', 20.8)
        W = (mt + 3.0) * 9.81                    # ped.py: 받침대 3 kg 가정
        F13 = 0.13 * W
        return dict(gravity=dict(Fz=W), push_fb=dict(Fy=F13, Mx=F13 * self.lever),
                    push_lat=dict(Fx=F13, My=F13 * self.lever))

    def evaluate(self, res, cond, occ_design=None):
        g = self.grid
        U = res['U']
        comb = {}
        for case, coef in self.loads(cond).items():
            u = np.zeros(3 * g.nn)
            for b, c in coef.items():
                if b in U:
                    u += c * U[b]
            comb[case] = u
        n = self.load_nodes
        w = np.where(g.nxc[n] == 0.0, 0.5, 1.0); w = w / w.sum()
        sag = float(-(comb['gravity'][3 * n + 2] @ w))
        ufb = self._tip(comb['push_fb'], g.nyc, 1)
        ulat = self._tip(comb['push_lat'], g.nxc, 0)
        on = (self.label == 1) | ((self.label == 0) & (np.asarray(res['occ']) > 0.5))
        vm = max(np.percentile(fem.von_mises(fem.element_stress(g, self.C, self.B0, u))[on], 99.5) for u in comb.values())
        self.loads_cache = self.loads(cond)
        pad = {case: self.pad_min_N(res, coef, case != 'gravity') for case, coef in self.loads_cache.items()} \
            if '_K' in res else {}      # 밀기는 자중과 함께 작용
        ZT = self.TV['top_above_bottom_mm'] + self.ZN
        out = dict(sag=sag, utop_fb=ufb, utop_lat=ulat, vm=float(vm), pad_min_N=pad,
                   tip_margin_fb=float(self.BY / (0.13 * ZT)), tip_margin_lat=float(self.BX / (0.13 * ZT)),
                   mass_g=self.mass_g(res['occ']))
        out['uplift'] = bool(pad and min(pad.values()) < 0)        # 경고: 고정 패드 가정이 깨짐(정보용)
        out['pass'] = bool(sag <= 0.10 and ufb <= 1.0 and ulat <= 1.0 and vm <= 184.0
                           and min(out['tip_margin_fb'], out['tip_margin_lat']) >= 1.0)
        return out


# =====================================================================================
GROUPS = {
    'bike_pad50': lambda: BikeMount(50.0, 16.0),
    'bike_pad80': lambda: BikeMount(80.0, 16.0),
    'bike_pad120': lambda: BikeMount(120.0, 16.0),
    'tvfeet_L300': lambda: TVFeet(300.0),
    'tvfeet_L220': lambda: TVFeet(220.0),
    'tvped': lambda: TVPedestal(),
}
PRODUCT_OF = {'bike_pad50': 'bike', 'bike_pad80': 'bike', 'bike_pad120': 'bike',
              'tvfeet_L300': 'tvfeet', 'tvfeet_L220': 'tvfeet', 'tvped': 'tvped'}


def get(group):
    return GROUPS[group]()


if __name__ == '__main__':
    for k in GROUPS:
        p = get(k)
        sp_ = p.spec()
        print(k, sp_['grid']['shape'], sp_['elements'], 'fixed groups', p.n_fixed, 'supports', len(p.supports))
