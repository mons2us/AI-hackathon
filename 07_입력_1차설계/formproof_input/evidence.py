"""Evidence DB: every number that enters a spec carries one of these ids.
status: 'cited' = taken from the listed source, 'assumed' = team/design choice (확인 필요)."""

SOURCES = {
    "isbs2020": dict(
        title="Viellehner & Potthast, Road to lab: cobblestone cycling vibrations transferred to the lab, ISBS Proceedings 38 (2020)",
        url="https://commons.nmu.edu/isbs/vol38/iss1/216/",
        note="바퀴 축(드롭아웃) 측정값. 핸들바에 그대로 적용하는 것은 보수적 가정"),
    "prusament_petg": dict(
        title="Prusament PETG V0 Technical Data Sheet v1.0 (2023), ISO 527-1 printed specimens",
        url="https://cdn.shopify.com/s/files/1/1745/6181/files/prusament-petg-v0-technical-data-sheet.pdf",
        note="출력 시편 수평 방향 값. 일반 PETG와 차이 가능"),
    "samsung_s25": dict(title="Samsung Galaxy S25 | S25+ specifications",
                        url="https://www.samsung.com/nz/smartphones/galaxy-s25/specs/"),
    "samsung_s25u": dict(title="Samsung Galaxy S25 Ultra specifications",
                         url="https://www.samsung.com/ph/smartphones/galaxy-s25-ultra/specs/"),
    "team_v7": dict(title="FormProof 자전거 폰 거치대 시나리오 v7 (팀 내부 사전 검증)",
                    url="02_시연페이지/bike_mount_v7.html"),
    "sdof": dict(title="1자유도 진동 전달률 T = 1/|1-r^2|, r = f_excitation / f_natural",
                 url=None, note="교과서 식. 강성 설계(f_n > f_ex)에서 T <= T_max 이면 f_n >= f_ex / sqrt(1 - 1/T_max)"),
}

# --- materials (N, mm, t units: E/strength in MPa, rho in t/mm^3)
MATERIALS = {
    "PETG": dict(E=1700.0, nu=0.38, rho=1.27e-9, yield_mpa=39.0, interlayer_mpa=16.4,
                 source="prusament_petg", nu_source="assumed"),
}

# --- road excitation classes (only classes with a measured source are 'cited')
ROADS = {
    "cobblestone": dict(f_lo=34.6, f_hi=45.6, peak_g=48.5, source="isbs2020", status="cited",
                        label="자갈·돌길(비포장)"),
}
ROAD_FALLBACK = "cobblestone"      # roads without data -> conservative cobblestone values, flagged

# --- phones (mass kg, H x W x D mm)
PHONES = {
    "galaxy_s25": dict(name="Galaxy S25", mass=0.162, dims=(146.9, 70.5, 7.2), source="samsung_s25"),
    "galaxy_s25_plus": dict(name="Galaxy S25+", mass=0.190, dims=(158.4, 75.8, 7.3), source="samsung_s25"),
    "galaxy_s25_ultra": dict(name="Galaxy S25 Ultra", mass=0.218, dims=(162.8, 77.6, 8.2), source="samsung_s25u"),
}
PHONE_DEFAULT_MASS = 0.200          # team_v7: phone 200 g + clamp 50 g = 250 g (assumed)
PHONE_CLAMP_MASS = 0.050            # assumed (commercial phone clamp, rigid)

# --- handlebar clamp diameters in common use (assumed: industry sizes, source to be confirmed)
HANDLEBAR_D = {"oversize": 31.8, "standard": 25.4, "mtb_35": 35.0, "grip": 22.2}

# --- design factors (choices, not data)
FACTORS = dict(safety_factor=1.5, t_max=4.0 / 3.0, min_feature_mm=5.0)
