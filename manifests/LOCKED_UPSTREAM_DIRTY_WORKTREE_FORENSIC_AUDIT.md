# LOCKED UPSTREAM DIRTY WORKTREE FORENSIC AUDIT

## 1. Executive Summary

The local repository at `D:\桌面文件\ECG\upstream\ecg-fm-benchmarking` is currently dirty, while `HEAD` still equals the locked authority `238409835ef55358a10bbc3459dfa9aaa91ad5e5`. Git reports four modified tracked Python files and one deleted tracked SVG, with no staged or untracked changes.

The current Windows checkout itself is not proven to have been executed by any formal run. Formal commands point to distinct Linux paths under `/root/autodl-tmp/ECG/...`. However, equivalent model-specific code changes were used by formal routes: ECG-FM used an approved patched worktree for PTB-XL(all) Finetuning and a documented Python 3.9 overlay for the other eight ECG-FM experiments; ST-MEM used the approved resampling and optimizer-grouping remediations; ECGFM-KED used the approved nested-checkpoint loader in its model-specific worktree. No unapproved source change is proven in a formal route.

The local dirty state is a composite residue: the ECGFM-KED loader remediation was applied first, the ECG-FM minimal integration was added while preserving that pre-existing change, and the ST-MEM resampling/optimizer fixes were then added while preserving both. The source provenance records and file hashes establish this sequence. `abstract.svg` has no located deletion provenance and is non-scientific.

Verdict: `FORMAL_EXECUTION_USED_CURRENT_DIRTY_WORKTREE=NOT_PROVEN`; `FORMAL_EXECUTION_USED_EQUIVALENT_MODIFIED_CODE=YES_DOCUMENTED_ACCEPTED`; `FORMAL_SCIENTIFIC_RESULT_IMPACT=DOCUMENTED_ACCEPTED_EXECUTION_REMEDIATION_ONLY`. No new scientific-result contradiction was found, and no scientific artifact recomputation is evidence-required. The historical phrase “locked upstream was not modified” requires qualification because it is false for the current local working tree and because formal routes sometimes used documented worktrees/overlays based on the locked commit.

## 2. Scope and Governance

This was a local, read-only forensic audit. It did not train, infer, map, aggregate, bootstrap, regenerate artifacts, connect to a remote host, or mutate Git state. The only writes are this report and its companion JSON. The nine previously identified ambiguous run identities remain classified as `PROVENANCE_IDENTITY_ONLY` and were not re-audited.

- Audit time: 2026-08-28, Asia/Shanghai.
- Local repository: `D:\桌面文件\ECG\upstream\ecg-fm-benchmarking`.
- Expected commit: `238409835ef55358a10bbc3459dfa9aaa91ad5e5`.
- Scientific authority separation: locked commit, documented execution overlay/remediation, and actual formal runtime evidence were evaluated separately.

## 3. Locked Commit Verification

Read-only Git results:

```text
git rev-parse --show-toplevel
D:/桌面文件/ECG/upstream/ecg-fm-benchmarking

git rev-parse HEAD
238409835ef55358a10bbc3459dfa9aaa91ad5e5

git status --porcelain=v1
 D abstract.svg
 M code/clinical_ts/models/ecg_foundation_models/ecg_fm_config.py
 M code/clinical_ts/models/fm_ecg.py
 M code/main_lite.py
 M code/main_lite_ecg.py
```

`git diff --cached --name-status` was empty; `git ls-files --others --exclude-standard` was empty. The substantive differences remain under `git diff --ignore-space-at-eol`, so they are not line-ending-only or permission-only changes.

## 4. Current Working-Tree Changes

| Relative path | Status | Current file | Current size | Current SHA256 | LastWriteTime | Locked blob SHA | Locked size | + / - | Scientific code/config |
|---|---:|---:|---:|---|---|---|---:|---:|---:|
| `abstract.svg` | D | NO | n/a | n/a | n/a | `ad36864d4514f27b4217171b752db9cfaa2a2ea6` | 3,331,327 | 0 / 3,088 | NO |
| `code/clinical_ts/models/ecg_foundation_models/ecg_fm_config.py` | M | YES | 1,122 | `752c420f5e7d9b57bb7148e635a2956742923a5476f753364e4e03ee7677c0ed` | `2026-08-17T11:49:13.8880184+08:00` | `7c4d5fd6d39a1052cec1f3f8785203717ad82922` | 1,205 | 42 / 42 | YES |
| `code/clinical_ts/models/fm_ecg.py` | M | YES | 44,254 | `4010498cc28b0aa7baa304143739784576181db8244b2a587baa77bd730ac9bb` | `2026-08-17T12:21:10.6637481+08:00` | `a2ae161c58f20748ad11ccfb9acd51233e65d5c8` | 43,880 | 110 / 118 | YES |
| `code/main_lite.py` | M | YES | 28,728 | `ff8d2b9ecf8b2e4c55cfb983bdf2fa35cd49fc111cf4f82bc36bd611c68fee87` | `2026-08-17T12:18:17.6463788+08:00` | `19a9cc198fe0b1837effd6f97afb3bdd89a78aa0` | 28,147 | 1 / 1 | YES |
| `code/main_lite_ecg.py` | M | YES | 21,377 | `601162753834ccf1b2e92a90ad5d2628a021df44a036d0621a217b01f8193683` | `2026-08-17T11:47:30.1338451+08:00` | `f5884f43717b20d38a1f593d13a218ac4ca158b4` | 20,575 | 10 / 1 | YES |

Git’s total is 163 insertions and 3,250 deletions. Most deletions are the removed SVG; the Python changes are compact, identifiable hunks.

## 5. Per-File Diff Analysis

### `abstract.svg`

The tracked illustration is absent. No project-local provenance explaining its deletion was located; only README references and the V2 audit mention it. It is not executable and cannot affect model, data, predictions, mapping, aggregation, Bootstrap, or AUROC. Impact level: `LEVEL 0: NON_SCIENTIFIC_OR_UNUSED`.

### `ecg_fm_config.py`

Lines 1–43 activate the previously commented `ECGTransformerFinetuningConfig` import and `ECG_FM_CONFIG`. Locked behavior left this integration disabled; current behavior constructs the configuration used by the ECG-FM wrapper. If executed, it enables the ECG-FM architecture but does not itself alter the recorded checkpoint, data, sampling, precision, or benchmark hyperparameters. It exactly matches the approved ECG-FM minimal-integration scope recorded in `D:\桌面文件\ECG\audits\ecg_fm\integration_preflight\source_provenance.md`. Impact level: `LEVEL 2` for formal ECG-FM routes through approved worktree/overlay equivalents.

### `fm_ecg.py`

This file contains three independent substantive regions:

1. ST-MEM optimizer grouping, current lines 412–420: names from `self.model.encoder.named_parameters()` are matched without an erroneous outer `encoder.` prefix. Locked behavior left all 166 encoder tensors outside the intended early/later groups; current behavior assigns the intended groups at LRs 0.00001 and 0.0001. The exact hunk and runtime parameter coverage are documented in `D:\桌面文件\ECG\audits\st_mem\STMEM_A_E_REMEDIATION_PREFLIGHT_AUDIT.md` and `D:\桌面文件\ECG\experiments\ptbxl_all\st_mem\remote_audits\STMEM_119_OPTIMIZER_GROUPING_APPLIED.patch`.
2. ECGFM-KED checkpoint handling, current line 659: locked code attempted to interpret the checkpoint’s top-level keys; current code loads `checkpoint["ecg_model"]` with `strict=False`. The official checkpoint has 1,224 nested entries and the approved validation reports zero missing and zero unexpected keys. Evidence: `D:\桌面文件\ECG\audits\ecgfm_ked\ECGFM_KED_LOADER_REMEDIATION_PROVENANCE.md` and the formal prelaunch diff under `D:\桌面文件\ECG\experiments\ptbxl_all\ecgfm_ked\formal_archive_195\formal_runs\ecgfm_ked_ptbxl_all_100e_195\git_diff_prelaunch.patch`.
3. ECG-FM wrapper activation, current lines 976 onward, including `dataclasses.replace`, fairseq-signals import, wrapper construction, optimizer groups, and forward dispatch. It matches the approved minimal-integration artifact `D:\桌面文件\ECG\experiments\ptbxl_all\ecg_fm\remote_artifacts\ecg_fm_ptbxl_all_formal_20260817T104823Z\evidence\ecg_fm_minimal_integration.diff`.

No single formal route is shown to have used this entire composite Windows file. Model-specific routes used their corresponding approved hunk(s). Impact level: `LEVEL 2` by hunk; no `LEVEL 4` use was found.

### `main_lite.py`

Current line 178 changes:

```text
len(memmap_meta)==0  ->  len(memmap_meta)!=0
```

The corrected branch adds `Resample(memmap_meta["fs"], fs_model)` when memmap metadata exists and the model rate differs. For PTB-XL `records500`, the locked condition skipped this intended branch; the current condition converts, for example, a 2.4 s ST-MEM segment from `(12,1200)` at 500 Hz to `(12,600)` at 250 Hz. This is documented and human-approved in `D:\桌面文件\ECG\audits\st_mem\STMEM_A_E_REMEDIATION_PREFLIGHT_AUDIT.md`, with the exact patch at `D:\桌面文件\ECG\experiments\ptbxl_all\st_mem\remote_audits\STMEM_119_RUNTIME_RESAMPLING_APPLIED.patch`.

By formal configuration, this shared branch is potentially relevant to 39 experiments: ECG-JEPA (9), ST-MEM (9), HuBERT-ECG (9), ECG-CPC (9), and S4 (3). Exact source hashes at launch were not retained for every shared-entry route. Existing behavior evidence is consistent with the intended contract: the ST-MEM real-data gate produced `(12,600)`; the PTB-XL(all) ECG-CPC Frozen and Linear logs show input sequence length 600 for 2.5 s at 240 Hz; ECG-JEPA’s wrapper requires exactly 2,500 time steps at 250 Hz. This is a provenance-coverage limitation, not evidence that any finalized result is wrong.

Impact level: `LEVEL 2` for the documented ST-MEM formal route; `LEVEL U` only for whether every other potentially affected direct-upstream route used this exact file byte-for-byte. No contradictory signal shape, split, prediction, mapping, or aggregation evidence was found.

### `main_lite_ecg.py`

Current line 21 imports `ECG_FM_Wrapper`; lines 191–200 add `architecture == "ecg_fm"` construction. Locked behavior had no active ECG-FM dispatch. It is the approved minimal ECG-FM integration, not a general preprocessing or metric change. Impact level: `LEVEL 2` for approved ECG-FM worktree/overlay routes.

## 6. Modification Provenance Search

The project-local evidence reconstructs this order:

1. ECGFM-KED loader remediation: `D:\桌面文件\ECG\audits\ecgfm_ked\ECGFM_KED_LOADER_REMEDIATION_PROVENANCE.md`, approved marker `HUMAN_APPROVED_MINIMAL_ECGFM_KED_NESTED_CHECKPOINT_LOADER_REMEDIATION`, post-file SHA256 `467d1a...6748`. Its patch file timestamp is 2026-08-17 11:45 local.
2. ECG-FM integration: `D:\桌面文件\ECG\audits\ecg_fm\integration_preflight\source_provenance.md` explicitly says the ECGFM-KED loader was a pre-existing unrelated change, preserved and excluded from `minimal_integration.diff`. It records the current config and `main_lite_ecg.py` hashes.
3. ST-MEM remediation: `D:\桌面文件\ECG\audits\st_mem\STMEM_A_E_REMEDIATION_PREFLIGHT_AUDIT.md` explicitly says existing unrelated dirty changes were preserved. Its post-patch hashes equal the current `main_lite.py` and `fm_ecg.py` hashes.

Per-file source classification:

| File/change | Modification source | Evidence |
|---|---|---|
| `abstract.svg` deletion | `UNKNOWN` | No provenance beyond README/V2 references |
| ECG-FM config activation | `DOCUMENTED_PATCH`; `FORMAL_EXECUTION_REMEDIATION` | ECG-FM integration provenance and formal source diff |
| ECG-FM wrapper/dispatch | `DOCUMENTED_PATCH`; `FORMAL_EXECUTION_REMEDIATION` | ECG-FM integration provenance and formal source manifest |
| ST-MEM optimizer grouping | `DOCUMENTED_PATCH`; `FORMAL_EXECUTION_REMEDIATION` | ST-MEM preflight, patch SHA, formal provenance |
| ST-MEM resampling condition | `DOCUMENTED_PATCH`; `FORMAL_EXECUTION_REMEDIATION` | ST-MEM preflight, patch SHA, formal provenance |
| ECGFM-KED nested loader | `DOCUMENTED_PATCH`; `FORMAL_EXECUTION_REMEDIATION` | KED loader provenance, prelaunch patch, loader-integrity JSON |

## 7. Execution Overlay Comparison

`ECG_FM_DIRTY_CHANGE_RELATION=PARTIAL_OVERLAP_WITH_OVERLAY`.

The three local ECG-FM regions match the approved minimal integration, but the full accepted ECG-FM formal patch also contains import-isolation/compatibility changes not present in the same form in the current local checkout. Conversely, the current `fm_ecg.py` contains ST-MEM and ECGFM-KED hunks unrelated to ECG-FM. Therefore the current checkout is neither the Python 3.9 overlay nor byte-identical to the all-Finetuning approved source patch.

The external routes are explicit:

- PTB-XL(all) ECG-FM Finetuning used `/root/autodl-tmp/ECG/worktrees/ecg_fm_preflight_245`; `git_status_at_launch.txt` lists four modified source files and the formal source manifest preserves `approved_source_diff.patch` and `ecg_fm_minimal_integration.diff` with hashes.
- The other eight ECG-FM experiments use `/root/autodl-tmp/ECG/execution_overlays/ecg_fm_py39_compat/ecg-fm-benchmarking/code/main_lite.py` with the same overlay path in `PYTHONPATH`. Exact commands are retained in the corresponding `formal_execution_metadata.json`, including `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\mapping_evidence\instance_451\PTBXL_ALL_ECG_FM_FROZEN_FORMAL_RUN_015_RETRY_01\formal_execution_metadata.json` and the SUB/SUPER residual bundles.
- ST-MEM overlays and hashes are enumerated in `D:\桌面文件\ECG\docs\PTBXL_SUB_SUPER_INSTANCE_RESTORE_PLAN.md` and used through `/root/autodl-tmp/ECG/worktrees/stmem_formal` or `STMEM_119_FORMAL_TRAIN_LAUNCH.py`.
- ECGFM-KED’s accepted execution overlay is enumerated in that same restore plan and its worktree is `/root/autodl-tmp/ECG/worktrees/ecgfm_ked`.

An overlay outside the repository is not itself a mutation of the repository. A patched model-specific Git worktree is dirty relative to the locked commit but remains distinct from the current Windows checkout.

## 8. Formal Execution Linkage

All formal commands use Linux paths; none uses `D:\桌面文件\ECG\upstream\ecg-fm-benchmarking`. There is no retained evidence that the current Windows directory was copied wholesale and then executed. The linkage is to equivalent, separately documented code.

| Route | Potentially relevant formal runs | Execution path proven | Locked commit recorded/anchored | External overlay or model worktree proven | Current Windows dirty tree use proven | Unresolved source identity |
|---|---:|---:|---:|---:|---:|---:|
| ECG-FM | 9 | 9 | 9 by locked-base provenance; exact launch commit retained for all-Finetuning | 9 (1 dedicated worktree + 8 Python 3.9 overlay routes) | 0 | 0 |
| ST-MEM | 9 | 9 | 9 by locked-base/restore provenance; exact commit in PTB-XL(all) Finetuning evidence | 7 model-worktree routes | 0 | 2 direct-upstream source hashes not retained (all Frozen/Linear) |
| ECGFM-KED | 9 | 9 | 9 by locked-base/restore provenance; exact commit in PTB-XL(all) Finetuning evidence | 7 model-worktree routes | 0 | 2 direct-upstream source hashes not retained (all Frozen/Linear) |
| Shared `main_lite.py` resampling condition | 39 | 39 entrypoint/command routes | Locked-base authority is recorded, but per-run source hashes are incomplete | Documented for ST-MEM; other routes use several worktrees/direct paths | 0 | 30 non-ST-MEM routes lack byte-level proof for this specific hunk |

Exact model-route identities used for this linkage:

- ECG-FM: `PTBXL_ALL_ECG_FM_FINETUNING_FORMAL` (archived remote directory `ecg_fm_ptbxl_all_formal_20260817T104823Z`), `PTBXL_ALL_ECG_FM_FROZEN_FORMAL_RUN_015_RETRY_01`, `PTBXL_ALL_ECG_FM_LINEAR_FORMAL_RUN_016`, `PTBXL_SUB_ECG_FM_FINETUNING_FORMAL_052_07`, `PTBXL_SUB_ECG_FM_FROZEN_FORMAL_052_08`, `PTBXL_SUB_ECG_FM_LINEAR_FORMAL_052_09`, `PTBXL_SUPER_ECG_FM_FINETUNING_FORMAL_052_10`, `PTBXL_SUPER_ECG_FM_FROZEN_FORMAL_052_11`, and `PTBXL_SUPER_ECG_FM_LINEAR_FORMAL_052_12`.
- ST-MEM: `PTBXL_ALL_ST_MEM_FINETUNING_FORMAL`, `PTBXL_ALL_ST_MEM_FROZEN_FORMAL_RUN_005`, `PTBXL_ALL_ST_MEM_LINEAR_FORMAL_RUN_006`, `PTBXL_SUB_07_ST_MEM_FINETUNING_FORMAL_RETRY_03`, `PTBXL_SUB_08_ST_MEM_FROZEN_FORMAL`, `PTBXL_SUB_09_ST_MEM_LINEAR_FORMAL`, `PTBXL_SUPER_07_ST_MEM_FINETUNING_FORMAL_RETRY_03`, `PTBXL_SUPER_08_ST_MEM_FROZEN_FORMAL`, and `PTBXL_SUPER_09_ST_MEM_LINEAR_FORMAL`.
- ECGFM-KED: `PTBXL_ALL_ECGFM_KED_FINETUNING_FORMAL`, `PTBXL_ALL_ECGFM_KED_FROZEN_FORMAL_RUN_009`, `PTBXL_ALL_ECGFM_KED_LINEAR_FORMAL_RUN_010`, `PTBXL_SUB_13_ECGFM_KED_FINETUNING_FORMAL_SUB2`, `PTBXL_SUB_14_ECGFM_KED_FROZEN_FORMAL_SUB2`, `PTBXL_SUB_15_ECGFM_KED_LINEAR_FORMAL_SUB2`, `PTBXL_SUPER_13_ECGFM_KED_FINETUNING_FORMAL_SUPER2`, `PTBXL_SUPER_14_ECGFM_KED_FROZEN_FORMAL_SUPER2`, and `PTBXL_SUPER_15_ECGFM_KED_LINEAR_FORMAL_SUPER2`.

For ECGFM-KED, seven commands explicitly resolve the KED worktree: PTB-XL(all) Finetuning and all six SUB/SUPER runs. The PTB-XL(all) Frozen/Linear commands invoke the BN guard without a recorded `PTBXL_EXECUTION_ROOT`; the guard defaults to `/root/autodl-tmp/ECG/upstream/ecg-fm-benchmarking`. Those two runs have complete result evidence and performance consistent with a loaded pretrained model, but no launch-time source hash proving the nested-loader hunk. This remains a provenance limitation, not proof of an unapproved loader.

## 9. Temporal Evidence

The four Python LastWriteTime values fall between 11:47 and 12:21 CST on 2026-08-17. The KED provenance/patch files are timestamped about 11:36–11:45; ECG-FM source provenance records the KED change as pre-existing; ST-MEM provenance records the ECG-FM/KED changes as pre-existing. The first archived ECG-FM and ST-MEM formal starts were at approximately 18:49 CST on 2026-08-17, and ECGFM-KED all-Finetuning started at 00:46 CST on 2026-08-18.

Thus all four Python changes are `PRE_FORMAL_POSSIBLE` in the local timeline and their purposes are documented. Filesystem times cannot prove the time of remote copying or remote execution. The deleted SVG has `TEMPORAL_RELATION=UNRESOLVED` because an absent file has no usable LastWriteTime.

## 10. main_lite.py Preprocessing Risk Analysis

1. Exact semantics: for a nonempty memmap metadata dictionary and `fs_model != memmap_meta["fs"]`, current code performs the intended rate conversion; locked code skipped it because it tested for an empty dictionary before indexing it.
2. Potential branch users: the 39 formal experiments configured below 500 Hz—ECG-JEPA, ST-MEM, HuBERT-ECG, ECG-CPC, and S4. Model-specific transforms can add further processing, but they occur after this shared transform list is constructed.
3. Formal PTB-XL use: proven for ST-MEM by patch hashes and real-data/formal provenance. Behavior consistent with the branch is independently visible for ECG-CPC (600 time steps at 2.5 s/240 Hz) and is required by ECG-JEPA’s exact 2,500-step interface.
4. Alternative scripts/overlays: ST-MEM uses `stmem_formal`; ECG-FM uses a Python 3.9 overlay but has `fs_model=fs_data=500`, so this condition is inactive for ECG-FM; ECGFM-KED also uses 500 Hz, so it is inactive there.
5. Independent validation: ST-MEM’s real-data gate validates `(12,1200) -> (12,600)`; formal outputs across all granularities have the expected labels, 2,198 aggregate records, strict mapping, and saved-aggregate reconstruction. These validate downstream artifacts but do not substitute for per-run source hashing.
6. Contract consistency: commands retain PTB-XL records500, declared source/model rates, fixed folds, expected output dimensions, and record-level aggregation.
7. Relation to the current Windows file: the current file’s hunk is exactly the approved ST-MEM patch. Formal use of the current Windows path is not proven; use of an equivalent hunk in ST-MEM formal execution is proven.

No evidence supports re-running preprocessing or any formal experiment.

## 11. ECG-FM Route Analysis

The local ECG-FM config, wrapper, and dispatch changes are the minimal model integration approved on 2026-08-17. They do not constitute the complete Python 3.9 overlay. The all-Finetuning formal run used an approved dirty remote worktree and preserved its commit, status, patch, command, checkpoint, data identity, output, and prediction evidence. The other eight ECG-FM runs have exact commands pointing to the external compatibility overlay.

`ECG_FM_DIRTY_CHANGE_RELATION=PARTIAL_OVERLAP_WITH_OVERLAY`.

`ECG_FM_FORMAL_EXECUTION_LINKAGE=EQUIVALENT_APPROVED_WORKTREE_OR_EXTERNAL_OVERLAY_PROVEN_FOR_9_OF_9; CURRENT_WINDOWS_WORKTREE_NOT_PROVEN`.

## 12. ST-MEM / ECGFM-KED Route Analysis

### ST-MEM

The optimizer prefix correction changes parameter grouping if Finetuning executes it; it is irrelevant to Frozen/Linear because those modes return head-only optimizer parameters. The resampling condition changes the input from 500 to 250 Hz and is required for the declared ST-MEM interface. Both were explicitly human-approved, validated, hash-preserved, and recorded in the PTB-XL(all) formal provenance. SUB/SUPER commands point to the restored `stmem_formal` worktree/launcher. The two PTB-XL(all) Frozen/Linear direct-upstream commands lack a launch-time source hash, but their source behavior and artifacts are consistent with the approved route.

No evidence attributes ST-MEM’s paper-vs-ours difference to a dependency or source remediation.

### ECGFM-KED

The nested loader is explicitly approved and validated against the actual 1,224-entry `ecg_model` state dict with zero missing/unexpected keys. PTB-XL(all) Finetuning and six SUB/SUPER commands use the KED worktree; the latter also retain the accepted `--skip-test-after-fit` and BN-guard execution routes where applicable. PTB-XL(all) Frozen/Linear lack per-run source hashing for the default upstream selected by the BN guard. That gap does not prove random initialization or an unapproved change, and no result/artifact contradiction was found.

No evidence attributes ECGFM-KED outliers to the BN guard or loader remediation.

## 13. Formal Scientific Impact Assessment

| Dirty change | Classification | Formal impact adjudication |
|---|---|---|
| `abstract.svg` deletion | LEVEL 0 | Non-scientific and unused |
| ECG-FM config activation | LEVEL 2 | Approved integration used through documented ECG-FM routes |
| ECG-FM wrapper/dispatch | LEVEL 2 | Approved integration used through documented ECG-FM routes |
| ST-MEM optimizer grouping | LEVEL 2 | Approved correction used by ST-MEM Finetuning |
| `main_lite.py` resampling condition | LEVEL 2 for ST-MEM; LEVEL U for byte-level identity of other shared routes | Intended rate conversion proven for ST-MEM; no contradictory formal signal/result evidence |
| ECGFM-KED nested loader | LEVEL 2 for proven KED worktree routes; LEVEL U for two all Frozen/Linear source hashes | Approved loader; no unapproved loader or result contradiction proven |

There is no `LEVEL 4` finding. Formal AUROC, predictions, targets, ECG-ID mapping, aggregation, Bootstrap outputs, and Tables 3–5 are not contradicted by this forensic audit.

## 14. Historical Statement Adjudication

Two propositions must be separated:

- “The current local locked repository working tree is clean”: false.
- “Formal execution introduced an unapproved modification to the locked scientific source”: not supported by the available evidence. Formal routes used the locked commit as base plus documented, approved model-specific worktrees/overlays; a few direct-upstream routes lack byte-level launch source hashes.

`HISTORICAL_STATEMENT_LOCKED_UPSTREAM_UNMODIFIED=REQUIRES_QUALIFICATION`.

Recommended wording for human use (not applied):

> The executable base was commit 238409835ef55358a10bbc3459dfa9aaa91ad5e5. Formal routes used documented, human-approved execution worktrees/overlays where required. No unapproved scientific source change or finalized-result contradiction has been proven. The present local checkout is dirty and must not be described as a clean working tree.

## 15. Findings

### F-DW-001 — MAJOR — repository-state/documentation qualification

- Affected artifact: current local locked checkout and final closure wording.
- Expected: distinguish locked commit identity, current checkout cleanliness, and approved execution overlays.
- Observed: HEAD matches, but the checkout has five tracked changes; closure documents say “Locked upstream was not modified” without this distinction.
- Evidence: current Git status; `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\FINAL_CLOSURE_REPORT_FINAL.md`.
- Scientific impact: no result contradiction proven; governance wording is materially overbroad.
- Recommended human action: qualify historical wording and later restore/create a clean checkout only under separate authorization.
- Auto-fixed: false.

### F-DW-002 — MAJOR — incomplete per-run source hashing

- Affected runs: PTB-XL(all) ST-MEM Frozen/Linear, PTB-XL(all) ECGFM-KED Frozen/Linear, and other shared `main_lite.py` routes without launch-time file hashes.
- Expected: exact commit plus source/overlay identity for every formal route.
- Observed: commands and formal artifacts are retained, but several direct-upstream routes lack byte-level launch source hashes for the relevant hunks.
- Evidence: corresponding `formal_execution_metadata.json`, exact commands, model-specific provenance files, and restore plan.
- Scientific impact: limits proof of exact implementation identity; it is not evidence of artifact corruption or wrong AUROC.
- Recommended human action: preserve this limitation and adjudicate whether existing command, behavior, checkpoint, and artifact evidence is sufficient for mentor handoff.
- Auto-fixed: false.

### F-DW-003 — MINOR — unknown SVG deletion provenance

- Affected artifact: `abstract.svg`.
- Expected: tracked repository assets remain present or have documented local disposition.
- Observed: file is deleted and no deletion provenance was located.
- Evidence: Git status and project-local `abstract.svg` search.
- Scientific impact: none; non-executable illustration.
- Recommended human action: decide separately whether to restore it during a later authorized repository-cleanup stage.
- Auto-fixed: false.

## 16. Final Verdict

```text
CURRENT_LOCAL_LOCKED_REPO_DIRTY=YES
FORMAL_EXECUTION_USED_CURRENT_DIRTY_WORKTREE=NOT_PROVEN
FORMAL_EXECUTION_USED_EQUIVALENT_MODIFIED_CODE=YES_DOCUMENTED_ACCEPTED
FORMAL_SCIENTIFIC_RESULT_IMPACT=DOCUMENTED_ACCEPTED_EXECUTION_REMEDIATION_ONLY
SCIENTIFIC_ARTIFACT_RECOMPUTATION_REQUIRED=NO
NEW_SCIENTIFIC_RESULT_CONTRADICTION_FOUND=NO
```

The dirty local checkout is a real repository-integrity/documentation issue, but the available provenance does not convert it into a formal scientific-result failure. The approved remediations must be disclosed as worktree/overlay changes based on the locked commit, rather than described by the absolute phrase “locked upstream unmodified.”

## 17. Recommended Human Remediation

1. Do not modify this repository until a separate remediation stage is authorized.
2. Qualify closure language using the wording above.
3. Preserve the three model-specific provenance chains and their patch hashes.
4. Record the per-run source-hash gap for direct-upstream formal routes as a provenance limitation.
5. If a later GitHub handoff is approved, prepare it from a separately verified clean locked checkout plus explicitly packaged overlays; do not silently normalize the present checkout.
6. No training, inference, preprocessing, mapping, aggregation, or Bootstrap rerun is recommended by this forensic evidence.
