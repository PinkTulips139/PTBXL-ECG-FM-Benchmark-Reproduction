#!/usr/bin/env python3
"""One real PTB-XL batch gate for the unified sub/super all-modes readiness."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

import torch
from torch import nn


LOCKED_COMMIT = "238409835ef55358a10bbc3459dfa9aaa91ad5e5"

CONFIG = {
    "ECGFounder": dict(architecture="ecg_founder", input_size=2.5, fs_model=500, input_channels=12, precision="32", checkpoint="ecg_founder/12_lead_ECGFounder.pth", worktree="common"),
    "ECG-JEPA": dict(architecture="ecg_jepa", input_size=10, fs_model=250, input_channels=8, precision="32", checkpoint="ecg_jepa/multiblock_epoch100.pth", worktree="common"),
    "ST-MEM": dict(architecture="st_mem", input_size=2.4, fs_model=250, input_channels=12, precision="16-mixed", checkpoint="st_mem/st_mem_vit_base_full.pth", worktree="stmem_formal"),
    "MERL": dict(architecture="merl", input_size=2.5, fs_model=500, input_channels=12, precision="32", checkpoint="merl/res18_best_encoder.pth", worktree="common", extra=["--merl-backbone", "resnet"]),
    "ECGFM-KED": dict(architecture="ecgfm_ked", input_size=10, fs_model=500, input_channels=12, precision="16-mixed", checkpoint="ecgfm_ked/best_valid_all_increase_with_augment_epoch_3.pt", worktree="ecgfm_ked"),
    "HuBERT-ECG": dict(architecture="hubert_ecg", input_size=5, fs_model=100, input_channels=12, precision="16-mixed", checkpoint="hubert_ecg/hubert_ecg_base.safetensors", worktree="hubert_ecg"),
    "S4": dict(architecture="s4", input_size=2.5, fs_model=100, input_channels=12, precision="32", checkpoint=None, worktree="common", extra=["--s4-n", "8", "--s4-h", "512", "--s4-layers", "4"]),
    "Net1D": dict(architecture="net1d", input_size=2.5, fs_model=500, input_channels=12, precision="32", checkpoint=None, worktree="common"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def install_bn_guard(wrapper_class: type[nn.Module]) -> None:
    def guarded_train(self: nn.Module, mode: bool = True) -> nn.Module:
        nn.Module.train(self, mode)
        if getattr(self, "eval_mode", None) in {"frozen", "linear"}:
            self.model.eval()
        return self

    wrapper_class.train = guarded_train


def find_optimizer(value):
    if isinstance(value, torch.optim.Optimizer):
        return value
    if isinstance(value, dict):
        for child in value.values():
            found = find_optimizer(child)
            if found is not None:
                return found
    if isinstance(value, (list, tuple)):
        for child in value:
            found = find_optimizer(child)
            if found is not None:
                return found
    return None


def core_module(wrapper: nn.Module, model_name: str) -> nn.Module:
    if model_name == "ECG-JEPA":
        return wrapper.encoder
    if model_name == "ST-MEM":
        return wrapper.model.encoder
    return wrapper.model


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="/root/autodl-tmp/ECG")
    parser.add_argument("--dataset", choices=("ptbxl_sub", "ptbxl_super"), required=True)
    parser.add_argument("--model", choices=tuple(CONFIG), required=True)
    parser.add_argument("--mode", choices=("finetuning", "frozen", "linear"), required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    expected_dim = 23 if args.dataset == "ptbxl_sub" else 5
    root = Path(args.root)
    cfg = CONFIG[args.model]
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "locked_commit": LOCKED_COMMIT,
        "dataset": args.dataset,
        "output_dim": expected_dim,
        "model": args.model,
        "mode": args.mode,
        "batch_size": 64,
        "precision": "FP32" if cfg["precision"] == "32" else cfg["precision"],
        "forward": "NOT_RUN",
        "bce_with_logits": "NOT_RUN",
        "backward": "NOT_RUN",
        "optimizer_step": "NO",
        "status": "FAIL",
    }

    try:
        repo = root / "worktrees" / cfg["worktree"]
        actual_commit = __import__("subprocess").check_output(
            ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
        ).strip()
        if actual_commit != LOCKED_COMMIT:
            raise RuntimeError(f"worktree commit mismatch: {actual_commit}")

        checkpoint = None
        if cfg["checkpoint"]:
            checkpoint = root / "checkpoints" / cfg["checkpoint"]
            if not checkpoint.is_file():
                raise FileNotFoundError(checkpoint)
            result["checkpoint"] = str(checkpoint)
            result["checkpoint_sha256"] = sha256(checkpoint)
        else:
            result["checkpoint"] = "SCRATCH"

        code_dir = repo / "code"
        sys.path.insert(0, str(code_dir))
        from main_lite import add_application_specific_args, add_default_args, add_model_specific_args
        from main_lite_ecg import Main_Lite_ECG
        if args.model in {"ECGFounder", "MERL", "ECGFM-KED"} and args.mode in {"frozen", "linear"}:
            from clinical_ts.models.fm_ecg import ECGFounderWrapper, EcgFmKEDWrapper, MerlWrapper
            guarded = {"ECGFounder": ECGFounderWrapper, "MERL": MerlWrapper, "ECGFM-KED": EcgFmKEDWrapper}
            install_bn_guard(guarded[args.model])
            result["bn_guard"] = "INSTALLED"
        else:
            result["bn_guard"] = "NOT_REQUIRED"

        project_parser = add_application_specific_args(add_model_specific_args(add_default_args()))
        eval_mode = "finetuning_linear" if args.mode == "finetuning" else args.mode
        cli = [
            "--data", str(root / "data/processed/ptb-xl/records500"),
            "--fs-data", "500",
            "--finetune-dataset", args.dataset,
            "--architecture", cfg["architecture"],
            "--input-size", str(cfg["input_size"]),
            "--fs-model", str(cfg["fs_model"]),
            "--input-channels", str(cfg["input_channels"]),
            "--precision", cfg["precision"],
            "--epochs", "100",
            "--modality", "ecg",
            "--lr", "0.001",
            "--wd", "0.001",
            "--optimizer", "adam",
            "--batch-size", "64",
            "--finetune",
            "--eval-mode", eval_mode,
            "--gpus", "1",
            "--lr-schedule", "const",
            "--accumulate", "1",
        ]
        if checkpoint is not None:
            cli += ["--pretrained", str(checkpoint)]
        cli += cfg.get("extra", [])
        hparams = project_parser.parse_args(cli)
        hparams.executable = "main_lite_ecg"
        hparams.revision = LOCKED_COMMIT

        pl_model = Main_Lite_ECG(hparams)
        pl_model.setup("fit")
        batch = next(iter(pl_model.train_dataloader()))
        if batch["seq"].shape[0] != 64:
            raise RuntimeError(f"unexpected batch size: {tuple(batch['seq'].shape)}")

        wrapper = pl_model.model
        if args.mode in {"frozen", "linear"}:
            wrapper.train(True)
            head_ids = {id(p) for p in wrapper.head.parameters()}
            optimizer_config = pl_model.configure_optimizers()
            optimizer = find_optimizer(optimizer_config)
            if optimizer is None:
                raise RuntimeError("optimizer not found")
            optimizer_ids = {id(p) for group in optimizer.param_groups for p in group["params"]}
            core = core_module(wrapper, args.model)
            encoder_ids = {id(p) for p in core.parameters()}
            result["head_class"] = type(wrapper.head).__name__
            result["optimizer_parameter_count"] = sum(p.numel() for group in optimizer.param_groups for p in group["params"])
            result["optimizer_encoder_parameter_count"] = sum(
                p.numel() for group in optimizer.param_groups for p in group["params"] if id(p) in encoder_ids
            )
            result["encoder_requires_grad_parameter_count"] = sum(p.numel() for p in core.parameters() if p.requires_grad)
            result["optimizer_exactly_head"] = optimizer_ids == head_ids
            if result["optimizer_encoder_parameter_count"] != 0 or not result["optimizer_exactly_head"]:
                raise RuntimeError("optimizer is not active-head-only")
            if result["encoder_requires_grad_parameter_count"] != 0:
                raise RuntimeError("encoder has trainable parameters")
            if args.mode == "frozen":
                if type(wrapper.head).__name__ != "LearnableQueryAttentionPoolingHead":
                    raise RuntimeError("frozen head class mismatch")
                attention = wrapper.head.head
                result["learnable_query_count"] = int(attention.query.shape[0])
                result["attention_heads"] = int(attention.num_heads)
                result["attention_bias"] = bool(attention.bias)
                if (result["learnable_query_count"], result["attention_heads"], result["attention_bias"]) != (1, 16, False):
                    raise RuntimeError("frozen attention head contract mismatch")
            else:
                if not isinstance(wrapper.head, nn.Linear) or wrapper.head.out_features != expected_dim:
                    raise RuntimeError("linear head contract mismatch")

            bn_modules = [module for module in core.modules() if isinstance(module, nn.modules.batchnorm._BatchNorm)]
            result["encoder_bn_count"] = len(bn_modules)
            result["encoder_bn_training_count"] = sum(int(module.training) for module in bn_modules)
            if result["encoder_bn_training_count"] != 0:
                raise RuntimeError("encoder BatchNorm re-entered training mode")
            bn_before = []
        else:
            bn_modules = []
            bn_before = []

        pl_model = pl_model.cuda().train()
        if args.mode in {"frozen", "linear"}:
            bn_before = [(module.running_mean.detach().clone(), module.running_var.detach().clone()) for module in bn_modules]
        seq = batch["seq"].cuda().float()
        targets = batch["label"].cuda().float()
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()
        mixed = cfg["precision"] == "16-mixed"
        with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=mixed):
            logits = pl_model(seq)
            result["forward"] = "PASS"
            if logits.shape != targets.shape:
                raise RuntimeError(f"shape mismatch: {tuple(logits.shape)} vs {tuple(targets.shape)}")
            loss = torch.nn.functional.binary_cross_entropy_with_logits(logits, targets)
            result["bce_with_logits"] = "PASS"
        scaler = torch.amp.GradScaler("cuda", enabled=mixed)
        scaler.scale(loss).backward()
        torch.cuda.synchronize()
        result["backward"] = "PASS"
        result["loss"] = float(loss.detach().cpu())
        result["input_shape"] = list(seq.shape)
        result["output_shape"] = list(logits.shape)
        result["peak_gpu_memory_bytes"] = int(torch.cuda.max_memory_allocated())
        result["peak_gpu_memory_gib"] = round(result["peak_gpu_memory_bytes"] / 1024**3, 3)
        result["peak_gpu_reserved_bytes"] = int(torch.cuda.max_memory_reserved())

        if args.mode in {"frozen", "linear"}:
            result["encoder_bn_buffers_unchanged"] = all(
                torch.equal(module.running_mean, before_mean)
                and torch.equal(module.running_var, before_var)
                for module, (before_mean, before_var) in zip(bn_modules, bn_before)
            )
            if not result["encoder_bn_buffers_unchanged"]:
                raise RuntimeError("encoder BatchNorm buffers changed")
            if args.model == "ST-MEM":
                head_ids = {id(p) for p in wrapper.head.parameters()}
                encoder_ids = {id(p) for p in wrapper.model.encoder.parameters()}
                auxiliary = [p for p in wrapper.model.parameters() if id(p) not in head_ids and id(p) not in encoder_ids]
                result["unused_auxiliary_parameter_count"] = sum(p.numel() for p in auxiliary)
                result["unused_auxiliary_in_optimizer"] = any(id(p) in optimizer_ids for p in auxiliary)
                result["unused_auxiliary_grad_non_none_count"] = sum(p.numel() for p in auxiliary if p.grad is not None)
                if result["unused_auxiliary_in_optimizer"] or result["unused_auxiliary_grad_non_none_count"] != 0:
                    raise RuntimeError("ST-MEM unused auxiliary contract violated")

        result["optimizer_step"] = "NO"
        result["status"] = "PASS"
        rc = 0
    except torch.cuda.OutOfMemoryError as exc:
        result["oom"] = "YES"
        result["error"] = str(exc)
        result["traceback"] = traceback.format_exc()
        result["peak_gpu_memory_bytes"] = int(torch.cuda.max_memory_allocated())
        result["peak_gpu_memory_gib"] = round(result["peak_gpu_memory_bytes"] / 1024**3, 3)
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
