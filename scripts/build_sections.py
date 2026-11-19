#!/usr/bin/env python3
"""Generate the pixel-art section ribbons and the profile footer."""
from __future__ import annotations

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

W = 1200
FONT = '"Cascadia Mono", "Consolas", "Courier New", monospace'

PANEL = "#0B1220"
BORDER = "#22304A"
CREAM = "#F4E8D0"
MUTED = "#8B98AB"
DIM = "#4F6079"
CYAN = "#00F7FF"
PINK = "#FF3D8B"
YELLOW = "#FFD166"
BLUE = "#70A5FD"
GREEN = "#4ADE80"

PAC = [
    "..###..",
    ".#####.",
    "###....",
    "##.....",
    "###....",
    ".#####.",
    "..###..",
]


def rect(x, y, w, h, fill, opacity=None, stroke=None, stroke_width=1, cls=None):
    attrs = [f'x="{x:g}"', f'y="{y:g}"', f'width="{w:g}"', f'height="{h:g}"', f'fill="{fill}"']
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    if cls:
        attrs.append(f'class="{cls}"')
    if stroke:
        attrs.append(f'stroke="{stroke}"')
        attrs.append(f'stroke-width="{stroke_width:g}"')
    return f'<rect {" ".join(attrs)}/>'


def text(x, y, content, size=12, fill=CREAM, anchor="start", weight=400, spacing=0, cls=None):
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
    return f'<text {" ".join(attrs)}>{content}</text>'


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


def defs(height: int, suffix: str) -> str:
    return (
        "<defs>"
        f'<linearGradient id="bg{suffix}" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#0C1424"/><stop offset="0.55" stop-color="#090D17"/>'
        '<stop offset="1" stop-color="#120C1A"/></linearGradient>'
        f'<linearGradient id="neon{suffix}" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{CYAN}"/><stop offset="0.5" stop-color="{BLUE}"/>'
        f'<stop offset="1" stop-color="{PINK}"/></linearGradient>'
        f'<pattern id="dots{suffix}" width="24" height="24" patternUnits="userSpaceOnUse">'
        '<circle cx="1" cy="1" r="1" fill="#22304A" opacity="0.4"/></pattern>'
        "</defs>"
    )


def section(index: str, title: str, subtitle: str, color: str, suffix: str) -> str:
    h = 84
    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" '
        f'role="img" aria-label="{title}" shape-rendering="crispEdges">',
        defs(h, suffix),
        rect(0, 0, W, h, f"url(#bg{suffix})"),
        rect(0, 0, W, h, f"url(#dots{suffix})"),
        rect(0, 0, W, h, "none", stroke=BORDER),
        rect(0, 0, 6, h, color),
        rect(6, 0, 2, h, "url(#neon" + suffix + ")", opacity="0.6"),
        # index badge
        rect(26, 22, 42, 30, "#080C14"),
        rect(26, 22, 42, 30, "none", stroke=color, stroke_width=1),
        text(47, 42, index, 13, color, "middle", 700, 1.2),
        # title + subtitle
        text(86, 42, title, 19, CREAM, "start", 700, 4.2),
        text(86, 62, subtitle, 10, MUTED, "start", 400, 1.6),
        # right module label
        text(1174, 38, "MÓDULO " + index, 8, MUTED, "end", 700, 1.8),
        text(1174, 55, "NICOLÁS.OS", 7.5, DIM, "end", 400, 1.4),
        # pac + dots
        sprite(PAC, 1050, 46, 2, color),
        rect(1080, 55, 3, 3, color, opacity="0.8"),
        rect(1092, 55, 3, 3, color, opacity="0.6"),
        rect(1104, 55, 3, 3, color, opacity="0.4"),
        # bottom accent
        line(0, h - 1, W, h - 1, BORDER),
        rect(86, h - 1, 120, 1, color, opacity="0.8"),
        '<path d="M1140 74v10h10M1140 74h-10" fill="none" stroke="' + color + '" stroke-opacity="0.5" stroke-width="1"/>',
        "</svg>",
    ]
    return "\n".join(p)


def footer() -> str:
    h = 150
    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" '
        'role="img" aria-label="Gracias por jugar" shape-rendering="crispEdges">',
        defs(h, "F"),
        rect(0, 0, W, h, "url(#bgF)"),
        rect(0, 0, W, h, "url(#dotsF)"),
        rect(0, 0, W, h, "none", stroke=BORDER),
        line(0, 0, W, 0, "url(#neonF)", 2, 0.7),
        '<path d="M0 26V0h26M1174 0h26v26M0 124v26h26M1200 124v26h-26" '
        f'fill="none" stroke="{CYAN}" stroke-opacity="0.4" stroke-width="2"/>',
        # title
        text(600, 52, "GRACIAS POR JUGAR", 22, CREAM, "middle", 700, 5.0),
        text(600, 72, "SIGUE APRENDIENDO · SIGUE CONSTRUYENDO · SIGUE JUGANDO", 10, MUTED, "middle", 400, 1.4),
        line(470, 86, 730, 86, BORDER),
        rect(560, 86, 80, 1, PINK, opacity="0.8"),
        # left pac-man
        sprite(PAC, 54, 54, 3, YELLOW),
        rect(92, 66, 5, 5, YELLOW, opacity="0.8"),
        rect(110, 66, 5, 5, YELLOW, opacity="0.6"),
        rect(128, 66, 5, 5, YELLOW, opacity="0.4"),
        # right coin slot
        rect(1030, 44, 112, 46, "#080C14"),
        rect(1030, 44, 112, 46, "none", stroke=YELLOW, stroke_width=1),
        text(1086, 64, "INSERTA MONEDA", 10, YELLOW, "middle", 700, 0.8, cls="blinkF"),
        text(1086, 80, "PARA CONTINUAR", 9, MUTED, "middle", 400, 1.0),
        # bottom line
        line(32, 112, 1168, 112, "#1B2A44"),
        rect(32, 124, 3, 3, GREEN, cls="pulseF"),
        text(42, 132, "BOGOTÁ, COLOMBIA · UTC-5", 9, MUTED, "start", 400, 0.8),
        text(600, 132, "HECHO CON PYTHON, SVG Y GITHUB ACTIONS", 9, MUTED, "middle", 400, 0.8),
        text(1168, 132, "NICOLÁS.OS", 9, PINK, "end", 700, 0.8),
        "<style>"
        ".blinkF{animation:blinkF 1.2s steps(1,end) infinite}"
        ".pulseF{animation:pulseF 2s ease-in-out infinite}"
        "@keyframes blinkF{0%,49%{opacity:1}50%,100%{opacity:.15}}"
        "@keyframes pulseF{0%,100%{opacity:.35}50%{opacity:1}}"
        "@media (prefers-reduced-motion:reduce){.blinkF,.pulseF{animation:none!important}}"
        "</style>",
        "</svg>",
    ]
    return "\n".join(p)


def main() -> None:
    outputs = {
        "section-about.svg": section("01", "SOBRE MÍ", "QUIÉN ESTÁ DETRÁS DEL PERFIL", CYAN, "A"),
        "section-contributions.svg": section("02", "CONTRIBUCIONES", "DATOS REALES · SIN RELLENO", PINK, "C"),
        "section-lab.svg": section("03", "LABORATORIO", "LO QUE ESTOY CONSTRUYENDO", YELLOW, "L"),
        "footer.svg": footer(),
    }
    for name, svg in outputs.items():
        path = ASSETS / name
        path.write_text(svg, encoding="utf-8")
        print(f"wrote {path} ({path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
