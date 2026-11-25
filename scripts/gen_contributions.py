#!/usr/bin/env python3
"""Generate pixel LED contribution heatmap & 4 LCD counters (dark & light themes)."""
from __future__ import annotations

import datetime as dt
import json
import pathlib
from typing import Any

from design_system import (
    ASSETS,
    REDUCED_MOTION_CSS,
    Palette,
    esc,
    get_palette,
    line,
    load_config,
    mono_text,
    pattern_bayer25,
    pattern_scanlines,
    pixel_text,
    rect,
    rpg_panel,
    svg_open,
)
from github_api import fetch_contributions

W, H = 900, 456
MONTHS = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]


def _heat_color(count: int, pal: Palette) -> str:
    if count <= 0:
        return pal.heat[0]
    if count == 1:
        return pal.heat[1]
    if count <= 3:
        return pal.heat[2]
    if count <= 6:
        return pal.heat[3]
    return pal.heat[4]


def _fmt_date(d: dt.date) -> str:
    return f"{d.day:02d} {MONTHS[d.month - 1]} {d.year}"


def _build_contributions_svg(stats: dict[str, Any], mode: str, cfg: dict[str, Any]) -> str:
    pal: Palette = get_palette(cfg, mode)
    prefix = f"ct_{mode}"
    weeks = list(stats.get("weeks") or [])
    created_str = str(stats.get("account_created") or dt.date.today().isoformat())
    created = dt.date.fromisoformat(created_str)
    today_str = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=5)).date().isoformat()
    source_tag = "EN VIVO · GRAPHQL" if stats.get("source") == "graphql" else "CACHÉ + REST PÚBLICO"
    status_col = pal.green if stats.get("source") == "graphql" else pal.amber

    p: list[str] = [
        svg_open(
            W,
            H,
            f"{prefix}Title",
            f"Mapa de calor pixel de contribuciones de {stats.get('login', '')} ({mode})",
            f"{prefix}Desc",
            f"{stats.get('total_contributions', 0)} contribuciones, "
            f"racha actual de {stats.get('current_streak', 0)} días, "
            f"{stats.get('active_days', 0)} días activos y {stats.get('public_repos', 0)} repos públicos.",
        ),
        "<defs>",
        pattern_bayer25(f"{prefix}Bg", pal.bg, pal.bg_deep, cell=4),
        pattern_scanlines(f"{prefix}Scan", pal),
        "<style>",
        f"""
        .ct-pulse {{ animation: ctPulse 2.2s ease-in-out infinite; }}
        .led-wave {{ animation: ledWave 4.6s ease-in-out infinite; }}
        @keyframes ctPulse {{ 0%,100%{{opacity:0.4}} 50%{{opacity:1}} }}
        @keyframes ledWave {{
          0%, 100% {{ opacity: 0.78; }}
          35% {{ opacity: 1; }}
        }}
        {REDUCED_MOTION_CSS}
        """,
        "</style>",
        "</defs>",
        rect(0, 0, W, H, f"url(#{prefix}Bg)", crisp=True),
        # Outer RPG Panel
        rpg_panel(8, 8, W - 20, H - 20, pal, accent=pal.green, chamfer=8, shadow=4),
        # Header Bar
        rect(20, 20, W - 44, 38, pal.bg_deep, stroke=pal.border, stroke_width=1.5, crisp=True),
        pixel_text(34, 27, "RADAR DE ACTIVIDAD", px=2.5 if False else 2, fill=pal.text, shadow=pal.green if not pal.is_dark else pal.bg_deep, shadow_offset=2),
        rect(484, 35, 8, 8, status_col, cls="ct-pulse", crisp=True),
        mono_text(500, 44, source_tag, size=11, fill=status_col, weight=700, spacing=0.8),
        mono_text(858, 44, str(stats.get("updated_local", "")), size=10.5, fill=pal.text_dim, anchor="end"),
    ]

    # ---- 4 Retro LCD Counters (y=72..154) ----
    counters = [
        ("CONTRIBUCIONES (AÑO)", f"{int(stats.get('total_contributions', 0)):02d}", "ÚLTIMOS 12 MESES", pal.cyan),
        ("RACHA ACTUAL", f"{int(stats.get('current_streak', 0)):02d}", f"MEJOR: {int(stats.get('longest_streak', 0)):02d} DÍAS", pal.magenta),
        ("DÍAS ACTIVOS", f"{int(stats.get('active_days', 0)):02d}", f"DESDE {created.strftime('%d/%m/%Y')}", pal.amber),
        ("REPOS PÚBLICOS", f"{int(stats.get('public_repos', 0)):02d}", f"COMMITS: {int(stats.get('commits', 0)):02d}", pal.green),
    ]
    cx = 24
    card_w = 204
    for label, val, sub, acc in counters:
        p.append(rpg_panel(cx, 72, card_w, 84, pal, accent=acc, chamfer=6, shadow=3, fill=pal.card_alt, top_strip=True))
        # Sunken LCD readout box
        p.append(rect(cx + 12, 98, card_w - 24, 34, pal.bg_deep, stroke=pal.border, stroke_width=1.5, crisp=True))
        p.append(mono_text(cx + 14, 92, label, size=10.5, fill=pal.text_muted, weight=700, spacing=0.5))
        p.append(mono_text(cx + card_w / 2, 124, val, size=24, fill=acc, anchor="middle", weight=700, spacing=2.0))
        p.append(mono_text(cx + 14, 148, sub, size=10, fill=pal.text_dim, weight=700, spacing=0.5))
        cx += card_w + 12

    # ---- LED Pixel Heatmap Matrix (y=172..416) ----
    p.append(rpg_panel(24, 172, W - 52, 232, pal, accent=pal.cyan, chamfer=8, shadow=4, fill=pal.card_alt, top_strip=False))
    p.append(mono_text(40, 196, "MATRIZ LED · 53 SEMANAS", size=11.5, fill=pal.cyan, weight=700, spacing=1.0))
    p.append(mono_text(856, 196, "DATOS REALES DE GITHUB · SIN MÉTRICAS INVENTADAS", size=10.5, fill=pal.text_dim, anchor="end"))

    grid_x = 76
    grid_y = 224
    pitch = 14
    cell = 11

    # Weekday labels
    for di, wd_label in ((1, "LUN"), (3, "MIÉ"), (5, "VIE")):
        p.append(mono_text(68, grid_y + di * pitch + 9, wd_label, size=10, fill=pal.text_dim, anchor="end", weight=700))

    months_drawn: list[int] = []
    for wi, week in enumerate(weeks[:53]):
        first_slot = next((slot for slot in week if slot), None)
        if first_slot:
            d0 = dt.date.fromisoformat(first_slot["date"])
            if not months_drawn or months_drawn[-1] != d0.month:
                months_drawn.append(d0.month)
                if wi <= 50:
                    p.append(mono_text(grid_x + wi * pitch, 215, MONTHS[d0.month - 1], size=10, fill=pal.text_muted, weight=700))

        for di in range(7):
            slot = week[di] if di < len(week) else None
            x = grid_x + wi * pitch
            y = grid_y + di * pitch
            if slot is None:
                p.append(rect(x, y, cell, cell, pal.bg_deep, opacity=0.35, crisp=True))
                continue

            day_iso = slot["date"]
            count = int(slot["count"])
            day_obj = dt.date.fromisoformat(day_iso)
            delay = f"{((wi + di) * 0.035):.2f}s"

            if day_obj < created:
                p.append(rect(x, y, cell, cell, pal.bg_deep, opacity=0.35, crisp=True))
                continue

            col = _heat_color(count, pal)
            if count > 0:
                p.append(
                    f'<g class="led-wave" style="animation-delay:{delay}">'
                    f'<title>{esc(_fmt_date(day_obj))} · {count} contribuciones</title>'
                    + rect(x, y, cell, cell, col, crisp=True)
                    + rect(x, y, cell, 2, "#FFFFFF", opacity=0.3, crisp=True)
                    + "</g>"
                )
            else:
                p.append(
                    rect(
                        x, y, cell, cell, col,
                        stroke="#C5BEB0" if not pal.is_dark else None,
                        stroke_width=0.8,
                        opacity=0.9,
                        cls="led-wave",
                        style=f"animation-delay:{delay}",
                        crisp=True,
                    )
                )

            if day_iso == today_str:
                p.append(rect(x - 1.5, y - 1.5, cell + 3, cell + 3, "none", stroke=pal.cyan, stroke_width=1.5, crisp=True))

    # Subtle watermark explaining pre-account region
    p.append(mono_text(grid_x + 19 * pitch, grid_y + 3 * pitch + 9, "ANTES DE MI CUENTA", size=10.5, fill=pal.text_dim, anchor="middle", weight=700, spacing=2.0, opacity=0.48))

    # Legend & Footnote inside Heatmap panel
    p.append(line(40, 338, 856, 338, pal.border, width=1))
    p.append(mono_text(40, 362, f"CUENTA CREADA: {_fmt_date(created)}", size=11, fill=pal.text_muted, weight=700))
    p.append(mono_text(40, 384, f"LOGIN: @{stats.get('login', '')} · ACTUALIZACIÓN CADA 8H", size=10.5, fill=pal.text_dim))

    lx = 556
    p.append(mono_text(lx - 10, 362, "MENOS", size=10.5, fill=pal.text_dim, anchor="end", weight=700))
    for i, hc in enumerate(pal.heat):
        p.append(rect(lx + i * 18, 351, 13, 13, hc, stroke=pal.border, stroke_width=1, crisp=True))
    p.append(mono_text(lx + len(pal.heat) * 18 + 8, 362, "MÁS", size=10.5, fill=pal.text_dim, weight=700))
    p.append(rect(760, 351, 13, 13, "none", stroke=pal.cyan, stroke_width=1.5, crisp=True))
    p.append(mono_text(780, 362, "HOY", size=10.5, fill=pal.cyan, weight=700))

    # Bottom status note
    p.append(mono_text(450, 434, "TELEMETRÍA PÚBLICA DE GITHUB · CERO MÉTRICAS INVENTADAS", size=11, fill=pal.text_muted, anchor="middle", weight=700, spacing=0.8))
    p.append(rect(8, 8, W - 20, H - 20, f"url(#{prefix}Scan)", crisp=True))
    p.append("</svg>")
    return "\n".join(p)


def generate_contributions(config: dict[str, Any] | None = None) -> tuple[dict[str, Any], list[pathlib.Path]]:
    cfg = config or load_config()
    ASSETS.mkdir(parents=True, exist_ok=True)
    json_path = ASSETS / "contributions.json"
    login = cfg["github_username"]
    stats = fetch_contributions(login, cache_path=json_path)

    # Persist clean public JSON cache (including compact weeks for resilient local builds)
    public_json = {
        "login": stats["login"],
        "source": stats["source"],
        "total_contributions": stats["total_contributions"],
        "active_days": stats["active_days"],
        "current_streak": stats["current_streak"],
        "longest_streak": stats["longest_streak"],
        "first_active": stats["first_active"],
        "commits": stats["commits"],
        "pull_requests": stats["pull_requests"],
        "issues": stats["issues"],
        "reviews": stats["reviews"],
        "public_repos": stats["public_repos"],
        "followers": stats["followers"],
        "days_on_github": stats["days_on_github"],
        "account_created": stats["account_created"],
        "updated_local": stats["updated_local"],
        "updated_utc": stats["updated_utc"],
        "updated_iso": stats["updated_iso"],
        "active_day_map": stats["active_day_map"],
        "engine": "profile-engine-v2",
    }
    json_path.write_text(json.dumps(public_json, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    written: list[pathlib.Path] = []
    for mode in ("dark", "light"):
        out = ASSETS / f"contributions-{mode}.svg"
        out.write_text(_build_contributions_svg(stats, mode, cfg), encoding="utf-8")
        written.append(out)
        print(f"wrote {out.name} ({out.stat().st_size:,} bytes)")
    return stats, written


if __name__ == "__main__":
    generate_contributions()
