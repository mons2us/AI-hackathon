"""GUI end-to-end check with headless Chrome (playwright). Start app/server.py first.
   CHROME=/path/to/chrome python tests/e2e_gui.py   (screenshots -> <tmp>/formproof_e2e)

확인: 한 화면(페이지 · 카드 스크롤 없음), 제품 버튼 없음 · 로고, 예시 3개(말 + 스케치 획) → [설계 사양] 표 → 수치 고치기 →
[확정] → [초기 설계 만들기] (확정 전 · 입력 바뀐 뒤에는 꺼짐), 고친 사양이 판정 기준으로, 말만 · 사진 입력,
메인 창을 돌리고 확대하면 아래 분포 창 카메라가 따라감, 도면 보기, TV · 글래스도 성능 항목 고르기(최적화 입력 묶음 저장),
P01 역설계 재생 → FEM 검증 · optimize_input.zip, 영상 모드(?video=1, 키 2 → 치고 그리기 → TV01)."""
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
    assert page.locator("#prodSeg").count() == 0 and page.is_visible("header .brand-r"), "제품 버튼이 남았거나 로고가 없음"
    assert page.is_disabled("#bConfirm") and page.is_disabled("#go"), "설계 사양 전에 확정 · 초기 설계 버튼이 켜져 있음"
    demos = json.load(urllib.request.urlopen(URL.rstrip("/") + "/api/demos"))
    assert [d["label"] for d in demos] == ["폰 거치대", "TV 스탠드", "AI 글래스"]

    def spec_then_design(name, edit=None):
        t = time.time()
        page.click("#bSpec")
        page.wait_for_function("() => document.querySelector('#specs').classList.contains('on') && !document.querySelector('#bConfirm').disabled",
                               timeout=90000)
        n = page.locator("#specBody tr").count()
        assert page.is_disabled("#go"), "확정 전에 초기 설계 버튼이 켜짐"
        if edit:
            k, v = edit
            page.fill(f"input[data-id={k}]", str(v)); page.locator(f"input[data-id={k}]").dispatch_event("change")
            page.wait_for_timeout(400)
        page.click("#bConfirm")
        assert not page.is_disabled("#go")
        info = page.inner_text("#specInfo")
        page.click("#go")
        wait_result(page)
        labs = [page.inner_text(f"#vS{i} .lab") for i in range(3)]
        print(f"{name}: {time.time() - t:.1f} s | 사양 {n}줄 ({info}) | {page.inner_text('#tplTag')} | 분포 창: {labs} | 성능: {page.inner_text('#perfTag')}")
        no_scroll(page)
        body = page.inner_text("body")
        assert "발표" not in body and "쪽" not in body, "발표 관련 글자가 남음"
        hard = [w for w in ("층간", "P01", "TV01", "AG-", "줄 (말", "FEM", "역설계", "벌점", "자갈길", "출력 층", "참고)", "N 누를", "근거 DB")
                if w in body]
        assert not hard, f"어려운 말이 남음: {hard}"
        page.screenshot(path=f"{SP}/gui_{name}.png")
        return n

    for i, (name, tid) in enumerate((("P01", "P01"), ("TV", "TV01"), ("GL", "AG-gm"))):
        page.select_option("#example", str(i))
        page.wait_for_timeout(600)
        assert page.input_value("#text") == demos[i]["prompt"], "예시를 골라도 말이 안 채워짐"
        n = spec_then_design(name, ("tilt", 8) if name == "TV" else None)
        assert n >= 8 and page.evaluate("() => S.rep.template.id") == tid, (name, n)
        if name == "TV":                                   # 고친 사양(기울기 10 → 8°)이 초기 설계 판정 기준으로
            assert "≥ 8 °" in page.locator("#metrics .metric").first.inner_text()
    # 사양을 만든 뒤 말을 바꾸면 확정 · 초기 설계가 꺼짐
    page.click("#bSpec"); page.wait_for_timeout(2500)
    page.type("#text", " 더 가볍게"); page.wait_for_timeout(200)
    assert page.is_disabled("#bConfirm") and page.is_disabled("#go") and page.is_visible("#specStale")
    # 말만 (템플릿 거치대)
    page.click("#clear"); page.fill("#text", "자전거 폰 거치대, 울퉁불퉁한 길에서도 안 흔들리게 땡볕에도 버티게")
    spec_then_design("T01")
    # 사진 (AI 글래스 공식 사진)
    page.click("#mImage")
    val = page.evaluate("() => [...document.querySelectorAll('#photoEx option')].map(o => o.value).filter(Boolean)[0]")
    page.select_option("#photoEx", val); page.wait_for_timeout(1200); page.fill("#text", "")
    spec_then_design("GLphoto")
    # TV · 글래스도 성능 항목 고르기 → 최적 설계는 없이 고른 기준만 최적화 입력 묶음으로
    blocks = page.locator("#metrics .metric")
    blocks.filter(has_text="총무게").click(); blocks.filter(has_text="온도").click()
    assert page.inner_text("#optimize").endswith("(2개)") and not page.is_disabled("#optimize")
    page.click("#optimize"); page.wait_for_timeout(1500)
    assert "요청 파일" in page.inner_text("#optText") and not page.is_hidden("#fOpt")
    zhref = page.get_attribute("#fOpt", "href").split("?")[0]
    import zipfile, io
    zg = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(URL.rstrip("/") + zhref).read()))
    TG = json.loads(zg.read("optimize_targets.json"))
    assert TG["targets"] == ["mass", "skin"] and "design_spec_confirmed.json" in zg.namelist(), (TG, zg.namelist())
    print("AI 글래스: 성능 항목 고르기 →", TG["targets"], "최적화 입력 묶음 저장 (최적 설계는 P01 만)")
    page.click("#mSketch")

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

    # P01: 성능 블록 고르기 → 물리 기반 최적화 실행 → 형상이 프레임마다 바뀌고 예측값이 움직임 → FEM 검증 값
    page.select_option("#example", "0"); page.wait_for_timeout(600)
    spec_then_design("P01b")
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
    assert "정밀 계산" in vals[0] and not page.is_hidden("#fOpt")
    page.screenshot(path=f"{SP}/gui_optimized.png")
    import urllib.request, zipfile, io
    href = page.get_attribute("#fOpt", "href").split("?")[0]
    base = URL.rstrip("/")
    z = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(base + href.replace("opt_final.stl", "optimize_input.zip")).read()))
    T = json.loads(z.read("optimize_targets.json"))
    assert sorted(T["targets"]) == ["Tmax", "f1"] and "opt_final.stl" in z.namelist() and "spec.json" in z.namelist(), T
    print("최적화 입력 묶음: 대상", T["targets"], "| 파일", len(z.namelist()), "개")
    # 영상 모드: 예시 목록 숨김, '2' 키 → 말을 치고 스케치를 그려 감 → 같은 TV01 로
    page.goto(URL.rstrip("/") + "/?video=1"); page.wait_for_timeout(1500)
    assert page.is_hidden("#example")
    t = time.time()
    page.keyboard.press("2"); page.wait_for_timeout(500)
    page.wait_for_function("() => !S.playing", timeout=90000)
    assert page.input_value("#text") == demos[1]["prompt"]
    spec_then_design("video_TV")
    assert page.evaluate("() => S.rep.template.id") == "TV01"
    print(f"영상 모드: 치기 · 그리기 {time.time() - t:.0f} s 포함")
    errs = [l for l in logs if "error" in l.lower() or "PAGEERROR" in l]
    print("\n".join(errs)[:2000] or "콘솔 오류 없음")
    b.close()
    sys.exit(1 if errs else 0)
