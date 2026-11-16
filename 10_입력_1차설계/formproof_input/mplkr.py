"""matplotlib 한글 글꼴 — 그림(도면 · 측면도 · 분석 그림)에 한글이 네모(□)로 깨지지 않게.

Windows 기본 글꼴 DejaVu Sans 에는 한글이 없어 글자가 깨짐 → 설치된 한글 글꼴 중 첫 번째를 쓰고,
한글 글꼴에서 깨지는 유니코드 빼기 기호(−) 대신 ASCII '-' 를 씀. 그림 그리는 곳은 모두 `pyplot()` 으로 받는다."""

FONTS = ("Malgun Gothic", "맑은 고딕", "AppleGothic", "Apple SD Gothic Neo", "NanumGothic", "Noto Sans CJK KR", "Noto Sans KR",
         "Noto Sans CJK JP", "Gulim", "Dotum", "Batang")
_done = []


def pyplot():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    if not _done:
        from matplotlib import font_manager
        have = {f.name for f in font_manager.fontManager.ttflist}
        kr = [f for f in FONTS if f in have]
        plt.rcParams["font.family"] = kr + ["DejaVu Sans"] if kr else ["DejaVu Sans"]
        plt.rcParams["axes.unicode_minus"] = False
        _done.append(kr[0] if kr else None)
    return plt


def korean_font():
    """쓰는 한글 글꼴 이름 (없으면 None) — 시험 · 진단용."""
    pyplot()
    return _done[0]
