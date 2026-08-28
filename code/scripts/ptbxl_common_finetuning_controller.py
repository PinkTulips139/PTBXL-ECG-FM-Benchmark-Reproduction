#!/usr/bin/env python3
"""Run one authorized PTB-XL common finetuning queue, then stop."""

import argparse
import csv
import fcntl
import json
import os
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ORDER = [
    "ECGFounder",
    "ECG-JEPA",
    "ST-MEM",
    "MERL",
    "ECGFM-KED",
    "HuBERT-ECG",
    "S4",
    "Net1D",
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=("ptbxl_sub", "ptbxl_super"), required=True)
    parser.add_argument("--matrix", required=True)
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--cwd", required=True)
    args = parser.parse_args()

    state_dir = Path(args.state_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    lock_handle = (state_dir / "controller.lock").open("w", encoding="utf-8")
    try:
        fcntl.flock(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("controller already active", file=sys.stderr)
        return 73

    with Path(args.matrix).open(newline="", encoding="utf-8-sig") as handle:
        rows = [
            row
            for row in csv.DictReader(handle)
            if row["dataset"] == args.dataset
            and row["model"] in ORDER
            and row["instance_group"] in ("INSTANCE_SUB_COMMON", "INSTANCE_SUPER_COMMON")
        ]
    by_model = {row["model"]: row for row in rows}
    missing = [model for model in ORDER if model not in by_model]
    if missing or len(rows) != 8:
        raise RuntimeError(f"invalid common queue matrix; missing={missing}, rows={len(rows)}")

    state = {
        "controller_pid": os.getpid(),
        "dataset": args.dataset,
        "queue_order": ORDER,
        "status": "RUNNING",
        "started_at_utc": now(),
        "current_model": None,
        "completed": [],
    }
    write_json(state_dir / "controller_state.json", state)
    (state_dir / "controller.pid").write_text(f"{os.getpid()}\n", encoding="utf-8")

    for model in ORDER:
        row = by_model[model]
        command = row["exact_command_template"]
        run_id = row["run_id"]
        state.update(
            current_model=model,
            current_run=run_id,
            current_command=command,
            current_started_at_utc=now(),
        )
        write_json(state_dir / "controller_state.json", state)
        run_dir = Path(row["output_dir"]).parent
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "exact_command.sh").write_text(command + "\n", encoding="utf-8")
        (run_dir / "controller_launch.json").write_text(
            json.dumps(
                {
                    "controller_pid": os.getpid(),
                    "run_id": run_id,
                    "model": model,
                    "dataset": args.dataset,
                    "started_at_utc": state["current_started_at_utc"],
                    "pretrained_checkpoint": row["pretrained_checkpoint"],
                    "precision": row["precision"],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"[{now()}] START {run_id}: {shlex.join(['/bin/bash', '-lc', command])}", flush=True)
        completed = subprocess.run(["/bin/bash", "-lc", command], cwd=args.cwd)
        ended = now()
        (run_dir / "controller_exit.json").write_text(
            json.dumps({"exit_code": completed.returncode, "ended_at_utc": ended}, indent=2)
            + "\n",
            encoding="utf-8",
        )
        if completed.returncode != 0:
            state.update(status="FAILED", failed_model=model, failed_run=run_id, exit_code=completed.returncode, ended_at_utc=ended)
            write_json(state_dir / "controller_state.json", state)
            print(f"[{ended}] FAIL {run_id} rc={completed.returncode}", flush=True)
            return completed.returncode
        state["completed"].append(run_id)
        print(f"[{ended}] PASS {run_id}", flush=True)

    state.update(status="STOPPED_COMPLETE", current_model=None, current_run=None, ended_at_utc=now())
    write_json(state_dir / "controller_state.json", state)
    print(f"[{state['ended_at_utc']}] QUEUE COMPLETE; STOP", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
