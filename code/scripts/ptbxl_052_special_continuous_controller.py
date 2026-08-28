#!/usr/bin/env python3
"""Fail-closed, storage-aware controller for the authorized 052 special queue.

This controller intentionally contains only execution orchestration.  It does
not alter model code, data, checkpoints, or scientific parameters.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


CONTROL_ROOT = Path("/root/autodl-tmp/ECG/execution_control/PTBXL_052_SPECIAL_CONTINUOUS_CONTROLLER")
FORMAL_ROOT = Path("/root/autodl-tmp/ECG/formal_runs")
DATA_ROOT = Path("/root/autodl-tmp")
SAFETY_BYTES = 10 * 1024**3
LOW_DISK_BYTES = SAFETY_BYTES
LOCKED_UPSTREAM = "238409835ef55358a10bbc3459dfa9aaa91ad5e5"


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def disk_record() -> dict[str, int]:
    usage = shutil.disk_usage(DATA_ROOT)
    return {"total_bytes": usage.total, "used_bytes": usage.used, "free_bytes": usage.free}


def cpc_environment_prefix() -> str:
    site = "/root/autodl-tmp/ECG/environments/common_hubert_052/lib/python3.13/site-packages/nvidia"
    libraries = [
        "cublas/lib", "cuda_cupti/lib", "cuda_nvrtc/lib", "cuda_runtime/lib",
        "cudnn/lib", "cufft/lib", "cufile/lib", "curand/lib", "cusolver/lib",
        "cusparse/lib", "nccl/lib", "nvjitlink/lib", "nvtx/lib",
    ]
    ld_library_path = ":".join(f"{site}/{part}" for part in libraries) + ":/usr/local/cuda-12.4/lib64"
    return f"env CUDA_PATH=/usr/local/cuda-12.4 LD_LIBRARY_PATH={ld_library_path}"


def command_for(*, model: str, dataset: str, mode: str, run_dir: Path) -> str:
    data = "/root/autodl-tmp/ECG/data/processed/ptb-xl/records500"
    output = run_dir / "output"
    predictions = run_dir / "predictions"
    eval_mode = {"Finetuning": "finetuning_linear", "Frozen": "frozen", "Linear": "linear"}[mode]
    if model == "ECG-CPC":
        prefix = cpc_environment_prefix()
        python = "/root/autodl-tmp/ECG/environments/common_hubert_052/bin/python"
        runner = "/root/autodl-tmp/ECG/upstream/ecg-fm-benchmarking/code/main_lite.py"
        checkpoint = "/root/autodl-tmp/ECG/checkpoints/cpc/config_last_11597276_ckpt.yaml"
        arguments = (
            f"{python} {runner} --data {data} --fs-data 500 --finetune-dataset {dataset} "
            f"--architecture cpc --input-size 2.5 --fs-model 240 --input-channels 12 "
            f"--pretrained {checkpoint} --precision 32 --epochs 100 --modality ecg --lr 0.001 "
            f"--batch-size 64 --finetune --eval-mode {eval_mode} --optimizer adam --wd 0.001 "
            f"--lr-schedule const --gpus 1 --num-nodes 1 --accumulate 1 --refresh-rate 0 "
            f"--output-path {output} --prediction-path {predictions} --export-predictions"
        )
        return f"{prefix} {arguments} > {run_dir / 'formal_training.log'} 2>&1"
    if model == "ECG-FM":
        python = "/root/autodl-tmp/ECG/environments/ecg_fm_052/bin/python"
        runner = "/root/autodl-tmp/ECG/execution_overlays/ecg_fm_py39_compat/ecg-fm-benchmarking/code/main_lite.py"
        pythonpath = "/root/autodl-tmp/ECG/execution_overlays/ecg_fm_py39_compat/ecg-fm-benchmarking/code"
        checkpoint = "/root/autodl-tmp/ECG/checkpoints/ecg_fm/mimic_iv_ecg_physionet_pretrained.pt"
        arguments = (
            f"{python} {runner} --data {data} --fs-data 500 --finetune-dataset {dataset} "
            f"--architecture ecg_fm --input-size 5 --fs-model 500 --input-channels 12 "
            f"--pretrained {checkpoint} --precision 16-mixed --epochs 100 --modality ecg --lr 0.001 "
            f"--batch-size 64 --finetune --eval-mode {eval_mode} --optimizer adam --wd 0.001 "
            f"--lr-schedule const --gpus 1 --num-nodes 1 --accumulate 1 --refresh-rate 0 "
            f"--output-path {output} --prediction-path {predictions} --export-predictions"
        )
        return f"env PYTHONPATH={pythonpath} {arguments} > {run_dir / 'formal_training.log'} 2>&1"
    raise ValueError(model)


def build_runs() -> list[dict[str, Any]]:
    specs = [
        ("PTBXL_ALL_ECG_FM_FROZEN_FORMAL_RUN_015_RETRY_01", "ECG-FM", "ptbxl_all", 71, "Frozen", 5),
        ("PTBXL_ALL_ECG_FM_LINEAR_FORMAL_RUN_016", "ECG-FM", "ptbxl_all", 71, "Linear", 5),
        ("PTBXL_SUB_ECG_CPC_FINETUNING_FORMAL_052_01", "ECG-CPC", "ptbxl_sub", 23, "Finetuning", 2),
        ("PTBXL_SUB_ECG_CPC_FROZEN_FORMAL_052_02", "ECG-CPC", "ptbxl_sub", 23, "Frozen", 1),
        ("PTBXL_SUB_ECG_CPC_LINEAR_FORMAL_052_03", "ECG-CPC", "ptbxl_sub", 23, "Linear", 1),
        ("PTBXL_SUPER_ECG_CPC_FINETUNING_FORMAL_052_04", "ECG-CPC", "ptbxl_super", 5, "Finetuning", 2),
        ("PTBXL_SUPER_ECG_CPC_FROZEN_FORMAL_052_05", "ECG-CPC", "ptbxl_super", 5, "Frozen", 1),
        ("PTBXL_SUPER_ECG_CPC_LINEAR_FORMAL_052_06", "ECG-CPC", "ptbxl_super", 5, "Linear", 1),
        ("PTBXL_SUB_ECG_FM_FINETUNING_FORMAL_052_07", "ECG-FM", "ptbxl_sub", 23, "Finetuning", 8),
        ("PTBXL_SUB_ECG_FM_FROZEN_FORMAL_052_08", "ECG-FM", "ptbxl_sub", 23, "Frozen", 5),
        ("PTBXL_SUB_ECG_FM_LINEAR_FORMAL_052_09", "ECG-FM", "ptbxl_sub", 23, "Linear", 5),
        ("PTBXL_SUPER_ECG_FM_FINETUNING_FORMAL_052_10", "ECG-FM", "ptbxl_super", 5, "Finetuning", 8),
        ("PTBXL_SUPER_ECG_FM_FROZEN_FORMAL_052_11", "ECG-FM", "ptbxl_super", 5, "Frozen", 5),
        ("PTBXL_SUPER_ECG_FM_LINEAR_FORMAL_052_12", "ECG-FM", "ptbxl_super", 5, "Linear", 5),
    ]
    runs: list[dict[str, Any]] = []
    for order, (run_id, model, dataset, output_dim, mode, expected_gib) in enumerate(specs, start=1):
        run_dir = FORMAL_ROOT / run_id
        runs.append({
            "order": order, "run_id": run_id, "model": model, "dataset": dataset,
            "output_dim": output_dim, "mode": mode, "run_dir": str(run_dir),
            "expected_artifact_bytes": expected_gib * 1024**3,
            "checkpoint": ("/root/autodl-tmp/ECG/checkpoints/cpc/config_last_11597276_ckpt.yaml"
                           if model == "ECG-CPC" else "/root/autodl-tmp/ECG/checkpoints/ecg_fm/mimic_iv_ecg_physionet_pretrained.pt"),
            "exact_command": command_for(model=model, dataset=dataset, mode=mode, run_dir=run_dir),
        })
    return runs


def verify_prerequisites() -> None:
    required = [
        Path("/root/autodl-tmp/ECG/checkpoints/cpc/config_last_11597276_ckpt.yaml"),
        Path("/root/autodl-tmp/ECG/checkpoints/cpc/last_11597276.ckpt"),
        Path("/root/autodl-tmp/ECG/checkpoints/ecg_fm/mimic_iv_ecg_physionet_pretrained.pt"),
        Path("/root/autodl-tmp/ECG/execution_overlays/ecg_fm_py39_compat/ecg-fm-benchmarking/code/main_lite.py"),
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(f"required route asset missing: {missing}")
    ecg_fm_python = "/root/autodl-tmp/ECG/environments/ecg_fm_052/bin/python"
    check = subprocess.run([ecg_fm_python, "-c", "import tensorboard"], capture_output=True, text=True)
    if check.returncode != 0:
        raise RuntimeError("ECG_FM_ENVIRONMENT_NOT_READY: tensorboard import failed")


def formal_processes() -> list[int]:
    result = subprocess.run(["ps", "-eo", "pid=,args="], capture_output=True, text=True, check=True)
    found = []
    for line in result.stdout.splitlines():
        if "main_lite.py" in line and "/root/autodl-tmp/ECG/formal_runs/" in line:
            found.append(int(line.strip().split(maxsplit=1)[0]))
    return found


def validate_run(run: dict[str, Any], return_code: int) -> dict[str, Any]:
    errors: list[str] = []
    run_dir = Path(run["run_dir"])
    log_path = run_dir / "formal_training.log"
    text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.is_file() else ""
    if return_code != 0:
        errors.append(f"return code {return_code}")
    if not text:
        errors.append("formal_training.log missing or empty")
    lowered = text.lower()
    if "traceback (most recent call last)" in lowered:
        errors.append("traceback present")
    if "cuda out of memory" in lowered or "torch.cuda.outofmemoryerror" in lowered:
        errors.append("CUDA OOM present")
    if not re.search(r"(?i)epoch\s*99(?:\D|$)", text):
        errors.append("epoch 99 evidence missing")
    output_dir = run_dir / "output"
    prediction_dir = run_dir / "predictions"
    best = sorted(output_dir.glob("**/best_model.ckpt"))
    last = sorted(output_dir.glob("**/last.ckpt"))
    if not best:
        errors.append("best checkpoint missing")
    if not last:
        errors.append("last checkpoint missing")
    if best and "best_model.ckpt" not in text:
        errors.append("best checkpoint test evidence missing")
    metric = None
    for line in text.splitlines():
        if "macro_auc_agg_test0" in line:
            values = re.findall(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", line.split("macro_auc_agg_test0", 1)[1])
            if values:
                metric = float(values[-1])
    if metric is None or not math.isfinite(metric):
        errors.append("finite primary Test Macro AUROC missing")
    aggregate = sorted(prediction_dir.glob("**/agg/*.npz"))
    raw = sorted(prediction_dir.glob("**/noagg/*.npz"))
    expected_shape = (2198, int(run["output_dim"]))
    aggregate_shapes: list[list[int]] = []
    if not aggregate:
        errors.append("aggregate prediction archive missing")
    else:
        try:
            with np.load(aggregate[-1]) as archive:
                aggregate_shapes = [list(archive[key].shape) for key in archive.files]
            if sum(tuple(shape) == expected_shape for shape in aggregate_shapes) < 2:
                errors.append(f"aggregate shape closure missing: expected {expected_shape}")
        except Exception as exc:
            errors.append(f"aggregate archive unreadable: {exc}")
    if not raw:
        errors.append("raw prediction archive missing")
    return {
        "status": "PASS" if not errors else "FAIL", "errors": errors,
        "return_code": return_code, "test_macro_auroc": metric,
        "best_checkpoint": str(best[0]) if best else None,
        "last_checkpoint": str(last[0]) if last else None,
        "aggregate_shapes": aggregate_shapes, "validated_at_utc": utcnow(),
    }


def write_state(**kwargs: Any) -> None:
    previous = {}
    state_path = CONTROL_ROOT / "controller_state.json"
    if state_path.exists():
        previous = json.loads(state_path.read_text(encoding="utf-8"))
    previous.update(kwargs)
    previous["updated_at_utc"] = utcnow()
    atomic_json(state_path, previous)


def fail_closed(reason: str, **details: Any) -> None:
    write_state(status="FAILED_CLOSED", stop_reason=reason, controller_process_alive=False, **details)
    (CONTROL_ROOT / "STOP_REASON.txt").write_text(
        f"FAILED_CLOSED\nTIME={utcnow()}\nREASON={reason}\nNO_RETRY=YES\n", encoding="utf-8"
    )


def main() -> int:
    CONTROL_ROOT.mkdir(parents=True, exist_ok=False)
    lock_handle = (CONTROL_ROOT / "controller.lock").open("w", encoding="utf-8")
    try:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return 2
    try:
        if formal_processes():
            raise RuntimeError(f"pre-existing formal process(es): {formal_processes()}")
        verify_prerequisites()
        runs = build_runs()
        atomic_json(CONTROL_ROOT / "queue_manifest.json", {
            "authorization": "AUTHORIZE_052_CONTINUOUS_SPECIAL_QUEUE_WITH_STORAGE_GUARD=YES",
            "locked_upstream_commit": LOCKED_UPSTREAM,
            "scientific_semantics_changed": "NO", "auto_shutdown": "NO",
            "safety_margin_bytes": SAFETY_BYTES, "runs": runs,
        })
        (CONTROL_ROOT / "controller.pid").write_text(f"{os.getpid()}\n", encoding="utf-8")
        (CONTROL_ROOT / "provenance.json").write_text(json.dumps({
            "controller_script_sha256": sha256(Path(__file__)),
            "ecg_fm_tensorboard_dependency": "tensorboard==2.21.0",
            "locked_upstream_modified": "NO", "scientific_semantics_changed": "NO",
        }, indent=2) + "\n", encoding="utf-8")
        completed: list[str] = []
        write_state(status="STARTED", controller_pid=os.getpid(), controller_process_alive=True,
                    completed_run_ids=completed, queue_length=len(runs), auto_shutdown="NO")
        for run in runs:
            current_disk = disk_record()
            preflight = {**current_disk, "expected_run_artifact_bytes": run["expected_artifact_bytes"],
                         "safety_margin_bytes": SAFETY_BYTES, "passed": current_disk["free_bytes"] >= run["expected_artifact_bytes"] + SAFETY_BYTES}
            atomic_json(CONTROL_ROOT / f"disk_preflight_{run['order']:02d}_{run['run_id']}.json", preflight)
            if not preflight["passed"]:
                fail_closed("DISK_CAPACITY_BLOCKED", current_run_id=run["run_id"], disk_preflight=preflight, completed_run_ids=completed)
                return 3
            run_dir = Path(run["run_dir"])
            if run_dir.exists() and any(run_dir.iterdir()):
                fail_closed("TARGET_RUN_DIRECTORY_ALREADY_NONEMPTY", current_run_id=run["run_id"], completed_run_ids=completed)
                return 3
            run_dir.mkdir(parents=True, exist_ok=False)
            (run_dir / "exact_command.txt").write_text(run["exact_command"] + "\n", encoding="utf-8")
            atomic_json(run_dir / "formal_execution_metadata.json", {
                **run, "scientific_semantics_changed": "NO", "locked_upstream_modified": "NO",
                "storage_preflight": preflight, "launch_time_utc": utcnow(),
            })
            process = subprocess.Popen(run["exact_command"], shell=True, executable="/bin/bash", start_new_session=True)
            write_state(status="RUNNING", current_run_id=run["run_id"], current_model=run["model"],
                        current_mode=run["mode"], current_training_pid=process.pid, completed_run_ids=completed,
                        disk_preflight=preflight)
            low_disk = False
            while process.poll() is None:
                observed = disk_record()
                if observed["free_bytes"] < LOW_DISK_BYTES:
                    low_disk = True
                    write_state(status="LOW_DISK_CURRENT_RUN_COMPLETION_ALLOWED", current_run_id=run["run_id"],
                                current_training_pid=process.pid, completed_run_ids=completed, disk_observation=observed)
                time.sleep(30)
            validation = validate_run(run, int(process.returncode))
            atomic_json(run_dir / "completion_validation.json", validation)
            if validation["status"] != "PASS":
                fail_closed("RUN_VALIDATION_FAILED", current_run_id=run["run_id"], validation=validation, completed_run_ids=completed)
                return 4
            completed.append(run["run_id"])
            if low_disk:
                fail_closed("FAIL_CLOSED_STOP_BEFORE_NEXT_RUN_LOW_DISK", current_run_id=None,
                            completed_run_ids=completed, last_validation=validation, disk_observation=disk_record())
                return 5
            write_state(status="RUN_VERIFIED", current_run_id=None, current_training_pid=None,
                        completed_run_ids=completed, last_validation=validation)
        write_state(status="STOPPED_AT_AUTHORIZED_BOUNDARY", current_run_id=None, current_training_pid=None,
                    completed_run_ids=completed, controller_process_alive=False)
        (CONTROL_ROOT / "STOP_AT_AUTHORIZED_BOUNDARY.txt").write_text(
            f"STOP_AT_AUTHORIZED_BOUNDARY\nTIME={utcnow()}\nAUTO_SHUTDOWN=NO\n", encoding="utf-8"
        )
        return 0
    except Exception as exc:
        fail_closed(f"UNEXPECTED_CONTROLLER_EXCEPTION: {type(exc).__name__}: {exc}")
        return 9


if __name__ == "__main__":
    raise SystemExit(main())
