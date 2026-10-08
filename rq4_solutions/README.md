# RQ4 Solutions Dataset

This folder contains the dataset used for **RQ4: How are the actual configuration bugs often fixed?**

## Files

- `rq4_data.csv`: Fix-pattern annotations for 345 issues with linked pull requests.

## Record Scope

- Total records: 345
- Granularity: One row per issue with an available PR
- Key columns for joining with other datasets: `System`, `Issue URL`

## Schema

| Column          | Description                                                            |
| --------------- | ---------------------------------------------------------------------- |
| `System`      | Target RAG system identifier.                                          |
| `Issue URL`   | Original GitHub issue URL.                                             |
| `Fix Pattern` | Taxonomy label describing how the issue is fixed (`FP1` to `FP6`). |
| `Fix Cost`    | Time-to-fix value measured in hours.                                   |
| `PR URL`      | Pull request linked to the issue resolution.                           |

## Notes

- This subset only includes issues that have pull requests usable for fix-pattern extraction.
