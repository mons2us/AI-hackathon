"""GUI end-to-end check with headless Chrome (playwright). Start app/server.py first.
   CHROME=/path/to/chrome python tests/e2e_gui.py   (screenshots -> <tmp>/formproof_e2e)

확인: 4단 화면이 한 화면에 들어감(페이지 · 카드 스크롤 없음), 제품 4개(P01 · T01 · TV · AI 글래스)마다 형상 + 분포 창,
메인 창을 돌리고 확대하면 아래 분포 창 카메라가 같은 방향 · 같은 거리로 따라감, 도면 보기,
성능 항목을 눌러 최적화 대상 고르기(1개 이상이면 실행 버튼 켜짐) → 고른 항목이 든 optimize_input.zip."""
import math, os, sys, tempfile, time
from playwright.sync_api import sync_playwright

SP = os.path.join(tempfile.gettempdir(), "formproof_e2e"); os.makedirs(SP, exist_ok=True)
URL = os.environ.get("URL", "http://localhost:8765")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def wait_result(page, timeout=90):
    page.wait_for_function("() => !document.querySelector('#busy').classList.contains('on') && !document.querySelector('#go').disabled"
                           " && document.querySelector('#vS0 .lab').textContent.length>0", timeout=timeout * 1000)
    time.sleep(2)


def no_scroll(page):
    s = page.evaluate("() => [document.documentElement.scrollHeight > document.documentElement.clientHeight,"
                      " document.documentElement.scrollWidth > document.documentElement.clientWidth,"
                      " ...[...document.querySelectorAll('.card.fill')].map(c => c.scrollHeight > c.clientHeight + 1)]")
    assert not any(s), f"스크롤 생김: {s}"


def cams(page):
    return page.evaluate("() => ({q: V3.cam.quaternion.toArray(), q2: V3.cam2.quaternion.toArray(),"
                         " d: V3.cam.position.distanceTo(V3.ctl.target), d2: V3.cam2.position.distanceTo(V3.mc)})")


with sync_playwright() as p:
    b = p.chromium.launch(**({"executable_path": os.environ["CHROME"]} if os.environ.get("CHROME") else {}),
                          args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    page = b.new_page(viewport={"width": 1920, "height": 950})
    logs = []
    page.on("console", lambda m: logs.append(f"{m.type}: {m.text}") if m.type == "error" else None)
    page.on("pageerror", lambda e: logs.append(f"PAGEERROR: {e}"))
    page.goto(URL)
    page.wait_for_timeout(1500)
    no_scroll(page)

    runs = [("P01", "bike", "#example", "/examples/presentation/input_sketch.png"), ("T01", "bike", "#example", "/examples/hand/hand_T01.png"),
            ("TV", "tv", "#example", "/examples/hand/hand_TV01.png"), ("GL", "glasses", "#photoEx", None)]
    for name, prod, sel, val in runs:
        page.click(f"#prodSeg button[data-p={prod}]")
        page.wait_for_timeout(300)
        if val is None:
            val = page.evaluate("() => [...document.querySelectorAll('#photoEx option')].map(o => o.value).filter(Boolean)[0]")
        page.select_option(sel, val)
        page.wait_for_timeout(1200)
        t = time.time()
        page.click("#go")
        wait_result(page)
        labs = [page.inner_text(f"#vS{i} .lab") for i in range(3)]
        print(f"{name}: {time.time() - t:.1f} s | {page.inner_text('#tplTag')} | 분포 창: {labs} | 성능: {page.inner_text('#perfTag')}")
        no_scroll(page)
        body = page.inner_text("body")
        assert "발표" not in body and "쪽" not in body, "발표 관련 글자가 남음"
        page.screenshot(path=f"{SP}/gui_{name}.png")

    # 메인 창 회전 · 확대 → 분포 창 카메라가 같은 방향 · 같은 거리
    box = page.locator("#vMain").bounding_box()
    c0 = cams(page)
    page.mouse.move(box["x"] + box["width"] * .5, box["y"] + box["height"] * .5); page.mouse.down()
    page.mouse.move(box["x"] + box["width"] * .3, box["y"] + box["height"] * .35, steps=8); page.mouse.up()
    page.mouse.wheel(0, 400)
    page.wait_for_timeout(1500)
    c1 = cams(page)
    assert max(abs(a - b) for a, b in zip(c1["q"], c0["q"])) > 0.05, "메인 창이 안 돌아감"
    assert max(abs(a - b) for a, b in zip(c1["q"], c1["q2"])) < 1e-6 and abs(c1["d"] - c1["d2"]) < 1e-3 * c1["d"], c1
    print(f"동기화: 회전 후 방향 같음, 거리 {c0['d']:.0f} → {c1['d']:.0f} mm (분포 창 {c1['d2']:.0f})")
    page.screenshot(path=f"{SP}/gui_sync.png")

    # 도면 보기 켜고 끄기
    page.click("#vDraw"); page.wait_for_timeout(800)
    page.screenshot(path=f"{SP}/gui_draw.png")
    page.click("#vDraw"); page.wait_for_timeout(500)

    # 성능 항목을 눌러 최적화 대상 고르기 → 1개 이상이면 버튼 켜짐 → 고른 항목이 든 최적화 입력 묶음
    import json, zipfile
    assert page.is_disabled("#optimize"), "아무것도 안 골랐는데 최적화 버튼이 켜져 있음"
    blocks = page.locator("#metrics .metric")
    blocks.nth(0).click(); blocks.nth(2).click(); blocks.nth(2).click(); blocks.nth(3).click()   # 0, 3 선택 (2는 눌렀다 해제)
    assert not page.is_disabled("#optimize")
    picked = [blocks.nth(i).inner_text().split("\n")[0].lstrip("✓").strip() for i in (0, 3)]
    with page.expect_download() as d:
        page.click("#optimize")
    zp = f"{SP}/optimize_input_test.zip"
    d.value.save_as(zp)
    T = json.loads(zipfile.ZipFile(zp).read("optimize_targets.json"))
    got = [t["label"] for t in T["targets"]]
    assert got == picked and "spec.json" in zipfile.ZipFile(zp).namelist(), (got, picked)
    print("최적화 버튼:", d.value.suggested_filename, "| 대상:", got, "| 버튼:", page.inner_text("#optimize"))
    errs = [l for l in logs if "error" in l.lower() or "PAGEERROR" in l]
    print("\n".join(errs)[:2000] or "콘솔 오류 없음")
    b.close()
    sys.exit(1 if errs else 0)
