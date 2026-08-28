"""Targeted, read-only mapping-evidence inventory; never runs model inference."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "tables"
MATRIX = TABLES / "PTBXL_GLOBAL_FORMAL_RUN_COMPLETION_MATRIX.csv"
OUT = TABLES / "PTBXL_GLOBAL_MAPPING_EVIDENCE_RECOVERY.csv"
STATUS = TABLES / "PTBXL_GLOBAL_MAPPING_CLOSURE_STATUS.csv"
MANIFEST = ROOT / "execution_control" / "PTBXL_FINAL_CLOSURE" / "FINAL_CLOSURE_STATUS_MANIFEST.json"

FIELDS = [
    "dataset", "model", "mode", "canonical_run", "previous_mapping_status", "evidence_source",
    "raw_prediction_status", "target_status", "aggregate_status", "ecg_id_metadata_status",
    "mapping_result", "unique_test_ecg_ids", "aggregation_reconstruction", "target_consistency",
    "saved_aggregate_match", "blocker_category", "notes",
]


def load_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def worker_row(row):
    return row["execution_authority"] == "EMERGENCY_WORKERS"


def record(row):
    previous = row["ecg_id_mapping_status"]
    dataset, model, mode = row["dataset"], row["model"], row["mode"]
    rid = row["canonical_run_id_or_directory"]
    common = {
        "dataset": dataset, "model": model, "mode": mode, "canonical_run": rid,
        "previous_mapping_status": previous,
    }
    if previous == "PASS":
        common.update({
            "evidence_source": "tables/PTBXL_ALL_MAPPING_RECOVERY_ADDENDUM.json; audits/ecg_id_mapping_recovery/mapping_recovery_verification.json; preserved mapping CSV",
            "raw_prediction_status": "PRESERVED_AND_PREVIOUSLY_VERIFIED", "target_status": "PRESERVED_AND_PREVIOUSLY_VERIFIED",
            "aggregate_status": "PRESERVED_AND_PREVIOUSLY_VERIFIED", "ecg_id_metadata_status": "PASS",
            "mapping_result": "PASS", "unique_test_ecg_ids": "2198", "aggregation_reconstruction": "PASS",
            "target_consistency": "PASS", "saved_aggregate_match": "PASS", "blocker_category": "",
            "notes": "Existing PASS read only; not recomputed in this closure pass.",
        })
    elif previous == "BLOCKED":
        common.update({
            "evidence_source": "docs/PTBXL_ALL_FROZEN_LINEAR_FINAL_CLOSURE_REPORT.md (ECGFounder Frozen Run 1 preserved sidecar)",
            "raw_prediction_status": "ARCHIVED_REFERENCE_ONLY", "target_status": "ARCHIVED_REFERENCE_ONLY",
            "aggregate_status": "ARCHIVED_REFERENCE_ONLY", "ecg_id_metadata_status": "SIDE_CAR_REFERENCED",
            "mapping_result": "BLOCKED", "unique_test_ecg_ids": "2198", "aggregation_reconstruction": "PASS",
            "target_consistency": "FAIL", "saved_aggregate_match": "PASS", "blocker_category": "ORDERING_NOT_PROVEN",
            "notes": "Preserved sidecar reports TARGET_GROUP_CONSISTENCY=False. No local raw bundle was recovered; no new discrepancy inferred.",
        })
    elif dataset == "ptbxl_all":
        common.update({
            "evidence_source": "docs/PTBXL_ALL_FROZEN_LINEAR_FINAL_CLOSURE_REPORT.md; archived 052 formal-run provenance",
            "raw_prediction_status": "ARCHIVED_REFERENCE_ONLY", "target_status": "ARCHIVED_REFERENCE_ONLY",
            "aggregate_status": "ARCHIVED_REFERENCE_ONLY", "ecg_id_metadata_status": "CANONICAL_ALL_MAP_AVAILABLE",
            "mapping_result": "DEFERRED", "unique_test_ecg_ids": "UNVERIFIED", "aggregation_reconstruction": "UNVERIFIED",
            "target_consistency": "UNVERIFIED", "saved_aggregate_match": "UNVERIFIED", "blocker_category": "REMOTE_COPY_NOT_YET_ARCHIVED",
            "notes": "Completion is authority-confirmed; local raw/target/aggregate bundle for this mode was not located in the targeted recovery scope.",
        })
    elif worker_row(row):
        common.update({
            "evidence_source": "tables/emergency_workers/*_FORMAL_COMMAND_MATRIX.csv",
            "raw_prediction_status": "NOT_LOCATED_LOCAL", "target_status": "NOT_LOCATED_LOCAL",
            "aggregate_status": "NOT_LOCATED_LOCAL", "ecg_id_metadata_status": "CANONICAL_DATASET_METADATA_AVAILABLE",
            "mapping_result": "MISSING_EVIDENCE", "unique_test_ecg_ids": "UNVERIFIED", "aggregation_reconstruction": "UNVERIFIED",
            "target_consistency": "UNVERIFIED", "saved_aggregate_match": "UNVERIFIED", "blocker_category": "ARCHIVED_WORKER_ARTIFACT_EXPECTED",
            "notes": "Exact worker run identity recovered from preserved command matrix; its prediction/target delivery bundle is not present locally.",
        })
    else:
        cat = "LOCAL_PATH_NOT_YET_LOCATED" if "CANONICAL_RUN_ID_PENDING" in rid else "REMOTE_COPY_NOT_YET_ARCHIVED"
        common.update({
            "evidence_source": "successor controller state/command matrix/current human completion authority",
            "raw_prediction_status": "NOT_LOCATED_LOCAL", "target_status": "NOT_LOCATED_LOCAL",
            "aggregate_status": "NOT_LOCATED_LOCAL", "ecg_id_metadata_status": "CANONICAL_DATASET_METADATA_AVAILABLE",
            "mapping_result": "MISSING_EVIDENCE", "unique_test_ecg_ids": "UNVERIFIED", "aggregation_reconstruction": "UNVERIFIED",
            "target_consistency": "UNVERIFIED", "saved_aggregate_match": "UNVERIFIED", "blocker_category": cat,
            "notes": "No local raw prediction/target/aggregate bundle found in the targeted canonical-run recovery scope.",
        })
    return common


def write(path, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader(); w.writerows(rows)


def main():
    rows = [record(row) for row in load_csv(MATRIX)]
    write(OUT, rows)
    write(STATUS, rows)
    counts = {
        "mapping_total": len(rows), "mapping_already_pass_before": 11,
        "mapping_newly_closed_this_run": 0, "mapping_pass_total": sum(r["mapping_result"] == "PASS" for r in rows),
        "mapping_deferred_remaining": sum(r["mapping_result"] == "DEFERRED" for r in rows),
        "mapping_blocked_remaining": sum(r["mapping_result"] == "BLOCKED" for r in rows),
        "mapping_missing_evidence_remaining": sum(r["mapping_result"] == "MISSING_EVIDENCE" for r in rows),
        "evidence_recovered_count": 0, "canonical_worker_identity_recovered_count": sum(worker_row(row) for row in load_csv(MATRIX)),
        "bootstrap_eligible_run_count": sum(r["mapping_result"] == "PASS" for r in rows),
    }
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["mapping_evidence_recovery"] = counts
    manifest["cpu_bootstrap_closure_ready"] = False
    manifest["cpu_bootstrap_closure_reason"] = "Strict mapping is not PASS for all 78 formal entries."
    manifest["mapping_evidence_recovery_csv"] = str(OUT.relative_to(ROOT)).replace("\\", "/")
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
