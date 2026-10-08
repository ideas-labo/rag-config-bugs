#!/usr/bin/env python3
"""Reconstruct the historical 3,258-to-654 issue selection ledger."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


URL_RE = re.compile(r"https://github\.com/([^/]+/[^/]+)/issues/(\d+)", re.IGNORECASE)
FIELDS = ["repository", "issue_number", "issue_url", "state", "decision", "decision_provenance"]


def parse_args() -> argparse.Namespace:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=here / "config.json")
    parser.add_argument("--candidate-source", type=Path, action="append", required=True)
    parser.add_argument("--final-dataset", type=Path, default=here.parent / "rag_configuration_issues.csv")
    parser.add_argument("--output", type=Path, default=here / "data" / "issue_selection_ledger.csv")
    parser.add_argument("--summary", type=Path, default=here / "data" / "issue_selection_summary.json")
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def json_files(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        if path.is_dir():
            yield from sorted(path.glob("*.json"))
        elif path.suffix.casefold() == ".json":
            yield path


def canonicalize_url(value: str) -> str:
    # One legacy FastGPT row contains a duplicated GitHub URL prefix. Preserve
    # the candidate while recording a canonical, resolvable issue URL.
    value = value.replace("https://github.com://github.com/", "https://github.com/")
    return value.rstrip("/")


def get_url(record: dict[str, Any]) -> str | None:
    value = record.get("issue_url") or record.get("url") or record.get("html_url")
    return canonicalize_url(value) if isinstance(value, str) else None


def read_final_urls(path: Path) -> set[str]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if "Issue URL" not in (reader.fieldnames or []):
            raise ValueError("final dataset must contain an 'Issue URL' column")
        return {canonicalize_url(row["Issue URL"]) for row in reader if row.get("Issue URL")}


def main() -> int:
    args = parse_args()
    with args.config.open(encoding="utf-8") as handle:
        config = json.load(handle)
    repo_configs = {item["repo"].casefold(): item for item in config["repositories"]}
    repo_order = {item["repo"].casefold(): index for index, item in enumerate(config["repositories"])}
    candidates: dict[str, dict[str, Any]] = {}

    for path in json_files(args.candidate_source):
        with path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, list):
            continue
        for record in payload:
            url = get_url(record)
            match = URL_RE.fullmatch(url or "")
            if not match:
                continue
            repository, issue_number = match.groups()
            if repository.casefold() not in repo_configs:
                continue
            state = str(record.get("state", "")).casefold()
            if state != "closed":
                continue
            candidates[url] = {
                "repository": repository,
                "issue_number": int(issue_number),
                "issue_url": url,
                "state": "closed",
            }

    final_urls = read_final_urls(args.final_dataset)
    missing = sorted(final_urls - set(candidates))
    rows = []
    for url, record in candidates.items():
        included = url in final_urls
        rows.append(
            {
                **record,
                "decision": "Include" if included else "Exclude",
                "decision_provenance": (
                    "Present in released 654-issue dataset"
                    if included
                    else "Absent from final dataset; criterion-level exclusion reason was not retained"
                ),
            }
        )
    rows.sort(key=lambda row: (repo_order[row["repository"].casefold()], row["issue_number"]))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    candidate_counts = Counter(row["repository"].casefold() for row in rows)
    included_counts = Counter(row["repository"].casefold() for row in rows if row["decision"] == "Include")
    repositories = []
    errors = []
    for repo in config["repositories"]:
        key = repo["repo"].casefold()
        actual_candidates = candidate_counts[key]
        actual_included = included_counts[key]
        repositories.append(
            {
                "repository": repo["repo"],
                "closed_candidates": actual_candidates,
                "included": actual_included,
                "excluded": actual_candidates - actual_included,
                "expected_closed": repo.get("expected_closed"),
                "expected_included": repo.get("expected_included"),
            }
        )
        if actual_candidates != repo.get("expected_closed"):
            errors.append(f"{repo['repo']}: closed candidates {actual_candidates} != {repo.get('expected_closed')}")
        if actual_included != repo.get("expected_included"):
            errors.append(f"{repo['repo']}: included {actual_included} != {repo.get('expected_included')}")
    if missing:
        errors.append(f"{len(missing)} final issue URLs were absent from candidate sources")

    summary = {
        "closed_candidate_count": len(rows),
        "included_count": sum(row["decision"] == "Include" for row in rows),
        "excluded_count": sum(row["decision"] == "Exclude" for row in rows),
        "repositories": repositories,
        "validation_errors": errors,
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    with args.summary.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if args.strict and errors:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
