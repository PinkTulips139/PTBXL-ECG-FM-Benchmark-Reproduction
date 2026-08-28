# LOCKED UPSTREAM EXECUTION QUALIFICATION V1

Generated: 2026-08-28T11:12:50.198Z

## 1. Purpose

This additive qualification replaces no historical file. It separates three propositions that were previously compressed into the unqualified phrase “locked upstream unmodified”:

1. the commit identity pinned for the benchmark;
2. the cleanliness of the current local Windows checkout; and
3. whether formal execution is proven to have used an unauthorized source modification.

Authority: `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\LOCKED_UPSTREAM_DIRTY_WORKTREE_FORENSIC_AUDIT.md` and its JSON companion.

## 2. Commit identity

- Locked repository: `D:\桌面文件\ECG\upstream\ecg-fm-benchmarking`
- Expected commit: `238409835ef55358a10bbc3459dfa9aaa91ad5e5`
- Observed HEAD: `238409835ef55358a10bbc3459dfa9aaa91ad5e5`
- `LOCKED_COMMIT_IDENTITY_VERIFIED=YES`

The commit is pinned and the observed HEAD matches it.

## 3. Current Windows working tree

The current checkout is not clean:

- tracked modified: `code/clinical_ts/models/ecg_foundation_models/ecg_fm_config.py`
- tracked modified: `code/clinical_ts/models/fm_ecg.py`
- tracked modified: `code/main_lite.py`
- tracked modified: `code/main_lite_ecg.py`
- tracked deleted: `abstract.svg`
- staged: 0
- untracked: 0

Therefore `CURRENT_LOCAL_LOCKED_WORKTREE_CLEAN=NO`. This is a statement about the present Windows working tree, not by itself a statement about formal execution.

## 4. Formal execution provenance

The forensic audit supports the following qualified conclusions:

- `FORMAL_EXECUTION_USED_CURRENT_DIRTY_WORKTREE=NOT_PROVEN`
- `FORMAL_EXECUTION_USED_EQUIVALENT_MODIFIED_CODE=YES_DOCUMENTED_ACCEPTED`
- `FORMAL_EXECUTION_UNAPPROVED_UPSTREAM_MODIFICATION_PROVEN=NO`
- `FORMAL_EXECUTION_ACCEPTED_REMEDIATION_USED=YES`
- `FORMAL_SCIENTIFIC_RESULT_IMPACT=DOCUMENTED_ACCEPTED_EXECUTION_REMEDIATION_ONLY`
- `SCIENTIFIC_RESULT_RECOMPUTATION_REQUIRED=NO`
- `NEW_SCIENTIFIC_RESULT_CONTRADICTION_FOUND=NO`

Formal commands point to Linux worktrees or compatibility overlays under `/root/autodl-tmp/ECG/...`, not to the Windows checkout. Exact or equivalent accepted remediation provenance is retained for ECG-FM, ST-MEM, and ECGFM-KED. Several direct-upstream routes have a documented byte-level launch-source-hash limitation, but no unapproved scientific source change or result contradiction is proven.

Evidence includes:

- `D:\桌面文件\ECG\experiments\ptbxl_all\ecg_fm\remote_artifacts\ecg_fm_ptbxl_all_formal_20260817T104823Z\evidence\approved_source_diff.patch`
- `D:\桌面文件\ECG\audits\st_mem\STMEM_A_E_REMEDIATION_PREFLIGHT_AUDIT.md`
- `D:\桌面文件\ECG\audits\ecgfm_ked\ECGFM_KED_LOADER_REMEDIATION_PROVENANCE.md`
- `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\mapping_evidence\instance_451`
- `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\LOCKED_UPSTREAM_DIRTY_WORKTREE_FORENSIC_AUDIT.json`

## 5. Required future wording

Use the following bounded statements together:

- `LOCKED_COMMIT_IDENTITY_VERIFIED=YES`
- `CURRENT_LOCAL_LOCKED_WORKTREE_CLEAN=NO`
- `FORMAL_EXECUTION_UNAPPROVED_UPSTREAM_MODIFICATION_PROVEN=NO`
- `FORMAL_EXECUTION_ACCEPTED_REMEDIATION_USED=YES`
- `SCIENTIFIC_RESULT_RECOMPUTATION_REQUIRED=NO`

Do not use `LOCKED_UPSTREAM_MODIFIED=NO` as a standalone project-wide statement.

## 6. GitHub source handoff policy

A future private GitHub handoff must not copy the current dirty working tree as canonical upstream source. Canonical source must be exported from exact commit `238409835ef55358a10bbc3459dfa9aaa91ad5e5`, preferably with `git archive` or an equivalent read-only exact-commit export. No export was performed in this stage.

Accepted execution remediations must be packaged separately under clearly named locations such as:

- `execution_overlays/`
- `patches/`
- `compatibility_notes/`
- provenance documentation

Modified files must not be merged into the locked source tree and then described as pristine upstream. Before any future staging, verify both the exported commit identity and the separation of overlay assets.

## 7. Decision

`LOCKED_UPSTREAM_QUALIFICATION=COMPLETE`

This qualification changes documentation and packaging policy only. No scientific artifact, result value, historical evidence, or repository file was modified.
