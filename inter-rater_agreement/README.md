# Inter-Rater Agreement Dataset

This folder contains paired annotation samples used to compute **Cohen's Kappa** for two coding dimensions:

- Symptom and Root Cause (and stages) labels (SP&RC)
- Fix Pattern labels (FP)

## Files

- `SP&RC_sampleKappa_1.csv`: Rater 1 annotations for symptom/root-cause categories and stages.
- `SP&RC_sampleKappa_2.csv`: Rater 2 annotations for the same issue sample as `SP&RC_sampleKappa_1.csv`.
- `FP_sampleKappa_1.csv`: Rater 1 annotations for fix-pattern labels.
- `FP_sampleKappa_2.csv`: Rater 2 annotations for the same issue sample as `FP_sampleKappa_1.csv`.

## Record Scope

- Granularity: One row per sampled issue
- Alignment key: `Issue_ID`
- Task scope:
  - SP&RC Kappa on symptom/root-cause (stages) fields
  - FP Kappa on fix-pattern field

## Schema

| Group | Columns Used for Kappa                                                                                           |
| ----- | ---------------------------------------------------------------------------------------------------------------- |
| SP&RC | `Symptom_Main`, `Symptom_Sub`, `Symptom_Stage`, `RootCause_Main`, `RootCause_Sub`, `RootCause_Stage` |
| FP    | `Fix_Pattern`                                                                                                  |

Common identifier and metadata columns include `Issue_ID`, `System`, `Issue_URL`, and `PR_URL`.

## Notes

- For each pair of files, align records by `Issue_ID` before computing Kappa.
