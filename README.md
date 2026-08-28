# PTB-XL ECG Foundation Model Benchmark Reproduction

This private mentor-review repository packages the code, execution evidence, finalized results, and sample-level inspection assets for the PTB-XL experiments from *Benchmarking ECG FMs: A Reality Check Across Clinical Tasks*. The executable authority is pinned to the official repository commit `238409835ef55358a10bbc3459dfa9aaa91ad5e5`. All 78 formal experiments are complete; 76 canonical record-level sample bundles are physically packaged, while two historical bundles are represented by provenance-only entries.

## Mentor Review Quick Start

The following repository-relative links provide the shortest path through the final handoff:

1. [Final Report V2](docs/Final_Report_V2.docx)
2. [Final Table 3 — Finetuning](results/tables/FINAL_TABLE3_FINETUNING.csv)
3. [Final Table 4 — Frozen](results/tables/FINAL_TABLE4_FROZEN.csv)
4. [Final Table 5 — Linear](results/tables/FINAL_TABLE5_LINEAR.csv)
5. [Static Sample Reviewer](review_html/index.html)
6. [78-run Completion Matrix V2](results/execution_control/PTBXL_FINAL_CLOSURE/PTBXL_GLOBAL_FORMAL_RUN_COMPLETION_MATRIX_V2.csv)
7. [Canonical Run ID Map V2](results/execution_control/PTBXL_FINAL_CLOSURE/FINAL_CANONICAL_RUN_ID_MAP_V2.csv)
8. [Strict Mapping Closure](results/tables/PTBXL_GLOBAL_MAPPING_CLOSURE_STATUS.csv)
9. [Final Bootstrap Summary](results/execution_control/PTBXL_FINAL_CLOSURE/FINAL_BOOTSTRAP_SUMMARY.csv)
10. [Training Metadata Recovery](results/execution_control/PTBXL_FINAL_CLOSURE/FINAL_TRAINING_METADATA_RECOVERY.csv)
11. [Worker Evidence Recovery](results/execution_control/PTBXL_FINAL_CLOSURE/PARALLEL_WORKER_EVIDENCE_RECOVERY.csv) and [88/88 SHA256 Closure](results/execution_control/PTBXL_FINAL_CLOSURE/PARALLEL_WORKER_HASH_CLOSURE.csv)
12. [Accepted Remediation Summary](docs/ACCEPTED_REMEDIATIONS.md)
13. [Locked-Upstream Qualification](docs/source_qualification/LOCKED_UPSTREAM_EXECUTION_QUALIFICATION_V1.md)
14. [Current Staging Manifest V3](manifests/STAGED_ASSET_MANIFEST_V3.csv) and its [JSON companion](manifests/STAGED_ASSET_MANIFEST_V3.json)

The staging-aware canonical navigation is [Mentor Handoff Index V4](docs/MENTOR_HANDOFF_INDEX_V4.md). Attribution and citation boundaries are documented in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and [docs/CITATION.md](docs/CITATION.md).

## Paper and executable authority

- Paper: *Benchmarking ECG FMs: A Reality Check Across Clinical Tasks*
- Official repository: `AI4HealthUOL/ecg-fm-benchmarking`
- Executable authority: commit `238409835ef55358a10bbc3459dfa9aaa91ad5e5`
- Clean source export: [`code/locked_upstream/`](code/locked_upstream/)
- Accepted compatibility overlays: [`code/execution_overlays/`](code/execution_overlays/)
- Source qualification: [`docs/source_qualification/LOCKED_UPSTREAM_EXECUTION_QUALIFICATION_V1.md`](docs/source_qualification/LOCKED_UPSTREAM_EXECUTION_QUALIFICATION_V1.md)
- Third-party source and redistribution boundary: [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)

The commit identity was pinned and verified. A later forensic review found that the historical local Windows working tree was not clean; this handoff therefore uses a clean exact-commit export rather than that working tree. Formal-execution evidence supports documented, accepted compatibility remediation routes kept separate from the locked source. No retraining, reinference, remapping, reaggregation, or re-bootstrap was required for this handoff.

## Dataset and task

The benchmark uses PTB-XL v1.0.3: 21,799 twelve-lead ECG records from 18,869 patients, originally sampled at 500 Hz. Folds 1–8 form the training set (17,418 records), fold 9 the validation set (2,183), and fold 10 the test set (2,198), with no patient overlap.

Three label granularities use the same signals, split, and 2,198 test ECGs; only the label space changes:

| Granularity | Outputs |
|---|---:|
| PTB-XL(all) | 71 |
| PTB-XL(sub) | 23 |
| PTB-XL(super) | 5 |

## Models and experiment matrix

The eight foundation models are ECGFounder, ECG-JEPA, ST-MEM, MERL, ECGFM-KED, HuBERT-ECG, ECG-CPC, and ECG-FM. S4 and Net1D are supervised baselines and participate only in Finetuning.

| Mode | Models × granularities | Formal runs |
|---|---:|---:|
| Finetuning | 10 × 3 | 30 |
| Frozen | 8 × 3 | 24 |
| Linear | 8 × 3 | 24 |
| **Total** |  | **78** |

Finetuning, Frozen, and Linear branches originate independently from the original pretrained checkpoint; Frozen and Linear do not branch from a finetuned checkpoint.

## Training and evaluation protocol

- AdamW, learning rate `1e-3`, weight decay `1e-3`, constant schedule
- Batch size 64, 100 epochs, BCEWithLogits loss
- Best checkpoint selected by highest validation aggregated Macro AUROC
- Formal test performed with the best validation checkpoint
- Primary metric: record-level aggregated Macro AUROC
- Aggregation: mean prediction probability across windows belonging to the same ECG
- Bootstrap: 1,000 iterations, 95% CI, ECG-record sampling unit, `N = 2,198`

## Results

The finalized tables contain 78 unique experiment entries: 30 Finetuning, 24 Frozen, and 24 Linear. Across all entries, mean absolute paper-versus-ours difference is approximately 0.008425, median 0.001943, and maximum 0.133420.

- [Table 3 — Finetuning](results/tables/FINAL_TABLE3_FINETUNING.csv)
- [Table 4 — Frozen](results/tables/FINAL_TABLE4_FROZEN.csv)
- [Table 5 — Linear](results/tables/FINAL_TABLE5_LINEAR.csv)
- [Canonical completion matrix V2](results/execution_control/PTBXL_FINAL_CLOSURE/PTBXL_GLOBAL_FORMAL_RUN_COMPLETION_MATRIX_V2.csv)
- [Canonical run-ID map V2](results/execution_control/PTBXL_FINAL_CLOSURE/FINAL_CANONICAL_RUN_ID_MAP_V2.csv)
- [Bootstrap summary](results/execution_control/PTBXL_FINAL_CLOSURE/FINAL_BOOTSTRAP_SUMMARY.csv)
- [Training metadata recovery](results/execution_control/PTBXL_FINAL_CLOSURE/FINAL_TRAINING_METADATA_RECOVERY.csv)
- [Final mentor report](docs/Final_Report_V2.docx)

ECGFounder was the most numerically stable reproduced foundation model. Larger deviations are concentrated in specific settings, including ST-MEM Finetuning, several ECGFM-KED Frozen/Linear settings, and ECG-CPC Linear(all). Available evidence does not establish causal root explanations for these deviations.

## Scientific closure status

| Item | Final status |
|---|---|
| Formal experiments | 78/78 complete |
| Canonical identities | 9/9 resolved |
| Strict ECG-ID mapping | 77 PASS, 1 historical blocker, 0 missing |
| Bootstrap | 72 complete, 5 provenance-blocked, 0 failed, 1 mapping-not-eligible |
| Emergency-worker evidence | 22/22 bundles recovered; 88/88 remote↔local SHA256 matches |
| Best-checkpoint references | 78/78 recovered |
| Best epoch | 50 recovered; 28 not recovered |
| Runtime | 15 recovered; 63 not recovered |
| Checkpoint binaries locally retained | 10 available; 68 unavailable |

## Repository structure

```text
docs/                 mentor report, navigation, and review documentation
code/                 clean locked source, overlays, scripts, and environment specs
logs/                 formal, validation, remediation, and superseded evidence
results/              finalized tables and closure summaries
sample_predictions/   canonical record-level and supplementary window-level bundles
provenance/            mapping, worker, hash, remediation, and audit evidence
review_html/           offline static sample reviewer and derived inspection data
manifests/             curated and staged asset manifests
```

The canonical staging-aware mentor navigation is [`docs/MENTOR_HANDOFF_INDEX_V4.md`](docs/MENTOR_HANDOFF_INDEX_V4.md). The curated final handoff manifest is [`manifests/FINAL_DELIVERY_MANIFEST_V3.csv`](manifests/FINAL_DELIVERY_MANIFEST_V3.csv), and the current pre-Git staging snapshot is [`manifests/STAGED_ASSET_MANIFEST_V3.csv`](manifests/STAGED_ASSET_MANIFEST_V3.csv).

## Sample-level predictions

The formal sample unit is one ECG record (`N = 2,198` per normally available run), not one signal window. A canonical record-level NPZ contains prediction probabilities and ground-truth targets in the same physical file. ECG IDs are added only in the derived review layer using the existing validated index mapping.

- Formal experiments represented: 78/78
- Physical canonical record-level bundles packaged: 76/78
- Physical bundles unavailable: ECGFounder / all / Frozen and ECGFounder / all / Linear

No inference, aggregation, mapping, or bootstrap was rerun solely to reconstruct missing artifacts for repository packaging. The two missing runs remain visible in the static reviewer as provenance-only entries.

The ECGFounder / all / Frozen run is the sole historical mapping blocker (`TARGET_GROUP_CONSISTENCY=False`). Its evidence preserves 2,198 unique ECG IDs, passes aggregation reconstruction, and matches the saved aggregate. The record-level result is therefore not automatically invalid, but the highest-grade prediction-to-target group provenance is incomplete. Because its physical canonical bundle is also unavailable, the reviewer marks it `PROVENANCE_ONLY_LIMITED`.

Window-level files under [`sample_predictions/window_level/`](sample_predictions/window_level/) are supplementary provenance. They are not the formal evaluation unit and are not the default reviewer data source.

## Bootstrap provenance

Final status is 72 complete, five provenance-blocked, zero failed, and one mapping-not-eligible. “Provenance-blocked” does not mean that a model, mapping, prediction, or Bootstrap computation failed; it means the historical provenance could not uniquely designate the canonical aggregate/target pair for a new unified CI. See the [Bootstrap blocker list](results/execution_control/PTBXL_FINAL_CLOSURE/BOOTSTRAP_BLOCKER_PROVENANCE_LIST.csv) and [final summary](results/execution_control/PTBXL_FINAL_CLOSURE/FINAL_BOOTSTRAP_SUMMARY.csv).

## Accepted execution remediations

Documented compatibility work includes ST-MEM dependency closure, the ECG-CPC PyKeOps/NVRTC route, the ECG-FM Python 3.9 overlay, ECG-JEPA identity aggregation adjudication, the MERL/ECGFM-KED execution-only BN guard, infrastructure succession and clone evidence, emergency-worker recovery, and the minimal scientific-evidence retention strategy. These measures are execution/provenance controls; they are not asserted as proven causes of paper-versus-ours deviations. See [`docs/ACCEPTED_REMEDIATIONS.md`](docs/ACCEPTED_REMEDIATIONS.md).

## Static Sample Reviewer

Open [`review_html/index.html`](review_html/index.html) directly in a browser. The reviewer uses local JavaScript shards and does not require a server, network connection, backend, database, analytics, or upload.

If a browser policy interferes with local scripts, an optional local server can be used:

```powershell
cd review_html
python -m http.server 8000
```

Then open `http://127.0.0.1:8000`. The interface displays stored probabilities together with ground truth and does not impose a fixed classification threshold. It is an inspection interface, not a new evaluation pipeline. See the [reviewer guide](review_html/README.md) and [sample-data dictionary](docs/SAMPLE_DATA_DICTIONARY.md).

## Packaging and retention policy

- Checkpoint binaries: 10/78 were locally retained, but zero are packaged by default because coverage is incomplete, total size is large, and best-checkpoint references remain traceable.
- Raw PTB-XL: not packaged; this repository records the dataset version and acquisition authority rather than mirroring the dataset.
- Environments and caches: binary environments, package caches, model caches, dataset caches, and temporary files are excluded; lightweight version/configuration evidence is retained.

## Known limitations

The handoff explicitly retains the two unavailable physical sample bundles, one historical mapping blocker, five Bootstrap provenance blockers, incomplete best-epoch and runtime recovery, incomplete checkpoint-binary retention, the qualified locked-source history, and large model-setting deviations without proven root causes. See [`docs/KNOWN_LIMITATIONS.md`](docs/KNOWN_LIMITATIONS.md).

## How to review

1. Read the [final report](docs/Final_Report_V2.docx).
2. Inspect the three finalized result tables and the completion matrix.
3. Open the [static sample reviewer](review_html/index.html).
4. Use the [mentor handoff index](docs/MENTOR_HANDOFF_INDEX_V4.md) for detailed staging-relative provenance navigation.
5. Verify packaged file integrity using the staged manifests under [`manifests/`](manifests/).

## Citation

Please cite the original paper and identify the official repository and pinned executable-authority commit when referencing this reproduction. See [docs/CITATION.md](docs/CITATION.md) for the conservative citation instructions and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for the third-party source boundary. This repository is a private reproduction handoff prepared for mentor review and is not presented as a public upstream release.
