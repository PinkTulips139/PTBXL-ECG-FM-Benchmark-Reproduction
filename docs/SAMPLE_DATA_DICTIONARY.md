# Sample Data Dictionary

## Canonical NPZ bundles

Each available record-level NPZ contains:

| Field | Meaning |
|---|---|
| `preds` | Record-level aggregated prediction probabilities; shape `2198 × C`; `float32` |
| `targs` | Ground-truth target matrix aligned to `preds`; shape `2198 × C`; `float32` |
| `lbl_itos` | Authoritative label names in stored column order; length `C` |
| `epoch` | Historical best-checkpoint epoch field retained in the source bundle where present |

Output dimension `C` is 71 for `all`, 23 for `sub`, and 5 for `super`.

## ECG IDs

The derived reviewer uses the approved 2,198-row prediction-index mapping under `sample_predictions/metadata/test_prediction_index_mapping.csv`. IDs are serialized without reordering, remapping, or inference. The mapping is shared because the three granularities use the same PTB-XL fold-10 ECG records and ordering.

## Reviewer shards

Each JavaScript shard registers one run-level columnar object containing metadata, ECG IDs, predictions, and targets. Label names are stored once in `review_html/data/manifest.js`. Numeric values are serialized at sufficient precision to round-trip exactly to the source dtype. Reviewer data are derived inspection representations, not independent scientific outputs.

## Coverage

- Formal runs: 78
- Physical record-level bundles: 76
- Provenance-only entries: 2
- Missing physical runs: ECGFounder/all/Frozen and ECGFounder/all/Linear

