"""Run every check and print one line each.  python tests/run_all.py"""
import os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_reproduce_opt3d, test_fem_cantilever, test_text_rules, test_sketch_match

CHECKS = [
    ("opt3d.py 문제 재현", test_reproduce_opt3d.test_reproduce),
    ("외팔보 이론식", test_fem_cantilever.test_cantilever),
    ("텍스트: 팀 v7 요청", test_text_rules.test_team_v7_request),
    ("텍스트: 폰·핸들", test_text_rules.test_phones_and_bars),
    ("텍스트: 포장도로·튼튼", test_text_rules.test_paved_and_strong),
    ("텍스트: 형태 힌트", test_text_rules.test_shape_hints),
    ("스케치: 정형 20장", test_sketch_match.test_clean_sketches_exact),
    ("스케치: 합성 손그림", test_sketch_match.test_hand_drawn),
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
