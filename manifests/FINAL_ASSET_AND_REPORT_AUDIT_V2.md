# FINAL ASSET AND REPORT AUDIT V2

## 1. Executive Summary

`AUDIT_STATUS=FAIL`. The scientific result tables themselves pass structural, paper-reference, and difference recomputation checks: 78/78 experiment combinations are present; all 78 paper values match `main.tex`; and all stored differences match `ours - paper` within tolerance `5e-12`. Mapping is 77 PASS plus one documented historical blocker; Bootstrap is 72 complete, five provenance-blocked, zero failed, and one mapping-blocker not eligible. Emergency-worker evidence is 22/22 bundles with 88/88 recorded-remote-to-current-local SHA256 matches. Training metadata counts also match the finalized recovery records.

Handoff nevertheless must stop. Three critical findings were independently established: the locked repository worktree has substantive tracked changes despite final claims of no modification; nine finalized entries retain placeholder run IDs that conflict with exact recovered identities; and the handoff-designated canonical completion matrix is materially stale. `NEW_SUBSTANTIVE_DISCREPANCY=YES`, `LOCKED_UPSTREAM_MODIFIED=YES`, while `SCIENTIFIC_SEMANTICS_CHANGED=NO` means only that this read-only audit did not prove a result-semantic change—it does not clear the implementation discrepancy.

Counts: CRITICAL=3, MAJOR=4, MINOR=1, DOCUMENTED_LIMITATION=5. Final Report consistency is `FAIL`.

## 2. Audit Scope and Governance

Stage: `FINAL_ASSET_AND_REPORT_AUDIT_V2`. Start: `2026-08-28T16:01:10.3556072+08:00`. Finish: `2026-08-28T16:22:56+08:00`. Host: `LAPTOP-T960HBDO`; Windows: `Windows-11-10.0.26200-SP0`; Python: `3.13.9`. No username or credentials were recorded.

This was local and read-only for scientific assets: `REMOTE_ACTION=NO`, `GPU_ACTION=NO`, `SCIENTIFIC_RECOMPUTATION=NO`. No training, inference, Bootstrap, mapping, aggregation, SSH, internet access, dependency installation, GitHub action, or scientific-artifact mutation occurred. Only this V2 Markdown and JSON were created after a collision recheck. Historical audit files remain untouched at `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\FINAL_ASSET_AND_REPORT_AUDIT.md` and `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\FINAL_ASSET_AND_REPORT_AUDIT.json`.

## 3. Scientific Authorities

- Paper specification and numeric authority: `D:\桌面文件\ECG\project_notes\source_materials\arxiv_source\main.tex`.
- Executable authority: locked commit `238409835ef55358a10bbc3459dfa9aaa91ad5e5` at `D:\桌面文件\ECG\upstream\ecg-fm-benchmarking`. Observed HEAD matches, but the worktree integrity fails; see V2-C001.
- Runtime evidence: finalized tables, manifests, logs, sidecars/sidecar records, Bootstrap outputs, worker evidence, and closure records under `D:\桌面文件\ECG`.

These authorities were kept separate. No upstream-main content was fetched or followed.

## 4. Benchmark Contract Verification

The audited contract is PTB-XL v1.0.3: 21,799 ECGs, 18,869 patients, 12 leads, 500 Hz; folds 1–8/9/10 contain 17,418/2,183/2,198 records with zero patient overlap. Label spaces are all/sub/super = 71/23/5 outputs on the same signals, split, and 2,198 test records. The experiment matrix is 30 Finetuning + 24 Frozen + 24 Linear = 78, with no S4/Net1D Frozen or Linear rows.

The paper/source protocol records AdamW, LR 1e-3, weight decay 1e-3, constant schedule, batch 64, 100 epochs, BCEWithLogits, best validation aggregated Macro AUROC checkpoint, record-level mean-over-window aggregation, and record-level Bootstrap (1,000 iterations, 95% CI, N=2,198). Sources: `D:\桌面文件\ECG\project_notes\source_materials\arxiv_source\main.tex`, locked repository at `D:\桌面文件\ECG\upstream\ecg-fm-benchmarking`, and `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\FINAL_CPU_BOOTSTRAP_MANIFEST.json`. The worktree discrepancy prevents an unqualified repository-integrity PASS.

## 5. Formal 78-Run Coverage

Expected=78; audited=78; missing=0; duplicate canonical keys=0; unexpected=0; ambiguous identities=9. Each canonical model × granularity × mode key joins to a finalized table row, Bootstrap row, and training-metadata row. Per-run audit records are embedded in `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\FINAL_ASSET_AND_REPORT_AUDIT_V2.json` under `formal_runs.records`.

The nine ambiguous entries are SUB ECG-CPC (all three modes), SUB ECG-FM (all three modes), and SUPER ECG-CPC (all three modes). Final tables and summaries retain `...CANONICAL_RUN_ID_PENDING_LOCAL_RECOVERY`, while `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\PARALLEL_451_RESIDUAL_SPECIAL_RECOVERY.csv` supplies exact recovered IDs (`052_01` through `052_09`) with bundle/hash PASS. This is critical provenance inconsistency V2-C002, not a missing scientific result.

## 6. Final Table 3–5 Audit

| Table | Mode | Rows | Numeric paper/ours/difference | Structural result |
|---|---:|---:|---:|---|
| `D:\桌面文件\ECG\tables\FINAL_TABLE3_FINETUNING.csv` | Finetuning | 30 | 30/30/30 | PASS |
| `D:\桌面文件\ECG\tables\FINAL_TABLE4_FROZEN.csv` | Frozen | 24 | 24/24/24 | PASS |
| `D:\桌面文件\ECG\tables\FINAL_TABLE5_LINEAR.csv` | Linear | 24 | 24/24/24 | PASS |

Combined rows=78, unique combinations=78, duplicates=0, missing expected combinations=0, unexpected combinations=0. S4 Frozen/Linear and Net1D Frozen/Linear counts are all zero. Numeric coverage is paper=78/78, ours=78/78, difference=78/78. Sixty-eight stale notes contradict verified paper-reference metadata; see V2-M001.

## 7. Paper Reference Verification

The three authoritative LaTeX tables (`tab:finetuning_result`, `tab:frozen_result`, `tab:linear_evaluation_result`) were parsed directly from `D:\桌面文件\ECG\project_notes\source_materials\arxiv_source\main.tex` and mapped by model, granularity, and mode. Match=78, mismatch=0, unverified=0, tolerance=`5e-12`. No finalized numeric paper-reference conflict was found.

## 8. Paper-vs-Ours Difference Verification

All 78 stored differences equal `ours - paper` within `5e-12`. Recomputed absolute-difference statistics:

| Scope | Count | Mean | Median | Max |
|---|---:|---:|---:|---:|
| Overall | 78 | 0.008425 | 0.001943 | 0.133420 |
| Finetuning | 30 | 0.005263 | 0.002307 | 0.026627 |
| Frozen | 24 | 0.008234 | 0.002000 | 0.097321 |
| Linear | 24 | 0.012568 | 0.001336 | 0.133420 |
| all | 26 | 0.005243 | 0.002031 | 0.030441 |
| sub | 26 | 0.012597 | 0.002274 | 0.133420 |
| super | 26 | 0.007433 | 0.001651 | 0.075109 |

Distribution: `|Δ|<0.002`=40; `<0.005`=58; `<0.010`=66; `>=0.010`=12. ECGFounder has 9 entries, mean |Δ|=0.000659527, max=0.001299993. ST-MEM Finetuning differences are approximately +0.024892/+0.020550/+0.026627 for all/sub/super. ECGFM-KED Frozen sub/super are +0.097321/+0.043671 and Linear sub/super +0.133420/+0.075109. ECG-CPC Linear(all) is paper 0.904, ours 0.873559, Δ=-0.030441. Eight of nine paper/ours top-model panels agree; Frozen(all) differs (paper: ECG-JEPA; ours: ECG-CPC). Source: the three finalized CSVs.

## 9. Strict ECG-ID Mapping Audit

PASS=77, historical blocker=1, missing=0. The only blocker is `PTBXL_ALL_ECGFOUNDER_FROZEN_FORMAL_RUN_001`. Preserved secondary records in `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\MAPPING_EVIDENCE_ACQUISITION_MANIFEST.csv`, `D:\桌面文件\ECG\execution_control\PTBXL_ALL_FINAL_CLOSURE_AUDIT\findings.md`, and `D:\桌面文件\ECG\docs\PTBXL_ALL_FROZEN_LINEAR_FINAL_CLOSURE_REPORT.md` record `TARGET_GROUP_CONSISTENCY=False`, 2,198 unique ECG IDs, aggregation reconstruction PASS, and saved aggregate match PASS. The original raw bundle/sidecar was not locally locatable for direct V2 inspection.

The run is not mapping PASS and not mapping missing. Its record-level prediction is not automatically invalid, but highest-grade group-level prediction↔target provenance is incomplete; sample-level correctness analysis must carry this limitation. No sidecar was changed or recomputed.

## 10. Bootstrap Audit

`D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\FINAL_BOOTSTRAP_SUMMARY.csv` has 78 unique canonical keys: complete=72, provenance-blocked=5, failed=0, mapping-blocker-not-eligible=1. The five blocker identities exactly match the expected list in `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\FINAL_CPU_BOOTSTRAP_MANIFEST.json`. Their formal AUROCs exist, strict mapping is PASS, and the limitation is non-unique historical canonical aggregate/target provenance—not model, mapping, prediction, or computation failure.

For all 72 complete rows, iterations=1,000 and CI bounds are present. The manifest records ECG-record sampling, N=2,198, and 95% CI. The finalized CI evidence supports paper point estimate inside ours CI for 65/72. This is a descriptive consistency check, not a statistical-equivalence proof.

## 11. Emergency-Worker Evidence Audit

The SUB/SUPER grouping contains 22 expected and 22 verified formal runs. `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\PARALLEL_WORKER_EVIDENCE_RECOVERY.csv` records 22/22 recovered scientific bundles; `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\PARALLEL_WORKER_STRICT_MAPPING_FINAL.csv` records 22/22 mapping PASS. All 88 historical remote/local pairs in `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\PARALLEL_WORKER_HASH_CLOSURE.csv` were checked against a freshly streamed SHA256 of the current local files: 88/88 match, zero missing, zero mismatches, and 88/88 sizes match. No worker was contacted.

## 12. Delivery Manifest Integrity Audit

`D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\FINAL_DELIVERY_MANIFEST.csv` and its JSON counterpart are semantically consistent at 24 rows. Artifact identities and paths are unique; invalid paths=0, missing files=0, stale sizes=0, stale hashes=0. Streamed SHA256 verification is 24/24 PASS.

Integrity is therefore PASS for listed files, but delivery completeness is not: key training-metadata and paper/table-correction artifacts are omitted from both the manifest and `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\MENTOR_HANDOFF_INDEX.md`. See V2-M004. The manifest was not refreshed.

## 13. Training Metadata Recovery Audit

`D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\FINAL_TRAINING_METADATA_RECOVERY.csv` and JSON agree across 78 unique runs: checkpoint reference recovered=78, missing=0; formal-time best-checkpoint use recorded=78; best epoch=50 recovered/28 not recovered; runtime=15/63; current checkpoint binary=10 available/68 unavailable/0 unproven. No blank status was silently classified.

Formal test having used the best checkpoint, the reference remaining traceable, and the binary still being locally retained are three separate facts. The 28/63/68 gaps are documented metadata/retention limitations, not scientific-result failures.

## 14. Accepted Remediations and Scientific Preservation

Coverage is `PARTIAL_WITH_MAJOR_FINDINGS`. Finalized documentation covers ST-MEM runtime closure, ECG-JEPA identity aggregation, ECG-FM Python 3.9 in part, 052→451, and worker recovery. Underlying local evidence also exists for the ECG-CPC compatibility route, MERL/ECGFM-KED execution-only BN guard, 573/871→780/775 successors, and minimal bundle strategy, but the closure/handoff/Final Report do not consistently carry all required details. Exact evidence paths are enumerated in `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\FINAL_ASSET_AND_REPORT_AUDIT_V2.json` under `accepted_remediations`.

Scientific-preservation wording cannot be accepted unqualified because the locked worktree is modified (V2-C001). No result-level scientific-semantics change was proven, so `SCIENTIFIC_SEMANTICS_CHANGED=NO`, but this remains a STOP requiring human provenance review. The Final Report's ST-MEM wording also implies an unsupported execution/dependency-route explanation for the deviation (V2-M003).

## 15. Final Report Consistency Audit

`D:\桌面文件\ECG\Final Report.doc` is a genuine legacy OLE compound `.doc` (magic `D0 CF 11 E0 A1 B1 1A E1`). It was opened through Microsoft Word COM with `ReadOnly=True`, automation macros disabled, no link update, no save, and no source modification. Extracted text was temporary and deleted. Readable content comprised 784 paragraphs and 14 tables; comments=0 and revisions=0.

All nine required semantic areas are present. Explicit model×granularity×mode values and headline difference statistics match finalized CSVs; 8/9 panel and 65/72 descriptive observations are accurate. No TODO/FIXME/TBD/TBC/UNKNOWN/待补/待确认/placeholder/lorem marker was found. However, the report omits several final evidence and metadata counts, incompletely covers accepted remediations, uses unsupported ST-MEM causal/route language, and states upstream was not modified despite the worktree evidence. `REPORT_CONSISTENCY=FAIL`.

## 16. Documented Limitations

1. `PTBXL_ALL_ECGFOUNDER_FROZEN_FORMAL_RUN_001`: historical mapping blocker; original local sidecar/raw bundle not directly inspectable in V2.
2. Five exact Bootstrap provenance blockers; no unified CI, not failures.
3. Best epoch not recovered for 28 runs.
4. Runtime not recovered for 63 runs.
5. Checkpoint binary not locally retained for 68 runs, while all 78 references remain traceable.

These five limitation categories do not increase the critical count.

## 17. Findings

| ID | Severity | Category | Affected artifact/run | Scientific impact | Auto-fixed |
|---|---|---|---|---|---|
| V2-C001 | CRITICAL | LOCKED_UPSTREAM_INTEGRITY | D:\桌面文件\ECG\upstream\ecg-fm-benchmarking | A new substantive implementation-governance discrepancy. The audit cannot prove that finalized scientific artifacts were produced with unchanged semantics, although no result-level contradiction was established by this check. | false |
| V2-C002 | CRITICAL | FORMAL_RUN_IDENTITY_PROVENANCE | 9 SUB/SUPER ECG-CPC or ECG-FM formal entries | The 78 results are located, but exact per-run traceability is ambiguous for nine entries and finalized navigation conflicts with recovery evidence. | false |
| V2-C003 | CRITICAL | FINALIZED_STATUS_CONTRADICTION | D:\桌面文件\ECG\tables\PTBXL_GLOBAL_FORMAL_RUN_COMPLETION_MATRIX.csv | A mentor following the advertised canonical route receives materially incorrect mapping/Bootstrap status and incomplete result metadata. | false |
| V2-M001 | MAJOR | FINAL_TABLE_METADATA | 68 rows across FINAL_TABLE3/4/5 | The numeric results are correct, but provenance annotations are internally contradictory and can mislead reviewers. | false |
| V2-M002 | MAJOR | FINAL_REPORT_COMPLETENESS | D:\桌面文件\ECG\Final Report.doc | Substantive reproducibility and limitation context is incomplete for mentor delivery, although stated table values match finalized CSVs. | false |
| V2-M003 | MAJOR | UNSUPPORTED_CAUSAL_LANGUAGE | Final Report.doc / ST-MEM Finetuning discussion | The wording overstates the supported root-cause boundary for a model-specific outlier. | false |
| V2-M004 | MAJOR | DELIVERY_COMPLETENESS | FINAL_DELIVERY_MANIFEST.csv/json and MENTOR_HANDOFF_INDEX.md | Listed manifest integrity is intact, but mentor-facing provenance navigation is materially incomplete. | false |
| V2-N001 | MINOR | BOOTSTRAP_JSON_SCHEMA | D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\FINAL_BOOTSTRAP_SUMMARY.json | No scientific result changes; this is a small machine-readable completeness issue. | false |
| V2-DL001 | DOCUMENTED_LIMITATION | HISTORICAL_MAPPING_BLOCKER | PTBXL_ALL_ECGFOUNDER_FROZEN_FORMAL_RUN_001 | Record-level prediction is not automatically invalid; highest-grade group-level prediction↔target provenance is incomplete, so sample-correctness analyses require this limitation. | false |
| V2-DL002 | DOCUMENTED_LIMITATION | BOOTSTRAP_PROVENANCE_BLOCKERS | PTBXL_ALL_ECGFOUNDER_FINETUNING_FORMAL, PTBXL_ALL_ECGFOUNDER_LINEAR_FORMAL_RUN_002, PTBXL_ALL_ECG_CPC_FINETUNING_FORMAL, PTBXL_ALL_NET1D_FINETUNING_FORMAL, PTBXL_ALL_S4_FINETUNING_FORMAL | Formal AUROC remains available; unified Bootstrap CI is unavailable for these five results. | false |
| V2-DL003 | DOCUMENTED_LIMITATION | BEST_EPOCH_RECOVERY | 28 of 78 formal runs | Metadata completeness limitation only; formal-time best checkpoint use and checkpoint reference remain recorded. | false |
| V2-DL004 | DOCUMENTED_LIMITATION | RUNTIME_RECOVERY | 63 of 78 formal runs | Metadata completeness limitation only. | false |
| V2-DL005 | DOCUMENTED_LIMITATION | CHECKPOINT_BINARY_RETENTION | 68 of 78 formal runs | Artifact-retention limitation, not a formal-result failure. | false |


Full expected/observed text, evidence paths, and recommended human action for every finding are in `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\FINAL_ASSET_AND_REPORT_AUDIT_V2.json` under `findings`. No finding was auto-fixed.

## 18. Final Verdict

`AUDIT_STATUS=FAIL` because CRITICAL findings V2-C001 through V2-C003 remain unresolved. The finalized numeric tables, paper reference mapping, difference recomputation, mapping counts, Bootstrap counts, worker hashes, listed-manifest hashes, and training-metadata counts pass their direct checks; this does not override the repository-integrity and final-provenance contradictions.

`NEW_SUBSTANTIVE_DISCREPANCY=YES`; `LOCKED_UPSTREAM_MODIFIED=YES`; `SCIENTIFIC_SEMANTICS_CHANGED=NO` (not proven, pending human provenance review). Existing release-readiness/closed state is not accepted for mentor handoff under V2.

## 19. GitHub Handoff Readiness Recommendation

`NEXT_STAGE_RECOMMENDATION=STOP_FOR_HUMAN_REVIEW`. Do not begin GitHub handoff inventory, size audit, staging, HTML, packaging, Git operations, upload, or collaborator invitation. `NEXT_STAGE_AUTHORIZED=NO`.
