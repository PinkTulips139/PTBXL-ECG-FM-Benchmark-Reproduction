#!/usr/bin/env python3
"""Exact ECG-JEPA PTB-XL batch-64 FP32 forward/backward resource gate."""

import argparse
import hashlib
import json
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

import torch


LOCKED_COMMIT = "238409835ef55358a10bbc3459dfa9aaa91ad5e5"
EXPECTED_CHECKPOINT_SHA256 = (
    "61334869f905a7d6de32bc573c60024eaf6efba7c35c0e45fc2ea7d52b6ff66e"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--dataset", choices=("ptbxl_sub", "ptbxl_super"), required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = Path(args.checkpoint)
    result = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "locked_commit": LOCKED_COMMIT,
        "dataset": args.dataset,
        "expected_output_dim": 23 if args.dataset == "ptbxl_sub" else 5,
        "batch_size": 64,
        "precision": "FP32",
        "preprocessing": {
            "duration_seconds": 10,
            "sample_rate_hz": 250,
            "selected_channels": ["I", "II", "V1", "V2", "V3", "V4", "V5", "V6"],
        },
        "forward": "NOT_RUN",
        "bce_with_logits": "NOT_RUN",
        "backward": "NOT_RUN",
        "optimizer_step": "NO",
        "status": "FAIL",
    }

    try:
        actual_sha = sha256(checkpoint)
        result["checkpoint"] = str(checkpoint)
        result["checkpoint_sha256"] = actual_sha
        if actual_sha != EXPECTED_CHECKPOINT_SHA256:
            raise RuntimeError(f"checkpoint SHA256 mismatch: {actual_sha}")

        code_dir = Path(args.repo) / "code"
        sys.path.insert(0, str(code_dir))
        from main_lite import add_application_specific_args, add_default_args, add_model_specific_args
        from main_lite_ecg import Main_Lite_ECG

        project_parser = add_application_specific_args(
            add_model_specific_args(add_default_args())
        )
        hparams = project_parser.parse_args(
            [
                "--data", args.data,
                "--fs-data", "500",
                "--finetune-dataset", args.dataset,
                "--architecture", "ecg_jepa",
                "--input-size", "10",
                "--fs-model", "250",
                "--input-channels", "8",
                "--pretrained", str(checkpoint),
                "--precision", "32",
                "--epochs", "100",
                "--modality", "ecg",
                "--lr", "0.001",
                "--wd", "0.001",
                "--optimizer", "adam",
                "--batch-size", "64",
                "--finetune",
                "--eval-mode", "finetuning_linear",
                "--gpus", "1",
                "--lr-schedule", "const",
            ]
        )
        hparams.executable = "main_lite_ecg"
        hparams.revision = LOCKED_COMMIT

        model = Main_Lite_ECG(hparams)
        model.setup("fit")
        batch = next(iter(model.train_dataloader()))
        if int(batch["seq"].shape[0]) != 64:
            raise RuntimeError(f"unexpected batch size: {batch['seq'].shape}")

        torch.set_default_dtype(torch.float32)
        model = model.cuda().float().train()
        seq = batch["seq"].cuda(non_blocking=False).float()
        targets = batch["label"].cuda(non_blocking=False).float()
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()

        logits = model(seq)
        result["forward"] = "PASS"
        result["input_shape"] = list(seq.shape)
        result["output_shape"] = list(logits.shape)
        if logits.shape != targets.shape:
            raise RuntimeError(
                f"logit/target shape mismatch: {tuple(logits.shape)} vs {tuple(targets.shape)}"
            )
        loss = torch.nn.functional.binary_cross_entropy_with_logits(logits, targets)
        result["bce_with_logits"] = "PASS"
        result["loss"] = float(loss.detach().cpu())
        loss.backward()
        torch.cuda.synchronize()
        result["backward"] = "PASS"
        result["peak_gpu_memory_bytes"] = int(torch.cuda.max_memory_allocated())
        result["peak_gpu_memory_gib"] = round(
            result["peak_gpu_memory_bytes"] / (1024 ** 3), 3
        )
        result["peak_gpu_reserved_bytes"] = int(torch.cuda.max_memory_reserved())
        result["optimizer_step"] = "NO"
        result["status"] = "PASS"
        rc = 0
    except torch.cuda.OutOfMemoryError as exc:
        result["oom"] = "YES"
        result["error"] = str(exc)
        result["traceback"] = traceback.format_exc()
        result["peak_gpu_memory_bytes"] = int(torch.cuda.max_memory_allocated())
        result["peak_gpu_memory_gib"] = round(
            result["peak_gpu_memory_bytes"] / (1024 ** 3), 3
        )
        rc = 2
    except Exception as exc:
        result["oom"] = "NO"
        result["error"] = str(exc)
        result["traceback"] = traceback.format_exc()
        rc = 1

    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
