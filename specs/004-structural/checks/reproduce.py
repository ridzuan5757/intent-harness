"""Reproduce the recorded structural numbers through the SDK.

Run from the repository root:

    INTENT_HARNESS_VLMBIAS_DIR=/path/to/benchmark-main \
    .venv/bin/python specs/004-structural/checks/reproduce.py

`INTENT_HARNESS_VLMBIAS_DIR` is the `benchmark-main` folder of the VLMBias dataset. Outputs go
to ~/Documents/workspace/intent-harness-runs/004/: `items.csv` (one row per image) and
`report.json`. `compare_recorded.py` then compares `items.csv` with the experiment's recorded
result files.
"""

import csv
import json
import os
import re
import sys
from pathlib import Path

from PIL import Image

from intent_harness import Choice, Harness
from intent_harness_structural import PAPER_KEYS
from intent_harness_structural.illusions import folder_to_key

OUTPUT_DIR = Path.home() / "Documents" / "workspace" / "intent-harness-runs" / "004"

# Notebook 13 section 10: quantity of the first original figure of each illusion (4 decimals).
NOTEBOOK_13_SECTION_10 = {
    "ebbinghaus": {384: 0.0000, 768: 0.0000, 1152: 0.0000},
    "muller_lyer": {384: 0.0583, 768: 0.0302, 1152: 0.0203},
    "poggendorff": {384: 0.0012, 768: 0.0004, 1152: 0.0002},
    "ponzo": {384: 0.0000, 768: 0.0000, 1152: 0.0000},
    "vertical_horizontal": {384: 0.0104, 768: 0.0000, 1152: 0.0000},
    "zollner": {384: 0.0000, 768: 0.0000, 1152: 0.0000},
}

RECORDED_ACCURACY = {
    "muller_lyer": (36, 36, 36, 36),
    "ponzo": (36, 36, 24, 36),
    "vertical_horizontal": (18, 18, 18, 18),
    "ebbinghaus": (36, 36, 36, 36),
    "poggendorff": (36, 36, 36, 36),
    "zollner": (36, 36, 36, 36),
}

FILE_PATTERN = re.compile(r"^([A-Za-z]+_\d+)_.*_px(\d+)\.png$")


class StructuralOnly:
    """A fixed classifier: every question goes to the structural intent."""

    def classify(self, question, intents):
        return Choice(key="structural", probabilities={"structural": 1.0}, confidence=1.0)


def list_items(benchmark_dir):
    """The 396 illusion images: item id, illusion, condition, gold answer, pixel size, path."""
    root = Path(benchmark_dir) / "vlms-are-biased-notitle"
    items = []
    for folder, key in folder_to_key().items():
        for path in sorted((root / folder / "images").glob("*.png")):
            match = FILE_PATTERN.match(path.name)
            if match is None:
                raise ValueError(f"unexpected file name: {path.name}")
            instance, pixel = match.group(1), int(match.group(2))
            original = "_diff0_" in path.name
            items.append({
                "item_id": f"{instance}_notitle_px{pixel}",
                "instance": instance,
                "illusion": key,
                "condition": "original" if original else "edited",
                "gold_answer": "Yes" if original else "No",
                "pixel": pixel,
                "path": str(path),
            })
    return items


def build_harness():
    harness = Harness()
    harness.load_tools("intent_harness_tools.measurement_plugin")
    harness.load_intents("intent_harness_structural.plugin")
    harness.register_classifier(StructuralOnly())
    return harness


def decide_quantity(answer):
    """The quantity from the `decide` step of the trace, or None."""
    for step in answer.trace:
        if step.tool == "decide":
            return float(step.inputs["quantity"])
    return None


def run(benchmark_dir):
    harness = build_harness()
    items = list_items(benchmark_dir)
    rows = []
    for item in items:
        image = Image.open(item["path"])
        answer = harness.answer(image, "")
        rows.append({
            **item,
            "named": answer.pipeline,
            "answer": answer.value,
            "quantity": decide_quantity(answer),
            "correct": answer.value == item["gold_answer"],
            "steps": len(answer.trace),
        })

    report = {"n_items": len(rows)}
    report["named_correctly"] = sum(1 for row in rows if row["named"] == row["illusion"])

    accuracy = {}
    for key in PAPER_KEYS:
        part = [row for row in rows if row["illusion"] == key]
        originals = [row for row in part if row["condition"] == "original"]
        edited = [row for row in part if row["condition"] == "edited"]
        accuracy[key] = (sum(row["correct"] for row in originals), len(originals),
                         sum(row["correct"] for row in edited), len(edited))
    report["accuracy"] = accuracy
    report["accuracy_matches_recorded"] = accuracy == RECORDED_ACCURACY

    # Notebook 13 section 10: the first original instance of each illusion at three sizes.
    section_10 = {}
    section_10_ok = True
    for key in PAPER_KEYS:
        originals = [row for row in rows if row["illusion"] == key and row["condition"] == "original"]
        first = sorted({row["instance"] for row in originals})[0]
        section_10[key] = {}
        for row in originals:
            if row["instance"] != first:
                continue
            measured = round(abs(row["quantity"]), 4)
            section_10[key][row["pixel"]] = measured
            if measured != NOTEBOOK_13_SECTION_10[key][row["pixel"]]:
                section_10_ok = False
    report["notebook_13_section_10"] = section_10
    report["notebook_13_section_10_matches"] = section_10_ok

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_DIR / "items.csv", "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    with open(OUTPUT_DIR / "report.json", "w") as handle:
        json.dump(report, handle, indent=2, default=str)
    return report


def main():
    benchmark_dir = os.environ.get("INTENT_HARNESS_VLMBIAS_DIR")
    if not benchmark_dir:
        sys.exit("Set INTENT_HARNESS_VLMBIAS_DIR to the VLMBias benchmark-main folder.")
    report = run(benchmark_dir)
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
