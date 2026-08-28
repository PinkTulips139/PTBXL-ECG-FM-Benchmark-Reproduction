#!/usr/bin/env bash
set -euo pipefail

old_controller_pid="$1"
matrix="$2"
state_dir="$3"
python=/root/autodl-tmp/ECG/environments/lightning3/bin/python
controller=/root/autodl-tmp/ECG/preparation/ptbxl_emergency_worker_controller.py

while kill -0 "$old_controller_pid" 2>/dev/null; do
  sleep 20
done

exec "$python" "$controller" \
  --matrix "$matrix" \
  --state-dir "$state_dir" \
  --resume-trained-first-row
