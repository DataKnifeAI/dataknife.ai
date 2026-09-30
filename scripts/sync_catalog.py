#!/usr/bin/env python3
"""Refresh projects.json from public GitHub and GitLab repositories.

Canonical code lives on GitHub. GitLab links are attached only when the
mirror under dk-raas/dkai is public. Forks and private repositories are
left off the index.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "projects.json"

GITHUB_ORG = "DataKnifeAI"
GITLAB_GROUP = "dk-raas/dkai"
SKIP_NAMES = {".github", "gitlab-profile"}

CATEGORIES = {
    "nauarchos": "Agents",
    "slashbay": "Agents",
    "enodios": "Agents",
    "dioptra": "Agents",
    "agent-skills": "Agents",
    "agent-workspace": "Agents",
    "high-command-api": "High Command",
    "high-command-ui": "High Command",
    "high-command-mcp": "High Command",
    "unifi-network-mcp": "MCP",
    "unifi-protect-mcp": "MCP",
    "unifi-manager-mcp": "MCP",
    "proxmox-ve-mcp": "MCP",
    "rancher-manager-mcp": "MCP",
    "gitops-mcp": "MCP",
    "rancher-deploy": "Platform",
    "gitops-tools": "Platform",
    "gitops-core": "Platform",
    "gitops-dev": "Platform",
    "coder-templates": "Platform",
    "github-workflows": "Platform",
    "freya": "Platform",
    "ck-scenarios": "Platform",
    "windrose-operator": "Games",
    "palworld-operator": "Games",
    "timesplice": "Games",
}

CATEGORY_ORDER = ["Agents", "High Command", "MCP", "Platform", "Games"]

PRIORITY = {
    "Agents": [
        "nauarchos",
        "slashbay",
        "enodios",
        "dioptra",
        "agent-skills",
        "agent-workspace",
    ],
    "High Command": [
        "high-command-api",
        "high-command-ui",
        "high-command-mcp",
    ],
    "MCP": [
        "proxmox-ve-mcp",
        "rancher-manager-mcp",
        "unifi-manager-mcp",
        "unifi-network-mcp",
        "unifi-protect-mcp",
        "gitops-mcp",
    ],
    "Platform": [
        "rancher-deploy",
        "gitops-core",
        "gitops-tools",
        "gitops-dev",
        "coder-templates",
        "freya",
        "github-workflows",
        "ck-scenarios",
    ],
    "Games": [
        "palworld-operator",
        "windrose-operator",
        "timesplice",
    ],
}


def run_json(cmd: list[str]) -> object:
    raw = subprocess.check_output(cmd, text=True)
    return json.loads(raw)


def github_repos() -> list[dict]:
    data = run_json(
        [
            "gh",
            "api",
            f"orgs/{GITHUB_ORG}/repos?per_page=100&type=public",
            "--paginate",
        ]
    )
    if not isinstance(data, list):
        raise SystemExit("unexpected GitHub response")
    return data


def gitlab_projects() -> list[dict]:
    projects: list[dict] = []
    page = 1
    while True:
        batch = run_json(
            [
                "glab",
                "api",
                (
                    "groups/dk-raas%2Fdkai/projects"
                    f"?include_subgroups=true&per_page=100&page={page}"
                ),
                "--hostname",
                "gitlab.com",
            ]
        )
        if not isinstance(batch, list) or not batch:
            break
        projects.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return projects


def category_for(name: str) -> str:
    if name in CATEGORIES:
        return CATEGORIES[name]
    if name.endswith("-mcp"):
        return "MCP"
    if name.endswith("-operator"):
        return "Games"
    return "Platform"


def day(value: str | None) -> str | None:
    if not value:
        return None
    return value[:10]


def sort_key(project: dict) -> tuple:
    category = project["category"]
    order = CATEGORY_ORDER.index(category) if category in CATEGORY_ORDER else len(CATEGORY_ORDER)
    priority = PRIORITY.get(category, [])
    rank = priority.index(project["name"]) if project["name"] in priority else len(priority)
    return (order, rank, project["name"])


def main() -> None:
    gh_repos = github_repos()
    fork_names = {repo["name"] for repo in gh_repos if repo.get("fork")}
    originals = [
        repo
        for repo in gh_repos
        if not repo.get("fork")
        and not repo.get("private")
        and repo["name"] not in SKIP_NAMES
    ]

    gitlab_by_name: dict[str, dict] = {}
    for project in gitlab_projects():
        if project.get("visibility") != "public":
            continue
        name = project.get("path") or project.get("name")
        if not name or name in fork_names or name in SKIP_NAMES:
            continue
        gitlab_by_name[name] = project

    catalog: list[dict] = []
    seen: set[str] = set()

    for repo in originals:
        name = repo["name"]
        seen.add(name)
        mirror = gitlab_by_name.get(name)
        homepage = (repo.get("homepage") or "").strip() or None
        catalog.append(
            {
                "name": name,
                "description": (repo.get("description") or "").strip(),
                "language": repo.get("language") or "",
                "category": category_for(name),
                "github": repo["html_url"],
                "gitlab": mirror["web_url"] if mirror else None,
                "homepage": homepage,
                "updated": day(repo.get("pushed_at")),
            }
        )

    for name, project in gitlab_by_name.items():
        if name in seen:
            continue
        catalog.append(
            {
                "name": name,
                "description": (project.get("description") or "").strip(),
                "language": "",
                "category": category_for(name),
                "github": None,
                "gitlab": project["web_url"],
                "homepage": None,
                "updated": day(project.get("last_activity_at")),
            }
        )

    catalog.sort(key=sort_key)
    payload = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "org": {
            "name": "DataKnifeAI",
            "description": (
                "Learn and solve problems with AI tools—built to stay "
                "maintainable through automation, and aligned with software freedom."
            ),
            "github": f"https://github.com/{GITHUB_ORG}",
            "gitlab": f"https://gitlab.com/{GITLAB_GROUP}",
        },
        "categories": CATEGORY_ORDER,
        "projects": catalog,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(catalog)} projects to {OUT}")


if __name__ == "__main__":
    main()
