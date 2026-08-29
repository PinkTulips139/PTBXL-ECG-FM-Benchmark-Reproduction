# Known Limitations

1. Physical canonical record-level and window-level sample bundles are available for 76 of 78 formal runs. ECGFounder/all/Frozen and ECGFounder/all/Linear were not reconstructed for packaging.
2. ECGFounder/all/Frozen has the sole historical strict-mapping blocker (`TARGET_GROUP_CONSISTENCY=False`). Its 2,198 IDs, aggregation reconstruction, and saved aggregate match are preserved, but highest-grade prediction-to-target group provenance is incomplete.
3. Bootstrap closure comprises 72 complete runs, five provenance-blocked runs, zero failed runs, and one mapping-not-eligible run. Provenance blocking is not a model or computation failure.
4. No checkpoint binaries are packaged. Best-checkpoint references remain traceable, but locally retained checkpoint binaries cover only 10 of 78 runs.
5. Several larger paper-versus-reproduction deviations remain without proven causal explanations. Compatibility remediation is not presented as their cause.
6. The HTML interface contains derived inspection data. It does not recompute formal metrics and does not define prediction correctness with a fixed threshold.
