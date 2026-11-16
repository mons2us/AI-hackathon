"""Write the reference sketch sheet (one per template) and a few synthetic hand-drawn inputs.
  python make_examples.py   -> examples/templates/<id>.png, examples/templates_sheet.png, examples/hand/*.png
  T templates: drawn from the template parameters; look templates (G.., L-..): traced from their CAD (look_sketch).
  python make_examples.py --products -> only the demo products: TV stand sketches (TV01-04) and AI glasses photos
  (synthetic studio renders standing in for the real product photo)."""
import os
import sys
import numpy as np
from skimage import io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from formproof_input import sketch as S
from formproof_input.templates.library import INTEGRAL, LOOKS, TEMPLATES

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_t = os.path.join(HERE, "examples", "templates")
    out_h = os.path.join(HERE, "examples", "hand")
    os.makedirs(out_t, exist_ok=True)
    os.makedirs(out_h, exist_ok=True)
    for t in TEMPLATES:
        img = S.draw_image(S.template_strokes(t["params"], phone=False), px=420, line=3)
        io.imsave(os.path.join(out_t, f"{t['id']}.png"), (img * 255).astype(np.uint8), check_contrast=False)
    for t in LOOKS + INTEGRAL:                            # look templates: traced from their CAD side view; P01 rough
        img = S.draw_image(S.template_strokes(t["params"], phone=True), px=420, line=3)
        io.imsave(os.path.join(out_t, f"{t['id']}.png"), (img * 255).astype(np.uint8), check_contrast=False)
    rng = np.random.default_rng(2026)
    for t in TEMPLATES + LOOKS + INTEGRAL:
        st = S.perturb(S.template_strokes(t["params"], phone=rng.random() < 0.5), rng, 1.0)
        img = S.draw_image(st, px=int(rng.integers(360, 640)), mirror=rng.random() < 0.5, line=int(rng.integers(2, 6)))
        io.imsave(os.path.join(out_h, f"hand_{t['id']}.png"), (img * 255).astype(np.uint8), check_contrast=False)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    have = {f.name for f in font_manager.fontManager.ttflist}
    plt.rcParams["font.family"] = [f for f in ("Malgun Gothic", "AppleGothic", "NanumGothic", "Noto Sans CJK KR",
                                               "Noto Sans CJK JP") if f in have] or ["sans-serif"]
    fig, ax = plt.subplots(2, 5, figsize=(15, 6))
    for a, t in zip(ax.flat, TEMPLATES):
        a.imshow(io.imread(os.path.join(out_t, f"{t['id']}.png")), cmap="gray")
        a.set_title(f"{t['id']} {t['name']}\n{t['desc']}", fontsize=9)
        a.axis("off")
    fig.suptitle("자전거 폰 거치대 정형 스케치 (측면, 오른쪽 = 진행 방향, 원 = 핸들바 클램프)", fontsize=12)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "examples", "templates_sheet.png"), dpi=90)


def products():
    from PIL import Image
    from formproof_input.products import glasses as G
    from formproof_input.products import tv_stand as TV
    out_t = os.path.join(HERE, "examples", "templates")
    out_h = os.path.join(HERE, "examples", "hand")
    out_g = os.path.join(HERE, "examples", "glasses")
    os.makedirs(out_g, exist_ok=True)
    rng = np.random.default_rng(55)
    for t in TV.TEMPLATES:
        img = S.draw_image(TV.front_strokes(t["id"]), px=420, line=3)
        io.imsave(os.path.join(out_t, f"{t['id']}.png"), (img * 255).astype(np.uint8), check_contrast=False)
        st = S.perturb(TV.front_strokes(t["id"], with_tv=t["id"] in ("TV01", "TV03")), rng, 1.0, drop=())
        img = S.draw_image(st, px=int(rng.integers(420, 600)), line=int(rng.integers(3, 6)))
        io.imsave(os.path.join(out_h, f"hand_{t['id']}.png"), (img * 255).astype(np.uint8), check_contrast=False)
    for name, kw in (("합성_슬림오벌_투명렌즈", dict(style="slim_oval", seed=1)),
                     ("합성_슬림오벌_어두운렌즈", dict(style="slim_oval", seed=2, dark_lens=True, tilt_deg=-2.0)),
                     ("합성_캣아이_투명렌즈", dict(style="cat_eye", seed=3, tilt_deg=2.5))):
        Image.fromarray(G.render_photo(**kw)).save(os.path.join(out_g, f"{name}.jpg"), quality=88)


if __name__ == "__main__":
    if "--products" in sys.argv:
        products()
    else:
        main()
        products()
