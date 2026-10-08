# Issue collection and screening pipeline

This directory documents the workflow used **after the ten repositories had
been selected**. It covers candidate-issue discovery, deduplication, manual
screening, and reconstruction of the historical 3,258-to-654 selection ledger.

This is a cleaned reconstruction of the original working scripts. The original
scripts were used interactively and were not preserved as a single immutable
pipeline. Consequently, this package documents and automates the reported
procedure, but it cannot recreate missing project-selection records or every
historical manual judgment.

## Method

Five GitHub issue-query groups are defined verbatim in `config.json`. Two search
modes were used:

1. **Label-assisted/high precision.** For repositories with consistent labels,
   each keyword group is combined with the repository's bug label. RAGFlow uses
   `🐞 bug`; the other label-assisted repositories use `bug`.
2. **Keyword-only/high recall.** DocsGPT, HippoRAG, and Obsidian Copilot are
   searched without a bug label because label-assisted searches returned too
   few candidates.

Results from the five queries are merged and deduplicated by issue URL. Pull
requests returned by GitHub's issue-search endpoint are excluded. Collection
includes both open and closed issues created no later than 2025-08-01. Only
closed issues proceed to the final manual screen.

An issue is included only when all three criteria hold:

1. it reports a system defect or user misconfiguration rather than a feature
   request or question;
2. its trigger, manifestation, fix, or workaround is directly attributable to
   at least one user-adjustable RAG configuration option (excluding operating-
   system-level settings); and
3. it is closed and contains enough issue discussion, reproduction evidence,
   or linked-PR evidence to infer the root cause.

The historical counts are 4,652 query candidates, 3,258 closed candidates, and
654 included issues. Expected per-repository counts are recorded in
`config.json` and checked by `build_historical_ledger.py`.

## 1. Install

```bash
python -m pip install -r requirements.txt
```

Set a GitHub token in the environment. Never place a token in a script or commit
it to the repository.

PowerShell:

```powershell
$env:GITHUB_TOKEN = "YOUR_TOKEN"
```

## 2. Inspect or run the searches

Inspect all resolved queries without network access:

```bash
python collect_issues.py --dry-run
```

Run the collection:

```bash
python collect_issues.py
```

The collector uses date-range splitting when a GitHub query exceeds the API's
1,000-result cap. Outputs are written under `output/candidates/`, with a query
and count manifest at `output/collection_manifest.json`.

GitHub content and issue state can change. A rerun therefore validates the
documented procedure, not a byte-identical reconstruction of the 2025 snapshot.

## 3. Create and validate a screening ledger

Create a CSV for independent manual screening:

```bash
python prepare_screening.py
```

For every row, reviewers fill the three `criterion_*` columns with `yes` or
`no`, set `decision` to `Include` or `Exclude`, and provide an exclusion reason
when applicable. Validate and split the completed ledger with:

```bash
python finalize_screening.py
```

This produces included/excluded CSV files and a per-repository summary.

## 4. Reconstruct the historical selection ledger

If the legacy per-repository candidate JSON files are available locally, the
following command maps the 3,258 closed candidates to the released 654 issues:

```powershell
$legacyRoot = "path\to\the\legacy\rag_empirical_study"
python build_historical_ledger.py `
  --candidate-source "$legacyRoot\rag_issues_json_close" `
  --candidate-source "$legacyRoot\rag_issues_json\QuivrHQ_quivr_all_states_desc.json" `
  --final-dataset "..\rag_configuration_issues.csv" `
  --strict
```

The resulting ledger records inclusion/exclusion for every closed candidate.
Criterion-level exclusion reasons were not consistently retained, so the
ledger explicitly marks that limitation instead of reconstructing reasons that
cannot be verified.

## Scope and limitations

- Project discovery (`RAG OR Retrieval-Augmented Generation`), the initial
  candidate-project list, and project-level exclusion decisions are outside
  this directory. The latter two records were not retained.
- Manual screening is inherently interpretive. These scripts expose the
  decision boundary and preserve decisions; they do not automate judgment.
- The historical working directory contains additional experimental scripts
  and projects that were not part of the final ten-system sample. `config.json`
  is the authoritative allowlist.
- PR linkage, annotation, and statistical analysis occur after the 654-issue
  sample is established and are documented elsewhere in the artifact.
