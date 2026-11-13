"""Run every check and print one line each.  python tests/run_all.py"""
import os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_reproduce_opt3d, test_fem_cantilever, test_text_rules, test_sketch_match, test_cad, test_requirements

CHECKS = [
    ("opt3d.py 문제 재현", test_reproduce_opt3d.test_reproduce),
    ("외팔보 이론식", test_fem_cantilever.test_cantilever),
    ("텍스트: 팀 v7 요청", test_text_rules.test_team_v7_request),
    ("텍스트: 폰·핸들", test_text_rules.test_phones_and_bars),
    ("텍스트: 포장도로·튼튼", test_text_rules.test_paved_and_strong),
    ("텍스트: 형태 힌트", test_text_rules.test_shape_hints),
    ("스케치: 정형 20장", test_sketch_match.test_clean_sketches_exact),
    ("스케치: 합성 손그림", test_sketch_match.test_hand_drawn),
    ("CAD: STEP 10종 (유효·왕복·복셀 질량 ±5%)", test_cad.test_step_all_templates),
    ("도면: 치수 = 명세", test_cad.test_drawing_dimensions),
    ("요구: 텍스트 감지", test_requirements.test_text_detects_requirements),
    ("요구: 땡볕 에너지 평형·HDT", test_requirements.test_thermal_physics),
    ("요구: 기울기 한계 = 손계산", test_requirements.test_tilt_vs_hand_calc),
    ("요구: 1차 설계는 그대로, 조건만 넘김", test_requirements.test_requirements_are_handoff_only),
]

if __name__ == "__main__":
    fails = 0
    for name, fn in CHECKS:
        t = time.time()
        try:
            r = fn()
            print(f"PASS  {name}  {r if r else ''}  ({time.time() - t:.1f}s)")
        except AssertionError as e:
            fails += 1
            print(f"FAIL  {name}  {e}")
    sys.exit(1 if fails else 0)
