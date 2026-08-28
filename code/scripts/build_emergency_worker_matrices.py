#!/usr/bin/env python3
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tables" / "emergency_workers"
OUT.mkdir(parents=True, exist_ok=True)

SPECS = {
    "SUB1": ("PTBXL_SUB_573_ALL_MODES_COMMAND_MATRIX.csv", range(10, 13)),
    "SUB2": ("PTBXL_SUB_573_ALL_MODES_COMMAND_MATRIX.csv", range(13, 16)),
    "SUB3": ("PTBXL_SUB_573_ALL_MODES_COMMAND_MATRIX.csv", range(16, 19)),
    "SUB4": ("PTBXL_SUB_573_ALL_MODES_COMMAND_MATRIX.csv", range(19, 21)),
    "SUPER1": ("PTBXL_SUPER_871_ALL_MODES_COMMAND_MATRIX.csv", range(10, 13)),
    "SUPER2": ("PTBXL_SUPER_871_ALL_MODES_COMMAND_MATRIX.csv", range(13, 16)),
    "SUPER3": ("PTBXL_SUPER_871_ALL_MODES_COMMAND_MATRIX.csv", range(16, 19)),
    "SUPER4": ("PTBXL_SUPER_871_ALL_MODES_COMMAND_MATRIX.csv", range(19, 21)),
}

for worker, (source_name, orders) in SPECS.items():
    source = ROOT / "tables" / source_name
    with source.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
        fields = list(rows[0])
    selected = [row.copy() for row in rows if int(row["execution_order"]) in orders]
    for bundle_order, row in enumerate(selected, 1):
        old_id = row["run_id"]
        new_id = f"{old_id}_{worker}"
        for key, value in row.items():
            if isinstance(value, str):
                row[key] = value.replace(old_id, new_id)
        row["run_id"] = new_id
        row["execution_order"] = str(bundle_order)
        row["status"] = "AUTHORIZED_EMERGENCY_WORKER"
    target = OUT / f"{worker}_FORMAL_COMMAND_MATRIX.csv"
    with target.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(selected)
    print(f"{worker}={target.name} rows={len(selected)}")
