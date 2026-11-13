"""Bike phone-mount template library (track 1: input -> one of these).

Each template only overrides side-view shape parameters (reach, pad height, arm style).
Bar diameter, phone, road, objective come from the text request, not from the template,
so the same shape can be re-used for any request. The parameter vector (reach, rise, arm)
is also the regression target for the track-2 sketch CNN."""

TEMPLATES = [
    # kind: structure family (bar_top / out_front / gooseneck / braced / under / arm)
    dict(id="T01", name="기본형", desc="팀 v7 기준: 클램프 위에서 앞으로 곧게 뻗은 팔",
         params=dict(arm="straight", pad_x0=80.0, pad_z0=16.0)),
    dict(id="T02", name="짧은 팔", desc="핸들 가까이(스템 앞) 받침",
         params=dict(arm="straight", pad_x0=50.0, pad_z0=16.0)),
    dict(id="T03", name="긴 팔", desc="핸들 앞으로 멀리 뻗은 받침",
         params=dict(arm="straight", pad_x0=120.0, pad_z0=16.0)),
    dict(id="T04", name="높은 받침", desc="받침이 높고 팔이 비스듬히 올라감",
         params=dict(arm="straight", pad_x0=80.0, pad_z0=40.0)),
    dict(id="T05", name="L자 팔", desc="위로 올라간 뒤 앞으로 꺾인 팔",
         params=dict(arm="L", pad_x0=80.0, pad_z0=40.0)),
    dict(id="T06", name="낮은 받침", desc="핸들 높이 앞쪽에 받침, 링 앞면에서 출발",
         params=dict(arm="low", pad_x0=70.0, pad_z0=0.0)),
    dict(id="T07", name="트러스", desc="곧은 팔 + 아래 보강대",
         params=dict(arm="truss", pad_x0=80.0, pad_z0=16.0)),
    dict(id="T08", name="긴 트러스", desc="긴 팔 + 아래 보강대",
         params=dict(arm="truss", pad_x0=120.0, pad_z0=16.0)),
    dict(id="T09", name="짧은 L자", desc="짧게 올라갔다 앞으로 꺾인 팔",
         params=dict(arm="L", pad_x0=50.0, pad_z0=30.0)),
    dict(id="T10", name="낮은 긴 팔", desc="핸들 높이로 멀리 뻗은 받침",
         params=dict(arm="low", pad_x0=110.0, pad_z0=0.0)),
    # --- shapes taken from mounts on sale (structure type and proportions only; see templates/SOURCES.md)
    dict(id="T11", name="핸들 위 직결형", desc="클램프 바로 위 짧은 기둥에 받침 (바 위 직접 고정형)", kind="bar_top",
         params=dict(arm="riser", pad_x0=-10.0, pad_z0=28.0)),
    dict(id="T12", name="높은 직결형", desc="클램프 위 높은 기둥에 받침", kind="bar_top",
         params=dict(arm="riser", pad_x0=-10.0, pad_z0=44.0)),
    dict(id="T13", name="아웃프론트", desc="핸들 높이로 앞으로 나간 뒤 받침으로 올라감 (사이클 컴퓨터 마운트형)", kind="out_front",
         params=dict(arm="step", pad_x0=76.0, pad_z0=24.0)),
    dict(id="T14", name="긴 아웃프론트", desc="앞으로 길게 나간 아웃프론트", kind="out_front",
         params=dict(arm="step", pad_x0=116.0, pad_z0=36.0)),
    dict(id="T15", name="구스넥", desc="비스듬히 올라가 받침 높이에서 앞으로 뻗음", kind="gooseneck",
         params=dict(arm="dogleg", pad_x0=80.0, pad_z0=40.0)),
    dict(id="T16", name="긴 구스넥", desc="짧게 올라가 길게 뻗은 구스넥", kind="gooseneck",
         params=dict(arm="dogleg", pad_x0=120.0, pad_z0=34.0, knee_frac=0.25)),
    dict(id="T17", name="V자 지지", desc="링 위와 앞에서 나온 두 팔이 받침에서 만남", kind="braced",
         params=dict(arm="vee", pad_x0=80.0, pad_z0=16.0)),
    dict(id="T18", name="긴 V자 지지", desc="길게 뻗은 V자 두 팔", kind="braced",
         params=dict(arm="vee", pad_x0=110.0, pad_z0=24.0)),
    dict(id="T19", name="아래 기둥형", desc="링 앞에서 낮게 나가 받침 아래 기둥으로 올라감", kind="under",
         params=dict(arm="stalk", pad_x0=70.0, pad_z0=30.0)),
    dict(id="T20", name="높은 V자 지지", desc="높은 받침을 두 팔이 받침", kind="braced",
         params=dict(arm="vee", pad_x0=80.0, pad_z0=40.0)),
    dict(id="T21", name="짧고 높은 팔", desc="핸들 가까이 높게 올린 받침", kind="bar_top",
         params=dict(arm="straight", pad_x0=50.0, pad_z0=40.0)),
    dict(id="T22", name="아래 우회형", desc="링 아래로 내려가 폰 공간을 피해 돌아 올라감", kind="under",
         params=dict(arm="under", pad_x0=80.0, pad_z0=30.0, stalk_base_z=-16.0)),
]
BY_ID = {t["id"]: t for t in TEMPLATES}
