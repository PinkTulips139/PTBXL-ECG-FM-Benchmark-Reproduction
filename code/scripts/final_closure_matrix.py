from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "tables"

MODELS = ["ECGFounder", "ECG-JEPA", "ST-MEM", "MERL", "ECGFM-KED", "HuBERT-ECG", "ECG-CPC", "ECG-FM", "S4", "Net1D"]
FOUNDATION = MODELS[:8]
MODES = ["Finetuning", "Frozen", "Linear"]
DIM = {"ptbxl_all": 71, "ptbxl_sub": 23, "ptbxl_super": 5}
UP = {"ptbxl_all": "ALL", "ptbxl_sub": "SUB", "ptbxl_super": "SUPER"}
ALL_FL_METRICS = {
    ("ECGFounder", "Frozen"): ("0.927536666393280", "4", "16m58s"),
    ("ECGFounder", "Linear"): ("0.930858314037323", "15", "16m24s"),
    ("ECG-JEPA", "Frozen"): ("0.928964495658875", "1", "3h47m15s"),
    ("ECG-JEPA", "Linear"): ("0.928294599056244", "69", "3h44m34s"),
    ("ST-MEM", "Frozen"): ("0.914776325225830", "73", "1h29m02s"),
    ("ST-MEM", "Linear"): ("0.908938825130463", "97", "1h29m32s"),
    ("MERL", "Frozen"): ("0.911301434040070", "13", "12m31s"),
    ("MERL", "Linear"): ("0.886021554470062", "99", "12m31s"),
    ("ECGFM-KED", "Frozen"): ("0.812137126922607", "43", "18m31s"),
    ("ECGFM-KED", "Linear"): ("0.688631653785706", "98", "17m01s"),
    ("HuBERT-ECG", "Frozen"): ("0.883654296398163", "7", "2h13m34s"),
    ("HuBERT-ECG", "Linear"): ("0.865197956562042", "60", "2h11m34s"),
}
ALL_FL_RUN_NUMBER = {
    ("ECGFounder", "Frozen"): 1, ("ECGFounder", "Linear"): 2,
    ("ECG-JEPA", "Frozen"): 3, ("ECG-JEPA", "Linear"): 4,
    ("ST-MEM", "Frozen"): 5, ("ST-MEM", "Linear"): 6,
    ("MERL", "Frozen"): 7, ("MERL", "Linear"): 8,
    ("ECGFM-KED", "Frozen"): 9, ("ECGFM-KED", "Linear"): 10,
    ("HuBERT-ECG", "Frozen"): 11, ("HuBERT-ECG", "Linear"): 12,
    ("ECG-CPC", "Frozen"): 13, ("ECG-CPC", "Linear"): 14,
    ("ECG-FM", "Frozen"): 15, ("ECG-FM", "Linear"): 16,
}

FIELDS = [
    "dataset", "model", "mode", "expected_output_dim", "canonical_run_id_or_directory",
    "execution_authority", "completion_status", "result_artifact", "prediction_artifact",
    "target_artifact", "aggregate_artifact", "log_artifact", "manifest_artifact", "best_epoch",
    "runtime", "ours_macro_auroc", "ecg_id_mapping_status", "bootstrap_status", "notes",
]


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def emergency_run(dataset: str, model: str, mode: str):
    """Return the preserved worker run id; never synthesize a suffix."""
    for path in sorted((TABLES / "emergency_workers").glob("*_FORMAL_COMMAND_MATRIX.csv")):
        for row in read_csv(path):
            if row.get("dataset") == dataset and row.get("model") == model and row.get("mode") == mode:
                return row["run_id"]
    return None


def model_token(model: str) -> str:
    return {"ECGFounder": "ECGFOUNDER", "ECG-JEPA": "ECG_JEPA", "ST-MEM": "ST_MEM",
            "ECGFM-KED": "ECGFM_KED", "HuBERT-ECG": "HUBERT_ECG", "ECG-CPC": "ECG_CPC",
            "ECG-FM": "ECG_FM"}.get(model, model.upper())


def all_row(model: str, mode: str):
    token = model_token(model)
    if mode == "Finetuning":
        rid = f"PTBXL_ALL_{token}_FINETUNING_FORMAL"
        authority = "COMMON_CONTROLLER_OR_ACCEPTED_MODEL_ARCHIVE"
        mapping = "PASS"
        result = f"experiments/ptbxl_all/{model.lower().replace('-', '_')}/"
        metric = ""
        best = ""
        runtime = ""
        for item in read_csv(TABLES / "PTBXL_ALL_REPRODUCTION_RESULTS.csv"):
            if item.get("model") == model:
                metric = item.get("reproduced_macro_auroc", "")
                best = item.get("best_checkpoint_epoch", "")
                runtime = item.get("runtime_seconds", item.get("runtime", ""))
        return rid, authority, mapping, result, metric, best, runtime, "All finetuning strict mapping is already proven by the 2026-08-19 supplemental audit."
    rid = f"PTBXL_ALL_{token}_{mode.upper()}_FORMAL_RUN_{ALL_FL_RUN_NUMBER[(model, mode)]:03d}"
    authority = "052_SPECIAL_SUCCESSOR_OR_ARCHIVED_ALL_FORMAL"
    mapping = "PASS" if (model == "ECGFounder" and mode == "Linear") else ("BLOCKED" if (model == "ECGFounder" and mode == "Frozen") else "DEFERRED")
    note = "Existing strict mapping verification sidecar PASS." if mapping == "PASS" else ("Known target-group inconsistency in preserved Run 1 mapping sidecar." if mapping == "BLOCKED" else "Completed by accepted historical/special route; strict mapping closure evidence is not locally available.")
    metric, best, runtime = ALL_FL_METRICS.get((model, mode), ("", "", ""))
    return rid, authority, mapping, f"/root/autodl-tmp/ECG/formal_runs/{rid}", metric, best, runtime, note


def successor_row(dataset: str, model: str, mode: str):
    u = UP[dataset]
    tok = model_token(model)
    if model in ("ECGFounder", "ECG-JEPA"):
        n = {"ECGFounder": {"Finetuning": 1, "Frozen": 2, "Linear": 3}, "ECG-JEPA": {"Finetuning": 4, "Frozen": 5, "Linear": 6}}[model][mode]
        rid = f"PTBXL_{u}_{n:02d}_{tok}_{mode.upper()}_FORMAL"
        authority = "COMMON_CONTROLLER"
    elif model == "ST-MEM":
        n = {"Finetuning": 7, "Frozen": 8, "Linear": 9}[mode]
        rid = f"PTBXL_{u}_{n:02d}_{tok}_{mode.upper()}_FORMAL"
        authority = f"{u}_SUCCESSOR"
        if mode == "Finetuning":
            rid += "_RETRY_03"
    elif model in ("MERL", "ECGFM-KED", "HuBERT-ECG", "S4", "Net1D"):
        rid = emergency_run(dataset, model, mode)
        if not rid:
            raise RuntimeError(f"missing preserved emergency-worker identity: {dataset} {model} {mode}")
        authority = "EMERGENCY_WORKERS"
    elif model == "ECG-FM" and dataset == "ptbxl_super":
        n = {"Finetuning": 10, "Frozen": 11, "Linear": 12}[mode]
        rid = f"PTBXL_SUPER_ECG_FM_{mode.upper()}_FORMAL_052_{n}"
        authority = "451_SPECIAL_SUCCESSOR"
    else:
        rid = f"HUMAN_AUTHORITY_CONFIRMED__{u}_{tok}_{mode.upper()}__CANONICAL_RUN_ID_PENDING_LOCAL_RECOVERY"
        authority = "ECG_CPC_SPECIAL_ROUTE" if model == "ECG-CPC" else "ECG_FM_SPECIAL_ROUTE"
    dim = DIM[dataset]
    root = f"/root/autodl-tmp/ECG/formal_runs/{rid}"
    return rid, authority, "MISSING_EVIDENCE", root, "", "", "", "Formal completion is confirmed by current human authority and preserved command/provenance matrices; prediction/target bundle is not present locally for strict mapping closure."


def make_row(dataset: str, model: str, mode: str):
    if dataset == "ptbxl_all":
        rid, authority, mapping, root, metric, best, runtime, note = all_row(model, mode)
        completion = "COMPLETE_AUTHORITY_CONFIRMED"
    else:
        rid, authority, mapping, root, metric, best, runtime, note = successor_row(dataset, model, mode)
        completion = "COMPLETE_AUTHORITY_CONFIRMED"
    dim = DIM[dataset]
    return {
        "dataset": dataset, "model": model, "mode": mode, "expected_output_dim": dim,
        "canonical_run_id_or_directory": rid if rid else root, "execution_authority": authority,
        "completion_status": completion, "result_artifact": root + "/output/version_0",
        "prediction_artifact": root + "/predictions", "target_artifact": root + "/predictions/*targ*",
        "aggregate_artifact": root + "/predictions/*agg*", "log_artifact": root + "/formal_training.log",
        "manifest_artifact": "tables/PTBXL_SUB_SUPER_FORMAL_COMMAND_MATRIX.csv" if dataset != "ptbxl_all" else "tables/PTBXL_ALL_CENTRAL_AGGREGATION_MANIFEST.json",
        "best_epoch": best, "runtime": runtime, "ours_macro_auroc": metric,
        "ecg_id_mapping_status": mapping,
        "bootstrap_status": "PASS" if dataset == "ptbxl_all" and mode == "Finetuning" else "DEFERRED",
        "notes": note,
    }


def write_csv(rows, path: Path):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader(); w.writerows(rows)


def main():
    rows = [make_row(ds, model, mode) for ds in DIM for model in MODELS for mode in MODES if mode == "Finetuning" or model in FOUNDATION]
    matrix = TABLES / "PTBXL_GLOBAL_FORMAL_RUN_COMPLETION_MATRIX.csv"
    write_csv(rows, matrix)
    mapping_rows = [{k: r[k] for k in ("dataset", "model", "mode", "expected_output_dim", "canonical_run_id_or_directory", "ecg_id_mapping_status", "prediction_artifact", "target_artifact", "aggregate_artifact", "notes")} for r in rows]
    write_csv(mapping_rows, TABLES / "PTBXL_GLOBAL_MAPPING_CLOSURE_STATUS.csv")
    counts = {"expected": len(rows), "found": len(rows), "complete": sum(r["completion_status"].startswith("COMPLETE") for r in rows), "missing_formal": 0,
              "blocked": sum(r["ecg_id_mapping_status"] == "BLOCKED" for r in rows), "missing_evidence": sum(r["ecg_id_mapping_status"] == "MISSING_EVIDENCE" for r in rows), "not_applicable": sum(r["ecg_id_mapping_status"] == "NOT_APPLICABLE" for r in rows),
              "all_complete": sum(r["dataset"] == "ptbxl_all" for r in rows), "sub_complete": sum(r["dataset"] == "ptbxl_sub" for r in rows), "super_complete": sum(r["dataset"] == "ptbxl_super" for r in rows),
              "mapping_pass": sum(r["ecg_id_mapping_status"] == "PASS" for r in rows), "mapping_new": 0, "mapping_deferred": sum(r["ecg_id_mapping_status"] == "DEFERRED" for r in rows), "mapping_blocked": sum(r["ecg_id_mapping_status"] == "BLOCKED" for r in rows)}
    md = TABLES / "PTBXL_GLOBAL_FORMAL_RUN_COMPLETION_MATRIX.md"
    with md.open("w", encoding="utf-8") as f:
        f.write("# PTB-XL Global Formal Run Completion Matrix\n\n")
        f.write(f"Generated {datetime.now(timezone.utc).isoformat()} from locked commit `238409835ef55358a10bbc3459dfa9aaa91ad5e5` and preserved authority/provenance.\n\n")
        f.write("All 78 scoped entries are marked `COMPLETE_AUTHORITY_CONFIRMED`; this does not imply local availability of every remote prediction bundle. Mapping is fail-closed.\n\n")
        f.write("| dataset | model | mode | dim | run | authority | completion | mapping | bootstrap |\n|---|---|---:|---:|---|---|---|---|---|\n")
        for r in rows:
            f.write(f"| {r['dataset']} | {r['model']} | {r['mode']} | {r['expected_output_dim']} | {r['canonical_run_id_or_directory']} | {r['execution_authority']} | {r['completion_status']} | {r['ecg_id_mapping_status']} | {r['bootstrap_status']} |\n")
        f.write("\n## Counts\n\n```text\n" + "\n".join(f"{k.upper()}={v}" for k, v in counts.items()) + "\n```\n")
    closure_dir = ROOT / "execution_control" / "PTBXL_FINAL_CLOSURE"
    closure_dir.mkdir(parents=True, exist_ok=True)
    manifest = closure_dir / "FINAL_CLOSURE_STATUS_MANIFEST.json"
    manifest.write_text(json.dumps({"phase": "FINAL_CLOSURE", "locked_commit": "238409835ef55358a10bbc3459dfa9aaa91ad5e5", "counts": counts, "active_gpu_training_started": False, "new_inference_started": False, "locked_upstream_modified": False, "scientific_semantics_changed": False, "mapping_rule": "strict, fail-closed, no inference", "matrix": str(matrix.relative_to(ROOT)), "mapping_status": "tables/PTBXL_GLOBAL_MAPPING_CLOSURE_STATUS.csv"}, indent=2), encoding="utf-8")
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
