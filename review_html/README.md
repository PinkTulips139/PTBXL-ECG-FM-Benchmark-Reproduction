# Static Sample Reviewer

This directory contains an offline, read-only inspection interface for the finalized PTB-XL record-level prediction bundles.

## Open the reviewer

The simplest method is to double-click `index.html`. Core data loading does not use `fetch`; the manifest is loaded by a normal script tag and each run shard registers through a dynamically inserted local script. This design supports direct `file://` use in common browsers.

If a local browser policy blocks scripts, start an optional local server:

```powershell
cd review_html
python -m http.server 8000
```

Open `http://127.0.0.1:8000`.

## Data structure

- `data/manifest.js`: 78 formal experiment entries and the authoritative 71/23/5 label sets
- `data/runs/*.js`: 76 compact, lazily loaded run shards
- `data/REVIEW_DATA_DERIVATION_MANIFEST.csv` and `.json`: source-to-derived fidelity evidence
- `assets/app.js`: local interaction logic
- `assets/styles.css`: local presentation

Each available shard contains ECG IDs, record-level prediction probabilities, and aligned targets. It is serialized directly from the packaged canonical NPZ without normalization, thresholding, calibration, label reordering, remapping, aggregation, or probability rounding. Stored values round-trip exactly to the source dtype.

## Coverage and missing runs

All 78 formal experiments appear in the selector. Physical sample data are packaged for 76. ECGFounder/all/Frozen and ECGFounder/all/Linear display provenance-only status cards and have no fabricated or empty data shards.

The Frozen run is additionally marked `PROVENANCE_ONLY_LIMITED` because it is the sole historical strict-mapping blocker. The Linear run is marked `PROVENANCE_ONLY` with mapping PASS.

No inference, aggregation, mapping, Bootstrap, or formal metric was rerun for this reviewer.

## Interpretation

One ECG record is the formal test sample. Window-level data are supplementary provenance and are not loaded by this interface. The UI displays probabilities and ground truth without imposing a fixed decision threshold. Probability ranking, top-k display, and mode comparison are inspection features, not new evaluation metrics or an equivalence test.

The reviewer is fully static: no backend, database, CDN, external library, internet access, analytics, remote API, or data upload is used.
