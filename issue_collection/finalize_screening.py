#!/usr/bin/env python3
"""Validate a completed screening CSV and emit included/excluded ledgers."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


TRUE_VALUES = {"yes", "y", "true", "1"}
FALSE_VALUES = {"no", "n", "false", "0"}


def parse_args() -> argparse.Namespace:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=here / "output" / "screening.csv")
    parser.add_argument("--output-dir", type=Path, default=here / "output" / "screened")
    return parser.parse_args()


def parse_bool(value: str, field: str, row_number: int) -> bool:
    normalized = value.strip().casefold()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    raise ValueError(f"row {row_number}: {field} must be yes/no")


def main() -> int:
    args = parse_args()
    with args.input.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))

    included, excluded, errors = [], [], []
    for row_number, row in enumerate(rows, start=2):
        try:
            criteria = [
                parse_bool(row["criterion_defect"], "criterion_defect", row_number),
                parse_bool(row["criterion_configuration_related"], "criterion_configuration_related", row_number),
                parse_bool(row["criterion_traceable"], "criterion_traceable", row_number),
            ]
            stated = row["decision"].strip().casefold()
            expected = "include" if all(criteria) and row["state"].strip().casefold() == "closed" else "exclude"
            if stated != expected:
                raise ValueError(f"row {row_number}: decision must be {expected}")
            if expected == "exclude" and not row["exclusion_reason"].strip():
                raise ValueError(f"row {row_number}: excluded rows require exclusion_reason")
            (included if expected == "include" else excluded).append(row)
        except (KeyError, ValueError) as exc:
            errors.append(str(exc))

    if errors:
        preview = "\n".join(errors[:20])
        raise SystemExit(f"Screening validation failed ({len(errors)} errors):\n{preview}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    for name, selected in (("included.csv", included), ("excluded.csv", excluded)):
        with (args.output_dir / name).open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(selected)

    summary = {
        "candidate_count": len(rows),
        "included_count": len(included),
        "excluded_count": len(excluded),
        "included_by_repository": dict(Counter(row["repository"] for row in included)),
    }
    with (args.output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
