#!/usr/bin/env python3
"""Generate reusable 16-bit Stage Header banners (dark & light themes)."""
from __future__ import annotations

import pathlib
from typing import Any

from design_system import (
    ASSETS,
    REDUCED_MOTION_CSS,
    Palette,
    get_palette,
    load_config,
    mono_text,
    pattern_bayer25,
    pattern_scanlines,
    pixel_sprite,
    pixel_text,
    rect,
    rpg_panel,
    svg_open,
)

W, H = 900, 68

ICONS: dict[str, list[str]] = {
    "star": [
        "...#...",
        "...#...",
        "..###..",
        "#######",
        ".#####.",
        "..###..",
        ".##.##.",
    ],
    "sword": [
        ".....##",
        "....###",
        "...###.",
        ".#.##..",
        "..##...",
        ".#..#..",
        "#......",
    ],
    "flask": [
        "..###..",
        "...#...",
        "...#...",
        "..###..",
        ".#####.",
        "#######",
        ".#####.",
    ],
    "radar": [
        "..###..",
        ".#...#.",
        "#..#..#",
        "#.#.#.#",
        "#..#..#",
        ".#...#.",
        "..###..",
    ],
    "mail": [
        "#######",
        "##...##",
        "#.#.#.#",
        "#..#..#",
        "#.....#",
        "#.....#",
        "#######",
    ],
}

STAGES = [
    ("01", "STAGE 01 · SOBRE MÍ", "star", "cyan"),
    ("02", "STAGE 02 · ARSENAL & STATS", "sword", "magenta"),
    ("03", "STAGE 03 · LABORATORIO", "flask", "amber"),
    ("04", "STAGE 04 · ACTIVIDAD EN VIVO", "radar", "green"),
    ("05", "STAGE 05 · CONEXIÓN", "mail", "cyan"),
]


def _build_stage(num: str, label: str, icon_key: str, accent_key: str, mode: str, cfg: dict[str, Any]) -> str:
    pal: Palette = get_palette(cfg, mode)
    acc = pal.accent(accent_key)
    prefix = f"st{num}_{mode}"

    p: list[str] = [
        svg_open(
            W,
            H,
            f"{prefix}Title",
            label,
            f"{prefix}Desc",
            f"Separador de sección arcade {label} en tema {mode}.",
        ),
        "<defs>",
        pattern_bayer25(f"{prefix}Bg", pal.card, pal.card_alt, cell=4),
        pattern_scanlines(f"{prefix}Scan", pal),
        f'<clipPath id="{prefix}TrackClip"><rect x="640" y="28" width="224" height="12"/></clipPath>',
        "<style>",
        f"""
        .st-glint {{ animation: glintRun 3.2s linear infinite; }}
        @keyframes glintRun {{
          0% {{ transform: translateX(-36px); }}
          100% {{ transform: translateX(256px); }}
        }}
        {REDUCED_MOTION_CSS}
        """,
        "</style>",
        "</defs>",
        # RPG Frame
        rpg_panel(4, 2, W - 12, H - 8, pal, accent=acc, chamfer=8, shadow=4, fill=f"url(#{prefix}Bg)"),
        # Left Icon Socket
        rect(22, 16, 36, 36, pal.bg_deep, stroke=acc, stroke_width=2, crisp=True),
        pixel_sprite(29, 23, ICONS[icon_key], {"#": acc}, px=3),
        # Pixel Stage Title (px=3 -> 27px height, centered vertically)
        pixel_text(
            74,
            20,
            label,
            px=3,
            fill=pal.text,
            shadow=acc if not pal.is_dark else pal.bg_deep,
            shadow_offset=2,
            letter_gap=1,
        ),
        # Right Progress Track with Animated Pixel Glint
        mono_text(640, 22, "CLEAR", size=10.5, fill=acc, weight=700, spacing=1.2),
        mono_text(864, 22, f"{num}/05", size=10.5, fill=pal.text_muted, anchor="end", weight=700, spacing=1.0),
    ]

    # 12 pixel blocks track
    for i in range(12):
        bx = 640 + i * 19
        filled = i < (int(num) * 2 + 2)
        p.append(
            rect(
                bx,
                28,
                15,
                12,
                acc if filled else pal.bg_deep,
                stroke=None if filled else pal.border,
                stroke_width=1,
                opacity=0.85 if filled else 0.9,
                crisp=True,
            )
        )

    p.append(f'<g clip-path="url(#{prefix}TrackClip)">')
    p.append(rect(640, 28, 28, 12, "#FFFFFF", opacity=0.45 if pal.is_dark else 0.65, cls="st-glint", crisp=True))
    p.append("</g>")
    p.append(rect(4, 2, W - 12, H - 8, f"url(#{prefix}Scan)", crisp=True))
    p.append("</svg>")
    return "\n".join(p)


def generate_stages(config: dict[str, Any] | None = None) -> list[pathlib.Path]:
    cfg = config or load_config()
    ASSETS.mkdir(parents=True, exist_ok=True)
    written: list[pathlib.Path] = []
    for num, label, icon_key, accent_key in STAGES:
        for mode in ("dark", "light"):
            out = ASSETS / f"stage-{num}-{mode}.svg"
            out.write_text(_build_stage(num, label, icon_key, accent_key, mode, cfg), encoding="utf-8")
            written.append(out)
            print(f"wrote {out.name} ({out.stat().st_size:,} bytes)")
    return written


if __name__ == "__main__":
    generate_stages()
