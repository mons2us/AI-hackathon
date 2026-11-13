"""Bike phone-mount template library (track 1: input -> one of these).

Each template only overrides side-view shape parameters (reach, pad height, arm style).
Bar diameter, phone, road, objective come from the text request, not from the template,
so the same shape can be re-used for any request. The parameter vector (reach, rise, arm)
is also the regression target for the track-2 sketch CNN."""

TEMPLATES = [
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
]
BY_ID = {t["id"]: t for t in TEMPLATES}
