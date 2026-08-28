#!/usr/bin/env python3
"""Fail-closed static/path audit for one prepared all-modes command matrix."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", required=True)
    parser.add_argument("--dataset", choices=("ptbxl_sub", "ptbxl_super"), required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    expected_dim = 23 if args.dataset == "ptbxl_sub" else 5
    with Path(args.matrix).open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))

    errors: list[str] = []
    if len(rows) != 20:
        errors.append(f"row_count={len(rows)}")
    if [row.get("mode") for row in rows].count("Finetuning") != 8:
        errors.append("finetuning_count")
    if [row.get("mode") for row in rows].count("Frozen") != 6:
        errors.append("frozen_count")
    if [row.get("mode") for row in rows].count("Linear") != 6:
        errors.append("linear_count")
    if [row.get("execution_order") for row in rows] != [f"{i:02d}" for i in range(1, 21)]:
        errors.append("execution_order")

    for row in rows:
        run = row.get("run_id", "UNKNOWN")
        command = row.get("exact_formal_command", "")
        if row.get("dataset") != args.dataset or row.get("output_dim") != str(expected_dim):
            errors.append(f"{run}:dataset_or_dim")
        for token in ("--batch-size 64", "--epochs 100", "--optimizer adam", "--lr 0.001", "--lr-schedule const"):
            if token not in command:
                errors.append(f"{run}:missing:{token}")
        if "--wd 0.001" not in command and "--weight-decay 0.001" not in command:
            errors.append(f"{run}:missing:weight_decay")
        if f"--finetune-dataset {args.dataset}" not in command:
            errors.append(f"{run}:dataset_command")
        if row.get("output_dir") not in command or row.get("log_path") not in command:
            errors.append(f"{run}:execution_paths")
        if "PTBXL_ALL" in command or "ptbxl_all" in command:
            errors.append(f"{run}:all_leak")
        for field in ("python_environment", "runner"):
            path = Path(row[field])
            if not path.exists():
                errors.append(f"{run}:missing_{field}:{path}")
        checkpoint = row.get("pretrained_checkpoint", "")
        if checkpoint and checkpoint not in {"SCRATCH", "SCRATCH_INITIALIZATION", "supervised scratch"} and not Path(checkpoint).is_file():
            errors.append(f"{run}:missing_checkpoint:{checkpoint}")
        if row.get("mode") != "Finetuning" and row.get("model") in {"ECGFounder", "MERL", "ECGFM-KED"}:
            if "ptbxl_frozen_linear_bn_guard_runner.py" not in command:
                errors.append(f"{run}:missing_bn_guard")
        if row.get("model") == "S4" and "PYKEOPS_BUILD_FOLDER=" not in command:
            errors.append(f"{run}:missing_keops_environment")

    result = {
        "dataset": args.dataset,
        "output_dim": expected_dim,
        "command_count": len(rows),
        "errors": errors,
        "status": "PASS" if not errors else "FAIL",
    }
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
