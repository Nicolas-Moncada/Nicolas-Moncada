#!/usr/bin/env python3
"""Inject the real public stats into README.md and .heartbeat."""
from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
HEARTBEAT = ROOT / ".heartbeat"
STATS = ROOT / "assets" / "contributions.json"


def plural(n: int, one: str, many: str) -> str:
    return one if n == 1 else many


def main() -> None:
    if not STATS.exists():
        raise SystemExit(f"missing {STATS}; run build_contributions.py first")
    data = json.loads(STATS.read_text(encoding="utf-8"))

    total = int(data.get("total_contributions", 0))
    active = int(data.get("active_days", 0))
    streak = int(data.get("current_streak", 0))
    stamp = data.get("updated_local", "sin fecha")

    block = (
        "<!-- LAST_ACTIVE_START -->"
        f'⚡ <b>Motor activo</b> · {total} {plural(total, "contribución", "contribuciones")} · '
        f'{active} {plural(active, "día activo", "días activos")} · '
        f'racha {streak} · sync {stamp}'
        "<!-- LAST_ACTIVE_END -->"
    )

    text = README.read_text(encoding="utf-8")
    pattern = re.compile(r"<!-- LAST_ACTIVE_START -->.*?<!-- LAST_ACTIVE_END -->", re.S)
    if not pattern.search(text):
        raise SystemExit("LAST_ACTIVE markers not found in README.md")
    README.write_text(pattern.sub(block, text, count=1), encoding="utf-8")

    heartbeat = {
        "status": "active",
        "engine": "profile-engine",
        "timezone": "America/Bogota",
        "last_sync_local": stamp,
        "last_sync_utc": data.get("updated_utc"),
        "profile": {
            "login": data.get("login"),
            "total_contributions": total,
            "active_days": active,
            "current_streak": streak,
            "longest_streak": int(data.get("longest_streak", 0)),
            "commits": int(data.get("commits", 0)),
            "pull_requests": int(data.get("pull_requests", 0)),
            "issues": int(data.get("issues", 0)),
            "public_repos": int(data.get("public_repos", 0)),
            "days_on_github": int(data.get("days_on_github", 0)),
            "account_created": data.get("account_created"),
        },
        "data_policy": "public GitHub data only; no invented metrics",
    }
    HEARTBEAT.write_text(json.dumps(heartbeat, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"heartbeat -> {stamp} · {total} contribuciones · {active} días activos")


if __name__ == "__main__":
    main()
