"""GUI end-to-end check with headless Chrome (playwright). Start app/server.py first.
   CHROME=/path/to/chrome python tests/e2e_gui.py   (screenshots -> <tmp>/formproof_e2e)"""
import json, math, os, sys, tempfile, time
from playwright.sync_api import sync_playwright

SP = os.path.join(tempfile.gettempdir(), "formproof_e2e"); os.makedirs(SP, exist_ok=True)
URL = "http://localhost:8765"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def draw(page, pts_list):
    box = page.locator("#pad").bounding_box()
    sx, sy = box["width"] / 800, box["height"] / 600
    for pts in pts_list:
        x, y = pts[0]
        page.mouse.move(box["x"] + x * sx, box["y"] + y * sy)
        page.mouse.down()
        for x, y in pts[1:]:
            page.mouse.move(box["x"] + x * sx, box["y"] + y * sy, steps=2)
        page.mouse.up()


def circle(cx, cy, r, n=40):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n + 1)]


def wait_result(page, timeout=90):
    page.wait_for_function("() => !document.querySelector('#busy').classList.contains('on') && document.querySelector('#go').disabled===false", timeout=timeout * 1000)
    time.sleep(1.5)


with sync_playwright() as p:
    b = p.chromium.launch(**({"executable_path": os.environ["CHROME"]} if os.environ.get("CHROME") else {"channel": "chrome"}),
                          args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    page = b.new_page(viewport={"width": 1440, "height": 1300})
    logs = []
    page.on("console", lambda m: logs.append(f"{m.type}: {m.text}"))
    page.on("pageerror", lambda e: logs.append(f"PAGEERROR: {e}"))
    page.goto(URL)
    page.wait_for_timeout(1500)
    page.screenshot(path=f"{SP}/gui_0_empty.png", full_page=True)

    # 1) hand sketch (side view: clamp circle, ears, straight arm, pad, strut) + text
    cx, cy, r = 210, 330, 48
    draw(page, [circle(cx, cy, r), circle(cx, cy, 36),
                [(196, 370), (196, 420), (224, 420), (224, 370)],
                [(cx, cy - r), (360, 300), (560, 262)],
                [(555, 250), (600, 250), (600, 268), (555, 268), (555, 250)],
                [(cx + r, cy), (420, 278)]])
    page.fill("#text", "자갈길에서도 폰이 안 흔들리게, 최대한 가볍게. 갤럭시 S25 울트라, 3D 프린터로 뽑을 거야")
    t = time.time()
    page.click("#go")
    wait_result(page)
    print("sketch run", round(time.time() - t, 1), "s | tag:", page.inner_text("#tplTag"))
    print("cands:", page.inner_text("#cands").replace("\n", " | "))
    page.screenshot(path=f"{SP}/gui_1_sketch.png", full_page=True)

    # 2) pick the 2nd candidate
    btns = page.locator("#cands button.cand")
    if btns.count() > 1:
        btns.nth(1).click()
        wait_result(page)
        print("candidate switch -> tag:", page.inner_text("#tplTag"))

    # 3) side view + drawing tabs
    page.click("button[data-pane=pside]")
    page.wait_for_timeout(500)
    page.locator("#view").screenshot(path=f"{SP}/gui_2_side.png")
    page.click("button[data-pane=pdraw]")
    page.wait_for_timeout(500)
    page.locator("#view").screenshot(path=f"{SP}/gui_3_draw.png")
    page.click("button[data-pane=p3d]")

    # 4) image attach (example hand-drawn image file)
    page.click("#mImage")
    page.set_input_files("#file", f"{ROOT}/examples/hand/hand_T05.png")
    page.fill("#text", "앞으로 길게, 튼튼하게")
    page.click("#go")
    wait_result(page)
    print("image run -> tag:", page.inner_text("#tplTag"))
    page.screenshot(path=f"{SP}/gui_4_image.png", full_page=True)

    # 5) text only
    page.click("#mSketch")
    page.click("#clear")
    page.fill("#text", "높게, L자로 꺾어서. 여름 땡볕에서도 변형 없고 화면 각도는 자유롭게")
    page.click("#go")
    wait_result(page)
    print("text run -> tag:", page.inner_text("#tplTag"))
    print("conditions:", page.inner_text("#cons")[:600].replace("\n", " | "))
    page.screenshot(path=f"{SP}/gui_5_text.png", full_page=True)

    # 6) hand-off download
    with page.expect_download() as d:
        page.click("#handoff")
    dl = d.value
    dl.save_as(f"{SP}/handoff_test.zip")
    print("download:", dl.suggested_filename)

    # 7) mobile width
    page.set_viewport_size({"width": 400, "height": 900})
    page.wait_for_timeout(800)
    page.screenshot(path=f"{SP}/gui_6_mobile.png", full_page=False)
    print("\n".join(l for l in logs if "error" in l.lower() or "PAGEERROR" in l)[:2000] or "no console errors")
    b.close()
