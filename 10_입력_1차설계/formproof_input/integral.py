"""P01 일체형 자전거 폰 거치대 — 발표 사례(발표초안 v83 7·10·14·22쪽)와 같은 1차 설계 · 설계 명세 · 물리 조건.

발표의 계산은 팀 엔진(11_구현패키지/FormProof_구현/engine/opt_int.py, GRIP=2 NX=88 MSYS=0.311 TILT=35)이 한다.
이 모듈은 입력 단계(말 · 스케치 → 1차 설계 + 조건)를 그 엔진과 '같은 문제'로 만든다.

  * 좌표: 폰 판 좌표계 (x' 폰 길이 방향, y 핸들바 축 = 폭, z' 판 법선). 세계: X = x'cos35 − z'sin35, Z = x'sin35 + z'cos35
  * 격자: 2 mm, 88 × 20 × 37, 원점 (−24, 0, −36), 절반 모델(y ≥ 0, y = 0 대칭) — opt_int 와 같음
  * 영역(지킬 곳 · 비울 곳 · 바꿀 곳): REGIONS 선언 → masks() — opt_int 의 solid / void / design 과 요소 하나까지 같음
    (tests/test_integral.py 가 data/grid_meta.npz 와 비교)
  * 1차 설계 = 발표의 '처음 설계 (판 + 기둥)': 클램프 + 20 × 8 mm 직선 보 + 2 mm 평판 (+ 고정 부품) — mkbase_int.py 와 같음
  * 조건: spec/bike_mount_spec.json(설계 명세, 항목마다 출처) · spec/bike_mount_targets.json(판정 기준)과 같은 값
  * 판정 계산: 팀 엔진 MODE=eval 을 그대로 호출(결과 캐시: templates/db/integral_eval.json)
  * 비교 형상(10쪽): LLM 단독 A·B·C(L1–L3.md 의 JSON 프리미티브, llm2rho.py 와 같은 변환), FormProof 최적화 결과
    (int35f95g2 120회), 출력 몸체 body_v3(STL 재격자화)
"""
import base64
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import time

import numpy as np

from .geometry import eval_shape

HERE = os.path.dirname(os.path.abspath(__file__))
INPUT_ROOT = os.path.dirname(HERE)                                   # 10_입력_1차설계
REPO = os.path.dirname(INPUT_ROOT)
PKG = os.path.join(REPO, "11_구현패키지", "FormProof_구현")          # team implementation package (master)
ENGINE = os.path.join(PKG, "engine", "opt_int.py")
LLM_DIR = os.path.join(REPO, "03_자전거거치대", "LLM단독비교", "일체형_2026-11-15")
DB = os.path.join(HERE, "templates", "db")
EVAL_DB = os.path.join(DB, "integral_eval.json")
SHAPES_DB = os.path.join(DB, "integral_shapes.npz")

# ------------------------------------------------------------------ constants (opt_int.py)
TILT = 35.0
H = 2.0
NX, NY, NZ = 88, 20, 37
ORIGIN = (-24.0, 0.0, -36.0)
XR, PL, ZB = -10.0, 150.0, 24.0          # plate x' in [XR, XR+PL] (grid stops at 140), z' in [24, 30]; phone back z' = 30
MATERIAL = dict(name="PETG (Prusament)", E=1700.0, nu=0.38, rho=1.27e-9, yield_mpa=39.0, density_g_cm3=1.27)
PAYLOAD = dict(mass_kg=0.311, box_mm=[165.0, 80.0, 15.0], cg=[XR + 75.0, 0.0, ZB + 6 + 7.5])
ENGINE_ENV = dict(GRIP="2", NX="88", MSYS="0.311", AM="1", RF="8", ETAE="0.7", TILT="35", FT="95", TLIM="21", DLIM="0.3",
                  ITERS="120", SCHED='{"0":1,"20":2,"40":4,"60":8,"80":16,"100":32}')

PRESENTATION_TEXT = "울퉁불퉁한 길에서도 폰이 안 흔들리게, 최대한 가볍게. 3D 프린터로 뽑을 거야"
SKETCH_NOTE = ("핸들바 스템 옆에 장착, 핸들바 위 라이더 쪽으로 폰, 35도쯤 기울임, 케이블·레버 피하기, "
               "'?' 상자 = 설계 영역, 모든 폰, 열 안 갇히게, 화면 눌러도 안 휘게, 안 흔들리게, 최대한 가볍게")


# ------------------------------------------------------------------ regions (phone frame)
def _box(**k):
    return {"box": {a: v for a, v in k.items()}}


def _rbox(**k):                       # box in the WORLD frame (handlebar frame), rotated by the tilt
    return {"rbox": dict(tilt_deg=TILT, **k)}


def _cyl(**k):
    return {"cyl": dict(axis="y", center=[0.0, 0.0], **k)}


# open bounds at element centres (odd mm); opt_int's '<15' etc. on centre values are written as the equivalent even
# bound (yc < 15  ==  yc < 14 on this grid) so no bound sits on a centre.
REGIONS = [
    # ---- void (precedence over solid, as in opt_int)
    dict(name="bore", role="void", shape=[_cyl(r_max=16.1)], why="핸들바 구멍 Ø32.2"),
    dict(name="slit", role="void", shape=[_rbox(X=[-1.0, 1.0], Z=[None, 0.0]), _cyl(r_max=26.0)], why="클램프 조임 절개"),
    dict(name="phone", role="void", shape=[_box(x=[XR, XR + PL], z=[ZB + 6, ZB + 14])], why="폰 (두께 8 mm, 판 위)"),
    dict(name="above_plate", role="void", shape=[_box(z=[ZB, None])], minus=["plate_layer", "hook"],
         why="판 윗면보다 위는 비움(아래 걸이만 예외)"),
    dict(name="channel", role="void", shape=[_box(x=[60.0, 70.0], z=[20.0, 28.0], y=[6.0, None])], why="슬라이드 집게 레일 채널"),
    dict(name="neck_slot", role="void", shape=[_box(x=[64.0, 66.0], z=[28.0, 30.0], y=[26.0, None])], why="집게 목 슬롯"),
    dict(name="rail_channel", role="void", shape=[_box(x=[104.0, 150.0], y=[None, 4.0], z=[14.0, 22.0])],
         why="위 걸이 슬라이드 채널"),
    dict(name="rail_slot", role="void", shape=[_box(x=[128.0, 150.0], y=[None, 2.0], z=[22.0, 30.0])], why="위 걸이 목 슬롯"),
    # ---- solid (fixed parts: kept as they are)
    dict(name="contact", role="solid", shape=[_cyl(r_min=16.1, r_max=20.6, y=[None, 10.0])], why="핸들바 클램프 링 (폭 20)"),
    dict(name="ears", role="solid", shape={"union": [[_rbox(X=[1.0, 9.0], Z=[-34.0, -14.0], y=[None, 10.0])],
                                                     [_rbox(X=[-9.0, -1.0], Z=[-34.0, -14.0], y=[None, 10.0])]]},
         why="M4 볼트 귀"),
    dict(name="jaw_housing", role="solid", shape=[_box(x=[56.0, 74.0], z=[18.0, 30.0])], why="양옆 슬라이드 집게 하우징 (x' 55–75)"),
    dict(name="ledge", role="solid", shape=[_box(x=[XR, -2.0], z=[ZB, ZB + 6], y=[None, 16.0])], why="폰 아래 끝 받침 턱"),
    dict(name="band", role="solid", shape=[_box(x=[56.0, 74.0], z=[ZB, ZB + 4])], why="집게 하우징 아래 띠"),
    dict(name="toppad", role="solid", shape=[_box(x=[126.0, 140.0], z=[ZB, ZB + 6], y=[None, 16.0])], why="폰 위 끝 뒷면 받침"),
    dict(name="hook", role="solid", shape=[_box(x=[-14.0, -10.0], y=[None, 14.0], z=[ZB, None])], why="아래 걸이 기둥"),
    dict(name="top_rail", role="solid", shape=[_box(x=[102.0, 150.0], y=[None, 10.0], z=[12.0, ZB])], why="위 슬라이드 걸이 레일"),
    # ---- helpers (only used through 'minus' and for the physics sets)
    dict(name="plate_layer", role="helper", shape=[_box(x=[XR, XR + PL], z=[ZB, ZB + 6])], why="받침판 층 z' 24–30"),
]
PRECEDENCE = ("void", "solid")


def grid_centres():
    k, j, i = np.meshgrid(np.arange(NZ), np.arange(NY), np.arange(NX), indexing="ij")
    ijk = np.c_[i.ravel(), j.ravel(), k.ravel()]
    return np.asarray(ORIGIN) + H * ijk + H / 2, ijk


def masks():
    """Element sets of the spec (same semantics as compile.Problem: void > solid > design)."""
    c, ijk = grid_centres()
    raw = {r["name"]: eval_shape(r["shape"], c, closed=False) for r in REGIONS}
    m = {}
    for r in REGIONS:
        v = raw[r["name"]].copy()
        for o in r.get("minus", []):
            v &= ~raw[o]
        m[r["name"]] = v
    lab = {}
    taken = np.zeros(len(c), bool)
    for role in PRECEDENCE:
        s = np.zeros(len(c), bool)
        for r in REGIONS:
            if r["role"] == role:
                s |= m[r["name"]]
        s &= ~taken
        lab[role] = s
        taken |= s
    x, y, z = c.T
    plate = m["plate_layer"]
    phone = m["phone"]
    out = dict(void=lab["void"], solid=lab["solid"], design=~taken, plate=plate, phone=phone, regions=m, centres=c, ijk=ijk)
    hous = eval_shape([_box(x=[56.0, 74.0], z=[18.0, 30.0])], c)
    out["attach"] = ((hous & (z > 28)) | m["ledge"] | m["toppad"] | (m["hook"] & (z > ZB + 6))) & ~lab["void"]
    out["heat_src"] = phone & (z < ZB + 8) & (x > XR + 100) & (x < XR + 125) & (y < 10)
    return out


def base_design(M=None):
    """발표 '처음 설계 (판 + 기둥)': 20 x 8 mm 직선 보(x' 0–140, z' 20–28) + 2 mm 평판(z' 28–30) — mkbase_int.py.
    Returned in the engine's format: full grid (nz, ny, nx) flattened, 1 = material (fixed parts added by the engine)."""
    c, _ = grid_centres()
    x, y, z = c.T
    beam = (y < 10) & (z > 20) & (z < 28) & (x > 0) & (x < 140)
    plate = (x > -10) & (x < 140) & (z > 28) & (z < 30)
    return (beam | plate).astype(float)


def full_density(rho, M=None):
    """Engine view of a design: r = where(design, rho, fixval)."""
    M = M or masks()
    return np.where(M["design"], np.asarray(rho, float).ravel(), M["solid"].astype(float))


# ------------------------------------------------------------------ conditions (설계 명세 · 판정 기준)
EVIDENCE = None


def evidence():
    global EVIDENCE
    if EVIDENCE is None:
        EVIDENCE = {i["id"]: i for i in json.load(open(os.path.join(PKG, "spec", "evidence_db.json"), encoding="utf-8"))["items"]}
    return EVIDENCE


TEXT_RULES = [   # (regex, key, value builder) — 말 → 물리 해석. 수치는 근거 DB에서만.
    (r"안\s*흔들", "vibration"), (r"울퉁불퉁|자갈|돌길|비포장", "shock"), (r"가볍|가벼", "mass"),
    (r"3D\s*프린터|출력|뽑을", "manufacturing"), (r"모든\s*폰|어떤\s*폰", "phones"),
    (r"열\s*안\s*갇|발열|뜨거", "thermal"), (r"눌러도|터치", "touch"),
]
SKETCH_RULES = [(r"35\s*도", "tilt"), (r"스템\s*옆", "mount_on"), (r"케이블|레버", "keep_out"), (r"\?|물음표", "design_space"),
                (r"모든\s*폰", "phones"), (r"열\s*안\s*갇", "thermal"), (r"눌러도", "touch"), (r"안\s*흔들", "vibration")]


def condition_spec(text=PRESENTATION_TEXT, sketch_note=SKETCH_NOTE, sketch_name="v17_sketch.png"):
    """① 조건 생성기(규칙판): 말 + 스케치 → 설계 명세 (spec/schema.json 형식, 항목마다 source). LLM 없이 같은 결과.
    수치는 근거 DB(spec/evidence_db.json)에서만 고르고, 없으면 questions_to_user 로 묻는다."""
    ev = evidence()
    t, s = text or "", sketch_note or ""
    said = {k for rx, k in TEXT_RULES if re.search(rx, t)}
    drawn = {k for rx, k in SKETCH_RULES if re.search(rx, s)}
    road, petg, sf = ev["road_vib_isbs2020"], ev["petg_prusament"], ev["safety_factor"]
    src = lambda *a: " / ".join(x for x in a if x)
    spec = {
        "_설명": "입력(텍스트 + 스케치)을 규칙판 조건 생성기가 읽어 만든 설계 명세 (팀 spec/schema.json 형식). 각 항목 source = 어디서 왔는지",
        "input": {"text": t, "sketch": sketch_name if s else ""},
        "geometry": {
            "mount_on": {"value": "핸들바 (스템 옆, 정중앙 아님)" if "mount_on" in drawn else "핸들바",
                         "source": "스케치: 위에서 본 그림의 X 표시와 '스템 옆에'" if "mount_on" in drawn else "가정"},
            "phone_position": {"value": "핸들바 위, 라이더 쪽을 향함", "source": "스케치: '여기에 폰!' 위치와 눈 → 폰 시선" if s else "가정"},
            "tilt_deg": {"value": 35, "source": "스케치: '35도쯤' 표기 (근사값)" if "tilt" in drawn else "가정"},
            "keep_out": {"value": ["스템", "브레이크 레버", "케이블"], "source": "스케치: '케이블, 레버 피하기', 스템 X 표시"} if "keep_out" in drawn
            else {"value": [], "source": "가정"},
            "design_space": {"value": "핸들바 클램프와 폰 받침 사이 (스케치의 '?' 상자)", "source": "스케치: '?' 상자 = AI가 정할 영역"
                             if "design_space" in drawn else "가정"},
            "handlebar_diameter_mm": {"value": 31.8, "source": "근거 DB: 로드·MTB 핸들바 클램프부 표준 지름. 스케치·텍스트에 없음 → 사용자 확인 질문"},
        },
        "objectives": {
            "vibration": {"value": f"핸들바 → 폰 진동 전달 최소 ({road['value']['band_hz'][0]}–{road['value']['band_hz'][1]} Hz)",
                          "source": src("텍스트: '안 흔들리게'" if "vibration" in said else "", "스케치: '안 흔들리게!'" if "vibration" in drawn else "")
                          or "가정"},
            "mass": {"value": "최소", "source": "텍스트: '최대한 가볍게'" if "mass" in said else "가정"},
        },
        "constraints": {
            "phones": {"value": "폭 64–90 mm, 두께 6–14 mm, ≤ 290 g, 4면 고정",
                       "source": "스케치: '모든 폰' → 근거 DB: 시판 폰 + 케이스 범위" if "phones" in drawn | said else "근거 DB: 시판 폰 + 케이스 범위"},
            "thermal": {"value": "폰 온도 상승 ≤ 21 °C (발열 4 W 가정)", "source": "스케치: '열 안 갇히게' → 발열량은 가정"},
            "touch": {"value": "화면 5 N 눌러도 처짐 ≤ 0.3 mm", "source": "스케치: '화면 눌러도 안 휘게' → 하중 5 N은 가정"},
            "shock": {"value": f"{road['value']['shock_g']} g 충격에 응력 ≤ {petg['value']['yield_mpa'] / sf['value']['sf']:g} MPa, 층간 ≤ 10.9 MPa",
                      "source": "텍스트·스케치: '울퉁불퉁한 길' → 근거 DB: ISBS 2020 조약돌길 실측"},
            "manufacturing": {"value": "PETG FDM 출력, 층간 강도, 부재 두께 하한", "source": "텍스트: '3D 프린터로 뽑을 거야'"
                              if "manufacturing" in said else "가정"},
        },
        "questions_to_user": [
            "핸들바 지름이 31.8 mm 맞나요? (25.4 / 35 mm도 있음)",
            "거치 각도 35°로 계산할까요? (스케치 근사값)",
            "폰 발열은 내비 사용 기준 4 W로 둘까요?",
        ],
    }
    return spec


def targets(spec=None):
    """설계 명세 → 판정 기준 (spec/schema.json 의 to_targets 규칙) = spec/bike_mount_targets.json."""
    ev = evidence()
    sf = ev["safety_factor"]["value"]["sf"]
    return {"f1_min_hz": 95, "phone_Tmax_rise_max_c": 21, "touch_max_mm": 0.3,
            "shock_vm_max_mpa": round(ev["petg_prusament"]["value"]["yield_mpa"] / sf, 1),
            "shock_interlayer_max_mpa": ev["petg_interlayer"]["value"]["interlayer_max_mpa"]}


# 발표 10쪽의 흔들림 판정(LLM 단독 B '앞뒤 흔들림 2.95배' 불합격, FormProof 1.39배 통과)에 맞춘 참고 기준.
# 근거 DB에 값이 없으므로 '가정'으로 표시하고 사용자에게 묻는다.
SHAKE_LIMIT = 1.5


def physics_conditions():
    """Engine physics as data (what opt_int computes, with sources)."""
    ev = evidence()
    road = ev["road_vib_isbs2020"]["value"]
    t = math.radians(TILT)
    return {
        "frame": dict(tilt_deg=TILT, world="X = x'cos t - z'sin t, Z = x'sin t + z'cos t (핸들바 축 = y)", source="스케치 35° → 질문"),
        "grid": dict(h_mm=H, shape=[NX, NY, NZ], origin=list(ORIGIN), symmetry="y = 0 (절반 모델, 대칭 모드: 위아래·앞뒤·핸들바축 회전)"),
        "material": dict(MATERIAL, source="근거 DB: petg_prusament"),
        "support": dict(name="handlebar", type="fixed", nodes="r <= 16.7 mm (핸들바 구멍 둘레 절점)", source="핸들바 Ø31.8 클램프"),
        "payload": dict(PAYLOAD, model="rigid_body", half_mass_kg=PAYLOAD["mass_kg"] / 2,
                        inertia_about_y_kg_mm2=round(PAYLOAD["mass_kg"] * (165 ** 2 + 15 ** 2) / 12, 1),
                        attach="집게 하우징 윗면 · 받침 턱 · 위 받침 · 아래 걸이 윗면 절점에 최소제곱 강체 연결",
                        parts="폰 + 케이스 ≤ 290 g + 집게 · 걸이 · 스프링 · 나사 = 311 g", source="근거 DB: phone_range + 부품 CAD"),
        "road_vibration": dict(freq_hz=[5, 100], judge_hz=road["band_hz"], damping=0.03,
                               directions={"vert": [round(math.sin(t), 4), round(math.cos(t), 4)], "fore": [round(math.cos(t), 4), round(-math.sin(t), 4)]},
                               measure="폰 무게중심 / 핸들바 진폭, 두 방향 중 큰 값", source="근거 DB: road_vib_isbs2020 (감쇠비 3 % 가정)"),
        "shock": dict(accel_g=road["shock_g"], directions=["vert", "fore"], stress="von Mises 99.9 백분위(클램프 링 r ≤ 19 제외)",
                      interlayer="적층 방향(z') 인장 99.9 백분위", source="근거 DB: road_vib_isbs2020"),
        "touch": dict(force_n=5.0, points_xprime=[XR + 145, XR + 5], limit_mm=0.3, source="스케치 '화면 눌러도 안 휘게' → 5 N 가정"),
        "thermal": dict(heat_w=4.0, k_petg_w_mk=0.2, k_phone_w_mk=15.0, h_ride_w_m2k=23.0, h_front_w_m2k=11.0,
                        source="근거 DB: phone_heat_nav (4 W 가정) · 주행 대류 23 W/m²K 가정"),
        "manufacturing": dict(build_direction="-z' (폰 닿는 판 윗면이 바닥)", am_filter=True, filter_radius_mm=8, source="텍스트 '3D 프린터'"),
        "optimizer": dict(ENGINE_ENV, note="팀 엔진 opt_int.py 기준 결과 설정 (scripts/run_reference.sh)"),
    }


# ------------------------------------------------------------------ comparison shapes (발표 10쪽)
def llm_rho(md_path):
    """LLM 단독 설계(JSON 프리미티브, 폰 좌표) → 격자 rho (nz, ny, nx), 셀당 8점 샘플 — llm2rho.py 와 같은 변환."""
    txt = open(md_path, encoding="utf-8").read()
    J = json.loads(re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", txt, re.S)[-1])
    K, Jj, I = np.meshgrid(np.arange(NZ), np.arange(NY), np.arange(NX), indexing="ij")
    acc = np.zeros(K.shape)
    x0, y0, z0 = ORIGIN
    for dx in (-.5, .5):
        for dy in (-.5, .5):
            for dz in (-.5, .5):
                X = x0 + 2 * I + 1 + dx
                Y = y0 + 2 * Jj + 1 + dy
                Z = z0 + 2 * K + 1 + dz

                def prim(p):
                    t = p["type"]
                    if t == "box":
                        a, b = p["min"], p["max"]
                        return ((X >= min(a[0], b[0])) & (X <= max(a[0], b[0])) & (Y >= min(a[1], b[1])) & (Y <= max(a[1], b[1]))
                                & (Z >= min(a[2], b[2])) & (Z <= max(a[2], b[2])))
                    if t == "cyl_y":
                        cx, cz = p["center_xz"]
                        return ((X - cx) ** 2 + (Z - cz) ** 2 <= p["r"] ** 2) & (Y >= min(p["y"])) & (Y <= max(p["y"]))
                    if t == "rod":
                        a = np.array(p["p0"], float)
                        b = np.array(p["p1"], float)
                        P = np.stack([X, Y, Z], -1)
                        ab = b - a
                        tt = np.clip(((P - a) @ ab) / (ab @ ab + 1e-9), 0, 1)
                        return np.linalg.norm(P - (a + tt[..., None] * ab), axis=-1) <= p["r"]
                    raise ValueError(t)
                S = np.zeros(K.shape, bool)
                for p in J["primitives"]:
                    if p.get("op", "add") != "sub":
                        S |= prim(p)
                for p in J["primitives"]:
                    if p.get("op", "add") == "sub":
                        S &= ~prim(p)
                acc += S
    return (acc / 8 >= 0.5).astype(float).ravel(), J


def vox_stl(path_world, nx=NX):
    """출력 STL(세계 좌표) → 폰 좌표로 되돌려 격자 점유율 (vox.py 와 같은 방법: 층 단면 · 셀당 8점)."""
    import manifold3d as mf
    import trimesh
    from matplotlib.path import Path
    T = trimesh.load(path_world)
    T.apply_transform(trimesh.transformations.rotation_matrix(math.radians(TILT), [0, 1, 0]))   # world -> phone frame
    A = mf.Manifold(mf.Mesh(vert_properties=np.asarray(T.vertices, np.float32), tri_verts=np.asarray(T.faces, np.uint32)))
    r = np.zeros((NZ, NY, nx))
    X, Y = np.meshgrid(-24 + 2 * np.arange(nx) + 1, 2 * np.arange(NY) + 1)
    for k in range(NZ):
        acc = np.zeros(X.shape)
        for dz in (-.5, .5):
            cs = A.slice(-36 + 2 * k + 1 + dz).to_polygons()
            for dx in (-.5, .5):
                for dy in (-.5, .5):
                    p = np.c_[(X + dx).ravel(), (Y + dy).ravel()]
                    w = np.zeros(len(p))
                    for poly in cs:
                        w += Path(poly).contains_points(p)
                    acc += (w % 2).reshape(X.shape)
        r[k] = acc / 8
    return (r.ravel() >= 0.5).astype(float)


SHAPES = [   # id, 이름, 발표 표기, 만드는 방법
    ("base", "처음 설계 (판 + 기둥)", "7·22쪽 처음 설계", "클램프 + 20×8 mm 직선 보 + 2 mm 평판 (mkbase_int.py)"),
    ("llm_A", "LLM 단독 A", "10쪽", "LLM 단독 세션 L1 의 JSON 프리미티브 → 격자 (llm2rho.py)"),
    ("llm_B", "LLM 단독 B", "10쪽", "LLM 단독 세션 L2"),
    ("llm_C", "LLM 단독 C", "10쪽", "LLM 단독 세션 L3"),
    ("formproof", "FormProof 최적화 결과", "10쪽 FormProof (출력 변환 전)", "위상 최적화 int35f95g2 120회 (topopt_snapshots)"),
    ("formproof_body", "FormProof 출력 몸체", "7·22쪽 최종 형상 검증", "출력 STL body_v3 → 재격자화 (vox.py)"),
]


def build_shapes():
    """Comparison shapes -> templates/db/integral_shapes.npz (packed bits of the full grid)."""
    out = {"base": base_design()}
    for k, n in (("llm_A", 1), ("llm_B", 2), ("llm_C", 3)):
        out[k] = llm_rho(os.path.join(LLM_DIR, f"L{n}.md"))[0]
    d = np.load(os.path.join(PKG, "data", "topopt_snapshots.npz"))
    names = [str(x) for x in d["names"]]
    out["formproof"] = np.unpackbits(d["r"][names.index("snap_int35f95g2_119.npy")])[:NX * NY * NZ].astype(float)
    out["formproof_body"] = vox_stl(os.path.join(PKG, "data", "reference", "body_v3_world.stl"))
    np.savez_compressed(SHAPES_DB, **{k: np.packbits(v > 0.5) for k, v in out.items()})
    return out


def shape(name):
    if name == "base":
        return base_design()
    d = np.load(SHAPES_DB)
    return np.unpackbits(d[name])[:NX * NY * NZ].astype(float)


# ------------------------------------------------------------------ evaluation (team engine)
def _sha(r):
    return hashlib.sha1(np.packbits(np.asarray(r).ravel() > 0.5).tobytes()).hexdigest()[:16]


def evaluate(rho, tag="p01", use_cache=True, timeout=1800):
    """팀 엔진 MODE=eval (opt_int.py) 그대로: 진동 전달 · 고유진동수 · 충격 · 층간 · 터치 · 폰 온도 · 무게.
    결과는 형상 해시로 캐시 (templates/db/integral_eval.json)."""
    key = _sha(rho)
    cache = json.load(open(EVAL_DB, encoding="utf-8")) if os.path.exists(EVAL_DB) else {}
    if use_cache and key in cache:
        return cache[key]
    if not os.path.exists(ENGINE):
        raise FileNotFoundError(f"팀 엔진이 없습니다: {ENGINE} (master 의 11_구현패키지)")
    with tempfile.TemporaryDirectory() as td:
        rp = os.path.join(td, "rho.npy")
        np.save(rp, np.asarray(rho, float).ravel())
        env = dict(os.environ, **{k: v for k, v in ENGINE_ENV.items() if k in ("GRIP", "NX", "MSYS", "TILT", "DLIM", "TLIM", "FT")},
                   MODE="eval", RHO=rp, TAG=tag)
        p = subprocess.run([sys.executable, ENGINE], cwd=td, env=env, capture_output=True, text=True, timeout=timeout)
        if p.returncode:
            raise RuntimeError("엔진 실패: " + (p.stderr or p.stdout)[-1500:])
        res = json.load(open(os.path.join(td, f"frfint_{tag}.json")))
    res["engine"] = "11_구현패키지/FormProof_구현/engine/opt_int.py MODE=eval GRIP=2 NX=88 MSYS=0.311 TILT=35"
    cache = json.load(open(EVAL_DB, encoding="utf-8")) if os.path.exists(EVAL_DB) else {}
    cache[key] = res
    with open(EVAL_DB, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, separators=(",", ":"))
    return res


def judge(res, tg=None):
    """판정 (팀 agent/pipeline.py gate 와 같은 항목) + 흔들림 참고 기준."""
    tg = tg or targets()
    shake = max(res["vert"]["peak"], res["fore"]["peak"])
    sdir = "앞뒤" if res["fore"]["peak"] >= res["vert"]["peak"] else "위아래"
    vm = max(res["shock"]["vert"]["vm999"], res["shock"]["fore"]["vm999"])
    il = max(res["shock"]["vert"]["interlayer999"], res["shock"]["fore"]["interlayer999"])
    rows = [
        dict(key="f1", name="1차 고유진동수", value=res["f"][0], unit="Hz", op=">=", limit=tg["f1_min_hz"], source="근거 DB: ISBS 2020 → 95 Hz"),
        dict(key="Tmax", name="폰 온도 상승", value=res["Tmax"], unit="°C", op="<=", limit=tg["phone_Tmax_rise_max_c"], source="스케치 '열 안 갇히게' · 4 W 가정"),
        dict(key="touch", name="화면 5 N 터치 처짐", value=max(res["touch_mm"]), unit="mm", op="<=", limit=tg["touch_max_mm"], source="스케치 '눌러도 안 휘게'"),
        dict(key="stress", name="충격 최대 응력", value=vm, unit="MPa", op="<=", limit=tg["shock_vm_max_mpa"], source="48.5 g · PETG 39 ÷ 1.5"),
        dict(key="interlayer", name="충격 층간 응력", value=il, unit="MPa", op="<=", limit=tg["shock_interlayer_max_mpa"], source="출력 층간 강도 (확인 필요)"),
        dict(key="shake", name=f"최대 흔들림 (10–100 Hz, {sdir})", value=shake, unit="배", op="<=", limit=SHAKE_LIMIT,
             source="가정 — 발표 10쪽 판정에 맞춤, 사용자 확인 질문", reference=False),
    ]
    for r in rows:
        r["ok"] = bool(r["value"] >= r["limit"] if r["op"] == ">=" else r["value"] <= r["limit"])
    fails = [r["name"] for r in rows if not r["ok"]]
    return dict(rows=rows, pass_=not fails, fails=fails, mass_g=res["mass_g"], shake=shake, shake_dir=sdir)


# ------------------------------------------------------------------ CAD (1차 설계 = 처음 설계, 출력 형상)
def _team_parts():
    import importlib.util
    spec = importlib.util.spec_from_file_location("fp_team_parts", os.path.join(PKG, "cad", "parts.py"))
    mod = importlib.util.module_from_spec(spec)
    cwd = os.getcwd()
    try:
        os.chdir(tempfile.gettempdir())
        spec.loader.exec_module(mod)
    finally:
        os.chdir(cwd)
    return mod


def build_cad():
    """처음 설계 (판 + 기둥) 출력 형상: 클램프 링 · 볼트 귀 + 보 + 평판 + 고정 부품(팀 cad/parts.py 의 집게 하우징 ·
    아래 걸이 · 위 레일) − 채널 · 슬롯 · 구멍 (팀 cad/build_body.py 와 같은 치수). Returns (world, phone-frame) workplanes."""
    import cadquery as cq
    P = _team_parts()
    box = P.box
    rot = lambda w, a: w.rotate((0, 0, 0), (0, 1, 0), a)          # +35: world -> phone frame, -35: phone -> world
    ring = cq.Workplane("XZ").circle(20.6).extrude(10, both=True)
    ears = rot(box(1, 9, -10, 10, -34, -14).union(box(-9, -1, -10, 10, -34, -14)), TILT)
    beam = box(0, 140, -10, 10, 20, 28)
    plate = box(-10, 140, -40, 40, 28, 30)
    band = box(56, 74, -40, 40, 24, 28)
    ledge = box(-10, -2, -16, 16, 24, 30)
    toppad = box(126, 140, -16, 16, 24, 30)
    body = ring.union(ears).union(beam).union(plate).union(band).union(ledge).union(toppad).union(P.H).union(P.K).union(P.HT)
    cut = []
    for s in (1, -1):
        cut += [box(59.95, 70.05, 4.95 if s > 0 else -43, 43 if s > 0 else -4.95, 19.95, 28.05),
                box(60.95, 69.05, 25.95 if s > 0 else -43, 43 if s > 0 else -25.95, 26.95, 31.5),
                cq.Workplane().circle(1.7).extrude(30).translate((65, 30 * s, 7))]
    cut += [box(103.95, 152, -5.05, 5.05, 13.95, 22.05), box(127.95, 152, -4.25, 4.25, 20.95, 31)]
    cut += [cq.Workplane("XZ").circle(1.7).extrude(7, both=True).translate((140, 10, 18)), box(137.25, 142.75, 6.95, 9.65, 14.95, 21.05)]
    for s in (1, -1):
        cut += [cq.Workplane("YZ").circle(1.7).extrude(4, both=True).translate((57, 20 * s, 24)),
                box(56.25, 59.05, 20 * s - 2.8, 20 * s + 2.8, 20.95, 27.05)]
    cut.append(cq.Workplane("XZ").circle(16.0).extrude(100, both=True))                     # 핸들바 Ø31.8 + 여유
    cut.append(rot(box(-1, 1, -60, 60, -28, 0), TILT))                                         # 조임 슬릿 (세계 |X| < 1, Z < 0)
    cut.append(rot(cq.Workplane("YZ").circle(2.25).extrude(20, both=True).translate((0, 0, -24)), TILT))   # M4 볼트 구멍
    cut.append(box(-10.05, 160, -46, 46, 30.02, 44.5))                                         # 폰 공간 (두께 14 까지), 걸이 제외
    for c in cut:
        body = body.cut(c)
    return rot(body, -TILT), body


def print_body(rho_full):
    """출력용 몸체 — 팀 cad/build_body.py 와 같은 절차: 격자 밀도(2 mm) → 0.5 mm 보간 · 평활 표면 + 정밀 집게 하우징 ·
    아래 걸이 · 위 레일(cad/parts.py) 결합 − 채널 · 슬롯 · 핀/볼트 구멍 · 핸들바 구멍 · 폰 공간. 발표 그림의 형상과 같은 방법.
    Returns (world trimesh, phone-frame trimesh)."""
    import manifold3d as mf
    import trimesh
    import cadquery as cq
    from scipy import ndimage
    from skimage import measure
    P = _team_parts()
    r = np.asarray(rho_full, float).reshape(NZ, NY, NX)
    full = np.concatenate([r[:, ::-1], r], 1)
    up = ndimage.zoom(np.pad(full, 2), 4, order=1)
    v = ndimage.gaussian_filter(up, 1.6)
    vs, f, _, _ = measure.marching_cubes(v, 0.5, spacing=(.5, .5, .5))
    z = vs[:, 0] - 4 + (-36) + 0.75
    y = vs[:, 1] - 4 + (-40) + 0.75
    x = vs[:, 2] - 4 + (-24) + 0.75
    body = trimesh.Trimesh(np.c_[x, y, z], f)
    body = max(body.split(only_watertight=False), key=lambda m: abs(m.volume))
    if body.volume < 0:
        body.invert()
    body.merge_vertices()
    trimesh.repair.fix_normals(body)
    M = lambda t: mf.Manifold(mf.Mesh(vert_properties=np.asarray(t.vertices, np.float32), tri_verts=np.asarray(t.faces, np.uint32)))

    def cqm(w):
        with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tf:
            pth = tf.name
        cq.exporters.export(w, pth, tolerance=0.02)
        t = trimesh.load(pth)
        os.unlink(pth)
        t.merge_vertices()
        return M(t)

    def bx(x0, x1, y0, y1, z0, z1):
        return mf.Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])

    def cyl(rr, h, ax, c):
        m = mf.Manifold.cylinder(h, rr, rr, 64).translate([0, 0, -h / 2])
        if ax == "y":
            m = m.rotate([90, 0, 0])
        if ax == "x":
            m = m.rotate([0, 90, 0])
        return m.translate(c)
    U = M(body) + cqm(P.H) + cqm(P.K) + cqm(P.HT)
    t = math.radians(TILT)
    w2p = lambda X, Z: (X * math.cos(t) + Z * math.sin(t), -X * math.sin(t) + Z * math.cos(t))
    cut = []
    for s_ in (1, -1):
        cut += [bx(59.95, 70.05, 4.95 if s_ > 0 else -43, 43 if s_ > 0 else -4.95, 19.95, 28.05),
                bx(60.95, 69.05, 25.95 if s_ > 0 else -43, 43 if s_ > 0 else -25.95, 26.95, 31.5), cyl(1.7, 30, "z", [65, 30 * s_, 22])]
    cut += [bx(103.95, 152, -5.05, 5.05, 13.95, 22.05), bx(127.95, 152, -4.25, 4.25, 20.95, 31)]
    cut += [cyl(1.7, 14, "y", [140, 10, 18]), bx(137.25, 142.75, 6.95, 9.65, 14.95, 21.05)]
    for s_ in (1, -1):
        cut += [cyl(1.7, 8, "x", [57, 20 * s_, 24]), bx(56.25, 59.05, 20 * s_ - 2.8, 20 * s_ + 2.8, 20.95, 27.05)]
    cut.append(cyl(16.0, 200, "y", [0, 0, 0]))
    cut.append(bx(-1, 1, -60, 60, -28, 0).rotate([0, -35, 0]))
    xb, zb = w2p(0, -24)
    cut.append(cyl(2.25, 40, "x", [0, 0, 0]).rotate([0, -35, 0]).translate([xb, 0, zb]))
    cut.append(bx(-10.05, 160, -46, 46, 30.02, 44.5))
    for c in cut:
        U = U - c
    m = U.to_mesh()
    T = trimesh.Trimesh(m.vert_properties[:, :3], m.tri_verts)
    W = T.copy()
    W.apply_transform(trimesh.transformations.rotation_matrix(-t, [0, 1, 0]))
    return W, T


def phone_world(W=76.0, L=160.0, T=8.0):
    """폰 (세계 좌표 자세): 중심, 크기, 기울기 — 3D 보기용."""
    cx, cz = XR + L / 2, ZB + 6 + T / 2
    t = math.radians(TILT)
    return dict(center=[cx * math.cos(t) - cz * math.sin(t), 0.0, cx * math.sin(t) + cz * math.cos(t)], H=L, W=W, D=T, tilt_deg=TILT)


# ------------------------------------------------------------------ sketch (대략)
def side_strokes(phone=True, include=("ring", "bar", "ears", "beam", "plate", "hook", "housing", "rail")):
    """대략적인 측면 스케치 (세계 좌표 mm): 클램프 링 · 핸들바 · 볼트 귀 · 보 · 평판 · 걸이 · 집게 하우징 · 레일 · 폰."""
    t = math.radians(TILT)
    w = lambda x, z: np.array([x * math.cos(t) - z * math.sin(t), x * math.sin(t) + z * math.cos(t)])
    rect = lambda x0, x1, z0, z1: np.array([w(x0, z0), w(x1, z0), w(x1, z1), w(x0, z1), w(x0, z0)])
    a = np.linspace(0, 2 * np.pi, 49)
    S = []
    if "ring" in include:
        S.append(("ring", np.c_[20.6 * np.cos(a), 20.6 * np.sin(a)]))
    if "bar" in include:
        S.append(("bar", np.c_[15.9 * np.cos(a), 15.9 * np.sin(a)]))
    if "ears" in include:
        S += [("ears", np.array([[1, -14], [9, -14], [9, -34], [1, -34], [1, -14]], float)),
              ("ears", np.array([[-1, -14], [-9, -14], [-9, -34], [-1, -34], [-1, -14]], float))]
    if "beam" in include:
        S.append(("beam", rect(0, 140, 20, 28)))
    if "plate" in include:
        S.append(("plate", rect(-10, 140, 28, 30)))
    if "hook" in include:
        S.append(("hook", np.array([w(-10, 30), w(-16, 30), w(-16, 47), w(-6, 47), w(-6, 44), w(-10, 44)])))
    if "housing" in include:
        S.append(("housing", rect(55, 75, 18, 28)))
        S.append(("jaw", np.array([w(57, 30), w(57, 47), w(69, 47)])))
    if "rail" in include:
        S.append(("rail", rect(102, 150, 12, 24)))
        S.append(("tophook", np.array([w(150, 30), w(150, 47), w(146, 47)])))
    if phone:
        S.append(("phone", rect(-10, 150, 30, 38)))
    return S


def side_skeleton(phone=True):
    """중심선 스케치: 링 · 보 중심선 · 판 · 걸이 · (폰)."""
    t = math.radians(TILT)
    w = lambda x, z: [x * math.cos(t) - z * math.sin(t), x * math.sin(t) + z * math.cos(t)]
    a = np.linspace(0, 2 * np.pi, 49)
    out = [("ring", np.c_[18.35 * np.cos(a), 18.35 * np.sin(a)]),
           ("ear", np.array([[5.0, -14.0], [5.0, -34.0]])), ("ear", np.array([[-5.0, -14.0], [-5.0, -34.0]])),
           ("arm", np.array([w(0, 24), w(140, 24)])), ("pad", np.array([w(-10, 29), w(140, 29)])),
           ("stem", np.array([w(-13, 30), w(-13, 47)])), ("stem", np.array([w(65, 24), w(65, 47)]))]
    if phone:
        out.append(("phone", np.array([w(-10, 34), w(150, 34)])))
    return out


def side_grid_png(rho, path, title=""):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    M = masks()
    r = full_density(rho, M).reshape(NZ, NY, NX)
    occ = r.max(1)
    solid = M["solid"].reshape(NZ, NY, NX).max(1)
    void = M["void"].reshape(NZ, NY, NX).min(1)
    img = np.ones((NZ, NX, 3))
    img[~void] = (0.93, 0.95, 0.97)
    img[occ > 0.5] = (0.17, 0.64, 0.65)
    img[solid & (occ > 0.5)] = (0.85, 0.6, 0.35)
    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.imshow(img, origin="lower", extent=[ORIGIN[0], ORIGIN[0] + NX * H, ORIGIN[2], ORIGIN[2] + NZ * H])
    a = np.linspace(0, 2 * np.pi, 80)
    ax.plot(15.9 * np.cos(a), 15.9 * np.sin(a), color="#555", lw=1)
    ax.add_patch(plt.Rectangle((XR, ZB + 6), 150, 8, fill=False, ls="--", color="#c0392b"))
    ax.set_title(title or "1차 설계 — 폰 판 좌표 측면 (청록 = 재료, 주황 = 고정 부품, 회색 = 설계 영역)", fontsize=9)
    ax.set_xlabel("x' (폰 길이 방향, mm)")
    ax.set_ylabel("z' (판 법선, mm)")
    ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def drawing_png(world_body, path, mass_g, title="자전거 폰 거치대 — 1차 설계 (처음 설계: 판 + 기둥)", pdf=None):
    """측면(세계) · 위(폰 판 좌표) 두 장 도면 (대략 치수)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    verts, tris = world_body.val().tessellate(0.1, 0.3)
    V = np.array([[p.x, p.y, p.z] for p in verts])
    F = np.array(tris)
    fig, ax = plt.subplots(1, 2, figsize=(15, 6.2), gridspec_kw=dict(width_ratios=[1.0, 1.1]))
    a = ax[0]
    a.add_collection(PolyCollection(V[F][:, :, [0, 2]], fc="#d6e9e7", ec="none"))
    tt = np.linspace(0, 2 * np.pi, 100)
    a.plot(15.9 * np.cos(tt), 15.9 * np.sin(tt), c="#333", lw=1)
    t = math.radians(TILT)
    w = lambda x, z: (x * math.cos(t) - z * math.sin(t), x * math.sin(t) + z * math.cos(t))
    p0, p1 = w(-10, 30), w(150, 30)
    a.plot([p0[0], p1[0]], [p0[1], p1[1]], c="#c0392b", lw=.8, ls="--")
    a.text(*w(60, 40), "폰 뒷면 (35°)", color="#c0392b", fontsize=8, rotation=TILT)
    a.text(-20, -50, "핸들바 Ø31.8 · 클램프 폭 20 · M4 볼트", fontsize=8)
    a.set_title("옆 (세계 좌표, 핸들바 중심 = 원점)", fontsize=10)
    a.set_xlim(-60, 140)
    a.set_ylim(-60, 120)
    a.set_aspect("equal")
    a.grid(alpha=.25)
    Vp = V.copy()
    Vp[:, 0], Vp[:, 2] = V[:, 0] * math.cos(t) + V[:, 2] * math.sin(t), -V[:, 0] * math.sin(t) + V[:, 2] * math.cos(t)
    b = ax[1]
    b.add_collection(PolyCollection(Vp[F][:, :, [0, 1]], fc="#d6e9e7", ec="none"))
    for (x0, x1, lab) in ((0, 140, "보 20 × 8 (x' 0–140)"), (-10, 140, "평판 2 mm (x' −10–140, 폭 80)")):
        pass
    b.annotate("", (-10, -46), (140, -46), arrowprops=dict(arrowstyle="<->", lw=.7))
    b.text(65, -52, "평판 150 (x' −10 – 140)", ha="center", fontsize=8)
    b.annotate("", (150, -40), (150, 40), arrowprops=dict(arrowstyle="<->", lw=.7))
    b.text(153, 0, "80", fontsize=8, va="center")
    b.text(65, 46, "집게 하우징 x' 55–75 · 위 레일 x' 102–150 · 아래 걸이 x' −16–−10", ha="center", fontsize=7.5)
    b.set_title("위 (폰 판 좌표, 화면 쪽에서)", fontsize=10)
    b.set_xlim(-35, 165)
    b.set_ylim(-60, 60)
    b.set_aspect("equal")
    b.grid(alpha=.25)
    fig.suptitle(f"{title} · PETG · {mass_g:.1f} g · 단위 mm", fontsize=12)
    fig.text(.5, .02, "보 20×8 mm 단면 · 평판 2 mm · 고정 부품(집게 하우징 · 아래 걸이 · 위 레일 · 클램프)은 팀 cad/parts.py 와 같은 치수 · "
             "출력 방향: 폰 뒷면이 바닥(적층 = 판 법선)", ha="center", fontsize=8, color="#555")
    fig.savefig(path, dpi=130, bbox_inches="tight")
    if pdf:
        fig.savefig(pdf, bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------------------ demo routing (스케치 인식은 이후 단계: 지금은 DB)
DEMO_SKETCHES = [os.path.join(INPUT_ROOT, "examples", "presentation", "input_sketch.png")]
_DEMO_FP = None


def _fingerprint(gray):
    """Ink thumbnail 64 x 45 (area mean), zero-mean unit-norm — survives rescaling / re-encoding of the same picture."""
    from skimage.transform import resize
    g = np.asarray(gray, float)
    if g.ndim == 3:
        g = g[..., :3].mean(-1)
    if g.max() > 1.5:
        g = g / 255.0
    ink = 1.0 - g
    ys, xs = np.where(ink > 0.35)                     # crop to the ink (canvas letterbox / margins)
    if len(xs) > 50:
        ink = ink[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    t = resize(ink, (45, 64), anti_aliasing=True)
    t = t - t.mean()
    return t / (np.linalg.norm(t) + 1e-9)


def matches_presentation_sketch(gray, thr=0.85):
    global _DEMO_FP
    if _DEMO_FP is None:
        from skimage import io
        _DEMO_FP = [_fingerprint(io.imread(p) / 255.0) for p in DEMO_SKETCHES if os.path.exists(p)]
    f = _fingerprint(gray)
    return any(float((f * d).sum()) >= thr for d in _DEMO_FP)


def is_presentation_text(text):
    t = re.sub(r"[\s.,!?~·]", "", text or "")
    key = re.sub(r"[\s.,!?~·]", "", PRESENTATION_TEXT)
    return "일체형" in t or key in t


# ------------------------------------------------------------------ pipeline
def frf_payload(res):
    fr = res["freq"]
    return {"z": dict(freq=fr, T=res["vert"]["T"], Tmax_band=res["vert"]["peak"]),
            "x": dict(freq=fr, T=res["fore"]["T"], Tmax_band=res["fore"]["peak"])}


def compare_rows():
    """발표 10쪽 비교표 (+ 처음 설계 · 출력 몸체): 같은 엔진 · 같은 조건 판정."""
    pred = {}
    for k, n in (("llm_A", 1), ("llm_B", 2), ("llm_C", 3)):
        J = llm_rho_meta(n)
        pred[k] = J
    rows = []
    tg = targets()
    for sid, name, slide, how in SHAPES:
        res = evaluate(full_density(shape(sid)), tag=sid)
        j = judge(res, tg)
        rows.append(dict(id=sid, name=name, slide=slide, how=how, mass_g=res["mass_g"], f1=res["f"][0], shake=j["shake"],
                         shake_dir=j["shake_dir"], Tmax=res["Tmax"], pass_=j["pass_"], fails=j["fails"], predicted=pred.get(sid)))
    return rows


def llm_rho_meta(n):
    txt = open(os.path.join(LLM_DIR, f"L{n}.md"), encoding="utf-8").read()
    J = json.loads(re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", txt, re.S)[-1])
    return dict(criteria=J.get("criteria"), predicted=J.get("predicted"))


HANDOFF = ["spec.json", "design_spec.json", "targets.json", "problem.npz", "initial_design.npy", "engine_env.json",
           "design_1st.step", "design_1st.stl", "design_1st_drawing.pdf", "report.json"]


def design(text="", out="out", with_mesh=False, sketch_note=None, chosen_by="텍스트", match=None, tid="P01", name=None):
    """P01: 말(+ 스케치) → 설계 명세 · 판정 기준 · 1차 설계(격자 · CAD · 도면) · 팀 엔진 판정 · 넘길 파일."""
    t0 = time.time()
    os.makedirs(out, exist_ok=True)
    note = SKETCH_NOTE if sketch_note is None else sketch_note
    dspec = condition_spec(text or PRESENTATION_TEXT, note)
    tg = targets(dspec)
    phys = physics_conditions()
    M = masks()
    rho = base_design(M)
    full = full_density(rho, M)
    res = evaluate(full, tag="p01_base")
    j = judge(res, tg)
    spec = dict(format="formproof.spec/0.1", kind="integral_mount", template=dict(id=tid, name=name or "일체형 거치대 (발표 사례)"),
                design_spec=dspec, targets=tg, physics=phys,
                regions=[dict(name=r["name"], role=r["role"], why=r["why"], shape=r["shape"], **({"minus": r["minus"]} if "minus" in r else {}))
                         for r in REGIONS],
                counts=dict(design=int(M["design"].sum()), solid=int(M["solid"].sum()), void=int(M["void"].sum())),
                first_design=dict(name="처음 설계 (판 + 기둥)", rule="보 y<10 · z' 20–28 · x' 0–140 + 평판 x' −10–140 · z' 28–30 (mkbase_int.py)"),
                assumptions=[
                    "발표 계산과 같은 팀 엔진(opt_int.py, GRIP=2 NX=88 MSYS=0.311 TILT=35)으로 판정 — 수치 = 발표 7·10·22쪽",
                    "폰 + 고정 부품 311 g 강체(165 × 80 × 15 mm), 절반 모델 대칭 모드(위아래 · 앞뒤 · 핸들바축 회전)만",
                    "감쇠비 3 %, 폰 발열 4 W, 터치 5 N, 층간 강도 10.9 MPa = 가정(근거 DB '확인 필요')",
                    f"최대 흔들림 ≤ {SHAKE_LIMIT}배는 발표 10쪽 판정에 맞춘 참고 기준(가정)"])
    with open(os.path.join(out, "spec.json"), "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=1)
    with open(os.path.join(out, "design_spec.json"), "w", encoding="utf-8") as f:
        json.dump(dspec, f, ensure_ascii=False, indent=1)
    with open(os.path.join(out, "targets.json"), "w", encoding="utf-8") as f:
        json.dump(dict(_설명="설계 명세에서 계산에 쓰는 판정 기준 (팀 엔진 FT · TLIM · DLIM 과 같은 값)", **tg), f, ensure_ascii=False, indent=1)
    with open(os.path.join(out, "engine_env.json"), "w", encoding="utf-8") as f:
        json.dump(dict(env=ENGINE_ENV, start_rho="initial_design.npy (START_RHO 로 넘기면 1차 설계에서 시작)",
                       run="cd 11_구현패키지/FormProof_구현/engine && env $(cat env) python3 opt_int.py",
                       eval="MODE=eval RHO=initial_design.npy"), f, ensure_ascii=False, indent=1)
    np.savez_compressed(os.path.join(out, "problem.npz"), design=M["design"], solid=M["solid"], void=M["void"], plate=M["plate"],
                        phone=M["phone"], attach=M["attach"], heat_src=M["heat_src"], centres=M["centres"].astype(np.float32),
                        shape=np.array([NZ, NY, NX]), h=H, origin=np.array(ORIGIN))
    np.save(os.path.join(out, "initial_design.npy"), rho)
    side_grid_png(rho, os.path.join(out, "side_view.png"), f"{tid} 처음 설계 (판 + 기둥) — 측면, 폰 판 좌표")
    import cadquery as cq
    pw_world, _ = print_body(full)                      # 출력용 몸체 (발표와 같은 절차) -> STL · 무게 · 3D 보기
    pw_world.export(os.path.join(out, "design_1st.stl"))
    mass_g = round(pw_world.volume * MATERIAL["density_g_cm3"] * 1e-3, 1)
    world, _ = build_cad()                               # 파라메트릭 CAD (평활 전, 편집용) -> STEP
    cq.exporters.export(world, os.path.join(out, "design_1st.step"), exportType="STEP")
    vol = world.val().Volume()
    step_g = round(vol * MATERIAL["density_g_cm3"] * 1e-3, 1)
    drawing_png(world, os.path.join(out, "design_1st_drawing.png"), mass_g, pdf=os.path.join(out, "design_1st_drawing.pdf"))
    shake_ok = next(r for r in j["rows"] if r["key"] == "shake")
    checks = {
        "transmissibility": dict(value=j["shake"], limit=f"<= {SHAKE_LIMIT}", pass_=shake_ok["ok"], label="최대 흔들림 (10–100 Hz)"),
        "f1": dict(value=res["f"][0], limit=f">= {tg['f1_min_hz']}", pass_=res["f"][0] >= tg["f1_min_hz"]),
        "stress": dict(value=max(res["shock"]["vert"]["vm999"], res["shock"]["fore"]["vm999"]), limit=f"<= {tg['shock_vm_max_mpa']}"),
        "interlayer": dict(value=max(res["shock"]["vert"]["interlayer999"], res["shock"]["fore"]["interlayer999"]),
                           limit=f"<= {tg['shock_interlayer_max_mpa']}"),
    }
    checks["stress"]["pass_"] = checks["stress"]["value"] <= tg["shock_vm_max_mpa"]
    checks["interlayer"]["pass_"] = checks["interlayer"]["value"] <= tg["shock_interlayer_max_mpa"]
    for c in checks.values():
        c["pass"] = bool(c.pop("pass_"))
    rep = dict(kind="integral", input=dict(text=text, sketch_note=note),
               text=dict(fired=[dict(rule=k, effect={}, why=v["source"]) for sec in ("geometry", "objectives", "constraints")
                                for k, v in dspec[sec].items() if v["source"] != "가정"],
                         questions=dspec["questions_to_user"] + [f"최대 흔들림 허용을 {SHAKE_LIMIT}배로 둘까요? (발표 판정 기준, 근거 DB 없음)"]),
               template=dict(id=tid, name=name or "일체형 거치대 (발표 사례)", desc="클램프 + 판 + 기둥, 폰 4면 고정 부품(집게 · 걸이 · 레일) — 발표 7·10쪽",
                             chosen_by=chosen_by, match=match),
               design_spec=dspec, targets=tg, physics=phys, judge=j, engine_result={k: v for k, v in res.items() if k not in ("freq",)},
               first_design_check=dict(checks=checks, frf=frf_payload(res), pass_=j["pass_"], **{"pass": j["pass_"]},
                                       extra=[r for r in j["rows"] if r["key"] in ("Tmax", "touch")], f=res["f"][:4]),
               compare=compare_rows(),
               problem=dict(elements=spec["counts"], grid=[NX, NY, NZ], h=H),
               criteria=[dict(id=r["key"], rule=f"{r['name']} {r['op']} {r['limit']} {r['unit']}", why=r["source"], source=r["source"]) for r in j["rows"]],
               assumptions=spec["assumptions"],
               design_vars=dict(bar_d=31.8, width=20, tilt_deg=TILT, beam="20 × 8 mm 직선 보 (x' 0–140)", plate="2 mm 평판 150 × 80",
                                payload_g=311, material=MATERIAL["name"], arm_t=8),
               summary=dict(product="자전거 폰 거치대 (일체형)", road="조약돌길 실측 (ISBS 2020)", vib="10–100 Hz", shock_g=48.5,
                            phone="모든 폰 (폭 64–90 · 두께 6–14 · ≤ 290 g)", point_mass_g=311, bar_d=31.8, objective="무게 최소 · 흔들림 최소",
                            safety_factor=1.5, material=MATERIAL["name"], requirements=["폰 온도 상승 ≤ 21 °C", "터치 처짐 ≤ 0.3 mm", "출력 층간 강도"]),
               cad=dict(step="design_1st.step", stl="design_1st.stl", mass_g=mass_g, step_mass_g=step_g, grid_mass_g=res["mass_g"],
                        note="STL = 출력용 몸체(팀 build_body 절차: 격자 평활 + 고정 부품 결합 − 구멍), STEP = 같은 치수의 파라메트릭 형상(평활 전)"),
               drawing=dict(sheet="A3", scale="비율 없음(PNG)"),
               payload=dict(model="rigid_body", total_g=311, integral=True),
               handoff_requirements=[], seconds=round(time.time() - t0, 2))
    with open(os.path.join(out, "report.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)
    import zipfile
    with zipfile.ZipFile(os.path.join(out, "handoff.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for n in HANDOFF:
            if os.path.exists(os.path.join(out, n)):
                z.write(os.path.join(out, n), n)
    if with_mesh:
        from .templates.bike_mount import Y_SYM                        # 스템 옆 (다른 템플릿과 같은 자리)
        mm = pw_world.copy()
        mm.vertices[:, 1] += Y_SYM
        pos = mm.vertices[mm.faces].reshape(-1, 3).astype(np.float32)
        rep["mesh"] = dict(pos=base64.b64encode(pos.tobytes()).decode(), triangles=int(len(mm.faces)))
        pw = phone_world()
        c = [pw["center"][0], Y_SYM, pw["center"][2]]
        rep["phone"] = dict(H=pw["H"], W=pw["W"], D=pw["D"], cog=[c[0], c[2]], clamp_t=0, pose=dict(center=c, tilt_deg=TILT))
        rep["geometry"] = dict(y_sym=Y_SYM, pad=dict(z=[0, 30]), bar_d=31.8, ring_ro=20.6)
    return rep
