# Third-Party Notices

## Purpose and scope

This repository is prepared for private project review of an ECG foundation-model benchmark reproduction. This packaging step does not authorize public release or redistribution.

## Original work

- Paper: *Benchmarking ECG FMs: A Reality Check Across Clinical Tasks*
- Official upstream repository: `AI4HealthUOL/ecg-fm-benchmarking`
- Pinned executable-authority commit: `238409835ef55358a10bbc3459dfa9aaa91ad5e5`

The directory [`code/locked_upstream/`](code/locked_upstream/) is a clean source snapshot exported from that exact commit. Accepted compatibility overlays and local reproduction scripts are retained separately under [`code/execution_overlays/`](code/execution_overlays/) and summarized in [`docs/EXECUTION_NOTES.md`](docs/EXECUTION_NOTES.md).

## Licensing and ownership boundary

No `LICENSE`, `COPYING`, or `NOTICE` file was present in the pinned upstream commit snapshot. This repository therefore does not assert a license for that upstream source, claim ownership of it, or relicense it. The absence of a license file is recorded as a packaging fact, not as a legal conclusion.

Any future public distribution must independently verify third-party licensing and redistribution permissions. The present repository visibility intent is private, and its authorized scope is project review only.

## Reproduction materials

Execution overlays, validation scripts, logs, results, and provenance materials document the reproduction workflow and its accepted compatibility routes. Their separation from `code/locked_upstream/` preserves the distinction between the pinned upstream snapshot and local execution materials.
