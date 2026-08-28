# Mentor Review Guide

This handoff separates finalized scientific artifacts, execution provenance, and browser-derived inspection data.

## Recommended sequence

1. Read `Final_Report_V2.docx`.
2. Review `results/tables/FINAL_TABLE3_FINETUNING.csv`, `FINAL_TABLE4_FROZEN.csv`, and `FINAL_TABLE5_LINEAR.csv`.
3. Confirm run closure in `results/execution_control/PTBXL_FINAL_CLOSURE/PTBXL_GLOBAL_FORMAL_RUN_COMPLETION_MATRIX_V2.csv`.
4. Open `review_html/index.html` to inspect record-level probabilities and targets.
5. Use `MENTOR_HANDOFF_INDEX_V3.md` for detailed provenance and audit navigation.

## Interpretation boundary

The static reviewer serializes existing canonical record-level outputs. It performs no inference, aggregation, mapping, Bootstrap, threshold optimization, or metric recomputation. Probability rankings and optional filtering are inspection views only; the formal primary metric is record-level aggregated Macro AUROC.

Formal experiment coverage is 78/78. Physical canonical sample coverage is 76/78. ECGFounder/all/Frozen and ECGFounder/all/Linear are represented by provenance-only reviewer entries because their physical canonical sample bundles were not retained locally.

