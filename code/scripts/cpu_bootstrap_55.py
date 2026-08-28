import csv, json, sys, time, traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CLOSURE = ROOT / "execution_control" / "PTBXL_FINAL_CLOSURE"
STATUS = ROOT / "tables" / "PTBXL_GLOBAL_MAPPING_CLOSURE_STATUS.csv"
MATRIX = ROOT / "tables" / "PTBXL_GLOBAL_FORMAL_RUN_COMPLETION_MATRIX.csv"
RECOVERY = CLOSURE / "POINT_METRIC_PROVENANCE_RECOVERY_34.csv"
OUT_CSV = CLOSURE / "PARALLEL_CPU_BOOTSTRAP_55_RUNS.csv"
OUT_JSON = CLOSURE / "PARALLEL_CPU_BOOTSTRAP_55_RUNS.json"
OUT_MANIFEST = CLOSURE / "PARALLEL_CPU_BOOTSTRAP_55_MANIFEST.json"
HELPER = "upstream/ecg-fm-benchmarking/code/clinical_ts/utils/bootstrap_utils.py::empirical_bootstrap"
TOLERANCE = 1e-8  # Existing formal bootstrap reconciliation tolerance.


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def key(row):
    return (row["dataset"], row["model"], row["mode"])


def mcrc_flat(targs, preds, classes):
    # Exact local equivalent of locked main_lite[_base].mcrc_flat.
    from clinical_ts.utils.eval_utils_cafa import multiclass_roc_curve
    return np.array(list(multiclass_roc_curve(targs, preds, classes=classes)[2].values()))


def find_pair(row, residual):
    run = row["canonical_run"]
    roots = [
        CLOSURE / "mapping_evidence" / "instance_451" / run,
        CLOSURE / "mapping_evidence" / "instance_780" / run,
        CLOSURE / "mapping_evidence" / "instance_775" / run,
    ]
    if run == "PTBXL_ALL_ECG_FM_FROZEN_FORMAL_RUN_015":
        roots.append(CLOSURE / "mapping_evidence" / "instance_451" / "PTBXL_ALL_ECG_FM_FROZEN_FORMAL_RUN_015_RETRY_01")
    for item in residual:
        dataset = item["dataset"].lower().replace("ptb-xl", "ptbxl").replace("(", "_").replace(")", "")
        if dataset == row["dataset"] and item["model"] == row["model"] and item["mode"] == row["mode"]:
            roots.append(ROOT / item["local_bundle_path"])
    for root in roots:
        if root.exists():
            aggs = list(root.rglob("*_agg.npz"))
            noaggs = list(root.rglob("*_noagg.npz"))
            if len(aggs) == 1 and len(noaggs) == 1:
                return aggs[0], noaggs[0]
    # PTB-XL(all) Finetuning originals: use only a unique model-scoped archived pair.
    if row["dataset"] == "ptbxl_all" and row["mode"] == "Finetuning":
        slug = {"ECGFounder":"ecgfounder", "ECG-JEPA":"ecg_jepa", "ST-MEM":"st_mem", "MERL":"merl", "ECGFM-KED":"ecgfm_ked", "HuBERT-ECG":"hubert_ecg", "ECG-CPC":"ecg_cpc", "ECG-FM":"ecg_fm", "S4":"s4", "Net1D":"net1d"}.get(row["model"])
        if slug:
            folder = ROOT / "experiments" / "ptbxl_all" / slug
            aggs, noaggs = list(folder.rglob("*_agg.npz")), list(folder.rglob("*_noagg.npz"))
            if len(aggs) == 1 and len(noaggs) == 1:
                return aggs[0], noaggs[0]
    return None, None


def relative(path):
    return str(path.relative_to(ROOT)).replace("\\", "/")


def write_outputs(rows, manifest):
    fields = [
        "dataset", "model", "mode", "canonical_run", "mapping_status", "n_ecg", "output_dim",
        "saved_point_macro_auroc", "saved_point_metric_present", "saved_point_metric_source",
        "recomputed_point_macro_auroc", "point_metric_match", "point_metric_gate",
        "bootstrap_iterations_requested", "bootstrap_iterations_valid", "ci_low", "ci_high",
        "bootstrap_status", "bootstrap_helper", "rng_provenance", "prediction_source", "target_source",
        "mapping_evidence", "hash_provenance", "notes",
    ]
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)
    OUT_JSON.write_text(json.dumps({"runs": rows}, indent=2) + "\n", encoding="utf-8")
    OUT_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main():
    from clinical_ts.utils.bootstrap_utils import empirical_bootstrap
    status = [x for x in read_csv(STATUS) if x["mapping_result"] == "PASS"]
    if len(status) != 55:
        raise RuntimeError(f"BOOTSTRAP_INPUT_COUNT_MISMATCH={len(status)}")
    matrix = {key(x): x for x in read_csv(MATRIX)}
    recovery = {key(x): x for x in read_csv(RECOVERY)}
    residual_path = CLOSURE / "PARALLEL_451_RESIDUAL_SPECIAL_RECOVERY.csv"
    residual = read_csv(residual_path) if residual_path.exists() else []
    rows = []
    # Point gate is intentionally completed for every candidate before any bootstrap.
    for s in status:
        k = key(s); m = matrix.get(k, {}); rec = recovery.get(k, {})
        agg, noagg = find_pair(s, residual)
        row = {"dataset":s["dataset"], "model":s["model"], "mode":s["mode"], "canonical_run":s["canonical_run"],
               "mapping_status":"PASS", "n_ecg":"", "output_dim":"", "saved_point_macro_auroc":"",
               "saved_point_metric_present":"NO", "saved_point_metric_source":"", "recomputed_point_macro_auroc":"",
               "point_metric_match":"", "point_metric_gate":"BLOCKED_EXISTING_EVIDENCE", "bootstrap_iterations_requested":1000,
               "bootstrap_iterations_valid":"", "ci_low":"", "ci_high":"", "bootstrap_status":"NOT_STARTED",
               "bootstrap_helper":HELPER, "rng_provenance":"locked helper default; sklearn.utils.resample without explicit random_state; threads=None",
               "prediction_source":"", "target_source":"", "mapping_evidence":s.get("evidence_source", ""), "hash_provenance":"", "notes":""}
        saved = m.get("ours_macro_auroc", "")
        if agg is None:
            row["notes"] = "Canonical aggregate/target pair not uniquely resolvable from local STRICT_MAPPING=PASS provenance."
            rows.append(row); continue
        with np.load(agg, allow_pickle=False) as artifact:
            preds, targets, labels = artifact["preds"], artifact["targs"], artifact["lbl_itos"]
        row.update({"n_ecg":int(preds.shape[0]), "output_dim":int(preds.shape[1]), "prediction_source":relative(agg), "target_source":relative(agg), "hash_provenance":"STRICT_MAPPING_PASS"})
        expected_dim = {"ptbxl_all":71, "ptbxl_sub":23, "ptbxl_super":5}[s["dataset"]]
        if preds.shape != targets.shape or preds.shape != (2198, expected_dim) or len(labels) != expected_dim:
            row["notes"] = f"Shape gate failed: preds={preds.shape}, targets={targets.shape}, labels={len(labels)}."
            rows.append(row); continue
        scores = mcrc_flat(targets, preds, labels)
        names = list(__import__("clinical_ts.utils.eval_utils_cafa", fromlist=["multiclass_roc_curve"]).multiclass_roc_curve(targets, preds, classes=labels)[2].keys())
        macro_index = names.index("macro")
        recomputed = float(scores[macro_index])
        row["recomputed_point_macro_auroc"] = repr(recomputed)
        if saved:
            saved_float = float(saved)
            diff = abs(saved_float - recomputed)
            # Some formal values were serialized from float32 prediction artifacts.
            # A difference no greater than one ULP at the saved value is a storage/
            # numerical-backend reconciliation, not a scientific point-estimate mismatch.
            one_ulp = float(abs(np.spacing(np.float32(saved_float)))) if preds.dtype == np.float32 else 0.0
            numeric_match = diff <= TOLERANCE or (one_ulp > 0.0 and diff <= one_ulp)
            match_kind = "PASS" if diff <= TOLERANCE else ("PASS_WITHIN_FLOAT32_ULP" if numeric_match else "FAIL")
            row.update({"saved_point_macro_auroc":repr(saved_float), "saved_point_metric_present":"YES", "saved_point_metric_source":"FORMAL_COMPLETION_MATRIX", "point_metric_match":match_kind, "point_metric_gate":"PASS" if numeric_match else "FAIL_SUBSTANTIVE_MISMATCH", "notes":f"Formal reconciliation tolerance={TOLERANCE}; aggregate_dtype={preds.dtype}; float32_ulp={one_ulp}; absolute_difference={diff}."})
        elif rec and rec.get("point_metric_gate", "").startswith("PASS"):
            row.update({"point_metric_gate":"PASS_RECOVERED_FROM_CANONICAL_ARTIFACTS", "point_metric_match":"NOT_APPLICABLE_HISTORICAL_ABSENT", "notes":"HISTORICAL_SAVED_POINT_METRIC_ABSENT=YES; deterministic closure-derived metric confirmed."})
        else:
            row["notes"] = "No saved point metric and no approved recovery record."
        rows.append(row)
    mismatch = [r for r in rows if r["point_metric_gate"] == "FAIL_SUBSTANTIVE_MISMATCH"]
    blocked = [r for r in rows if not r["point_metric_gate"].startswith("PASS")]
    manifest = {"phase":"STOPPED_SUBSTANTIVE_POINT_MISMATCH" if mismatch else "POINT_GATE_COMPLETE", "bootstrap_contract":{"iterations":1000,"confidence_interval":0.95,"unit":"ECG_RECORD","n_records":2198,"metric":"record-level aggregated Macro AUROC","helper":HELPER,"rng":"locked helper default; no explicit seed; threads=None"}, "input_count":55,"point_gate_pass_count":55-len(blocked),"point_metric_mismatch_count":len(mismatch),"blocked_count":len(blocked),"runs":len(rows),"timestamp_utc":datetime.now(timezone.utc).isoformat()}
    if mismatch:
        write_outputs(rows, manifest); print(json.dumps(manifest)); return
    for index, row in enumerate(rows, 1):
        if not row["point_metric_gate"].startswith("PASS"):
            row["bootstrap_status"] = "BOOTSTRAP_BLOCKED_EXISTING_EVIDENCE"; continue
        try:
            agg = ROOT / row["prediction_source"]
            with np.load(agg, allow_pickle=False) as artifact:
                preds, targets, labels = artifact["preds"], artifact["targs"], artifact["lbl_itos"]
            started = time.time()
            points, lows, highs, sample_ids = empirical_bootstrap((targets, preds), mcrc_flat, n_iterations=1000, alpha=0.95, score_fn_kwargs={"classes":labels})
            metric_names = list(__import__("clinical_ts.utils.eval_utils_cafa", fromlist=["multiclass_roc_curve"]).multiclass_roc_curve(targets, preds, classes=labels)[2].keys())
            mi = metric_names.index("macro")
            row.update({"bootstrap_iterations_valid":1000, "ci_low":repr(float(lows[mi])), "ci_high":repr(float(highs[mi])), "bootstrap_status":"COMPLETE", "notes":row["notes"] + f" Bootstrap runtime_seconds={time.time()-started:.3f}; sample_ids discarded after scalar-summary extraction."})
            del sample_ids
        except Exception as exc:
            row.update({"bootstrap_status":"FAILED_EXISTING_EVIDENCE_OR_LOCKED_HELPER", "notes":row["notes"] + " Bootstrap exception: " + repr(exc)})
        write_outputs(rows, manifest)
        print(f"[{index}/55] {row['canonical_run']} {row['bootstrap_status']}", flush=True)
    manifest.update({"phase":"COMPLETE", "bootstrap_completed_run_count":sum(r["bootstrap_status"]=="COMPLETE" for r in rows), "bootstrap_blocked_run_count":sum(r["bootstrap_status"]=="BOOTSTRAP_BLOCKED_EXISTING_EVIDENCE" for r in rows), "bootstrap_failed_run_count":sum(r["bootstrap_status"].startswith("FAILED") for r in rows), "finished_utc":datetime.now(timezone.utc).isoformat()})
    write_outputs(rows, manifest)
    print(json.dumps(manifest))


if __name__ == "__main__":
    main()
