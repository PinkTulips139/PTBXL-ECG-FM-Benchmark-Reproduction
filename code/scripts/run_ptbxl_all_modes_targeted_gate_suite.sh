#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 || ( "$1" != "ptbxl_sub" && "$1" != "ptbxl_super" ) ]]; then
  echo "usage: $0 ptbxl_sub|ptbxl_super" >&2
  exit 64
fi

dataset="$1"
root=/root/autodl-tmp/ECG
python="$root/environments/lightning3/bin/python"
gate="$root/scripts/ptbxl_all_modes_targeted_gate.py"
outdir="$root/preparation/gates/$dataset"
mkdir -p "$outdir"
mkdir -p "$root/preparation/keops_cache"
export LIBRARY_PATH="/usr/local/cuda/targets/x86_64-linux/lib:${LIBRARY_PATH:-}"
export LD_LIBRARY_PATH="/usr/local/cuda/targets/x86_64-linux/lib:${LD_LIBRARY_PATH:-}"
export PYKEOPS_BUILD_FOLDER="$root/preparation/keops_cache"

run_gate() {
  local ordinal="$1" model="$2" mode="$3" slug="$4"
  local result="$outdir/${ordinal}_${slug}_${mode}.json"
  if [[ -f "$result" ]] && "$python" - "$result" <<'PY'
import json
import pathlib
import sys
raise SystemExit(0 if json.loads(pathlib.Path(sys.argv[1]).read_text()).get("status") == "PASS" else 1)
PY
  then
    echo "reuse PASS gate: $result"
    return 0
  fi
  "$python" "$gate" \
    --dataset "$dataset" \
    --model "$model" \
    --mode "$mode" \
    --output "$result"
}

# Fail closed and preserve the fixed 11-gate evidence order.
run_gate 01 "ECG-JEPA" finetuning ecg_jepa
run_gate 02 "ECGFounder" frozen ecg_founder
run_gate 03 "ECG-JEPA" frozen ecg_jepa
run_gate 04 "ST-MEM" frozen st_mem
run_gate 05 "MERL" frozen merl
run_gate 06 "ECGFM-KED" frozen ecgfm_ked
run_gate 07 "HuBERT-ECG" frozen hubert_ecg
run_gate 08 "MERL" linear merl
run_gate 09 "ECGFM-KED" linear ecgfm_ked
run_gate 10 "S4" finetuning s4
run_gate 11 "Net1D" finetuning net1d

"$python" - "$outdir" <<'PY'
import json
import pathlib
import sys

directory = pathlib.Path(sys.argv[1])
rows = [json.loads(path.read_text()) for path in sorted(directory.glob("[0-9][0-9]_*.json"))]
summary = {
    "gate_count": len(rows),
    "pass_count": sum(row.get("status") == "PASS" for row in rows),
    "status": "PASS" if len(rows) == 11 and all(row.get("status") == "PASS" for row in rows) else "FAIL",
    "gates": rows,
}
(directory / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(json.dumps({key: summary[key] for key in ("gate_count", "pass_count", "status")}, sort_keys=True))
PY
