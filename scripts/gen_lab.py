#!/usr/bin/env python3
"""Generate retro cartridge project SVGs from real public GitHub repositories."""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import textwrap
from typing import Any

from design_system import (
    ASSETS,
    REDUCED_MOTION_CSS,
    Palette,
    get_palette,
    language_accent,
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
from github_api import fetch_public_repos

CARD_W, CARD_H = 436, 206
EMPTY_W, EMPTY_H = 900, 176

PLAY_TRIANGLE = [
    "#...",
    "##..",
    "###.",
    "##..",
    "#...",
]

STAR_ICON = [
    "..#..",
    "..#..",
    "#####",
    ".###.",
    ".#.#.",
]


def _relative_es(iso_ts: str, now_utc: dt.datetime | None = None) -> str:
    if not iso_ts:
        return "reciente"
    try:
        parsed = dt.datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
    except ValueError:
        return "reciente"
    now = now_utc or dt.datetime.now(dt.timezone.utc)
    delta = now - parsed
    days = max(0, delta.days)
    if days == 0:
        hours = max(1, int(delta.total_seconds() // 3600))
        return "hoy" if delta.total_seconds() < 3600 else f"hace {hours}h"
    if days == 1:
        return "ayer"
    if days < 30:
        return f"hace {days} días"
    months = days // 30
    if months < 12:
        return f"hace {months} {'mes' if months == 1 else 'meses'}"
    years = days // 365
    return f"hace {years} {'año' if years == 1 else 'años'}"


def _wrap_description(desc: str, width: int = 44, max_lines: int = 2) -> list[str]:
    text = (desc or "").strip() or "Proyecto público en GitHub · código y pruebas."
    lines = textwrap.wrap(text, width=width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        if len(lines[-1]) > width - 3:
            lines[-1] = lines[-1][: width - 3].rstrip() + "..."
        else:
            lines[-1] = lines[-1].rstrip(".") + "..."
    return lines


def _build_repo_card(repo: dict[str, Any], idx: int, mode: str, cfg: dict[str, Any]) -> str:
    pal: Palette = get_palette(cfg, mode)
    lang = repo.get("language") or "Otro"
    acc = language_accent(lang, pal)
    prefix = f"lab{idx}_{mode}"
    name = str(repo["name"])
    custom_descs = (cfg.get("lab") or {}).get("repo_descriptions") or {}
    desc_raw = custom_descs.get(name) or repo.get("description") or ""
    desc_lines = _wrap_description(desc_raw, width=44, max_lines=2)
    stars = int(repo.get("stars", 0))
    rel = _relative_es(str(repo.get("pushed_at") or repo.get("updated_at") or ""))

    title_px = 3 if len(name) <= 18 else 2
    title_y = 54 if title_px == 3 else 58

    p: list[str] = [
        svg_open(
            CARD_W,
            CARD_H,
            f"{prefix}Title",
            f"Cartucho de proyecto: {name}",
            f"{prefix}Desc",
            f"Repositorio {name} en {lang}. Actualizado {rel}.",
        ),
        "<defs>",
        pattern_bayer25(f"{prefix}Bg", pal.card, pal.card_alt, cell=4),
        pattern_scanlines(f"{prefix}Scan", pal),
        "<style>",
        f"""
        .cart-blink {{ animation: cartBlink 1.3s steps(1,end) infinite; }}
        @keyframes cartBlink {{ 0%,60%{{opacity:1}} 61%,100%{{opacity:0.55}} }}
        {REDUCED_MOTION_CSS}
        """,
        "</style>",
        "</defs>",
        # Cartridge Outer Shell
        rpg_panel(4, 4, CARD_W - 12, CARD_H - 12, pal, accent=acc, chamfer=8, shadow=4, fill=f"url(#{prefix}Bg)", top_strip=False),
        # Cartridge Top Colored Stripe + Grip Grooves
        rect(16, 10, CARD_W - 36, 12, acc, crisp=True),
        rect(24, 14, 36, 4, pal.bg_deep, opacity=0.45, crisp=True),
        rect(CARD_W - 64, 14, 36, 4, pal.bg_deep, opacity=0.45, crisp=True),
        # Cartridge Index + Language Label
        mono_text(24, 42, f"CART-{idx:02d}", size=11, fill=pal.text_dim, weight=700, spacing=1.0),
        rect(CARD_W - 134, 29, 110, 18, pal.bg_deep, stroke=acc, stroke_width=1.5, crisp=True),
        mono_text(CARD_W - 79, 42, lang.upper()[:11], size=10.5, fill=acc, anchor="middle", weight=700, spacing=0.8),
        # Repo Name (Pixel Bitmap Title)
        pixel_text(24, title_y, name, px=title_px, fill=pal.text, shadow=pal.bg_deep if pal.is_dark else pal.shadow, shadow_offset=2),
        # Description (up to 2 lines)
    ]

    dy = 104
    for dline in desc_lines:
        p.append(mono_text(24, dy, dline, size=12.5, fill=pal.text_muted))
        dy += 20

    # Bottom Metadata Bar
    p.append(line(24, 148, CARD_W - 28, 148, pal.border, width=1.5))

    meta_x = 24
    if stars > 0:
        p.append(pixel_sprite(meta_x, 162, STAR_ICON, {"#": pal.amber}, px=2.5))
        p.append(mono_text(meta_x + 18, 173, str(stars), size=12, fill=pal.amber, weight=700))
        meta_x += 44

    p.append(mono_text(meta_x, 173, f"UPD: {rel.upper()}", size=11, fill=pal.text_dim, weight=700, spacing=0.5))

    # PRESS START ▸
    p.append(mono_text(CARD_W - 44, 173, "PRESS START", size=11.5, fill=acc, anchor="end", weight=700, spacing=0.8, cls="cart-blink"))
    p.append('<g class="cart-blink">')
    p.append(pixel_sprite(CARD_W - 38, 162, PLAY_TRIANGLE, {"#": acc}, px=2.5))
    p.append("</g>")

    p.append(rect(4, 4, CARD_W - 12, CARD_H - 12, f"url(#{prefix}Scan)", crisp=True))
    p.append("</svg>")
    return "\n".join(p)


def _build_next_card(slot_num: int, mode: str, cfg: dict[str, Any], *, full_width: bool = False) -> str:
    pal: Palette = get_palette(cfg, mode)
    w, h = (EMPTY_W, EMPTY_H) if full_width else (CARD_W, CARD_H)
    prefix = f"lab_next_{slot_num}_{mode}"
    acc = pal.amber

    p: list[str] = [
        svg_open(
            w,
            h,
            f"{prefix}Title",
            "Próximo nivel en construcción",
            f"{prefix}Desc",
            "Espacio reservado para próximos proyectos públicos en construcción.",
        ),
        "<defs>",
        pattern_bayer25(f"{prefix}Bg", pal.card, pal.card_alt, cell=4),
        pattern_scanlines(f"{prefix}Scan", pal),
        f'<clipPath id="{prefix}LoadClip"><rect x="24" y="{h - 68}" width="{w - 56}" height="14"/></clipPath>',
        "<style>",
        f"""
        .load-sweep {{ animation: loadSweep 2.8s linear infinite; }}
        .next-blink {{ animation: nextBlink 1.5s steps(1,end) infinite; }}
        @keyframes loadSweep {{
          0% {{ transform: translateX(-80px); }}
          100% {{ transform: translateX({w}px); }}
        }}
        @keyframes nextBlink {{ 0%,55%{{opacity:1}} 56%,100%{{opacity:0.25}} }}
        {REDUCED_MOTION_CSS}
        """,
        "</style>",
        "</defs>",
        rpg_panel(4, 4, w - 12, h - 12, pal, accent=acc, chamfer=8, shadow=4, fill=f"url(#{prefix}Bg)", top_strip=False),
        rect(16, 10, w - 36, 10, acc, opacity=0.75, crisp=True),
        mono_text(24, 42, f"SLOT-{slot_num:02d} · EXPANSIÓN", size=11, fill=pal.text_dim, weight=700, spacing=1.0),
        pixel_text(24, 56, "PRÓXIMO NIVEL", px=3, fill=pal.text, shadow=pal.bg_deep if pal.is_dark else pal.shadow, shadow_offset=2),
        mono_text(24, 98, "EN CONSTRUCCIÓN · PRUEBAS EN CURSO", size=12.5, fill=pal.text_muted, weight=700),
    ]

    bar_y = h - 68
    bar_w = w - 56
    seg_count = (bar_w // 18)
    for i in range(seg_count):
        sx = 24 + i * 18
        active = i < int(seg_count * 0.65)
        p.append(rect(sx, bar_y, 14, 14, acc if active else pal.bg_deep, stroke=None if active else pal.border, stroke_width=1, opacity=0.85 if active else 0.9, crisp=True))

    p.append(f'<g clip-path="url(#{prefix}LoadClip)">')
    p.append(rect(24, bar_y, 64, 14, "#FFFFFF", opacity=0.4 if pal.is_dark else 0.65, cls="load-sweep", crisp=True))
    p.append("</g>")

    p.append(mono_text(w - 28, h - 26, "LOADING...", size=11, fill=acc, anchor="end", weight=700, spacing=1.0, cls="next-blink"))
    p.append(rect(4, 4, w - 12, h - 12, f"url(#{prefix}Scan)", crisp=True))
    p.append("</svg>")
    return "\n".join(p)


def generate_lab(config: dict[str, Any] | None = None, repos: list[dict[str, Any]] | None = None) -> tuple[list[dict[str, Any]], list[pathlib.Path]]:
    cfg = config or load_config()
    ASSETS.mkdir(parents=True, exist_ok=True)
    login = cfg["github_username"]
    lab_cfg = cfg.get("lab") or {}
    max_cards = int(lab_cfg.get("max_cards", 4))
    exclude = set(cfg.get("profile_repos_to_exclude") or [])
    featured = list(lab_cfg.get("featured_repos") or [])

    if repos is None:
        repos = fetch_public_repos(login, exclude_names=exclude, featured=featured, max_items=max_cards)
        cache_file = ASSETS / "lab-repos.json"
        if repos:
            cache_file.write_text(json.dumps(repos, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        elif cache_file.exists():
            print("[warn] Usando caché local de repositorios en assets/lab-repos.json")
            repos = json.loads(cache_file.read_text(encoding="utf-8"))[:max_cards]

    # Clean stale lab-card-*.svg files if repo count changed
    for old in ASSETS.glob("lab-card-*.svg"):
        old.unlink()
    for old in ASSETS.glob("lab-next-*.svg"):
        old.unlink()

    written: list[pathlib.Path] = []
    for idx, repo in enumerate(repos, start=1):
        for mode in ("dark", "light"):
            out = ASSETS / f"lab-card-{idx}-{mode}.svg"
            out.write_text(_build_repo_card(repo, idx, mode, cfg), encoding="utf-8")
            written.append(out)
            print(f"wrote {out.name} ({out.stat().st_size:,} bytes)")

    # Generate balanced slot card if odd number of repos (e.g. 3 -> 4th slot) and empty fallback banner
    if repos and len(repos) % 2 == 1:
        slot = len(repos) + 1
        for mode in ("dark", "light"):
            out = ASSETS / f"lab-next-{slot}-{mode}.svg"
            out.write_text(_build_next_card(slot, mode, cfg, full_width=False), encoding="utf-8")
            written.append(out)
            print(f"wrote {out.name} ({out.stat().st_size:,} bytes)")

    for mode in ("dark", "light"):
        out = ASSETS / f"lab-empty-{mode}.svg"
        out.write_text(_build_next_card(1, mode, cfg, full_width=True), encoding="utf-8")
        written.append(out)
        print(f"wrote {out.name} ({out.stat().st_size:,} bytes)")

    return repos, written


if __name__ == "__main__":
    generate_lab()
