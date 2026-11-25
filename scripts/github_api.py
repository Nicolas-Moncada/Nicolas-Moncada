#!/usr/bin/env python3
"""Lightweight GitHub REST + GraphQL client using Python standard library only."""
from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import urllib.error
import urllib.request
from typing import Any

USER_AGENT = "nicolas-profile-engine/2.0"

CONTRIB_QUERY = """
query($login: String!) {
  user(login: $login) {
    login
    name
    createdAt
    followers { totalCount }
    repositories(privacy: PUBLIC, ownerAffiliations: OWNER) { totalCount }
    contributionsCollection {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
            weekday
          }
        }
      }
    }
  }
}
"""


def _http_json(
    url: str,
    *,
    method: str = "GET",
    data: dict[str, Any] | None = None,
    token: str | None = None,
    timeout: int = 12,
) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    raw_body: bytes | None = None
    if data is not None:
        headers["Content-Type"] = "application/json"
        raw_body = json.dumps(data).encode("utf-8")

    req = urllib.request.Request(url, data=raw_body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_user_profile(login: str, token: str | None = None) -> dict[str, Any] | None:
    """Fetch public GitHub user profile via REST API."""
    try:
        return _http_json(f"https://api.github.com/users/{login}", token=token)
    except Exception as exc:
        print(f"[warn] No se pudo consultar perfil REST de {login}: {exc}")
        return None


def fetch_public_repos(
    login: str,
    *,
    exclude_names: set[str] | None = None,
    featured: list[str] | None = None,
    max_items: int = 6,
    token: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch real public repositories excluding profile repo and empty forks."""
    exclude = {n.lower() for n in (exclude_names or set())}
    exclude.add(login.lower())

    try:
        raw_repos = _http_json(
            f"https://api.github.com/users/{login}/repos?per_page=50&type=owner&sort=updated",
            token=token,
        )
    except Exception as exc:
        print(f"[warn] No se pudo consultar repositorios de {login}: {exc}")
        return []

    filtered: list[dict[str, Any]] = []
    for repo in raw_repos:
        if repo.get("private") or repo.get("archived"):
            continue
        name = str(repo.get("name", ""))
        if not name or name.lower() in exclude:
            continue
        # Exclude empty forks (fork with 0 stars and no description/size)
        if repo.get("fork") and int(repo.get("stargazers_count", 0)) == 0 and int(repo.get("size", 0)) == 0:
            continue
        filtered.append(
            {
                "name": name,
                "description": (repo.get("description") or "").strip(),
                "language": repo.get("language") or "Otro",
                "stars": int(repo.get("stargazers_count", 0)),
                "forks": int(repo.get("forks_count", 0)),
                "fork": bool(repo.get("fork")),
                "pushed_at": repo.get("pushed_at") or repo.get("updated_at") or "",
                "updated_at": repo.get("updated_at") or "",
                "url": repo.get("html_url") or f"https://github.com/{login}/{name}",
                "topics": list(repo.get("topics") or []),
            }
        )

    featured_order = [name.lower() for name in (featured or [])]
    if featured_order:
        rank = {name: idx for idx, name in enumerate(featured_order)}
        filtered.sort(
            key=lambda r: (
                0 if r["name"].lower() in rank else 1,
                rank.get(r["name"].lower(), 9999),
                -int(r["stars"]),
                r["pushed_at"],
            )
        )
        # Keep stable reverse chronological for non-featured
        featured_part = [r for r in filtered if r["name"].lower() in rank]
        rest_part = sorted(
            [r for r in filtered if r["name"].lower() not in rank],
            key=lambda r: r["pushed_at"],
            reverse=True,
        )
        filtered = featured_part + rest_part
    else:
        filtered.sort(key=lambda r: r["pushed_at"], reverse=True)

    return filtered[:max_items]


def _compute_streaks(
    all_days: list[tuple[dt.date, int]], local_today: dt.date
) -> tuple[int, int, int, dt.date | None]:
    active = [d for d, count in all_days if count > 0]
    active_set = set(active)
    longest = 0
    run = 0
    prev: dt.date | None = None
    for day in active:
        if prev is not None and (day - prev).days == 1:
            run += 1
        else:
            run = 1
        longest = max(longest, run)
        prev = day

    cursor = local_today
    if cursor not in active_set:
        cursor -= dt.timedelta(days=1)
    current = 0
    while cursor in active_set:
        current += 1
        cursor -= dt.timedelta(days=1)

    return len(active), current, longest, (active[0] if active else None)


def _blank_calendar_weeks(local_today: dt.date, active_days_map: dict[str, int] | None = None) -> list[list[dict[str, Any] | None]]:
    """Build a 53-week Sunday-Saturday calendar ending on local_today."""
    # GitHub weekday: Sunday=0 .. Saturday=6
    today_gh_wd = (local_today.weekday() + 1) % 7
    last_sunday = local_today - dt.timedelta(days=today_gh_wd)
    first_sunday = last_sunday - dt.timedelta(weeks=52)
    counts = active_days_map or {}

    weeks: list[list[dict[str, Any] | None]] = []
    for w in range(53):
        week_slots: list[dict[str, Any] | None] = []
        for wd in range(7):
            d = first_sunday + dt.timedelta(weeks=w, days=wd)
            if d > local_today:
                week_slots.append(None)
            else:
                iso = d.isoformat()
                week_slots.append({"date": iso, "count": int(counts.get(iso, 0))})
        weeks.append(week_slots)
    return weeks


def fetch_contributions(
    login: str,
    *,
    cache_path: pathlib.Path | None = None,
    token: str | None = None,
) -> dict[str, Any]:
    """Fetch GitHub GraphQL contribution stats with robust REST + local cache fallback."""
    tok = token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    now_utc = dt.datetime.now(dt.timezone.utc)
    local_now = now_utc - dt.timedelta(hours=5)
    local_today = local_now.date()

    if tok:
        try:
            payload = _http_json(
                "https://api.github.com/graphql",
                method="POST",
                data={"query": CONTRIB_QUERY, "variables": {"login": login}},
                token=tok,
            )
            if "errors" in payload:
                raise RuntimeError(json.dumps(payload["errors"], ensure_ascii=False))
            user = payload["data"]["user"]
            if not user:
                raise RuntimeError(f"Usuario {login!r} no encontrado en GraphQL")

            coll = user["contributionsCollection"]
            cal = coll["contributionCalendar"]
            weeks: list[list[dict[str, Any] | None]] = []
            all_days: list[tuple[dt.date, int]] = []
            day_map: dict[str, int] = {}

            for w in cal["weeks"]:
                slots: dict[int, dict[str, Any]] = {}
                for item in w["contributionDays"]:
                    d = dt.date.fromisoformat(item["date"])
                    c = int(item["contributionCount"])
                    slots[int(item["weekday"])] = {"date": item["date"], "count": c}
                    all_days.append((d, c))
                    if c > 0:
                        day_map[item["date"]] = c
                weeks.append([slots.get(i) for i in range(7)])

            all_days.sort()
            created_str = user["createdAt"][:10]
            created = dt.date.fromisoformat(created_str)
            active_days, cur_streak, best_streak, first_active = _compute_streaks(all_days, local_today)

            return {
                "source": "graphql",
                "login": user["login"],
                "account_created": created_str,
                "days_on_github": max(1, (local_today - created).days + 1),
                "total_contributions": int(cal["totalContributions"]),
                "active_days": active_days,
                "current_streak": cur_streak,
                "longest_streak": best_streak,
                "first_active": first_active.isoformat() if first_active else None,
                "commits": int(coll["totalCommitContributions"]),
                "issues": int(coll["totalIssueContributions"]),
                "pull_requests": int(coll["totalPullRequestContributions"]),
                "reviews": int(coll["totalPullRequestReviewContributions"]),
                "public_repos": int(user["repositories"]["totalCount"]),
                "followers": int(user["followers"]["totalCount"]),
                "weeks": weeks,
                "active_day_map": day_map,
                "updated_local": f"{local_now.strftime('%d %b %Y').upper()} · {local_now.strftime('%H:%M')} COT",
                "updated_utc": now_utc.strftime("%Y-%m-%d %H:%M UTC"),
                "updated_iso": now_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
        except Exception as exc:
            print(f"[warn] Fallo GraphQL para {login}; usando respaldo seguro: {exc}")
    else:
        print("[warn] GITHUB_TOKEN no definido localmente; usando caché + REST público.")

    # Safe fallback: cached JSON + public REST API
    cached: dict[str, Any] = {}
    if cache_path and cache_path.exists():
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"[warn] No se pudo leer caché {cache_path}: {exc}")

    rest_user = fetch_user_profile(login)
    created_str = (
        (rest_user or {}).get("created_at", "")[:10]
        or cached.get("account_created")
        or local_today.isoformat()
    )
    created = dt.date.fromisoformat(created_str)
    public_repos = int((rest_user or {}).get("public_repos", cached.get("public_repos", 0)))
    followers = int((rest_user or {}).get("followers", cached.get("followers", 0)))
    day_map = dict(cached.get("active_day_map") or {})
    weeks = cached.get("weeks") or _blank_calendar_weeks(local_today, day_map)

    return {
        "source": "cache+rest" if rest_user else "cache",
        "login": (rest_user or {}).get("login") or login,
        "account_created": created_str,
        "days_on_github": max(1, (local_today - created).days + 1),
        "total_contributions": int(cached.get("total_contributions", 0)),
        "active_days": int(cached.get("active_days", 0)),
        "current_streak": int(cached.get("current_streak", 0)),
        "longest_streak": int(cached.get("longest_streak", 0)),
        "first_active": cached.get("first_active"),
        "commits": int(cached.get("commits", 0)),
        "issues": int(cached.get("issues", 0)),
        "pull_requests": int(cached.get("pull_requests", 0)),
        "reviews": int(cached.get("reviews", 0)),
        "public_repos": public_repos,
        "followers": followers,
        "weeks": weeks,
        "active_day_map": day_map,
        "updated_local": cached.get("updated_local") or f"{local_now.strftime('%d %b %Y').upper()} · {local_now.strftime('%H:%M')} COT",
        "updated_utc": now_utc.strftime("%Y-%m-%d %H:%M UTC"),
        "updated_iso": now_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
