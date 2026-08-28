# ECG Foundation Model Benchmark Reproduction — Final Closure Report

## 1. Scope

This closure covers PTB-XL(all), PTB-XL(sub), and PTB-XL(super): 26 formal entries per dataset and 78 entries globally. All 78 formal runs are complete.

## 2. Locked executable authority

The executable reproduction authority is the locked official commit `238409835ef55358a10bbc3459dfa9aaa91ad5e5` under the approved decision `APPROVE_R1_LOCKED_OFFICIAL_GITHUB_AS_EXECUTABLE_REPRODUCTION_AUTHORITY`. Locked upstream was not modified.

## 3. Dataset and analysis contract

The canonical test set contains 2,198 ECG records. Expected output dimensions are 71 for all, 23 for sub, and 5 for super. Each dataset contains 10 Finetuning, 8 Frozen, and 8 Linear entries. S4 and Net1D occur only under Finetuning. Bootstrap uses record-level aggregated Macro AUROC, 1,000 iterations, 95% confidence intervals, and `clinical_ts.utils.bootstrap_utils.empirical_bootstrap` with its accepted sampling, RNG, invalid-resample, and percentile-CI behavior.

## 4. Formal-run completion

Formal completion is 78/78. Historical execution attempts remain provenance, but superseded attempts are not counted as final scientific failures.

## 5. Strict ECG-ID mapping closure

Strict mapping is PASS for 77 entries. `PTBXL_ALL_ECGFOUNDER_FROZEN_FORMAL_RUN_001` remains the sole historical blocker because its preserved sidecar records `TARGET_GROUP_CONSISTENCY=False`. That sidecar and its source artifacts remain unchanged.

## 6. Bootstrap closure

Bootstrap is COMPLETE for 72 entries and `BLOCKED_EXISTING_PROVENANCE` for five; zero entries failed and zero remain pending. No CI was inferred for blocked entries.

## 7. Accepted remediation and provenance

- Emergency workers: 22/22 minimum scientific bundles recovered, 88/88 remote-local SHA256 comparisons PASS, and 22/22 strict mappings PASS.
- ECG-JEPA: the six agg/noagg-identical artifacts were adjudicated as valid whole-record, single-test-segment identity aggregation; this has no final metric or bootstrap impact.
- ECG-FM: accepted Python 3.9/fairseq-signals compatibility-route provenance is retained, including execution-only TensorBoard remediation and successful Retry01 evidence for Run015.
- ST-MEM: historical resampy, sklearn, and safetensors dependency failures are preserved; successful Retry03 supersedes those attempts scientifically without deleting provenance.
- Historical source 052: recovered through the complete data-disk clone carried by 451; historical execution authority remains 052 where applicable.

## 8. Power state and remote-only evidence

The user confirmed through the AutoDL UI that all project-related remote instances are stopped. This is recorded as `HUMAN_AUTODL_UI_CONFIRMATION`, not as an SSH process probe. Current running remote instances: 0. Critical remote-only scientific artifacts remaining: 0.

## 9. Final tables

Dataset-complete summaries are `PTBXL_ALL_FINAL_RESULTS.csv`, `PTBXL_SUB_FINAL_RESULTS.csv`, and `PTBXL_SUPER_FINAL_RESULTS.csv`. Paper-aligned mode tables are `FINAL_TABLE3_FINETUNING.csv`, `FINAL_TABLE4_FROZEN.csv`, and `FINAL_TABLE5_LINEAR.csv`. Missing verified paper comparison values are explicitly `NOT_REPORTED / NA`; no values were inferred.

## 10. Documented limitations

1. One historical ECG-ID mapping blocker remains.
2. Five mapping-PASS runs remain bootstrap-blocked because their canonical local aggregate/target provenance is not uniquely locatable; CI fields remain blank.

Neither limitation is classified as a final scientific execution failure.

## 11. Final reproducibility statement

The formal completion matrix, run-level provenance, prediction/target evidence, strict mapping records, bootstrap summaries, final tables, and delivery hashes form the local reproducibility chain. This project is closed with documented limitations. Human authors remain responsible for scientific interpretation and external release approval.
