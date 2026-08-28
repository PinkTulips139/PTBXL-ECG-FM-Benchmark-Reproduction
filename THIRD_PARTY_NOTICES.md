# Third-Party Notices

## Purpose and scope

This repository is prepared for private mentor review of an ECG foundation-model benchmark reproduction. This packaging step does not authorize a public release or public redistribution.

## Original work

- Paper: *Benchmarking ECG FMs: A Reality Check Across Clinical Tasks*
- Official upstream repository: `AI4HealthUOL/ecg-fm-benchmarking`
- Pinned executable-authority commit: `238409835ef55358a10bbc3459dfa9aaa91ad5e5`

The directory [`code/locked_upstream/`](code/locked_upstream/) is a clean source snapshot exported from that exact commit. Accepted execution-compatibility overlays and local reproduction scripts are retained separately under [`code/execution_overlays/`](code/execution_overlays/) and the associated remediation provenance.

## Licensing and ownership boundary

No `LICENSE`, `COPYING`, or `NOTICE` file was present in the pinned upstream commit snapshot. This handoff therefore does not assert a license for that upstream source, claim ownership of it, or relicense it. The absence of a license file is recorded as a packaging fact, not as a legal conclusion.

Any future public distribution must independently verify third-party licensing and redistribution permissions. The present repository visibility intent is private, and its authorized scope is mentor review and reproduction handoff only.

## Reproduction materials

Execution overlays, validation scripts, logs, reports, and provenance materials are packaged to document the reproduction workflow and its accepted compatibility remediations. Their separation from `code/locked_upstream/` preserves the distinction between the pinned upstream snapshot and local execution/provenance materials.
