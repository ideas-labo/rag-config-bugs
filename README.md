# Configuring RAG Systems: What Breaks, Where Originates, and How to Fix

This repository contains dataset for the empirical study on **Configuring RAG Systems: What Breaks, Where Originates, and How to Fix**.

The dataset includes **654 real-world configuration issues** collected from 10 representative open-source RAG systems. It provides a comprehensive dataset of how configuration issues manifest (Symptoms), where they originate (Root Causes), how they propagate (Diagnosis Gap), and how they are resolved (Fix Patterns).

In addition, this repository includes an **inter-rater agreement sample set** for Cohen's Kappa calculation on these annotation dimensions: Symptom, Root Cause (and stages) and Fix Pattern labels

And the insights supplement provides detailed guidance for the nine actionable insights reported in the paper. For each insight, it explains the empirical basis, gives concrete engineering guidance, and includes an example of how the insight can be applied in practice.

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
