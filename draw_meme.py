#!/usr/bin/env python3
"""Draw the gta6-meme-x-01 entry: a Vice City sunset meme, 1200x1200 PNG.

Deterministic: fixed geometry, seeded randomness, no wall clock, no network.
The make.fun ghost mark (ghost-mark.png, fetched from https://make.fun/press/)
is composited into the scene as the driver of the convertible, and the name
"make.fun" appears on a billboard. Run: python3 draw_meme.py -> meme.png
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 1200
HERE = Path(__file__).resolve().parent
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Palette: Vice City sunset.
SKY_TOP = (255, 46, 136)      # hot pink
SKY_MID = (255, 122, 61)      # orange
SKY_LOW = (255, 201, 60)      # golden horizon
SUN_CORE = (255, 243, 176)
SUN_GLOW = (255, 214, 90)
SKYLINE = (43, 10, 61)        # dark purple buildings
PALM = (30, 11, 51)           # palm silhouettes
ROAD = (22, 10, 36)           # dark asphalt
CAR = (233, 30, 140)          # magenta convertible
CAR_DARK = (160, 12, 96)
BILLBOARD = (216, 17, 122)    # magenta panel
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 210, 63)
WINDOW = (255, 210, 63)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def font(size):
    return ImageFont.truetype(FONT_PATH, size)


def fit_font(draw, text, start_size, max_width):
    """Largest bold size at which text fits max_width."""
    size = start_size
    while size > 10:
        f = font(size)
        if draw.textlength(text, font=f) <= max_width:
            return f
        size -= 2
    return font(10)


def outlined_text(draw, xy, text, fnt, fill, stroke=4):
    draw.text(xy, text, font=fnt, fill=fill,
              stroke_width=stroke, stroke_fill=BLACK)


def centered_text(draw, cx, y, text, fnt, fill, stroke=4):
    w = draw.textlength(text, font=fnt)
    outlined_text(draw, (cx - w / 2, y), text, fnt, fill, stroke)


def draw_sky(img):
    px = img.load()
    for y in range(760):
        if y < 380:
            t = y / 380.0
            c = lerp(SKY_TOP, SKY_MID, t)
        else:
            t = (y - 380) / 380.0
            c = lerp(SKY_MID, SKY_LOW, t)
        for x in range(W):
            px[x, y] = c


def draw_sun(draw):
    cx, cy, r = 600, 520, 150
    for i, (rr, col) in enumerate([(210, (255, 190, 60)),
                                   (180, SUN_GLOW),
                                   (150, SUN_CORE)]):
        draw.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)
    # Sun stripes (retro synthwave slats) across the lower half.
    for i, y in enumerate(range(cy + 30, cy + 150, 26)):
        half = int(math.sqrt(max(0, r * r - (y - cy) ** 2)))
        draw.rectangle([cx - half, y, cx + half, y + 9], fill=SKY_LOW)


def draw_sparkles(draw):
    rng = random.Random(7)
    for _ in range(14):
        x = rng.randint(30, 1170)
        y = rng.randint(20, 300)
        s = rng.randint(4, 9)
        draw.polygon([(x, y - s), (x + s // 3, y - s // 3), (x + s, y),
                      (x + s // 3, y + s // 3), (x, y + s),
                      (x - s // 3, y + s // 3), (x - s, y),
                      (x - s // 3, y - s // 3)], fill=WHITE)


def draw_billboard(draw):
    # Poles first (skyline will cover their feet).
    draw.rectangle([95, 445, 107, 640], fill=PALM)
    draw.rectangle([395, 445, 407, 640], fill=PALM)
    # Panel.
    draw.rounded_rectangle([55, 330, 445, 445], radius=18,
                           fill=BILLBOARD, outline=BLACK, width=7)
    f = fit_font(draw, "make.fun", 84, 360)
    centered_text(draw, 250, 348, "make.fun", f, WHITE, stroke=3)


def draw_skyline(draw):
    rng = random.Random(42)
    x = 0
    while x < W:
        bw = rng.randint(55, 130)
        bh = rng.randint(90, 220)
        top = 760 - bh
        draw.rectangle([x, top, x + bw, 760], fill=SKYLINE)
        # Antenna on some buildings.
        if rng.random() < 0.4:
            draw.rectangle([x + bw // 2 - 2, top - 34, x + bw // 2 + 2, top],
                           fill=SKYLINE)
            draw.ellipse([x + bw // 2 - 5, top - 42, x + bw // 2 + 5, top - 32],
                         fill=(255, 80, 80))
        # Lit windows.
        for wy in range(top + 14, 748, 26):
            for wx in range(x + 10, x + bw - 12, 24):
                if rng.random() < 0.35:
                    draw.rectangle([wx, wy, wx + 10, wy + 14], fill=WINDOW)
        x += bw + rng.randint(2, 14)


def draw_palm(draw, base_x, base_y, lean, scale, flip=False):
    """A palm silhouette: curved trunk + 7 fronds."""
    top_x = base_x + lean
    top_y = base_y - int(300 * scale)
    # Trunk as a series of segments along a curve.
    segs = 14
    prev = (base_x, base_y)
    for i in range(1, segs + 1):
        t = i / segs
        x = base_x + lean * t * t
        y = base_y - int(300 * scale) * t
        wdt = max(4, int(16 * scale * (1 - 0.5 * t)))
        draw.line([prev, (x, y)], fill=PALM, width=wdt)
        prev = (x, y)
    # Fronds: arcs drooping from the crown.
    for k in range(7):
        ang = -160 + k * 26  # degrees, spread over the crown
        rad = math.radians(ang)
        length = int(150 * scale)
        ex = top_x + int(math.cos(rad) * length)
        ey = top_y + int(math.sin(rad) * length * 0.55) + 26
        # Frond as a thick arc: approximate with a quadratic curve.
        midx = top_x + int(math.cos(rad) * length * 0.5)
        midy = top_y + int(math.sin(rad) * length * 0.28) - 18
        pts = []
        for s in range(21):
            t = s / 20.0
            px = (1 - t) ** 2 * top_x + 2 * (1 - t) * t * midx + t * t * ex
            py = (1 - t) ** 2 * top_y + 2 * (1 - t) * t * midy + t * t * ey
            pts.append((px, py))
        draw.line(pts, fill=PALM, width=max(5, int(9 * scale)), joint="curve")
    # Coconuts.
    draw.ellipse([top_x - 12, top_y + 2, top_x + 2, top_y + 16], fill=PALM)
    draw.ellipse([top_x + 2, top_y + 4, top_x + 16, top_y + 18], fill=PALM)


def draw_road(draw):
    draw.rectangle([0, 760, W, H], fill=ROAD)
    draw.rectangle([0, 760, W, 768], fill=(58, 20, 84))
    # Subtle lane dashes below the caption area.
    for x in range(60, W, 180):
        draw.rectangle([x, 1188, x + 90, 1195], fill=(90, 60, 110))


def draw_car(draw):
    # Convertible body.
    draw.rounded_rectangle([280, 850, 920, 950], radius=34,
                           fill=CAR, outline=BLACK, width=6)
    # Hood / trunk hint lines.
    draw.line([(330, 872), (870, 872)], fill=CAR_DARK, width=5)
    # Wheels.
    for wx in (360, 800):
        draw.ellipse([wx - 52, 920, wx + 52, 1024], fill=BLACK)
        draw.ellipse([wx - 26, 946, wx + 26, 998], fill=(150, 150, 160))
        draw.ellipse([wx - 10, 962, wx + 10, 982], fill=(60, 60, 70))
    # Headlight.
    draw.ellipse([884, 892, 916, 916], fill=YELLOW, outline=BLACK, width=3)


def main():
    img = Image.new("RGB", (W, H), SKY_TOP)
    draw = ImageDraw.Draw(img)

    draw_sky(img)
    draw_sparkles(draw)
    draw_sun(draw)
    draw_billboard(draw)
    draw_skyline(draw)
    draw_palm(draw, 48, 760, -18, 0.68)
    draw_palm(draw, 1110, 760, 35, 1.05)
    draw_road(draw)
    draw_car(draw)

    # The make.fun ghost: the real press mark, driving the convertible.
    # Drawn after the car so its lower edge tucks behind the car's top edge.
    ghost = Image.open(HERE / "ghost-mark.png").convert("RGBA")
    ghost = ghost.resize((260, 260), Image.LANCZOS)
    img.paste(ghost, (640, 620), ghost)

    # Captions.
    f1 = fit_font(draw, "13 YEARS OF WAITING.", 62, 1120)
    centered_text(draw, 600, 34, "13 YEARS OF WAITING.", f1, WHITE, stroke=4)
    f2 = fit_font(draw, "GTA 6 IS FINALLY OUT", 96, 1140)
    centered_text(draw, 600, 108, "GTA 6 IS FINALLY OUT", f2, YELLOW, stroke=5)
    f3 = fit_font(draw, "MY SICK LEAVE WAS", 64, 1120)
    centered_text(draw, 600, 1036, "MY SICK LEAVE WAS", f3, WHITE, stroke=4)
    f4 = fit_font(draw, "APPROVED 13 YEARS AGO.", 64, 1120)
    centered_text(draw, 600, 1108, "APPROVED 13 YEARS AGO.", f4, WHITE, stroke=4)

    img.save(HERE / "meme.png", format="PNG")


if __name__ == "__main__":
    main()
