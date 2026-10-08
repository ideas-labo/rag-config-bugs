# RQ3 Impact Dataset

This folder contains the dataset used for **RQ3: How do the deviated stages between symptom and root cause affect the resolution of configuration issues?**

## Files

- `rq3_data.csv`: Impact-related annotations for all 654 issues.
- `analyze_rq3_stats.py`: Statistical analysis script for RQ3 (gap summary, Spearman correlation, and Mann-Whitney U test).

## Record Scope

- Total records: 654
- Granularity: One row per issue
- Key columns for joining with other datasets: `System`, `Issue URL`

## Schema

| Column                  | Description                                                  |
| ----------------------- | ------------------------------------------------------------ |
| `System`              | Target RAG system identifier.                                |
| `Issue URL`           | Original GitHub issue URL.                                   |
| `Symptom Stage`       | Stage where the issue becomes observable.                    |
| `Root Cause Stage`    | Stage where the issue is introduced.                         |
| `Root Cause Category` | Root cause top-level category (`RC-A`, `RC-B`).          |
| `Stage Gap`           | Numeric distance between symptom stage and root-cause stage. |
| `Fix Cost`            | Time-to-fix value measured in hours.                         |

## Stage Gap Definition

- Stage index mapping: `S0=0`, `S1=1`, `S2=2`, `S3=3`, `S4=4`, `S5=5`
- Formula: `Stage Gap = | Symptom Stage Index - Root Cause Stage Index |`

## Notes

- This file combines key symptom and root-cause stage information to quantify diagnosis difficulty.

# Script for RQ3 Analysis

`analyze_rq3_stats.py` performs three analyses from `rq3_data.csv`:

1. Stage-gap distribution with median fix cost per gap.
2. Spearman correlation between `Stage Gap` and `Fix Cost` (overall and by root-cause group).
3. Mann-Whitney U test comparing low-gap vs high-gap fix-cost distributions.

## How to Run

From repository root:

```bash
python rq3_impact/analyze_rq3_stats.py
```

Optional custom run:

```bash
python rq3_impact/analyze_rq3_stats.py --input rq3_impact/rq3_data.csv --output-dir rq3_impact
```

## Main Arguments

- `--input`: Input CSV path. Default is `rq3_data.csv`.
- `--output-dir`: Output directory for generated CSV files. Default is current script directory (`.`).
- `--low-max-gap`: Upper bound of low-gap group (inclusive). Default: `1`.
- `--high-min-gap`: Lower bound of high-gap group (inclusive). Default: `2`.
- `--print-only`: Print results without writing output files.

## Output Files

- `rq3_gap_count_median.csv`: Count and median fix cost by stage gap.
- `rq3_spearman_results.csv`: Spearman rho and p-value for overall/RC-A/RC-B.
- `rq3_mwu_results.csv`: Mann-Whitney U statistics for low-gap vs high-gap comparison.

## Dependency Note

- `scipy` is optional.
- If `scipy` is not installed, the script still runs, but Spearman and Mann-Whitney inferential statistics are reported as `N/A`.
