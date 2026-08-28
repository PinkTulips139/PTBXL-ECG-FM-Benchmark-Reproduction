"""Record read-only strict-mapping evidence acquisition state.

This script never contacts a host, copies a file, runs inference, or changes a
scientific artifact.  It converts the current canonical matrix and recovery
inventory plus separately observed SSH reachability outcomes into a durable
per-run acquisition manifest.
"""
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "tables"
RECOVERY = TABLES / "PTBXL_GLOBAL_MAPPING_EVIDENCE_RECOVERY.csv"
MATRIX = TABLES / "PTBXL_GLOBAL_FORMAL_RUN_COMPLETION_MATRIX.csv"
CLOSURE = ROOT / "execution_control" / "PTBXL_FINAL_CLOSURE"
OUT = CLOSURE / "MAPPING_EVIDENCE_ACQUISITION_MANIFEST.csv"
JSON_OUT = CLOSURE / "MAPPING_EVIDENCE_ACQUISITION_MANIFEST.json"
FINAL_MANIFEST = CLOSURE / "FINAL_CLOSURE_STATUS_MANIFEST.json"

FIELDS = [
    "dataset", "model", "mode", "canonical_run", "classification_before",
    "source_authority", "source_instance_or_worker", "source_path", "local_path",
    "artifact_types_recovered", "remote_connectivity", "acquisition_time_utc",
    "acquisition_method", "remote_sha256", "local_sha256", "file_size_bytes",
    "hash_verification", "mapping_after", "blocker_after", "user_power_on_required",
    "notes",
]


def load(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    recovery = load(RECOVERY)
    matrix = {r["canonical_run_id_or_directory"]: r for r in load(MATRIX)}
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    rows = []
    unreachable_runs = {
        "PTBXL_SUB_07_ST_MEM_FINETUNING_FORMAL_RETRY_03": "780",
        "PTBXL_SUB_08_ST_MEM_FROZEN_FORMAL": "780",
        "PTBXL_SUB_09_ST_MEM_LINEAR_FORMAL": "780",
        "PTBXL_SUPER_07_ST_MEM_FINETUNING_FORMAL_RETRY_03": "775",
        "PTBXL_SUPER_08_ST_MEM_FROZEN_FORMAL": "775",
        "PTBXL_SUPER_09_ST_MEM_LINEAR_FORMAL": "775",
    }
    for r in recovery:
        rid = r["canonical_run"]
        m = matrix[rid]
        source_path = m["prediction_artifact"]
        instance = ""
        connectivity = "NOT_APPLICABLE"
        power = "NO"
        notes = r["notes"]
        if rid in unreachable_runs:
            instance = unreachable_runs[rid]
            connectivity = "REMOTE_HOST_UNREACHABLE"
            power = "YES"
            notes += " Read-only SSH on 2026-08-22 to the recorded instance endpoint returned 'banner exchange: Connection refused'; no retry, copy, or remote mutation was performed."
        elif r["blocker_category"] == "ARCHIVED_WORKER_ARTIFACT_EXPECTED":
            instance = "EMERGENCY_WORKER_IDENTITY_RECOVERED"
            connectivity = "LOCAL_ARCHIVE_NOT_PRESENT"
        elif r["blocker_category"] == "REMOTE_COPY_NOT_YET_ARCHIVED":
            instance = "SOURCE_INSTANCE_ENDPOINT_NOT_RECOVERED"
            connectivity = "NOT_ATTEMPTED_ENDPOINT_UNAVAILABLE_IN_LOCAL_PROVENANCE"
        elif r["blocker_category"] == "LOCAL_PATH_NOT_YET_LOCATED":
            instance = "LOCAL_SPECIAL_ROUTE"
            connectivity = "LOCAL_PATH_NOT_LOCATED"
        elif r["mapping_result"] == "PASS":
            connectivity = "PREEXISTING_LOCAL_PASS"
        elif r["mapping_result"] == "BLOCKED":
            connectivity = "HISTORICAL_SIDECAR_ONLY"

        rows.append({
            "dataset": r["dataset"], "model": r["model"], "mode": r["mode"],
            "canonical_run": rid, "classification_before": r["blocker_category"],
            "source_authority": m["execution_authority"],
            "source_instance_or_worker": instance, "source_path": source_path,
            "local_path": "", "artifact_types_recovered": "NONE",
            "remote_connectivity": connectivity, "acquisition_time_utc": now,
            "acquisition_method": "READ_ONLY_INVENTORY_AND_REACHABILITY_CHECK",
            "remote_sha256": "", "local_sha256": "", "file_size_bytes": "",
            "hash_verification": "NOT_APPLICABLE_NO_NEW_FILE", "mapping_after": r["mapping_result"],
            "blocker_after": r["blocker_category"], "user_power_on_required": power,
            "notes": notes,
        })

    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader(); w.writerows(rows)
    summary = {
        "phase": "MAPPING_EVIDENCE_ACQUISITION_AND_CLOSURE",
        "generated_utc": now,
        "acquisition_policy": "read-only; no training, inference, rerun, or remote mutation",
        "rows": len(rows),
        "new_evidence_files_copied": 0,
        "local_path_recovered": 0,
        "worker_archive_recovered": 0,
        "remote_copy_recovered": 0,
        "remote_host_unreachable_count": sum(x["remote_connectivity"] == "REMOTE_HOST_UNREACHABLE" for x in rows),
        "user_power_on_required_count": sum(x["user_power_on_required"] == "YES" for x in rows),
        "unreachable_instances": ["780", "775"],
        "manifest_csv": str(OUT.relative_to(ROOT)).replace("\\", "/"),
    }
    JSON_OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    final = json.loads(FINAL_MANIFEST.read_text(encoding="utf-8"))
    final["mapping_evidence_acquisition"] = summary
    final["mapping_evidence_acquisition_manifest"] = str(OUT.relative_to(ROOT)).replace("\\", "/")
    FINAL_MANIFEST.write_text(json.dumps(final, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
