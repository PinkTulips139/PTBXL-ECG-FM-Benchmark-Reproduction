"""Minimal read-only acquisition of six completed ST-MEM mapping bundles.

Only prediction NPZs (which contain targets), post-run validation, exact command,
and the sole separate formal test logs are copied.  Checkpoints, events, data,
and environments are deliberately excluded.
"""
from __future__ import annotations

import csv
import hashlib
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST_ROOT = ROOT / "execution_control" / "PTBXL_FINAL_CLOSURE" / "mapping_evidence"
OUT = ROOT / "execution_control" / "PTBXL_FINAL_CLOSURE" / "STMEM_780_775_ACQUISITION_RECORD.csv"
SSH_DIR = Path(r"C:\Users\86151\.ssh")

SPECS = [
    ("780", "connect.westc.seetacloud.com", "24159", SSH_DIR / "ecg_autodl_573", "ptbxl_sub", "Finetuning", "PTBXL_SUB_07_ST_MEM_FINETUNING_FORMAL_RETRY_03", "PTBXL_SUB", [
        ("exact_formal_command.sh", "fe4447e5c54c70f9481db5b56e09693915e2f4893d2a989d9d63e30f6beef0da"),
        ("formal_test.log", "b63a795dee2c7526b72c841afb4956d56e4c938733711e41c7dda2a0dd46d490"),
        ("post_run_validation.json", "43aa57729afe7411c0b4aee568b3256fff1d798bd3d3aabb73cf8db1e378895a"),
        ("predictions/ptbxl_sub_version_0/agg/test_0_epoch_0_agg.npz", "b8efaeea9f6b463a00e07b3d39ede80e856d737e00b414e684d2a331386b0211"),
        ("predictions/ptbxl_sub_version_0/noagg/test_0_epoch_0_noagg.npz", "21d352e8d9e657953b44d4c045cb3de2c9ffba552760967d5924c2a342f2b6a3"),
    ]),
    ("780", "connect.westc.seetacloud.com", "24159", SSH_DIR / "ecg_autodl_573", "ptbxl_sub", "Frozen", "PTBXL_SUB_08_ST_MEM_FROZEN_FORMAL", "PTBXL_SUB", [
        ("exact_formal_command.sh", "d0145983a4859c31437a783a1bba7b9d8391f1f69bc52ea14607911f4cb9e4a9"),
        ("post_run_validation.json", "9fcf82b8d98ba2edf248d184da20502bd5d6f0758369096bb911ec2510ce0f81"),
        ("predictions/ptbxl_sub_version_0/agg/test_0_epoch_100_agg.npz", "dd4040cf97536bd3fc8b4d290b49d9954f401466224a28c7e64f680c8efb6b71"),
        ("predictions/ptbxl_sub_version_0/noagg/test_0_epoch_100_noagg.npz", "803dae078b4c7e1e6cecc151e4ac42700c5a4b915d686086bf8fefcc931c4847"),
    ]),
    ("780", "connect.westc.seetacloud.com", "24159", SSH_DIR / "ecg_autodl_573", "ptbxl_sub", "Linear", "PTBXL_SUB_09_ST_MEM_LINEAR_FORMAL", "PTBXL_SUB", [
        ("exact_formal_command.sh", "e93d4184b55ded35e34e982e2278893e8b8d7922ce6c633361a818a3e8345561"),
        ("post_run_validation.json", "2c9bfb7385a76304eab54a19dd3b551d3aeb56f9ad8f56bf51e700d10648db9e"),
        ("predictions/ptbxl_sub_version_0/agg/test_0_epoch_100_agg.npz", "3c77b5508297224845fb84c1f9c7eea575b68e51672eb486af3474b61e3b7132"),
        ("predictions/ptbxl_sub_version_0/noagg/test_0_epoch_100_noagg.npz", "3deb9ddaa6f424bddf475e0136cadd0ebf22dc1b36b9e59e725e816f684108af"),
    ]),
    ("775", "connect.westc.seetacloud.com", "25176", SSH_DIR / "ecg_autodl_871", "ptbxl_super", "Finetuning", "PTBXL_SUPER_07_ST_MEM_FINETUNING_FORMAL_RETRY_03", "PTBXL_SUPER", [
        ("exact_formal_command.sh", "30babac98f37459a701208f60418c70911e0e01f4d4ec0c3db817a4ba7d089fc"),
        ("formal_test.log", "ee8b4306d9b72524abf60d83f69bfda3ccf1c6c469c40b74d02bd9c213ce40cc"),
        ("post_run_validation.json", "81ff03ba872b55ac88771e5d6eeb6a224b35999db7f370eea9fb8d2a7643af84"),
        ("predictions/ptbxl_super_version_0/agg/test_0_epoch_0_agg.npz", "f8bcd8ab5a396f9d8371041706e7c60faf87bd2fc7d1ba76ebefaf7902738e59"),
        ("predictions/ptbxl_super_version_0/noagg/test_0_epoch_0_noagg.npz", "a4f4cc7f35be808c6302167e5ce6017b0869e768c8a6bf8d743e4993c6080d3a"),
    ]),
    ("775", "connect.westc.seetacloud.com", "25176", SSH_DIR / "ecg_autodl_871", "ptbxl_super", "Frozen", "PTBXL_SUPER_08_ST_MEM_FROZEN_FORMAL", "PTBXL_SUPER", [
        ("exact_formal_command.sh", "06137476599a909f0d6f2bd71fec46e362b525369c98acbdad8e5cddfee0f876"),
        ("post_run_validation.json", "a117482c2e8358c5b444b33676861b37a96fc8c9ce5a2eea54b696ea454a0870"),
        ("predictions/ptbxl_super_version_0/agg/test_0_epoch_100_agg.npz", "0422ac3d2b6cca757c2c6ceedf105efaa9c7433cf2fdc407ffae6893b28cdf83"),
        ("predictions/ptbxl_super_version_0/noagg/test_0_epoch_100_noagg.npz", "baf18e52c255bd346e31cb71d19af8a05da38fb94d816eeaf73f4f48808eb1c5"),
    ]),
    ("775", "connect.westc.seetacloud.com", "25176", SSH_DIR / "ecg_autodl_871", "ptbxl_super", "Linear", "PTBXL_SUPER_09_ST_MEM_LINEAR_FORMAL", "PTBXL_SUPER", [
        ("exact_formal_command.sh", "905d83affd3c42e8a757b84ad04d3757fc8c3299eaa366cca65cea27799cba96"),
        ("post_run_validation.json", "4099a70e652ffefbb793d4c2bddf95bb5bcbd3bc8df6bae333ea273463d0740a"),
        ("predictions/ptbxl_super_version_0/agg/test_0_epoch_100_agg.npz", "18632f3a9bb31ed7fa49e31384a2badb5d2772684debcc9dc5de2236d7a81719"),
        ("predictions/ptbxl_super_version_0/noagg/test_0_epoch_100_noagg.npz", "c6eafaa704ecfe3174116ed36f2be8ab40ffd93458a29ad31fcf6c3045f9f5bf"),
    ]),
]

FIELDS = ["dataset", "model", "mode", "canonical_run", "instance", "remote_path", "local_path", "artifact_type", "file_size_bytes", "remote_sha256", "local_sha256", "remote_local_hash_match", "acquisition_timestamp_utc", "acquisition_method", "dedup_action"]

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def artifact_type(relative: str) -> str:
    if relative.endswith("noagg.npz"): return "RAW_WINDOW_PREDICTIONS_AND_TARGETS"
    if relative.endswith("agg.npz"): return "SAVED_AGGREGATE_PREDICTIONS_AND_TARGETS"
    if relative.endswith("post_run_validation.json"): return "FINAL_RESULT_AND_VALIDATION"
    if relative.endswith("exact_formal_command.sh"): return "RUN_MANIFEST_COMMAND"
    return "FORMAL_TEST_LOG"

def main():
    records = []; transferred = skipped = 0
    stamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    for instance, host, port, key, dataset, mode, run, family, files in SPECS:
        remote_base = f"/root/autodl-tmp/ECG/formal_runs/{family}/{run}"
        local_base = DEST_ROOT / f"instance_{instance}" / run
        for relative, remote_sha in files:
            remote_path = f"{remote_base}/{relative}"
            local_path = local_base / relative
            local_path.parent.mkdir(parents=True, exist_ok=True)
            action = "TRANSFERRED"
            if local_path.exists():
                if digest(local_path) == remote_sha:
                    action = "REUSE_EXISTING_LOCAL_COPY"
                    skipped += local_path.stat().st_size
                else:
                    local_path = local_path.with_name(local_path.name + f".conflict_{remote_sha[:12]}")
                    action = "TRANSFERRED_CONFLICT_PRESERVED"
            if action != "REUSE_EXISTING_LOCAL_COPY":
                subprocess.run(["scp", "-p", "-q", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", "-i", str(key), "-P", port, f"root@{host}:{remote_path}", str(local_path)], check=True)
                transferred += local_path.stat().st_size
            local_sha = digest(local_path)
            if local_sha != remote_sha:
                raise RuntimeError(f"HASH_MISMATCH {remote_path} {local_path}")
            records.append({"dataset": dataset, "model": "ST-MEM", "mode": mode, "canonical_run": run, "instance": instance, "remote_path": remote_path, "local_path": str(local_path.relative_to(ROOT)).replace("\\", "/"), "artifact_type": artifact_type(relative), "file_size_bytes": local_path.stat().st_size, "remote_sha256": remote_sha, "local_sha256": local_sha, "remote_local_hash_match": "PASS", "acquisition_timestamp_utc": stamp, "acquisition_method": "READ_ONLY_SCP_MINIMAL_BUNDLE", "dedup_action": action})
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(records)
    print(f"files={len(records)} transferred={transferred} skipped_by_hash={skipped}")

if __name__ == "__main__":
    main()
