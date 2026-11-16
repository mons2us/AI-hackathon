"""GUI end-to-end check with headless Chrome (playwright). Start app/server.py first.
   CHROME=/path/to/chrome python tests/e2e_gui.py   (screenshots -> <tmp>/formproof_e2e)

확인: 4단 화면이 한 화면에 들어감(페이지 · 카드 스크롤 없음), 제품 4개(P01 · T01 · TV · AI 글래스)마다 형상 + 분포 창,
메인 창을 돌리고 확대하면 아래 분포 창 카메라가 같은 방향 · 같은 거리로 따라감, 도면 보기,
P01 만 성능 항목을 눌러 최적화 대상 고르기(1개 이상이면 실행 버튼 켜짐) → 역설계 재생(형상 · 예측값) → FEM 검증 · optimize_input.zip."""
import json, math, os, sys, tempfile, time, urllib.request
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

    # 데모 입력(말 + 스케치) 3개 + 손 스케치 T01 + 글래스 사진: 예시 고르면 말도 채워짐, 카드가 형상보다 먼저
    demos = {d["product"]: d for d in json.load(urllib.request.urlopen(URL.rstrip("/") + "/api/demos"))}
    runs = [("P01", "bike", "#example", demos["bike"]["sketch"]), ("T01", "bike", "#example", "/examples/hand/hand_T01.png"),
            ("TV", "tv", "#example", demos["tv"]["sketch"]), ("GL", "glasses", "#example", demos["glasses"]["sketch"]),
            ("GLphoto", "glasses", "#photoEx", None)]
    ORDER = ("() => { window.__ord = []; const add = k => { if (!__ord.includes(k)) __ord.push(k); };"
             " new MutationObserver(() => { if (document.querySelector('#specs .sc.in')) add('cards'); })"
             ".observe(document.querySelector('#specs'), {subtree: true, childList: true, attributes: true});"
             " new MutationObserver(() => add('shape')).observe(document.querySelector('#tplTag'), {childList: true, characterData: true, subtree: true}); }")
    for name, prod, sel, val in runs:
        page.click(f"#prodSeg button[data-p={prod}]")
        page.wait_for_timeout(300)
        if val is None:
            page.click("#mImage")
            val = page.evaluate("() => [...document.querySelectorAll('#photoEx option')].map(o => o.value).filter(Boolean)[0]")
        page.select_option(sel, val)
        page.wait_for_timeout(1200)
        if prod in demos and val == demos[prod]["sketch"]:
            assert page.input_value("#text") == demos[prod]["prompt"], "예시를 골라도 말이 안 채워짐"
        page.evaluate(ORDER)
        t = time.time()
        page.click("#go")
        wait_result(page)
        labs = [page.inner_text(f"#vS{i} .lab") for i in range(3)]
        cards = page.locator("#specs .sc").all_inner_texts()
        order = page.evaluate("() => __ord")
        print(f"{name}: {time.time() - t:.1f} s | {page.inner_text('#tplTag')} | 분포 창: {labs} | 성능: {page.inner_text('#perfTag')}"
              f" | 조건 카드 {len(cards)}장 {order}")
        assert len(cards) >= (6 if name in ("P01", "TV", "GL") else 4) and order[:2] == ["cards", "shape"], (name, len(cards), order)
        if name in ("TV", "GL"):
            assert ("TV01" if name == "TV" else "AG-gm") in page.inner_text("#tplTag")
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

    # P01 이 아닌 제품(마지막 = AI 글래스)은 1차 설계까지만: 고르기 · 최적화 버튼 없음
    assert page.is_hidden("#optimize") and page.is_hidden("#pickHint"), "P01 이 아닌데 최적화 버튼이 보임"

    # P01: 성능 블록 고르기 → 물리 기반 최적화 실행 → 형상이 프레임마다 바뀌고 예측값이 움직임 → FEM 검증 값
    page.click("#prodSeg button[data-p=bike]"); page.wait_for_timeout(300)
    page.select_option("#example", "/examples/presentation/input_sketch.png"); page.wait_for_timeout(1200)
    page.click("#go"); wait_result(page)
    assert page.is_disabled("#optimize"), "아무것도 안 골랐는데 최적화 버튼이 켜져 있음"
    blocks = page.locator("#metrics .metric")
    blocks.nth(0).click(); blocks.nth(2).click(); blocks.nth(2).click(); blocks.nth(1).click()   # 떨림 주파수 · 폰 온도 (화면 휨은 눌렀다 해제)
    assert page.inner_text("#optimize").endswith("(2개)")
    tri0 = page.evaluate("() => V3.mount.geometry.attributes.position.count")
    t = time.time()
    page.click("#optimize")
    seen = set()
    while time.time() - t < 300:
        st = page.evaluate("() => [document.querySelector('#optText').textContent, V3.mount.geometry.attributes.position.count,"
                           " document.querySelector('#optInfo').className]")
        seen.add(st[1])
        if "ok" in st[2].split() or "bad" in st[2].split():
            break
        page.wait_for_timeout(250)
    final = page.inner_text("#optText")
    vals = page.locator("#metrics .metric").all_inner_texts()
    print(f"최적화: {time.time() - t:.1f} s, 형상 {len(seen)}가지(처음 {tri0 // 3} 삼각형) | {final}")
    print("  성능:", [v.split("\n")[0].lstrip("✓") + " " + v.split("\n")[1] for v in vals][:6])
    assert len(seen) >= 10, "형상이 거의 안 바뀜"
    assert "FEM 검증" in vals[0] and not page.is_hidden("#fOpt")
    page.screenshot(path=f"{SP}/gui_optimized.png")
    import urllib.request, zipfile, io
    href = page.get_attribute("#fOpt", "href").split("?")[0]
    base = URL.rstrip("/")
    z = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(base + href.replace("opt_final.stl", "optimize_input.zip")).read()))
    T = json.loads(z.read("optimize_targets.json"))
    assert sorted(T["targets"]) == ["Tmax", "f1"] and "opt_final.stl" in z.namelist() and "spec.json" in z.namelist(), T
    print("최적화 입력 묶음: 대상", T["targets"], "| 파일", len(z.namelist()), "개")
    errs = [l for l in logs if "error" in l.lower() or "PAGEERROR" in l]
    print("\n".join(errs)[:2000] or "콘솔 오류 없음")
    b.close()
    sys.exit(1 if errs else 0)
