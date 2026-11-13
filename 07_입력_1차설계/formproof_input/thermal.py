"""Requirement '여름 땡볕에서 변형이 없도록' -> sun-heated part temperature vs heat-deflection limit.

Two scenarios: parked in the sun (still air, phone weight only = 1 g static load) and riding
(forced convection, vibration criteria apply). The deflection limit is the material HDT at the
part's own static stress level (ISO 75 gives HDT at 0.45 and 1.8 MPa; linear in between)."""
import math
from scipy.optimize import brentq
from . import evidence as ev

SIGMA = 5.67e-8


def surface_temp(absorptance, h, sun=None):
    """Steady temperature (°C) of a thin part lit on one face, convecting and radiating on both faces."""
    s = sun or ev.SUN
    Ta = s["air_c"] + 273.15
    Tsky, Tg = Ta + s["sky_dt"], Ta + s["ground_dt"]
    f = lambda T: absorptance * s["G"] - 2 * h * (T - Ta) - s["eps"] * SIGMA * ((T ** 4 - Tsky ** 4) + (T ** 4 - Tg ** 4))
    return brentq(f, 200.0, 600.0) - 273.15


def h_forced(v_kmh, L_m, air_c=40.0):
    """Laminar flat plate, average h (W/m2K). Air at ~40 °C: nu 1.7e-5 m2/s, k 0.027 W/mK, Pr 0.71."""
    nu, k, pr = 1.7e-5, 0.027, 0.71
    re = v_kmh / 3.6 * L_m / nu
    return 0.664 * math.sqrt(re) * pr ** (1 / 3) * k / L_m, re


def hdt_at(stress_mpa, table):
    """HDT for the part's static stress: flat below the lowest test load, linear between, flagged above."""
    (s0, t0), (s1, t1) = table
    if stress_mpa <= s0:
        return t0, "시험 하중 이하 → 0.45 MPa 값 사용"
    if stress_mpa <= s1:
        return t0 + (t1 - t0) * (stress_mpa - s0) / (s1 - s0), "0.45–1.8 MPa 사이 선형 보간"
    return t1 - (t0 - t1) / (s1 - s0) * (stress_mpa - s1), "1.8 MPa 초과 → 외삽(근거 없음, 확인 필요)"


def check(spec, fem_result):
    s = ev.SUN
    mat = ev.MATERIALS[spec["material"]["name"]]
    colour = spec.get("finish", {}).get("colour", "black")
    shock = next(c for c in spec["load_cases"] if c["name"] == "shock_vertical")
    sigma_1g = fem_result["shock_vertical"]["vm_max_mpa"] / shock["accel_g"]      # linear: phone weight only
    hdt, how = hdt_at(sigma_1g, mat["hdt"])
    h_ride, re = h_forced(s["ride_kmh"], s["part_len_m"])
    limit = hdt - s["margin_k"]
    rows = []
    for col in ("black", "white"):
        a = ev.ABSORPTANCE[col]
        tp = surface_temp(a, s["h_still"])
        tr = surface_temp(a, max(h_ride, s["h_still"]))
        rows.append(dict(colour=col, absorptance=a, parked_c=round(tp, 1), riding_c=round(tr, 1),
                         limit_c=round(limit, 1), parked_ok=tp <= limit, riding_ok=tr <= limit))
    mine = next(r for r in rows if r["colour"] == colour)
    alt = []
    for name, m in ev.HEAT_ALTERNATIVES.items():
        alt.append(dict(material=name, limit_c=m["no_deform_c"] - s["margin_k"],
                        parked_black_ok=rows[0]["parked_c"] <= m["no_deform_c"] - s["margin_k"],
                        source=m["source"], note=m["note"]))
    ok = mine["parked_ok"] and mine["riding_ok"]
    rec = None
    if not ok:
        if next(r for r in rows if r["colour"] == "white")["parked_ok"]:
            rec = "출력 색을 흰색(밝은 색)으로 지정 — 같은 PETG로 기준 충족"
        elif any(a["parked_black_ok"] for a in alt):
            rec = "재료를 ASA로 변경 검토 (기계 물성 확보 후 재검증 필요)"
        else:
            rec = "색·재료 변경으로도 부족 — 그늘막/커버 형상 필요"
    return dict(
        requirement="sun_heat", pass_=ok, colour=colour,
        sigma_static_mpa=round(sigma_1g, 2), hdt_c=round(hdt, 1), hdt_rule=how, margin_k=s["margin_k"],
        h_parked=s["h_still"], h_riding=round(h_ride, 1), re_riding=round(re), rows=rows, alternatives=alt,
        recommendation=rec,
        assumptions=[f"일사 {s['G']:.0f} W/m², 기온 {s['air_c']:.0f} °C, 하늘 {s['sky_dt']:+.0f} K, 노면 {s['ground_dt']:+.0f} K",
                     f"주차 무풍 h {s['h_still']} W/m²K, 주행 {s['ride_kmh']:.0f} km/h 평판 강제대류",
                     f"HDT − {s['margin_k']:.0f} K 여유 (선택값)",
                     "온도에 따른 탄성계수 저하 데이터 없음 → 진동 판정은 상온 E 사용",
                     "볼트 체결부 응력(예압)과 그 크리프는 해석에 없음 — 고온 주차 후 클램프 풀림은 시험으로 확인"])
