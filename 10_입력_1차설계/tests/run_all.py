"""Run every check and print one line each.  python tests/run_all.py"""
import os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_reproduce_opt3d, test_rigid_payload, test_fem_cantilever, test_text_rules, test_sketch_match, test_cad, test_requirements
import test_looks, test_integral

CHECKS = [
    ("opt3d.py 문제 재현", test_reproduce_opt3d.test_reproduce),
    ("폰 강체(팀 v3) = 팀 전체 모델 opt3d_am", test_rigid_payload.test_rigid_payload_matches_team_full_model),
    ("폰 강체 충격 하중 합력", test_rigid_payload.test_payload_load_resultant),
    ("외팔보 이론식", test_fem_cantilever.test_cantilever),
    ("텍스트: 팀 v7 요청", test_text_rules.test_team_v7_request),
    ("텍스트: 폰·핸들", test_text_rules.test_phones_and_bars),
    ("텍스트: 포장도로·튼튼", test_text_rules.test_paved_and_strong),
    ("텍스트: 형태 힌트", test_text_rules.test_shape_hints),
    ("스케치: 정형 (템플릿 × 폰 유무)", test_sketch_match.test_clean_sketches_exact),
    ("스케치: 합성 손그림", test_sketch_match.test_hand_drawn),
    ("CAD: STEP 전 템플릿 (유효·왕복·복셀 질량 ±5%)", test_cad.test_step_all_templates),
    ("도면: 치수 = 명세", test_cad.test_drawing_dimensions),
    ("요구: 텍스트 감지", test_requirements.test_text_detects_requirements),
    ("요구: 땡볕 에너지 평형·HDT", test_requirements.test_thermal_physics),
    ("요구: 기울기 한계 = 손계산", test_requirements.test_tilt_vs_hand_calc),
    ("요구: 1차 설계는 그대로, 조건만 넘김", test_requirements.test_requirements_are_handoff_only),
    ("외형: 홀더 탑재 하중 표 = CAD 질량 특성", test_looks.test_payload_table_matches_cad),
    ("외형: 문장 단어 → 외형 템플릿", test_looks.test_text_picks_look),
    ("외형: 185종 명세·격자·FEM·폰 간섭 없음", test_looks.test_every_look_builds_and_solves),
    ("외형: CAD 몸체 = 해석 격자 질량 (팔 10종)", test_looks.test_cad_matches_grid),
    ("외형: 정형 스케치 자기 찾기 (1/3 표본)", test_looks.test_clean_look_sketches),
    ("외형: 합성 손그림 185장 (+ 홀더·클램프 단어)", test_looks.test_hand_drawn_looks),
    ("P01 발표 사례: 격자 영역 = 팀 grid_meta", test_integral.test_grid_same_as_team),
    ("P01: 1차 설계 = 발표 처음 설계 (판 + 기둥)", test_integral.test_first_design_is_presentation_base),
    ("P01: 설계 명세 · 판정 기준 = 팀 spec", test_integral.test_conditions_same_as_team_spec),
    ("P01: 10쪽 비교 형상 = llm2rho 출력", test_integral.test_comparison_shapes_same_as_team),
    ("P01: 수치 · 판정 = 발표 7·10·22쪽", test_integral.test_numbers_same_as_presentation),
    ("P01: 발표 문장 · 스케치 → P01", test_integral.test_routing),
    ("P01: 파이프라인 출력 파일", test_integral.test_pipeline_outputs),
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
