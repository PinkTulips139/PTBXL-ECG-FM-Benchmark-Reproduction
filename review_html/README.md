# Static Sample Reviewer

This directory contains the offline, read-only inspection interface for finalized PTB-XL record-level prediction bundles. It is designed for private project review and does not perform inference, aggregation, mapping, Bootstrap, threshold optimization, or formal metric recomputation.

## Open the reviewer

**Online:** [Open the Cloudflare Access-protected reviewer](https://ptbxl-ecg-fm-reviewer.lekang-sun.workers.dev).

**Offline:** double-click [`index.html`](index.html).

Core loading does not use `fetch`: `data/manifest.js` is loaded by a normal script tag, and each selected run shard registers through a dynamically inserted local script. This supports direct `file://` use in common browsers.

If a browser policy blocks local scripts, start an optional local server:

```powershell
cd review_html
python -m http.server 8000
```

Then open `http://127.0.0.1:8000`.

## Reviewer controls

- Filter by model, granularity, mode, and formal run ID.
- Search an exact ECG ID or use Previous, Next, and Random navigation.
- Inspect positive ground-truth labels and stored probabilities.
- View Top 5, Top 10, all labels, or ground-truth-positive labels.
- Sort by probability, label, or ground-truth-positive-first.
- Compare Finetuning, Frozen, and Linear for the same model, granularity, label, and ECG ID.
- Switch between light and dark themes; preference remains local to the browser.

Keyboard shortcuts work when focus is not inside a form control:

| Key | Action |
|---|---|
| `←` | Previous ECG |
| `→` | Next ECG |
| `/` | Focus ECG-ID search |

## Data structure

- `data/manifest.js`: 78 formal experiment entries and authoritative 71/23/5 label sets
- `data/runs/*.js`: 76 compact, lazily loaded run shards
- `data/REVIEW_DATA_MANIFEST.csv` and `.json`: source-to-derived fidelity evidence
- `assets/app.js`: local interaction logic
- `assets/styles.css`: local responsive light/dark presentation

Each available shard contains ECG IDs, record-level prediction probabilities, and aligned targets. It is serialized directly from the packaged canonical NPZ without normalization, thresholding, calibration, label reordering, remapping, aggregation, or probability rounding. Stored prediction values round-trip exactly to the source dtype.

## Coverage and missing runs

All 78 formal experiments appear in the selector. Physical sample data are packaged for 76. ECGFounder/all/Frozen and ECGFounder/all/Linear display explicit provenance-only status cards and have no fabricated, empty, or hidden data shards.

- ECGFounder/all/Frozen: mapping `HISTORICAL_BLOCKED`; review mode `PROVENANCE_ONLY_LIMITED`
- ECGFounder/all/Linear: mapping `PASS`; review mode `PROVENANCE_ONLY`

No scientific computation was rerun to reconstruct either missing physical bundle.

## Interpretation boundary

One ECG record is the formal test sample. Window-level data are supplementary provenance and are not loaded by this interface. The UI displays probabilities and ground truth without imposing a fixed decision threshold. Probability ranking, top-k display, sorting, and mode comparison are inspection features—not new evaluation metrics, an equivalence test, or a definition of prediction correctness.

The reviewer is fully static: no backend, database, CDN, external library, internet requirement, analytics, remote API, or data upload is used.
