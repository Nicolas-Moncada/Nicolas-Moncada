#!/usr/bin/env python3
"""Generate animated 16-bit Gamer Room hero scenes (dark & light themes)."""
from __future__ import annotations

import pathlib
from typing import Any

from design_system import (
    ASSETS,
    REDUCED_MOTION_CSS,
    Palette,
    esc,
    get_palette,
    glow_filter,
    line,
    load_config,
    mono_text,
    pattern_bayer25,
    pattern_checker,
    pattern_scanlines,
    pixel_sprite,
    pixel_text,
    rect,
    rpg_panel,
    segmented_bar,
    svg_open,
)

W, H = 900, 360

# Cute pixel-art cat sitting on windowsill (12x10)
CAT_ROWS = [
    ".#......#...",
    "###....###..",
    "##########..",
    "##W####W##..",
    "##########..",
    ".########...",
    ".########.#.",
    ".########.##",
    ".########.#.",
    ".##....##...",
]

# Music note 5x6
NOTE_ROWS = [
    "..###",
    "..#.#",
    "..#..",
    ".##..",
    "###..",
    ".#...",
]

# Tiny space invader for mini arcade screen (7x5)
INVADER_ROWS = [
    ".#...#.",
    "..###..",
    ".#####.",
    "##.#.##",
    "#.#.#.#",
]

# Tiny heart icon for P1 HUD (7x6)
HEART_ROWS = [
    ".##.##.",
    "#######",
    "#######",
    ".#####.",
    "..###..",
    "...#...",
]


def _build_scene(config: dict[str, Any], mode: str) -> str:
    pal: Palette = get_palette(config, mode)
    is_dark = pal.is_dark
    prefix = f"hero_{mode}"
    display_name = config.get("display_name", "NICOLÁS")
    full_name = config.get("full_name", "Nicolás Moncada Montaño")
    class_tag = config.get("class_tag", "SYS.ENG")
    location = config.get("location", "Bogotá, Colombia")
    tz_label = config.get("timezone_label", "UTC-5")
    semester = config.get("semester", "3er semestre")
    term_lines = list(config.get("terminal_lines") or [
        "$ whoami",
        "> nicolas",
        "$ cat pasion.txt",
        "> codigo + sistemas + arcade",
    ])[:4]

    # Theme-native room & environment colors
    if is_dark:
        wall_a, wall_b = "#0B0E17", "#101626"
        floor_a, floor_b = "#1E1210", "#140B09"
        rug_a, rug_b = "#1C1433", "#2A1C4D"
        desk_top, desk_bevel, desk_front = "#4E3426", "#78533D", "#2D1C14"
        wood_frame, wood_hi = "#3B281E", "#5C4030"
        sky_bands = ("#060916", "#0B1633", "#151D44", "#241942")
        mountain_col = "#091020"
        building_col = "#10192D"
        crt_case, crt_bevel, crt_scr = "#BEB39B", "#DED4BE", "#06121A"
        kb_body, kb_hi = "#1A2234", "#2E3B56"
        cab_body, cab_trim, cab_scr = "#201436", "#39235E", "#060B12"
        cat_colors = {"#": "#2D3748", "W": "#FDE68A"}
        mug_col, mug_hi = "#C7BBA4", "#EBE3D3"
        steam_col = "#CBD5E1"
        celestial_col = "#FDE68A"
        ant_blink = pal.magenta
    else:
        wall_a, wall_b = "#EFECE3", "#E5E0D2"
        floor_a, floor_b = "#B68A5D", "#9B7046"
        rug_a, rug_b = "#DBEAFE", "#BFDBFE"
        desk_top, desk_bevel, desk_front = "#A47247", "#C69464", "#7C5230"
        wood_frame, wood_hi = "#6B472B", "#8D613E"
        sky_bands = ("#1D63B8", "#3B82F6", "#7DD3FC", "#FEF08A")
        mountain_col = "#475569"
        building_col = "#334155"
        crt_case, crt_bevel, crt_scr = "#D6D0C4", "#EFECE4", "#0F172A"
        kb_body, kb_hi = "#334155", "#475569"
        cab_body, cab_trim, cab_scr = "#1E293B", "#0066CC", "#0B1324"
        cat_colors = {"#": "#D97706", "W": "#111827"}
        mug_col, mug_hi = "#FFFFFF", "#F8FAFC"
        steam_col = "#64748B"
        celestial_col = "#F59E0B"
        ant_blink = "#DC2626"

    p: list[str] = [
        svg_open(
            W,
            H,
            f"{prefix}Title",
            f"{display_name} — Habitación gamer 16-bit ({mode})",
            f"{prefix}Desc",
            f"Escena pixel art de {full_name}, {config.get('role', '')}, en {location}. "
            "Incluye HUD arcade, ventana animada, monitor CRT con terminal en bucle, teclado RGB, "
            "taza de café, tocadiscos, mini arcade y mascota pixelada.",
        )
    ]

    # ---- <defs> ----
    p.append("<defs>")
    p.append(pattern_bayer25(f"{prefix}Wall", wall_a, wall_b, cell=4))
    p.append(pattern_checker(f"{prefix}Sky01", sky_bands[0], sky_bands[1], cell=4))
    p.append(pattern_checker(f"{prefix}Sky12", sky_bands[1], sky_bands[2], cell=4))
    p.append(pattern_checker(f"{prefix}Sky23", sky_bands[2], sky_bands[3], cell=4))
    p.append(pattern_checker(f"{prefix}Rug", rug_a, rug_b, cell=4))
    p.append(pattern_scanlines(f"{prefix}Scan", pal))
    if is_dark:
        p.append(glow_filter(f"{prefix}Glow", std_dev=3.5))
    p.append(f'<clipPath id="{prefix}WinClip"><rect x="32" y="60" width="248" height="152"/></clipPath>')
    p.append(f'<clipPath id="{prefix}CrtClip"><rect x="304" y="128" width="176" height="72"/></clipPath>')
    p.append(f'<clipPath id="{prefix}CabClip"><rect x="760" y="200" width="84" height="44"/></clipPath>')

    # Styles & Keyframes
    p.append("<style>")
    p.append(f"""
      .led-pulse {{ animation: ledPulse 2s ease-in-out infinite; }}
      .ant-blink {{ animation: hardBlink 1.4s steps(1,end) infinite; }}
      .twinkle-a {{ animation: twinkle 3.2s ease-in-out infinite; }}
      .twinkle-b {{ animation: twinkle 4.1s ease-in-out 1.1s infinite; }}
      .twinkle-c {{ animation: twinkle 2.7s ease-in-out 1.9s infinite; }}
      .shoot-star {{ animation: shootStar 12s linear infinite; opacity: 0; }}
      .cloud-drift {{ animation: cloudDrift 18s linear infinite; }}
      .cat-eye {{ transform-box: fill-box; transform-origin: center; animation: catBlink 5.2s steps(1,end) infinite; }}
      .cat-tail {{ transform-box: fill-box; transform-origin: 0% 100%; animation: tailWag 3.2s ease-in-out infinite; }}
      .cursor-blink {{ animation: hardBlink 0.9s steps(1,end) infinite; }}
      .crt-sweep {{ animation: crtSweep 4.5s linear infinite; }}
      .curtain-1 {{ animation: cur1 10s steps(12,end) infinite; }}
      .curtain-2 {{ animation: cur2 10s steps(12,end) infinite; }}
      .curtain-3 {{ animation: cur3 10s steps(16,end) infinite; }}
      .curtain-4 {{ animation: cur4 10s steps(24,end) infinite; }}
      .vinyl-spin {{ transform-box: fill-box; transform-origin: center; animation: spin360 3.2s steps(16,end) infinite; }}
      .note-a {{ animation: noteFloat 4.2s ease-in-out infinite; }}
      .note-b {{ animation: noteFloat 4.2s ease-in-out 2.1s infinite; }}
      .steam-a {{ animation: steamUp 3.2s ease-out infinite; }}
      .steam-b {{ animation: steamUp 3.2s ease-out 1.1s infinite; }}
      .steam-c {{ animation: steamUp 3.2s ease-out 2.2s infinite; }}
      .rgb-key {{ animation: rgbPulse 2.8s ease-in-out infinite; }}
      .invader-patrol {{ animation: patrol 4.6s steps(10,end) infinite alternate; }}
      .xp-shimmer {{ animation: xpPulse 2.4s ease-in-out infinite; }}
      .glitch-cyan {{ animation: glitchA 6.5s steps(1,end) infinite; }}
      .glitch-mag {{ animation: glitchB 6.5s steps(1,end) infinite; }}
      .hero-pulse {{ animation: heroPulse 4s ease-in-out infinite; }}

      @keyframes ledPulse {{ 0%,100%{{opacity:0.45}} 50%{{opacity:1}} }}
      @keyframes hardBlink {{ 0%,49%{{opacity:1}} 50%,100%{{opacity:0.12}} }}
      @keyframes twinkle {{ 0%,100%{{opacity:0.2}} 50%{{opacity:1}} }}
      @keyframes shootStar {{
        0%, 74% {{ transform: translate(0,0); opacity: 0; }}
        76% {{ opacity: 1; }}
        84% {{ transform: translate(84px, 34px); opacity: 0; }}
        100% {{ opacity: 0; }}
      }}
      @keyframes cloudDrift {{
        0% {{ transform: translateX(-28px); }}
        100% {{ transform: translateX(260px); }}
      }}
      @keyframes catBlink {{
        0%, 90%, 96%, 100% {{ transform: scaleY(1); }}
        92%, 94% {{ transform: scaleY(0.15); }}
      }}
      @keyframes tailWag {{
        0%,100% {{ transform: rotate(0deg); }}
        50% {{ transform: rotate(8deg); }}
      }}
      @keyframes crtSweep {{
        0% {{ transform: translateY(-4px); opacity: 0; }}
        15% {{ opacity: 0.35; }}
        85% {{ opacity: 0.35; }}
        100% {{ transform: translateY(74px); opacity: 0; }}
      }}
      @keyframes cur1 {{
        0%, 88% {{ transform: translateX(176px); }}
        92%, 95% {{ transform: translateX(0); }}
        99%, 100% {{ transform: translateX(176px); }}
      }}
      @keyframes cur2 {{
        0% {{ transform: translateX(64px); }}
        14%, 88% {{ transform: translateX(176px); }}
        92%, 97% {{ transform: translateX(0); }}
        100% {{ transform: translateX(64px); }}
      }}
      @keyframes cur3 {{
        0%, 14% {{ transform: translateX(0); }}
        34%, 88% {{ transform: translateX(176px); }}
        92%, 100% {{ transform: translateX(0); }}
      }}
      @keyframes cur4 {{
        0%, 34% {{ transform: translateX(0); }}
        62%, 88% {{ transform: translateX(176px); }}
        92%, 100% {{ transform: translateX(0); }}
      }}
      @keyframes spin360 {{ to {{ transform: rotate(360deg); }} }}
      @keyframes noteFloat {{
        0% {{ transform: translate(0, 0); opacity: 0; }}
        20% {{ opacity: 1; }}
        80% {{ opacity: 0.9; }}
        100% {{ transform: translate(10px, -28px); opacity: 0; }}
      }}
      @keyframes steamUp {{
        0% {{ transform: translate(0, 0); opacity: 0; }}
        25% {{ opacity: 0.7; }}
        100% {{ transform: translate(-4px, -20px); opacity: 0; }}
      }}
      @keyframes rgbPulse {{
        0%,100% {{ opacity: 0.35; }}
        50% {{ opacity: 0.95; }}
      }}
      @keyframes patrol {{
        0% {{ transform: translateX(0); }}
        100% {{ transform: translateX(36px); }}
      }}
      @keyframes xpPulse {{
        0%,100% {{ opacity: 0.55; }}
        50% {{ opacity: 1; }}
      }}
      @keyframes heroPulse {{
        0%,100% {{ opacity: 0.94; }}
        50% {{ opacity: 1; }}
      }}
      @keyframes glitchA {{
        0%, 88%, 93%, 100% {{ transform: translate(0, 0); opacity: 0; }}
        89% {{ transform: translate(-3px, 1px); opacity: 0.75; }}
        91% {{ transform: translate(2px, -1px); opacity: 0.55; }}
      }}
      @keyframes glitchB {{
        0%, 88%, 93%, 100% {{ transform: translate(0, 0); opacity: 0; }}
        89% {{ transform: translate(3px, -1px); opacity: 0.75; }}
        91% {{ transform: translate(-2px, 1px); opacity: 0.55; }}
      }}
      @media (prefers-reduced-motion: reduce) {{
        * {{ animation: none !important; transition: none !important; }}
        .curtain-1, .curtain-2, .curtain-3, .curtain-4 {{ display: none !important; }}
        .shoot-star, .glitch-cyan, .glitch-mag {{ opacity: 0 !important; }}
      }}
    """)
    p.append("</style>")
    p.append("</defs>")

    # ---- Room Backdrop ----
    p.append(rect(0, 0, W, H, pal.bg, crisp=True))
    p.append(rect(0, 36, W, 256, f"url(#{prefix}Wall)", crisp=True))
    for wx in range(40, W, 80):
        p.append(rect(wx, 36, 4, 256, pal.bg_deep, opacity=0.35 if is_dark else 0.45, crisp=True))

    # Floor & Baseboard
    p.append(rect(0, 288, W, 4, pal.border, crisp=True))
    p.append(rect(0, 292, W, 40, floor_a, crisp=True))
    for fy in (304, 316, 328):
        p.append(rect(0, fy, W, 2, floor_b, opacity=0.65, crisp=True))
    # Pixel Rug under desk
    p.append(rect(108, 304, 624, 24, f"url(#{prefix}Rug)", stroke=pal.border, stroke_width=2, crisp=True))
    p.append(rect(116, 308, 608, 2, pal.cyan, opacity=0.45, crisp=True))

    # ---- Window (x=24..288, y=52..220) ----
    p.append(rect(24, 52, 264, 168, wood_frame, stroke=pal.border, stroke_width=2, crisp=True))
    p.append(rect(28, 56, 256, 4, wood_hi, crisp=True))
    # Sky bands with pixel dithering transitions
    p.append(f'<g clip-path="url(#{prefix}WinClip)" shape-rendering="crispEdges">')
    p.append(rect(32, 60, 248, 32, sky_bands[0]))
    p.append(rect(32, 92, 248, 24, f"url(#{prefix}Sky01)"))
    p.append(rect(32, 116, 248, 24, sky_bands[1]))
    p.append(rect(32, 140, 248, 20, f"url(#{prefix}Sky12)"))
    p.append(rect(32, 160, 248, 28, sky_bands[2]))
    p.append(rect(32, 188, 248, 24, f"url(#{prefix}Sky23)"))

    if is_dark:
        # Pixel moon
        p.append(rect(236, 72, 16, 16, celestial_col))
        p.append(rect(244, 72, 8, 8, sky_bands[0]))
        # Twinkling stars
        stars = [
            (48, 72, "twinkle-a"), (76, 84, "twinkle-b"), (104, 68, "twinkle-c"),
            (132, 92, "twinkle-a"), (160, 72, "twinkle-b"), (192, 88, "twinkle-c"),
            (212, 70, "twinkle-a"), (64, 108, "twinkle-c"), (116, 116, "twinkle-b"),
            (176, 108, "twinkle-a"), (252, 104, "twinkle-b"), (92, 132, "twinkle-a"),
            (204, 128, "twinkle-c"),
        ]
        for sx, sy, cls in stars:
            p.append(rect(sx, sy, 4, 4, "#F8FAFC", cls=cls))
        # Shooting star (~12s)
        p.append('<g class="shoot-star">')
        p.append(rect(68, 72, 8, 4, "#FFFFFF"))
        p.append(rect(60, 68, 8, 4, pal.cyan, opacity=0.7))
        p.append("</g>")
    else:
        # Daytime pixel sun + drifting pixel clouds
        p.append(rect(232, 72, 20, 20, celestial_col))
        p.append(rect(236, 76, 12, 12, "#FEF08A"))
        p.append('<g class="cloud-drift">')
        p.append(rect(40, 84, 36, 12, "#FFFFFF"))
        p.append(rect(48, 76, 20, 8, "#FFFFFF"))
        p.append(rect(144, 100, 44, 12, "#FFFFFF", opacity=0.9))
        p.append(rect(156, 92, 20, 8, "#FFFFFF", opacity=0.9))
        p.append("</g>")

    # Mountain ridge (Bogotá eastern hills)
    p.append(
        f'<path d="M32 192 L64 164 L96 176 L136 148 L176 176 L216 156 L252 172 L280 160 L280 212 L32 212 Z" '
        f'fill="{mountain_col}"/>'
    )
    # City buildings + lit windows + blinking rooftop antennas
    buildings = [
        (36, 172, 24, 40), (64, 156, 24, 56), (92, 180, 20, 32),
        (116, 148, 28, 64), (148, 168, 24, 44), (176, 152, 24, 60),
        (204, 176, 24, 36), (232, 160, 24, 52), (260, 176, 20, 36),
    ]
    for idx, (bx, by, bw, bh) in enumerate(buildings):
        p.append(rect(bx, by, bw, bh, building_col))
        # Rooftop antennas on two taller buildings
        if idx in (3, 5):
            ax = bx + bw // 2 - 2
            p.append(rect(ax, by - 12, 4, 12, pal.text_dim))
            p.append(rect(ax, by - 16, 4, 4, ant_blink, cls="ant-blink"))
        # Lit windows
        win_col = pal.amber if idx % 2 == 0 else (pal.cyan if is_dark else "#FDE68A")
        for wy in range(by + 6, 206, 10):
            for wx in range(bx + 4, bx + bw - 6, 8):
                if (wx + wy + idx) % 3 != 0:
                    p.append(rect(wx, wy, 4, 4, win_col, opacity=0.85 if is_dark else 0.9))

    # Window cross mullions
    p.append(rect(154, 60, 4, 152, wood_frame))
    p.append(rect(32, 134, 248, 4, wood_frame))
    p.append("</g>")

    # Window Sill
    p.append(rect(16, 216, 280, 12, wood_frame, stroke=pal.border, stroke_width=2, crisp=True))
    p.append(rect(18, 218, 276, 3, wood_hi, crisp=True))

    # Tiny Cactus on Sill (right)
    p.append(rect(244, 200, 16, 16, "#B45309", stroke=pal.border, stroke_width=1, crisp=True))
    p.append(rect(248, 184, 8, 16, pal.green, crisp=True))
    p.append(rect(244, 188, 4, 8, pal.green, crisp=True))
    p.append(rect(256, 190, 4, 6, pal.green, crisp=True))

    # Cute Pixel Cat on Sill (left) with blinking eyes & swaying tail
    cat_x, cat_y = 40, 176
    p.append(pixel_sprite(cat_x, cat_y, CAT_ROWS[:9], cat_colors, px=4))
    # Tail separate animated piece
    p.append('<g class="cat-tail" shape-rendering="crispEdges">')
    p.append(rect(cat_x + 44, cat_y + 24, 8, 4, cat_colors["#"]))
    p.append(rect(cat_x + 48, cat_y + 20, 4, 8, cat_colors["#"]))
    p.append("</g>")
    # Cat collar & blinking eye overlay
    p.append(rect(cat_x + 8, cat_y + 20, 24, 3, pal.magenta, crisp=True))
    p.append('<g class="cat-eye" shape-rendering="crispEdges">')
    p.append(rect(cat_x + 8, cat_y + 12, 4, 4, cat_colors["W"]))
    p.append(rect(cat_x + 28, cat_y + 12, 4, 4, cat_colors["W"]))
    p.append("</g>")

    # ---- Right Wall Hero Name Signboard (x=512..876, y=48..176) ----
    p.append(rpg_panel(512, 48, 364, 128, pal, accent=pal.cyan, chamfer=8, shadow=4))
    p.append(mono_text(532, 72, "PLAYER 1 · READY", size=11, fill=pal.cyan, weight=700, spacing=1.2))
    p.append(mono_text(856, 72, f"{tz_label}", size=11, fill=pal.green, anchor="end", weight=700, spacing=1.0))

    # Main Title "NICOLÁS" with subtle glitch + neon pulse
    title_x = 694
    title_y = 80
    p.append(
        pixel_text(
            title_x, title_y, display_name, px=6,
            fill=pal.cyan, cls="glitch-cyan", anchor="middle", letter_gap=1,
        )
    )
    p.append(
        pixel_text(
            title_x, title_y, display_name, px=6,
            fill=pal.magenta, cls="glitch-mag", anchor="middle", letter_gap=1,
        )
    )
    p.append(
        pixel_text(
            title_x, title_y, display_name, px=6,
            fill=pal.text,
            shadow=pal.magenta if is_dark else pal.cyan,
            shadow_offset=3,
            anchor="middle",
            letter_gap=1,
            cls="hero-pulse",
            filter_id=f"{prefix}Glow" if is_dark else None,
        )
    )
    p.append(line(532, 144, 856, 144, pal.border, width=1.5))
    p.append(rect(634, 143, 120, 3, pal.magenta, crisp=True))
    p.append(
        mono_text(
            694, 163,
            f"{full_name.upper()} · {semester.upper()}",
            size=10.5, fill=pal.text_muted, anchor="middle", weight=700, spacing=0.7,
        )
    )

    # ---- Desk (x=120..720, y=224..292) ----
    p.append(rect(120, 224, 596, 12, desk_top, stroke=pal.border, stroke_width=2, crisp=True))
    p.append(rect(122, 226, 592, 3, desk_bevel, crisp=True))
    p.append(rect(128, 236, 580, 16, desk_front, stroke=pal.border, stroke_width=1.5, crisp=True))
    p.append(rect(136, 252, 16, 40, desk_front, stroke=pal.border, stroke_width=1.5, crisp=True))
    p.append(rect(684, 252, 16, 40, desk_front, stroke=pal.border, stroke_width=1.5, crisp=True))

    # ---- Turntable / Vinyl Player (x=136..244, y=180..224) ----
    p.append(rect(136, 184, 108, 40, pal.card, stroke=pal.border, stroke_width=2, crisp=True))
    p.append(rect(140, 188, 100, 4, pal.amber, opacity=0.85, crisp=True))
    # Spinning pixel vinyl record
    p.append('<g class="vinyl-spin">')
    p.append(f'<circle cx="176" cy="206" r="14" fill="#0F172A" stroke="{pal.border_hi}" stroke-width="2"/>')
    p.append(f'<circle cx="176" cy="206" r="6" fill="{pal.magenta}"/>')
    p.append(f'<circle cx="176" cy="206" r="2" fill="{pal.text}"/>')
    p.append(rect(175, 194, 2, 4, pal.text_muted, crisp=True))
    p.append("</g>")
    # Tonearm & slider
    p.append(f'<path d="M204 192 L204 206 L194 212" fill="none" stroke="{pal.text_muted}" stroke-width="2.5"/>')
    p.append(rect(216, 200, 16, 4, pal.cyan, crisp=True))
    p.append(rect(216, 208, 16, 4, pal.green, crisp=True))
    # Floating pixel music notes
    p.append('<g class="note-a">' + pixel_sprite(196, 162, NOTE_ROWS, {"#": pal.magenta}, px=2) + "</g>")
    p.append('<g class="note-b">' + pixel_sprite(214, 168, NOTE_ROWS, {"#": pal.cyan}, px=2) + "</g>")

    # ---- Main CRT Monitor (x=284..500, y=112..224) ----
    p.append(rect(288, 112, 208, 100, crt_case, stroke=pal.border, stroke_width=2, crisp=True))
    p.append(rect(290, 114, 204, 4, crt_bevel, crisp=True))
    # Stand
    p.append(rect(368, 212, 48, 6, pal.border_hi, crisp=True))
    p.append(rect(352, 218, 80, 6, crt_case, stroke=pal.border, stroke_width=1.5, crisp=True))
    # Screen cavity
    p.append(rect(300, 124, 184, 80, pal.border, crisp=True))
    p.append(rect(304, 128, 176, 72, crt_scr, crisp=True))
    # Typing terminal lines (4 lines, crisp 10px monospace + sliding curtain reveal)
    line_specs = [
        (term_lines[0], pal.cyan if is_dark else "#38BDF8", 144, "curtain-1"),
        (term_lines[1], "#E6EDF3", 160, "curtain-2"),
        (term_lines[2], pal.amber if is_dark else "#FBBF24", 176, "curtain-3"),
        (term_lines[3], pal.green if is_dark else "#4ADE80", 192, "curtain-4"),
    ]
    p.append(f'<g clip-path="url(#{prefix}CrtClip)">')
    for content, col, ly, ccls in line_specs:
        p.append(mono_text(312, ly, content, size=10, fill=col, weight=700))
        p.append(rect(310, ly - 11, 172, 14, crt_scr, cls=ccls, crisp=True))
    p.append(rect(304, 128, 176, 3, pal.cyan, opacity=0.35, cls="crt-sweep", crisp=True))
    p.append("</g>")
    # Blinking cursor
    p.append(rect(468, 183, 7, 10, "#38BDF8" if not is_dark else pal.cyan, cls="cursor-blink", crisp=True))
    # Monitor power LED
    p.append(rect(480, 206, 4, 4, pal.green, cls="led-pulse", crisp=True))

    # ---- Mechanical Keyboard with RGB Wave (x=296..488, y=220..236? wait: sit on desk top at y=214..224 or front desk edge) ----
    # Place keyboard cleanly on desk surface in front of monitor stand (y=220..232)
    p.append(rect(300, 220, 184, 12, kb_body, stroke=pal.border, stroke_width=1.5, crisp=True))
    p.append(rect(302, 221, 180, 2, kb_hi, crisp=True))
    rgb_cols = [pal.cyan, pal.magenta, pal.amber, pal.green]
    for ki in range(14):
        kx = 308 + ki * 12
        kc = rgb_cols[ki % len(rgb_cols)]
        delay = f"{(ki * 0.16):.2f}s"
        p.append(rect(kx, 224, 8, 4, kc, cls="rgb-key", crisp=True, style=f"animation-delay:{delay}"))

    # ---- Coffee Mug with Rising Pixel Steam (x=520..552, y=196..224) ----
    p.append(rect(520, 200, 24, 24, mug_col, stroke=pal.border, stroke_width=2, crisp=True))
    p.append(rect(522, 202, 20, 3, mug_hi, crisp=True))
    p.append(rect(544, 206, 6, 12, mug_col, stroke=pal.border, stroke_width=1.5, crisp=True))
    p.append(rect(526, 210, 12, 4, pal.magenta, crisp=True))
    p.append(rect(524, 188, 4, 8, steam_col, cls="steam-a", crisp=True))
    p.append(rect(532, 186, 4, 8, steam_col, cls="steam-b", crisp=True))
    p.append(rect(538, 190, 4, 6, steam_col, cls="steam-c", crisp=True))

    # ---- Mini Arcade Cabinet (x=744..876, y=184..292) ----
    p.append(rect(748, 184, 124, 108, cab_body, stroke=pal.border, stroke_width=2, crisp=True))
    p.append(rect(752, 188, 116, 12, cab_trim, crisp=True))
    p.append(mono_text(810, 198, "ARCADE", size=9.5, fill="#FFFFFF" if not is_dark else pal.amber, anchor="middle", weight=700, spacing=1.6))
    # Mini Screen
    p.append(rect(758, 204, 104, 44, cab_scr, stroke=pal.border_hi, stroke_width=1.5, crisp=True))
    p.append(f'<g clip-path="url(#{prefix}CabClip)" shape-rendering="crispEdges">')
    p.append('<g class="invader-patrol">')
    p.append(pixel_sprite(768, 210, INVADER_ROWS, {"#": pal.magenta}, px=3))
    p.append(pixel_sprite(796, 224, INVADER_ROWS, {"#": pal.cyan}, px=3))
    p.append("</g>")
    p.append(rect(798, 240, 16, 4, pal.green))
    p.append("</g>")
    # Control deck & coin door
    p.append(rect(744, 252, 132, 10, cab_trim, stroke=pal.border, stroke_width=1.5, crisp=True))
    p.append(rect(760, 248, 4, 6, pal.amber, crisp=True))
    p.append(rect(828, 255, 6, 4, pal.magenta, crisp=True))
    p.append(rect(840, 255, 6, 4, pal.cyan, crisp=True))
    p.append(rect(784, 268, 52, 20, pal.bg_deep, stroke=pal.border, stroke_width=1.5, crisp=True))
    p.append(rect(796, 274, 8, 8, pal.amber, cls="led-pulse", crisp=True))
    p.append(rect(816, 274, 8, 8, pal.amber, cls="led-pulse", crisp=True))

    # ---- Top HUD Bar (y=0..36) ----
    p.append(rect(0, 0, W, 36, pal.bg_deep, crisp=True))
    p.append(line(0, 36, W, 36, pal.border, width=2))
    p.append(rect(0, 34, W, 2, pal.cyan, opacity=0.65, crisp=True))
    p.append(pixel_sprite(14, 10, HEART_ROWS, {"#": pal.magenta}, px=2.5))
    p.append(mono_text(38, 23, f"P1 · {display_name}", size=12.5, fill=pal.text, weight=700, spacing=1.0))
    # ONLINE + LED
    p.append(rect(192, 14, 8, 8, pal.green, cls="led-pulse", crisp=True))
    p.append(mono_text(208, 23, "ONLINE", size=12, fill=pal.green, weight=700, spacing=1.0))
    # CLASS
    p.append(mono_text(308, 23, f"CLASS: {class_tag}", size=12, fill=pal.cyan, weight=700, spacing=0.8))
    # Decorative XP bar
    p.append(mono_text(532, 23, "XP", size=12, fill=pal.amber, weight=700, spacing=1.0))
    p.append(segmented_bar(558, 12, 8, 12, pal.amber, pal, seg_w=12, seg_h=12, gap=3))
    p.append(rect(558 + 8 * 15, 12, 12, 12, pal.cyan, cls="xp-shimmer", crisp=True))
    p.append(mono_text(882, 23, "LVL 03", size=12, fill=pal.text_muted, anchor="end", weight=700, spacing=1.0))

    # ---- Bottom Status Bar (y=332..360) ----
    p.append(rect(0, 332, W, 28, pal.bg_deep, crisp=True))
    p.append(line(0, 332, W, 332, pal.border, width=2))
    p.append(mono_text(16, 350, f"{location.upper()} · {tz_label}", size=11, fill=pal.text_muted, weight=700, spacing=0.8))
    p.append(mono_text(450, 350, "IA · CIBERSEGURIDAD · DISEÑO · CÓDIGO", size=11, fill=pal.cyan, anchor="middle", weight=700, spacing=0.8))
    p.append(mono_text(884, 350, config.get("handle", "NICOLÁS.OS"), size=11, fill=pal.magenta, anchor="end", weight=700, spacing=0.8))

    # ---- CRT Scanlines + Frame Border ----
    p.append(rect(0, 0, W, H, f"url(#{prefix}Scan)", crisp=True))
    p.append(rect(1, 1, W - 2, H - 2, "none", stroke=pal.border, stroke_width=2, crisp=True))
    p.append("</svg>")
    return "\n".join(p)


def generate_hero(config: dict[str, Any] | None = None) -> list[pathlib.Path]:
    cfg = config or load_config()
    ASSETS.mkdir(parents=True, exist_ok=True)
    written: list[pathlib.Path] = []
    for mode in ("dark", "light"):
        out = ASSETS / f"hero-{mode}.svg"
        out.write_text(_build_scene(cfg, mode), encoding="utf-8")
        written.append(out)
        print(f"wrote {out.name} ({out.stat().st_size:,} bytes)")
    return written


if __name__ == "__main__":
    generate_hero()
