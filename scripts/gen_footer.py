#!/usr/bin/env python3
"""Generate animated INSERT COIN arcade footer banners (dark & light themes)."""
from __future__ import annotations

import datetime as dt
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
    pixel_sprite,
    pixel_text,
    rect,
    rpg_panel,
    svg_open,
)

W, H = 900, 148

COIN_ROWS = [
    ".####.",
    "######",
    "##YY##",
    "##YY##",
    "######",
    ".####.",
]


def _build_footer(sync_utc: str, mode: str, cfg: dict[str, Any]) -> str:
    pal: Palette = get_palette(cfg, mode)
    prefix = f"ft_{mode}"
    handle = cfg.get("handle", "NICOLÁS.OS")
    location = cfg.get("location", "Bogotá, Colombia")
    tz = cfg.get("timezone_label", "UTC-5")
    coin_colors = {"#": pal.amber, "Y": "#FEF08A" if pal.is_dark else "#FDE047"}

    p: list[str] = [
        svg_open(
            W,
            H,
            f"{prefix}Title",
            "Insert Coin — Gracias por jugar",
            f"{prefix}Desc",
            f"Banner final estilo arcade con telemetría de sincronización: {sync_utc}.",
        ),
        "<defs>",
        pattern_bayer25(f"{prefix}Bg", pal.card, pal.card_alt, cell=4),
        pattern_scanlines(f"{prefix}Scan", pal),
        f'<clipPath id="{prefix}SlotClip"><rect x="34" y="22" width="52" height="72"/></clipPath>',
        "<style>",
        f"""
        .ft-blink {{ animation: ftBlink 1.1s steps(1,end) infinite; }}
        .ft-coin {{ animation: coinDrop 2.6s steps(10,end) infinite; }}
        .ft-pulse {{ animation: ftPulse 2s ease-in-out infinite; }}
        @keyframes ftBlink {{ 0%,50%{{opacity:1}} 51%,100%{{opacity:0.15}} }}
        @keyframes ftPulse {{ 0%,100%{{opacity:0.45}} 50%{{opacity:1}} }}
        @keyframes coinDrop {{
          0%, 10% {{ transform: translateY(0); opacity: 1; }}
          68% {{ transform: translateY(32px); opacity: 1; }}
          82%, 92% {{ transform: translateY(38px); opacity: 0; }}
          100% {{ transform: translateY(0); opacity: 1; }}
        }}
        {REDUCED_MOTION_CSS}
        """,
        "</style>",
        "</defs>",
        # Outer RPG Panel
        rpg_panel(4, 4, W - 12, H - 12, pal, accent=pal.magenta, chamfer=8, shadow=4, fill=f"url(#{prefix}Bg)"),
        # Left Coin Slot + Animated Dropping Pixel Coin
        rect(34, 24, 52, 68, pal.bg_deep, stroke=pal.border, stroke_width=2, crisp=True),
        rect(54, 72, 12, 14, "#000000" if pal.is_dark else "#1E2433", stroke=pal.amber, stroke_width=1.5, crisp=True),
        f'<g clip-path="url(#{prefix}SlotClip)">',
        '<g class="ft-coin">' + pixel_sprite(48, 30, COIN_ROWS, coin_colors, px=4) + "</g>",
        "</g>",
        # Center Pixel Title + PRESS START
        pixel_text(416, 32, "INSERT COIN · GRACIAS POR JUGAR", px=3, fill=pal.text, shadow=pal.magenta if pal.is_dark else pal.shadow, shadow_offset=2, anchor="middle"),
        mono_text(416, 78, "PRESS START", size=14, fill=pal.amber, anchor="middle", weight=700, spacing=3.0, cls="ft-blink"),
        # Right 1UP / Credits Badge
        rect(744, 30, 124, 54, pal.bg_deep, stroke=pal.cyan, stroke_width=1.5, crisp=True),
        mono_text(806, 52, "CREDIT 01", size=12, fill=pal.cyan, anchor="middle", weight=700, spacing=1.2),
        mono_text(806, 72, "READY!", size=12, fill=pal.green, anchor="middle", weight=700, spacing=1.4, cls="ft-pulse"),
        # Bottom Telemetry Line
        line(24, 102, W - 28, 102, pal.border, width=1.5),
        rect(24, 115, 8, 8, pal.green, cls="ft-pulse", crisp=True),
        mono_text(40, 124, f"SYNC: {sync_utc} · PROFILE ENGINE v2.0", size=11.5, fill=pal.text_muted, weight=700, spacing=0.6),
        mono_text(W - 28, 124, f"{location.upper()} · {tz} · {handle}", size=11, fill=pal.magenta, anchor="end", weight=700, spacing=0.6),
        rect(4, 4, W - 12, H - 12, f"url(#{prefix}Scan)", crisp=True),
        "</svg>",
    ]
    return "\n".join(p)


def generate_footer(config: dict[str, Any] | None = None, *, sync_utc: str | None = None) -> list[pathlib.Path]:
    cfg = config or load_config()
    ASSETS.mkdir(parents=True, exist_ok=True)
    stamp = sync_utc or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    written: list[pathlib.Path] = []
    for mode in ("dark", "light"):
        out = ASSETS / f"footer-{mode}.svg"
        out.write_text(_build_footer(stamp, mode, cfg), encoding="utf-8")
        written.append(out)
        print(f"wrote {out.name} ({out.stat().st_size:,} bytes)")
    return written


if __name__ == "__main__":
    generate_footer()
