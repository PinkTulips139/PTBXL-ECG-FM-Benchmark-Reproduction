# Mentor Handoff Index V4

Status: `CURRENT_STAGING_AWARE_MENTOR_NAVIGATION`

This index uses repository-relative paths for the private mentor-review handoff. The earlier V3 index is preserved as historical pre-staging navigation and is not the current repository entry point.

## 1. Mentor-facing entry points

- [Final Report V2](Final_Report_V2.docx)
- [Static Sample Reviewer](../review_html/index.html)
- [Reviewer instructions](../review_html/README.md)
- [Known limitations](KNOWN_LIMITATIONS.md)
- [Sample-data dictionary](SAMPLE_DATA_DICTIONARY.md)

## 2. Final scientific result tables

- [Final Table 3 — Finetuning](../results/tables/FINAL_TABLE3_FINETUNING.csv) — 30 formal experiments
- [Final Table 4 — Frozen](../results/tables/FINAL_TABLE4_FROZEN.csv) — 24 formal experiments
- [Final Table 5 — Linear](../results/tables/FINAL_TABLE5_LINEAR.csv) — 24 formal experiments

Canonical finalized state: 78/78 formal experiments and 78 unique model × granularity × mode keys.

## 3. Canonical experiment state

- [78-run Completion Matrix V2](../results/execution_control/PTBXL_FINAL_CLOSURE/PTBXL_GLOBAL_FORMAL_RUN_COMPLETION_MATRIX_V2.csv)
- [Completion Matrix V2 JSON](../results/execution_control/PTBXL_FINAL_CLOSURE/PTBXL_GLOBAL_FORMAL_RUN_COMPLETION_MATRIX_V2.json)
- [Canonical Run ID Map V2](../results/execution_control/PTBXL_FINAL_CLOSURE/FINAL_CANONICAL_RUN_ID_MAP_V2.csv)
- [Canonical Run ID Map V2 JSON](../results/execution_control/PTBXL_FINAL_CLOSURE/FINAL_CANONICAL_RUN_ID_MAP_V2.json)

The canonical map resolves 9/9 historical placeholder identities without changing scientific results or historical evidence.

## 4. Mapping, aggregation, and Bootstrap provenance

- [Strict Mapping Closure](../results/tables/PTBXL_GLOBAL_MAPPING_CLOSURE_STATUS.csv)
- [Residual Strict Mapping](../results/execution_control/PTBXL_FINAL_CLOSURE/PARALLEL_451_RESIDUAL_STRICT_MAPPING.csv)
- [Worker Strict Mapping](../results/execution_control/PTBXL_FINAL_CLOSURE/PARALLEL_WORKER_STRICT_MAPPING_FINAL.csv)
- [Final Bootstrap Summary](../results/execution_control/PTBXL_FINAL_CLOSURE/FINAL_BOOTSTRAP_SUMMARY.csv)
- [Final Bootstrap Summary JSON](../results/execution_control/PTBXL_FINAL_CLOSURE/FINAL_BOOTSTRAP_SUMMARY.json)
- [Bootstrap Blocker Provenance](../results/execution_control/PTBXL_FINAL_CLOSURE/BOOTSTRAP_BLOCKER_PROVENANCE_LIST.csv)

Final mapping status is 77 PASS, 1 historical blocker, and 0 missing. Final Bootstrap status is 72 complete, 5 provenance-blocked, 0 failed, and 1 mapping-not-eligible.

## 5. Emergency-worker evidence and hashes

- [Worker Evidence Recovery](../results/execution_control/PTBXL_FINAL_CLOSURE/PARALLEL_WORKER_EVIDENCE_RECOVERY.csv)
- [Worker SHA256 Closure](../results/execution_control/PTBXL_FINAL_CLOSURE/PARALLEL_WORKER_HASH_CLOSURE.csv)
- [Worker Strict Mapping](../results/execution_control/PTBXL_FINAL_CLOSURE/PARALLEL_WORKER_STRICT_MAPPING_FINAL.csv)

Final worker state: 22/22 scientific bundles recovered and 88/88 recorded remote/local SHA256 comparisons passed.

## 6. Training metadata

- [Training Metadata Recovery](../results/execution_control/PTBXL_FINAL_CLOSURE/FINAL_TRAINING_METADATA_RECOVERY.csv)
- [Training Metadata Recovery JSON](../results/execution_control/PTBXL_FINAL_CLOSURE/FINAL_TRAINING_METADATA_RECOVERY.json)

Best-checkpoint references are recovered for 78/78 runs; best epoch is recovered for 50 and not recovered for 28; runtime is recovered for 15 and not recovered for 63; checkpoint binaries were locally retained for 10 and unavailable for 68. Checkpoint binaries are not packaged in this repository.

## 7. Source authority and accepted remediation

- [Clean exact-commit source snapshot](../code/locked_upstream/)
- [Accepted execution overlays](../code/execution_overlays/)
- [Locked-Upstream Qualification](source_qualification/LOCKED_UPSTREAM_EXECUTION_QUALIFICATION_V1.md)
- [Accepted Remediation Summary](ACCEPTED_REMEDIATIONS.md)
- [Third-Party Notices](../THIRD_PARTY_NOTICES.md)
- [Citation Instructions](CITATION.md)

The executable authority is commit `238409835ef55358a10bbc3459dfa9aaa91ad5e5`. The handoff uses its clean export and keeps accepted compatibility remediation separate. No scientific-result recomputation was required for packaging.

## 8. Sample coverage

- [Record-level sample bundles](../sample_predictions/record_level/)
- [Window-level supplementary provenance](../sample_predictions/window_level/)
- [Sample availability metadata](../sample_predictions/metadata/sample_availability.json)

Formal experiment coverage is 78/78. Physical record-level bundles are packaged for 76/78 experiments. `ECGFounder|all|Frozen` and `ECGFounder|all|Linear` are represented as provenance-only entries; no inference, aggregation, mapping, or Bootstrap was rerun solely for packaging.

## 9. Manifests and integrity

- [Curated Final Delivery Manifest V3 CSV](../manifests/FINAL_DELIVERY_MANIFEST_V3.csv)
- [Curated Final Delivery Manifest V3 JSON](../manifests/FINAL_DELIVERY_MANIFEST_V3.json)
- [Current Staging Manifest V3 CSV](../manifests/STAGED_ASSET_MANIFEST_V3.csv)
- [Current Staging Manifest V3 JSON](../manifests/STAGED_ASSET_MANIFEST_V3.json)

The staging manifest is a hash inventory of the content intended for the initial private Git commit and excludes its own CSV/JSON files to avoid self-reference.

## 10. Historical navigation boundary

`MENTOR_HANDOFF_INDEX_V3.md` is retained unchanged as historical source-tree navigation. It contains original workstation paths and is superseded by this V4 index for mentor-facing repository review. Historical evidence remains preserved; V4 changes navigation, not scientific state.
