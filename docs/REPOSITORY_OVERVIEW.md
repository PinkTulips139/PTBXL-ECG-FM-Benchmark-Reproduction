# Repository Overview

## Purpose and audience

This repository is a private, evidence-oriented package of the PTB-XL ECG foundation-model benchmark reproduction. It is structured for project review: the landing README provides the shortest review path, the final report and tables provide the scientific summary, and the provenance layer preserves the evidence needed to audit execution and sample-level outputs.

## Repository layers

| Layer | Main paths | Role |
|---|---|---|
| Review synthesis | `README.md`, `docs/`, `results/` | Scientific scope, final report, finalized tables, review guidance |
| Executable authority | `code/locked_upstream/` | Clean export of pinned commit `238409835ef55358a10bbc3459dfa9aaa91ad5e5` |
| Compatibility and execution | `code/execution_overlays/`, `code/scripts/`, `logs/` | Accepted compatibility routes, formal commands, execution evidence |
| Canonical sample artifacts | `sample_predictions/record_level/`, `sample_predictions/window_level/` | Packaged record-level outputs and supplementary window-level provenance |
| Derived inspection layer | `review_html/` | Offline browser representation of existing canonical record-level bundles |
| Scientific provenance | `provenance/`, `results/execution_control/` | Mapping, Bootstrap, worker, hash, canonical-identity, remediation, and audit evidence |
| Integrity metadata | `manifests/` | Curated delivery and staged-content inventories with sizes and SHA256 |

## Canonical versus derived data

The canonical scientific sample artifacts are the packaged record-level NPZ files. Each physical file contains prediction probabilities and aligned targets. The static reviewer’s JavaScript shards are byte-verified serialized inspection representations; they do not normalize, threshold, calibrate, remap, reorder, aggregate, or recompute formal metrics.

Window-level/no-aggregation files are supplementary provenance. The formal evaluation and Bootstrap sampling unit is one ECG record (`N = 2,198` per normally available run), not one window row.

## Sample availability

- Formal experiments: 78/78 complete
- Physical record-level bundles: 76/78 packaged
- Physical window-level bundles: 76/78 packaged
- Metadata/provenance-only entries: 2/78

The two unavailable physical bundles are ECGFounder / all / Frozen and ECGFounder / all / Linear. Frozen is the sole historical mapping blocker and is shown as `PROVENANCE_ONLY_LIMITED`; Linear has mapping PASS and is shown as `PROVENANCE_ONLY`. No scientific computation was rerun to reconstruct either file for packaging.

## Evidence hierarchy

1. Final Tables 3/4/5 and Final Report V2 summarize the finalized scientific results.
2. Completion Matrix V2 and Canonical Run ID Map V2 define the 78-run canonical state.
3. Mapping, aggregation, Bootstrap, and worker-hash evidence establish sample/provenance closure.
4. Accepted-remediation and locked-source qualification documents define the executable governance boundary.
5. Staged manifests record packaged file identity, size, and SHA256.

The static reviewer is a navigation and inspection aid over this hierarchy; it is not an evaluation pipeline.

## Recommended review path

1. Open [`Final_Report_V2.docx`](Final_Report_V2.docx).
2. Review the three finalized CSV tables under `results/tables/` from the repository root.
3. Open [`../review_html/index.html`](../review_html/index.html) to inspect available record-level predictions and targets.
4. Use the [Final Review Index](MENTOR_HANDOFF_INDEX_V4.md) for detailed evidence navigation.
5. Verify staged identity using [`../manifests/STAGED_ASSET_MANIFEST_V4.csv`](../manifests/STAGED_ASSET_MANIFEST_V4.csv).

## Intentionally excluded

- Raw PTB-XL waveform data
- Checkpoint binaries
- Conda/virtual-environment binaries and package/model caches
- Temporary, duplicate, and editor-generated files
- Any reconstructed sample bundle for the two unavailable historical artifacts

These exclusions define storage and redistribution scope; they do not reduce the formal experiment count from 78/78.
