#!/usr/bin/env python3
"""Generate pixel-art contact channel SVG buttons ONLY for configured links."""
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
    rect,
    rpg_panel,
    svg_open,
)

BTN_W, BTN_H = 290, 68
EMPTY_W, EMPTY_H = 900, 88

ICONS: dict[str, list[str]] = {
    "github": [
        ".#...#.",
        "#######",
        "#.###.#",
        "#######",
        ".#####.",
        "..###..",
        ".##.##.",
    ],
    "linkedin": [
        "##.....",
        ".......",
        "##.###.",
        "##.#..#",
        "##.#..#",
        "##.#..#",
        "##.#..#",
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
    "web": [
        "..###..",
        ".#.#.#.",
        "#######",
        "#..#..#",
        "#######",
        ".#.#.#.",
        "..###..",
    ],
}

CURSOR = [
    "#...",
    "##..",
    "###.",
    "##..",
    "#...",
]


def active_contact_links(cfg: dict[str, Any]) -> list[dict[str, str]]:
    raw = (cfg.get("contact") or {}).get("links") or []
    return [
        item for item in raw
        if isinstance(item, dict) and str(item.get("url") or "").strip()
    ]


def _build_button(link_item: dict[str, str], mode: str, cfg: dict[str, Any]) -> str:
    pal: Palette = get_palette(cfg, mode)
    cid = str(link_item.get("id", "channel"))
    label = str(link_item.get("label", cid)).upper()
    sublabel = str(link_item.get("sublabel") or link_item.get("url", ""))
    acc = pal.accent(str(link_item.get("accent", "cyan")))
    icon_rows = ICONS.get(str(link_item.get("icon", "web")), ICONS["web"])
    prefix = f"cnt_{cid}_{mode}"

    p: list[str] = [
        svg_open(
            BTN_W,
            BTN_H,
            f"{prefix}Title",
            f"Canal de contacto: {label}",
            f"{prefix}Desc",
            f"Botón arcade para abrir {label} ({sublabel}).",
        ),
        "<defs>",
        pattern_bayer25(f"{prefix}Bg", pal.card, pal.card_alt, cell=4),
        pattern_scanlines(f"{prefix}Scan", pal),
        "<style>",
        f"""
        .cnt-blink {{ animation: cntBlink 1.2s steps(1,end) infinite; }}
        @keyframes cntBlink {{ 0%,60%{{opacity:1}} 61%,100%{{opacity:0.45}} }}
        {REDUCED_MOTION_CSS}
        """,
        "</style>",
        "</defs>",
        rpg_panel(4, 4, BTN_W - 12, BTN_H - 12, pal, accent=acc, chamfer=6, shadow=4, fill=f"url(#{prefix}Bg)"),
        rect(16, 16, 36, 36, pal.bg_deep, stroke=acc, stroke_width=1.5, crisp=True),
        pixel_sprite(23, 23, icon_rows, {"#": acc}, px=3),
        mono_text(64, 32, label, size=13, fill=pal.text, weight=700, spacing=1.2),
        mono_text(64, 49, sublabel[:24], size=11, fill=acc, weight=700),
        '<g class="cnt-blink">',
        pixel_sprite(BTN_W - 34, 26, CURSOR, {"#": acc}, px=3),
        "</g>",
        rect(4, 4, BTN_W - 12, BTN_H - 12, f"url(#{prefix}Scan)", crisp=True),
        "</svg>",
    ]
    return "\n".join(p)


def _build_empty(mode: str, cfg: dict[str, Any]) -> str:
    pal: Palette = get_palette(cfg, mode)
    prefix = f"cnt_empty_{mode}"
    acc = pal.amber
    return "\n".join([
        svg_open(
            EMPTY_W,
            EMPTY_H,
            f"{prefix}Title",
            "Canal en configuración",
            f"{prefix}Desc",
            "Sin enlaces de contacto externos configurados todavía.",
        ),
        "<defs>",
        pattern_bayer25(f"{prefix}Bg", pal.card, pal.card_alt, cell=4),
        pattern_scanlines(f"{prefix}Scan", pal),
        "<style>",
        f"""
        .cnt-pulse {{ animation: cntPulse 2s ease-in-out infinite; }}
        @keyframes cntPulse {{ 0%,100%{{opacity:0.45}} 50%{{opacity:1}} }}
        {REDUCED_MOTION_CSS}
        """,
        "</style>",
        "</defs>",
        rpg_panel(4, 4, EMPTY_W - 12, EMPTY_H - 12, pal, accent=acc, chamfer=8, shadow=4, fill=f"url(#{prefix}Bg)"),
        rect(24, 36, 12, 12, acc, cls="cnt-pulse", crisp=True),
        mono_text(48, 40, "CANAL EN CONFIGURACIÓN", size=14, fill=pal.text, weight=700, spacing=1.4),
        mono_text(48, 60, "Agrega tus enlaces públicos reales en profile.config.json.", size=12, fill=pal.text_muted),
        rect(4, 4, EMPTY_W - 12, EMPTY_H - 12, f"url(#{prefix}Scan)", crisp=True),
        "</svg>",
    ])


def generate_contact(config: dict[str, Any] | None = None) -> tuple[list[dict[str, str]], list[pathlib.Path]]:
    cfg = config or load_config()
    ASSETS.mkdir(parents=True, exist_ok=True)
    for old in ASSETS.glob("contact-*.svg"):
        old.unlink()

    links = active_contact_links(cfg)
    written: list[pathlib.Path] = []
    if links:
        for item in links:
            cid = str(item.get("id", "link"))
            for mode in ("dark", "light"):
                out = ASSETS / f"contact-{cid}-{mode}.svg"
                out.write_text(_build_button(item, mode, cfg), encoding="utf-8")
                written.append(out)
                print(f"wrote {out.name} ({out.stat().st_size:,} bytes)")
    else:
        for mode in ("dark", "light"):
            out = ASSETS / f"contact-empty-{mode}.svg"
            out.write_text(_build_empty(mode, cfg), encoding="utf-8")
            written.append(out)
            print(f"wrote {out.name} ({out.stat().st_size:,} bytes)")
    return links, written


if __name__ == "__main__":
    generate_contact()
