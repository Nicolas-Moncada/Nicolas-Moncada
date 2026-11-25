#!/usr/bin/env python3
"""Master orchestrator for Nicolás Moncada's 16-bit GitHub Profile Engine.

Runs all SVG generators (dark & light), audits generated SVGs for GitHub
compatibility and accessibility, updates README.md and .heartbeat, and
optionally generates a local preview.html (gitignored).
"""
from __future__ import annotations

import argparse
import html
import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET
from typing import Any

# Ensure sibling imports work regardless of invocation CWD
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from design_system import ASSETS, ROOT, load_config  # noqa: E402
from gen_contact import active_contact_links, generate_contact  # noqa: E402
from gen_contributions import generate_contributions  # noqa: E402
from gen_footer import generate_footer  # noqa: E402
from gen_hero import generate_hero  # noqa: E402
from gen_lab import generate_lab  # noqa: E402
from gen_player import generate_player  # noqa: E402
from gen_stages import generate_stages  # noqa: E402

MAX_SVG_BYTES = 250 * 1024
EXTERNAL_URL_RE = re.compile(r'(?:href|xlink:href|src)\s*=\s*["\']https?://|url\(\s*["\']?https?://', re.I)


def _picture_block(dark_rel: str, light_rel: str, alt: str, width: str = "100%") -> str:
    safe_alt = html.escape(alt, quote=True)
    return (
        "<picture>\n"
        f'  <source media="(prefers-color-scheme: dark)" srcset="{dark_rel}" />\n'
        f'  <source media="(prefers-color-scheme: light)" srcset="{light_rel}" />\n'
        f'  <img src="{dark_rel}" width="{width}" alt="{safe_alt}" />\n'
        "</picture>"
    )


def _plural(n: int, one: str, many: str) -> str:
    return one if n == 1 else many


def render_readme(
    cfg: dict[str, Any],
    repos: list[dict[str, Any]],
    stats: dict[str, Any],
    links: list[dict[str, str]],
) -> str:
    login = cfg["github_username"]
    full_name = cfg.get("full_name", "Nicolás Moncada Montaño")
    role = cfg.get("role", "Estudiante de Ingeniería de Sistemas")
    semester = cfg.get("semester", "3er semestre · UNIMINUTO")
    location = cfg.get("location", "Bogotá, Colombia")
    bio_paragraphs = list(cfg.get("bio") or [])
    attributes = list(cfg.get("attributes") or [])
    stack = list(cfg.get("stack") or [])
    interests = list(cfg.get("interests") or [])
    custom_descs = (cfg.get("lab") or {}).get("repo_descriptions") or {}

    total_contrib = int(stats.get("total_contributions", 0))
    active_days = int(stats.get("active_days", 0))
    streak = int(stats.get("current_streak", 0))
    best_streak = int(stats.get("longest_streak", 0))
    public_repos = int(stats.get("public_repos", 0))
    stamp_local = str(stats.get("updated_local", ""))
    stamp_utc = str(stats.get("updated_utc", ""))

    # Build project cards HTML (<a href="..."><picture>...</picture></a>)
    if repos:
        card_blocks: list[str] = []
        for idx, repo in enumerate(repos, start=1):
            rname = repo["name"]
            rlang = repo.get("language") or "Otro"
            rdesc = custom_descs.get(rname) or repo.get("description") or "Proyecto público en desarrollo"
            rurl = repo.get("url") or f"https://github.com/{login}/{rname}"
            pic = _picture_block(
                f"./assets/lab-card-{idx}-dark.svg",
                f"./assets/lab-card-{idx}-light.svg",
                f"Cartucho de proyecto {rname} ({rlang}): {rdesc}",
                width="430",
            )
            card_blocks.append(f'<a href="{html.escape(rurl, quote=True)}">\n{pic}\n</a>')

        if len(repos) % 2 == 1:
            slot = len(repos) + 1
            next_pic = _picture_block(
                f"./assets/lab-next-{slot}-dark.svg",
                f"./assets/lab-next-{slot}-light.svg",
                "Próximo nivel en construcción — ver todos los repositorios",
                width="430",
            )
            card_blocks.append(f'<a href="https://github.com/{login}?tab=repositories">\n{next_pic}\n</a>')

        lab_visual = '<div align="center">\n' + "\n".join(card_blocks) + "\n</div>"

        repo_rows = []
        for repo in repos:
            rname = repo["name"]
            rlang = repo.get("language") or "Otro"
            rdesc = custom_descs.get(rname) or repo.get("description") or "Repositorio público en desarrollo"
            rurl = repo.get("url") or f"https://github.com/{login}/{rname}"
            stars = int(repo.get("stars", 0))
            star_txt = f"★ {stars}" if stars > 0 else "—"
            repo_rows.append(f"| [{rname}]({rurl}) | {rlang} | {star_txt} | {rdesc} |")
        lab_accessible = (
            "<details>\n"
            "<summary>Índice accesible de repositorios públicos</summary>\n\n"
            "| Proyecto | Lenguaje | Estrellas | Descripción |\n"
            "| :--- | :--- | :---: | :--- |\n"
            + "\n".join(repo_rows)
            + "\n\n</details>"
        )
    else:
        lab_visual = (
            '<div align="center">\n'
            + _picture_block(
                "./assets/lab-empty-dark.svg",
                "./assets/lab-empty-light.svg",
                "Próximo nivel en construcción",
                width="100%",
            )
            + "\n</div>"
        )
        lab_accessible = "_Próximo nivel en construcción: pronto habrá nuevos repositorios públicos aquí._"

    # Build contact section
    if links:
        btn_blocks: list[str] = []
        md_links: list[str] = []
        for item in links:
            cid = item["id"]
            label = item.get("label", cid)
            sublabel = item.get("sublabel") or item["url"]
            url = item["url"]
            pic = _picture_block(
                f"./assets/contact-{cid}-dark.svg",
                f"./assets/contact-{cid}-light.svg",
                f"Abrir {label}: {sublabel}",
                width="290",
            )
            btn_blocks.append(f'<a href="{html.escape(url, quote=True)}">\n{pic}\n</a>')
            md_links.append(f"- **{label}:** [{sublabel}]({url})")
        contact_visual = '<div align="center">\n' + "\n".join(btn_blocks) + "\n</div>"
        contact_md = "\n".join(md_links)
    else:
        contact_visual = (
            '<div align="center">\n'
            + _picture_block(
                "./assets/contact-empty-dark.svg",
                "./assets/contact-empty-light.svg",
                "Canal en configuración",
                width="100%",
            )
            + "\n</div>"
        )
        contact_md = "_Canales de contacto en configuración (`profile.config.json`)._"

    # Build accessible tables for Stage 02 (Stack & Attributes)
    stack_rows = "\n".join(
        f"| {s['name']} | `{s['level']}` |" for s in stack
    )
    attr_rows = "\n".join(
        f"| {a['name']} | {a['detail']} | `{a['level']}` |" for a in attributes
    )

    bio_md = "\n\n".join(bio_paragraphs)
    interests_md = " · ".join(f"`{item}`" for item in interests)

    parts = [
        "<!--",
        "  PROFILE ENGINE v2.0 · 16-bit Arcade Edition",
        "  Generado automáticamente por scripts/build_all.py (Python + SVG puro).",
        "  Datos reales de GitHub sin métricas inventadas.",
        "-->",
        "",
        '<div align="center">',
        _picture_block(
            "./assets/hero-dark.svg",
            "./assets/hero-light.svg",
            f"Escena pixel art de {full_name}: habitación gamer en {location} con monitor CRT, teclado RGB, tocadiscos, taza de café, mini arcade y mascota.",
            width="100%",
        ),
        "</div>",
        "",
        '<p align="center">',
        "  <sub>",
        '    <a href="#stage-01">STAGE 01 · SOBRE MÍ</a> &nbsp;·&nbsp;',
        '    <a href="#stage-02">STAGE 02 · ARSENAL</a> &nbsp;·&nbsp;',
        '    <a href="#stage-03">STAGE 03 · LABORATORIO</a> &nbsp;·&nbsp;',
        '    <a href="#stage-04">STAGE 04 · ACTIVIDAD</a> &nbsp;·&nbsp;',
        '    <a href="#stage-05">STAGE 05 · CONEXIÓN</a>',
        "  </sub>",
        "</p>",
        "",
        '<a id="stage-01"></a>',
        "",
        '<div align="center">',
        _picture_block("./assets/stage-01-dark.svg", "./assets/stage-01-light.svg", "Stage 01 — Sobre mí", width="100%"),
        "</div>",
        "",
        f"**{full_name}** · {role} ({semester}) · {location}.",
        "",
        bio_md,
        "",
        f"**Intereses:** {interests_md}",
        "",
        '<a id="stage-02"></a>',
        "",
        '<div align="center">',
        _picture_block("./assets/stage-02-dark.svg", "./assets/stage-02-light.svg", "Stage 02 — Arsenal y stats", width="100%"),
        "</div>",
        "",
        '<div align="center">',
        _picture_block(
            "./assets/player-card-dark.svg",
            "./assets/player-card-light.svg",
            f"Ficha de jugador de {full_name}: avatar pixel art, atributos, intereses y stack técnico cualitativo.",
            width="100%",
        ),
        "</div>",
        "",
        "<details>",
        "<summary>Ficha técnica accesible (atributos y stack cualitativo)</summary>",
        "",
        "| Atributo | Enfoque | Nivel |",
        "| :--- | :--- | :---: |",
        attr_rows,
        "",
        "| Tecnología | Nivel cualitativo |",
        "| :--- | :---: |",
        stack_rows,
        "",
        "</details>",
        "",
        '<a id="stage-03"></a>',
        "",
        '<div align="center">',
        _picture_block("./assets/stage-03-dark.svg", "./assets/stage-03-light.svg", "Stage 03 — Laboratorio", width="100%"),
        "</div>",
        "",
        lab_visual,
        "",
        lab_accessible,
        "",
        '<a id="stage-04"></a>',
        "",
        '<div align="center">',
        _picture_block("./assets/stage-04-dark.svg", "./assets/stage-04-light.svg", "Stage 04 — Actividad en vivo", width="100%"),
        "</div>",
        "",
        '<div align="center">',
        _picture_block(
            "./assets/contributions-dark.svg",
            "./assets/contributions-light.svg",
            f"Mapa de calor pixel de contribuciones de {login}: {total_contrib} contribuciones, {active_days} días activos, racha {streak} y {public_repos} repositorios públicos.",
            width="100%",
        ),
        "</div>",
        "",
        "<details>",
        "<summary>Resumen de telemetría pública de GitHub</summary>",
        "",
        f"- **Usuario:** `@{login}`",
        f"- **Contribuciones (año):** {total_contrib}",
        f"- **Racha actual:** {streak} {_plural(streak, 'día', 'días')} (mejor racha: {best_streak})",
        f"- **Días activos:** {active_days}",
        f"- **Repositorios públicos:** {public_repos}",
        f"- **Última sincronización:** `{stamp_utc}`",
        "",
        "</details>",
        "",
        '<a id="stage-05"></a>',
        "",
        '<div align="center">',
        _picture_block("./assets/stage-05-dark.svg", "./assets/stage-05-light.svg", "Stage 05 — Conexión", width="100%"),
        "</div>",
        "",
        contact_visual,
        "",
        contact_md,
        "",
        '<div align="center">',
        _picture_block(
            "./assets/footer-dark.svg",
            "./assets/footer-light.svg",
            f"Insert Coin — Gracias por jugar · Sync {stamp_utc}",
            width="100%",
        ),
        "</div>",
        "",
        '<div align="center">',
        f'  <sub><!-- LAST_ACTIVE_START -->⚡ <b>Profile Engine v2.0</b> · {total_contrib} {_plural(total_contrib, "contribución", "contribuciones")} · {active_days} {_plural(active_days, "día activo", "días activos")} · racha {streak} · {public_repos} repos públicos · sync {stamp_local}<!-- LAST_ACTIVE_END --></sub>',
        "</div>",
        "",
    ]
    return "\n".join(parts)


def update_heartbeat(stats: dict[str, Any]) -> None:
    heartbeat = {
        "status": "active",
        "engine": "profile-engine-v2",
        "timezone": "America/Bogota",
        "last_sync_local": stats.get("updated_local"),
        "last_sync_utc": stats.get("updated_iso") or stats.get("updated_utc"),
        "source": stats.get("source"),
        "profile": {
            "login": stats.get("login"),
            "total_contributions": int(stats.get("total_contributions", 0)),
            "active_days": int(stats.get("active_days", 0)),
            "current_streak": int(stats.get("current_streak", 0)),
            "longest_streak": int(stats.get("longest_streak", 0)),
            "commits": int(stats.get("commits", 0)),
            "pull_requests": int(stats.get("pull_requests", 0)),
            "issues": int(stats.get("issues", 0)),
            "public_repos": int(stats.get("public_repos", 0)),
            "days_on_github": int(stats.get("days_on_github", 0)),
            "account_created": stats.get("account_created"),
        },
        "data_policy": "public GitHub data only; no invented metrics",
    }
    (ROOT / ".heartbeat").write_text(json.dumps(heartbeat, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def validate_svgs(assets_dir: pathlib.Path = ASSETS) -> list[str]:
    """Audit all generated SVGs for XML validity, weight, self-containment, and reduced-motion."""
    errors: list[str] = []
    svg_files = sorted(assets_dir.glob("*.svg"))
    if not svg_files:
        return ["No se encontraron archivos .svg en assets/"]

    for svg_path in svg_files:
        raw = svg_path.read_text(encoding="utf-8")
        size_bytes = svg_path.stat().st_size

        try:
            root = ET.fromstring(raw)
        except ET.ParseError as exc:
            errors.append(f"{svg_path.name}: XML inválido ({exc})")
            continue

        if "viewBox" not in root.attrib:
            errors.append(f"{svg_path.name}: falta atributo viewBox")
        if root.attrib.get("width") != "100%":
            errors.append(f"{svg_path.name}: width debe ser '100%' para responsive")

        if size_bytes >= MAX_SVG_BYTES:
            errors.append(f"{svg_path.name}: excede 250 KB ({size_bytes:,} bytes)")

        lower = raw.lower()
        if "<script" in lower or "<iframe" in lower:
            errors.append(f"{svg_path.name}: contiene etiqueta prohibida (<script> o <iframe>)")

        if EXTERNAL_URL_RE.search(raw):
            errors.append(f"{svg_path.name}: contiene referencia URL externa (http/https)")

        if "prefers-reduced-motion" not in lower:
            errors.append(f"{svg_path.name}: falta @media (prefers-reduced-motion: reduce)")

        print(f"  [OK] {svg_path.name:30s} {size_bytes:7,d} bytes")

    return errors


def build_preview_html(cfg: dict[str, Any], repos: list[dict[str, Any]], links: list[dict[str, str]]) -> pathlib.Path:
    """Create local preview.html (gitignored) showing 400px & 900px in light & dark modes."""
    def _section_stack(mode: str, is_mobile: bool) -> str:
        card_w = "100%" if is_mobile else "430px"
        btn_w = "100%" if is_mobile else "290px"
        cards_html = []
        if repos:
            for idx, _ in enumerate(repos, start=1):
                cards_html.append(f'<img src="./assets/lab-card-{idx}-{mode}.svg" style="width:{card_w};max-width:100%;height:auto;display:block;" />')
            if len(repos) % 2 == 1:
                slot = len(repos) + 1
                cards_html.append(f'<img src="./assets/lab-next-{slot}-{mode}.svg" style="width:{card_w};max-width:100%;height:auto;display:block;" />')
        else:
            cards_html.append(f'<img src="./assets/lab-empty-{mode}.svg" style="width:100%;height:auto;display:block;" />')

        btns_html = []
        if links:
            for item in links:
                cid = item["id"]
                btns_html.append(f'<img src="./assets/contact-{cid}-{mode}.svg" style="width:{btn_w};max-width:100%;height:auto;display:block;" />')
        else:
            btns_html.append(f'<img src="./assets/contact-empty-{mode}.svg" style="width:100%;height:auto;display:block;" />')

        grid_style = "display:flex;flex-wrap:wrap;justify-content:center;gap:12px;"
        return f"""
        <div class="stack">
          <img src="./assets/hero-{mode}.svg" class="full" />
          <img src="./assets/stage-01-{mode}.svg" class="full" />
          <img src="./assets/stage-02-{mode}.svg" class="full" />
          <img src="./assets/player-card-{mode}.svg" class="full" />
          <img src="./assets/stage-03-{mode}.svg" class="full" />
          <div style="{grid_style}">{"".join(cards_html)}</div>
          <img src="./assets/stage-04-{mode}.svg" class="full" />
          <img src="./assets/contributions-{mode}.svg" class="full" />
          <img src="./assets/stage-05-{mode}.svg" class="full" />
          <div style="{grid_style}">{"".join(btns_html)}</div>
          <img src="./assets/footer-{mode}.svg" class="full" />
        </div>
        """

    html_doc = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Preview Profile Engine v2.0 — {html.escape(cfg.get("github_username", ""))}</title>
<style>
  body {{ margin: 0; padding: 24px; font-family: system-ui, sans-serif; background: #1e293b; color: #e2e8f0; }}
  h1, h2 {{ margin: 0 0 12px; font-size: 15px; letter-spacing: 0.04em; text-transform: uppercase; }}
  .viewport-label {{ margin: 28px 0 10px; color: #94a3b8; }}
  .frame {{ padding: 16px; border-radius: 8px; box-sizing: border-box; border: 1px solid #30363d; margin-bottom: 24px; }}
  .frame.dark {{ background: #0d1117; color: #e6edf3; }}
  .frame.light {{ background: #ffffff; color: #1f2328; border-color: #d0d7de; }}
  .w900 {{ width: 932px; max-width: 100%; }}
  .w400 {{ width: 432px; max-width: 100%; }}
  .stack {{ display: flex; flex-direction: column; gap: 14px; }}
  img.full {{ width: 100%; height: auto; display: block; }}
</style>
</head>
<body>
  <h1>GitHub Profile Preview (Dark &amp; Light · 900px &amp; 400px)</h1>

  <h2 class="viewport-label">Desktop 900px · Dark Mode (#0d1117)</h2>
  <div id="desktop-dark" class="frame dark w900">{_section_stack("dark", False)}</div>

  <h2 class="viewport-label">Desktop 900px · Light Mode (#ffffff)</h2>
  <div id="desktop-light" class="frame light w900">{_section_stack("light", False)}</div>

  <h2 class="viewport-label">Mobile 400px · Dark Mode (#0d1117)</h2>
  <div id="mobile-dark" class="frame dark w400">{_section_stack("dark", True)}</div>

  <h2 class="viewport-label">Mobile 400px · Light Mode (#ffffff)</h2>
  <div id="mobile-light" class="frame light w400">{_section_stack("light", True)}</div>
</body>
</html>
"""
    out = ROOT / "preview.html"
    out.write_text(html_doc, encoding="utf-8")
    print(f"wrote {out.name} (gitignored local preview)")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Build & audit all GitHub profile SVGs and README.")
    parser.add_argument("--validate-only", action="store_true", help="Only validate existing assets/*.svg")
    parser.add_argument("--preview", action="store_true", help="Also generate gitignored preview.html")
    args = parser.parse_args()

    if args.validate_only:
        print("── Auditoría SVG ────────────────────────")
        errs = validate_svgs()
        if errs:
            for err in errs:
                print(f"[ERROR] {err}")
            raise SystemExit(1)
        print("Todos los SVGs pasaron la auditoría.")
        return

    cfg = load_config()
    print("── Generando assets ─────────────────────")
    generate_hero(cfg)
    generate_stages(cfg)
    generate_player(cfg)
    repos, _ = generate_lab(cfg)
    stats, _ = generate_contributions(cfg)
    links, _ = generate_contact(cfg)
    generate_footer(cfg, sync_utc=stats["updated_utc"])

    readme_text = render_readme(cfg, repos, stats, links)
    (ROOT / "README.md").write_text(readme_text, encoding="utf-8")
    print("wrote README.md")

    update_heartbeat(stats)
    print("wrote .heartbeat")

    if args.preview:
        build_preview_html(cfg, repos, links)

    print("── Auditoría SVG ────────────────────────")
    errs = validate_svgs()
    if errs:
        for err in errs:
            print(f"[ERROR] {err}")
        raise SystemExit(1)
    print("Build completo y auditoría SVG aprobada.")


if __name__ == "__main__":
    main()
