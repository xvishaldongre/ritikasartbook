#!/usr/bin/env python3
"""Generate whimsical pastel placeholder artwork (SVG) for ritikasartbook.

These are stand-ins so the layout looks complete. Swap them for real scans
by replacing files in images/ with the same names (or edit the partials).
"""
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "images"
IMG.mkdir(exist_ok=True)

W, H = 800, 600

PALETTES = {
    "blush":   ["#FFE3EC", "#FFC8DD", "#FFAFCC", "#FDE2E4", "#FFF5F7", "#BDE0FE"],
    "mint":    ["#D8F3DC", "#B7E4C7", "#C7F0DB", "#95D5B2", "#F1FAEE", "#FFE5B4"],
    "sky":     ["#CDE8FF", "#A9D6F5", "#E8F4FD", "#BFE1F7", "#FFF3C4", "#FDE2E4"],
    "butter":  ["#FFF3C4", "#FFE9A8", "#FFF9E6", "#FFDFBA", "#D8F3DC", "#FFC8DD"],
    "lavender":["#E7DCFB", "#D8C6F5", "#F3EDFF", "#CDB4F0", "#FFE3EC", "#CDE8FF"],
    "peach":   ["#FFE5D9", "#FFD7BA", "#FFF1E6", "#FCD5CE", "#FFE3EC", "#C7F0DB"],
}
CAT_STYLE = {
    "book-cover": "lavender",
    "general-illustration": "sky",
    "character-design": "peach",
    # cycling lists give each piece its own colour story
    "surface-pattern": ["mint", "blush", "butter", "sky", "lavender", "peach"],
    "portfolio": ["blush", "sky", "lavender", "mint", "peach", "butter", "sky", "mint"],
    "hero": "butter",
}

# Legible motif colours (deeper than the washes, so pattern artwork never
# disappears into its own background).
MOTIF = {
    "blush":    ["#FF8FBF", "#FFB3D1", "#FFC94D", "#7FB8E0"],
    "mint":     ["#5FBF8A", "#9FE3C0", "#FF9EC4", "#FFC94D"],
    "sky":      ["#5C9FD6", "#A9D6F5", "#FF9EC4", "#FFC94D"],
    "butter":   ["#E8B62C", "#FFD96A", "#FF9EC4", "#7FB8E0"],
    "lavender": ["#A57BD8", "#CDB4F0", "#FF9EC4", "#FFC94D"],
    "peach":    ["#F2835C", "#FFB694", "#FF9EC4", "#7FB8E0"],
}


def lerp(a, b, t):
    return a + (b - a) * t


def grad(idx, pal):
    """Soft two-stop pastel gradient definition."""
    c1, c2 = pal[idx % len(pal)], pal[(idx + 2) % len(pal)]
    return (
        f'<linearGradient id="bg{idx}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0%" stop-color="{c1}"/><stop offset="100%" stop-color="{c2}"/>'
        f"</linearGradient>"
    )


def hill(y, color, amp=40, phase=0.0, opacity=1.0):
    pts = []
    for i in range(0, 41):
        x = W * i / 40
        yy = y + amp * math.sin((i / 40) * math.pi * 2 + phase)
        pts.append(f"{x:.1f},{yy:.1f}")
    return (
        f'<polygon points="0,{H} {" ".join(pts)} {W},{H}" fill="{color}" '
        f'opacity="{opacity}"/>'
    )


def cloud(cx, cy, s, color, opacity=0.9):
    return (
        f'<g fill="{color}" opacity="{opacity}" transform="translate({cx},{cy}) scale({s})">'
        f'<ellipse cx="0" cy="0" rx="52" ry="30"/>'
        f'<ellipse cx="-40" cy="8" rx="34" ry="22"/>'
        f'<ellipse cx="42" cy="10" rx="30" ry="20"/>'
        f"</g>"
    )


def sparkle(cx, cy, s, color):
    return (
        f'<path transform="translate({cx},{cy}) scale({s})" fill="{color}" '
        f'd="M0,-16 C2,-5 5,-2 16,0 C5,2 2,5 0,16 C-2,5 -5,2 -16,0 C-5,-2 -2,-5 0,-16 Z"/>'
    )


def flower(cx, cy, s, petal, center):
    parts = [f'<g transform="translate({cx},{cy}) scale({s})">']
    for i in range(5):
        a = i * 72
        parts.append(
            f'<ellipse cx="0" cy="-16" rx="9" ry="15" fill="{petal}" '
            f'transform="rotate({a})"/>'
        )
    parts.append(f'<circle r="8" fill="{center}"/></g>')
    return "".join(parts)


def moon(cx, cy, r, color="#FFF6D6"):
    return (
        f'<g><circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}"/>'
        f'<circle cx="{cx + r * 0.38}" cy="{cy - r * 0.22}" r="{r * 0.86}" '
        f'fill="url(#bg0)" opacity="0.0"/></g>'
    )


def critter(cx, cy, s, body, accent, ink="#6B5B71"):
    """A small cute creature - the whimsy mascot."""
    return f"""<g transform="translate({cx},{cy}) scale({s})">
  <ellipse cx="0" cy="52" rx="46" ry="10" fill="{ink}" opacity="0.10"/>
  <ellipse cx="0" cy="0" rx="44" ry="40" fill="{body}"/>
  <ellipse cx="-30" cy="-34" rx="15" ry="16" fill="{body}"/>
  <ellipse cx="30" cy="-34" rx="15" ry="16" fill="{body}"/>
  <ellipse cx="-30" cy="-34" rx="7" ry="8" fill="{accent}"/>
  <ellipse cx="30" cy="-34" rx="7" ry="8" fill="{accent}"/>
  <circle cx="-14" cy="-4" r="5" fill="{ink}"/>
  <circle cx="14" cy="-4" r="5" fill="{ink}"/>
  <circle cx="-12.5" cy="-5.5" r="1.8" fill="#FFFFFF"/>
  <circle cx="15.5" cy="-5.5" r="1.8" fill="#FFFFFF"/>
  <path d="M-9,12 Q0,21 9,12" stroke="{ink}" stroke-width="3.4" fill="none"
        stroke-linecap="round"/>
  <circle cx="-26" cy="12" r="6" fill="{accent}" opacity="0.55"/>
  <circle cx="26" cy="12" r="6" fill="{accent}" opacity="0.55"/>
</g>"""


def scene(kind, idx, seed, cat):
    rnd = random.Random(seed)
    style = CAT_STYLE.get(cat, "blush")
    if isinstance(style, list):
        style = style[(idx - 1) % len(style)]
    pal = PALETTES[style]
    mot = MOTIF[style]
    c = [rnd.choice(pal) for _ in range(6)]
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img">',
        f"<defs>{grad(idx, pal)}</defs>",
        f'<rect width="{W}" height="{H}" fill="url(#bg{idx})"/>',
    ]

    if kind == "landscape":
        out.append(moon(650, 110, 46, pal[4]))
        out.append(cloud(160, 110, 1.0, "#FFFFFF", 0.85))
        out.append(cloud(430, 70, 0.72, "#FFFFFF", 0.7))
        out.append(hill(330, c[2], 34, 0.4, 0.85))
        out.append(hill(420, c[1], 44, 2.1, 0.9))
        out.append(hill(520, c[3], 30, 1.2, 0.95))
        for i in range(4):
            out.append(flower(90 + i * 190, 545 - (i % 2) * 26, 0.85, c[0], pal[3]))
        out.append(sparkle(300, 180, 0.9, "#FFFFFF"))
        out.append(sparkle(560, 240, 0.6, "#FFFFFF"))
        out.append(critter(390, 400, 0.85, "#FFFFFF", c[0]))

    elif kind == "pattern":
        # patterns get their own light wash so motifs stay readable when tiled
        out[1] = (
            f'<defs><linearGradient id="pat{idx}" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0%" stop-color="{pal[0]}"/>'
            f'<stop offset="100%" stop-color="{pal[4]}"/></linearGradient></defs>'
        )
        out[2] = f'<rect width="{W}" height="{H}" fill="url(#pat{idx})"/>'
        step_x, step_y = 150, 132
        for r in range(5):
            for col in range(7):
                x = 42 + col * step_x + (75 if r % 2 else 0)
                y = r * step_y + 58
                choice = (r * 3 + col) % 4
                if choice == 0:
                    out.append(flower(x, y, 1.2, mot[0], mot[3]))
                elif choice == 1:
                    out.append(sparkle(x, y, 0.95, mot[2]))
                elif choice == 2:
                    out.append(
                        f'<circle cx="{x}" cy="{y}" r="21" fill="{mot[1]}" opacity="0.95"/>'
                        f'<circle cx="{x}" cy="{y}" r="9" fill="{mot[3]}" opacity="0.95"/>'
                    )
                else:
                    out.append(
                        f'<circle cx="{x}" cy="{y}" r="9" fill="{mot[0]}" opacity="0.85"/>'
                        f'<ellipse cx="{x + 36}" cy="{y + 26}" rx="13" ry="8" '
                        f'fill="{mot[2]}" opacity="0.8"/>'
                    )

    elif kind == "portrait":
        out.append(cloud(140, 100, 0.85, "#FFFFFF", 0.7))
        out.append(cloud(650, 150, 0.65, "#FFFFFF", 0.6))
        out.append(hill(470, c[2], 26, 1.6, 0.8))
        out.append(sparkle(210, 190, 1.0, "#FFFFFF"))
        out.append(sparkle(600, 300, 0.7, "#FFFFFF"))
        out.append(sparkle(330, 120, 0.55, "#FFFFFF"))
        out.append(critter(400, 330, 1.5, "#FFFFFF", c[0]))

    else:  # "abstract" / cover art
        out.append(moon(400, 250, 120, pal[4]))
        out.append(hill(400, c[1], 40, 0.7, 0.75))
        out.append(hill(500, c[2], 34, 2.4, 0.9))
        for i, (x, y, s) in enumerate(
            [(170, 140, 1.1), (640, 180, 0.9), (400, 90, 0.7), (560, 420, 0.8),
             (200, 430, 0.7)]
        ):
            out.append(sparkle(x, y, s, "#FFFFFF"))
        out.append(flower(120, 520, 1.0, c[0], pal[3]))
        out.append(flower(690, 500, 0.85, c[3], pal[4]))

    out.append("</svg>")
    return "\n".join(out)


KINDS = {
    "book-cover": ["abstract", "portrait", "landscape"],
    "general-illustration": ["landscape", "abstract", "portrait"],
    "character-design": ["portrait", "landscape", "abstract"],
    "surface-pattern": ["pattern", "pattern", "pattern"],
    "portfolio": ["landscape", "portrait", "abstract", "pattern"],
}


def build(cat, count, prefix):
    for i in range(1, count + 1):
        kind = KINDS[cat][(i - 1) % len(KINDS[cat])]
        svg = scene(kind, i, seed=hash((cat, i)) & 0xFFFF, cat=cat)
        (IMG / f"{prefix}-{i}.svg").write_text(svg, encoding="utf-8")


def build_logo():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64"
  height="64" role="img">
  <circle cx="32" cy="32" r="30" fill="#FFE3EC"/>
  <path d="M32 12 C40 22 44 28 44 36 a12 12 0 0 1 -24 0 C20 28 24 22 32 12 Z"
        fill="#FFAFCC"/>
  <circle cx="26" cy="35" r="3.4" fill="#6B5B71"/>
  <circle cx="38" cy="35" r="3.4" fill="#6B5B71"/>
  <path d="M26 43 Q32 48 38 43" stroke="#6B5B71" stroke-width="3" fill="none"
        stroke-linecap="round"/>
  <circle cx="45" cy="18" r="4" fill="#FFF3C4"/>
</svg>"""
    (IMG / "logo.svg").write_text(svg, encoding="utf-8")
    (ROOT / "favicon.svg").write_text(svg, encoding="utf-8")


def build_og():
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630"
  width="1200" height="630">
  <defs><linearGradient id="og" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#FFE3EC"/><stop offset="45%" stop-color="#FFF3C4"/>
    <stop offset="100%" stop-color="#CDE8FF"/></linearGradient></defs>
  <rect width="1200" height="630" fill="url(#og)"/>
  {sparkle(180, 140, 1.4, "#FFFFFF")}
  {sparkle(1020, 200, 1.1, "#FFFFFF")}
  {sparkle(950, 500, 0.8, "#FFFFFF")}
  {cloud(300, 480, 1.1, "#FFFFFF", 0.75)}
  {cloud(900, 460, 0.9, "#FFFFFF", 0.6)}
  {flower(140, 560, 1.4, "#FFC8DD", "#FFF3C4")}
  {flower(1080, 560, 1.2, "#C7F0DB", "#FFFFFF")}
  <text x="600" y="300" text-anchor="middle" font-family="Verdana, sans-serif"
        font-size="86" font-weight="bold" fill="#6B5B71">ritikasartbook</text>
  <text x="600" y="380" text-anchor="middle" font-family="Verdana, sans-serif"
        font-size="38" fill="#8A7A90">whimsical illustration &amp; surface pattern</text>
</svg>"""
    (IMG / "og-cover.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    counts = {
        "book-cover": 6,
        "general-illustration": 6,
        "character-design": 6,
        "surface-pattern": 8,
        "portfolio": 8,
    }
    for cat, n in counts.items():
        build(cat, n, cat)
    build_logo()
    build_og()
    made = sorted(p.name for p in IMG.glob("*.svg"))
    print(f"generated {len(made)} files:")
    print("\n".join(made))
