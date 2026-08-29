<p align="center">
  <img src="docs/assets/repository-banner.svg" alt="PTB-XL ECG Foundation Model Benchmark Reproduction — private project review" width="100%">
</p>

<p align="center">
  <img src="docs/assets/status/formal-runs.svg" alt="Formal runs: 78 of 78">
  <img src="docs/assets/status/record-samples.svg" alt="Record samples: 76 of 78 packaged">
  <img src="docs/assets/status/mapping.svg" alt="Mapping: 77 pass and 1 historical blocker">
  <img src="docs/assets/status/bootstrap.svg" alt="Bootstrap: 72 complete and 5 provenance-blocked">
  <img src="docs/assets/status/repository-scope.svg" alt="Private review">
  <img src="docs/assets/status/locked-commit.svg" alt="Pinned commit 2384098">
</p>

# PTB-XL ECG Foundation Model Benchmark Reproduction

This private project-review repository contains the executable source authority, compatibility overlays, formal results, essential provenance, and sample-level inspection assets for the PTB-XL experiments from *Benchmarking ECG FMs: A Reality Check Across Clinical Tasks*. All **78 formal experiments** are complete; **76 canonical record-level bundles** are physically packaged and two historical runs remain visible as provenance-only entries.

No training, inference, aggregation, mapping, Bootstrap, or scientific-result recomputation was performed solely for repository packaging.

## Quick Start

| Review item | Open |
|---|---|
| Final report | [Final Report](Final_Report.pdf) |
| Static sample reviewer | [Open the offline reviewer](review_html/index.html) |
| Finetuning results | [Table 3](results/tables/FINAL_TABLE3_FINETUNING.csv) |
| Frozen results | [Table 4](results/tables/FINAL_TABLE4_FROZEN.csv) |
| Linear results | [Table 5](results/tables/FINAL_TABLE5_LINEAR.csv) |
| Formal experiment state | [Formal Run Completion Matrix](results/FORMAL_RUN_COMPLETION_MATRIX.csv) |
| Bootstrap status | [Bootstrap Summary](results/BOOTSTRAP_SUMMARY.csv) |
| Limitations | [Known Limitations](docs/KNOWN_LIMITATIONS.md) |

## At a Glance

| Scope | Final state |
|---|---:|
| Formal experiments | **78/78 complete** |
| Foundation models | **8** |
| Supervised baselines | **2** |
| Test ECG records per run | **2,198** |
| Record-level bundles packaged | **76/78** |
| Window-level bundles packaged | **76/78** |
| Strict ECG-ID mapping | **77 PASS + 1 historical blocker** |
| Bootstrap closure | **72 complete / 5 provenance-blocked / 0 failed / 1 mapping-not-eligible** |
| Emergency-worker evidence | **22/22 bundles recovered; 88/88 SHA256 PASS** |
| Checkpoint binaries packaged | **0** |

## Project Scope

- **Executable authority:** clean export of official commit `238409835ef55358a10bbc3459dfa9aaa91ad5e5` under [`code/locked_upstream/`](code/locked_upstream/).
- **Compatibility layer:** accepted overlays and execution scripts remain separate under [`code/execution_overlays/`](code/execution_overlays/) and [`code/scripts/`](code/scripts/).
- **Results:** final comparison tables, formal completion state, canonical run identities, Bootstrap status, and training metadata.
- **Inspection:** canonical record-level bundles, supplementary window-level data, and an offline static reviewer.
- **Distribution boundary:** private project review; this repository is not a public dataset mirror or a public upstream release.

See [Execution Notes](docs/EXECUTION_NOTES.md) for the concise source and compatibility record, [Citation Instructions](docs/CITATION.md), and [Third-Party Notices](THIRD_PARTY_NOTICES.md).

## Benchmark Contract

PTB-XL v1.0.3 contains 21,799 twelve-lead ECG records from 18,869 patients, originally sampled at 500 Hz. Folds 1–8 are training (17,418 records), fold 9 is validation (2,183), and fold 10 is test (2,198), with no patient overlap.

| Label space | Outputs | Records and split |
|---|---:|---|
| PTB-XL(all) | 71 | Same ECG records and folds |
| PTB-XL(sub) | 23 | Same ECG records and folds |
| PTB-XL(super) | 5 | Same ECG records and folds |

Only the label space changes across all/sub/super; the test population is not resampled.

<details>
<summary><strong>Training and evaluation protocol</strong></summary>

- Optimizer: AdamW; learning rate `1e-3`; weight decay `1e-3`; constant schedule
- Batch size: 64; epochs: 100; loss: BCEWithLogits
- Best checkpoint: highest validation aggregated Macro AUROC
- Formal test: best validation checkpoint
- Primary metric: record-level aggregated Macro AUROC
- Aggregation: mean probability over windows belonging to the same ECG
- Bootstrap: 1,000 iterations; 95% CI; sampling unit = ECG record; `N = 2,198`

</details>

## Models and Experiment Matrix

The eight foundation models are **ECGFounder, ECG-JEPA, ST-MEM, MERL, ECGFM-KED, HuBERT-ECG, ECG-CPC, and ECG-FM**. **S4** and **Net1D** are supervised baselines and participate only in Finetuning.

<p align="center">
  <img src="docs/assets/diagrams/experiment-matrix.svg" alt="Finetuning, Frozen, and Linear independently branch from the original pretrained checkpoint; 30 plus 24 plus 24 equals 78 formal experiments" width="100%">
</p>

| Mode | Models × label spaces | Formal runs |
|---|---:|---:|
| Finetuning | 10 × 3 | 30 |
| Frozen | 8 × 3 | 24 |
| Linear | 8 × 3 | 24 |
| **Total** |  | **78** |

The three modes branch independently from the original pretrained checkpoint. Frozen and Linear do not originate from a finetuned checkpoint.

## Reproduction Results

The final tables contain 78 unique model × mode × label-space entries. These are descriptive reproduction comparisons, not a statistical-equivalence claim.

| Scope | Entries | Mean \|Δ\| | Median \|Δ\| | Max \|Δ\| |
|---|---:|---:|---:|---:|
| Overall | 78 | 0.008425 | 0.001943 | 0.133420 |
| Finetuning | 30 | 0.005263 | 0.002307 | 0.026627 |
| Frozen | 24 | 0.008234 | 0.002000 | 0.097321 |
| Linear | 24 | 0.012568 | 0.001336 | 0.133420 |

**66/78** entries have `|Δ| < 0.010`, and **8/9** dataset × mode panels retain the same top model. Larger deviations are concentrated in specific settings; the available evidence does not establish causal root explanations. Open [Table 3](results/tables/FINAL_TABLE3_FINETUNING.csv), [Table 4](results/tables/FINAL_TABLE4_FROZEN.csv), and [Table 5](results/tables/FINAL_TABLE5_LINEAR.csv) for all entries.

## Static Sample Reviewer

Open [`review_html/index.html`](review_html/index.html) directly in a browser. The reviewer is fully local: no backend, database, CDN, analytics, remote API, network requirement, or data upload. It lazily loads one JavaScript shard per selected run and supports direct `file://` use.

It provides run filtering, ECG-ID search, previous/next/random navigation, target-positive labels, probability ranking, same-model mode comparison, provenance status, light/dark themes, and keyboard shortcuts. Probability display and top-k ranking are inspection views—not new metrics. No fixed classification threshold is part of the formal Macro AUROC protocol.

See the [reviewer documentation](review_html/README.md) for controls and an optional local HTTP-server fallback.

## Sample-Level Data Availability

The formal sample unit is **one ECG record**, not one signal window. A canonical record-level NPZ contains prediction probabilities and ground-truth targets in the same physical file; ECG IDs enter the derived reviewer only through existing validated mapping evidence.

| Representation | Coverage | Role |
|---|---:|---|
| Formal experiment entries | 78/78 | Complete benchmark state |
| Physical record-level bundles | 76/78 | Canonical sample-inspection source |
| Metadata-only entries | 2/78 | Provenance-only representation |
| Window-level bundles | 76/78 | Supplementary provenance |

> [!NOTE]
> **Packaging limitation, not experiment failure.** Physical canonical sample bundles are unavailable for **ECGFounder / all / Frozen** and **ECGFounder / all / Linear**. No inference, aggregation, mapping, or Bootstrap was rerun to reconstruct them. The reviewer shows `PROVENANCE_ONLY_LIMITED` for Frozen and `PROVENANCE_ONLY` for Linear.

ECGFounder / all / Frozen is the sole historical mapping blocker (`TARGET_GROUP_CONSISTENCY=False`). Its evidence preserves 2,198 unique ECG IDs, passes aggregation reconstruction, and matches the saved aggregate; highest-grade prediction-to-target group provenance remains incomplete.

Window-level files under [`sample_predictions/window_level/`](sample_predictions/window_level/) are supplementary provenance and are not the formal evaluation unit or the reviewer’s primary data source.

## Repository Structure

```text
Final_Report.pdf       user-selected final report
code/                  locked source, overlays, scripts, configs, and environment specs
docs/                  citation, execution notes, limitations, and local visual assets
logs/                  formal execution and final validation logs
results/               final tables and canonical result summaries
sample_predictions/    record-level bundles, window-level provenance, and availability metadata
review_html/           offline reviewer and verified derived inspection shards
provenance/            mapping, Bootstrap, worker, and hash evidence
manifests/             current repository file manifest
```

## Evidence and Provenance

<p align="center">
  <img src="docs/assets/diagrams/evidence-chain.svg" alt="Evidence chain from window-level prediction through ECG identity, target alignment, record aggregation, saved aggregate verification, Macro AUROC, and record-level Bootstrap CI" width="100%">
</p>

| Evidence area | Entry point |
|---|---|
| Formal completion | [Formal Run Completion Matrix](results/FORMAL_RUN_COMPLETION_MATRIX.csv) |
| Canonical run identity | [Canonical Run ID Map](results/CANONICAL_RUN_ID_MAP.csv) |
| Strict mapping | [Mapping Closure](provenance/mapping/MAPPING_CLOSURE_STATUS.csv) |
| Bootstrap | [Bootstrap Summary](results/BOOTSTRAP_SUMMARY.csv) |
| Training metadata | [Training Metadata](results/TRAINING_METADATA.csv) |
| Emergency-worker recovery | [22/22 Bundle Recovery](provenance/workers/WORKER_EVIDENCE_RECOVERY.csv) · [88/88 Hash Closure](provenance/workers/WORKER_HASH_CLOSURE.csv) |
| Repository integrity | [File Manifest](manifests/FILE_MANIFEST.csv) |

## Execution Notes and Limitations

Compatibility work includes the ST-MEM dependency closure, ECG-CPC compatibility route, ECG-FM Python 3.9 overlay, ECG-JEPA identity-aggregation adjudication, the MERL/ECGFM-KED execution-only BN guard, and emergency-worker recovery. These measures are execution and provenance controls; they are not asserted as causes of paper-versus-reproduction differences. Read [Execution Notes](docs/EXECUTION_NOTES.md) for the concise record.

Bootstrap closure is 72 complete, five provenance-blocked, zero failed, and one mapping-not-eligible. Best-epoch, runtime, and checkpoint-binary retention are incomplete. See [Known Limitations](docs/KNOWN_LIMITATIONS.md) for the final qualified list.

## Citation and Repository Status

For scientific use, cite the original paper and identify the official repository and pinned executable-authority commit. See [Citation Instructions](docs/CITATION.md) and [Third-Party Notices](THIRD_PARTY_NOTICES.md).

- **Visibility intent:** Private Project Review
- **Executable authority:** `238409835ef55358a10bbc3459dfa9aaa91ad5e5`
- **Scientific artifact recomputation required:** no
- **Raw PTB-XL dataset packaged:** no
- **Checkpoint binaries packaged:** no

This repository is not presented as a public upstream, public dataset mirror, or fully licensed open-source release.
