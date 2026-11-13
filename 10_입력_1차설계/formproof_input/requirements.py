"""User requirement library: words -> physics conditions handed to the optimisation stage.

The input stage does NOT redesign for these requirements; it only defines them (constraints,
keep-out spaces, finish) in the spec so the physics / optimisation stage can satisfy and judge them.
Evaluation functions for the conditions live in thermal.py and angle.py for that stage to call."""
import re

import numpy as np

LIBRARY = {
    "sun_heat": dict(
        name="여름 땡볕에서 변형 없음",
        triggers=r"땡볕|햇빛|햇볕|직사광선|여름|뙤약볕|더위|뜨거운\s*날|고온",
        physics="햇빛 아래 주차 표면온도 ≤ 재료 열변형온도(폰 무게에 의한 자기 응력에서) − 10 K",
        handoff="sun_heat 제약 + 마감 색. 판정 함수 thermal.check",
    ),
    "free_angle": dict(
        name="화면 각도 최대한 자유롭게",
        triggers=r"각도|기울|틸트|돌려|회전|가로\s*(로|모드)?|세로\s*(로|모드)?|자유롭게\s*(조절|돌)",
        physics="폰이 360° 회전 + 기울기 −30~+60°의 모든 자세에서 핸들·거치대와 3 mm 이상 떨어짐, "
                "관절 회전 모드 ≥ 진동 기준, 충격 시 관절 유지 토크",
        handoff="폰이 지나가는 공간(keepout 마스크), pose_clearance·joint_stiffness·joint_hold 제약. 판정 함수 angle.check",
    ),
}


def detect(text):
    return [k for k, v in LIBRARY.items() if re.search(v["triggers"], text or "")]


def handoff_summary(spec, P):
    """What each requirement adds for the optimisation stage, plus conflicts the input stage can already see."""
    out = []
    cons = {c["id"]: c for c in spec["constraints"]}
    for rid in spec.get("requirements", []):
        lib = LIBRARY[rid]
        item = dict(id=rid, name=lib["name"], physics=lib["physics"], handoff=lib["handoff"],
                    constraints=[dict(id=c["id"], rule=f'{c["quantity"]} {c["op"]} {c["value"]}',
                                      why=c.get("derivation", "")) for c in spec["constraints"]
                                 if c.get("requirement") == rid],
                    warnings=[])
        if rid == "free_angle" and P.keepout is not None:
            clash = int((P.keepout & (P.solid | P.rigid)).sum())
            item["keepout_elements"] = int(P.keepout.sum())
            if clash:
                item["warnings"].append(
                    f"폰이 지나가는 공간이 지켜야 할 부품(클램프·받침)과 {clash}개 요소에서 겹침 → "
                    "최적화 단계에서 관절 높이 또는 받침 위치(도달 거리) 조정 필요")
        if rid == "sun_heat":
            item["colour"] = spec.get("finish", {}).get("colour")
        out.append(item)
    return out
