#!/usr/bin/env python3
"""Generate the RPG Character Sheet SVG (dark & light themes) from profile.config.json."""
from __future__ import annotations

import pathlib
from typing import Any

from design_system import (
    ASSETS,
    REDUCED_MOTION_CSS,
    Palette,
    get_palette,
    line,
    load_config,
    mono_text,
    pattern_bayer25,
    pattern_scanlines,
    pixel_badge,
    pixel_sprite,
    pixel_text,
    rect,
    rpg_panel,
    segmented_bar,
    svg_open,
)

W, H = 900, 480

# 16x16 crisp pixel-art developer character portrait (retro avatar with headphones)
AVATAR_ROWS = [
    "....########....",
    "..##HHHHHHHH##..",
    ".P#HHHHHHHHHH#P.",
    ".P#HSSSSSSSS##P.",
    "PP#HSSKSSKSS##PP",
    "PP#HSSSSSSSS##PP",
    ".P##SSSMMMSS##P.",
    ".P..#SSSSSS#..P.",
    ".....##SS##.....",
    "...##JJJJJJ##...",
    "..#JJJYYYYJJJ#..",
    ".#JJJCCCCCCJJJ#.",
    ".#JJJJJJJJJJJJ#.",
    ".#JJJ.JJJJ.JJJ#.",
    "..###......###..",
    "................",
]

MINI_ICONS: dict[str, list[str]] = {
    "ai": [
        ".#####.",
        "#..#..#",
        "#######",
        "#..#..#",
        ".#####.",
    ],
    "flow": [
        ".##....",
        "#..#...",
        ".##.##.",
        "...####",
        "....##.",
    ],
    "shield": [
        ".#####.",
        "#.....#",
        "#..#..#",
        ".#...#.",
        "..###..",
    ],
    "design": [
        ".#####.",
        "#..#..#",
        ".#####.",
        "...#...",
        "..#....",
    ],
    "code": [
        ".#...#.",
        "#.....#",
        ".#...#.",
        "..#.#..",
        "...#...",
    ],
    "db": [
        ".#####.",
        "#.....#",
        ".#####.",
        "#.....#",
        ".#####.",
    ],
}


def _build_player(config: dict[str, Any], mode: str) -> str:
    pal: Palette = get_palette(cfg := config, mode)
    prefix = f"pc_{mode}"
    display_name = cfg.get("display_name", "NICOLÁS")
    full_name = cfg.get("full_name", "Nicolás Moncada Montaño")
    role = cfg.get("role", "Estudiante de Ingeniería de Sistemas")
    semester = cfg.get("semester", "3er semestre · UNIMINUTO")
    location = cfg.get("location", "Bogotá, Colombia")
    age = cfg.get("age", 20)
    class_tag = cfg.get("class_tag", "SYS.ENG")
    attributes = list(cfg.get("attributes") or [])[:4]
    stack = list(cfg.get("stack") or [])[:6]
    interests = list(cfg.get("interests") or [])[:6]

    avatar_colors = {
        "#": "#0A0E17" if pal.is_dark else "#1E2433",
        "H": "#2C1B14",
        "S": "#E8B08A",
        "K": "#14141F",
        "M": "#9A4B3C",
        "P": pal.magenta,
        "J": "#2B3A67" if pal.is_dark else "#1D4ED8",
        "Y": pal.amber,
        "C": pal.cyan,
    }

    p: list[str] = [
        svg_open(
            W,
            H,
            f"{prefix}Title",
            f"Ficha de jugador de {full_name} ({mode})",
            f"{prefix}Desc",
            f"{role}, {semester}, {location}. Atributos, stack técnico cualitativo sin porcentajes inventados e intereses.",
        ),
        "<defs>",
        pattern_bayer25(f"{prefix}Bg", pal.bg, pal.bg_deep, cell=4),
        pattern_scanlines(f"{prefix}Scan", pal),
        "<style>",
        f"""
        .pc-pulse {{ animation: pcPulse 2.2s ease-in-out infinite; }}
        .pc-bob {{ animation: pcBob 4.5s ease-in-out infinite; }}
        @keyframes pcPulse {{ 0%,100%{{opacity:0.4}} 50%{{opacity:1}} }}
        @keyframes pcBob {{ 0%,100%{{transform:translateY(0)}} 50%{{transform:translateY(-4px)}} }}
        {REDUCED_MOTION_CSS}
        """,
        "</style>",
        "</defs>",
        rect(0, 0, W, H, f"url(#{prefix}Bg)", crisp=True),
        # Outer RPG Sheet Panel
        rpg_panel(8, 8, W - 20, H - 20, pal, accent=pal.cyan, chamfer=8, shadow=4),
        # Top Sheet Title Strip
        rect(20, 20, W - 44, 34, pal.bg_deep, stroke=pal.border, stroke_width=1.5, crisp=True),
        mono_text(34, 42, f"CHARACTER SHEET · {display_name}", size=13, fill=pal.cyan, weight=700, spacing=1.2),
        rect(734, 33, 8, 8, pal.green, cls="pc-pulse", crisp=True),
        mono_text(862, 42, f"CLASS: {class_tag}", size=12, fill=pal.green, anchor="end", weight=700, spacing=1.0),
    ]

    # ---- Left Column: Profile & Avatar (x=24..348, y=68..452) ----
    p.append(rpg_panel(24, 68, 324, 384, pal, accent=pal.magenta, chamfer=8, shadow=4, fill=pal.card_alt, top_strip=False))
    # Avatar Frame
    p.append(rect(44, 84, 284, 152, pal.bg_deep, stroke=pal.border, stroke_width=2, crisp=True))
    p.append(rect(44, 84, 284, 4, pal.magenta, crisp=True))
    p.append(mono_text(56, 106, "P1 · AVATAR", size=11, fill=pal.magenta, weight=700, spacing=1.0))
    p.append(mono_text(316, 106, f"LVL {age:02d}", size=11, fill=pal.amber, anchor="end", weight=700, spacing=1.0))
    p.append('<g class="pc-bob">')
    p.append(pixel_sprite(122, 104, AVATAR_ROWS, avatar_colors, px=8))
    p.append("</g>")

    # Profile Identity & Bio Summary
    p.append(pixel_text(44, 252, display_name, px=3, fill=pal.text, shadow=pal.cyan if not pal.is_dark else pal.bg_deep, shadow_offset=2))
    p.append(mono_text(44, 294, role, size=12.5, fill=pal.cyan, weight=700))
    p.append(mono_text(44, 314, semester, size=12, fill=pal.text_muted))
    p.append(mono_text(44, 334, f"{location} · {age} años", size=12, fill=pal.text_muted))
    p.append(line(44, 348, 328, 348, pal.border, width=1.5))
    p.append(mono_text(44, 368, "INTERESES CLAVE", size=11, fill=pal.amber, weight=700, spacing=1.0))

    # Interest Badges (2 rows of 3)
    ix, iy = 44, 378
    interest_accents = [pal.cyan, pal.magenta, pal.amber, pal.green, pal.purple, pal.blue]
    for idx, item in enumerate(interests):
        badge_svg, bw = pixel_badge(ix, iy, item.upper(), interest_accents[idx % len(interest_accents)], pal, size=10.5, pad_x=8, height=24)
        if ix + bw > 334:
            ix = 44
            iy += 30
            badge_svg, bw = pixel_badge(ix, iy, item.upper(), interest_accents[idx % len(interest_accents)], pal, size=10.5, pad_x=8, height=24)
        p.append(badge_svg)
        ix += bw + 8

    # ---- Right Column: Attributes + Segmented 8-Bit Stack (x=364..872, y=68..452) ----
    # Panel A: Attributes (y=68..224)
    p.append(rpg_panel(364, 68, 508, 156, pal, accent=pal.cyan, chamfer=8, shadow=4, fill=pal.card_alt, top_strip=False))
    p.append(mono_text(384, 92, "ATRIBUTOS & ENFOQUE", size=12, fill=pal.cyan, weight=700, spacing=1.2))
    p.append(mono_text(852, 92, "CLASE ACTIVA", size=11, fill=pal.text_dim, anchor="end", weight=700, spacing=1.0))
    p.append(line(384, 100, 852, 100, pal.border, width=1))

    ay = 112
    for idx, attr in enumerate(attributes):
        acc = pal.accent(attr.get("accent", "cyan"))
        ic = MINI_ICONS.get(attr.get("icon", "code"), MINI_ICONS["code"])
        if idx % 2 == 0:
            p.append(rect(382, ay - 4, 472, 24, pal.bg_deep, opacity=0.55, crisp=True))
        p.append(pixel_sprite(388, ay, ic, {"#": acc}, px=3))
        p.append(mono_text(418, ay + 12, attr["name"], size=12.5, fill=pal.text, weight=700))
        p.append(mono_text(528, ay + 12, attr["detail"], size=11, fill=pal.text_muted))
        p.append(mono_text(854, ay + 12, attr["level"], size=11, fill=acc, anchor="end", weight=700, spacing=0.7))
        ay += 27

    # Panel B: Stack with 8-bit Segmented Bars & Qualitative Levels (y=236..452)
    p.append(rpg_panel(364, 236, 508, 216, pal, accent=pal.amber, chamfer=8, shadow=4, fill=pal.card_alt, top_strip=False))
    p.append(mono_text(384, 260, "INVENTARIO & STACK TÉCNICO", size=12, fill=pal.amber, weight=700, spacing=1.2))
    p.append(mono_text(852, 260, "NIVEL CUALITATIVO", size=11, fill=pal.text_dim, anchor="end", weight=700, spacing=1.0))
    p.append(line(384, 268, 852, 268, pal.border, width=1))

    sy = 282
    for item in stack:
        acc = pal.accent(item.get("accent", "cyan"))
        ic = MINI_ICONS.get(item.get("icon", "code"), MINI_ICONS["code"])
        segs = max(1, min(8, int(item.get("segments", 3))))
        p.append(pixel_sprite(386, sy, ic, {"#": acc}, px=3))
        p.append(mono_text(416, sy + 12, item["name"], size=13, fill=pal.text, weight=700))
        p.append(segmented_bar(548, sy + 1, segs, 8, acc, pal, seg_w=16, seg_h=12, gap=4))
        p.append(mono_text(852, sy + 12, item["level"], size=11.5, fill=acc, anchor="end", weight=700, spacing=0.8))
        sy += 27

    p.append(rect(8, 8, W - 20, H - 20, f"url(#{prefix}Scan)", crisp=True))
    p.append("</svg>")
    return "\n".join(p)


def generate_player(config: dict[str, Any] | None = None) -> list[pathlib.Path]:
    cfg = config or load_config()
    ASSETS.mkdir(parents=True, exist_ok=True)
    written: list[pathlib.Path] = []
    for mode in ("dark", "light"):
        out = ASSETS / f"player-card-{mode}.svg"
        out.write_text(_build_player(cfg, mode), encoding="utf-8")
        written.append(out)
        print(f"wrote {out.name} ({out.stat().st_size:,} bytes)")
    return written


if __name__ == "__main__":
    generate_player()
