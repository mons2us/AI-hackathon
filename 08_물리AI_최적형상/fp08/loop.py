"""자동 루프 (설계 결정 9번) — 데이터 → DeepSDF → PINO → 품질 관문 → 능동 학습(최대 3바퀴) → 시연 최적화·FEM 검증.

python -m fp08.loop --run runs/main --data data --workers 32 --devices cuda:0,cuda:1,cuda:2 \
       --n-shapes 5000 --n-fem 1000 --sdf-steps 20000 --pino-steps 30000 --deadline "2026-11-16 07:00"
python -m fp08.loop --run runs/main --stages shapes,fem           # CPU 서버: 데이터만
python -m fp08.loop --run runs/main --stages sdf,pino,gate,al,demo  # GPU 서버: 학습부터

- 상태 파일 runs/main/state.json : 단계별 완료 여부·시간·지표. 끊기면 같은 명령으로 이어서.
- 진행 보고서 runs/main/report.html : 단계·지표·관문 결과 (자동 갱신, 자동 push 없음).
- 로그 runs/main/loop.log
"""
import os, sys, json, time, argparse, subprocess, datetime, html
import numpy as np

from . import problems, datagen, sweep

GATE = dict(relL2_mean=0.10, judge=0.05, stress=0.15, freq_within5=0.95)
STRESS_KEYS = ('vm', 'interlayer')
DEMO = {  # 시연 조건 (07 고정 시나리오와 맞춤)
    'bike_pad80': [dict(phone_mass_g=200.0, phone_angle_deg=0.0), dict(phone_mass_g=220.0, phone_angle_deg=15.0)],
    'bike_pad50': [dict(phone_mass_g=200.0, phone_angle_deg=0.0)],
    'bike_pad120': [dict(phone_mass_g=200.0, phone_angle_deg=0.0)],
    'bike_pad80_free': [dict(phone_mass_g=200.0, phone_angle_deg=0.0)],    # 화면 각도 자유 (기둥 60 mm, 폰 회전 공간 비움)
    'tvfeet_L300': [dict(tv_mass_kg=20.8, leg_span_mm=1200.0)],
    'tvfeet_L220': [dict(tv_mass_kg=20.8, leg_span_mm=1200.0)],
    'tvped': [dict(tv_mass_kg=20.8)],
}


class Loop:
    def __init__(self, a):
        self.a = a
        self.run = a.run
        os.makedirs(self.run, exist_ok=True)
        self.sf = os.path.join(self.run, 'state.json')
        self.state = json.load(open(self.sf, encoding='utf-8')) if os.path.exists(self.sf) else dict(stages={}, rounds=[], started=now())
        self.deadline = time.mktime(time.strptime(a.deadline, '%Y-%m-%d %H:%M')) if a.deadline else None
        self.groups = a.groups.split(',') if a.groups else list(problems.GROUPS)
        self.products = sorted({problems.PRODUCT_OF[g] for g in self.groups})
        self.devices = a.devices.split(',')

    # ---------------------------------------------------------------- 기록
    def log(self, msg):
        line = f'[{now()}] {msg}'
        print(line, flush=True)
        with open(os.path.join(self.run, 'loop.log'), 'a', encoding='utf-8') as f:
            f.write(line + '\n')

    def save(self):
        self.state['updated'] = now()
        with open(self.sf + '.tmp', 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=1, default=float)
        os.replace(self.sf + '.tmp', self.sf)
        write_report(self.run, self.state)

    def done(self, key):
        return self.state['stages'].get(key, {}).get('done', False)

    def mark(self, key, **kw):
        self.state['stages'][key] = dict(done=True, at=now(), **kw)
        self.save()

    def pgroups(self, pr):
        """--groups 로 일부 그룹만 돌릴 때 PINO 도 그 그룹만 (전부면 옵션 없음)"""
        from . import train_pino
        gs = [g for g in train_pino.PRODUCTS[pr] if g in self.groups]
        return [] if len(gs) == len(train_pino.PRODUCTS[pr]) else ['--groups', ','.join(gs)]

    def left(self):
        return None if self.deadline is None else self.deadline - time.time()

    # ---------------------------------------------------------------- 병렬 작업 (GPU 여러 장)
    def run_jobs(self, jobs):
        """jobs: [(이름, [명령])] → 장치마다 하나씩 동시에 실행"""
        procs, queue = {}, list(jobs)
        slots = list(enumerate(self.devices))          # 같은 장치를 여러 번 적으면 그 수만큼 동시 실행
        while queue or procs:
            for slot, dv in slots:
                if slot not in procs and queue:
                    name, cmd = queue.pop(0)
                    lf = open(os.path.join(self.run, f'{name}.log'), 'a', encoding='utf-8')
                    env = dict(os.environ, PYTHONUTF8='1')       # Windows(cp949)에서 한글·기호 로그 깨짐/오류 방지
                    if dv == 'cpu':
                        env['OMP_NUM_THREADS'] = str(max(1, (os.cpu_count() or 2) // len(self.devices)))
                    procs[slot] = (name, subprocess.Popen(cmd + ['--device', dv], stdout=lf, stderr=subprocess.STDOUT, env=env), lf)
                    self.log(f'시작 {name} on {dv}')
            time.sleep(5)
            for slot in list(procs):
                name, pr, lf = procs[slot]
                if pr.poll() is not None:
                    lf.close()
                    self.log(f'끝 {name} (코드 {pr.returncode})')
                    del procs[slot]
            self.save()

    # ---------------------------------------------------------------- 단계
    def st_shapes(self):
        for g in self.groups:
            k = f'shapes:{g}'
            prev = self.state['stages'].get(k, {})
            if prev.get('done') and prev.get('n', 0) >= self.a.n_shapes and (prev.get('eso', False) or not self.a.eso):
                continue                                   # --n-shapes 를 늘리거나 --eso 를 새로 켜면 모자란 만큼만 추가 생성
            t = time.time()
            datagen.make_shapes(g, self.a.n_shapes, self.a.data, self.a.workers, n_cand=self.a.n_cand, eso=self.a.eso, log=self.log)
            self.mark(k, sec=round(time.time() - t, 1), n=self.a.n_shapes, eso=bool(self.a.eso or prev.get('eso')),
                      total=datagen.count_shapes(self.a.data, g))
        # 금지 공간 그룹: 무작위 형상이 기준에 한참 못 미침 → '위에서 깎기' 형상(꽉 찬 형상 → ESO 단계별)과 그 FEM 정답 추가
        for g in self.groups:
            k = f'topdown:{g}'
            if self.a.topdown <= 0 or problems.get(g).keepout_meta is None:
                continue
            if self.state['stages'].get(k, {}).get('n', 0) >= self.a.topdown:
                continue
            t = time.time()
            datagen.make_topdown(g, self.a.topdown, self.a.data, self.a.workers, log=self.log)
            self.mark(k, sec=round(time.time() - t, 1), n=self.a.topdown, total=datagen.count_shapes(self.a.data, g))

    def st_fem(self):
        for g in self.groups:
            k = f'fem:{g}'
            prev = self.state['stages'].get(k, {})
            if prev.get('done') and prev.get('req', prev.get('n', 0)) >= self.a.n_fem and (prev.get('eso', False) or not self.a.eso):
                continue                                   # --n-fem 을 늘리면 모자란 만큼만 추가
            t = time.time()
            datagen.make_fem(g, self.a.n_fem, self.a.data, self.a.workers, log=self.log, eso=self.a.eso)
            R = datagen.load_fem(self.a.data, g)
            self.mark(k, sec=round(time.time() - t, 1), n=int(len(R['idx'])), req=self.a.n_fem, eso=bool(self.a.eso),
                      n_eso=int(((R['idx'] >= datagen.ESO_BASE) & (R['idx'] < 2 * datagen.ESO_BASE)).sum()) if len(R['idx']) else 0,
                      pass_frac=float(np.mean([e['pass'] for e in R['eval']])) if R['eval'] else None)

    def st_sdf(self):
        """체크포인트 기준으로 판단: 없거나, 스텝이 모자라거나(--sdf-steps 를 늘림), 형상 수가 바뀌었으면(데이터 추가) 학습.
        sweep 으로 고른 모델도 여기서 같은 설정으로 이어감 (설정은 체크포인트에 저장돼 있음)"""
        import torch
        jobs = []
        for g in self.groups:
            ck = os.path.join(self.run, 'sdf', g, 'ckpt.pt')
            if os.path.exists(ck):
                c = torch.load(ck, map_location='cpu', weights_only=False)
                if c['step'] >= self.a.sdf_steps and c['n'] == datagen.count_shapes(self.a.data, g):
                    continue
            jobs.append((f'sdf_{g}', [sys.executable, '-m', 'fp08.train_sdf', '--group', g, '--data', self.a.data,
                                      '--out', self.run, '--steps', str(self.a.sdf_steps),
                                      '--eval-every', str(max(self.a.sdf_steps // 10, 100)),
                                      '--width', str(self.a.sdf_width), '--depth', str(self.a.sdf_depth), '--n-eval', '30']))
        self.run_jobs(jobs)
        for g in self.groups:
            ck = os.path.join(self.run, 'sdf', g, 'ckpt.pt')
            if os.path.exists(ck):
                c = torch.load(ck, map_location='cpu', weights_only=False)
                if c['step'] >= self.a.sdf_steps:
                    self.mark(f'sdf:{g}', last=c['hist'][-1] if c['hist'] else None, step=c['step'], n=c['n'], cfg=c.get('cfg'))

    # ---------------------------------------------------------------- 학습 방법 고르기 (sweep)
    def _sweep(self, kind, units, cands, mk_cmd, read_hist, score_fn, full_steps, canon):
        """kind: 'sdf'|'pino', units: 그룹 또는 제품 목록, mk_cmd(unit, 이름, 후보, stop_at) → 명령
        1차: 후보 전부 SCREEN_FRAC 까지 → 검증 점수 상위 top-k 를 끝까지 → 최선을 canon(unit) 위치로 복사"""
        st = self.state.setdefault('sweep', {}).setdefault(kind, {})
        screen = max(1, int(full_steps * sweep.SCREEN_FRAC))
        todo = [u for u in units if not self.done(f'sweep_{kind}:{u}')]
        if not todo:
            return
        self.log(f'sweep {kind}: 후보 {list(cands)} × {todo}, 1차 {screen} 스텝 → 상위 {self.a.sweep_topk} 개 {full_steps} 스텝')
        jobs = [(f'sw_{kind}_{u}_{n}', mk_cmd(u, n, c, screen)) for u in todo for n, c in cands.items()
                if (read_hist(u, n) or [{}])[-1].get('step', 0) < screen]
        self.run_jobs(jobs)
        finals = {}
        for u in todo:
            sc = {n: score_fn(read_hist(u, n)) for n in cands}
            finals[u] = sweep.pick(sc, self.a.sweep_topk)
            st.setdefault(u, {})['screen'] = sc
            self.log(f'sweep {kind} {u}: 1차 점수 {json.dumps({k: round(v, 4) for k, v in sc.items()})} → 끝까지: {finals[u]}')
        self.save()
        jobs = [(f'sw_{kind}_{u}_{n}', mk_cmd(u, n, cands[n], None)) for u in todo for n in finals[u]
                if (read_hist(u, n) or [{}])[-1].get('step', 0) < full_steps]
        self.run_jobs(jobs)
        for u in todo:
            sc = {n: score_fn(read_hist(u, n)) for n in finals[u]
                  if (read_hist(u, n) or [{}])[-1].get('step', 0) >= full_steps}
            if not sc:
                self.log(f'sweep {kind} {u}: 끝까지 학습된 후보 없음 (로그 확인)'); continue
            best = sweep.pick(sc, 1)[0]
            sweep.promote(os.path.join(self.run, f'sweep_{kind}', best, u), canon(u))
            st[u].update(final=sc, chosen=best, cfg=cands[best])
            self.mark(f'sweep_{kind}:{u}', chosen=best, score=sc[best])
            self.log(f'sweep {kind} {u}: 선택 {best} (검증 점수 {sc[best]:.4f})')

    def sweep_sdf(self):
        import torch
        def hist(g, n):
            ck = os.path.join(self.run, 'sweep_sdf', n, g, 'ckpt.pt')
            return torch.load(ck, map_location='cpu', weights_only=False)['hist'] if os.path.exists(ck) else []
        def cmd(g, n, c, stop):
            return ([sys.executable, '-m', 'fp08.train_sdf', '--group', g, '--data', self.a.data, '--out', self.run,
                     '--tag', f'sweep_sdf/{n}', '--steps', str(self.a.sdf_steps), '--n-eval', '30',
                     '--eval-every', str(max(self.a.sdf_steps // 10, 100))] + sweep.sdf_args(c)
                    + (['--stop-at', str(stop)] if stop else []))
        self._sweep('sdf', self.groups, sweep.SDF_CANDS, cmd, hist, sweep.sdf_score, self.a.sdf_steps,
                    lambda g: os.path.join(self.run, 'sdf', g))
        for g in self.groups:
            if self.done(f'sweep_sdf:{g}') and not self.done(f'sdf:{g}'):
                c = torch.load(os.path.join(self.run, 'sdf', g, 'ckpt.pt'), map_location='cpu', weights_only=False)
                self.mark(f'sdf:{g}', last=c['hist'][-1], chosen=self.state['sweep']['sdf'][g]['chosen'])

    def sweep_pino(self):
        from . import train_pino
        def hist(pr, n):
            try:
                return train_pino.load(self.run, f'sweep_pino/{n}', pr)[1]['hist']
            except FileNotFoundError:
                return []
        def cmd(pr, n, c, stop):
            return ([sys.executable, '-m', 'fp08.train_pino', '--product', pr, '--data', self.a.data, '--out', self.run,
                     '--tag', f'sweep_pino/{n}', '--steps', str(self.a.pino_steps),
                     '--eval-every', str(max(self.a.pino_steps // 15, 50))] + self.pgroups(pr) + sweep.pino_args(c)
                    + (['--stop-at', str(stop)] if stop else []))
        self._sweep('pino', self.products, sweep.PINO_CANDS, cmd, hist, sweep.pino_score, self.a.pino_steps,
                    lambda pr: os.path.join(self.run, 'pino', pr))
        for pr in self.products:
            if self.done(f'sweep_pino:{pr}') and not self.done(f'pino:{pr}:r0'):
                self.mark(f'pino:{pr}:r0', chosen=self.state['sweep']['pino'][pr]['chosen'])
            if self.done(f'sweep_pino:{pr}') and f'pino:{pr}' not in self.state.get('pino_data', {}):
                self.state.setdefault('pino_data', {})[f'pino:{pr}'] = sum(
                    datagen.count_fem(self.a.data, g) for g in train_pino.PRODUCTS[pr] if g in self.groups)
                self.save()

    def sdf_test(self):
        """DeepSDF 시험 셋 성적 (고르는 데 안 쓴 10%) → state['sdf_test'] (모델이 바뀌면 다시 계산)"""
        import torch
        from . import train_sdf
        for g in self.groups:
            ck = os.path.join(self.run, 'sdf', g, 'ckpt.pt')
            if not os.path.exists(ck):
                continue
            c = torch.load(ck, map_location='cpu', weights_only=False)
            old = self.state.get('sdf_test', {}).get(g, {})
            if old.get('step') == c['step'] and old.get('n_shapes') == c['n']:
                continue
            m = train_sdf.test_metrics(ck, self.a.data, g)
            m.update(step=c['step'], n_shapes=c['n'])
            self.state.setdefault('sdf_test', {})[g] = m
            self.log(f'DeepSDF 시험 셋 {g}: {json.dumps(m)}')
            self.save()

    def st_pino(self, tag='pino', extra=(), steps=None, round_=0):
        """체크포인트 기준으로 판단: 없거나 스텝이 모자라면 학습. FEM 정답 수가 지난 학습 때보다 늘었으면
        (‑‑n-fem 을 늘림) 스텝을 1/3 만큼 더해 이어서 학습 (능동 학습과 같은 방식)"""
        from . import train_pino
        steps = steps or self.a.pino_steps
        jobs, target = [], {}
        for pr in self.products:
            gs = [g for g in train_pino.PRODUCTS[pr] if g in self.groups]
            nfem = sum(datagen.count_fem(self.a.data, g) for g in gs)
            st = steps
            try:
                c = train_pino.load(self.run, tag, pr)[1]
                seen = self.state.get('pino_data', {}).get(f'{tag}:{pr}')
                if c['step'] >= steps:
                    if seen is None or nfem <= seen:
                        target[pr] = (c['step'], nfem); continue
                    st = c['step'] + self.a.pino_steps // 3
                    self.log(f'{tag} {pr}: FEM 정답 {seen} → {nfem} 로 늘어남 → {c["step"]} → {st} 스텝까지 이어서 학습')
            except FileNotFoundError:
                pass
            target[pr] = (st, nfem)
            jobs.append((f'{tag}_{pr}', [sys.executable, '-m', 'fp08.train_pino', '--product', pr, '--data', self.a.data,
                                         '--out', self.run, '--steps', str(st), '--tag', tag,
                                         '--eval-every', str(max(self.a.pino_steps // 15, 50))] + self.pgroups(pr) + list(extra)))
        self.run_jobs(jobs)
        for pr in self.products:
            try:
                _, c = train_pino.load(self.run, tag, pr)
                if c['step'] >= target[pr][0]:
                    self.state.setdefault('pino_data', {})[f'{tag}:{pr}'] = target[pr][1]
                    self.mark(f'{tag}:{pr}:r{round_}', last=c['hist'][-1] if c['hist'] else None, step=c['step'], n_fem=target[pr][1])
            except FileNotFoundError:
                pass

    def gate(self, round_):
        """품질 관문 — 검증 셋 지표로 제품·그룹별 합격 판정"""
        from . import train_pino
        res = {}
        for pr in self.products:
            net, c = train_pino.load(self.run, 'pino', pr)
            for g in train_pino.PRODUCTS[pr]:
                if g not in self.groups:
                    continue
                gd = train_pino.GroupData(g, self.a.data, 'cpu')
                m = train_pino.validate(net, gd, ks=gd.te if len(gd.te) else None)   # 시험 셋 (sweep 선택에 안 쓴 10%)
                m['set'] = 'test' if len(gd.te) else 'val'
                why = []
                if m['relL2_mean'] is not None and m['relL2_mean'] > GATE['relL2_mean']:
                    why.append(f"변위장 L2 {m['relL2_mean']:.3f}")
                for q, v in m['judge_abs_p90'].items():
                    lim = GATE['stress'] if q in STRESS_KEYS else GATE['judge']
                    if q in ('mass_g', 'tip_margin_fb', 'tip_margin_lat'):
                        continue
                    if v > lim:
                        why.append(f'{q} {v:.3f}')
                if 'freq_within5_frac' in m and m['freq_within5_frac'] < GATE['freq_within5']:
                    why.append(f"진동수 ±5% {m['freq_within5_frac']:.2f}")
                res[g] = dict(metrics=m, passed=not why, why=why)
                self.log(f'관문 r{round_} {g}: {"합격" if not why else "불합격 " + ", ".join(why)}')
        self.state.setdefault('gate', {})[f'r{round_}'] = res
        self.save()
        return res

    def active_learning(self, round_, failed):
        """그룹당 200개: 물리 잔차 큰 형상 100 + 최적화 후보 100 → FEM 정답 → 재학습"""
        import torch
        from . import train_pino, models
        for g in failed:
            key = f'al:{g}:r{round_}'
            if self.done(key):
                continue
            pr = problems.PRODUCT_OF[g]
            net, _ = train_pino.load(self.run, 'pino', pr)
            gd = train_pino.GroupData(g, self.a.data, 'cpu')
            sc = []
            for s in range(0, min(len(gd.u_idx), 1000), 4):
                k = np.arange(s, min(s + 4, len(gd.u_idx)))
                out, occ_t, nm, Fb = train_pino.predict(net, gd, gd.u_occ[k], [gd.u_cond[i] for i in k])
                ks_ = gd.pt.kscale(occ_t)
                e = torch.stack([gd.pt.residual(ks_, out['u'][:, j], Fb[:, j], gd.pt.free[j]) for j in range(out['u'].shape[1])]).mean(0)
                sc += e.tolist()
            pick = np.argsort(sc)[::-1][:self.a.al_n // 2]
            idx = gd.u_idx[pick]; occ = gd.u_occ[pick]
            # 최적화 후보: 직전 시연 최적화에서 나온 실패 후보 + 학습 형상 주변 무작위 섞기
            cand = self.opt_candidates(g, self.a.al_n - len(idx))
            if len(cand):
                base = 100_000_000 * (round_ + 1)        # ESO 번호대(1천만~2천만)와 겹치지 않게
                idx = np.concatenate([idx, base + np.arange(len(cand))]); occ = np.concatenate([occ, cand])
            tasks = [(g, s, self.a.data, idx[s * 25:(s + 1) * 25], occ[s * 25:(s + 1) * 25], f'al{round_}')
                     for s in range((len(idx) + 24) // 25)]
            datagen.run_pool(datagen.fem_shard, tasks, self.a.workers, self.log)
            self.mark(key, n=int(len(idx)))

    def opt_candidates(self, g, n):
        d = os.path.join(self.run, 'demo')
        out = []
        if os.path.isdir(d):
            for f in os.listdir(d):
                if f.startswith(f'fail_{g}_') and f.endswith('.npy'):
                    p = problems.get(g)
                    out.append(np.unpackbits(np.load(os.path.join(d, f)), axis=1)[:, :p.grid.ne].astype(bool))
        return np.concatenate(out)[:n] if out else np.zeros((0,), bool)

    def demo(self, round_):
        import torch
        from . import design_opt, train_pino
        res = {}
        gate = self.state.get('gate', {}).get(f'r{round_}', {})
        for g in self.groups:
            pr = problems.PRODUCT_OF[g]
            net, _ = train_pino.load(self.run, 'pino', pr)
            margins = {}
            m = gate.get(g, {}).get('metrics', {})
            for q, v in m.get('judge_abs_p90', {}).items():
                margins[q] = float(min(max(v, 0.02), 0.3))
            if 'freq_abs_p95' in m:
                margins['f_min'] = float(min(max(m['freq_abs_p95'], 0.02), 0.3))
            for cond in DEMO[g]:
                s, _ = design_opt.optimize(g, cond, os.path.join(self.run, 'sdf', g, 'ckpt.pt'), net, self.a.data,
                                           margins=margins, n_starts=self.a.n_starts, steps=self.a.opt_steps,
                                           log=self.log, out_dir=os.path.join(self.run, 'demo'))
                res.setdefault(g, []).append(dict(cond=cond, status=s['status'], t=s['t'],
                                                  best=(s['best'] or {}).get('fem'), margins=margins))
                self.log(f'시연 {g} {cond}: {s["status"]} {s["t"]:.0f}s')
        self.state.setdefault('demo', {})[f'r{round_}'] = res
        self.save()
        return res

    # ---------------------------------------------------------------- 전체 흐름
    def main(self):
        st = self.a.stages.split(',')
        self.log(f'루프 시작: 단계 {st}, 그룹 {self.groups}, 마감 {self.a.deadline}')
        if 'shapes' in st: self.st_shapes()
        if 'fem' in st: self.st_fem()
        if 'sdf' in st:
            if self.a.sweep: self.sweep_sdf()
            self.st_sdf()                   # sweep 뒤에도 호출: 스텝·데이터가 늘었으면 고른 모델을 이어서 학습
            self.sdf_test()
        if 'pino' in st:
            if self.a.sweep: self.sweep_pino()
            self.st_pino()
        if 'compare' in st:              # 부록 비교: FNO(물리 손실 없음), 레일리 대신 직접 회귀
            self.st_pino('fno', ['--no-physics'])
            self.st_pino('direct', ['--freq', 'direct'])
        r = 0
        while 'gate' in st:
            res = self.gate(r)
            failed = [g for g, v in res.items() if not v['passed']]
            if 'demo' in st:
                self.demo(r)
            if not failed or r >= self.a.max_rounds or 'al' not in st:
                break
            if self.left() is not None and self.left() < 3 * 3600:
                self.log('마감 3시간 전 → 능동 학습 중단'); break
            self.active_learning(r, failed)
            r += 1
            self.state['rounds'].append(dict(round=r, failed=failed, at=now())); self.save()
            self.st_pino(steps=self.a.pino_steps + r * self.a.pino_steps // 3, round_=r)   # 이어서 추가 학습
        self.state['finished'] = now(); self.save()
        self.log('루프 끝')


def now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def sweep_html(state):
    e = html.escape
    out = ''
    sw = state.get('sweep', {})
    if sw:
        out += '<h3>학습 방법 고르기 (sweep) — 검증 셋 점수, 작을수록 좋음</h3><table><tr><th>모델</th><th>대상</th><th>1차(20%) 점수</th><th>끝까지 점수</th><th>선택</th></tr>'
        for kind, d in sw.items():
            for u, v in d.items():
                f2 = lambda x: e(json.dumps({k: round(a, 4) for k, a in (x or {}).items()}))
                out += f'<tr><td>{kind}</td><td>{u}</td><td><code>{f2(v.get("screen"))}</code></td><td><code>{f2(v.get("final"))}</code></td><td><b>{e(str(v.get("chosen", "-")))}</b></td></tr>'
        out += '</table>'
    t = state.get('sdf_test', {})
    if t:
        out += '<h3>DeepSDF 시험 셋 성적 (제안 기준: IoU ≥ 0.90, 표면 오차 ≤ 0.5칸 — 미확정)</h3><table><tr><th>그룹</th><th>형상 수</th><th>IoU 평균</th><th>IoU 하위10%</th><th>표면 오차 mm</th><th>표면 오차 칸</th></tr>'
        for g, m in t.items():
            out += f'<tr><td>{g}</td><td>{m["n"]}</td><td>{m["iou_test"]:.3f}</td><td>{m["iou_test_p10"]:.3f}</td><td>{m["surf_err_mm_test"]:.3f}</td><td>{m["surf_err_cell_test"]:.2f}</td></tr>'
        out += '</table>'
    return out


def write_report(run, state):
    """진행 보고서 HTML (서버 파일)"""
    e = html.escape
    rows = ''.join(f'<tr><td>{e(k)}</td><td>{e(str(v.get("at","")))}</td><td><code>{e(json.dumps({a: b for a, b in v.items() if a not in ("done", "at", "last")}, ensure_ascii=False, default=float))[:200]}</code></td></tr>'
                   for k, v in state.get('stages', {}).items())
    gates = ''
    for r, res in state.get('gate', {}).items():
        for g, v in res.items():
            m = v['metrics']
            gates += (f'<tr><td>{r}</td><td>{g}</td><td>{"✅" if v["passed"] else "❌"}</td><td>{m.get("relL2_mean") or 0:.3f}</td>'
                      f'<td>{m.get("freq_within5_frac", "-")}</td><td><code>{e(json.dumps({k: round(x, 3) for k, x in m.get("judge_abs_p90", {}).items()}))}</code></td>'
                      f'<td>{e(", ".join(v["why"]))}</td></tr>')
    demos = ''
    for r, res in state.get('demo', {}).items():
        for g, lst in res.items():
            for d in lst:
                b = d.get('best') or {}
                demos += (f'<tr><td>{r}</td><td>{g}</td><td>{e(json.dumps(d["cond"]))}</td><td>{d["status"]}</td>'
                          f'<td>{b.get("mass_g", "-")}</td><td><code>{e(json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in b.items() if k not in ("f", "pad_min_N")}, default=str))[:220]}</code></td><td>{d["t"]:.0f}s</td></tr>')
    doc = f"""<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><meta http-equiv="refresh" content="60">
<title>08 자동 루프 진행</title><style>body{{font-family:sans-serif;margin:20px;max-width:1100px}}table{{border-collapse:collapse;width:100%;margin-bottom:18px;font-size:13px}}
td,th{{border:1px solid #ddd;padding:4px 6px}}th{{background:#f3f3f3}}code{{font-size:11px}}</style></head><body>
<h2>08 물리 AI 자동 루프 — 진행 보고서</h2><p>시작 {e(state.get('started',''))} · 갱신 {e(state.get('updated',''))} · 끝 {e(state.get('finished','진행 중'))}</p>
{sweep_html(state)}
<h3>품질 관문 (시험 셋)</h3><p>기준: 변위장 상대 L2 평균 ≤ {GATE['relL2_mean']}, 판정값 오차(상위 10%) ≤ {GATE['judge']}, 응력 ≤ {GATE['stress']}, 진동수 ±5% 이내 비율 ≥ {GATE['freq_within5']}</p>
<table><tr><th>바퀴</th><th>그룹</th><th>결과</th><th>L2</th><th>진동수 ±5%</th><th>판정값 오차 p90</th><th>불합격 사유</th></tr>{gates}</table>
<h3>시연 최적화 + FEM 검증</h3><table><tr><th>바퀴</th><th>그룹</th><th>조건</th><th>상태</th><th>질량 g</th><th>FEM 판정값</th><th>시간</th></tr>{demos}</table>
<h3>단계</h3><table><tr><th>단계</th><th>완료 시각</th><th>정보</th></tr>{rows}</table></body></html>"""
    with open(os.path.join(run, 'report.html'), 'w', encoding='utf-8') as f:
        f.write(doc)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', default='runs/main'); ap.add_argument('--data', default='data')
    ap.add_argument('--stages', default='shapes,fem,sdf,pino,gate,al,demo')
    ap.add_argument('--groups', default=None)
    ap.add_argument('--workers', type=int, default=os.cpu_count())
    ap.add_argument('--devices', default='cpu')
    ap.add_argument('--n-shapes', type=int, default=5000); ap.add_argument('--n-cand', type=int, default=12000); ap.add_argument('--eso', action='store_true'); ap.add_argument('--n-fem', type=int, default=1000)
    ap.add_argument('--sdf-steps', type=int, default=20000); ap.add_argument('--sdf-width', type=int, default=256); ap.add_argument('--sdf-depth', type=int, default=8); ap.add_argument('--pino-steps', type=int, default=30000)
    ap.add_argument('--al-n', type=int, default=200); ap.add_argument('--max-rounds', type=int, default=3)
    ap.add_argument('--n-starts', type=int, default=10); ap.add_argument('--opt-steps', type=int, default=300)
    ap.add_argument('--deadline', default=None)
    ap.add_argument('--topdown', type=int, default=100, help='금지 공간 그룹에 추가할 위에서 깎기 순서열 수 (약 10형상씩, FEM 정답 포함)')
    ap.add_argument('--sweep', action='store_true', help='학습 방법 후보 여러 개 → 검증 점수로 최선 자동 선택 (fp08/sweep.py)')
    ap.add_argument('--sweep-topk', type=int, default=1, help='1차 거르기 뒤 끝까지 학습할 후보 수 (1: GPU 시간 약 1.6배, 2: 약 2.4배)')
    Loop(ap.parse_args()).main()
