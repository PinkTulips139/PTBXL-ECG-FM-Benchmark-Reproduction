#!/usr/bin/env bash
set -euo pipefail

target_host="$1"
target_port="$2"
checkpoint_dir="$3"

checkpoint_args=()
if [[ "$checkpoint_dir" != "NONE" ]]; then
  checkpoint_args+=("ECG/checkpoints/${checkpoint_dir}")
fi

tar -C /root/autodl-tmp \
  --use-compress-program=/root/miniconda3/bin/zstd \
  -cf - \
  ECG/data \
  ECG/upstream \
  ECG/execution_overlays \
  ECG/scripts \
  ECG/environments \
  ECG/worktrees \
  ECG/helpers \
  "${checkpoint_args[@]}" \
| ssh \
    -o BatchMode=yes \
    -o IdentitiesOnly=yes \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/root/emergency_worker_known_hosts \
    -i /root/emergency_transfer_ed25519 \
    -p "$target_port" \
    "root@${target_host}" \
    'mkdir -p /root/autodl-tmp && tar -C /root/autodl-tmp --use-compress-program=/root/miniconda3/bin/zstd -xpf -'

echo "TRANSFER_COMPLETE host=${target_host} port=${target_port} checkpoint=${checkpoint_dir}"
