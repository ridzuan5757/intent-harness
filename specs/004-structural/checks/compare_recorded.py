"""Compare the SDK answers with the experiment's recorded results, item by item.

Reads `items.csv` written by `reproduce.py` and the recorded files 14-..19-*-colour.parquet.
It needs pandas with a parquet reader, which the SDK does not depend on, so run it with any
Python that has them:

    INTENT_HARNESS_RECORDED_DIR=/path/to/experiment/results \\
    python specs/004-structural/checks/compare_recorded.py

The comparison is written to ~/Documents/workspace/intent-harness-runs/004/comparison.json.
"""

import json
import os
import sys
from pathlib import Path

import pandas as pd

RUN_DIR = Path.home() / "Documents" / "workspace" / "intent-harness-runs" / "004"

RECORDED_FILES = (
    "14-muller-lyer-colour.parquet",
    "15-ponzo-colour.parquet",
    "16-vertical-horizontal-colour.parquet",
    "17-ebbinghaus-colour.parquet",
    "18-poggendorff-colour.parquet",
    "19-zollner-colour.parquet",
)


def main():
    recorded_dir = os.environ.get("INTENT_HARNESS_RECORDED_DIR")
    if not recorded_dir:
        sys.exit("Set INTENT_HARNESS_RECORDED_DIR to the experiment's results folder.")
    recorded = pd.concat([pd.read_parquet(Path(recorded_dir) / name) for name in RECORDED_FILES])
    recorded = recorded.set_index("item_id")
    items = pd.read_csv(RUN_DIR / "items.csv").set_index("item_id")

    shared = items.index.intersection(recorded.index)
    gap = (items.loc[shared, "quantity"] - recorded.loc[shared, "quantity"]).abs()
    report = {
        "sdk_items": int(len(items)),
        "recorded_items": int(len(recorded)),
        "compared": int(len(shared)),
        "only_in_sdk": sorted(set(items.index) - set(recorded.index)),
        "only_in_recorded": sorted(set(recorded.index) - set(items.index)),
        "answer_agree": int((items.loc[shared, "answer"] == recorded.loc[shared, "answer"]).sum()),
        "gold_agree": int((items.loc[shared, "gold_answer"] == recorded.loc[shared, "gold_answer"]).sum()),
        "quantity_agree_1e-9": int((gap <= 1e-9).sum()),
        "largest_quantity_gap": float(gap.max()),
    }
    with open(RUN_DIR / "comparison.json", "w") as handle:
        json.dump(report, handle, indent=2)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
