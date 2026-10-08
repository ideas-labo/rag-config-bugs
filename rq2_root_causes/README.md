# RQ2 Root Causes Dataset

This folder contains the dataset used for **RQ2: What commonly causes the configuration issues?**

## Files

- `rq2_data.csv`: Root-cause annotations for all 654 issues.

## Record Scope

- Total records: 654
- Granularity: One row per issue
- Key columns for joining with other datasets: `System`, `Issue URL`

## Schema

| Column                      | Description                                                           |
| --------------------------- | --------------------------------------------------------------------- |
| `System`                  | Target RAG system identifier.                                         |
| `Issue URL`               | Original GitHub issue URL.                                            |
| `Root Cause Category`     | Top-level root cause category (for example `RC-A`, `RC-B`).       |
| `Root Cause Sub-Category` | Fine-grained root cause taxonomy label.                               |
| `Root Cause Stage`        | Pipeline stage where the root cause is introduced (`S0` to `S5`). |

## Notes

- This file is a focused slice of the master dataset at the root-cause level.
