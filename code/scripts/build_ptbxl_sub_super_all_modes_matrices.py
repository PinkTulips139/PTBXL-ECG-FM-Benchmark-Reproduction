#!/usr/bin/env python3
"""Build deterministic sub/super all-modes formal command matrices (readiness only)."""

import csv
import re
from pathlib import Path


ROOT = "/root/autodl-tmp/ECG"
ORDER = [
    ("ECGFounder", ("Finetuning", "Frozen", "Linear")),
    ("ECG-JEPA", ("Finetuning", "Frozen", "Linear")),
    ("ST-MEM", ("Finetuning", "Frozen", "Linear")),
    ("MERL", ("Finetuning", "Frozen", "Linear")),
    ("ECGFM-KED", ("Finetuning", "Frozen", "Linear")),
    ("HuBERT-ECG", ("Finetuning", "Frozen", "Linear")),
    ("S4", ("Finetuning",)),
    ("Net1D", ("Finetuning",)),
]

FIELDS = [
    "execution_order", "run_id", "dataset", "output_dim", "model", "mode",
    "python_environment", "runner", "wrapper", "pretrained_checkpoint",
    "initialization_source", "precision", "batch_size", "epochs", "optimizer",
    "lr", "weight_decay", "lr_schedule", "output_dir", "log_path",
    "prediction_path", "checkpoint_dir", "exact_formal_command",
    "exact_test_command", "formal_test_route", "optimizer_scope", "bn_guard", "gpu_gate_policy",
    "special_protection", "status",
]


def replace_option(command: str, option: str, value: str) -> str:
    pattern = rf"({re.escape(option)}\s+)(\S+)"
    updated, count = re.subn(pattern, rf"\g<1>{value}", command, count=1)
    if count != 1:
        raise RuntimeError(f"missing option {option}: {command}")
    return updated


def strip_redirect(command: str) -> str:
    return re.sub(r"\s+>\s+\S+\s+2>&1\s*$", "", command)


def replace_entrypoint(command: str, old_python: str, old_runner: str, new_python: str, new_runner: str, prefix: str = "") -> str:
    old = f"{old_python} {old_runner}"
    if old not in command:
        raise RuntimeError(f"entrypoint not found: {old}")
    return command.replace(old, f"{prefix}{new_python} {new_runner}", 1)


def build(dataset: str, output_dim: int, target: Path, source_rows: list[dict]) -> None:
    source = {row["model"]: row for row in source_rows if row["dataset"] == dataset and "COMMON" in row["instance_group"]}
    rows = []
    sequence = 0
    dataset_tag = "PTBXL_SUB" if dataset == "ptbxl_sub" else "PTBXL_SUPER"
    for model, modes in ORDER:
        base = source[model]
        for mode in modes:
            sequence += 1
            model_tag = re.sub(r"[^A-Z0-9]+", "_", model.upper()).strip("_")
            run_id = f"{dataset_tag}_{sequence:02d}_{model_tag}_{mode.upper()}_FORMAL"
            run_root = f"{ROOT}/formal_runs/{dataset_tag}/{run_id}"
            output_dir = f"{run_root}/output"
            log_path = f"{run_root}/formal_training.log"
            prediction_path = f"{run_root}/predictions"
            checkpoint_dir = f"{output_dir}/version_0"
            command = strip_redirect(base["exact_command_template"])
            if "--lr-schedule" not in command:
                command += " --lr-schedule const"
            command = re.sub(r"^RUN_ID=\S+", f"RUN_ID={run_id}", command)
            command = replace_option(command, "--output-path", output_dir)
            if "--prediction-path" in command:
                command = replace_option(command, "--prediction-path", prediction_path)
            elif model not in {"ECGFM-KED", "HuBERT-ECG"}:
                command += f" --prediction-path {prediction_path} --export-predictions"
            command += f" > {log_path} 2>&1"

            if model == "S4":
                command = (
                    "LIBRARY_PATH=/usr/local/cuda/targets/x86_64-linux/lib:${LIBRARY_PATH:-} "
                    "LD_LIBRARY_PATH=/usr/local/cuda/targets/x86_64-linux/lib:${LD_LIBRARY_PATH:-} "
                    f"PYKEOPS_BUILD_FOLDER={ROOT}/preparation/keops_cache " + command
                )

            python_env = base["python_environment"]
            runner = base["runner"]
            wrapper = base["wrapper"]
            optimizer_scope = "full accepted Finetuning parameter groups"
            bn_guard = "NOT_APPLICABLE"
            gate_policy = "TARGETED_GPU_GATE_REQUIRED"
            protection = "original checkpoint/scratch; independent mode branch"

            if mode == "Finetuning" and runner == "code/main_lite.py":
                absolute_runner = f"{ROOT}/worktrees/common/code/main_lite.py"
                command = replace_entrypoint(command, python_env, runner, python_env, absolute_runner)
                runner = absolute_runner

            if mode != "Finetuning":
                eval_mode = mode.lower()
                command = replace_option(command, "--eval-mode", eval_mode)
                python_env = f"{ROOT}/environments/lightning3/bin/python"
                if model == "ECGFM-KED":
                    execution_root = f"{ROOT}/worktrees/ecgfm_ked"
                elif model == "HuBERT-ECG":
                    execution_root = f"{ROOT}/worktrees/hubert_ecg"
                elif model == "ST-MEM":
                    execution_root = f"{ROOT}/worktrees/stmem_formal"
                else:
                    execution_root = f"{ROOT}/worktrees/common"
                new_runner = f"{execution_root}/code/main_lite.py"
                if model in {"ECGFounder", "MERL", "ECGFM-KED"}:
                    guard = f"{ROOT}/scripts/ptbxl_frozen_linear_bn_guard_runner.py"
                    command = replace_entrypoint(command, base["python_environment"], base["runner"], python_env, guard, f"PTBXL_EXECUTION_ROOT={execution_root} ")
                    runner = guard
                    bn_guard = "REQUIRED_ACCEPTED_EXECUTION_ONLY"
                    protection += "; encoder model.eval re-applied after wrapper.train"
                elif model == "ST-MEM":
                    command = replace_entrypoint(command, base["python_environment"], base["runner"], python_env, new_runner)
                    runner = new_runner
                    protection += "; unused auxiliary warning non-blocking and excluded from optimizer"
                else:
                    command = replace_entrypoint(command, base["python_environment"], base["runner"], python_env, new_runner)
                    runner = new_runner
                optimizer_scope = "active attention head only" if mode == "Frozen" else "active Linear head only"
                wrapper = base["wrapper"].split(" + ")[0]
                if mode == "Linear" and model not in {"ECGFounder", "MERL", "ECGFM-KED"}:
                    gate_policy = "STATIC_LINEAR_AUDIT_PLUS_CORRESPONDING_FROZEN_GPU_GATE"

            if mode != "Finetuning" and "--prediction-path" in command and "--export-predictions" not in command:
                command = command.replace(f" > {log_path} 2>&1", f" --export-predictions > {log_path} 2>&1")

            formal_test_route = "runner automatic best-checkpoint test with prediction export"
            exact_test_command = "IN_COMMAND_AUTOMATIC_BEST_CHECKPOINT_TEST"
            if "--skip-test-after-fit" in command or model == "ST-MEM" and mode == "Finetuning":
                formal_test_route = "accepted separated best_model.ckpt test; prediction/target export required before run closure"
                test_command = strip_redirect(command).replace(" --skip-test-after-fit", "")
                test_command = replace_option(test_command, "--epochs", "0")
                test_command = replace_option(test_command, "--output-path", f"{run_root}/formal_test_output")
                test_command += f" --eval-only {checkpoint_dir}/best_model.ckpt"
                if "--prediction-path" in test_command:
                    test_command = replace_option(test_command, "--prediction-path", prediction_path)
                else:
                    test_command += f" --prediction-path {prediction_path}"
                if "--export-predictions" not in test_command:
                    test_command += " --export-predictions"
                if model == "ST-MEM" and mode == "Finetuning":
                    test_command = replace_entrypoint(
                        test_command,
                        base["python_environment"],
                        base["runner"],
                        f"{ROOT}/environments/lightning3/bin/python",
                        f"{ROOT}/worktrees/stmem_formal/code/main_lite.py",
                    )
                exact_test_command = f"{test_command} > {run_root}/formal_test.log 2>&1"

            rows.append({
                "execution_order": f"{sequence:02d}", "run_id": run_id,
                "dataset": dataset, "output_dim": output_dim, "model": model, "mode": mode,
                "python_environment": python_env, "runner": runner, "wrapper": wrapper,
                "pretrained_checkpoint": base["pretrained_checkpoint"],
                "initialization_source": "supervised scratch" if model in {"S4", "Net1D"} else "original accepted pretrained checkpoint",
                "precision": base["precision"], "batch_size": 64, "epochs": 100,
                "optimizer": "AdamW (--optimizer adam)", "lr": "1e-3", "weight_decay": "1e-3",
                "lr_schedule": "constant", "output_dir": output_dir, "log_path": log_path,
                "prediction_path": prediction_path, "checkpoint_dir": checkpoint_dir,
                "exact_formal_command": command, "exact_test_command": exact_test_command,
                "formal_test_route": formal_test_route,
                "optimizer_scope": optimizer_scope, "bn_guard": bn_guard,
                "gpu_gate_policy": gate_policy, "special_protection": protection,
                "status": "COMMAND_PREPARED_NOT_AUTHORIZED",
            })

    if len(rows) != 20 or sum(r["mode"] == "Finetuning" for r in rows) != 8 or sum(r["mode"] == "Frozen" for r in rows) != 6 or sum(r["mode"] == "Linear" for r in rows) != 6:
        raise RuntimeError("matrix cardinality failure")
    for row in rows:
        if "ptbxl_all" in row["exact_formal_command"] or "/PTBXL_ALL/" in row["exact_formal_command"]:
            raise RuntimeError(f"all dataset leaked into {row['run_id']}")
        if row["run_id"] not in row["exact_formal_command"]:
            raise RuntimeError(f"run id not concretized: {row['run_id']}")
        if row["output_dir"] not in row["exact_formal_command"]:
            raise RuntimeError(f"output path not concretized: {row['run_id']}")
    with target.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    with (root / "tables/PTBXL_SUB_SUPER_FORMAL_COMMAND_MATRIX.csv").open(newline="", encoding="utf-8-sig") as handle:
        source_rows = list(csv.DictReader(handle))
    build("ptbxl_sub", 23, root / "tables/PTBXL_SUB_573_ALL_MODES_COMMAND_MATRIX.csv", source_rows)
    build("ptbxl_super", 5, root / "tables/PTBXL_SUPER_871_ALL_MODES_COMMAND_MATRIX.csv", source_rows)


if __name__ == "__main__":
    main()
