#!/usr/bin/env python3
"""Build a pixel-art player card with Nicolás' profile attributes (enhanced edition)."""
from __future__ import annotations

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "player-card.svg"
W, H = 1200, 650
FONT = '"Cascadia Mono", "Consolas", "Courier New", monospace'

INK = "#080C14"
PANEL = "#0B1220"
PANEL2 = "#0E1728"
CREAM = "#F4E8D0"
WHITE = "#E6EDF3"
MUTED = "#7D8CA3"
DIM = "#43536B"
CYAN = "#00F7FF"
PINK = "#FF3D8B"
YELLOW = "#FFD166"
BLUE = "#70A5FD"
GREEN = "#4ADE80"
PURPLE = "#7C4DFF"
ORANGE = "#FF9E4A"
TEAL = "#00E6A8"
BORDER = "#22304A"


def rect(x, y, w, h, fill, rx=0, opacity=None, cls=None):
    a = [f'x="{x:g}"', f'y="{y:g}"', f'width="{w:g}"', f'height="{h:g}"', f'fill="{fill}"']
    if rx:
        a.append(f'rx="{rx:g}"')
    if opacity is not None:
        a.append(f'opacity="{opacity}"')
    if cls:
        a.append(f'class="{cls}"')
    return f'<rect {" ".join(a)}/>'


def text(x, y, s, size=12, fill=WHITE, anchor="start", weight=400, spacing=0, cls=None, opacity=None):
    a = [f'x="{x:g}"', f'y="{y:g}"', f'font-size="{size:g}"', f'fill="{fill}"',
         f'text-anchor="{anchor}"', f'font-family=\'{FONT}\'']
    if weight != 400:
        a.append(f'font-weight="{weight}"')
    if spacing:
        a.append(f'letter-spacing="{spacing:g}"')
    if cls:
        a.append(f'class="{cls}"')
    if opacity is not None:
        a.append(f'opacity="{opacity}"')
    return f'<text {" ".join(a)}>{s}</text>'


def line(x1, y1, x2, y2, stroke, width=1, opacity=None):
    a = [f'x1="{x1:g}"', f'y1="{y1:g}"', f'x2="{x2:g}"', f'y2="{y2:g}"',
         f'stroke="{stroke}"', f'stroke-width="{width:g}"']
    if opacity is not None:
        a.append(f'opacity="{opacity}"')
    return f'<line {" ".join(a)}/>'


def sprite(rows, x, y, pixel, color):
    out = []
    for ry, row in enumerate(rows):
        for rx, ch in enumerate(row):
            if ch == "#":
                out.append(rect(x + rx * pixel, y + ry * pixel, pixel, pixel, color))
    return "".join(out)


def tag(x_right, y, label, color, size=9.0):
    """Small qualitative status tag, right-aligned, with a pixel border."""
    w = 18 + len(label) * size * 0.82
    x = x_right - w
    out = [rect(x, y, w, 20, BORDER), rect(x + 1, y + 1, w - 2, 18, "#0B1626")]
    out.append(rect(x + 1, y + 1, 2, 18, color))
    out.append(text(x + 9, y + 14, label, size, color, "start", 700, 0.7))
    return "".join(out)


def barcode(x, y, width=84, height=22):
    out = []
    pattern = [2, 1, 3, 1, 2, 4, 1, 2, 1, 3, 2, 1, 4, 1, 2, 3, 1, 2, 4, 1, 2, 1]
    cx = x
    for i, w in enumerate(pattern):
        if cx + w > x + width:
            break
        if i % 2 == 0:
            out.append(rect(cx, y, w, height, CREAM, opacity="0.8"))
        cx += w + 1
    return "".join(out)


# ── portrait sprite (32x40 grid) ──────────────────────────────────────────────
GW, GH = 32, 40
grid = [["." for _ in range(GW)] for _ in range(GH)]


def span(y, x0, x1, ch):
    for x in range(x0, x1 + 1):
        if 0 <= x < GW and 0 <= y < GH:
            grid[y][x] = ch


def fill(x0, y0, x1, y1, ch):
    for y in range(y0, y1 + 1):
        span(y, x0, x1, ch)


# shoulders / hoodie
for y, (a, b) in {
    27: (12, 19), 28: (9, 22), 29: (7, 24), 30: (5, 26),
    31: (4, 27), 32: (3, 28), 33: (2, 29), 34: (2, 29),
    35: (2, 29), 36: (2, 29), 37: (2, 29), 38: (2, 29), 39: (2, 29),
}.items():
    span(y, a, b, "J")
# hoodie shading
fill(2, 30, 4, 39, "j")
fill(27, 30, 29, 39, "k")
fill(13, 28, 18, 30, "k")
fill(12, 28, 19, 28, "j")
# hood rim
fill(11, 27, 20, 27, "j")
# drawstrings
fill(13, 29, 13, 34, "W")
fill(18, 29, 18, 34, "W")
fill(13, 34, 13, 35, "Y")
fill(18, 34, 18, 35, "Y")
# pin (small pac-man on the chest)
fill(21, 32, 23, 34, "Y")
grid[32][24] = "Y"
grid[34][22] = "."
grid[33][22] = "."

# neck
fill(13, 24, 18, 27, "S")
fill(16, 24, 18, 27, "s")
fill(13, 24, 18, 24, "s")

# face
face = {
    8: (9, 22), 9: (8, 23), 10: (8, 23), 11: (8, 23), 12: (8, 23),
    13: (8, 23), 14: (8, 23), 15: (9, 22), 16: (9, 22), 17: (9, 22),
    18: (10, 21), 19: (10, 21), 20: (11, 20), 21: (12, 19), 22: (13, 18), 23: (14, 17),
}
for y, (a, b) in face.items():
    span(y, a, b, "S")
# side shading
for y in range(10, 19):
    grid[y][face[y][1]] = "s"
# ears
fill(7, 13, 7, 16, "S")
fill(24, 13, 24, 16, "S")
# hair top
hair = {
    2: (11, 20), 3: (9, 22), 4: (8, 23), 5: (7, 24), 6: (6, 25),
    7: (6, 25), 8: (5, 26),
}
for y, (a, b) in hair.items():
    span(y, a, b, "H")
fill(5, 9, 7, 14, "H")
fill(24, 9, 26, 14, "H")
fill(5, 15, 6, 16, "H")
fill(25, 15, 26, 16, "H")
# hair highlights
span(3, 12, 15, "h")
span(4, 10, 12, "h")
fill(6, 9, 7, 10, "h")
# eyebrows
fill(11, 11, 14, 11, "H")
fill(17, 11, 20, 11, "H")
# eyes
fill(11, 13, 13, 14, "W")
fill(18, 13, 20, 14, "W")
grid[13][12] = "E"
grid[14][12] = "E"
grid[13][19] = "E"
grid[14][19] = "E"
grid[13][11] = "K"
grid[13][20] = "K"
# nose
fill(15, 16, 16, 17, "s")
grid[16][15] = "d"
# mouth
fill(13, 19, 18, 19, "M")
grid[18][12] = "M"
grid[18][19] = "M"
# cheek shadow
fill(9, 17, 10, 18, "s")
fill(21, 17, 22, 18, "s")
# jaw shadow
fill(12, 22, 19, 23, "s")
# headphones band
span(2, 10, 21, "P")
span(3, 8, 9, "P")
span(3, 22, 23, "P")
span(4, 6, 7, "P")
span(4, 24, 25, "P")
span(5, 5, 5, "P")
span(5, 26, 26, "P")
# cups
fill(2, 12, 5, 18, "P")
fill(26, 12, 29, 18, "P")
fill(2, 12, 2, 18, "p")
fill(5, 12, 5, 18, "K")
fill(26, 12, 26, 18, "K")
fill(29, 12, 29, 18, "p")
fill(3, 14, 4, 15, "E")
fill(27, 14, 28, 15, "E")
grid[12][3] = "p"
grid[12][28] = "p"
# cyan LED on left cup
grid[13][3] = "C"
# rim lights
for y in range(3, 19):
    xs = [x for x in range(GW) if grid[y][x] != "."]
    if xs:
        grid[y][xs[0]] = "C"
        grid[y][xs[-1]] = "p"
# dark outline around shoulders top
for y in (27, 28, 29, 30, 31):
    xs = [x for x in range(GW) if grid[y][x] != "."]
    if xs:
        grid[y][xs[0]] = "K"
        grid[y][xs[-1]] = "K"

COLORS = {
    ".": None, "K": "#080C14", "H": "#24160F", "h": "#3A2418",
    "S": "#E8B08A", "s": "#C98A66", "d": "#A96A4A", "E": "#16110E",
    "W": "#F4E8D0", "M": "#8A4A3A", "C": "#6EE7F2", "p": "#FF9EC4",
    "P": "#FF3D8B", "J": "#2B3A67", "j": "#3E4F82", "k": "#1E2A4A",
    "Y": "#FFD166",
}

PIX = 8


def portrait_svg(x0, y0):
    out = [f'<g transform="translate({x0},{y0})" shape-rendering="crispEdges">']
    for y in range(GH):
        run_ch = None
        run_start = 0
        for x in range(GW + 1):
            ch = grid[y][x] if x < GW else None
            if ch != run_ch:
                if run_ch not in (None, "."):
                    color = COLORS[run_ch]
                    out.append(rect(run_start * PIX, y * PIX, (x - run_start) * PIX, PIX, color))
                run_ch = ch
                run_start = x
    out.append("</g>")
    return "".join(out)


# ── pixel icons (10x10) ──────────────────────────────────────────────────────
ICONS = {
    "ai": [
        "..######..",
        "..#....#..",
        "###.##.###",
        "..#.##.#..",
        "..#.##.#..",
        "###.##.###",
        "..#....#..",
        "..######..",
        "..........",
        "..........",
        "..........",
    ],
    "flow": [
        "..##......",
        ".#..#.....",
        ".#..#.....",
        "..##......",
        "....##....",
        "...####...",
        "....##....",
        "..........",
        "..........",
        "..........",
    ],
    "shield": [
        "..######..",
        ".#......#.",
        "#........#",
        "#.####...#",
        "#.#..#...#",
        "#.####...#",
        ".#.....#..",
        "..#...#...",
        "...###....",
        "....#.....",
    ],
    "design": [
        "..#####...",
        ".#.....#..",
        "#..###..#.",
        "#.#...#.#.",
        "#..###..#.",
        ".#.....#..",
        "..#####...",
        "....#.....",
        "...#......",
        "..#.......",
    ],
    "code": [
        "..#....#..",
        ".#.....#..",
        "#.......#.",
        "#.......#.",
        "#.......#.",
        ".#.....#..",
        "..#...#...",
        "...#.#....",
        "....#.....",
        "..........",
    ],
    "rocket": [
        "....##....",
        "...####...",
        "...####...",
        "..#.##.#..",
        "..#.##.#..",
        ".#..##..#.",
        ".#......#.",
        "..######..",
        "...####...",
        "....##....",
    ],
    "gamepad": [
        "..####..####..",
        ".#....##....#.",
        "#............#",
        "#..##....##..#",
        "#............#",
        ".#..........#.",
        "..##......##..",
        "..............",
        "..............",
        "..............",
    ],
    "music": [
        "....####..",
        "....#..#..",
        "....#..#..",
        "....#..#..",
        "....#..#..",
        ".####..#..",
        "#####.....",
        ".###......",
        "..........",
        "..........",
    ],
}


def icon(name, x, y, color, px=2):
    rows = ICONS[name]
    out = []
    for ry, row in enumerate(rows):
        for rx, ch in enumerate(row):
            if ch == "#":
                out.append(rect(x + rx * px, y + ry * px, px, px, color))
    return "".join(out)


def meter(x, y, filled, color, total=5, bw=14, bh=7, gap=4):
    out = []
    for i in range(total):
        c = color if i < filled else "#1A2436"
        out.append(rect(x + i * (bw + gap), y, bw, bh, c))
    return "".join(out)


def build():
    p: list[str] = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
             'role="img" aria-labelledby="pcTitle pcDesc" shape-rendering="crispEdges">')
    p.append('<title id="pcTitle">Ficha de jugador de Nicolás Moncada Montaño</title>')
    p.append('<desc id="pcDesc">Ficha pixel art con los atributos de Nicolás: 20 años, Bogotá, tercer semestre de Ingeniería de Sistemas en UNIMINUTO; nivel intermedio de IA; vibe coding para mejorar su flujo de desarrollo; interés en ciberseguridad; diseño y creatividad; programación y resolución de problemas; proyectos básicos con enfoque escalable; videojuegos y música. Lenguajes en práctica: Python, JavaScript, HTML/CSS y SQL.</desc>')
    p.append("<defs>")
    p.append('<linearGradient id="pcBg" x1="0" y1="0" x2="1" y2="1">'
             '<stop offset="0" stop-color="#0C1424"/><stop offset="0.55" stop-color="#090D17"/>'
             '<stop offset="1" stop-color="#120C1A"/></linearGradient>')
    p.append('<linearGradient id="pcNeon" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0" stop-color="{CYAN}"/><stop offset="0.5" stop-color="{BLUE}"/>'
             f'<stop offset="1" stop-color="{PINK}"/></linearGradient>')
    p.append('<radialGradient id="pcHalo" cx="0.5" cy="0.5" r="0.5">'
             f'<stop offset="0" stop-color="{CYAN}" stop-opacity="0.16"/>'
             '<stop offset="1" stop-color="#00F7FF" stop-opacity="0"/></radialGradient>')
    p.append('<pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">'
             '<circle cx="1" cy="1" r="1" fill="#22304A" opacity="0.45"/></pattern>')
    p.append('<style>')
    p.append('''
      text { paint-order: stroke fill; }
      .blink { animation: blink 1.1s steps(1,end) infinite; }
      .pulse { animation: pulse 2s ease-in-out infinite; }
      .scan { animation: scan 5s linear infinite; }
      .portrait { animation: float 6s ease-in-out infinite; }
      @keyframes blink { 0%,49%{opacity:1} 50%,100%{opacity:0} }
      @keyframes pulse { 0%,100%{opacity:.35} 50%{opacity:1} }
      @keyframes scan { 0%{transform:translateY(0);opacity:0} 10%{opacity:.35} 90%{opacity:.35} 100%{transform:translateY(320px);opacity:0} }
      @keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-6px)} }
      @media (prefers-reduced-motion: reduce) { .blink,.pulse,.scan,.portrait { animation:none !important; } }
    ''')
    p.append('</style>')
    p.append('</defs>')

    # background
    p.append(rect(0, 0, W, H, "url(#pcBg)"))
    p.append(rect(0, 0, W, H, "url(#dots)"))
    p.append('<ellipse cx="210" cy="230" rx="300" ry="260" fill="url(#pcHalo)"/>')
    p.append(rect(0, 0, W, H, "none", rx=0))
    p.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" fill="none" stroke="{BORDER}" stroke-width="1"/>')
    # corner brackets
    p.append('<path d="M0 26V0h26M1174 0h26v26M0 624v26h26M1200 624v26h-26" fill="none" stroke="#00F7FF" stroke-opacity="0.35" stroke-width="2"/>')

    # top bar
    p.append(rect(0, 0, W, 64, "#080C14", opacity="0.85"))
    p.append(line(0, 64, W, 64, BORDER))
    p.append(text(32, 30, "FICHA DE JUGADOR", 15, CREAM, "start", 700, 2.4))
    p.append(text(32, 48, "ARCHIVO DE PERFIL  ·  NICOLÁS.OS", 9, MUTED, "start", 400, 1.8))
    p.append(rect(540, 22, 8, 8, YELLOW))
    p.append(rect(552, 22, 8, 8, PINK))
    p.append(rect(564, 22, 8, 8, CYAN))
    p.append(text(596, 32, "PLAYER 1", 9, CYAN, "start", 700, 2.2))
    p.append(text(596, 48, "PARTIDA GUARDADA", 9, MUTED, "start", 400, 1.2))
    p.append(rect(1138, 25, 3, 3, GREEN, cls="pulse"))
    p.append(text(1168, 33, "EN LÍNEA", 9, GREEN, "end", 400, 1.2))
    p.append(line(0, 64, W, 64, "url(#pcNeon)", 1, 0.5))

    # ── left panel ────────────────────────────────────────────────────────────
    p.append(rect(32, 84, 352, 482, PANEL, opacity="0.72"))
    p.append(f'<rect x="32.5" y="84.5" width="351" height="481" fill="none" stroke="{BORDER}"/>')
    p.append(rect(56, 108, 304, 354, "#0A101C"))
    p.append(f'<rect x="56.5" y="108.5" width="303" height="353" fill="none" stroke="#263A54"/>')
    p.append(rect(56, 108, 304, 2, "url(#pcNeon)", opacity="0.55"))
    # portrait glow + sprite
    p.append('<ellipse cx="208" cy="282" rx="150" ry="150" fill="url(#pcHalo)"/>')
    p.append('<g class="portrait">' + portrait_svg(80, 126) + '</g>')
    # scanline over portrait
    p.append(rect(56, 108, 304, 354, "#000000", opacity="0.0"))
    p.append(f'<g clip-path="url(#pcPortraitClip)"><rect x="56" y="108" width="304" height="2" fill="{CYAN}" opacity="0.25" class="scan"/></g>')
    p.append('<clipPath id="pcPortraitClip"><rect x="56" y="108" width="304" height="354"/></clipPath>')
    # frame corners
    p.append('<path d="M56 132V108h24M360 132V108h-24M56 438v24h24M360 438v24h-24" fill="none" stroke="#00F7FF" stroke-opacity="0.5" stroke-width="2"/>')
    p.append(text(68, 124, "PLAYER 1", 8, CYAN, "start", 700, 1.6))
    p.append(text(342, 124, "READY", 9, GREEN, "end", 700, 1.4, cls="pulse"))
    # name block
    p.append(text(56, 500, "NICOLÁS", 30, CREAM, "start", 700, 2))
    p.append(text(56, 520, "MONCADA MONTAÑO", 12, BLUE, "start", 600, 2.2))
    p.append(text(56, 540, "INGENIERÍA DE SISTEMAS  ·  3ER SEMESTRE  ·  UNIMINUTO", 9, MUTED, "start", 400, 1.2))
    p.append(text(56, 556, "BOGOTÁ, COLOMBIA  ·  20 AÑOS  ·  UTC-5", 9, MUTED, "start", 400, 1.4))
    p.append(barcode(56, 566, 90, 16))
    p.append(text(156, 579, "ID NM-BOG-2026", 8, DIM, "start", 400, 1.0))

    # ── right panel ───────────────────────────────────────────────────────────
    p.append(rect(408, 84, 760, 482, PANEL, opacity="0.55"))
    p.append(f'<rect x="408.5" y="84.5" width="759" height="481" fill="none" stroke="{BORDER}"/>')
    p.append(text(432, 116, "ATRIBUTOS", 9, CYAN, "start", 700, 3))
    p.append(text(1152, 116, "PERFIL COMPLETO", 9, MUTED, "end", 400, 1.2))
    p.append(line(432, 126, 1152, 126, "#1B2A44"))

    attrs = [
        ("ai", "IA", "NIVEL INTERMEDIO · LA USO A DIARIO", "INTERMEDIO", CYAN),
        ("flow", "VIBE CODING", "PARA MEJORAR MI FLUJO DE DESARROLLO", "EN FLUJO", PINK),
        ("shield", "CIBERSEGURIDAD", "APRENDIENDO · ME INTERESA CADA VEZ MÁS", "APRENDIENDO", YELLOW),
        ("design", "DISEÑO", "CREATIVIDAD APLICADA A LO QUE CONSTRUYO", "CREATIVO", BLUE),
        ("code", "CÓDIGO", "PROGRAMAR Y RESOLVER PROBLEMAS", "EN PRÁCTICA", GREEN),
        ("rocket", "PROYECTOS", "BÁSICOS, CON ENFOQUE ESCALABLE", "ESCALABLES", PINK),
    ]
    y = 140
    for i, (ic, name, desc, status, color) in enumerate(attrs):
        p.append(rect(430, y, 724, 30, "#0D1727" if i % 2 == 0 else "#0B1422", opacity="0.55"))
        p.append(icon(ic, 438, y + 5, color, 2))
        p.append(text(482, y + 13, name, 12, CREAM, "start", 700, 1.2))
        p.append(text(482, y + 26, desc, 9.5, MUTED, "start", 400, 0.6))
        p.append(tag(1150, y + 7, status, color))
        y += 32

    p.append(line(432, 344, 1152, 344, "#1B2A44"))

    # languages
    p.append(text(432, 372, "LENGUAJES", 9, CYAN, "start", 700, 3))
    lang = [
        ("PYTHON", "EN PRÁCTICA", 3, CYAN),
        ("JAVASCRIPT", "EN PRÁCTICA", 3, CYAN),
        ("HTML / CSS", "EN PRÁCTICA", 3, CYAN),
        ("SQL", "APRENDIENDO", 2, YELLOW),
    ]
    ly = 390
    for name, status, lvl, color in lang:
        p.append(text(432, ly, name, 11, CREAM, "start", 600, 1.0))
        p.append(rect(690, ly - 6, 5, 5, color))
        p.append(text(702, ly, status, 9, MUTED, "start", 400, 0.8))
        ly += 26
    p.append(text(432, 506, "Aprendizaje constante: ningún experto nace sabiendo.", 8.5, DIM, "start", 400, 0.6))

    # interests
    p.append(text(850, 372, "INTERESES", 9, CYAN, "start", 700, 3))
    chips = [
        ("VIDEOJUEGOS", PINK), ("MÚSICA", BLUE), ("DISEÑO", YELLOW),
        ("IA", CYAN), ("CIBERSEGURIDAD", GREEN), ("APRENDER", "#A9B8D8"),
    ]
    cx, cy = 850, 390
    for label, color in chips:
        w = 10 + len(label) * 6.2 + 12
        p.append(rect(cx, cy, w, 28, "#0B1626", opacity="0.9"))
        p.append(rect(cx, cy, 3, 28, color))
        p.append(text(cx + 12, cy + 18.5, label, 9, color, "start", 600, 0.7))
        cx += w + 10
        if cx > 1040:
            cx = 850
            cy += 32

    # quote
    p.append(text(432, 540, "“", 46, YELLOW, "start", 700, 0))
    p.append(text(472, 526, "Me apasiona programar, diseñar", 15, CREAM, "start", 600, 0.6))
    p.append(text(472, 548, "y resolver problemas.", 15, CREAM, "start", 600, 0.6))
    p.append(text(850, 526, "Vibe coding: una herramienta para", 10, MUTED, "start", 400, 0.7))
    p.append(text(850, 543, "pensar más rápido y cuidar el flujo,", 10, MUTED, "start", 400, 0.7))
    p.append(text(850, 560, "sin saltarme los fundamentos.", 10, MUTED, "start", 400, 0.7))

    # footer
    p.append(line(0, 600, W, 600, BORDER))
    p.append(rect(0, 600, W, 50, "#080C14", opacity="0.9"))
    p.append(rect(24, 618, 3, 3, YELLOW, cls="blink"))
    p.append(text(36, 626, "INSERT COIN TO CONTINUE", 10, YELLOW, "start", 700, 1.2))
    p.append(text(600, 626, "NICOLÁS MONCADA  ·  BOGOTÁ, CO  ·  APRENDIZAJE CONSTANTE", 10, MUTED, "middle", 400, 1.0))
    p.append(text(1168, 626, "NICOLÁS.OS", 10, PINK, "end", 700, 1.0))

    # CRT overlay
    p.append('<rect width="1200" height="650" fill="none" stroke="#22304A" stroke-width="2"/>')
    p.append("</svg>")
    return "\n".join(p)


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes)")

