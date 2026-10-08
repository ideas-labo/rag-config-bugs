#!/usr/bin/env python3
"""Convert collected per-repository JSON files into a manual-screening CSV."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


FIELDS = [
    "repository",
    "issue_number",
    "issue_url",
    "state",
    "title",
    "labels",
    "criterion_defect",
    "criterion_configuration_related",
    "criterion_traceable",
    "decision",
    "exclusion_reason",
    "reviewer_notes",
]


def parse_args() -> argparse.Namespace:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-dir", type=Path, default=here / "output" / "candidates")
    parser.add_argument("--output", type=Path, default=here / "output" / "screening.csv")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = []
    for path in sorted(args.candidate_dir.glob("*.json")):
        with path.open(encoding="utf-8-sig") as handle:
            issues = json.load(handle)
        for issue in issues:
            rows.append(
                {
                    "repository": issue["repository"],
                    "issue_number": issue["issue_number"],
                    "issue_url": issue["issue_url"],
                    "state": issue.get("state", ""),
                    "title": issue.get("title", ""),
                    "labels": "; ".join(issue.get("labels", [])),
                    "criterion_defect": "",
                    "criterion_configuration_related": "",
                    "criterion_traceable": "",
                    "decision": "",
                    "exclusion_reason": "",
                    "reviewer_notes": "",
                }
            )
    rows.sort(key=lambda row: (row["repository"].casefold(), int(row["issue_number"])))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
