#!/usr/bin/env python3
"""Build the pixel-art hero scene for the GitHub profile (enhanced edition)."""
from __future__ import annotations

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "pixel-hero.svg"

S = 4  # one art pixel = 4 screen pixels
W, H = 1200, 700

CYAN = "#00F7FF"
PINK = "#FF3D8B"
MAGENTA = "#FF007F"
YELLOW = "#FFD166"
GOLD = "#FFB800"
CREAM = "#F4E8D0"
INK = "#080C14"
WHITE = "#E6EDF3"
MUTED = "#8B98AB"
PURPLE = "#7C4DFF"
DARK_PURPLE = "#2A1A4A"
TEAL = "#00E6A8"
ORANGE = "#FF9E4A"
BRICK = "#C94F4F"

FONT = '"Cascadia Mono", "Consolas", "Courier New", monospace'


def u(v: float) -> float:
    return v * S


def rect(x, y, w, h, fill, opacity=None, cls=None, rx=0):
    attrs = [f'x="{u(x):g}"', f'y="{u(y):g}"', f'width="{u(w):g}"', f'height="{u(h):g}"', f'fill="{fill}"']
    if rx:
        attrs.append(f'rx="{u(rx):g}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    if cls:
        attrs.append(f'class="{cls}"')
    return f'<rect {" ".join(attrs)}/>'


def srect(x, y, w, h, fill, opacity=None, cls=None, rx=0):
    """Rectangle in screen pixels (for thin overlays)."""
    attrs = [f'x="{x:g}"', f'y="{y:g}"', f'width="{w:g}"', f'height="{h:g}"', f'fill="{fill}"']
    if rx:
        attrs.append(f'rx="{rx:g}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    if cls:
        attrs.append(f'class="{cls}"')
    return f'<rect {" ".join(attrs)}/>'


def line(x1, y1, x2, y2, stroke, width=1, opacity=None, cls=None):
    attrs = [
        f'x1="{u(x1):g}"', f'y1="{u(y1):g}"', f'x2="{u(x2):g}"', f'y2="{u(y2):g}"',
        f'stroke="{stroke}"', f'stroke-width="{width:g}"',
    ]
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    if cls:
        attrs.append(f'class="{cls}"')
    return f'<line {" ".join(attrs)}/>'


def text(x, y, content, size=12, fill=WHITE, anchor="start", weight=400, spacing=0, cls=None, opacity=None):
    attrs = [
        f'x="{x:g}"', f'y="{y:g}"', f'font-size="{size:g}"', f'fill="{fill}"',
        f'text-anchor="{anchor}"', f'font-family=\'{FONT}\'',
    ]
    if weight != 400:
        attrs.append(f'font-weight="{weight}"')
    if spacing:
        attrs.append(f'letter-spacing="{spacing:g}"')
    if cls:
        attrs.append(f'class="{cls}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    return f'<text {" ".join(attrs)}>{content}</text>'


def sprite(x, y, rows, color, unit=1, cls=None, extra=None):
    out = [f'<g class="{cls}">' if cls else "<g>"]
    for ry, row in enumerate(rows):
        cx = 0
        while cx < len(row):
            if row[cx] != "#":
                cx += 1
                continue
            run = 1
            while cx + run < len(row) and row[cx + run] == "#":
                run += 1
            out.append(rect(x + cx * unit, y + ry * unit, run * unit, unit, color))
            cx += run
    out.append("</g>")
    return "".join(out)


def pacman(x, y, color=YELLOW, unit=1, cls=None):
    rows = [
        "..###..",
        ".#####.",
        "###....",
        "##.....",
        "###....",
        ".#####.",
        "..###..",
    ]
    closed = [
        "..###..",
        ".#####.",
        "#######",
        "#######",
        "#######",
        ".#####.",
        "..###..",
    ]
    return (
        f'<g class="{cls}">' if cls else "<g>"
        + sprite(x, y, rows, color, unit)
        + sprite(x, y, closed, color, unit, cls="pac-closed")
        + "</g>"
    )


def ghost(x, y, color, unit=1, cls=None):
    rows = [
        ".#####.",
        "#######",
        "#######",
        "#######",
        "#######",
        "##.#.##",
    ]
    return sprite(x, y, rows, color, unit, cls)


def heart(x, y, color, unit=1, cls=None):
    rows = [
        ".###.###.",
        "#########",
        "#########",
        "#########",
        ".#######.",
        "..#####..",
        "...###...",
        "....#....",
    ]
    return sprite(x, y, rows, color, unit, cls)


def build() -> str:
    p: list[str] = []
    p.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        'role="img" aria-labelledby="heroTitle heroDesc" shape-rendering="crispEdges">'
    )
    p.append('<title id="heroTitle">NICOLÁS.OS — habitación gamer pixel art de Nicolás Moncada</title>')
    p.append(
        '<desc id="heroDesc">Escena pixel art de una habitación gamer: Nicolás Moncada, 20 años, '
        'estudiante de tercer semestre de Ingeniería de Sistemas en Bogotá, aparece con audífonos '
        'frente a un computador retro, un tocadiscos y una máquina arcade de Pac-Man. La escena '
        'incluye sus intereses: videojuegos, música, inteligencia artificial, vibe coding y diseño.</desc>'
    )

    p.append("<defs>")
    p.append(
        '<linearGradient id="wallGrad" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#121B30"/><stop offset="0.62" stop-color="#0C1322"/>'
        '<stop offset="1" stop-color="#080D18"/></linearGradient>'
    )
    p.append(
        '<linearGradient id="neonGrad" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{CYAN}"/><stop offset="0.52" stop-color="#A9C4FF"/>'
        f'<stop offset="1" stop-color="{PINK}"/></linearGradient>'
    )
    p.append(
        '<linearGradient id="screenGrad" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#0A2A33"/><stop offset="1" stop-color="#061019"/></linearGradient>'
    )
    p.append(
        '<radialGradient id="cabinetGlow" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="{PINK}" stop-opacity="0.30"/>'
        f'<stop offset="0.55" stop-color="{CYAN}" stop-opacity="0.10"/>'
        '<stop offset="1" stop-color="#00F7FF" stop-opacity="0"/></radialGradient>'
    )
    p.append(
        '<radialGradient id="lampGlow" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="{YELLOW}" stop-opacity="0.34"/>'
        '<stop offset="1" stop-color="#FFD166" stop-opacity="0"/></radialGradient>'
    )
    p.append(
        '<radialGradient id="neonGlow" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="{CYAN}" stop-opacity="0.45"/>'
        '<stop offset="1" stop-color="#00F7FF" stop-opacity="0"/></radialGradient>'
    )
    p.append(
        '<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
        '<rect width="4" height="1" fill="#FFFFFF" opacity="0.022"/></pattern>'
    )
    p.append(
        '<filter id="softGlow" x="-40%" y="-40%" width="180%" height="180%">'
        '<feGaussianBlur stdDeviation="6" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
    )
    p.append("<style>")
    p.append(
        """
        text { paint-order: stroke fill; }
        .twinkle { animation: twinkle 3.4s ease-in-out infinite; }
        .twinkle.d1 { animation-delay: .5s; }
        .twinkle.d2 { animation-delay: 1.1s; }
        .twinkle.d3 { animation-delay: 1.7s; }
        .twinkle.d4 { animation-delay: 2.2s; }
        .neon { animation: neon 7s steps(1, end) infinite; }
        .neon-sub { animation: neonSub 7s steps(1, end) infinite; }
        .blink { animation: blink 1.1s steps(1, end) infinite; }
        .blink.slow { animation-duration: 2.4s; }
        .pulse { animation: pulse 1.9s ease-in-out infinite; }
        .pac-closed { animation: pacClosed .28s steps(1, end) infinite; }
        .pac-run { animation: pacRun 7.2s steps(24, end) infinite; }
        .ghost-bob { animation: ghostBob 1.15s steps(2, end) infinite; }
        .ghost-bob.g2 { animation-delay: .3s; animation-duration: 1.45s; }
        .ghost-bob.g3 { animation-delay: .6s; animation-duration: 1.3s; }
        .char-bob { animation: charBob 2.2s steps(2, end) infinite; }
        .record { transform-box: fill-box; transform-origin: 50% 50%; animation: spin 3.6s steps(16, end) infinite; }
        .note { animation: note 4.8s ease-in-out infinite; }
        .note.n2 { animation-delay: 1.6s; }
        .note.n3 { animation-delay: 3.2s; }
        .eq { transform-box: fill-box; transform-origin: 50% 100%; animation: eq .9s steps(4, end) infinite alternate; }
        .eq.e2 { animation-delay: .1s; }
        .eq.e3 { animation-delay: .2s; }
        .eq.e4 { animation-delay: .3s; }
        .eq.e5 { animation-delay: .4s; }
        .eq.e6 { animation-delay: .5s; }
        .steam { animation: steam 3.6s ease-out infinite; }
        .steam.s2 { animation-delay: 1.2s; }
        .steam.s3 { animation-delay: 2.4s; }
        .scanline { animation: scanline 4.2s linear infinite; }
        .cab-glow { animation: cabGlow 2.4s ease-in-out infinite; }
        .flicker { animation: flicker 5s steps(1, end) infinite; }
        .sway { transform-box: fill-box; transform-origin: 50% 100%; animation: sway 5s ease-in-out infinite; }
        .shoot { animation: shoot 9s linear infinite; opacity: 0; }
        @keyframes twinkle { 0%,100%{opacity:.15} 50%{opacity:.95} }
        @keyframes neon {
          0%,4%,7%,100% { opacity:1 } 5%,6% { opacity:.35 }
          46%,47% { opacity:.55 } 48%,49% { opacity:1 }
          82%,83% { opacity:.4 } 84%,85% { opacity:1 }
        }
        @keyframes neonSub { 0%,8%,100%{opacity:.85} 9%,10%{opacity:.3} 56%,57%{opacity:.45} }
        @keyframes blink { 0%,49%{opacity:1} 50%,100%{opacity:0} }
        @keyframes pulse { 0%,100%{opacity:.35} 50%{opacity:1} }
        @keyframes pacClosed { 0%,45%{opacity:0} 46%,100%{opacity:1} }
        @keyframes pacRun { 0%{transform:translateX(0)} 78%,100%{transform:translateX(172px)} }
        @keyframes ghostBob { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-4px)} }
        @keyframes charBob { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-3px)} }
        @keyframes spin { to{transform:rotate(360deg)} }
        @keyframes note { 0%{transform:translate(0,0);opacity:0} 12%{opacity:1} 70%{opacity:.9} 100%{transform:translate(10px,-54px);opacity:0} }
        @keyframes eq { 0%{transform:scaleY(.18)} 100%{transform:scaleY(1)} }
        @keyframes steam { 0%{transform:translate(0,2px);opacity:0} 18%{opacity:.55} 100%{transform:translate(-3px,-22px);opacity:0} }
        @keyframes scanline { 0%{transform:translateY(0);opacity:0} 12%{opacity:.5} 88%{opacity:.5} 100%{transform:translateY(116px);opacity:0} }
        @keyframes cabGlow { 0%,100%{opacity:.4} 50%{opacity:.9} }
        @keyframes flicker { 0%,3%,5%,100%{opacity:1} 4%{opacity:.25} 47%,48%{opacity:.6} }
        @keyframes sway { 0%,100%{transform:rotate(0)} 50%{transform:rotate(1.4deg)} }
        @keyframes shoot {
          0%, 68% { transform: translate(0,0); opacity:0; }
          70% { opacity:.9; }
          78% { transform: translate(64px,26px); opacity:0; }
          100% { opacity:0; }
        }
        @media (prefers-reduced-motion: reduce) {
          .twinkle,.neon,.neon-sub,.blink,.pulse,.pac-closed,.pac-run,.ghost-bob,.char-bob,
          .record,.note,.eq,.steam,.scanline,.cab-glow,.flicker,.sway,.shoot { animation:none !important; }
          .pac-closed { opacity: 0; }
          .shoot { opacity: 0; }
        }
        """
    )
    p.append("</style>")
    p.append("</defs>")

    # ── frame / room ──────────────────────────────────────────────────────────
    p.append(rect(0, 0, 300, 175, "#060911"))
    p.append(rect(0, 0, 300, 175, "url(#wallGrad)"))
    p.append(rect(0, 12, 300, 120, "#0B1220", opacity="0.18"))

    # wall panelling
    for x in range(10, 300, 20):
        p.append(rect(x, 12, 0.5, 120, "#060B14", opacity="0.55"))
    p.append(rect(0, 12, 300, 1, "#1B2A44", opacity="0.55"))

    # floor
    p.append(rect(0, 132, 300, 33, "#24150F"))
    for y in range(133, 165, 5):
        p.append(rect(0, y, 300, 0.5, "#180C08", opacity="0.8"))
    for i, x in enumerate(range(6, 300, 24)):
        p.append(rect(x + (i % 2) * 6, 132, 0.5, 33, "#180C08", opacity="0.55"))
    p.append(rect(0, 130, 300, 2, "#1C2436"))
    p.append(rect(0, 130, 300, 0.5, "#33425C", opacity="0.7"))
    p.append(rect(0, 132, 300, 0.5, "#090D16"))

    # soft ambient glows
    p.append('<ellipse cx="1020" cy="620" rx="240" ry="220" fill="url(#cabinetGlow)" class="cab-glow"/>')
    p.append('<ellipse cx="250" cy="120" rx="210" ry="190" fill="url(#lampGlow)" opacity="0.55"/>')

    # ── window ────────────────────────────────────────────────────────────────
    p.append(rect(10, 15, 84, 81, "#5B3E2A"))
    p.append(rect(11, 16, 82, 79, "#2A1A12"))
    p.append(rect(14, 20, 76, 70, "#0A1630"))
    # sky bands
    p.append(rect(14, 20, 76, 18, "#0B1B3A"))
    p.append(rect(14, 38, 76, 18, "#12244A"))
    p.append(rect(14, 56, 76, 22, "#1A2350"))
    p.append(rect(14, 78, 76, 12, "#251E48"))
    # stars
    stars = [(20, 24, "d1"), (28, 30, ""), (36, 23, "d2"), (44, 32, "d3"), (52, 25, "d1"),
             (60, 29, ""), (68, 23, "d4"), (75, 33, "d2"), (82, 26, "d1"), (24, 42, "d3"),
             (33, 38, ""), (47, 41, "d2"), (58, 37, "d4"), (70, 43, "d1"), (80, 39, "d3"),
             (18, 52, "d2"), (30, 50, ""), (42, 47, "d1"), (64, 51, "d3"), (78, 48, "")]
    for sx, sy, cls in stars:
        p.append(rect(sx, sy, 1, 1, "#EAF6FF", cls=f"twinkle {cls}".strip()))
    # shooting star
    p.append('<g class="shoot">' + rect(28, 30, 3, 1, "#EAF6FF") + rect(26, 31, 2, 1, "#9ED8FF", opacity="0.7") + "</g>")
    # moon
    p.append(sprite(66, 30, ["..###..", ".#####.", "#######", "#######", "#######", ".#####.", "..###.."], "#F4E8C0", 1))
    p.append(rect(68, 33, 2, 2, "#D6C79A"))
    p.append(rect(71, 36, 1, 1, "#D6C79A"))
    # mountains + city
    p.append('<path d="M14 84 L24 68 L33 78 L43 64 L54 79 L64 70 L75 82 L90 74 L90 90 L14 90 Z" fill="#0A1222"/>')
    buildings = [(15, 72, 8, 18), (24, 66, 7, 24), (32, 75, 9, 15), (42, 70, 6, 20),
                 (49, 63, 8, 27), (58, 73, 7, 17), (66, 68, 9, 22), (76, 71, 14, 19)]
    for bx, by, bw, bh in buildings:
        p.append(rect(bx, by, bw, bh, "#111A2B"))
    lit = [(16, 76), (18, 80), (26, 70), (28, 74), (34, 79), (36, 84), (44, 74), (46, 78),
           (51, 68), (53, 72), (55, 76), (60, 77), (63, 81), (68, 72), (70, 76), (73, 80),
           (79, 75), (82, 79), (85, 74)]
    for i, (lx, ly) in enumerate(lit):
        color = YELLOW if i % 3 else CYAN
        cls = "blink slow" if i in (4, 11, 16) else ("flicker" if i in (7, 18) else "")
        p.append(rect(lx, ly, 1, 1, color, opacity="0.8", cls=cls))
    # window mullions
    p.append(rect(50, 20, 2, 70, "#5B3E2A"))
    p.append(rect(14, 54, 76, 2, "#5B3E2A"))
    p.append(rect(51, 20, 0.5, 70, "#7A573C", opacity="0.7"))
    p.append(rect(14, 54.5, 76, 0.5, "#7A573C", opacity="0.7"))
    # sill
    p.append(rect(8, 96, 88, 3, "#6B4A2F"))
    p.append(rect(8, 96, 88, 0.75, "#8E6742"))
    p.append(rect(8, 99, 88, 1, "#3A2418"))
    # curtains
    p.append(rect(6, 14, 7, 83, "#3A1B3A"))
    p.append(rect(8, 14, 2, 83, "#542A54"))
    p.append(rect(11, 14, 2, 83, "#2A122A"))
    p.append(rect(87, 14, 7, 83, "#3A1B3A"))
    p.append(rect(89, 14, 2, 83, "#542A54"))
    p.append(rect(92, 14, 2, 83, "#2A122A"))
    p.append(rect(4, 12, 92, 2, "#C9A227"))
    p.append(rect(4, 12, 2, 4, "#E3C25A"))
    p.append(rect(94, 12, 2, 4, "#E3C25A"))
    # tiny cactus on the sill
    p.append(rect(74, 92, 4, 4, "#8B4A2F"))
    p.append(rect(75, 88, 2, 4, "#2E7D4F"))
    p.append(rect(73, 89, 2, 1, "#2E7D4F"))
    p.append(rect(77, 87, 1, 3, "#4ADE80"))
    p.append(rect(73, 92, 6, 1, "#5A2E1C"))

    # ── posters ───────────────────────────────────────────────────────────────
    # Pac-Man poster
    p.append(rect(98, 20, 36, 48, "#8A6A4A"))
    p.append(rect(99, 21, 34, 46, "#150E24"))
    p.append(rect(99, 21, 34, 4, "#241634"))
    p.append(text(464, 108, "PAC-MAN", 8, YELLOW, "middle", 700, 1.2))
    p.append(pacman(102, 29, YELLOW, 1))
    p.append(ghost(112, 33, PINK, 1))
    p.append(ghost(119, 33, CYAN, 1))
    p.append(ghost(126, 33, "#FF9E4A", 1))
    for i in range(5):
        p.append(rect(104 + i * 3, 44, 1, 1, "#FFE9A8"))
    p.append(text(464, 203, "1UP", 7, CREAM, "middle", 700, 1.4))
    p.append(rect(99, 21, 34, 1, "#3A2440"))
    # heart / NM poster
    p.append(rect(138, 24, 20, 34, "#8A6A4A"))
    p.append(rect(139, 25, 18, 32, "#26102A"))
    p.append(heart(143, 28, PINK, 1))
    p.append(text(592, 208, "NM", 8, CREAM, "middle", 700, 1.5))
    p.append(rect(139, 25, 18, 3, "#3A1538"))

    # ── shelf ─────────────────────────────────────────────────────────────────
    p.append(rect(98, 72, 108, 2, "#5A3A24"))
    p.append(rect(98, 72, 108, 0.5, "#8E6742"))
    p.append(rect(100, 74, 3, 4, "#3A2418"))
    p.append(rect(201, 74, 3, 4, "#3A2418"))
    # books
    books = [(102, 64, 3, 8, "#FF3D8B"), (106, 62, 3, 10, "#00A7B5"), (110, 65, 2, 7, "#FFD166"),
             (113, 63, 3, 9, "#70A5FD"), (117, 66, 4, 6, "#8B5E3C")]
    for bx, by, bw, bh, bc in books:
        p.append(rect(bx, by, bw, bh, bc))
        p.append(rect(bx, by, bw, 0.5, "#FFFFFF", opacity="0.18"))
    # cassette
    p.append(rect(124, 66, 10, 6, "#1B2636"))
    p.append(rect(125, 67, 8, 2, "#FFD166"))
    p.append(rect(126, 70, 6, 1, "#3A4A60"))
    p.append(rect(125, 67, 1, 5, "#2A3A52"))
    p.append(rect(132, 67, 1, 5, "#2A3A52"))
    # trophy
    p.append(rect(138, 67, 6, 2, "#FFD166"))
    p.append(rect(139, 69, 4, 2, "#FFB800"))
    p.append(rect(140, 71, 2, 2, "#FFD166"))
    p.append(rect(138, 73, 6, 1, "#8A6A4A"))
    # stack of game cases
    p.append(rect(160, 64, 16, 2, "#1B2636"))
    p.append(rect(161, 64, 14, 1, CYAN))
    p.append(rect(160, 66, 16, 2, "#1B2636"))
    p.append(rect(161, 66, 14, 1, PINK))
    p.append(rect(160, 68, 16, 2, "#1B2636"))
    p.append(rect(161, 68, 14, 1, YELLOW))
    p.append(rect(160, 70, 16, 2, "#1B2636"))
    p.append(rect(161, 70, 14, 1, "#70A5FD"))
    # small trophy-shaped figure
    p.append(rect(181, 66, 5, 6, "#FFD166"))
    p.append(rect(182, 67, 3, 2, "#FFB800"))
    p.append(rect(180, 72, 7, 1, "#8A6A4A"))
    # small neon strip under shelf
    p.append(rect(98, 79, 108, 0.5, CYAN, opacity="0.45"))
    p.append(rect(98, 79, 108, 2, "url(#neonGrad)", opacity="0.08"))

    # ── neon name panel ───────────────────────────────────────────────────────
    p.append(rect(160, 18, 132, 44, "#070C16", opacity="0.92"))
    # stepped border
    p.append('<path d="M160 22 L164 18 L288 18 L292 22 L292 58 L288 62 L164 62 L160 58 Z" fill="none" stroke="#263A54" stroke-width="2"/>')
    p.append('<path d="M163 23 L166 20 L286 20 L290 23 L290 57 L286 60 L166 60 L163 57 Z" fill="none" stroke="#00F7FF" stroke-opacity="0.28" stroke-width="1"/>')
    p.append(rect(164, 20, 2, 2, CYAN))
    p.append(rect(286, 20, 2, 2, PINK))
    p.append(text(672, 88, "PLAYER 1", 8, "#A9B8D8", "start", 700, 1.8))
    p.append(text(1132, 88, "READY", 8, "#4ADE80", "end", 700, 1.8, cls="pulse"))
    p.append(rect(648, 92, 40, 0.75, "#2A3A52"))
    p.append(rect(1112, 92, 32, 0.75, "#2A3A52"))
    p.append(text(896, 146, "NICOLÁS", 60, "url(#neonGrad)", "middle", 700, 5, cls="neon"))
    p.append(text(896, 180, "MONCADA MONTAÑO", 15, "#A9B8D8", "middle", 600, 5, cls="neon-sub"))
    p.append(rect(660, 194, 472, 1, "#243450"))
    p.append(rect(740, 194, 120, 1, "#FF3D8B", opacity="0.8"))
    p.append(text(896, 216, "INGENIERÍA DE SISTEMAS  ·  3ER SEMESTRE", 9, "#C9D1D9", "middle", 400, 2.2))
    p.append(text(896, 234, "BOGOTÁ, COLOMBIA  ·  20 AÑOS  ·  UTC-5", 9, MUTED, "middle", 400, 2.2))
    # ── rug ───────────────────────────────────────────────────────────────────
    p.append(rect(8, 148, 202, 16, "#2E1740"))
    p.append(rect(8, 148, 202, 1, "#5A3A7A"))
    p.append(rect(8, 163, 202, 1, "#1A0E26"))
    for i in range(11):
        x = 16 + i * 18
        p.append(rect(x, 152, 9, 1, "#45255E", opacity="0.9"))
        p.append(rect(x + 4, 156, 9, 1, "#45255E", opacity="0.9"))
        p.append(rect(x + 8, 160, 9, 1, "#45255E", opacity="0.9"))
    p.append(rect(20, 150, 4, 2, "#FF3D8B", opacity="0.6"))
    p.append(rect(180, 158, 4, 2, "#00F7FF", opacity="0.5"))

    # ── desk ──────────────────────────────────────────────────────────────────
    p.append(rect(34, 112, 168, 5, "#5A3A24"))
    p.append(rect(34, 112, 168, 1, "#8E6742"))
    p.append(rect(34, 117, 168, 15, "#3A2418"))
    p.append(rect(34, 117, 168, 1, "#24140C"))
    p.append(rect(36, 132, 4, 29, "#2A1810"))
    p.append(rect(196, 132, 4, 29, "#2A1810"))
    p.append(rect(36, 160, 4, 1, "#0E0806"))
    p.append(rect(196, 160, 4, 1, "#0E0806"))
    p.append(rect(34, 120, 3, 12, "#4A2E1E"))
    p.append(rect(199, 120, 3, 12, "#4A2E1E"))
    # drawer fronts
    p.append(rect(40, 120, 50, 10, "#42291A"))
    p.append(rect(40, 120, 50, 0.5, "#5E3C26"))
    p.append(rect(96, 120, 58, 10, "#3E2618"))
    p.append(rect(160, 120, 38, 10, "#42291A"))
    p.append(rect(160, 120, 38, 0.5, "#5E3C26"))
    p.append(rect(65, 122, 6, 1.5, "#C9A227"))
    p.append(rect(176, 122, 6, 1.5, "#C9A227"))
    p.append(rect(65, 123, 6, 0.5, "#8A6A4A"))
    p.append(rect(176, 123, 6, 0.5, "#8A6A4A"))
    p.append(rect(34, 132, 168, 4, "#000000", opacity="0.22"))

    # ── CRT monitor ───────────────────────────────────────────────────────────
    p.append('<g transform="translate(104,0)">')
    p.append(rect(84, 78, 64, 36, "#C9B89A"))
    p.append(rect(84, 78, 64, 2, "#E6D8C0"))
    p.append(rect(84, 112, 64, 2, "#8A7A62"))
    p.append(rect(88, 82, 56, 28, "#2A2118"))
    p.append(rect(90, 84, 52, 24, "#061018"))
    p.append(rect(90, 84, 52, 1, "#1B4A54", opacity="0.8"))
    # code lines
    p.append(text(374, 352, "$ whoami", 9, CYAN))
    p.append(text(374, 366, "> nicolas", 9, WHITE))
    p.append(text(374, 380, "$ cat pasion.txt", 9, CYAN))
    p.append(text(374, 394, "> crear · aprender", 9, "#FF9E4A"))
    p.append(text(374, 408, "> IA · diseño · código", 9, "#4ADE80"))
    p.append(text(374, 422, "> seguridad + diseño", 9, "#70A5FD"))
    p.append(srect(506, 414, 6, 8, CYAN, cls="blink"))
    # tiny IA badge
    p.append(rect(128, 86, 10, 5, "#0B2428"))
    p.append(rect(128, 86, 10, 0.5, CYAN, opacity="0.7"))
    p.append(text(526, 356, "IA", 6, CYAN, "middle", 700, 0.8))
    # scanline inside the screen
    p.append('<g clip-path="url(#screenClip)">' + srect(360, 336, 208, 1, CYAN, opacity="0.35", cls="scanline") + "</g>")
    p.append('<clipPath id="screenClip"><rect x="360" y="336" width="208" height="96"/></clipPath>')
    # power LED + vent
    p.append(rect(141, 109, 1, 1, "#4ADE80", cls="pulse"))
    for i in range(4):
        p.append(rect(88 + i * 3, 109, 2, 0.5, "#8A7A62"))
    # stand
    p.append(rect(108, 112, 16, 2, "#8A7A62"))
    p.append(rect(104, 114, 24, 2, "#C9B89A"))
    p.append(rect(104, 114, 24, 0.5, "#E6D8C0"))
    # keyboard (in front of the monitor, wider than the bezel)
    p.append(rect(78, 106, 78, 6, "#1B2636"))
    p.append(rect(78, 106, 78, 1, "#3A4A60"))
    for row in range(3):
        for col in range(24):
            p.append(rect(80 + col * 3, 107.5 + row * 1.5, 2, 1, "#2E3A4E"))
    p.append(rect(78, 112, 78, 0.5, "#0B1018"))
    # mouse
    p.append(rect(160, 108, 5, 4, "#C9B89A"))
    p.append(rect(162, 109, 1, 1, "#8A7A62"))
    p.append("</g>")

    # ── turntable ─────────────────────────────────────────────────────────────
    p.append(rect(40, 94, 38, 18, "#4A2E1E"))
    p.append(rect(40, 94, 38, 1, "#8E6742"))
    p.append(rect(42, 96, 30, 14, "#151821"))
    p.append('<circle cx="228" cy="424" r="24" fill="#0A0C12" stroke="#2A3A52" stroke-width="2"/>')
    p.append('<g class="record"><circle cx="228" cy="424" r="17" fill="#0C0E16" stroke="#1B2636" stroke-width="1"/>'
             '<circle cx="228" cy="424" r="9" fill="#FF3D8B"/><circle cx="228" cy="424" r="3" fill="#F4E8D0"/>'
             '<rect x="226" y="410" width="4" height="2" fill="#8B98AB"/></g>')
    # tonearm
    p.append('<path d="M290 404 L300 414 L300 430" fill="none" stroke="#C9B89A" stroke-width="3"/>')
    p.append('<rect x="288" y="402" width="6" height="6" fill="#8A7A62"/>')
    p.append(rect(64, 104, 5, 2, "#FFD166"))
    p.append(rect(70, 104, 5, 2, "#00F7FF"))
    p.append(rect(64, 107, 2, 1, "#4ADE80"))
    p.append(text(236, 444, "MÚSICA", 8, MUTED, "middle", 700, 1.6))
    # music notes
    p.append('<g class="note">' + rect(72, 82, 3, 2, PINK) + rect(74, 78, 1, 5, PINK) + rect(75, 78, 2, 1, PINK) + "</g>")
    p.append('<g class="note n2">' + rect(79, 88, 3, 2, CYAN) + rect(81, 84, 1, 5, CYAN) + "</g>")
    p.append('<g class="note n3">' + rect(66, 88, 3, 2, YELLOW) + rect(68, 84, 1, 5, YELLOW) + "</g>")

    # ── mug + equalizer ───────────────────────────────────────────────────────
    # mug
    p.append(rect(170, 102, 9, 9, "#C9B89A"))
    p.append(rect(170, 102, 9, 1, "#E6D8C0"))
    p.append(rect(179, 105, 2, 3, "#C9B89A"))
    p.append(rect(172, 104, 5, 1, PINK, opacity="0.8"))
    p.append(rect(172, 106, 5, 0.5, PINK, opacity="0.4"))
    p.append('<g class="steam">' + rect(173, 99, 1, 2, "#C9D1D9") + "</g>")
    p.append('<g class="steam s2">' + rect(176, 98, 1, 2, "#C9D1D9") + "</g>")
    p.append('<g class="steam s3">' + rect(179, 99, 1, 2, "#C9D1D9") + "</g>")
    # tiny speaker / equalizer behind mug
    p.append(rect(184, 94, 8, 12, "#151821"))
    p.append(rect(184, 94, 8, 1, "#3A4A60"))
    for i in range(5):
        p.append(rect(185 + i * 1.3, 104 - (i % 3) * 2, 0.8, 2 + (i % 3) * 2, CYAN, cls=f"eq e{i+1}"))

    # sketchbook on the desk (design / creativity)
    p.append(rect(82, 105, 22, 7, "#C9B89A"))
    p.append(rect(83, 106, 20, 5, "#F4E8D0"))
    p.append(rect(84, 107, 18, 0.5, "#D8C8A8"))
    p.append(rect(87, 107, 2, 2, YELLOW))
    p.append(rect(89, 109, 1, 1, YELLOW))
    p.append(rect(92, 108, 4, 1, PINK))
    p.append(rect(97, 109, 3, 1, CYAN))
    p.append(rect(101, 102, 1, 9, "#FFD166"))
    p.append(rect(101, 102, 1, 1, "#FF9E4A"))
    p.append(rect(101, 100, 1, 2, "#F4E8D0"))
    p.append(rect(80, 112, 26, 1, "#24140C", opacity="0.5"))

    # ── floor plant ───────────────────────────────────────────────────────────
    p.append('<g class="sway">')
    p.append(rect(204, 146, 10, 14, "#8B4A2F"))
    p.append(rect(204, 146, 10, 1, "#B86A45"))
    p.append(rect(207, 140, 4, 6, "#2E7D4F"))
    p.append(rect(203, 138, 4, 4, "#3FA866"))
    p.append(rect(212, 136, 3, 6, "#4ADE80"))
    p.append(rect(206, 132, 3, 5, "#2E7D4F"))
    p.append(rect(200, 141, 4, 3, "#3FA866"))
    p.append(rect(213, 143, 4, 3, "#2E7D4F"))
    p.append("</g>")

    # ── character (back view, gaming) ─────────────────────────────────────────
    p.append('<g transform="translate(-12,0)">')
    # beanbag
    p.append(rect(12, 142, 34, 20, "#143A42"))
    p.append(rect(12, 142, 34, 2, "#2C6A72"))
    p.append(rect(14, 160, 30, 2, "#0A2024"))
    p.append(rect(10, 150, 4, 10, "#1B4A52"))
    p.append(rect(44, 150, 4, 10, "#1B4A52"))
    p.append(rect(16, 146, 3, 8, "#205A62", opacity="0.9"))
    p.append(rect(40, 146, 3, 8, "#205A62", opacity="0.9"))
    p.append(rect(12, 149, 34, 1, "#2C6A72", opacity="0.7"))
    p.append('<g class="char-bob">')
    # legs
    p.append(rect(18, 148, 9, 8, "#202A44"))
    p.append(rect(31, 148, 9, 8, "#202A44"))
    p.append(rect(16, 156, 11, 3, "#111827"))
    p.append(rect(31, 156, 11, 3, "#111827"))
    # hoodie body
    p.append(rect(17, 126, 26, 24, "#2B3A67"))
    p.append(rect(17, 126, 26, 2, "#3E4F82"))
    p.append(rect(20, 128, 20, 20, "#344577"))
    p.append(rect(19, 130, 3, 14, "#25345C"))
    p.append(rect(38, 130, 3, 14, "#25345C"))
    # rim light to separate the silhouette from the room
    p.append(rect(16, 128, 1, 18, "#5A6FA8"))
    p.append(rect(43, 128, 1, 18, "#5A6FA8"))
    # hood
    p.append(rect(21, 122, 18, 6, "#3E4F82"))
    p.append(rect(23, 120, 14, 4, "#2B3A67"))
    p.append(rect(20, 126, 20, 1, "#4A5C96"))
    p.append(rect(25, 128, 1, 4, "#A9B8D8"))
    p.append(rect(34, 128, 1, 4, "#A9B8D8"))
    p.append(rect(29, 128, 1, 18, "#25345C"))
    p.append(rect(24, 139, 12, 2, "#25345C"))
    # NM on back
    p.append(text(120, 556, "NM", 11, YELLOW, "middle", 700, 1.6))
    # arms resting on the beanbag
    p.append(rect(14, 134, 5, 10, "#2B3A67"))
    p.append(rect(41, 134, 5, 10, "#2B3A67"))
    p.append(rect(18, 142, 4, 3, "#E8B08A"))
    p.append(rect(38, 142, 4, 3, "#E8B08A"))
    # head (back view, hair + headphones)
    p.append(rect(27, 118, 6, 4, "#C98A66"))
    p.append(rect(21, 101, 18, 22, "#070A12"))
    p.append(rect(22, 102, 16, 20, "#24160F"))
    p.append(rect(24, 104, 12, 2, "#3A2418"))
    p.append(rect(22, 110, 2, 8, "#2E1B12"))
    p.append(rect(36, 110, 2, 8, "#2E1B12"))
    p.append(rect(25, 100, 10, 2, "#2E1B12"))
    p.append(rect(29, 119, 2, 2, "#C98A66"))
    # headphones
    p.append(rect(18, 104, 4, 12, "#FF3D8B"))
    p.append(rect(38, 104, 4, 12, "#FF3D8B"))
    p.append(rect(19, 106, 1, 6, "#FF9EC4"))
    p.append(rect(40, 106, 1, 6, "#FF9EC4"))
    p.append('<path d="M22 104 Q30 94 38 104" fill="none" stroke="#FF3D8B" stroke-width="2"/>')
    p.append(rect(20, 116, 2, 1, CYAN, cls="pulse"))
    # tiny floating music note by headphones
    p.append('<g class="note n2">' + rect(44, 98, 2, 1, CYAN) + rect(45, 95, 1, 4, CYAN) + "</g>")
    p.append("</g>")
    p.append("</g>")

    # game cartridge on the rug
    p.append(rect(56, 158, 8, 5, "#1B2636"))
    p.append(rect(57, 156, 6, 2, "#3A4A60"))
    p.append(rect(58, 159, 4, 2, PINK, opacity="0.8"))
    p.append(rect(57, 158, 6, 0.5, YELLOW))

    # ── arcade cabinet ────────────────────────────────────────────────────────
    p.append('<ellipse cx="1080" cy="648" rx="150" ry="22" fill="#000000" opacity="0.45"/>')
    p.append(rect(220, 70, 66, 90, "#231638"))
    p.append(rect(220, 70, 66, 2, "#3B2458"))
    p.append(rect(220, 70, 2, 90, "#3B2458"))
    p.append(rect(284, 70, 2, 90, "#140C24"))
    p.append(rect(222, 158, 62, 4, "#120A1E"))
    # side edges
    p.append(rect(221, 90, 4, 62, "#2E1740"))
    p.append(rect(283, 90, 2, 62, "#2E1740"))
    p.append(rect(282, 100, 2, 4, PINK, opacity="0.6"))
    p.append(rect(282, 108, 2, 4, CYAN, opacity="0.6"))
    # marquee
    p.append(rect(224, 74, 58, 12, "#0D0818"))
    p.append(rect(225, 75, 56, 10, "#2A1140"))
    p.append(rect(225, 75, 56, 1, PINK, opacity="0.8"))
    p.append(text(1080, 336, "PAC-MAN", 13, YELLOW, "middle", 700, 3))
    # screen bezel
    p.append(rect(226, 88, 54, 34, "#090611"))
    p.append(rect(228, 90, 50, 30, "#120A1E"))
    p.append(rect(230, 92, 46, 26, "#050B10"))
    # mini maze
    p.append(rect(232, 94, 42, 0.5, "#1B4A8A"))
    p.append(rect(232, 118, 42, 0.5, "#1B4A8A"))
    p.append(rect(232, 94, 0.5, 24, "#1B4A8A"))
    p.append(rect(273, 94, 0.5, 24, "#1B4A8A"))
    p.append(rect(244, 94, 0.5, 8, "#1B4A8A"))
    p.append(rect(260, 94, 0.5, 8, "#1B4A8A"))
    p.append(rect(244, 110, 0.5, 8, "#1B4A8A"))
    p.append(rect(260, 110, 0.5, 8, "#1B4A8A"))
    p.append(rect(232, 102, 8, 0.5, "#1B4A8A"))
    p.append(rect(264, 102, 8, 0.5, "#1B4A8A"))
    # pellets
    for i in range(12):
        p.append(rect(234 + i * 3.4, 100, 0.8, 0.8, "#FFE9A8"))
        p.append(rect(234 + i * 3.4, 113, 0.8, 0.8, "#FFE9A8"))
    # pac + ghosts inside screen
    p.append('<g class="pac-run">' + pacman(234, 105, YELLOW, 1) + "</g>")
    p.append(ghost(252, 106, PINK, 1, cls="ghost-bob g2"))
    p.append(ghost(260, 106, CYAN, 1, cls="ghost-bob g3"))
    p.append(ghost(268, 106, "#FF9E4A", 1, cls="ghost-bob"))
    # screen glow + scanline
    p.append(rect(230, 92, 46, 26, CYAN, opacity="0.07", cls="cab-glow"))
    p.append(rect(230, 118, 46, 0.5, CYAN, opacity="0.35"))
    # control panel
    p.append(rect(224, 122, 58, 12, "#160E26"))
    p.append(rect(224, 122, 58, 1, "#4A2E70"))
    p.append(rect(230, 124, 2, 4, "#3A4A60"))
    p.append(rect(229, 123, 4, 3, "#E63946"))
    p.append(rect(239, 126, 2, 2, YELLOW))
    p.append(rect(244, 126, 2, 2, PINK))
    p.append(rect(249, 126, 2, 2, CYAN))
    p.append(rect(236, 125, 1, 1, "#FFFFFF"))
    # coin door
    p.append(rect(236, 138, 34, 16, "#0D0818"))
    p.append(rect(238, 140, 30, 12, "#1B1128"))
    p.append(rect(240, 143, 4, 6, "#0A0C12"))
    p.append(rect(256, 143, 4, 6, "#0A0C12"))
    p.append(rect(241, 144, 2, 1, "#FFD166", cls="pulse"))
    p.append(rect(257, 144, 2, 1, "#FFD166", cls="pulse"))
    p.append(rect(244, 150, 14, 1, "#3A2458"))
    p.append(text(1080, 630, "INSERT COIN", 6.5, PINK, "middle", 700, 1.2, cls="blink slow"))
    # base + speaker grille
    p.append(rect(222, 154, 62, 4, "#0E0818"))
    for i in range(9):
        p.append(rect(230 + i * 4, 156, 2, 1, "#2A1A3C"))
    p.append(rect(282, 126, 2, 2, "#4ADE80", cls="pulse"))

    # ── arcade light spill ────────────────────────────────────────────────────
    p.append('<ellipse cx="1100" cy="560" rx="140" ry="60" fill="url(#cabinetGlow)" opacity="0.5"/>')

    # ── top bar ───────────────────────────────────────────────────────────────
    p.append(rect(0, 0, 300, 12, "#080C14"))
    p.append(rect(0, 12, 300, 0.5, "#22304A"))
    p.append(text(24, 33, "NICOLÁS.OS", 13, CYAN, "start", 700, 2.4))
    p.append(srect(148, 20, 10, 10, YELLOW))
    p.append(srect(161, 20, 10, 10, PINK))
    p.append(srect(174, 20, 10, 10, CYAN))
    menus = [(206, "PERFIL"), (270, "MÚSICA"), (342, "JUEGOS"), (414, "CÓDIGO")]
    for mx, label in menus:
        p.append(text(mx, 30, label, 7.5, MUTED, "start", 400, 1.4))
    p.append(srect(206, 40, 38, 2, CYAN))
    p.append(text(806, 30, "RÉCORD 0020", 7.5, YELLOW, "start", 700, 1.6))
    p.append(srect(1012, 23, 3, 3, "#4ADE80", cls="pulse"))
    p.append(text(1022, 30, "EN LÍNEA", 7.5, "#4ADE80", "start", 400, 1.4))
    p.append(text(1172, 30, "BOGOTÁ, CO", 7.5, "#70A5FD", "end", 400, 1.4))
    p.append(srect(0, 46, 1200, 2, "url(#neonGrad)", opacity="0.35"))

    # ── bottom bar ────────────────────────────────────────────────────────────
    p.append(rect(0, 165, 300, 10, "#080C14"))
    p.append(srect(0, 660, 1200, 2, "#22304A"))
    p.append(srect(0, 660, 1200, 2, "url(#neonGrad)", opacity="0.5"))
    p.append(srect(96, 678, 3, 3, "#4ADE80", cls="pulse"))
    p.append(text(108, 686, "EN LÍNEA", 9, "#4ADE80", "start", 400, 1.3))
    for dx in (196, 310, 460, 590):
        p.append(srect(dx, 670, 1, 22, "#1B2636"))
    p.append(text(212, 686, "20 AÑOS", 9, MUTED, "start", 400, 1.3))
    p.append(text(326, 686, "3ER SEMESTRE", 9, MUTED, "start", 400, 1.3))
    p.append(text(476, 686, "BOGOTÁ, CO", 9, MUTED, "start", 400, 1.3))
    p.append(text(610, 686, "VIDEOJUEGOS · MÚSICA · IA · VIBE CODING · CIBERSEGURIDAD · DISEÑO", 8.5, "#70A5FD", "start", 400, 1.1))
    p.append(text(1176, 686, "MOTOR DEL PERFIL", 9, MAGENTA, "end", 400, 1.3))

    # ── CRT overlay / vignette ────────────────────────────────────────────────
    p.append(rect(0, 0, 300, 175, "url(#scan)", opacity="0.55"))
    p.append('<rect width="1200" height="700" fill="none" stroke="#22304A" stroke-width="2"/>')
    p.append('<path d="M2 40V2h38M1160 2h38v38M2 660v38h38M1198 660v38h-38" fill="none" stroke="#00F7FF" stroke-opacity="0.32" stroke-width="2"/>')
    p.append('<radialGradient id="vig" cx="0.5" cy="0.5" r="0.72"><stop offset="0.55" stop-color="#000000" stop-opacity="0"/><stop offset="1" stop-color="#000000" stop-opacity="0.42"/></radialGradient>')
    p.append('<rect width="1200" height="700" fill="url(#vig)" pointer-events="none"/>')

    p.append("</svg>")
    return "\n".join(p)


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes)")
