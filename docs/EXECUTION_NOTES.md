# Execution Notes

## Executable authority

The official executable authority is pinned to commit `238409835ef55358a10bbc3459dfa9aaa91ad5e5` from `AI4HealthUOL/ecg-fm-benchmarking`. The repository directory `code/locked_upstream/` is a clean export of that exact commit and does not include the historical working tree or its `.git` metadata.

Accepted compatibility changes are kept separately under `code/execution_overlays/`, with supporting scripts, configs, logs, and provenance in their corresponding repository layers. This separation preserves the distinction between the locked upstream snapshot and local execution support.

## Accepted execution compatibility

- **ST-MEM:** runtime dependency closure required for the formal environment.
- **ECG-CPC:** documented compatibility route used for formal execution.
- **ECG-FM:** Python 3.9 compatibility overlay retained separately from locked source.
- **MERL and ECGFM-KED:** execution-only batch-normalization guard used by the accepted run path.
- **ECG-JEPA:** identity-based aggregation adjudication retained with mapping provenance.
- **Emergency-worker evidence:** 22 of 22 scientific bundles were recovered, with 88 of 88 remote-to-local SHA256 checks passing.

These measures are execution and provenance controls. They are not presented as proven causes of paper-versus-reproduction differences.

## Packaging boundary

No training, inference, mapping, aggregation, Bootstrap, prediction generation, or target generation was rerun solely for GitHub packaging. The repository contains 78 formal experiment entries, 76 physical record-level sample bundles, 76 supplementary window-level bundles, and two explicitly represented provenance-only sample states.
