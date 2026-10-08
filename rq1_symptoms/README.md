# RQ1 Symptoms Dataset

This folder contains the dataset used for **RQ1: What common symptoms do configuration issues exhibit in RAG systems?**

## Files

- `rq1_data.csv`: Symptom annotations for all 654 issues.

## Record Scope

- Total records: 654
- Granularity: One row per issue
- Key columns for joining with other datasets: `System`, `Issue URL`

## Schema

| Column                   | Description                                                      |
| ------------------------ | ---------------------------------------------------------------- |
| `System`               | Target RAG system identifier.                                    |
| `Issue URL`            | Original GitHub issue URL.                                       |
| `Symptom Category`     | Top-level symptom category (for example `SP-A`, `SP-B`).     |
| `Symptom Sub-Category` | Fine-grained symptom taxonomy label.                             |
| `Symptom Stage`        | Pipeline stage where the symptom is observed (`S0` to `S5`). |

## Notes

- This file is a focused slice of the master dataset at the symptom level.
