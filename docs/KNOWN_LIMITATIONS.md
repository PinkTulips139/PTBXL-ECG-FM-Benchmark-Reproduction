# Known Limitations

1. Physical canonical record-level and window-level bundles are available for 76 of 78 formal runs. ECGFounder/all/Frozen and ECGFounder/all/Linear are not reconstructed for packaging.
2. ECGFounder/all/Frozen has a historical strict-mapping blocker (`TARGET_GROUP_CONSISTENCY=False`). Its 2,198 IDs, aggregation reconstruction, and saved aggregate match are preserved, but highest-grade prediction-to-target group provenance is incomplete.
3. Bootstrap closure comprises 72 complete runs, five provenance-blocked runs, zero failures, and one mapping-not-eligible run. Provenance blocking is not a model or computation failure.
4. Best epoch is recovered for 50/78 runs and unavailable for 28/78. Runtime is recovered for 15/78 and unavailable for 63/78.
5. Checkpoint binaries are locally retained for 10/78 runs and unavailable for 68/78. No checkpoint binaries are packaged in this handoff.
6. The executable authority is pinned to commit `238409835ef55358a10bbc3459dfa9aaa91ad5e5`; the later historical local Windows working tree was not clean. This handoff uses a clean exact-commit export, while accepted compatibility changes remain separate overlays.
7. Several larger paper-versus-ours deviations remain without proven causal explanations. Execution compatibility remediation is not presented as their cause.
8. The HTML interface is derived inspection data. It does not recompute formal metrics and does not define prediction correctness with a fixed threshold.
