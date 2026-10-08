#!/usr/bin/env python3
"""Collect and deduplicate candidate GitHub issues for the selected systems."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

import requests


API_ROOT = "https://api.github.com"
SEARCH_ENDPOINT = f"{API_ROOT}/search/issues"


def parse_args() -> argparse.Namespace:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=here / "config.json")
    parser.add_argument("--output-dir", type=Path, default=here / "output" / "candidates")
    parser.add_argument("--repos", nargs="*", help="Optional owner/repo allowlist")
    parser.add_argument("--dry-run", action="store_true", help="Print queries without calling GitHub")
    parser.add_argument("--request-delay", type=float, default=0.25)
    return parser.parse_args()


def load_config(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        config = json.load(handle)
    if not config.get("query_groups") or not config.get("repositories"):
        raise ValueError("config must define query_groups and repositories")
    return config


def quote_label(label: str) -> str:
    escaped = label.replace('"', '\\"')
    return f'label:"{escaped}"'


def resolved_queries(repo_config: dict[str, Any], query_groups: Iterable[str]) -> list[str]:
    if repo_config["search_mode"] == "keyword_only":
        return list(query_groups)
    if repo_config["search_mode"] == "label":
        label = repo_config.get("bug_label")
        if not label:
            raise ValueError(f"missing bug_label for {repo_config['repo']}")
        return [f"{query} {quote_label(label)}" for query in query_groups]
    raise ValueError(f"unknown search_mode for {repo_config['repo']}")


class GitHubClient:
    def __init__(self, token: str, delay: float) -> None:
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "rag-configuration-study-replication",
            }
        )

    def get_json(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        while True:
            response = self.session.get(url, params=params, timeout=60)
            if response.status_code in {403, 429} and response.headers.get("X-RateLimit-Remaining") == "0":
                reset = int(response.headers.get("X-RateLimit-Reset", int(time.time()) + 60))
                wait = max(reset - int(time.time()) + 1, 1)
                print(f"GitHub rate limit reached; waiting {wait}s", file=sys.stderr)
                time.sleep(wait)
                continue
            response.raise_for_status()
            time.sleep(self.delay)
            return response.json()

    def repository_created_date(self, repository: str) -> date:
        payload = self.get_json(f"{API_ROOT}/repos/{repository}")
        return datetime.fromisoformat(payload["created_at"].replace("Z", "+00:00")).date()

    def search_page(self, query: str, page: int = 1) -> dict[str, Any]:
        return self.get_json(
            SEARCH_ENDPOINT,
            {"q": query, "per_page": 100, "page": page, "sort": "created", "order": "asc"},
        )


def split_date_range(start: date, end: date) -> tuple[tuple[date, date], tuple[date, date]]:
    midpoint = start + timedelta(days=(end - start).days // 2)
    return (start, midpoint), (midpoint + timedelta(days=1), end)


def collect_window(client: GitHubClient, base_query: str, start: date, end: date) -> list[dict[str, Any]]:
    dated_query = f"{base_query} created:{start.isoformat()}..{end.isoformat()}"
    first = client.search_page(dated_query)
    total = int(first.get("total_count", 0))
    if total > 1000:
        if start >= end:
            raise RuntimeError(f"GitHub's 1,000-result cap is exceeded for one day: {dated_query}")
        left, right = split_date_range(start, end)
        return collect_window(client, base_query, *left) + collect_window(client, base_query, *right)

    items = list(first.get("items", []))
    page = 2
    while len(items) < total:
        payload = client.search_page(dated_query, page)
        page_items = payload.get("items", [])
        if not page_items:
            break
        items.extend(page_items)
        page += 1
    return items


def normalize_issue(repository: str, item: dict[str, Any], matched_query: str) -> dict[str, Any]:
    return {
        "repository": repository,
        "issue_number": item["number"],
        "issue_url": item["html_url"],
        "state": item.get("state"),
        "title": item.get("title"),
        "body": item.get("body"),
        "labels": [label["name"] for label in item.get("labels", [])],
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at"),
        "closed_at": item.get("closed_at"),
        "comments": item.get("comments"),
        "matched_queries": [matched_query],
    }


def merge_issue(existing: dict[str, Any], matched_query: str) -> None:
    if matched_query not in existing["matched_queries"]:
        existing["matched_queries"].append(matched_query)


def safe_name(repository: str) -> str:
    return repository.replace("/", "__")


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    selected = set(args.repos or [])
    repositories = [r for r in config["repositories"] if not selected or r["repo"] in selected]
    snapshot_end = date.fromisoformat(config["snapshot_end"])

    manifest: dict[str, Any] = {
        "snapshot_end": config["snapshot_end"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repositories": [],
    }

    if args.dry_run:
        for repo_config in repositories:
            queries = resolved_queries(repo_config, config["query_groups"])
            manifest["repositories"].append(
                {"repository": repo_config["repo"], "search_mode": repo_config["search_mode"], "queries": queries}
            )
        # ASCII escaping keeps dry-run output portable on Windows consoles
        # whose active code page cannot encode RAGFlow's emoji bug label.
        print(json.dumps(manifest, indent=2, ensure_ascii=True))
        return 0

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise SystemExit("Set GITHUB_TOKEN in the environment; credentials are never stored in this repository.")
    client = GitHubClient(token, args.request_delay)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for repo_config in repositories:
        repository = repo_config["repo"]
        queries = resolved_queries(repo_config, config["query_groups"])
        start = client.repository_created_date(repository)
        deduplicated: dict[str, dict[str, Any]] = {}
        print(f"Collecting {repository} ({repo_config['search_mode']})")
        for query in queries:
            base_query = f"{query} is:issue repo:{repository}"
            for item in collect_window(client, base_query, start, snapshot_end):
                if "pull_request" in item:
                    continue
                url = item["html_url"].rstrip("/")
                if url in deduplicated:
                    merge_issue(deduplicated[url], query)
                else:
                    deduplicated[url] = normalize_issue(repository, item, query)

        issues = sorted(deduplicated.values(), key=lambda x: x["issue_number"])
        closed = sum(issue["state"] == "closed" for issue in issues)
        output_path = args.output_dir / f"{safe_name(repository)}.json"
        with output_path.open("w", encoding="utf-8") as handle:
            json.dump(issues, handle, indent=2, ensure_ascii=False)
        manifest["repositories"].append(
            {
                "repository": repository,
                "search_mode": repo_config["search_mode"],
                "queries": queries,
                "candidate_count": len(issues),
                "closed_count": closed,
                "historical_candidate_count": repo_config.get("expected_candidates"),
                "historical_closed_count": repo_config.get("expected_closed"),
                "output": output_path.name,
            }
        )
        print(f"  wrote {len(issues)} candidates ({closed} currently closed)")

    with (args.output_dir.parent / "collection_manifest.json").open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
