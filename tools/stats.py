import datetime
import json
import os
import pathlib
import sys
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from generate import (DARK_GREEN, DARK_RED, FONT, GOLD, GREEN, INDIGO, NIGHT, OUT, PAL, RED,
                      TURQUOISE, WHITE, Grid, draw_text, small_motif, text_width)

USER = os.environ.get("GH_USER", "GostWarrir186")
TOKEN = os.environ["GITHUB_TOKEN"]
P = 4

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    contributionsCollection {
      totalCommitContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date } }
      }
    }
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, first: 100, isFork: false) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}
"""


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(data["errors"])
    return data["data"]["user"]


def streaks(days):
    today = datetime.date.today().isoformat()
    counts = [d["contributionCount"] for d in days if d["date"] <= today]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    current = 0
    i = len(counts) - 1
    if i >= 0 and counts[i] == 0:
        i -= 1
    while i >= 0 and counts[i]:
        current += 1
        i -= 1
    return current, longest


def safe(text):
    return "".join(c for c in text.upper() if c in FONT)


def frame(g):
    for y in range(g.h):
        for x in range(g.w):
            g.set(x, y, NIGHT)
    for x in range(g.w):
        for y in (0, g.h - 1):
            g.set(x, y, GOLD)
        for y in (1, g.h - 2):
            if x % 4 in (0, 1, 2):
                g.set(x, y, RED if y == 1 else GREEN)
    for y in range(g.h):
        g.set(0, y, GOLD)
        g.set(g.w - 1, y, GOLD)
    m = small_motif()
    for cx, cy in ((3, 4), (g.w - 8, 4), (3, g.h - 9), (g.w - 8, g.h - 9)):
        for sy, row in enumerate(m):
            for sx, ch in enumerate(row):
                if ch in PAL:
                    g.set(cx + sx, cy + sy, PAL[ch])


def title(g, text, x, y):
    draw_text(g, text, x, y, 1, GOLD, shadow=DARK_RED)


ICONS = {
    "star": ["...Y...", "..YYY..", "YYYYYYY", ".YYYYY.", "..YYY..", ".YY.YY.", "YY...YY"],
    "commit": ["...R...", "...R...", "..RRR..", ".RR.RR.", "..RRR..", "...R...", "...R..."],
    "repo": ["GGGGGG.", "G....G.", "G.WW.G.", "G....G.", "G.WW.G.", "GGGGGG.", ".G..G.."],
    "fire": ["...R...", "..RR...", "..RRR.R", ".RRYRRR", "RRYYYRR", "RRYYYRR", ".RRRRR."],
    "trophy": ["YYYYYYY", "YYYYYYY", ".YYYYY.", "..YYY..", "...Y...", "..YYY..", ".YYYYY."],
    "grid": ["G.G.G.G", ".......", "G.R.G.R", ".......", "Y.G.R.G", ".......", "G.Y.G.G"],
    "people": [".W...W.", "WWW.WWW", ".W...W.", ".......", "WWW.WWW", "WWW.WWW", "WWW.WWW"],
}


def icon(g, name, x, y):
    for iy, row in enumerate(ICONS[name]):
        for ix, ch in enumerate(row):
            if ch in PAL:
                g.set(x + ix, y + iy, PAL[ch])


def build_stats(u):
    cal = u["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    current, longest = streaks(days)
    repos = u["repositories"]["nodes"]
    stars = sum(r["stargazerCount"] for r in repos)

    langs = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:5]

    W, H = 300, 88
    g = Grid(W, H, P)
    frame(g)

    title(g, "GITHUB STATS", 14, 6)
    rows = [
        ("grid", "CONTRIBUTIONS", cal["totalContributions"]),
        ("commit", "COMMITS", u["contributionsCollection"]["totalCommitContributions"]),
        ("repo", "PUBLIC REPOS", u["repositories"]["totalCount"]),
        ("star", "STARS", stars),
        ("fire", "CURRENT STREAK", current),
        ("trophy", "LONGEST STREAK", longest),
    ]
    for i, (ic, label, val) in enumerate(rows):
        y = 19 + i * 11
        icon(g, ic, 14, y)
        draw_text(g, label, 25, y, 1, WHITE)
        v = str(val)
        draw_text(g, v, 140 - text_width(v, 1), y, 1, GOLD)
        if i < len(rows) - 1:
            for x in range(25, 141, 2):
                g.set(x, y + 9, "#2e2255")

    for y in range(6, H - 6):
        g.set(150, y, GOLD if y % 3 else RED)

    title(g, "TOP LANGUAGES", 160, 6)
    bar_colors = [RED, GOLD, GREEN, TURQUOISE, WHITE]
    for i, (name, size) in enumerate(top):
        y = 18 + i * 13
        pct = size * 100 / total
        n = safe(name)[:14]
        draw_text(g, n, 160, y, 1, WHITE)
        ps = f"{pct:.1f}%"
        draw_text(g, ps, 287 - text_width(ps, 1), y, 1, GOLD)
        bx, bw = 160, 127
        for x in range(bx, bx + bw):
            g.set(x, y + 9, "#2e2255")
            g.set(x, y + 10, "#2e2255")
        fill = max(1, round(bw * pct / 100))
        c = bar_colors[i % len(bar_colors)]
        for x in range(bx, bx + fill):
            g.set(x, y + 9, c)
            g.set(x, y + 10, c if (x - bx) % 6 != 5 else NIGHT)

    (OUT / "stats.svg").write_text(svg(g))


def build_calendar(u):
    cal = u["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    levels = ["#2a1f4a", DARK_GREEN, GREEN, RED, GOLD]
    mx = max((d["contributionCount"] for w in weeks for d in w["contributionDays"]), default=0) or 1

    def level(c):
        if c == 0:
            return 0
        return min(4, 1 + int(3 * c / mx + 0.5)) if mx > 1 else 4

    cell, gap = 4, 1
    W = 300
    grid_w = len(weeks) * (cell + gap) - gap
    x0 = (W - grid_w) // 2
    H = 20 + 7 * (cell + gap) + 16
    g = Grid(W, H, P)
    frame(g)
    t = f"{cal['totalContributions']} CONTRIBUTIONS IN THE LAST YEAR"
    title(g, t, (W - text_width(t, 1)) // 2, 6)

    today = datetime.date.today().isoformat()
    cells = {}
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            if d["date"] > today:
                continue
            wd = datetime.date.fromisoformat(d["date"]).isoweekday() % 7
            cells[(wi, wd)] = level(d["contributionCount"])
            x, y = x0 + wi * (cell + gap), 18 + wd * (cell + gap)
            for dy in range(cell):
                for dx in range(cell):
                    corner = dx in (0, cell - 1) and dy in (0, cell - 1)
                    if not corner:
                        g.set(x + dx, y + dy, levels[0])

    ly = 18 + 7 * (cell + gap) + 3
    lx = W - 22 - (5 * (cell + gap)) - text_width("LESS", 1) - text_width("MORE", 1) - 4
    draw_text(g, "LESS", lx, ly, 1, WHITE)
    lx += text_width("LESS", 1) + 2
    for c in levels:
        for dy in range(cell):
            for dx in range(cell):
                g.set(lx + dx, ly + 1 + dy, c)
        lx += cell + gap
    draw_text(g, "MORE", lx + 1, ly, 1, WHITE)

    extra = snake_layer(cells, levels, x0, cell, gap, len(weeks))
    (OUT / "calendar.svg").write_text(svg(g, extra))


def cell_path(x, y, cell):
    u = P
    return (f"M{(x + 1) * u} {y * u}h{(cell - 2) * u}v{u}h{u}v{(cell - 2) * u}h-{u}v{u}"
            f"h-{(cell - 2) * u}v-{u}h-{u}v-{(cell - 2) * u}h{u}z")


def snake_layer(cells, levels, x0, cell, gap, nweeks):
    step = cell + gap
    tail = 7
    path = [(-i, 0) for i in range(tail, 0, -1)]
    for wi in range(nweeks):
        days = range(7) if wi % 2 == 0 else range(6, -1, -1)
        path += [(wi, d) for d in days]
    last = path[-1]
    path += [(last[0] + i, last[1]) for i in range(1, tail + 2)]
    pause = 25
    n = len(path) + pause
    dur = round(n * 0.07, 2)

    def pos(p):
        return ((x0 + p[0] * step) * P, (18 + p[1] * step) * P)

    frames = []
    for i, p in enumerate(path):
        x, y = pos(p)
        frames.append(f"{i * 100 / n:.3f}%{{transform:translate({x}px,{y}px)}}")
    x, y = pos(path[-1])
    frames.append(f"{len(path) * 100 / n:.3f}%,100%{{transform:translate({x}px,{y}px)}}")
    css = [f"@keyframes mv{{{''.join(frames)}}}",
           f".sn{{animation:mv {dur}s steps(1,end) infinite;opacity:0}}",
           "@keyframes on{0%,100%{opacity:1}}"]

    index = {p: i for i, p in enumerate(path)}
    food = []
    for (wi, wd), lv in cells.items():
        if lv == 0:
            continue
        t = index[(wi, wd)] * 100 / n
        css.append(f"@keyframes f{wi}_{wd}{{0%,{t:.3f}%{{opacity:1}}{t + 0.01:.3f}%,99.9%{{opacity:0}}100%{{opacity:1}}}}")
        food.append(f'<path class="f{wi}_{wd}" style="animation:f{wi}_{wd} {dur}s steps(1,end) infinite" '
                    f'fill="{levels[lv]}" d="{cell_path(x0 + wi * step, 18 + wd * step, cell)}"/>')

    body = [GOLD, RED, RED, WHITE, WHITE, GREEN, GREEN, DARK_GREEN]
    seg_delay = dur / n
    segs = []
    for k in reversed(range(len(body))):
        shape = f'<path fill="{body[k]}" d="{cell_path(0, 0, cell)}"/>'
        if k == 0:
            cap = [
                "..KKKK..",
                ".KKWWKK.",
                "KWKKKKWK",
                "KKWKKWKK",
                "RWRWRWRW",
            ]
            colors = {"K": "#111111", "W": WHITE, "R": RED}
            hat = "".join(
                f'<rect x="{(cx - 2) * P}" y="{(cy - 5) * P}" width="{P}" height="{P}" fill="{colors[ch]}"/>'
                for cy, row in enumerate(cap) for cx, ch in enumerate(row) if ch in colors)
            shape = (f'<path fill="{GOLD}" d="M0 0h{cell * P}v{cell * P}h-{cell * P}z"/>'
                     f'<rect x="{P}" y="{P}" width="{P}" height="{P}" fill="{NIGHT}"/>'
                     f'<rect x="{2 * P}" y="{P}" width="{P}" height="{P}" fill="{NIGHT}"/>' + hat)
        segs.append(f'<g class="sn" style="animation-delay:-{(n - k) * seg_delay:.3f}s;'
                    f'animation-name:mv;opacity:1">{shape}</g>')
    style = "<style>" + "".join(css) + "</style>"
    clip = (f'<clipPath id="in"><rect x="{2 * P}" y="{3 * P}" width="{(300 - 4) * P}" '
            f'height="{(18 + 7 * step + 2) * P}"/></clipPath>')
    return style + clip + "".join(food) + '<g clip-path="url(#in)">' + "".join(segs) + "</g>"


def svg(g, extra=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {g.w * P} {g.h * P}" '
            f'width="{g.w * P}" height="{g.h * P}" shape-rendering="crispEdges">{g.rects()}{extra}</svg>')


if __name__ == "__main__":
    u = fetch()
    build_stats(u)
    build_calendar(u)
