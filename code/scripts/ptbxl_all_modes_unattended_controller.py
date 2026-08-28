#!/usr/bin/env python3
"""Prepared-only singleton controller for one authorized 20-run all-modes queue."""

import argparse
import csv
import fcntl
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def now():
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path, payload):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", required=True)
    parser.add_argument("--state-dir", required=True)
    args = parser.parse_args()
    state_dir = Path(args.state_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    lock = (state_dir / "controller.lock").open("w", encoding="utf-8")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("singleton controller already active", file=sys.stderr)
        return 73

    with Path(args.matrix).open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 20 or [int(row["execution_order"]) for row in rows] != list(range(1, 21)):
        raise RuntimeError("matrix must contain the ordered 20-run queue")

    state = {
        "status": "RUNNING", "controller_pid": os.getpid(), "started_at_utc": now(),
        "current_run": None, "current_stage": None, "completed": [],
        "retry_policy": "NO_RETRY", "auto_shutdown": "NO",
    }
    atomic_json(state_dir / "controller_state.json", state)
    (state_dir / "controller.pid").write_text(f"{os.getpid()}\n", encoding="utf-8")

    for row in rows:
        run_root = Path(row["output_dir"]).parent
        run_root.mkdir(parents=True, exist_ok=True)
        (run_root / "exact_formal_command.sh").write_text(row["exact_formal_command"] + "\n", encoding="utf-8")
        (run_root / "exact_test_command.sh").write_text(row["exact_test_command"] + "\n", encoding="utf-8")
        stages = [("TRAIN_AND_AUTOMATIC_TEST", row["exact_formal_command"])]
        if row["exact_test_command"] != "IN_COMMAND_AUTOMATIC_BEST_CHECKPOINT_TEST":
            stages = [("TRAIN", row["exact_formal_command"]), ("BEST_CHECKPOINT_TEST", row["exact_test_command"])]
        for stage, command in stages:
            state.update(current_run=row["run_id"], current_model=row["model"], current_mode=row["mode"], current_stage=stage, current_started_at_utc=now())
            atomic_json(state_dir / "controller_state.json", state)
            completed = subprocess.run(["/bin/bash", "-lc", command])
            if completed.returncode != 0:
                state.update(status="FAILED_CLOSED", exit_code=completed.returncode, ended_at_utc=now())
                atomic_json(state_dir / "controller_state.json", state)
                return completed.returncode
        state["completed"].append(row["run_id"])

    state.update(status="STOPPED_COMPLETE", current_run=None, current_stage=None, ended_at_utc=now())
    atomic_json(state_dir / "controller_state.json", state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
