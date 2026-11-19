#!/usr/bin/env python3
"""Wrap the Platane/snk contribution snake in a pixel-art profile frame.

Usage:
    python scripts/build_snake_frame.py dist/github-contribution-grid-snake-dark.svg
"""
from __future__ import annotations

import argparse
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "contribution-snake.svg"

W, H = 1200, 400
FONT = '"Cascadia Mono", "Consolas", "Courier New", monospace'

PANEL = "#0B1220"
BORDER = "#22304A"
BORDER_DIM = "#1B2A44"
CREAM = "#F4E8D0"
MUTED = "#8B98AB"
DIM = "#4F6079"
CYAN = "#00F7FF"
PINK = "#FF3D8B"
YELLOW = "#FFD166"
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

PALETTE = {
    "cb": "#1B2A44",
    "cs": "#00F7FF",
    "ce": "#0F1726",
    "c0": "#1E6E7A",
    "c1": "#00A8B8",
    "c2": "#FFD166",
    "c3": "#FF9E4A",
    "c4": "#FFD166",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def rect(x, y, w, h, fill, opacity=None, stroke=None, stroke_width=1, rx=0):
    attrs = [f'x="{x:g}"', f'y="{y:g}"', f'width="{w:g}"', f'height="{h:g}"', f'fill="{fill}"']
    if rx:
        attrs.append(f'rx="{rx:g}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
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


def extract(svg: str) -> tuple[str, str]:
    match = re.search(r"<svg\b([^>]*)>(.*)</svg>\s*$", svg, re.S)
    if not match:
        raise SystemExit("input is not a standalone SVG")
    attrs, inner = match.group(1), match.group(2)
    vb = re.search(r'viewBox="([^"]+)"', attrs)
    view_box = vb.group(1) if vb else "0 0 880 192"
    return view_box, inner


def recolor(inner: str) -> str:
    inner = inner.replace(":root{", ".snake-root{")
    for var, value in PALETTE.items():
        inner = re.sub(rf"--{var}:[^;}}]+", f"--{var}:{value}", inner)
    inner = inner.replace(
        "</style>",
        "@media (prefers-reduced-motion:reduce){.c,.u,.s{animation:none!important}}</style>",
        1,
    )
    return inner


def build(snake_path: pathlib.Path) -> str:
    source = snake_path.read_text(encoding="utf-8")
    view_box, inner = extract(source)
    inner = recolor(inner)

    p: list[str] = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
             'role="img" aria-labelledby="snTitle snDesc" shape-rendering="crispEdges">')
    p.append('<title id="snTitle">Serpiente de contribuciones de Nicolás Moncada Montaño</title>')
    p.append('<desc id="snDesc">La serpiente recorre el calendario real de contribuciones de GitHub. '
             'Los colores siguen la paleta Pac-Man del perfil.</desc>')
    p.append("<defs>")
    p.append('<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
             '<stop offset="0" stop-color="#0C1424"/><stop offset="0.55" stop-color="#090D17"/>'
             '<stop offset="1" stop-color="#140C1C"/></linearGradient>')
    p.append('<linearGradient id="neon" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0" stop-color="{CYAN}"/><stop offset="0.5" stop-color="#70A5FD"/>'
             f'<stop offset="1" stop-color="{PINK}"/></linearGradient>')
    p.append('<pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">'
             '<circle cx="1" cy="1" r="1" fill="#22304A" opacity="0.4"/></pattern>')
    p.append("</defs>")

    p.append(rect(0, 0, W, H, "url(#bg)"))
    p.append(rect(0, 0, W, H, "url(#dots)"))
    p.append(rect(0, 0, W, H, "none", stroke=BORDER, stroke_width=2))
    p.append('<path d="M0 26V0h26M1174 0h26v26M0 374v26h26M1200 374v26h-26" '
             f'fill="none" stroke="{CYAN}" stroke-opacity="0.4" stroke-width="2"/>')

    # top bar
    p.append(rect(0, 0, W, 64, "#080C14", opacity="0.88"))
    p.append(line(0, 64, W, 64, BORDER))
    p.append(line(0, 64, W, 64, "url(#neon)", 1, 0.5))
    p.append(rect(24, 24, 8, 8, YELLOW))
    p.append(rect(38, 24, 8, 8, PINK))
    p.append(rect(52, 24, 8, 8, CYAN))
    p.append(text(78, 38, "SERPIENTE DE CONTRIBUCIONES", 15, CREAM, "start", 700, 2.8))
    p.append(text(78, 53, "PLATANE / SNK · DATOS REALES · PALETA PAC-MAN", 9, MUTED, "start", 400, 1.4))
    p.append(rect(1006, 25, 3, 3, GREEN))
    p.append(text(1018, 34, "AUTOMÁTICA", 9, GREEN, "start", 700, 1.4))
    p.append(text(1168, 50, "CADA 8 HORAS", 8, DIM, "end", 400, 1.2))

    # snake panel
    p.append(rect(24, 72, 1152, 280, PANEL, opacity="0.82"))
    p.append(rect(24, 72, 1152, 280, "none", stroke=BORDER, stroke_width=1))
    p.append(rect(24, 72, 1152, 2, "url(#neon)", opacity="0.55"))
    p.append('<path d="M24 96V72h24M1176 96V72h-24M24 328v24h24M1176 328v24h-24" '
             f'fill="none" stroke="{CYAN}" stroke-opacity="0.45" stroke-width="2"/>')
    p.append(text(40, 90, "ÚLTIMOS 12 MESES", 8, MUTED, "start", 700, 1.6))
    p.append(text(1160, 90, "GRID 53 × 7", 8, MUTED, "end", 700, 1.6))

    # the real snake, embedded and isolated by the .snake-root scope
    p.append(f'<svg x="40" y="98" width="1120" height="244.36" viewBox="{view_box}" '
             'preserveAspectRatio="xMidYMid meet">')
    p.append('<g class="snake-root">')
    p.append(inner)
    p.append("</g>")
    p.append("</svg>")

    # footer
    p.append(line(24, 356, 1176, 356, BORDER_DIM))
    p.append(sprite(PAC, 32, 366, 2, YELLOW))
    p.append(text(60, 378, "CADA CÉLULA ES UN DÍA · LA SERPIENTE RECORRE TU ACTIVIDAD REAL", 8, MUTED, "start", 400, 0.8))
    p.append(text(1168, 378, "NICOLÁS.OS · SNAKE v4.0", 8, PINK, "end", 700, 0.8))

    p.append(rect(0, 0, W, H, "none", stroke="#2A3A54", stroke_width=1))
    p.append("</svg>")
    return "\n".join(p)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("snake", nargs="?", default="dist/github-contribution-grid-snake-dark.svg")
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args()

    snake = pathlib.Path(args.snake)
    if not snake.exists():
        raise SystemExit(f"snake SVG not found: {snake} (run Platane/snk first)")
    svg = build(snake)
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
