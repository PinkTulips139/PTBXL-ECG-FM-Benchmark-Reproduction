#!/usr/bin/env python3
"""Singleton, no-retry worker controller with post-run fail-closed validation."""

import argparse
import csv
import fcntl
import json
import math
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


def now():
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path, payload):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def validate_run(row):
    errors = []
    log_path = Path(row["log_path"])
    output_dir = Path(row["output_dir"])
    prediction_dir = Path(row["prediction_path"])
    training_text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.is_file() else ""
    test_log_path = log_path.with_name("formal_test.log")
    test_text = test_log_path.read_text(encoding="utf-8", errors="replace") if test_log_path.is_file() else ""
    text = training_text + "\n" + test_text
    if not training_text:
        errors.append("formal log missing or empty")
    lowered = text.lower()
    if "traceback (most recent call last)" in lowered:
        errors.append("traceback present")
    if "cuda out of memory" in lowered or "torch.cuda.outofmemoryerror" in lowered:
        errors.append("CUDA OOM present")
    if not re.search(r"(?i)epoch\s*99(?:\D|$)", text):
        errors.append("epoch 99 evidence missing")

    best = sorted(output_dir.glob("**/best_model.ckpt"))
    last = sorted(output_dir.glob("**/last.ckpt"))
    if not best:
        errors.append("best checkpoint missing")
    if not last:
        errors.append("last checkpoint missing")
    if best and str(best[0]) not in text and "best_model.ckpt" not in text:
        errors.append("best-checkpoint test restoration evidence missing")

    metric = None
    for line in text.splitlines():
        if "macro_auc_agg_test0" in line:
            numbers = re.findall(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", line.split("macro_auc_agg_test0", 1)[1])
            if numbers:
                metric = float(numbers[-1])
    if metric is None or not math.isfinite(metric):
        errors.append("finite primary Test Macro AUROC missing")

    agg_files = sorted(prediction_dir.glob("**/agg/*.npz"))
    noagg_files = sorted(prediction_dir.glob("**/noagg/*.npz"))
    if not agg_files:
        errors.append("aggregate predictions/targets archive missing")
    if not noagg_files:
        errors.append("raw predictions/targets archive missing")
    expected = (2198, int(row["output_dim"]))
    aggregate_shapes = []
    if agg_files:
        try:
            with np.load(agg_files[-1]) as archive:
                aggregate_shapes = [list(archive[key].shape) for key in archive.files]
            if sum(tuple(shape) == expected for shape in aggregate_shapes) < 2:
                errors.append(f"aggregate prediction/target shape closure missing: expected {expected}")
        except Exception as exc:
            errors.append(f"aggregate archive unreadable: {exc}")
    raw_shapes = []
    if noagg_files:
        try:
            with np.load(noagg_files[-1]) as archive:
                raw_shapes = [list(archive[key].shape) for key in archive.files]
            if len(raw_shapes) < 2:
                errors.append("raw prediction/target arrays missing")
        except Exception as exc:
            errors.append(f"raw archive unreadable: {exc}")

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "primary_test_macro_auroc": metric,
        "best_checkpoint": str(best[0]) if best else None,
        "last_checkpoint": str(last[0]) if last else None,
        "aggregate_shapes": aggregate_shapes,
        "raw_shapes": raw_shapes,
        "validated_at_utc": now(),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", required=True)
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--resume-trained-first-row", action="store_true")
    args = parser.parse_args()
    state_dir = Path(args.state_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    lock = (state_dir / "controller.lock").open("w", encoding="utf-8")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return 73

    with Path(args.matrix).open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or [int(row["execution_order"]) for row in rows] != list(range(1, len(rows) + 1)):
        raise RuntimeError("worker matrix order is invalid")

    resume_evidence = None
    state_path = state_dir / "controller_state.json"
    if args.resume_trained_first_row:
        resume_evidence = json.loads(state_path.read_text(encoding="utf-8"))
        if resume_evidence.get("status") != "FAILED_CLOSED" or resume_evidence.get("current_run") != rows[0]["run_id"]:
            raise RuntimeError("resume requires first-row FAILED_CLOSED post-training evidence")
        if rows[0]["exact_test_command"] == "IN_COMMAND_AUTOMATIC_BEST_CHECKPOINT_TEST":
            raise RuntimeError("resume is only valid for a separate formal-test route")

    state = {
        "status": "RUNNING", "controller_pid": os.getpid(), "started_at_utc": now(),
        "current_run": None, "completed": [], "retry_policy": "NO_RETRY",
        "auto_shutdown": "NO", "validation_policy": "FAIL_CLOSED_BEFORE_NEXT_RUN",
        "resume_trained_first_row": args.resume_trained_first_row,
    }
    if resume_evidence is not None:
        state["resume_evidence"] = resume_evidence
    atomic_json(state_path, state)
    (state_dir / "controller.pid").write_text(f"{os.getpid()}\n", encoding="utf-8")

    for index, row in enumerate(rows):
        run_root = Path(row["output_dir"]).parent
        resume_this_row = args.resume_trained_first_row and index == 0
        if not resume_this_row and run_root.exists() and any(run_root.iterdir()):
            state.update(status="FAILED_CLOSED", failure="target run directory already nonempty", ended_at_utc=now())
            atomic_json(state_dir / "controller_state.json", state)
            return 74
        run_root.mkdir(parents=True, exist_ok=True)
        if not resume_this_row:
            (run_root / "exact_formal_command.sh").write_text(row["exact_formal_command"] + "\n", encoding="utf-8")
        state.update(current_run=row["run_id"], current_model=row["model"], current_mode=row["mode"], current_started_at_utc=now())
        atomic_json(state_dir / "controller_state.json", state)
        if resume_this_row:
            stages = [("BEST_CHECKPOINT_TEST_RESUME_WITHOUT_TRAIN_RETRY", row["exact_test_command"])]
        else:
            stages = [("TRAIN_AND_AUTOMATIC_TEST", row["exact_formal_command"])]
        if not resume_this_row and row["exact_test_command"] != "IN_COMMAND_AUTOMATIC_BEST_CHECKPOINT_TEST":
            stages = [("TRAIN", row["exact_formal_command"]), ("BEST_CHECKPOINT_TEST", row["exact_test_command"])]
        for stage, command in stages:
            state["current_stage"] = stage
            atomic_json(state_dir / "controller_state.json", state)
            completed = subprocess.run(["/bin/bash", "-lc", command])
            if completed.returncode != 0:
                state.update(status="FAILED_CLOSED", return_code=completed.returncode, failed_stage=stage, ended_at_utc=now())
                atomic_json(state_dir / "controller_state.json", state)
                return completed.returncode
        validation = validate_run(row)
        atomic_json(run_root / "post_run_validation.json", validation)
        if validation["status"] != "PASS":
            state.update(status="FAILED_CLOSED", validation=validation, ended_at_utc=now())
            atomic_json(state_dir / "controller_state.json", state)
            return 75
        state["completed"].append(row["run_id"])
        atomic_json(state_dir / "controller_state.json", state)

    state.update(status="STOPPED_COMPLETE", current_run=None, ended_at_utc=now())
    atomic_json(state_dir / "controller_state.json", state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
