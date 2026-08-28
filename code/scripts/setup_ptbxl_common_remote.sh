#!/usr/bin/env bash
set -euo pipefail

ROOT=/root/autodl-tmp/ECG
REPO=/root/autodl-tmp/ECG/upstream/ecg-fm-benchmarking
COMMIT=238409835ef55358a10bbc3459dfa9aaa91ad5e5

mkdir -p "$ROOT/worktrees" "$ROOT/audits/st_mem"
cp "$ROOT/execution_overlays/st_mem/STMEM_119_FORMAL_TRAIN_LAUNCH.py" \
  "$ROOT/audits/st_mem/STMEM_119_FORMAL_TRAIN_LAUNCH.py"

add_worktree() {
  local target=$1
  if [[ ! -e "$target/.git" ]]; then
    git -C "$REPO" worktree add -q --detach "$target" "$COMMIT"
  fi
}

apply_once() {
  local target=$1
  local patch=$2
  if git -C "$target" apply --check "$patch" 2>/dev/null; then
    git -C "$target" apply "$patch"
  elif git -C "$target" apply --reverse --check "$patch" 2>/dev/null; then
    : # already applied
  else
    echo "PATCH_STATE_INVALID target=$target patch=$patch" >&2
    exit 1
  fi
}

add_worktree "$ROOT/worktrees/common"
add_worktree "$ROOT/worktrees/ecgfm_ked"
add_worktree "$ROOT/worktrees/hubert_ecg"
add_worktree "$ROOT/worktrees/stmem_formal"

apply_once "$ROOT/worktrees/common" \
  "$ROOT/execution_overlays/st_mem/STMEM_119_RUNTIME_RESAMPLING_APPLIED.patch"

apply_once "$ROOT/worktrees/ecgfm_ked" \
  "$ROOT/execution_overlays/st_mem/STMEM_119_RUNTIME_RESAMPLING_APPLIED.patch"
apply_once "$ROOT/worktrees/ecgfm_ked" \
  "$ROOT/execution_overlays/ecgfm_ked/git_diff_prelaunch.patch"

apply_once "$ROOT/worktrees/hubert_ecg" \
  "$ROOT/execution_overlays/st_mem/STMEM_119_RUNTIME_RESAMPLING_APPLIED.patch"
apply_once "$ROOT/worktrees/hubert_ecg" \
  "$ROOT/execution_overlays/ecgfm_ked/git_diff_prelaunch.patch"

apply_once "$ROOT/worktrees/stmem_formal" \
  "$ROOT/execution_overlays/st_mem/STMEM_119_RUNTIME_RESAMPLING_APPLIED.patch"
apply_once "$ROOT/worktrees/stmem_formal" \
  "$ROOT/execution_overlays/st_mem/STMEM_119_OPTIMIZER_GROUPING_APPLIED.patch"
# The accepted launcher provides runtime module stubs; the archived proposed
# import-isolation patch is retained as evidence but is not mechanically valid.

for target in common ecgfm_ked hubert_ecg stmem_formal; do
  test "$(git -C "$ROOT/worktrees/$target" rev-parse HEAD)" = "$COMMIT"
  echo "WORKTREE=$target"
  git -C "$ROOT/worktrees/$target" status --short
done

# Portability links preserve the previously accepted exact command paths.
mkdir -p \
  /root/autodl-tmp/ecg_ptbxl_reproduction/conda_envs \
  /root/autodl-tmp/ecg_ptbxl_reproduction/data/processed/ptb-xl \
  /root/autodl-tmp/ecg_ptbxl_reproduction/checkpoints \
  /root/autodl-tmp/envs \
  /root/autodl-tmp/processed/ptb-xl \
  /root/autodl-tmp/checkpoints \
  "$ROOT/assets"
ln -sfn "$ROOT/environments/lightning3" \
  /root/autodl-tmp/ecg_ptbxl_reproduction/conda_envs/lightning3
ln -sfn "$ROOT/worktrees/common" \
  /root/autodl-tmp/ecg_ptbxl_reproduction/ecg-fm-benchmarking
ln -sfn "$ROOT/data/processed/ptb-xl/records500" \
  /root/autodl-tmp/ecg_ptbxl_reproduction/data/processed/ptb-xl/records500
ln -sfn "$ROOT/checkpoints/ecg_jepa" \
  /root/autodl-tmp/ecg_ptbxl_reproduction/checkpoints/ecg_jepa
ln -sfn "$ROOT/checkpoints/merl" \
  /root/autodl-tmp/ecg_ptbxl_reproduction/checkpoints/merl
ln -sfn "$ROOT/environments/lightning3" /root/autodl-tmp/envs/ecgfounder
ln -sfn "$ROOT/data/processed/ptb-xl/records500" \
  /root/autodl-tmp/processed/ptb-xl/records500
ln -sfn "$ROOT/checkpoints/ecg_founder" /root/autodl-tmp/checkpoints/ecg_founder
ln -sfn "$ROOT/environments/lightning3" "$ROOT/environments/ecgfm_ked_195"
ln -sfn "$ROOT/environments/lightning3" "$ROOT/environments/hubert_ecg"
ln -sfn "$ROOT/checkpoints/st_mem" "$ROOT/assets/st_mem"
