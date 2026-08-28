#!/usr/bin/env python3
import argparse
import json
import pickle
from pathlib import Path

import pandas as pd


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--dataset", choices=("ptbxl_sub", "ptbxl_super"), required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    root = Path(args.data)
    df = pd.read_pickle(root / "df.pkl")
    with (root / "lbl_itos.pkl").open("rb") as handle:
        labels = pickle.load(handle)
    required = [
        "label_diag_subclass",
        "label_diag_subclass_filtered_numeric",
        "label_diag_superclass",
        "label_diag_superclass_filtered_numeric",
        "strat_fold",
        "patient_id",
    ]
    missing = [column for column in required if column not in df.columns]
    train = df[df.strat_fold.between(1, 8)]
    val = df[df.strat_fold == 9]
    test = df[df.strat_fold == 10]
    patient_sets = [set(frame.patient_id.tolist()) for frame in (train, val, test)]
    overlap = len(patient_sets[0] & patient_sets[1]) + len(patient_sets[0] & patient_sets[2]) + len(patient_sets[1] & patient_sets[2])
    label_key = "label_diag_subclass" if args.dataset == "ptbxl_sub" else "label_diag_superclass"
    output_dim = len(labels[label_key])
    expected_dim = 23 if args.dataset == "ptbxl_sub" else 5
    result = {
        "dataset": args.dataset,
        "missing_columns": missing,
        "train_records": len(train),
        "val_records": len(val),
        "test_records": len(test),
        "patient_overlap": overlap,
        "output_dim": output_dim,
        "expected_output_dim": expected_dim,
    }
    result["ready"] = (
        not missing
        and len(train) == 17418
        and len(val) == 2183
        and len(test) == 2198
        and overlap == 0
        and output_dim == expected_dim
    )
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
