#!/usr/bin/env python3
"""Render the real GitHub contribution calendar as a pixel-art SVG (enhanced edition).

Public data only. The script talks to the GitHub GraphQL API with the token in
GITHUB_TOKEN, or reads a cached JSON payload with --data for local design work.

Usage:
    GITHUB_TOKEN=... python scripts/build_contributions.py
    python scripts/build_contributions.py --data /tmp/github-data.json
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import pathlib
import urllib.request

DEFAULT_LOGIN = "nicolasmoncada160622-prog"
ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

W, H = 1200, 660
FONT = '"Cascadia Mono", "Consolas", "Courier New", monospace'

INK = "#080C14"
PANEL = "#0B1220"
PANEL_2 = "#0A101C"
BORDER = "#22304A"
BORDER_DIM = "#1B2A44"
CREAM = "#F4E8D0"
WHITE = "#E6EDF3"
MUTED = "#8B98AB"
DIM = "#4F6079"
CYAN = "#00F7FF"
PINK = "#FF3D8B"
YELLOW = "#FFD166"
ORANGE = "#FF9E4A"
GREEN = "#4ADE80"
BLUE = "#70A5FD"
PURPLE = "#7C4DFF"
TEAL = "#00E6A8"

# Contribution heat: empty -> max
CELL_EMPTY = "#111A2B"
CELL_1 = "#1E6E7A"
CELL_2 = "#00A8B8"
CELL_3 = "#FFD166"
CELL_4 = "#FF3D8B"

MONTHS = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
          "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]

PAC_OPEN = [
    "..###..",
    ".#####.",
    "###....",
    "##.....",
    "###....",
    ".#####.",
    "..###..",
]
PAC_CLOSED = [
    "..###..",
    ".#####.",
    "#######",
    "#######",
    "#######",
    ".#####.",
    "..###..",
]

QUERY = """
query($login: String!) {
  user(login: $login) {
    login
    name
    createdAt
    followers { totalCount }
    repositories(privacy: PUBLIC, ownerAffiliations: OWNER) { totalCount }
    contributionsCollection {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
            weekday
          }
        }
      }
    }
  }
}
"""


# ── helpers ──────────────────────────────────────────────────────────────────
def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def rect(x, y, w, h, fill, opacity=None, cls=None, rx=0, stroke=None, stroke_width=1):
    attrs = [f'x="{x:g}"', f'y="{y:g}"', f'width="{w:g}"', f'height="{h:g}"', f'fill="{fill}"']
    if rx:
        attrs.append(f'rx="{rx:g}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    if cls:
        attrs.append(f'class="{cls}"')
    if stroke:
        attrs.append(f'stroke="{stroke}"')
        attrs.append(f'stroke-width="{stroke_width:g}"')
    return f'<rect {" ".join(attrs)}/>'


def text(x, y, content, size=12, fill=WHITE, anchor="start", weight=400, spacing=0, cls=None, opacity=None):
    attrs = [
        f'x="{x:g}"', f'y="{y:g}"', f'font-size="{size:g}"', f'fill="{fill}"',
        f'text-anchor="{anchor}"', f"font-family='{FONT}'",
    ]
    if weight != 400:
        attrs.append(f'font-weight="{weight}"')
    if spacing:
        attrs.append(f'letter-spacing="{spacing:g}"')
    if cls:
        attrs.append(f'class="{cls}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    return f'<text {" ".join(attrs)}>{esc(content)}</text>'


def line(x1, y1, x2, y2, stroke, width=1, opacity=None):
    attrs = [
        f'x1="{x1:g}"', f'y1="{y1:g}"', f'x2="{x2:g}"', f'y2="{y2:g}"',
        f'stroke="{stroke}"', f'stroke-width="{width:g}"',
    ]
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    return f'<line {" ".join(attrs)}/>'


def sprite(rows, x, y, pixel, color):
    out = []
    for ry, row in enumerate(rows):
        for rx, ch in enumerate(row):
            if ch == "#":
                out.append(rect(x + rx * pixel, y + ry * pixel, pixel, pixel, color))
    return "".join(out)


def pacman(x, y, color, pixel=2, closed=False, cls=None):
    rows = PAC_CLOSED if closed else PAC_OPEN
    body = sprite(rows, x, y, pixel, color)
    if cls:
        return f'<g class="{cls}">{body}</g>'
    return body


def tag(x, y, label, color, size=7):
    w = 14 + len(label) * size * 0.82
    return "".join([
        rect(x, y, w, 18, BORDER),
        rect(x + 1, y + 1, w - 2, 16, "#0B1626"),
        rect(x + 1, y + 1, 2, 16, color),
        text(x + 9, y + 12.5, label, size, color, "start", 700, 0.9),
    ])


def plural(n: int, one: str, many: str) -> str:
    return one if n == 1 else many


def fmt_date(day: dt.date, with_year: bool = True) -> str:
    base = f"{day.day:02d} {MONTHS[day.month - 1]}"
    return f"{base} {day.year}" if with_year else base


def fmt_stamp(now_utc: dt.datetime) -> tuple[str, str]:
    local = now_utc - dt.timedelta(hours=5)
    return (
        f"{fmt_date(local.date())} · {local.hour:02d}:{local.minute:02d} COT",
        now_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
    )


# ── data ─────────────────────────────────────────────────────────────────────
def fetch_payload(login: str, token: str) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "nicolas-profile-engine",
        },
    )
    with urllib.request.urlopen(req) as resp:
        payload = json.load(resp)
    if "errors" in payload:
        raise RuntimeError("GitHub GraphQL error: " + json.dumps(payload["errors"], ensure_ascii=False))
    return payload


def parse(payload: dict) -> dict:
    user = payload["data"]["user"]
    collection = user["contributionsCollection"]
    calendar = collection["contributionCalendar"]

    weeks = []
    all_days = []
    for week in calendar["weeks"]:
        slots = {}
        for item in week["contributionDays"]:
            day = dt.date.fromisoformat(item["date"])
            slots[item["weekday"]] = {
                "date": day,
                "count": int(item["contributionCount"]),
            }
            all_days.append((day, int(item["contributionCount"])))
        weeks.append([slots.get(i) for i in range(7)])

    all_days.sort()
    now_utc = dt.datetime.now(dt.timezone.utc)
    local_today = (now_utc - dt.timedelta(hours=5)).date()
    created = dt.date.fromisoformat(user["createdAt"][:10])
    days_on_github = max(1, (local_today - created).days + 1)

    active = [d for d, n in all_days if n > 0]
    active_set = set(active)
    longest = 0
    run = 0
    prev = None
    for day in active:
        if prev is not None and (day - prev).days == 1:
            run += 1
        else:
            run = 1
        longest = max(longest, run)
        prev = day

    cursor = local_today
    if cursor not in active_set:
        cursor -= dt.timedelta(days=1)
    current = 0
    while cursor in active_set:
        current += 1
        cursor -= dt.timedelta(days=1)

    first = active[0] if active else None
    stamp_local, stamp_utc = fmt_stamp(now_utc)

    return {
        "login": user["login"],
        "created": created,
        "days_on_github": days_on_github,
        "today": local_today,
        "weeks": weeks,
        "total": int(calendar["totalContributions"]),
        "active_days": len(active),
        "current_streak": current,
        "longest_streak": longest,
        "first_active": first,
        "commits": int(collection["totalCommitContributions"]),
        "issues": int(collection["totalIssueContributions"]),
        "prs": int(collection["totalPullRequestContributions"]),
        "reviews": int(collection["totalPullRequestReviewContributions"]),
        "restricted": int(collection["restrictedContributionsCount"]),
        "public_repos": int(user["repositories"]["totalCount"]),
        "followers": int(user["followers"]["totalCount"]),
        "updated_local": stamp_local,
        "updated_utc": stamp_utc,
        "total_days": len(all_days),
    }


# ── SVG ──────────────────────────────────────────────────────────────────────
def cell_color(count: int) -> str:
    if count <= 0:
        return CELL_EMPTY
    if count == 1:
        return CELL_1
    if count <= 3:
        return CELL_2
    if count <= 6:
        return CELL_3
    return CELL_4


def build(stats: dict) -> str:
    p: list[str] = []
    today = stats["today"]
    created = stats["created"]
    weeks = stats["weeks"]

    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
             'role="img" aria-labelledby="ctTitle ctDesc" shape-rendering="crispEdges">')
    p.append('<title id="ctTitle">Contribuciones reales de Nicolás Moncada Montaño</title>')
    p.append(f'<desc id="ctDesc">Calendario público de GitHub con {stats["total"]} contribuciones, '
             f'{stats["active_days"]} días activos y una racha actual de {stats["current_streak"]} '
             'días. Se actualiza automáticamente.</desc>')

    p.append("<defs>")
    p.append('<linearGradient id="bgGrad" x1="0" y1="0" x2="1" y2="1">'
             '<stop offset="0" stop-color="#0C1424"/><stop offset="0.55" stop-color="#090D17"/>'
             '<stop offset="1" stop-color="#140C1C"/></linearGradient>')
    p.append('<linearGradient id="neon" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0" stop-color="{CYAN}"/><stop offset="0.5" stop-color="{BLUE}"/>'
             f'<stop offset="1" stop-color="{PINK}"/></linearGradient>')
    p.append('<linearGradient id="cardTop" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0" stop-color="{CYAN}" stop-opacity="0.8"/>'
             f'<stop offset="1" stop-color="{PINK}" stop-opacity="0.35"/></linearGradient>')
    p.append('<pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">'
             '<circle cx="1" cy="1" r="1" fill="#22304A" opacity="0.4"/></pattern>')
    p.append('<pattern id="pre" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
             '<rect width="6" height="6" fill="#0B111C"/><rect width="2" height="6" fill="#141E2E"/></pattern>')
    p.append('<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
             '<rect width="4" height="1" fill="#000000"/></pattern>')
    p.append("<style>")
    p.append("""
      .pulse { animation: pulse 2.2s ease-in-out infinite; }
      .blink { animation: blink 1.1s steps(1,end) infinite; }
      .pac-run { animation: pacrun 17s linear infinite; }
      .chomp { animation: chomp .26s steps(1,end) infinite; }
      @keyframes pulse { 0%,100%{opacity:.35} 50%{opacity:1} }
      @keyframes blink { 0%,49%{opacity:1} 50%,100%{opacity:0} }
      @keyframes pacrun {
        0% { transform: translateX(0); opacity: 1; }
        92% { transform: translateX(830px); opacity: 1; }
        96% { transform: translateX(900px); opacity: 0; }
        100% { transform: translateX(0); opacity: 0; }
      }
      @keyframes chomp { 0%,49%{opacity:1} 50%,100%{opacity:0} }
      @media (prefers-reduced-motion: reduce) {
        .pulse,.blink,.pac-run,.chomp { animation: none !important; }
        .chomp { opacity: 0; }
      }
    """)
    p.append("</style>")
    p.append("</defs>")

    # background
    p.append(rect(0, 0, W, H, "url(#bgGrad)"))
    p.append(rect(0, 0, W, H, "url(#dots)"))
    p.append('<ellipse cx="180" cy="120" rx="300" ry="180" fill="#00F7FF" opacity="0.035"/>')
    p.append('<ellipse cx="1050" cy="560" rx="320" ry="220" fill="#FF3D8B" opacity="0.035"/>')
    p.append(rect(0, 0, W, H, "none", stroke=BORDER, stroke_width=2))
    p.append('<path d="M0 26V0h26M1174 0h26v26M0 634v26h26M1200 634v26h-26" '
             f'fill="none" stroke="{CYAN}" stroke-opacity="0.4" stroke-width="2"/>')

    # top bar
    p.append(rect(0, 0, W, 64, "#080C14", opacity="0.88"))
    p.append(line(0, 64, W, 64, BORDER))
    p.append(line(0, 64, W, 64, "url(#neon)", 1, 0.5))
    p.append(rect(24, 24, 8, 8, YELLOW))
    p.append(rect(38, 24, 8, 8, PINK))
    p.append(rect(52, 24, 8, 8, CYAN))
    p.append(text(78, 38, "CONTRIBUCIONES", 16, CREAM, "start", 700, 3.2))
    p.append(text(78, 53, "DATOS REALES · SIN MÉTRICAS INVENTADAS", 9, MUTED, "start", 400, 1.6))
    p.append(rect(938, 25, 3, 3, GREEN, cls="pulse"))
    p.append(text(950, 34, "EN VIVO", 9, GREEN, "start", 700, 1.4))
    p.append(text(1024, 34, "· " + stats["updated_local"], 8, MUTED, "start", 400, 0.6))
    p.append(text(1168, 50, "ACTUALIZACIÓN AUTOMÁTICA", 8.5, MUTED, "end", 400, 1.2))

    # section label
    p.append(text(32, 88, "CALENDARIO DE ACTIVIDAD", 10, CYAN, "start", 700, 2.4))
    p.append(text(1168, 88, f'{stats["total_days"]} DÍAS · 53 SEMANAS', 8.5, DIM, "end", 400, 1.2))

    # calendar panel
    p.append(rect(32, 96, 1136, 232, PANEL, opacity="0.82"))
    p.append(rect(32, 96, 1136, 232, "none", stroke=BORDER, stroke_width=1))
    p.append(rect(32, 96, 1136, 2, "url(#cardTop)", opacity="0.7"))
    p.append('<path d="M32 120V96h24M1168 120V96h-24M32 304v24h24M1168 304v24h-24" '
             f'fill="none" stroke="{CYAN}" stroke-opacity="0.45" stroke-width="2"/>')

    grid_x = 48
    grid_y = 128
    pitch = 18
    cell = 15
    months_drawn: list[int] = []
    for wi, week in enumerate(weeks):
        first_day = next((slot["date"] for slot in week if slot), None)
        if first_day and (not months_drawn or months_drawn[-1] != first_day.month):
            months_drawn.append(first_day.month)
            p.append(text(grid_x + wi * pitch, 117, MONTHS[first_day.month - 1], 8, MUTED, "start", 400, 0.6))
        for di, slot in enumerate(week):
            x = grid_x + wi * pitch
            y = grid_y + di * pitch
            if slot is None:
                p.append(rect(x, y, cell, cell, "#0C1320", opacity="0.35"))
                continue
            day = slot["date"]
            count = slot["count"]
            if day < created:
                p.append(rect(x, y, cell, cell, "url(#pre)", opacity="0.55"))
                continue
            color = cell_color(count)
            if count > 0:
                p.append(f'<g><title>{esc(fmt_date(day))} · {count} {plural(count, "contribución", "contribuciones")}</title>')
                p.append(rect(x, y, cell, cell, color))
                p.append(rect(x, y, cell, 1, "#FFFFFF", opacity="0.2"))
                p.append(rect(x, y, 1, cell, "#FFFFFF", opacity="0.1"))
                p.append("</g>")
            else:
                p.append(rect(x, y, cell, cell, CELL_EMPTY))
            if day == today:
                p.append(rect(x - 2, y - 2, cell + 4, cell + 4, "none", stroke=CYAN, stroke_width=1))

    # the long stretch before the account existed is shown as a deliberate prologue
    p.append(text(grid_x + 20 * pitch, 196, "ANTES DE MI CUENTA", 9, "#2A405C", "middle", 700, 3.2, opacity="0.75"))

    # weekday labels
    for di, label in ((1, "LUN"), (3, "MIÉ"), (5, "VIE")):
        p.append(text(36, grid_y + di * pitch + 10, label, 7.5, DIM, "end", 700, 0.5))

    # legend (right)
    lx = 1024
    p.append(text(lx, 136, "ACTIVIDAD", 9, CYAN, "start", 700, 1.8))
    legend = [("NADA", CELL_EMPTY), ("POCO", CELL_1), ("MEDIO", CELL_2), ("ALTO", CELL_3), ("MÁX", CELL_4)]
    ly = 156
    for label, color in legend:
        p.append(rect(lx, ly - 9, 10, 10, color))
        p.append(text(lx + 18, ly, label, 8, MUTED, "start", 400, 0.9))
        ly += 20
    p.append(rect(lx, 253, 10, 10, "none", stroke=CYAN, stroke_width=1))
    p.append(text(lx + 18, 262, "HOY", 8, CYAN, "start", 700, 0.9))

    # calendar footnote
    p.append(line(40, 300, 1160, 300, BORDER_DIM, 1, 0.8))
    note = f'CUENTA CREADA EL {fmt_date(created)} · LOS DÍAS ANTERIORES SE MUESTRAN ATENUADOS'
    if stats["first_active"]:
        note += f' · PRIMER PIXEL: {fmt_date(stats["first_active"], False)}'
    p.append(text(40, 318, note, 8, DIM, "start", 400, 0.8))

    # stat cards
    cards = [
        ("CONTRIBUCIONES", f'{stats["total"]:02d}', "EN LOS ÚLTIMOS 12 MESES", CYAN),
        ("DÍAS ACTIVOS", f'{stats["active_days"]:02d}', f'DE {stats["days_on_github"]} DÍAS EN GITHUB', GREEN),
        ("RACHA ACTUAL", f'{stats["current_streak"]:02d}',
         f'MEJOR: {stats["longest_streak"]:02d} {plural(stats["longest_streak"], "DÍA", "DÍAS")}', PINK),
        ("COMMITS", f'{stats["commits"]:02d}', f'PR {stats["prs"]:02d} · ISSUES {stats["issues"]:02d}', YELLOW),
    ]
    cx = 32
    for label, value, sub, color in cards:
        p.append(rect(cx, 344, 264, 108, PANEL, opacity="0.78"))
        p.append(rect(cx, 344, 264, 108, "none", stroke=BORDER, stroke_width=1))
        p.append(rect(cx, 344, 264, 2, color, opacity="0.7"))
        p.append(text(cx + 18, 368, label, 9, MUTED, "start", 700, 1.8))
        p.append(rect(cx + 246, 360, 3, 3, color, cls="pulse"))
        p.append(text(cx + 18, 410, value, 36, color, "start", 700, 1.0))
        p.append(text(cx + 18, 433, sub, 8.5, MUTED, "start", 400, 0.5))
        cx += 280

    # mission panel
    p.append(rect(32, 468, 720, 136, PANEL, opacity="0.78"))
    p.append(rect(32, 468, 720, 136, "none", stroke=BORDER, stroke_width=1))
    p.append(rect(32, 468, 720, 2, "url(#cardTop)", opacity="0.6"))
    p.append(text(50, 492, "MISIÓN ACTUAL", 9, CYAN, "start", 700, 2.2))
    p.append(tag(678, 476, "EN CURSO", GREEN, 8))
    p.append(text(50, 522, "Convertir lo que aprendo en proyectos reales,", 15, CREAM, "start", 600, 0.4))
    p.append(text(50, 544, "escalables y bien documentados.", 15, CREAM, "start", 600, 0.4))
    chips = [("APRENDER", CYAN), ("CONSTRUIR", YELLOW), ("DOCUMENTAR", PINK)]
    chx = 50
    for label, color in chips:
        w = 16 + len(label) * 9 * 0.82
        p.append(rect(chx, 564, w, 22, "#0B1626"))
        p.append(rect(chx, 564, 3, 22, color))
        p.append(text(chx + 11, 579, label, 9, color, "start", 700, 0.9))
        chx += w + 10
    # mission flag
    p.append(rect(664, 520, 2, 34, CREAM, opacity="0.85"))
    p.append(rect(666, 520, 22, 12, PINK))
    p.append(rect(666, 520, 22, 2, "#FF9EC4", opacity="0.8"))
    p.append(rect(666, 532, 22, 1, "#B0235F"))
    p.append(rect(660, 552, 10, 2, BORDER))
    p.append(text(676, 570, "META", 7, DIM, "middle", 700, 1.2))

    # activity panel
    p.append(rect(768, 468, 400, 136, PANEL, opacity="0.78"))
    p.append(rect(768, 468, 400, 136, "none", stroke=BORDER, stroke_width=1))
    p.append(rect(768, 468, 400, 2, "url(#cardTop)", opacity="0.6"))
    p.append(text(786, 492, "ACTIVIDAD DETALLADA", 9, CYAN, "start", 700, 2.0))
    rows = [
        ("COMMITS", stats["commits"], YELLOW),
        ("PULL REQUESTS", stats["prs"], PINK),
        ("ISSUES", stats["issues"], BLUE),
        ("REVISIONES", stats["reviews"], GREEN),
        ("REPOS PÚBLICOS", stats["public_repos"], CYAN),
    ]
    ry = 512
    for label, value, color in rows:
        p.append(rect(786, ry - 6, 3, 3, color))
        p.append(text(796, ry, label, 8.5, MUTED, "start", 400, 1.0))
        p.append(text(1150, ry, f"{value:02d}", 9.5, CREAM if value else DIM, "end", 700, 1.0))
        ry += 17

    # footer
    p.append(line(32, 618, 1168, 618, BORDER_DIM))
    p.append(rect(32, 630, 3, 3, GREEN, cls="pulse"))
    p.append(text(42, 638, "DATOS PÚBLICOS DE GITHUB · SE ACTUALIZA AUTOMÁTICAMENTE CADA 8 HORAS", 8, MUTED, "start", 400, 0.8))
    p.append(text(1168, 638, "NICOLÁS.OS · CONTRIBUCIONES", 8, PINK, "end", 700, 0.8))

    # CRT scan + inner border
    p.append(rect(0, 0, W, H, "url(#scan)", opacity="0.08"))
    p.append(rect(1, 1, W - 2, H - 2, "none", stroke="#2A3A54", stroke_width=1, opacity="0.5"))
    p.append("</svg>")
    return "\n".join(p)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", help="Cached GraphQL JSON (local preview)")
    parser.add_argument("--out", default=str(ASSETS / "contributions.svg"))
    parser.add_argument("--json", default=str(ASSETS / "contributions.json"))
    parser.add_argument("--login", default=os.environ.get("PROFILE_USER", DEFAULT_LOGIN))
    args = parser.parse_args()

    if args.data:
        payload = json.loads(pathlib.Path(args.data).read_text(encoding="utf-8"))
    else:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if not token:
            raise SystemExit("GITHUB_TOKEN is required (or pass --data for local preview)")
        payload = fetch_payload(args.login, token)

    stats = parse(payload)
    svg = build(stats)
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding="utf-8")

    public = {
        "login": stats["login"],
        "total_contributions": stats["total"],
        "active_days": stats["active_days"],
        "current_streak": stats["current_streak"],
        "longest_streak": stats["longest_streak"],
        "commits": stats["commits"],
        "pull_requests": stats["prs"],
        "issues": stats["issues"],
        "reviews": stats["reviews"],
        "public_repos": stats["public_repos"],
        "followers": stats["followers"],
        "days_on_github": stats["days_on_github"],
        "account_created": stats["created"].isoformat(),
        "updated_local": stats["updated_local"],
        "updated_utc": stats["updated_utc"],
        "engine": "profile-engine",
    }
    pathlib.Path(args.json).write_text(json.dumps(public, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size:,} bytes)")
    print(f"wrote {args.json}")
    print(f'data: {stats["total"]} contributions · {stats["active_days"]} active days · '
          f'streak {stats["current_streak"]} · commits {stats["commits"]}')


if __name__ == "__main__":
    main()

