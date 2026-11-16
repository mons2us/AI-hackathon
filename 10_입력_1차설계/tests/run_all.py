"""Run every check and print one line each.  python tests/run_all.py"""
import os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_reproduce_opt3d, test_rigid_payload, test_fem_cantilever, test_text_rules, test_sketch_match, test_cad, test_requirements
import test_looks, test_integral, test_products, test_spec_view, test_optimize, test_inverse, test_spec_table

CHECKS = [
    ("설계 사양 카드: 4개 제품 경로 같은 형식 · 출처 태그", test_spec_view.test_spec_rows_all_products),
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
    ("P01: 폰 고정 부품 (집게 ×2 · 위 걸이) = 팀 parts.py · 발표 22쪽 무게", test_integral.test_fixing_parts),
    ("P01: 3D 보기 표면 = 닫힌 다양체 (간소화 뒤에도 구멍 · 뒤집힌 면 없음)", test_integral.test_view_mesh_clean),
    ("3D 분포(응력·흔들림·온도) = 발표 8쪽 · 메쉬 정점마다", test_integral.test_heat_maps),
    ("데모 제품: 복셀 FEM 외팔보 이론식", test_products.test_voxfem_cantilever),
    ("TV 스탠드: 넘어짐 각 · 수평력 · 바퀴 하중 = 손계산", test_products.test_tv_tip_hand_calc),
    ("TV 스탠드: IEC 62368-1 수치 · 스탠바이미 27형", test_products.test_tv_conditions_iec),
    ("TV 스탠드: 스탠드가 화면을 뚫지 않음", test_products.test_tv_no_clash),
    ("TV 스탠드: 정면 스케치 매칭 · 높이 읽기", test_products.test_tv_sketch_match),
    ("TV 스탠드: 가로 · 세로 1차 설계 · 미충족 판정 · 파일", test_products.test_tv_designs),
    ("AI 글래스: 합성 제품 사진 → 렌즈 윤곽 · 치수", test_products.test_glasses_photo_analysis),
    ("AI 글래스: 거치대 그림은 안경 아님", test_products.test_glasses_no_false_positive),
    ("AI 글래스: 공식 사진 → 템플릿 1차 설계 · 미충족 판정 · 핀 열계산", test_products.test_glasses_design),
    ("AI 글래스: 착용 · 브리지 응력 · 변위 분포 좌우 대칭 · 끊김 없음", test_products.test_glasses_heat_symmetric),
    ("템플릿 결과 DB: 시나리오마다 4 s 이내", test_products.test_template_db_speed),
    ("제품 선택 · 큰 격자 분포 압축", test_products.test_routing_and_heat_payload),
    ("간이 물리 최적화: T01 12 반복 (목적 감소 · 부피 · 연결 · 개선)", test_optimize.test_simple_optimizer),
    ("P01 최적화: 1차 설계 → FEM 검증 통과 형상 (경로 · 무게 · 벌점)", test_inverse.test_path_reaches_verified_design),
    ("P01 최적화: 고른 기준만 벌점", test_inverse.test_only_selected_targets_penalised),
    ("P01 최적화: 학습 모델 자리(models/) · 못 읽으면 대체 모델", test_inverse.test_model_slot_fallback),
    ("설계 사양 표: 데모 입력(말 + 스케치) → 행 · 수치 = 판정 기준 · 근거", test_spec_table.test_demo_spec_rows),
    ("설계 사양 표: 데모 입력 → 지금 1차 설계 그대로 (P01 · TV01 낮게 · AG-gm)", test_spec_table.test_demo_inputs_keep_first_design),
    ("설계 사양 표: 고친 값 → 판정 기준 · 템플릿 (렌즈 폭 · 화면 높이)", test_spec_table.test_edited_spec),
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
