"""Deterministic final-delivery normalization; no scientific recomputation."""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "tables"
CLOSURE = ROOT / "execution_control" / "PTBXL_FINAL_CLOSURE"
LOCKED_COMMIT = "238409835ef55358a10bbc3459dfa9aaa91ad5e5"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise RuntimeError(f"refusing to write empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_row(source: dict[str, str]) -> dict[str, str]:
    paper = source["paper_macro_auroc"]
    notes = ""
    try:
        float(paper)
    except (TypeError, ValueError):
        paper = "NOT_REPORTED / NA"
        notes = "No corresponding verified paper value was located in the existing local paper extract; no value was inferred."
    mapping = source["mapping_status"]
    prediction_status = (
        "AVAILABLE_STRICT_MAPPING_PASS"
        if mapping == "PASS"
        else "AVAILABLE_HISTORICAL_MAPPING_BLOCKED"
    )
    return {
        "dataset": source["dataset"],
        "model": source["model"],
        "mode": source["mode"],
        "paper_macro_auroc": paper,
        "ours_macro_auroc": source["ours_macro_auroc"],
        "difference": source["difference_ours_minus_paper"],
        "ci_low": source["ci95_low"],
        "ci_high": source["ci95_high"],
        "best_epoch": source["best_epoch"],
        "runtime": source["runtime"],
        "prediction_status": prediction_status,
        "ecg_id_mapping_status": mapping,
        "bootstrap_status": source["bootstrap_status"],
        "canonical_run": source["canonical_run"],
        "provenance_reference": source["provenance"],
        "notes": notes,
    }


def main() -> None:
    generated_utc = datetime.now(timezone.utc).isoformat()
    draft_sources = {
        "ptbxl_all": TABLES / "DRAFT_TABLE3_PTBXL_ALL.csv",
        "ptbxl_sub": TABLES / "DRAFT_TABLE4_PTBXL_SUB.csv",
        "ptbxl_super": TABLES / "DRAFT_TABLE5_PTBXL_SUPER.csv",
    }
    rows: list[dict[str, str]] = []
    for dataset, path in draft_sources.items():
        current = read_csv(path)
        if len(current) != 26 or {row["dataset"] for row in current} != {dataset}:
            raise RuntimeError(f"dataset draft validation failed: {path}")
        rows.extend(normalized_row(row) for row in current)

    if len(rows) != 78:
        raise RuntimeError(f"formal table row count is {len(rows)}, expected 78")

    dataset_outputs = {
        "ptbxl_all": TABLES / "PTBXL_ALL_FINAL_RESULTS.csv",
        "ptbxl_sub": TABLES / "PTBXL_SUB_FINAL_RESULTS.csv",
        "ptbxl_super": TABLES / "PTBXL_SUPER_FINAL_RESULTS.csv",
    }
    for dataset, path in dataset_outputs.items():
        write_csv(path, [row for row in rows if row["dataset"] == dataset])

    mode_outputs = {
        "Finetuning": TABLES / "FINAL_TABLE3_FINETUNING.csv",
        "Frozen": TABLES / "FINAL_TABLE4_FROZEN.csv",
        "Linear": TABLES / "FINAL_TABLE5_LINEAR.csv",
    }
    expected_mode_counts = {"Finetuning": 30, "Frozen": 24, "Linear": 24}
    for mode, path in mode_outputs.items():
        selected = [row for row in rows if row["mode"] == mode]
        if len(selected) != expected_mode_counts[mode]:
            raise RuntimeError(f"{mode} count is {len(selected)}, expected {expected_mode_counts[mode]}")
        if mode != "Finetuning" and any(row["model"] in {"S4", "Net1D"} for row in selected):
            raise RuntimeError(f"forbidden S4/Net1D {mode} row detected")
        write_csv(path, selected)

    mapping_status = read_csv(TABLES / "PTBXL_GLOBAL_MAPPING_CLOSURE_STATUS.csv")
    bootstrap = read_csv(CLOSURE / "FINAL_BOOTSTRAP_SUMMARY.csv")
    worker_evidence = read_csv(CLOSURE / "PARALLEL_WORKER_EVIDENCE_RECOVERY.csv")
    worker_hash = read_csv(CLOSURE / "PARALLEL_WORKER_HASH_CLOSURE.csv")
    worker_mapping = read_csv(CLOSURE / "PARALLEL_WORKER_STRICT_MAPPING_FINAL.csv")

    mapping_pass = sum(row["mapping_result"] == "PASS" for row in mapping_status)
    mapping_blocked = sum(row["mapping_result"] == "BLOCKED" for row in mapping_status)
    bootstrap_complete = sum(row["bootstrap_status"] == "COMPLETED" for row in bootstrap)
    bootstrap_blocked = sum("BLOCKED" in row["bootstrap_status"] for row in bootstrap)
    bootstrap_failed = sum(row["bootstrap_status"] == "FAILED" for row in bootstrap)
    hash_pass = sum(row.get("hash_match", "") == "PASS" for row in worker_hash)
    worker_mapping_pass = sum(row["mapping_status"] == "PASS" for row in worker_mapping)

    required_counts = {
        "mapping_pass": (mapping_pass, 77),
        "mapping_blocked": (mapping_blocked, 1),
        "bootstrap_complete": (bootstrap_complete, 72),
        "bootstrap_blocked": (bootstrap_blocked, 5),
        "bootstrap_failed": (bootstrap_failed, 0),
        "worker_evidence": (len(worker_evidence), 22),
        "worker_hash_pass": (hash_pass, 88),
        "worker_mapping_pass": (worker_mapping_pass, 22),
    }
    mismatches = {name: values for name, values in required_counts.items() if values[0] != values[1]}
    if mismatches:
        raise RuntimeError(f"canonical count mismatch: {mismatches}")

    report = f"""# ECG Foundation Model Benchmark Reproduction — Final Closure Report

## 1. Scope

This closure covers PTB-XL(all), PTB-XL(sub), and PTB-XL(super): 26 formal entries per dataset and 78 entries globally. All 78 formal runs are complete.

## 2. Locked executable authority

The executable reproduction authority is the locked official commit `{LOCKED_COMMIT}` under the approved decision `APPROVE_R1_LOCKED_OFFICIAL_GITHUB_AS_EXECUTABLE_REPRODUCTION_AUTHORITY`. Locked upstream was not modified.

## 3. Dataset and analysis contract

The canonical test set contains 2,198 ECG records. Expected output dimensions are 71 for all, 23 for sub, and 5 for super. Each dataset contains 10 Finetuning, 8 Frozen, and 8 Linear entries. S4 and Net1D occur only under Finetuning. Bootstrap uses record-level aggregated Macro AUROC, 1,000 iterations, 95% confidence intervals, and `clinical_ts.utils.bootstrap_utils.empirical_bootstrap` with its accepted sampling, RNG, invalid-resample, and percentile-CI behavior.

## 4. Formal-run completion

Formal completion is 78/78. Historical execution attempts remain provenance, but superseded attempts are not counted as final scientific failures.

## 5. Strict ECG-ID mapping closure

Strict mapping is PASS for 77 entries. `PTBXL_ALL_ECGFOUNDER_FROZEN_FORMAL_RUN_001` remains the sole historical blocker because its preserved sidecar records `TARGET_GROUP_CONSISTENCY=False`. That sidecar and its source artifacts remain unchanged.

## 6. Bootstrap closure

Bootstrap is COMPLETE for 72 entries and `BLOCKED_EXISTING_PROVENANCE` for five; zero entries failed and zero remain pending. No CI was inferred for blocked entries.

## 7. Accepted remediation and provenance

- Emergency workers: 22/22 minimum scientific bundles recovered, 88/88 remote-local SHA256 comparisons PASS, and 22/22 strict mappings PASS.
- ECG-JEPA: the six agg/noagg-identical artifacts were adjudicated as valid whole-record, single-test-segment identity aggregation; this has no final metric or bootstrap impact.
- ECG-FM: accepted Python 3.9/fairseq-signals compatibility-route provenance is retained, including execution-only TensorBoard remediation and successful Retry01 evidence for Run015.
- ST-MEM: historical resampy, sklearn, and safetensors dependency failures are preserved; successful Retry03 supersedes those attempts scientifically without deleting provenance.
- Historical source 052: recovered through the complete data-disk clone carried by 451; historical execution authority remains 052 where applicable.

## 8. Power state and remote-only evidence

The user confirmed through the AutoDL UI that all project-related remote instances are stopped. This is recorded as `HUMAN_AUTODL_UI_CONFIRMATION`, not as an SSH process probe. Current running remote instances: 0. Critical remote-only scientific artifacts remaining: 0.

## 9. Final tables

Dataset-complete summaries are `PTBXL_ALL_FINAL_RESULTS.csv`, `PTBXL_SUB_FINAL_RESULTS.csv`, and `PTBXL_SUPER_FINAL_RESULTS.csv`. Paper-aligned mode tables are `FINAL_TABLE3_FINETUNING.csv`, `FINAL_TABLE4_FROZEN.csv`, and `FINAL_TABLE5_LINEAR.csv`. Missing verified paper comparison values are explicitly `NOT_REPORTED / NA`; no values were inferred.

## 10. Documented limitations

1. One historical ECG-ID mapping blocker remains.
2. Five mapping-PASS runs remain bootstrap-blocked because their canonical local aggregate/target provenance is not uniquely locatable; CI fields remain blank.

Neither limitation is classified as a final scientific execution failure.

## 11. Final reproducibility statement

The formal completion matrix, run-level provenance, prediction/target evidence, strict mapping records, bootstrap summaries, final tables, and delivery hashes form the local reproducibility chain. This project is closed with documented limitations. Human authors remain responsible for scientific interpretation and external release approval.
"""
    (CLOSURE / "FINAL_CLOSURE_REPORT_FINAL.md").write_text(report, encoding="utf-8")

    handoff = f"""# Mentor Handoff Index — ECG Foundation Model Benchmark Reproduction

## Paper and authority

- Paper: *Benchmarking ECG FMs: A Reality Check Across Clinical Tasks*; consult the paper and Appendix alongside this index.
- Locked executable commit: `{LOCKED_COMMIT}`.
- Dataset contract: PTB-XL(all/sub/super), 2,198 test ECG records; output dimensions 71/23/5.

## End-to-end trace

`paper / Appendix` → locked commit → `tables/PTBXL_GLOBAL_FORMAL_RUN_COMPLETION_MATRIX.csv` canonical run → formal result/prediction/target references → `tables/PTBXL_GLOBAL_MAPPING_CLOSURE_STATUS.csv` → `FINAL_BOOTSTRAP_SUMMARY.csv` → final dataset and mode tables.

## Final tables

- Paper Table 3 semantics: `tables/FINAL_TABLE3_FINETUNING.csv` (3 datasets × 10 models = 30 entries).
- Paper Table 4 semantics: `tables/FINAL_TABLE4_FROZEN.csv` (3 datasets × 8 foundation models = 24 entries).
- Paper Table 5 semantics: `tables/FINAL_TABLE5_LINEAR.csv` (3 datasets × 8 foundation models = 24 entries).
- Dataset summaries: `tables/PTBXL_ALL_FINAL_RESULTS.csv`, `tables/PTBXL_SUB_FINAL_RESULTS.csv`, `tables/PTBXL_SUPER_FINAL_RESULTS.csv` (26 entries each).

## Canonical scientific records

- Completion matrix: `tables/PTBXL_GLOBAL_FORMAL_RUN_COMPLETION_MATRIX.csv`.
- Mapping closure: `tables/PTBXL_GLOBAL_MAPPING_CLOSURE_STATUS.csv` and `tables/PTBXL_GLOBAL_MAPPING_EVIDENCE_RECOVERY.csv`.
- Bootstrap: `FINAL_BOOTSTRAP_SUMMARY.csv/json`, `FINAL_CPU_BOOTSTRAP_77_RUNS.csv/json`, and `FINAL_CPU_BOOTSTRAP_MANIFEST.json`.
- Worker provenance: `PARALLEL_WORKER_EVIDENCE_RECOVERY.csv`, `PARALLEL_WORKER_HASH_CLOSURE.csv`, and `PARALLEL_WORKER_STRICT_MAPPING_FINAL.csv`.
- Accepted remediation: `ECG_JEPA_AGG_NOAGG_DISCREPANCY_ADJUDICATION.csv/json`, `RUN015_TARGETED_RECOVERY_AND_RELEASE_GATE.json`, `STMEM_780_775_STRICT_MAPPING_VERIFICATION.json`, and acquisition/controller manifests.
- Limitations: `BOOTSTRAP_BLOCKER_PROVENANCE_LIST.csv` plus the preserved ECGFounder Frozen mapping sidecar provenance.
- Final closure report: `FINAL_CLOSURE_REPORT_FINAL.md`.
- Delivery integrity: `FINAL_DELIVERY_MANIFEST.csv/json`.

## Human review gates

- Do not reinterpret the historical mapping blocker.
- Do not impute the five missing bootstrap confidence intervals.
- Paper comparison fields marked `NOT_REPORTED / NA` require source verification before replacement.
- External release and manuscript approval remain human decisions.
"""
    (CLOSURE / "MENTOR_HANDOFF_INDEX.md").write_text(handoff, encoding="utf-8")

    readiness = {
        "generated_utc": generated_utc,
        "release_readiness": "READY",
        "project_final_closure_status": "CLOSED_WITH_DOCUMENTED_LIMITATIONS",
        "locked_commit": LOCKED_COMMIT,
        "formal_runs_complete": "78/78",
        "mapping_pass": 77,
        "mapping_historical_blocked": 1,
        "bootstrap_complete": 72,
        "bootstrap_blocked_existing_provenance": 5,
        "bootstrap_failed": 0,
        "critical_remote_only_artifact_count_global": 0,
        "remote_power_state_confirmation_method": "HUMAN_AUTODL_UI_CONFIRMATION",
        "remote_power_state_note": "Human UI confirmation; not an SSH process inspection in this phase.",
        "remote_instances_currently_running": 0,
        "worker_evidence_recovered": "22/22",
        "worker_remote_local_sha256_match": "88/88 PASS",
        "worker_strict_mapping_pass": "22/22",
        "final_tables_created": True,
        "final_closure_report_finalized": True,
        "mentor_handoff_finalized": True,
        "minimal_local_footprint": True,
        "new_substantive_discrepancy": False,
        "active_gpu_training_started": False,
        "new_inference_started": False,
        "locked_upstream_modified": False,
        "scientific_semantics_changed": False,
    }
    readiness_path = CLOSURE / "FINAL_RELEASE_READINESS_MANIFEST.json"
    readiness_path.write_text(json.dumps(readiness, indent=2) + "\n", encoding="utf-8")

    closure_manifest_path = CLOSURE / "FINAL_CLOSURE_STATUS_MANIFEST.json"
    closure_manifest = json.loads(closure_manifest_path.read_text(encoding="utf-8"))
    closure_manifest["final_release_readiness"] = readiness
    closure_manifest_path.write_text(json.dumps(closure_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    deliverables = [
        ("final_table", TABLES / "FINAL_TABLE3_FINETUNING.csv", "Paper-aligned Finetuning results", "canonical normalized tables"),
        ("final_table", TABLES / "FINAL_TABLE4_FROZEN.csv", "Paper-aligned Frozen results", "canonical normalized tables"),
        ("final_table", TABLES / "FINAL_TABLE5_LINEAR.csv", "Paper-aligned Linear results", "canonical normalized tables"),
        ("dataset_summary", TABLES / "PTBXL_ALL_FINAL_RESULTS.csv", "PTB-XL(all) 26-entry summary", "canonical normalized tables"),
        ("dataset_summary", TABLES / "PTBXL_SUB_FINAL_RESULTS.csv", "PTB-XL(sub) 26-entry summary", "canonical normalized tables"),
        ("dataset_summary", TABLES / "PTBXL_SUPER_FINAL_RESULTS.csv", "PTB-XL(super) 26-entry summary", "canonical normalized tables"),
        ("completion_matrix", TABLES / "PTBXL_GLOBAL_FORMAL_RUN_COMPLETION_MATRIX.csv", "78-run completion authority", "formal completion closure"),
        ("mapping_status", TABLES / "PTBXL_GLOBAL_MAPPING_CLOSURE_STATUS.csv", "Strict ECG-ID mapping status", "mapping closure"),
        ("mapping_evidence", TABLES / "PTBXL_GLOBAL_MAPPING_EVIDENCE_RECOVERY.csv", "Mapping evidence provenance", "mapping closure"),
        ("bootstrap_summary", CLOSURE / "FINAL_BOOTSTRAP_SUMMARY.csv", "Canonical bootstrap summary", "accepted locked bootstrap helper"),
        ("bootstrap_summary", CLOSURE / "FINAL_BOOTSTRAP_SUMMARY.json", "Canonical bootstrap summary", "accepted locked bootstrap helper"),
        ("bootstrap_detail", CLOSURE / "FINAL_CPU_BOOTSTRAP_77_RUNS.csv", "77 eligible-run bootstrap state", "legacy 50 reuse plus 22 worker runs"),
        ("bootstrap_manifest", CLOSURE / "FINAL_CPU_BOOTSTRAP_MANIFEST.json", "Bootstrap contract and counts", "accepted locked bootstrap helper"),
        ("blocker_provenance", CLOSURE / "BOOTSTRAP_BLOCKER_PROVENANCE_LIST.csv", "Five preserved bootstrap blockers", "fail-closed closure"),
        ("worker_provenance", CLOSURE / "PARALLEL_WORKER_EVIDENCE_RECOVERY.csv", "22 worker bundles", "emergency-worker recovery"),
        ("worker_hash", CLOSURE / "PARALLEL_WORKER_HASH_CLOSURE.csv", "88 remote-local hash comparisons", "emergency-worker hash closure"),
        ("worker_mapping", CLOSURE / "PARALLEL_WORKER_STRICT_MAPPING_FINAL.csv", "22 worker strict mappings", "emergency-worker mapping closure"),
        ("adjudication", CLOSURE / "ECG_JEPA_AGG_NOAGG_DISCREPANCY_ADJUDICATION.json", "ECG-JEPA identity aggregation adjudication", "locked implementation adjudication"),
        ("special_route", CLOSURE / "RUN015_TARGETED_RECOVERY_AND_RELEASE_GATE.json", "ECG-FM special-route Run015 provenance", "052 historical source / 451 carrier"),
        ("stmem_provenance", CLOSURE / "STMEM_780_775_STRICT_MAPPING_VERIFICATION.json", "ST-MEM successful retry evidence", "780/775 successor evidence"),
        ("closure_report", CLOSURE / "FINAL_CLOSURE_REPORT_FINAL.md", "Final closure narrative", "global canonical closure"),
        ("mentor_handoff", CLOSURE / "MENTOR_HANDOFF_INDEX.md", "Mentor traceability index", "global canonical closure"),
        ("release_readiness", readiness_path, "Release-readiness decision record", "human AutoDL UI confirmation plus local evidence"),
        ("closure_manifest", closure_manifest_path, "Canonical closure status", "global canonical closure"),
    ]
    manifest_rows = []
    for artifact_type, path, purpose, authority in deliverables:
        if not path.is_file():
            raise RuntimeError(f"required delivery artifact missing: {path}")
        manifest_rows.append(
            {
                "artifact_type": artifact_type,
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "size": str(path.stat().st_size),
                "SHA256": sha256(path),
                "purpose": purpose,
                "authority/provenance": authority,
                "required_for_mentor_handoff": "YES",
            }
        )
    manifest_csv = CLOSURE / "FINAL_DELIVERY_MANIFEST.csv"
    write_csv(manifest_csv, manifest_rows)
    manifest_json = CLOSURE / "FINAL_DELIVERY_MANIFEST.json"
    manifest_json.write_text(
        json.dumps(
            {
                "generated_utc": generated_utc,
                "manifest_self_hash_policy": "The two manifest files are excluded from their own hash list to avoid self-referential hashes.",
                "artifact_count": len(manifest_rows),
                "artifacts": manifest_rows,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "dataset_table_counts": {dataset: 26 for dataset in dataset_outputs},
                "mode_table_counts": expected_mode_counts,
                "mapping_pass": mapping_pass,
                "mapping_blocked": mapping_blocked,
                "bootstrap_complete": bootstrap_complete,
                "bootstrap_blocked": bootstrap_blocked,
                "bootstrap_failed": bootstrap_failed,
                "critical_remote_only_artifact_count_global": 0,
                "delivery_artifact_count": len(manifest_rows),
                "release_readiness": "READY",
            }
        )
    )


if __name__ == "__main__":
    main()
