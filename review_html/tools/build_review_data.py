#!/usr/bin/env python3
"""Serialize packaged canonical NPZs into static, file://-safe review shards.

This tool performs representation-only derivation. It does not infer, aggregate,
map, bootstrap, threshold, normalize, calibrate, or reorder scientific data.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

import numpy as np


MODEL_ORDER = [
    "ECGFounder", "ECG-JEPA", "ST-MEM", "MERL", "ECGFM-KED",
    "HuBERT-ECG", "ECG-CPC", "ECG-FM", "S4", "Net1D",
]
GRANULARITY_ORDER = ["all", "sub", "super"]
MODE_ORDER = ["Finetuning", "Frozen", "Linear"]
OUTPUT_DIMS = {"all": 71, "sub": 23, "super": 5}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def json_compact(value) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def parse_shard(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    prefix = "window.ECGReviewRegisterRunData("
    suffix = ");\n"
    if not text.startswith(prefix) or not text.endswith(suffix):
        raise ValueError(f"Invalid shard wrapper: {path}")
    return json.loads(text[len(prefix):-len(suffix)])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staging-root", type=Path, required=True)
    parser.add_argument("--source-verification-csv", type=Path, required=True)
    args = parser.parse_args()
    root = args.staging_root.resolve()
    data_dir = root / "review_html" / "data"
    run_dir = data_dir / "runs"
    run_dir.mkdir(parents=True, exist_ok=True)

    availability_path = root / "sample_predictions" / "metadata" / "sample_availability.json"
    matrix_path = root / "results" / "FORMAL_RUN_COMPLETION_MATRIX.csv"
    mapping_path = root / "sample_predictions" / "metadata" / "test_prediction_index_mapping.csv"
    bootstrap_path = root / "results" / "BOOTSTRAP_SUMMARY.csv"
    canonical_map_path = root / "results" / "CANONICAL_RUN_ID_MAP.csv"

    availability = json.loads(availability_path.read_text(encoding="utf-8-sig"))
    availability_by_key = {row["canonical_experiment_key"]: row for row in availability["entries"]}
    matrix_rows = read_csv(matrix_path)
    if len(matrix_rows) != 78 or len(availability_by_key) != 78:
        raise ValueError("Expected exactly 78 matrix and availability entries")
    if set(availability_by_key) != {row["canonical_experiment_key"] for row in matrix_rows}:
        raise ValueError("Availability and completion-matrix canonical keys differ")

    mapping_rows = read_csv(mapping_path)
    mapping_rows.sort(key=lambda row: int(row["prediction_index"]))
    if [int(row["prediction_index"]) for row in mapping_rows] != list(range(len(mapping_rows))):
        raise ValueError("Prediction-index mapping is not contiguous from zero")
    ecg_ids = [str(row["ecg_id"]) for row in mapping_rows]
    if len(ecg_ids) != 2198 or len(set(ecg_ids)) != len(ecg_ids):
        raise ValueError("Approved ECG-ID mapping must contain 2,198 unique IDs")

    sort_key = lambda row: (
        MODEL_ORDER.index(row["model"]),
        GRANULARITY_ORDER.index(row["granularity"]),
        MODE_ORDER.index(row["mode"]),
    )
    matrix_rows.sort(key=sort_key)

    label_sets: dict[str, list[str]] = {}
    run_entries: list[dict] = []
    verification: list[dict] = []
    shard_paths: list[Path] = []

    common_refs = [
        matrix_path.relative_to(root).as_posix(),
        mapping_path.relative_to(root).as_posix(),
        bootstrap_path.relative_to(root).as_posix(),
        canonical_map_path.relative_to(root).as_posix(),
    ]

    for row in matrix_rows:
        key = row["canonical_experiment_key"]
        available = availability_by_key[key]
        granularity = row["granularity"]
        output_dim = OUTPUT_DIMS[granularity]
        base_entry = {
            "canonical_experiment_key": key,
            "formal_run_id": row["formal_run_id"],
            "model": row["model"],
            "granularity": granularity,
            "mode": row["mode"],
            "formal_complete": row["formal_complete"].strip().upper() == "YES",
            "ours_auroc": float(row["ours_auroc"]),
            "paper_auroc": float(row["paper_auroc"]),
            "difference": float(row["difference"]),
            "mapping_status": row["mapping_status"],
            "bootstrap_status": row["bootstrap_status"],
            "physical_sample_available": bool(available["physical_sample_available"]),
            "review_mode": available["review_mode"],
            "record_count": 2198 if available["physical_sample_available"] else None,
            "output_dim": output_dim,
            "source_sample_sha256": None,
            "data_shard_path": None,
            "provenance_references": common_refs,
            "packaging_note": available["note"],
        }

        if not available["physical_sample_available"]:
            verification.append({
                "canonical_experiment_key": key,
                "formal_run_id": row["formal_run_id"],
                "source_relative_path": "NOT_AVAILABLE",
                "source_sha256": "NOT_AVAILABLE",
                "source_record_count": "NOT_AVAILABLE",
                "source_shape": "NOT_AVAILABLE",
                "source_dtype": "NOT_AVAILABLE",
                "mapping_evidence_path": mapping_path.relative_to(root).as_posix(),
                "derived_data_path": "NOT_AVAILABLE",
                "derived_sha256": "NOT_AVAILABLE",
                "derived_record_count": "NOT_AVAILABLE",
                "output_dim": output_dim,
                "prediction_roundtrip_max_abs_diff": "NOT_APPLICABLE",
                "target_exact_match": "NOT_APPLICABLE",
                "ecg_id_exact_match": "NOT_APPLICABLE",
                "status": "NOT_PACKAGED_PHYSICAL_SOURCE_UNAVAILABLE",
            })
            run_entries.append(base_entry)
            continue

        if row["mapping_status"] != "PASS":
            raise ValueError(f"Available physical bundle lacks mapping PASS: {key}")
        source_rel = available["staged_record_level_path"]
        source_path = root / Path(source_rel)
        if not source_path.is_file():
            raise FileNotFoundError(source_path)

        with np.load(source_path, allow_pickle=True) as bundle:
            required = {"preds", "targs", "lbl_itos"}
            if not required.issubset(bundle.files):
                raise ValueError(f"Required arrays absent: {source_rel}")
            predictions = np.asarray(bundle["preds"])
            targets = np.asarray(bundle["targs"])
            labels = [str(value) for value in bundle["lbl_itos"].tolist()]
            if predictions.shape != (len(ecg_ids), output_dim) or targets.shape != predictions.shape:
                raise ValueError(f"Unexpected shape for {source_rel}: {predictions.shape}, {targets.shape}")
            if len(labels) != output_dim:
                raise ValueError(f"Unexpected label count for {source_rel}")
            if granularity in label_sets and label_sets[granularity] != labels:
                raise ValueError(f"Label order differs within {granularity}: {source_rel}")
            label_sets.setdefault(granularity, labels)

            source_digest = sha256(source_path)
            shard_rel = f"data/runs/{slug(row['model'])}__{granularity}__{slug(row['mode'])}.js"
            shard_path = root / "review_html" / Path(shard_rel)
            payload = {
                "schema_version": 1,
                "canonical_experiment_key": key,
                "formal_run_id": row["formal_run_id"],
                "granularity": granularity,
                "mode": row["mode"],
                "model": row["model"],
                "source_sample_sha256": source_digest,
                "mapping_status": row["mapping_status"],
                "record_count": int(predictions.shape[0]),
                "output_dim": int(predictions.shape[1]),
                "ecg_ids": ecg_ids,
                "predictions": predictions.tolist(),
                "targets": targets.tolist(),
            }
            shard_path.write_text(
                "window.ECGReviewRegisterRunData(" + json_compact(payload) + ");\n",
                encoding="utf-8",
                newline="\n",
            )
            shard_paths.append(shard_path)

            derived = parse_shard(shard_path)
            derived_predictions = np.asarray(derived["predictions"], dtype=predictions.dtype)
            derived_targets = np.asarray(derived["targets"], dtype=targets.dtype)
            derived_ids = [str(value) for value in derived["ecg_ids"]]
            if derived_predictions.shape != predictions.shape or derived_targets.shape != targets.shape:
                raise ValueError(f"Derived shape mismatch: {shard_rel}")
            pred_exact = np.array_equal(derived_predictions, predictions)
            target_exact = np.array_equal(derived_targets, targets)
            id_exact = derived_ids == ecg_ids
            max_abs = float(np.max(np.abs(derived_predictions.astype(np.float64) - predictions.astype(np.float64))))
            if not pred_exact or max_abs != 0.0 or not target_exact or not id_exact:
                raise ValueError(f"Lossless derivation failed: {key}")

        base_entry.update({
            "source_sample_sha256": source_digest,
            "data_shard_path": shard_rel,
        })
        run_entries.append(base_entry)
        verification.append({
            "canonical_experiment_key": key,
            "formal_run_id": row["formal_run_id"],
            "source_relative_path": source_rel,
            "source_sha256": source_digest,
            "source_record_count": int(predictions.shape[0]),
            "source_shape": f"{predictions.shape[0]}x{predictions.shape[1]}",
            "source_dtype": str(predictions.dtype),
            "mapping_evidence_path": mapping_path.relative_to(root).as_posix(),
            "derived_data_path": f"review_html/{shard_rel}",
            "derived_sha256": sha256(shard_path),
            "derived_record_count": int(derived_predictions.shape[0]),
            "output_dim": int(derived_predictions.shape[1]),
            "prediction_roundtrip_max_abs_diff": "0",
            "target_exact_match": "YES",
            "ecg_id_exact_match": "YES",
            "status": "PASS",
        })

    if {key: len(value) for key, value in label_sets.items()} != OUTPUT_DIMS:
        raise ValueError("Authoritative label sets are incomplete or have unexpected lengths")
    if sum(bool(row["physical_sample_available"]) for row in run_entries) != 76:
        raise ValueError("Expected 76 available physical runs")
    if len(shard_paths) != 76 or len(verification) != 78:
        raise ValueError("Expected 76 shards and 78 derivation-manifest rows")

    review_manifest = {
        "schema_version": 1,
        "project": "PTB-XL ECG Foundation Model Benchmark Reproduction",
        "purpose": "STATIC_INSPECTION_INTERFACE_NOT_NEW_EVALUATION_PIPELINE",
        "locked_commit": "238409835ef55358a10bbc3459dfa9aaa91ad5e5",
        "formal_experiment_entries": 78,
        "physical_sample_bundles": 76,
        "missing_sample_entries": 2,
        "test_record_count_per_available_run": 2198,
        "formal_evaluation_unit": "ECG_RECORD",
        "model_order": MODEL_ORDER,
        "granularity_order": GRANULARITY_ORDER,
        "mode_order": MODE_ORDER,
        "label_sets": label_sets,
        "runs": run_entries,
    }
    manifest_js = data_dir / "manifest.js"
    manifest_js.write_text("window.ECG_REVIEW_MANIFEST=" + json_compact(review_manifest) + ";\n", encoding="utf-8", newline="\n")

    fields = [
        "canonical_experiment_key", "formal_run_id", "source_relative_path", "source_sha256",
        "source_record_count", "source_shape", "source_dtype", "mapping_evidence_path",
        "derived_data_path", "derived_sha256", "derived_record_count", "output_dim",
        "prediction_roundtrip_max_abs_diff", "target_exact_match", "ecg_id_exact_match", "status",
    ]
    derivation_csv = data_dir / "REVIEW_DATA_MANIFEST.csv"
    write_csv(derivation_csv, verification, fields)
    derivation_json = data_dir / "REVIEW_DATA_MANIFEST.json"
    derivation_json.write_text(json.dumps({
        "schema_version": 1,
        "derivation_type": "LOSSLESS_BROWSER_SERIALIZATION_OF_PACKAGED_CANONICAL_RECORD_LEVEL_ASSETS",
        "scientific_recomputation": False,
        "source_scope": "STAGING_SAMPLE_PREDICTIONS_RECORD_LEVEL_ONLY",
        "formal_entries": 78,
        "pass": 76,
        "physical_source_unavailable": 2,
        "prediction_roundtrip_pass": 76,
        "target_exact_match_pass": 76,
        "ecg_id_exact_match_pass": 76,
        "rows": verification,
    }, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8", newline="\n")
    write_csv(args.source_verification_csv, verification, fields)

    total_shard_bytes = sum(path.stat().st_size for path in shard_paths)
    largest_shard = max(path.stat().st_size for path in shard_paths)
    if total_shard_bytes > 500 * 1024 * 1024:
        raise ValueError("Derived run shards exceed the 500 MiB governance limit")
    print(json.dumps({
        "formal_entries": len(run_entries),
        "shards": len(shard_paths),
        "missing": sum(not row["physical_sample_available"] for row in run_entries),
        "pass": sum(row["status"] == "PASS" for row in verification),
        "total_shard_bytes": total_shard_bytes,
        "largest_shard_bytes": largest_shard,
        "label_lengths": {key: len(value) for key, value in label_sets.items()},
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
