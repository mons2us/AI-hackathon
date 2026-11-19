"""같은 형상 AI(GUI 의 DeepSDF, 숫자 16개) + 물리 AI 만 바꿔 AI 탐색 비교: FNO(같은 데이터로 새로 학습) vs GINO.
시작 = 초기 설계에 맞춘 z0 (GUI 캐시, 맞추기 1500회), 기준 = 데모와 같음 (진동수 ≥ 95 Hz · 폰 온도 ≤ 21 · 휨 ≤ 0.3 mm),
목적 = 무게(정확식) + 3·(Σ 정규화 위반 × 10)² + 1e-3‖z‖², Adam lr 0.02, 300회 — GUI real.trace 와 같은 식 (출력 조건 필터는 둘 다 끔).
GINO 연결: 형상 AI 점유 확률 → 전체 칸(고정 부품 포함) → 2×2×2 평균 = 잠재 격자 특징 (미분 경로),
          표면 점 · 출력 점은 매 회 현재 형상(0.5 기준)에서 다시 뽑음 (위치는 미분하지 않음)."""
import sys, os, json, time, numpy as np, torch
H = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [H, '/home/claude/input-spec/13_AI학습_일체형', '/home/claude/input-spec/10_입력_1차설계']
torch.set_num_threads(int(os.environ.get('THREADS', '2')))
from ai.data import LabelNorm
from ai.surrogate import Surrogate
from gino_data import Geo
from gino_model import GinoSur
from formproof_input.inverse.fp11.deepsdf import ShapeAI
M = '/home/claude/input-spec/10_입력_1차설계/models/fp11'
geo = Geo(); g = geo.g; S = ShapeAI(M + '/runs/sdf.pt', g)
z0 = np.load(M + '/z0_3a61befe66c5_1500.npy').reshape(1, -1)
LIM = {'f1': ('>=', 95.0), 'Tmax': ('<=', 21.0), 'touch': ('<=', 0.3)}
SOLID = torch.tensor(g.solid, dtype=torch.float32); DIDX = torch.tensor(g.didx); TH = geo.thermal.ravel()
CELL = torch.tensor(geo.cell.reshape(-1, 3)); LAT = torch.tensor(geo.latent)

def keys(y): return {'f1': y[1], 'Tmax': y[3], 'touch': torch.maximum(y[4], y[5]), 'stress': y[6]}
def pen(k):
    p = torch.zeros(())
    for n, (op, L) in LIM.items(): p = p + (torch.relu(L - k[n]) if op == '>=' else torch.relu(k[n] - L)) / L * 10
    return p

class GinoPred:
    def __init__(self, ck):
        st = torch.load(ck, map_location='cpu', weights_only=False); a = st['args']
        self.net = GinoSur(rin=a['r'], rout=a['r']); st['state'].pop('_metadata', None);   self.net.load_state_dict(st['state']); self.net.eval(); self.norm = LabelNorm(state=st['norm'])
        self.rng = np.random.default_rng(0); self.ns, self.no = 2048, 2048
    def predict(self, o):                                   # o: (1, nd) 점유 확률 (미분 가능)
        full = SOLID.index_put((DIDX,), o[0]).view(g.nz, g.ny, g.nx)
        F = (full.detach() > 0.5).numpy().astype(np.float32); P, Nn = geo.surface(F)
        k = np.nonzero((F.ravel() > 0.5) | TH)[0]
        si = self.rng.choice(len(P), min(self.ns, len(P)), replace=False); ko = torch.tensor(self.rng.choice(k, min(self.no, len(k)), replace=False))
        s, _ = self.net(torch.tensor(P[si]), torch.tensor(Nn[si]), LAT, geo.latent_occ(full), CELL[ko])   # 학습 때처럼 표면 2048 · 출력 2048 점 (속도)
        s = torch.cat([torch.zeros(1), s[1:]])        # 무게 출력(학습 안 함)은 0 으로: decode 의 exp 넘침 → 0×inf = NaN 기울기 방지 (무게는 정확식으로 대체)
        y = self.norm.decode_t(s[None])[0]
        return torch.cat([g.mass_g(o)[0:1], y[1:]])

class FnoPred:
    def __init__(self, ck): self.s = Surrogate(ck, g, torch.device('cpu'))
    def predict(self, o):                                   # GINO 와 같은 처리: 무게 출력(학습 안 함)은 0 → decode, 무게는 정확식
        yn, _ = self.s.net(g.to_grid(o), self.s.coords)
        yn = torch.cat([torch.zeros(1, 1), yn[:, 1:]], 1); y = self.s.norm.decode_t(yn)[0]
        return torch.cat([g.mass_g(o)[0:1], y[1:]])

def run(pred, iters=300, lr=0.02, w=3.0):
    z = torch.tensor(z0, dtype=torch.float32).requires_grad_(True); opt = torch.optim.Adam([z], lr=lr); tr = []; t0 = time.time()
    for it in range(iters + 1):
        o = S.decode(z, sharp=2.0); y = pred.predict(o); k = keys(y); p = pen(k)
        full = g.solid.copy(); full[g.didx] = (o.detach()[0] > 0.5).numpy()
        if it % 10 == 0 or it == iters:
            tr.append(dict(it=it, mass=round(float(full.sum()) * 0.02032, 2), pen=round(float(p), 4), **{n: round(float(v), 3) for n, v in k.items()}))
        if it == iters: break
        loss = y[0] + w * p ** 2 + 1e-3 * (z ** 2).sum(); opt.zero_grad(); loss.backward(); opt.step()
    return dict(trace=tr, seconds=round(time.time() - t0, 1), rho=full, z=z.detach().numpy()[0].tolist())

if __name__ == '__main__':
    which = sys.argv[1:] or ['fno', 'gino']                     # 하나씩 돌릴 수 있게 (결과는 search_<이름>.json)
    TAG = os.environ.get('TAG', '')                              # 데이터 늘린 실험: TAG=734 → fno734.pt · gino734.pt, 결과 search_<이름>734.json
    for name in which:
        pred = FnoPred(H + ('/fno_base.pt' if not TAG else f'/fno{TAG}.pt')) if name == 'fno' else GinoPred(H + f'/gino{TAG}.pt')
        name = name + TAG
        r = run(pred); np.save(f'{H}/search_{name}_rho.npy', r.pop('rho'))
        json.dump(r, open(f'{H}/search_{name}.json', 'w'), ensure_ascii=False, indent=1)
        print(name, r['seconds'], 's', r['trace'][-1], flush=True)
