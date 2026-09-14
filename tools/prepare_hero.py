#!/usr/bin/env python3
"""Prepare the hero artwork from a source PNG.

    .venv/bin/python tools/prepare_hero.py [source.png] [--mode bust|full]

Modes
  bust  (default) square head-and-torso crop, framed for the round hero portrait
  full            the whole figure, cut out (kept for other uses)

The script finds the figure via the alpha channel, crops away the empty canvas,
ignores stray export marks, and writes web-ready files:

    images/hero-ritika.png    transparent PNG (fallback)
    images/hero-ritika.webp   transparent WebP (served first, much smaller)

The heavy source file stays in Downloads and is never committed. Re-run this
whenever you export new hero art.
"""
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "images"

# ---------------------------------------------------------------- tuning ----
# Output size: the portrait is displayed around 440px across, so 900 is ~2x
# for crisp rendering on high-density screens.
BUST_PX = 900
FULL_PX_H = 1150

# Square bust crop, expressed relative to the figure's bounding box.
BUST_WIDTH_FACTOR = 1.035   # >1 leaves a sliver of air around her shoulders
BUST_TOP_FACTOR = -0.015    # negative nudges the crop up, so hair is not cut

# The backpack makes the bounding box wider on her right, so the *body* centre
# sits left of the geometric centre. Nudge by this fraction of the bbox width
# to keep her face centred in the round frame.
BODY_CENTRE_SHIFT = 0.05

# Padding for the full-figure cut-out.
PAD_X = 0.02
PAD_TOP = 0.01
PAD_BOTTOM = 0.012

# Stray marks in the source export sit outside the figure (a thin sliver near
# x=3140). Ignore anything beyond this x when measuring the content.
IGNORE_RIGHT_OF = 2000


def content_box(im):
    """Bounding box of the actual drawn figure, ignoring stray export marks."""
    alpha = im.getchannel("A")
    if not alpha.getbbox():
        raise SystemExit("source image is fully transparent - nothing to crop")

    a = alpha.load()
    w, h = im.size
    limit = min(w, IGNORE_RIGHT_OF)

    cols = []
    for x in range(limit):
        for y in range(0, h, 4):              # sample rows: fast enough, plenty exact
            if a[x, y] > 200:
                cols.append(x)
                break
    if not cols:
        return alpha.getbbox()
    x0, x1 = min(cols), max(cols)

    rows = [y for y in range(h)
            if any(a[x, y] > 200 for x in range(x0, x1 + 1, 4))]
    return (x0, min(rows), x1 + 1, max(rows) + 1)


def bust_crop(im, box):
    """Square head-and-torso crop, centred on the body rather than the bbox."""
    x0, y0, x1, y1 = box
    fw = x1 - x0
    size = int(round(fw * BUST_WIDTH_FACTOR))
    cx = (x0 + x1) // 2 - int(round(fw * BODY_CENTRE_SHIFT))
    top = y0 + int(round(size * BUST_TOP_FACTOR))
    left = cx - size // 2
    return (max(0, left), max(0, top),
            min(im.width, left + size), min(im.height, top + size))


def full_crop(im, box):
    x0, y0, x1, y1 = box
    fw, fh = x1 - x0, y1 - y0
    px, ptop, pbot = int(fw * PAD_X), int(fh * PAD_TOP), int(fh * PAD_BOTTOM)
    return (max(0, x0 - px), max(0, y0 - ptop),
            min(im.width, x1 + px), min(im.height, y1 + pbot))


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    mode = "bust"
    for a in sys.argv[1:]:
        if a.startswith("--mode"):
            mode = a.split("=", 1)[1] if "=" in a else mode
    if "--mode" in sys.argv:
        mode = sys.argv[sys.argv.index("--mode") + 1]

    src = Path(argv[0]) if argv else Path.home() / "Downloads" / "hero-art.png"
    if not src.exists():
        raise SystemExit(f"source image not found: {src}")
    if mode not in ("bust", "full"):
        raise SystemExit("--mode must be 'bust' or 'full'")

    im = Image.open(src).convert("RGBA")
    print(f"source : {src}")
    print(f"         {im.width}x{im.height}")

    box = content_box(im)
    x0, y0, x1, y1 = box
    print(f"figure : x {x0}..{x1}  y {y0}..{y1}   ({x1 - x0}x{y1 - y0})")
    print(f"mode   : {mode}")

    crop_box = bust_crop(im, box) if mode == "bust" else full_crop(im, box)
    crop = im.crop(crop_box)
    print(f"crop   : {crop.width}x{crop.height}  (aspect {crop.width / crop.height:.3f})")

    if mode == "bust":
        size = (BUST_PX, BUST_PX)
    else:
        size = (max(1, round(crop.width * FULL_PX_H / crop.height)), FULL_PX_H)
    out = crop.resize(size, Image.LANCZOS)
    print(f"output : {size[0]}x{size[1]}")

    OUT.mkdir(exist_ok=True)
    png, webp = OUT / "hero-ritika.png", OUT / "hero-ritika.webp"
    out.save(png, optimize=True)
    out.save(webp, quality=90, method=6)
    print(f"wrote  : {png.relative_to(ROOT)}  ({png.stat().st_size / 1024:.0f} KB)")
    print(f"wrote  : {webp.relative_to(ROOT)} ({webp.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
