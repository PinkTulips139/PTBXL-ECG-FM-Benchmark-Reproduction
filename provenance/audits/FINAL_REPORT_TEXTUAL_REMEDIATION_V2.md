# FINAL REPORT TEXTUAL REMEDIATION V2

Generated: 2026-08-29T00:00:29.9530770+08:00

## 1. Executive Summary

`REPORT_REMEDIATION_STATUS=PASS`.

The legacy OLE source report at `D:\桌面文件\ECG\Final Report.doc` was opened through Microsoft Word COM with macro execution disabled, link updating disabled, and `ReadOnly=True`. It was not saved or modified. Targeted textual and structural remediation was saved as the new Word Open XML document `D:\桌面文件\ECG\Final Report_V2.docx`.

The remediated report covers all nine required logical sections, preserves the 14 source tables, contains no comments or tracked changes, and passed finalized-evidence numeric checks. No scientific artifact or result value was changed, and no scientific recomputation is required.

## 2. Source and Output Integrity

| Item | Value |
|---|---|
| Source format | Legacy OLE DOC |
| Source size | 215,040 bytes |
| Source SHA256 | `A7489A668D4036CA19AEB559A22C47E0382C79B3B090C344D316F245A8EF53C7` |
| Source mtime before/after | `2026-08-23T02:55:43.7920000+08:00` |
| Source unchanged | YES |
| Output format | Word Open XML DOCX |
| Output size | 44,707 bytes |
| Output SHA256 | `CF2BBB5FB0F1236154B9559F0440640FD3BA79E1CC55D7E3795CDBB589851BFE` |
| Output pages | 14 |
| Output paragraphs | 779 |
| Output tables | 14 |
| Output comments | 0 |
| Output revisions | 0 |

The source contained 14 tables and no inline or floating images; the output retains 14 tables and therefore has no image-loss finding.

## 3. Structural Remediation

The report now explicitly and sequentially covers:

1. Benchmark / Task
2. Official Experimental Protocol
3. Reproduction Setup
4. Results
5. Paper vs Ours Difference Analysis
6. Implementation Challenges and Scientific Preservation
7. Prediction-Level Evidence and Reproducibility Validation
8. Limitations
9. Takeaway

A Model Overview was added for the eight Foundation Models and the two supervised baselines. It states that S4 and Net1D participate only in Finetuning and that Finetuning, Frozen, and Linear branch independently from the original pretrained checkpoint. The matrix is stated as 30 + 24 + 24 = 78 formal experiments, with PTB-XL label spaces of 71, 23, and 5 outputs over the same signals, split, and 2,198 test ECGs.

The original correct largest-difference table was preserved as Section 5.4. Inherited Word list numbering was removed from inserted prose; real bullets were retained only for the five Bootstrap provenance-blocker run IDs.

## 4. Scientific Claim and Wording Remediation

### Locked-source qualification

The unqualified claim that upstream was unmodified was replaced by the bounded conclusions from `LOCKED_UPSTREAM_EXECUTION_QUALIFICATION_V1.md`:

- executable authority is pinned to commit `238409835ef55358a10bbc3459dfa9aaa91ad5e5`;
- the current Windows working tree contains four tracked Python modifications and one tracked deletion and is not clean;
- formal use of that current dirty Windows working tree was not proven;
- equivalent formal-execution changes have documented accepted compatibility-remediation provenance;
- no unapproved formal-execution modification or new scientific-result contradiction was proven;
- no retraining, reinference, remapping, or re-bootstrap is required.

### ST-MEM causal boundary

The Results section no longer implies that dependency or runtime history explains the ST-MEM Finetuning deviations. It now states that execution compatibility was restored and clean `RETRY_03` runs superseded earlier failed attempts, while the deviation remains without a proven root cause.

### Closure and evidence wording

The report now states:

- formal experiments: 78/78;
- strict mapping: 77 PASS, 1 historical blocker, 0 missing;
- Bootstrap: 72 complete, 5 provenance-blocked, 0 failed, 1 mapping-not-eligible;
- emergency workers: 22/22 scientific bundles, 22/22 strict mappings, and 88/88 SHA256 pairs PASS;
- best-checkpoint references: 78/78 recovered;
- best epoch: 50 recovered / 28 not recovered;
- runtime: 15 recovered / 63 not recovered;
- local checkpoint binaries: 10 available / 68 not locally retained / 0 unproven.

The ECGFounder Frozen(all) historical blocker is described without being relabeled as PASS or failure. The five Bootstrap blockers are described as provenance blockers, not model, mapping, prediction, or Bootstrap-computation failures. The 65/72 CI observation is explicitly bounded as descriptive consistency evidence rather than an equivalence test.

## 5. Accepted Remediation Coverage

All nine topics from `ACCEPTED_EXECUTION_REMEDIATIONS_FINAL_V1.md` are represented:

1. ST-MEM dependency closure and clean `RETRY_03` supersession;
2. ECG-CPC PyKeOps/NVRTC/CUDA/FP32/path-shim route;
3. ECG-FM Python 3.9 compatibility overlay and versions;
4. ECG-JEPA identity aggregation adjudication;
5. MERL/ECGFM-KED execution-only BN guard, without outlier causation;
6. 052 historical authority to 451 clone/evidence carrier;
7. 573/871 predecessor to 780/775 successor evidence;
8. emergency-worker evidence recovery;
9. minimal scientific evidence bundle strategy.

`ACCEPTED_REMEDIATION_COVERAGE=PASS`.

## 6. Numeric Consistency Audit

Authorities:

- `D:\桌面文件\ECG\tables\FINAL_TABLE3_FINETUNING.csv`
- `D:\桌面文件\ECG\tables\FINAL_TABLE4_FROZEN.csv`
- `D:\桌面文件\ECG\tables\FINAL_TABLE5_LINEAR.csv`
- `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\FINAL_BOOTSTRAP_SUMMARY.csv`
- `D:\桌面文件\ECG\execution_control\PTBXL_FINAL_CLOSURE\FINAL_TRAINING_METADATA_RECOVERY.csv`

Checks performed:

- overall count/statistics/distribution: PASS;
- Finetuning/Frozen/Linear counts, means, medians, maxima, and threshold counts: PASS;
- all/sub/super counts, means, medians, and maxima: PASS;
- 12 model × granularity × mode rows in the largest-difference table: paper, ours, and difference all PASS at displayed six-decimal precision;
- 7 model × granularity × mode rows in the CI table: paper, ours, CI low, and CI high all PASS at displayed six-decimal precision;
- ECGFounder stability, ST-MEM Finetuning values, ECGFM-KED outliers, ECG-CPC Linear(all), ECG-FM Linear all/sub, and 8/9 panel-top observation: PASS;
- closure counts and 65/72 descriptive CI observation: PASS.

`NUMERIC_CONSISTENCY=PASS`.

## 7. Cleanliness and Visual QA

OOXML ZIP integrity and `word/document.xml` presence passed. Structural inspection found 0 comments, 0 tracked insertions, 0 tracked deletions, and 0 unresolved placeholder terms (`TODO`, `FIXME`, `TBD`, `TBC`, `UNKNOWN`, `待补`, `待确认`, `placeholder`, `lorem ipsum`).

The packaged `render_docx.py` could not start because its preinstalled environment lacked `pdf2image`; no dependency was installed. A Word-native PDF export plus the already available PyMuPDF rasterizer was used as the non-project temporary fallback. All 14 page PNGs were inspected at full resolution. No clipping, overlap, broken table, missing glyph, header/footer defect, or anomalous blank page was found. Temporary render assets were not included in the project deliverables.

`OUTPUT_REPORT_VALID=YES` and `REPORT_STRUCTURE_COMPLETE=YES`.

## 8. Preservation Verification

The three final table hashes before and after remediation are unchanged:

- Table 3: `063C3BCB747731F66682E74466CFD82DEBD61106BCF0FA45CB6A478DA8E8B8A3`
- Table 4: `FB2C8F84FC1543EC3ADD0911CEDF253761B103149DAC73796D3F63F103988F5C`
- Table 5: `D213E99E5BDBD0F4BFE40B71CCBF20724237B22EDCD5E6930DC4AD143154DAE5`

Locked repository HEAD remains `238409835ef55358a10bbc3459dfa9aaa91ad5e5`, and status remains exactly:

- ` D abstract.svg`
- ` M code/clinical_ts/models/ecg_foundation_models/ecg_fm_config.py`
- ` M code/clinical_ts/models/fm_ecg.py`
- ` M code/main_lite.py`
- ` M code/main_lite_ecg.py`

Therefore:

- `ORIGINAL_REPORT_UNCHANGED=YES`
- `FINAL_TABLES_UNCHANGED=YES`
- `LOCKED_WORKTREE_CHANGED_BY_REPORT_REMEDIATION=NO`
- `SCIENTIFIC_ARTIFACT_RECOMPUTATION_REQUIRED=NO`

## 9. Final Verdict

`REPORT_REMEDIATION_STATUS=PASS`.

Unsupported causal attribution count is 0. TODO/placeholder count is 0. The new report is mentor-ready for the separately authorized final handoff re-audit.

`NEXT_STAGE_RECOMMENDATION=FINAL_HANDOFF_REAUDIT`  
`NEXT_STAGE_AUTHORIZED=NO`  
`GITHUB_HANDOFF_ALLOWED_NOW=NO`
