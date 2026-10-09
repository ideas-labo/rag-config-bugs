# Configuring RAG Systems: What Breaks, Where Originates, and How to Fix

This repository provides the dataset and supporting artifacts for the empirical study **Configuring RAG Systems: What Breaks, Where Originates, and How to Fix**. The study investigates configuration-related issues in open-source Retrieval-Augmented Generation (RAG) systems, including both system-side configuration bugs and user misconfigurations.

The dataset contains **654 real-world configuration issues** collected from **10 representative open-source RAG systems**. It records how issues manifest (**Symptoms**), where they originate (**Root Causes**), how far their symptoms and root causes are separated across pipeline stages (**Stage Gap**, also referred to as diagnosis gap), and how they are resolved (**Fix Patterns**). The released artifacts cover issue collection and screening, annotation reliability, the four research questions, and practical guidance derived from the findings.

The repository includes the following components:

- **Master dataset — [rag_configuration_issues.csv](rag_configuration_issues.csv).** The complete annotated sample contains one row per issue, combining system identifiers, issue URLs, symptom and root-cause labels, their pipeline stages, stage gaps, resolving costs, and available PR and repair annotations. It serves as the shared basis for the RQ-specific datasets.

- **Issue collection and screening — [issue_collection/](issue_collection/README.md).** This folder documents the collection workflow after the ten repositories were selected. It contains the repository and query configuration, scripts for candidate discovery, deduplication, and preparation and validation of manual screening records, together with a reconstructed historical selection ledger. The historical workflow reduced 4,652 query candidates to 3,258 closed candidates and then to the 654 included issues. 

- **Inter-rater agreement — [inter-rater_agreement/](inter-rater_agreement/README.md).** This folder provides paired annotation samples from two raters for Cohen's Kappa assessment. The SP&RC files cover symptom and root-cause categories, subcategories, and stages; the FP files cover fix-pattern labels. These samples support assessment of annotation consistency and are subsets of the study data.

- **RQ1: Symptoms — [rq1_symptoms/](rq1_symptoms/README.md).** This folder contains symptom annotations for all 654 issues, including their main categories, subcategories, and observable pipeline stages. It supports investigating what failures configuration issues produce and where those failures become visible.

- **RQ2: Root causes — [rq2_root_causes/](rq2_root_causes/README.md).** This folder contains root-cause annotations for all 654 issues. It distinguishes configuration bugs from user misconfigurations and records finer-grained causes and their origin stages, supporting analysis of why configuration issues occur and where they begin.

- **RQ3: Impact — [rq3_impact/](rq3_impact/README.md).** This folder combines symptom stages, root-cause stages, stage gaps, and resolving costs for all 654 issues. It also includes a statistical analysis script and result CSV files for gap distributions, Spearman correlations, and Mann–Whitney U comparisons. These artifacts support investigating how stage separation relates to the elapsed time required to resolve an issue.

- **RQ4: Solutions — [rq4_solutions/](rq4_solutions/README.md).** This folder contains repair annotations for the 345 issues with linked pull requests usable for fix-pattern analysis. It records fix patterns, resolving costs, and PR URLs, supporting investigation of how configuration issues are repaired in practice. This dataset is a PR-backed subset of the master sample.

- **Actionable insights — [insights_supplement.pdf](insights_supplement.pdf).** The supplement expands the nine insights derived from the empirical findings for RAG system developers, users, and researchers. Each insight presents its empirical basis, concrete engineering guidance, and an example of its application.

The folder READMEs provide the corresponding file descriptions, data schemas, and usage instructions.

## 📂 Repository Structure

To align directly with the Research Questions in our paper, the dataset is organized as follows:

```text
.
├── rag_configuration_issues.csv   # The master dataset containing all 654 issues and full annotations.
│
├── inter-rater_agreement/         # Sample datasets for inter-rater agreement (Cohen's Kappa) in annotation.
├── issue_collection/              # Reconstructed issue-query and manual-screening pipeline, with the 3,258-to-654 ledger.
├── rq1_symptoms/                  # [N=654] Data for RQ1 (Symptom manifestation and stages).
├── rq2_root_causes/               # [N=654] Data for RQ2 (Root cause and stages).
├── rq3_impact/                    # [N=654] Data for RQ3 (Stage Gap and Resolving Costs).
└── rq4_solutions/                 # [N=345] Data for RQ4 (Fix Patterns). Filtered to only include issues with Pull Requests.
```
