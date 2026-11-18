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
        import logging
        from matplotlib import font_manager
        # 보통 굵기(400)가 있는 글꼴만 고름: 굵은 체만 깔린 글꼴(예: Noto Sans KR Bold)을 목록에 넣으면
        # 'findfont: Failed to find font weight normal for Noto Sans …' 경고가 그림마다 찍힘
        have = {f.name for f in font_manager.fontManager.ttflist if f.weight in (400, "normal", "regular", "book")}
        kr = [f for f in FONTS if f in have][:1]                # 한 글꼴만 (목록 전체를 넣으면 없는 굵기마다 경고)
        plt.rcParams["font.family"] = kr + ["DejaVu Sans"]
        logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
        plt.rcParams["axes.unicode_minus"] = False
        _done.append(kr[0] if kr else None)
    return plt


def korean_font():
    """쓰는 한글 글꼴 이름 (없으면 None) — 시험 · 진단용."""
    pyplot()
    return _done[0]
