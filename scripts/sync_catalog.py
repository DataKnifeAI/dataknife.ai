#!/usr/bin/env python3
"""Refresh projects.json from public GitHub and GitLab repositories.

Canonical code lives on GitHub. GitLab links are attached only when the
mirror under dk-raas/dkai is public. Forks and private repositories are
left off the index.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "projects.json"

GITHUB_ORG = "DataKnifeAI"
GITLAB_GROUP = "dk-raas/dkai"
SKIP_NAMES = {".github", "gitlab-profile", "dataknife.ai"}

CATEGORIES = {
    "nauarchos": "Agents",
    "slashbay": "Agents",
    "enodios": "Agents",
    "dioptra": "Agents",
    "agent-skills": "Agents",
    "agent-workspace": "Agents",
    "high-command-api": "Apps",
    "high-command-ui": "Apps",
    "high-command-mcp": "MCP",
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
    "ck-scenarios": "Platform",
    "freya": "Apps",
    "windrose-operator": "Apps",
    "palworld-operator": "Apps",
    "timesplice": "Apps",
}

CATEGORY_ORDER = ["Agents", "MCP", "Platform", "Apps"]

STATUS = {
    "nauarchos": "Design",
    "slashbay": "Active",
    "palworld-operator": "Beta",
    "high-command-ui": "Live",
}

LIVE = {
    "high-command-ui": "https://hc.dataknife.ai/",
}


def github_token() -> str | None:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        return token
    if shutil.which("gh"):
        try:
            return subprocess.check_output(["gh", "auth", "token"], text=True).strip() or None
        except subprocess.CalledProcessError:
            return None
    return None


def get_json(url: str, headers: dict[str, str] | None = None) -> object:
    request = urllib.request.Request(url, headers={"User-Agent": "dataknife.ai-catalog", **(headers or {})})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def github_repos() -> list[dict]:
    headers = {"Accept": "application/vnd.github+json"}
    token = github_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    repos: list[dict] = []
    page = 1
    while True:
        batch = get_json(
            f"https://api.github.com/orgs/{GITHUB_ORG}/repos?type=public&per_page=100&page={page}",
            headers,
        )
        if not isinstance(batch, list) or not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return repos


def gitlab_projects() -> list[dict]:
    group = urllib.parse.quote(GITLAB_GROUP, safe="")
    projects: list[dict] = []
    page = 1
    while True:
        batch = get_json(
            f"https://gitlab.com/api/v4/groups/{group}/projects"
            f"?include_subgroups=true&visibility=public&per_page=100&page={page}"
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
        return "Apps"
    return "Platform"


def day(value: str | None) -> str | None:
    return value[:10] if value else None


def main() -> None:
    gh_repos = github_repos()
    fork_names = {repo["name"] for repo in gh_repos if repo.get("fork")}
    originals = [
        repo
        for repo in gh_repos
        if not repo.get("fork")
        and not repo.get("private")
        and not repo.get("archived")
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
        catalog.append(
            {
                "name": name,
                "description": (repo.get("description") or "").strip(),
                "language": repo.get("language") or "",
                "topics": repo.get("topics") or [],
                "category": category_for(name),
                "status": STATUS.get(name),
                "stars": repo.get("stargazers_count") or 0,
                "github": repo["html_url"],
                "gitlab": mirror["web_url"] if mirror else None,
                "homepage": LIVE.get(name) or (repo.get("homepage") or "").strip() or None,
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
                "topics": project.get("topics") or [],
                "category": category_for(name),
                "status": STATUS.get(name),
                "stars": project.get("star_count") or 0,
                "github": None,
                "gitlab": project["web_url"],
                "homepage": None,
                "updated": day(project.get("last_activity_at")),
            }
        )

    catalog.sort(key=lambda project: project["updated"] or "", reverse=True)
    payload = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "categories": CATEGORY_ORDER,
        "projects": catalog,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(catalog)} projects to {OUT}")


if __name__ == "__main__":
    main()
