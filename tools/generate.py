import math
import pathlib
import random

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

NIGHT = "#140c2b"
INDIGO = "#1f1440"
RED = "#d52b1e"
DARK_RED = "#8e1a14"
GOLD = "#f8c300"
DARK_GOLD = "#b58900"
GREEN = "#00873e"
DARK_GREEN = "#005a2b"
WHITE = "#ffffff"
TURQUOISE = "#1fb5a8"

FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "G": ["01111", "10000", "10000", "10011", "10001", "10001", "01111"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "Б": ["11111", "10000", "10000", "11110", "10001", "10001", "11110"],
    "И": ["10001", "10011", "10101", "10101", "11001", "10001", "10001"],
    "Ш": ["10101", "10101", "10101", "10101", "10101", "10101", "11111"],
    "Ф": ["00100", "01110", "10101", "10101", "10101", "01110", "00100"],
    "Ҳ": ["100010", "100010", "010100", "001000", "010100", "100010", "100011"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "·": ["000", "000", "000", "010", "000", "000", "000"],
    " ": ["000", "000", "000", "000", "000", "000", "000"],
}
FONT["Р"] = FONT["P"]
FONT["А"] = FONT["A"]
FONT["М"] = FONT["M"]
FONT["Т"] = FONT["T"]
FONT["О"] = FONT["O"]


def text_width(s, scale):
    return sum((len(FONT[c][0]) + 1) * scale for c in s) - scale


def draw_text(grid, s, x0, y0, scale, color, shadow=None):
    if shadow:
        draw_text(grid, s, x0 + scale, y0 + scale, scale, shadow)
    x = x0
    for c in s:
        g = FONT[c]
        for gy, row in enumerate(g):
            for gx, bit in enumerate(row):
                if bit == "1":
                    for dy in range(scale):
                        for dx in range(scale):
                            grid.set(x + gx * scale + dx, y0 + gy * scale + dy, color)
        x += (len(g[0]) + 1) * scale


class Grid:
    def __init__(self, w, h, px):
        self.w, self.h, self.px = w, h, px
        self.cells = [[None] * w for _ in range(h)]
        self.layers = []

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.cells[y][x] = c

    def get(self, x, y):
        return self.cells[y][x] if 0 <= x < self.w and 0 <= y < self.h else None

    def rects(self, cells=None):
        cells = cells or self.cells
        out = []
        p = self.px
        for y, row in enumerate(cells):
            x = 0
            while x < len(row):
                c = row[x]
                if c is None:
                    x += 1
                    continue
                start = x
                while x < len(row) and row[x] == c:
                    x += 1
                out.append((c, f"M{start * p} {y * p}h{(x - start) * p}v{p}h-{(x - start) * p}z"))
        by = {}
        for c, d in out:
            by.setdefault(c, []).append(d)
        return "".join(f'<path fill="{c}" d="{"".join(ds)}"/>' for c, ds in by.items())


def ornament_motif():
    return [
        ".....GG.....",
        "....GRRG....",
        "...GRWWRG...",
        "..GRWYYWRG..",
        ".GRWY..YWRG.",
        "GRWY.RR.YWRG",
        "GRWY.RR.YWRG",
        ".GRWY..YWRG.",
        "..GRWYYWRG..",
        "...GRWWRG...",
        "....GRRG....",
        ".....GG.....",
    ]


def small_motif():
    return [
        "..Y..",
        ".YRY.",
        "YRWRY",
        ".YRY.",
        "..Y..",
    ]


PAL = {"G": GREEN, "R": RED, "W": WHITE, "Y": GOLD, "T": TURQUOISE, "D": DARK_RED}


def draw_band(grid, y0, bg=NIGHT):
    w = grid.w
    for x in range(w):
        for y in range(y0, y0 + 16):
            grid.set(x, y, bg)
        grid.set(x, y0, GOLD)
        grid.set(x, y0 + 15, GOLD)
        tooth = x % 4
        if tooth in (0, 1, 2):
            grid.set(x, y0 + 1, RED)
            grid.set(x, y0 + 14, GREEN)
        if tooth == 1:
            grid.set(x, y0 + 2, RED)
            grid.set(x, y0 + 13, GREEN)
    motif = ornament_motif()
    step = 18
    offset = (w % step) // 2
    for mx in range(offset - step, w, step):
        for my, row in enumerate(motif):
            for mxi, ch in enumerate(row):
                if ch in PAL:
                    grid.set(mx + mxi, y0 + 2 + my, PAL[ch])
        sm = small_motif()
        for sy, row in enumerate(sm):
            for sx, ch in enumerate(row):
                if ch in PAL:
                    grid.set(mx + 12 + 1 + sx, y0 + 5 + sy, PAL[ch])


def mountain_heights(w, peaks, base, rng, jitter=1):
    h = [base] * w
    side = [False] * w
    for px_, py_, slope in peaks:
        for x in range(w):
            y = py_ + abs(x - px_) / slope
            if y < h[x]:
                h[x] = y
                side[x] = x > px_
    out = [int(h[x]) for x in range(w)]
    return list(zip(out, side))


def draw_mountains(grid, heights, bottom, light, shade, snow=None, snow_shade=None, snowline=None, rng=None):
    for x, (top, shadow) in enumerate(heights):
        for y in range(top, bottom):
            grid.set(x, y, shade if shadow else light)
        if snow and snowline is not None and top < snowline:
            depth = snowline - top + (1 if (x * 5) % 3 == 0 else 0)
            for y in range(top, top + max(1, depth)):
                grid.set(x, y, snow_shade if shadow else snow)


def build_header():
    W, H, P = 300, 96, 4
    g = Grid(W, H, P)
    rng = random.Random(186)

    sky = [
        (0, "#140c2b"), (10, "#1d1238"), (20, "#281747"), (30, "#3a1d52"),
        (38, "#521f55"), (45, "#6f2452"), (51, "#932b4a"), (56, "#b8363e"),
        (60, "#d74f32"), (64, "#ec7a2c"), (68, "#f6a531"),
    ]
    for i, (y0, c) in enumerate(sky):
        y1 = sky[i + 1][0] if i + 1 < len(sky) else 80
        for y in range(y0, y1):
            for x in range(W):
                if i + 1 < len(sky) and y == y1 - 1 and x % 2 == 0:
                    g.set(x, y, sky[i + 1][1])
                else:
                    g.set(x, y, c)

    sx, sy, r = 232, 58, 11
    for y in range(sy - r, sy + r + 1):
        for x in range(sx - r, sx + r + 1):
            d = math.hypot(x - sx, y - sy)
            if d <= r:
                g.set(x, y, "#ffd93b" if d < r - 2 else GOLD)
            elif d <= r + 2 and (x + y) % 2 == 0:
                g.set(x, y, "#f7b733")

    far = mountain_heights(W, [(20, 46, 1.3), (70, 40, 1.1), (130, 44, 1.2), (190, 38, 1.0), (265, 44, 1.3)], 80, rng)
    draw_mountains(g, far, 82, "#7a3a6e", "#5e2c5a", "#e9d6ea", "#c6a9c9", snowline=47, rng=rng)

    mid = mountain_heights(W, [(45, 52, 1.0), (105, 47, 0.9), (160, 54, 1.1), (215, 49, 0.9), (285, 53, 1.0)], 84, rng)
    draw_mountains(g, mid, 84, "#3d2358", "#2a1742", WHITE, "#b9c3dc", snowline=55, rng=rng)

    near = mountain_heights(W, [(0, 72, 3.0), (80, 70, 3.5), (170, 73, 3.0), (250, 70, 3.2), (300, 72, 3.0)], 82, rng)
    draw_mountains(g, near, 82, DARK_GREEN, "#004220")
    for x in range(W):
        top = near[x][0]
        if (x * 7) % 5 == 0:
            g.set(x, top, GREEN)
        if x % 9 == 0:
            for y in range(top - 3, top):
                g.set(x, y, "#004220")
            g.set(x - 1, top - 2, "#004220")
            g.set(x + 1, top - 2, "#004220")

    draw_band(g, 80)

    crown = [
        "........Y........",
        ".......YYY.......",
        "..Y.....Y.....Y..",
        "..YY...YYY...YY..",
        "..YYY.YYYYY.YYY..",
        "..YYYYYYYYYYYYY..",
        "..YYYRYYYYYRYYY..",
        "..YYYYYYYYYYYYY..",
        "..YYYYYYYYYYYYY..",
    ]
    stars_arc = []
    cx = W // 2
    cw = len(crown[0])
    for ry, row in enumerate(crown):
        for rx, ch in enumerate(row):
            if ch in PAL:
                g.set(cx - cw // 2 + rx, 3 + ry, PAL[ch])
    for i in range(7):
        a = math.pi * (0.15 + 0.7 * i / 6)
        stx = int(round(cx - math.cos(a) * 22))
        sty = int(round(11 - math.sin(a) * 9))
        g.set(stx, sty, GOLD)
        g.set(stx - 1, sty, GOLD)
        g.set(stx + 1, sty, GOLD)
        g.set(stx, sty - 1, GOLD)
        g.set(stx, sty + 1, GOLD)

    name = "AZAMBEK ALIMBAEV"
    tw = text_width(name, 2)
    draw_text(g, name, (W - tw) // 2, 15, 2, WHITE, shadow=DARK_RED)

    sub = "PYTHON DEVELOPER · TAJIKISTAN"
    sw = text_width(sub, 1)
    draw_text(g, sub, (W - sw) // 2, 34, 1, GOLD, shadow="#140c2b")

    base = g.rects()

    star_pts = []
    taken = set()
    while len(star_pts) < 38:
        x, y = rng.randrange(2, W - 2), rng.randrange(1, 40)
        if 50 < x < 250 and y < 44:
            continue
        if any(abs(x - a) < 4 and abs(y - b) < 4 for a, b in taken):
            continue
        taken.add((x, y))
        star_pts.append((x, y))
    stars = []
    for i, (x, y) in enumerate(star_pts):
        cls = f"s{i % 4}"
        if i % 5 == 0:
            stars.append(
                f'<g class="{cls}"><rect x="{x * P}" y="{(y - 1) * P}" width="{P}" height="{P * 3}" fill="#fff4c2"/>'
                f'<rect x="{(x - 1) * P}" y="{y * P}" width="{P * 3}" height="{P}" fill="#fff4c2"/></g>')
        else:
            stars.append(f'<rect class="{cls}" x="{x * P}" y="{y * P}" width="{P}" height="{P}" fill="#fff4c2"/>')

    cloud = ["..WWW.....", ".WWWWWW...", "WWWWWWWWW.", ".WWWWWWWWW"]
    def cloud_svg(x0, y0, cls):
        parts = []
        for cy, row in enumerate(cloud):
            for cxi, ch in enumerate(row):
                if ch == "W":
                    parts.append(f'<rect x="{(x0 + cxi) * P}" y="{(y0 + cy) * P}" width="{P}" height="{P}" fill="#f3c6b8" opacity=".55"/>')
        return f'<g class="{cls}">' + "".join(parts) + "</g>"

    clouds = cloud_svg(20, 44, "c1") + cloud_svg(180, 40, "c2")

    style = """
    <style>
      .s0{animation:tw 3s steps(2) infinite}
      .s1{animation:tw 4s steps(2) infinite .7s}
      .s2{animation:tw 2.4s steps(2) infinite 1.3s}
      .s3{animation:tw 5s steps(2) infinite 2s}
      @keyframes tw{0%,100%{opacity:1}50%{opacity:.15}}
      .c1{animation:dr 38s steps(60) infinite}
      .c2{animation:dr 52s steps(80) infinite reverse}
      @keyframes dr{0%{transform:translateX(0)}50%{transform:translateX(160px)}100%{transform:translateX(0)}}
    </style>"""
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W * P} {H * P}" width="{W * P}" height="{H * P}" '
           f'shape-rendering="crispEdges">{style}{base}{"".join(stars)}{clouds}</svg>')
    (OUT / "header.svg").write_text(svg)


def build_divider():
    W, H, P = 300, 16, 4
    g = Grid(W, H, P)
    draw_band(g, 0)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W * P} {H * P}" width="{W * P}" height="{H * P}" '
           f'shape-rendering="crispEdges">{g.rects()}</svg>')
    (OUT / "divider.svg").write_text(svg)


def build_footer():
    W, H, P = 300, 50, 4
    g = Grid(W, H, P)
    rng = random.Random(7)
    for y in range(H):
        for x in range(W):
            g.set(x, y, NIGHT if y < 20 else INDIGO)
    for i in range(30):
        g.set(rng.randrange(W), rng.randrange(0, 14), "#6d5a9c")
    far = mountain_heights(W, [(20, 20, 1.0), (60, 16, 0.9), (240, 15, 0.9), (285, 19, 1.0)], 50, rng)
    draw_mountains(g, far, 34, "#3d2358", "#2a1742", WHITE, "#b9c3dc", snowline=21, rng=rng)
    for x in range(W):
        for y in range(30, 34):
            if g.get(x, y) in (NIGHT, INDIGO):
                g.set(x, y, "#2a1742")
    draw_band(g, 34)
    txt = "РАҲМАТ БАРОИ ТАШРИФ!"
    tw = text_width(txt, 1)
    pad = 3
    x0 = (W - tw) // 2
    draw_text(g, txt, x0, 4, 1, GOLD, shadow=DARK_RED)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W * P} {H * P}" width="{W * P}" height="{H * P}" '
           f'shape-rendering="crispEdges">{g.rects()}</svg>')
    (OUT / "footer.svg").write_text(svg)


def build_title(key, text):
    scale = 1
    tw = text_width(text, scale)
    W, H, P = tw + 20, 13, 4
    g = Grid(W, H, P)
    for y in range(H):
        for x in range(W):
            if not ((x in (0, W - 1)) and (y in (0, H - 1))):
                g.set(x, y, NIGHT)
    for x in range(1, W - 1):
        g.set(x, 0, GOLD)
        g.set(x, H - 1, GOLD)
    for y in range(1, H - 1):
        g.set(0, y, GOLD)
        g.set(W - 1, y, GOLD)
    motif = small_motif()
    for sy, row in enumerate(motif):
        for sx, ch in enumerate(row):
            if ch in PAL:
                g.set(2 + sx, 4 + sy, PAL[ch])
                g.set(W - 7 + sx, 4 + sy, PAL[ch])
    draw_text(g, text, 10, 3, scale, GOLD, shadow=DARK_RED)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W * P} {H * P}" width="{W * P}" height="{H * P}" '
           f'shape-rendering="crispEdges">{g.rects()}</svg>')
    (OUT / f"title-{key}.svg").write_text(svg)


if __name__ == "__main__":
    build_header()
    build_divider()
    build_footer()
    for key, text in [("about", "ABOUT ME"), ("stack", "TECH STACK"), ("projects", "PROJECTS"), ("stats", "STATS")]:
        build_title(key, text)
