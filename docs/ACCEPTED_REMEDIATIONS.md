# ACCEPTED EXECUTION REMEDIATIONS — FINAL V1

Generated: 2026-08-28T11:12:50.198Z

This canonical summary is additive. It describes execution compatibility and provenance decisions; it does not change the locked paper specification, finalized AUROC values, predictions, targets, aggregation, mapping, Bootstrap outputs, or Tables 3–5.

## 1. ST-MEM runtime dependency closure

The accepted dependency and execution remediation allowed the locked implementation to run. The accepted runtime-resampling and optimizer-grouping patches are recorded at:

- `D:\桌面文件\ECG\audits\st_mem\STMEM_A_E_REMEDIATION_PREFLIGHT_AUDIT.md`
- `D:\桌面文件\ECG\experiments\ptbxl_all\st_mem\remote_audits\STMEM_119_RUNTIME_RESAMPLING_APPLIED.patch`
- `D:\桌面文件\ECG\experiments\ptbxl_all\st_mem\remote_audits\STMEM_119_OPTIMIZER_GROUPING_APPLIED.patch`

For SUB/SUPER Finetuning, clean `RETRY_03` successes supersede prior failed attempts. The successful records and strict mapping are in:

- `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\mapping_evidence\instance_780\PTBXL_SUB_07_ST_MEM_FINETUNING_FORMAL_RETRY_03`
- `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\mapping_evidence\instance_775\PTBXL_SUPER_07_ST_MEM_FINETUNING_FORMAL_RETRY_03`
- `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\STMEM_780_775_STRICT_MAPPING_VERIFICATION.json`

These compatibility events must not be claimed as the cause of the observed ST-MEM Finetuning AUROC deviations; no root cause for those deviations is proven.

## 2. ECG-CPC compatibility route

The accepted route comprises PyKeOps 2.3, NVRTC visibility, `CUDA_PATH=/usr/local/cuda-12.4`, precedence for the torch-cu126 NVIDIA runtime libraries in `LD_LIBRARY_PATH`, FP32 execution, and historical checkpoint/dataset path shims. Evidence:

- `D:\桌面文件\ECG\reports\PTBXL_ECG_CPC_REPRODUCTION.md`
- `D:\桌面文件\ECG\docs\PTBXL_ALL_SPECIAL_FROZEN_LINEAR_READINESS.md`
- `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\PARALLEL_451_RESIDUAL_SPECIAL_BUNDLE\PTBXL_SUB_ECG_CPC_FINETUNING_FORMAL_052_01\formal_execution_metadata.json`

The route is execution compatibility and path portability; it is not a scientific-result rewrite.

## 3. ECG-FM Python 3.9 compatibility overlay

The accepted environment is Python 3.9.23, fairseq-signals `1.0.0a0+571a124`, torch 2.8.0 (recorded CUDA build `2.8.0+cu128` where reported), Lightning 2.5.5, OmegaConf 2.1.1, and TensorBoard 2.21.0. The formal overlay route is:

`/root/autodl-tmp/ECG/execution_overlays/ecg_fm_py39_compat/ecg-fm-benchmarking`

The all-Finetuning route used its separately approved dedicated worktree; the other eight ECG-FM formal experiments used the Python 3.9 overlay. Evidence:

- `D:\桌面文件\ECG\reports\PTBXL_ECG_FM_REPRODUCTION.md`
- `D:\桌面文件\ECG\execution_control\PTBXL_451_ECGFM_SUPER_FINAL_CONTROLLER\findings.md`
- `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\LOCKED_UPSTREAM_DIRTY_WORKTREE_FORENSIC_AUDIT.md`
- `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\mapping_evidence\instance_451\PTBXL_ALL_ECG_FM_FROZEN_FORMAL_RUN_015_RETRY_01\formal_execution_metadata.json`

## 4. ECG-JEPA identity aggregation adjudication

For the six affected whole-record ECG-JEPA routes, there is one test segment per ECG. Mean aggregation is therefore the identity operation: the aggregated prediction equals the original prediction while remaining separately named. This is legal locked-implementation behavior, not an overwrite or aliasing bug.

Evidence: `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\ECG_JEPA_AGG_NOAGG_DISCREPANCY_ADJUDICATION.json`.

## 5. MERL / ECGFM-KED execution-only BN guard

The accepted Frozen/Linear runner reapplies `encoder.eval()` after wrapper training-mode transitions so frozen encoder BatchNorm state is not updated. It is an execution-only guard; the active head and declared mode remain the scientific branch.

Evidence:

- `D:\桌面文件\ECG\scripts\ptbxl_frozen_linear_bn_guard_runner.py`
- `D:\桌面文件\ECG\tables\PTBXL_SUB_573_ALL_MODES_COMMAND_MATRIX.csv`
- `D:\桌面文件\ECG\tables\PTBXL_SUPER_871_ALL_MODES_COMMAND_MATRIX.csv`
- `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\PARALLEL_WORKER_EVIDENCE_BUNDLE\PTBXL_SUB_14_ECGFM_KED_FROZEN_FORMAL_SUB2\exact_formal_command.sh`

The guard must not be asserted as the cause of the ECGFM-KED outliers; that causal claim is unproven.

## 6. Historical 052 to clone/evidence carrier 451

Instance 052 remains the historical authority. Instance 451 is the read-only clone/evidence carrier for the nine residual special runs; the recovery record does not redefine 451 as the original execution authority.

Evidence:

- `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\PARALLEL_451_RESIDUAL_SPECIAL_RECOVERY.json`
- `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\PARALLEL_451_RESIDUAL_SPECIAL_RECOVERY.csv`
- `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\PARALLEL_451_RESIDUAL_SPECIAL_BUNDLE`

## 7. Predecessors 573/871 to successors 780/775

The SUB common route prepared under predecessor context 573 is represented by successor evidence from 780; the SUPER common route prepared under predecessor context 871 is represented by successor evidence from 775. The versioned handoff must preserve predecessor/successor provenance rather than collapsing instance identities.

Evidence:

- `D:\桌面文件\ECG\tables\PTBXL_SUB_573_ALL_MODES_COMMAND_MATRIX.csv`
- `D:\桌面文件\ECG\tables\PTBXL_SUB_780_STMEM_SUCCESSOR_COMMAND_MATRIX.csv`
- `D:\桌面文件\ECG\tables\PTBXL_SUPER_871_ALL_MODES_COMMAND_MATRIX.csv`
- `D:\桌面文件\ECG\tables\PTBXL_SUPER_775_STMEM_SUCCESSOR_COMMAND_MATRIX.csv`
- `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\COMMON_780_775_STRICT_MAPPING_VERIFICATION.json`
- `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\STMEM_780_775_ACQUISITION_RECORD.csv`

## 8. Emergency-worker evidence recovery

Twenty-two formal scientific bundles were recovered; all 22 strict mappings passed; 88 of 88 recorded remote/local artifact SHA256 pairs matched.

Evidence:

- `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\PARALLEL_WORKER_EVIDENCE_RECOVERY.csv`
- `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\PARALLEL_WORKER_HASH_CLOSURE.csv`
- `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\PARALLEL_WORKER_STRICT_MAPPING_FINAL.csv`
- `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\PARALLEL_WORKER_EVIDENCE_BUNDLE`

## 9. Minimal scientific evidence bundle strategy

Long-term handoff prioritizes prediction/target arrays, saved aggregates, mapping evidence, Bootstrap outputs, exact commands, completion validation, and provenance/hash records. It intentionally does not duplicate the entire PTB-XL dataset, environments, caches, every checkpoint binary, or runtime trees.

Evidence:

- `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\STMEM_780_775_ACQUISITION_RECORD.csv`
- `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\PARALLEL_WORKER_EVIDENCE_RECOVERY.csv`
- `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\FINAL_TRAINING_METADATA_RECOVERY.csv`
- `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\FINAL_CLOSURE_REPORT_FINAL.md`

This retention strategy explains why 68 checkpoint binaries are not locally retained while their formal best-checkpoint references remain traceable. It is a documented completeness limitation, not a loss of the finalized result.

## Final preservation statement

- `LOCKED_COMMIT_IDENTITY_VERIFIED=YES`
- `FORMAL_EXECUTION_UNAPPROVED_UPSTREAM_MODIFICATION_PROVEN=NO`
- `SCIENTIFIC_SEMANTICS_CHANGED=NO`
- `SCIENTIFIC_RESULT_VALUES_MODIFIED=NO`
- `SCIENTIFIC_ARTIFACT_RECOMPUTATION_REQUIRED=NO`
