#!/usr/bin/env python3
"""Central 16-bit / Arcade Design System for Nicolás Moncada's GitHub Profile.

Provides:
- Dual native palettes: Midnight Arcade (dark) and Retro Cartridge (light)
- Pixel-dithered <pattern> backdrops, subtle CRT scanlines, dark-mode neon glow
- RPG chamfered pixel frames with solid 4px offset shadows
- Self-contained 5x7 (+ accent header) SVG pixel bitmap font (ASCII + Spanish)
- Run-length compressed pixel sprites and 8-bit segmented progress bars
"""
from __future__ import annotations

import html
import json
import pathlib
from dataclasses import dataclass
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
CONFIG_PATH = ROOT / "profile.config.json"

MONO_FONT = "ui-monospace, 'Cascadia Code', 'Fira Code', 'Consolas', monospace"

REDUCED_MOTION_CSS = (
    "@media (prefers-reduced-motion: reduce) {"
    " * { animation: none !important; transition: none !important; }"
    " }"
)

# ---------------------------------------------------------------------------
# Color Palette Model
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Palette:
    mode: str
    is_dark: bool
    bg: str
    bg_deep: str
    card: str
    card_alt: str
    border: str
    border_hi: str
    cyan: str
    magenta: str
    amber: str
    green: str
    blue: str
    purple: str
    text: str
    text_muted: str
    text_dim: str
    shadow: str
    heat: tuple[str, ...]
    scan_color: str
    scan_opacity: float

    def accent(self, name: str) -> str:
        mapping = {
            "cyan": self.cyan,
            "magenta": self.magenta,
            "amber": self.amber,
            "green": self.green,
            "blue": self.blue,
            "purple": self.purple,
        }
        return mapping.get(name, self.cyan)


def load_config(path: pathlib.Path = CONFIG_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def get_palette(config: dict[str, Any], mode: str) -> Palette:
    if mode not in ("dark", "light"):
        raise ValueError(f"Unsupported theme mode: {mode}")
    raw = config["palettes"][mode]
    is_dark = mode == "dark"
    return Palette(
        mode=mode,
        is_dark=is_dark,
        bg=raw["bg"],
        bg_deep=raw["bg_deep"],
        card=raw["card"],
        card_alt=raw["card_alt"],
        border=raw["border"],
        border_hi=raw["border_hi"],
        cyan=raw["cyan"],
        magenta=raw["magenta"],
        amber=raw["amber"],
        green=raw["green"],
        blue=raw["blue"],
        purple=raw["purple"],
        text=raw["text"],
        text_muted=raw["text_muted"],
        text_dim=raw["text_dim"],
        shadow=raw["shadow"],
        heat=tuple(raw["heat"]),
        scan_color="#FFFFFF" if is_dark else "#1E2433",
        scan_opacity=0.065 if is_dark else 0.03,
    )


def language_accent(lang: str, pal: Palette) -> str:
    key = (lang or "").strip().lower()
    if key in ("python",):
        return pal.cyan
    if key in ("javascript", "typescript"):
        return pal.amber
    if key in ("php", "ruby"):
        return pal.purple
    if key in ("html", "css", "scss"):
        return pal.magenta
    if key in ("c", "c++", "rust", "go", "shell"):
        return pal.green
    return pal.blue


# ---------------------------------------------------------------------------
# XML / SVG Core Primitives
# ---------------------------------------------------------------------------

def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def svg_open(
    w: int,
    h: int,
    title_id: str,
    title: str,
    desc_id: str,
    desc: str,
    *,
    crisp: bool = False,
) -> str:
    attrs = [
        'xmlns="http://www.w3.org/2000/svg"',
        f'viewBox="0 0 {w} {h}"',
        'width="100%"',
        'role="img"',
        f'aria-labelledby="{esc(title_id)} {esc(desc_id)}"',
    ]
    if crisp:
        attrs.append('shape-rendering="crispEdges"')
    return (
        f'<svg {" ".join(attrs)}>\n'
        f'<title id="{esc(title_id)}">{esc(title)}</title>\n'
        f'<desc id="{esc(desc_id)}">{esc(desc)}</desc>'
    )


def rect(
    x: float,
    y: float,
    w: float,
    h: float,
    fill: str,
    *,
    opacity: float | None = None,
    stroke: str | None = None,
    stroke_width: float = 1,
    cls: str | None = None,
    rx: float = 0,
    crisp: bool = False,
    style: str | None = None,
) -> str:
    attrs = [
        f'x="{x:g}"',
        f'y="{y:g}"',
        f'width="{w:g}"',
        f'height="{h:g}"',
        f'fill="{fill}"',
    ]
    if rx:
        attrs.append(f'rx="{rx:g}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity:g}"')
    if stroke:
        attrs.append(f'stroke="{stroke}"')
        attrs.append(f'stroke-width="{stroke_width:g}"')
    if cls:
        attrs.append(f'class="{cls}"')
    if crisp:
        attrs.append('shape-rendering="crispEdges"')
    if style:
        attrs.append(f'style="{style}"')
    return f'<rect {" ".join(attrs)}/>'


def line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    stroke: str,
    *,
    width: float = 1,
    opacity: float | None = None,
    cls: str | None = None,
) -> str:
    attrs = [
        f'x1="{x1:g}"',
        f'y1="{y1:g}"',
        f'x2="{x2:g}"',
        f'y2="{y2:g}"',
        f'stroke="{stroke}"',
        f'stroke-width="{width:g}"',
    ]
    if opacity is not None:
        attrs.append(f'opacity="{opacity:g}"')
    if cls:
        attrs.append(f'class="{cls}"')
    return f'<line {" ".join(attrs)}/>'


def mono_text(
    x: float,
    y: float,
    content: str,
    *,
    size: float = 13,
    fill: str = "#E6EDF3",
    anchor: str = "start",
    weight: int = 400,
    spacing: float = 0,
    cls: str | None = None,
    opacity: float | None = None,
) -> str:
    attrs = [
        f'x="{x:g}"',
        f'y="{y:g}"',
        f'font-size="{size:g}"',
        f'fill="{fill}"',
        f'text-anchor="{anchor}"',
        f'font-family="{esc(MONO_FONT)}"',
    ]
    if weight != 400:
        attrs.append(f'font-weight="{weight}"')
    if spacing:
        attrs.append(f'letter-spacing="{spacing:g}"')
    if cls:
        attrs.append(f'class="{cls}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity:g}"')
    return f'<text {" ".join(attrs)}>{esc(content)}</text>'


# ---------------------------------------------------------------------------
# Dithering Patterns, Scanlines, and RPG Chamfered Frames
# ---------------------------------------------------------------------------

def pattern_checker(pid: str, c1: str, c2: str, cell: int = 4) -> str:
    """2x2 pixel checkerboard dither pattern on strict grid."""
    s = cell * 2
    return (
        f'<pattern id="{pid}" width="{s}" height="{s}" patternUnits="userSpaceOnUse">'
        f'<rect width="{s}" height="{s}" fill="{c1}"/>'
        f'<rect x="0" y="0" width="{cell}" height="{cell}" fill="{c2}"/>'
        f'<rect x="{cell}" y="{cell}" width="{cell}" height="{cell}" fill="{c2}"/>'
        "</pattern>"
    )


def pattern_bayer25(pid: str, base: str, dot: str, cell: int = 4) -> str:
    """25% density 2x2 pixel dither pattern."""
    s = cell * 2
    return (
        f'<pattern id="{pid}" width="{s}" height="{s}" patternUnits="userSpaceOnUse">'
        f'<rect width="{s}" height="{s}" fill="{base}"/>'
        f'<rect x="0" y="0" width="{cell}" height="{cell}" fill="{dot}"/>'
        "</pattern>"
    )


def pattern_scanlines(pid: str, pal: Palette) -> str:
    return (
        f'<pattern id="{pid}" width="4" height="4" patternUnits="userSpaceOnUse">'
        f'<rect width="4" height="2" fill="{pal.scan_color}" opacity="{pal.scan_opacity}"/>'
        "</pattern>"
    )


def glow_filter(fid: str, std_dev: float = 3.2) -> str:
    return (
        f'<filter id="{fid}" x="-25%" y="-25%" width="150%" height="150%">'
        f'<feGaussianBlur stdDeviation="{std_dev:g}" result="glow"/>'
        '<feMerge><feMergeNode in="glow"/><feMergeNode in="SourceGraphic"/></feMerge>'
        "</filter>"
    )


def chamfer_path(x: float, y: float, w: float, h: float, c: float = 8) -> str:
    """Stepped 16-bit pixel chamfered polygon path."""
    if c <= 0:
        return f"M{x:g} {y:g}H{x+w:g}V{y+h:g}H{x:g}Z"
    s = c / 2
    return (
        f"M{x+c:g} {y:g} H{x+w-c:g} "
        f"V{y+s:g} H{x+w-s:g} V{y+c:g} H{x+w:g} "
        f"V{y+h-c:g} H{x+w-s:g} V{y+h-s:g} H{x+w-c:g} V{y+h:g} "
        f"H{x+c:g} V{y+h-s:g} H{x+s:g} V{y+h-c:g} H{x:g} "
        f"V{y+c:g} H{x+s:g} V{y+s:g} H{x+c:g} Z"
    )


def rpg_panel(
    x: float,
    y: float,
    w: float,
    h: float,
    pal: Palette,
    *,
    accent: str | None = None,
    chamfer: float = 8,
    shadow: float = 4,
    fill: str | None = None,
    top_strip: bool = True,
) -> str:
    """Render an authentic 16-bit RPG dialog panel with solid 4px shadow and double pixel frame."""
    acc = accent or pal.cyan
    bg = fill or pal.card
    out: list[str] = ['<g shape-rendering="crispEdges">']
    if shadow > 0:
        out.append(
            f'<path d="{chamfer_path(x + shadow, y + shadow, w, h, chamfer)}" '
            f'fill="{pal.shadow}" opacity="{"0.85" if pal.is_dark else "0.9"}"/>'
        )
    out.append(
        f'<path d="{chamfer_path(x, y, w, h, chamfer)}" '
        f'fill="{bg}" stroke="{pal.border}" stroke-width="2"/>'
    )
    if w > 24 and h > 24:
        out.append(
            f'<path d="{chamfer_path(x + 4, y + 4, w - 8, h - 8, max(4, chamfer - 4))}" '
            f'fill="none" stroke="{acc}" stroke-width="1" opacity="{"0.45" if pal.is_dark else "0.35"}"/>'
        )
    if top_strip and w > 40:
        out.append(rect(x + chamfer + 4, y + 2, w - 2 * (chamfer + 4), 3, acc, opacity=0.9))
    # Corner pixel rivets
    for rx, ry in (
        (x + chamfer, y + 4),
        (x + w - chamfer - 4, y + 4),
        (x + chamfer, y + h - 8),
        (x + w - chamfer - 4, y + h - 8),
    ):
        out.append(rect(rx, ry, 4, 4, acc, opacity=0.85))
    out.append("</g>")
    return "\n".join(out)


def segmented_bar(
    x: float,
    y: float,
    filled: int,
    total: int,
    color: str,
    pal: Palette,
    *,
    seg_w: int = 16,
    seg_h: int = 12,
    gap: int = 4,
) -> str:
    """8-bit segmented level meter with crisp pixel bevels."""
    empty_bg = "#1B2336" if pal.is_dark else "#E2DDD1"
    empty_border = pal.border if pal.is_dark else "#B8B1A2"
    out = ['<g shape-rendering="crispEdges">']
    for i in range(total):
        sx = x + i * (seg_w + gap)
        if i < filled:
            out.append(rect(sx, y, seg_w, seg_h, color))
            out.append(rect(sx, y, seg_w, 3, "#FFFFFF", opacity=0.28 if pal.is_dark else 0.35))
            out.append(rect(sx, y + seg_h - 2, seg_w, 2, "#000000", opacity=0.2))
        else:
            out.append(rect(sx, y, seg_w, seg_h, empty_bg, stroke=empty_border, stroke_width=1))
    out.append("</g>")
    return "".join(out)


def pixel_badge(
    x: float,
    y: float,
    label: str,
    color: str,
    pal: Palette,
    *,
    size: float = 11.5,
    pad_x: float = 10,
    height: float = 24,
) -> tuple[str, float]:
    """Crisp arcade pill/tag with left accent bar; returns (svg, width)."""
    w = max(56, round(pad_x * 2 + len(label) * (size * 0.63) + 6))
    bg = pal.bg_deep if pal.is_dark else pal.card_alt
    out = [
        '<g shape-rendering="crispEdges">',
        rect(x + 2, y + 2, w, height, pal.shadow, opacity=0.65),
        rect(x, y, w, height, bg, stroke=pal.border, stroke_width=1.5),
        rect(x + 1.5, y + 1.5, 4, height - 3, color),
        mono_text(x + pad_x + 4, y + height / 2 + size * 0.35, label, size=size, fill=color, weight=700, spacing=0.6),
        "</g>",
    ]
    return "".join(out), w


def pixel_sprite(
    x: float,
    y: float,
    rows: list[str],
    colors: dict[str, str | None],
    px: int = 4,
    *,
    cls: str | None = None,
) -> str:
    """Render a multi-color sprite with horizontal run-length merging."""
    out = [f'<g class="{cls}" shape-rendering="crispEdges">' if cls else '<g shape-rendering="crispEdges">']
    for ry, row in enumerate(rows):
        run_ch = None
        run_start = 0
        n = len(row)
        for rx in range(n + 1):
            ch = row[rx] if rx < n else None
            if ch != run_ch:
                if run_ch is not None and colors.get(run_ch):
                    out.append(
                        rect(
                            x + run_start * px,
                            y + ry * px,
                            (rx - run_start) * px,
                            px,
                            str(colors[run_ch]),
                        )
                    )
                run_ch = ch
                run_start = rx
    out.append("</g>")
    return "".join(out)


# ---------------------------------------------------------------------------
# 5x7 (+2 accent rows) Native SVG Pixel Bitmap Font (ASCII + Spanish)
# ---------------------------------------------------------------------------
# Each glyph has 9 rows of width 5 (rows 0-1: accent/tilde zone; rows 2-8: cap body).

_BLANK2 = [".....", "....."]

def _g(accent: list[str], body: list[str]) -> list[str]:
    return accent + body


GLYPHS: dict[str, list[str]] = {
    " ": _BLANK2 + ["....."] * 7,
    "A": _g(_BLANK2, [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"]),
    "B": _g(_BLANK2, ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."]),
    "C": _g(_BLANK2, [".####", "#....", "#....", "#....", "#....", "#....", ".####"]),
    "D": _g(_BLANK2, ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."]),
    "E": _g(_BLANK2, ["#####", "#....", "#....", "####.", "#....", "#....", "#####"]),
    "F": _g(_BLANK2, ["#####", "#....", "#....", "####.", "#....", "#....", "#...."]),
    "G": _g(_BLANK2, [".####", "#....", "#....", "#..##", "#...#", "#...#", ".####"]),
    "H": _g(_BLANK2, ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"]),
    "I": _g(_BLANK2, [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."]),
    "J": _g(_BLANK2, ["..###", "...#.", "...#.", "...#.", "#..#.", "#..#.", ".##.."]),
    "K": _g(_BLANK2, ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"]),
    "L": _g(_BLANK2, ["#....", "#....", "#....", "#....", "#....", "#....", "#####"]),
    "M": _g(_BLANK2, ["#...#", "##.##", "#.#.#", "#...#", "#...#", "#...#", "#...#"]),
    "N": _g(_BLANK2, ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"]),
    "O": _g(_BLANK2, [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."]),
    "P": _g(_BLANK2, ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."]),
    "Q": _g(_BLANK2, [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"]),
    "R": _g(_BLANK2, ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"]),
    "S": _g(_BLANK2, [".####", "#....", "#....", ".###.", "....#", "....#", "####."]),
    "T": _g(_BLANK2, ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."]),
    "U": _g(_BLANK2, ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."]),
    "V": _g(_BLANK2, ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."]),
    "W": _g(_BLANK2, ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"]),
    "X": _g(_BLANK2, ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"]),
    "Y": _g(_BLANK2, ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."]),
    "Z": _g(_BLANK2, ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"]),
    "0": _g(_BLANK2, [".###.", "#..##", "#.#.#", "#.#.#", "##..#", "#...#", ".###."]),
    "1": _g(_BLANK2, ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."]),
    "2": _g(_BLANK2, [".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"]),
    "3": _g(_BLANK2, ["####.", "....#", "....#", ".###.", "....#", "....#", "####."]),
    "4": _g(_BLANK2, ["#...#", "#...#", "#...#", "#####", "....#", "....#", "....#"]),
    "5": _g(_BLANK2, ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."]),
    "6": _g(_BLANK2, [".###.", "#....", "####.", "#...#", "#...#", "#...#", ".###."]),
    "7": _g(_BLANK2, ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."]),
    "8": _g(_BLANK2, [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."]),
    "9": _g(_BLANK2, [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."]),
    # Spanish accented uppercase
    "Á": _g(["...#.", "..#.."], [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"]),
    "É": _g(["...#.", "..#.."], ["#####", "#....", "#....", "####.", "#....", "#....", "#####"]),
    "Í": _g(["...#.", "..#.."], [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."]),
    "Ó": _g(["...#.", "..#.."], [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."]),
    "Ú": _g(["...#.", "..#.."], ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."]),
    "Ü": _g([".#.#.", "....."], ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."]),
    "Ñ": _g([".##.#", "#..#."], ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"]),
    # Punctuation & symbols
    "·": _g(_BLANK2, [".....", ".....", "..##.", "..##.", ".....", ".....", "....."]),
    ".": _g(_BLANK2, [".....", ".....", ".....", ".....", ".....", "..##.", "..##."]),
    ",": _g(_BLANK2, [".....", ".....", ".....", ".....", "..##.", "..#..", ".#..."]),
    ":": _g(_BLANK2, [".....", "..##.", "..##.", ".....", "..##.", "..##.", "....."]),
    "-": _g(_BLANK2, [".....", ".....", ".....", ".###.", ".....", ".....", "....."]),
    "+": _g(_BLANK2, [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."]),
    "/": _g(_BLANK2, ["....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."]),
    "_": _g(_BLANK2, [".....", ".....", ".....", ".....", ".....", ".....", "#####"]),
    "!": _g(_BLANK2, ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."]),
    "¡": _g(_BLANK2, ["..#..", ".....", "..#..", "..#..", "..#..", "..#..", "..#.."]),
    "?": _g(_BLANK2, [".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."]),
    "¿": _g(_BLANK2, ["..#..", ".....", "..#..", ".##..", "#....", "#...#", ".###."]),
    "&": _g(_BLANK2, [".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"]),
    ">": _g(_BLANK2, [".....", "#....", ".#...", "..#..", ".#...", "#....", "....."]),
    "<": _g(_BLANK2, [".....", "....#", "...#.", "..#..", "...#.", "....#", "....."]),
    "$": _g(_BLANK2, ["..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."]),
    "#": _g(_BLANK2, [".#.#.", "#####", ".#.#.", ".#.#.", "#####", ".#.#.", "....."]),
    "(": _g(_BLANK2, ["...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."]),
    ")": _g(_BLANK2, [".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."]),
    "@": _g(_BLANK2, [".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."]),
}


def _normalize_pixel_chars(text: str) -> str:
    # Map lowercase Spanish letters directly to uppercase bitmap glyphs
    lower_map = {"á": "Á", "é": "É", "í": "Í", "ó": "Ó", "ú": "Ú", "ü": "Ü", "ñ": "Ñ"}
    out = []
    for ch in text:
        if ch in lower_map:
            out.append(lower_map[ch])
        else:
            up = ch.upper()
            out.append(up if up in GLYPHS else " ")
    return "".join(out)


def measure_pixel_text(text: str, px: int = 4, letter_gap: int = 1) -> tuple[int, int]:
    """Return (width, height) in screen pixels for a pixel-font string."""
    norm = _normalize_pixel_chars(text)
    if not norm:
        return 0, 9 * px
    glyph_w = 5 * px
    step = glyph_w + letter_gap * px
    return len(norm) * step - letter_gap * px, 9 * px


def _build_pixel_path(norm: str, x0: float, y0: float, px: int, letter_gap: int) -> str:
    segs: list[str] = []
    step = (5 + letter_gap) * px
    for idx, ch in enumerate(norm):
        rows = GLYPHS[ch]
        gx = x0 + idx * step
        for ry, row in enumerate(rows):
            rx = 0
            while rx < 5:
                if row[rx] != "#":
                    rx += 1
                    continue
                run = 1
                while rx + run < 5 and row[rx + run] == "#":
                    run += 1
                sx = gx + rx * px
                sy = y0 + ry * px
                rw = run * px
                segs.append(f"M{sx:g} {sy:g}h{rw:g}v{px:g}h-{rw:g}z")
                rx += run
    return "".join(segs)


def pixel_text(
    x: float,
    y: float,
    text: str,
    *,
    px: int = 4,
    fill: str = "#E6EDF3",
    shadow: str | None = None,
    shadow_offset: int | None = None,
    anchor: str = "start",
    letter_gap: int = 1,
    cls: str | None = None,
    filter_id: str | None = None,
    opacity: float | None = None,
) -> str:
    """Render crisp native SVG pixel-grid display text (supports ASCII + Spanish).

    Note: `y` is the top-left of the 9-row glyph box (accent rows 0-1, cap rows 2-8).
    """
    norm = _normalize_pixel_chars(text)
    w, _ = measure_pixel_text(norm, px=px, letter_gap=letter_gap)
    if anchor == "middle":
        x0 = x - w / 2
    elif anchor == "end":
        x0 = x - w
    else:
        x0 = x

    d_main = _build_pixel_path(norm, x0, y, px, letter_gap)
    if not d_main:
        return ""

    parts: list[str] = ['<g shape-rendering="crispEdges">']
    if shadow:
        off = shadow_offset if shadow_offset is not None else max(2, px // 2)
        d_sh = _build_pixel_path(norm, x0 + off, y + off, px, letter_gap)
        parts.append(f'<path d="{d_sh}" fill="{shadow}"/>')

    attrs = [f'd="{d_main}"', f'fill="{fill}"']
    if cls:
        attrs.append(f'class="{cls}"')
    if filter_id:
        attrs.append(f'filter="url(#{filter_id})"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity:g}"')
    parts.append(f'<path {" ".join(attrs)}/>')
    parts.append("</g>")
    return "".join(parts)
