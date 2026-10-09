"""Build the shipped board references and compare them with the experiment's crops (SC-003).

Run from the repository root with an environment that has pandas (the experiment's .venv):

    PYTHONPATH=. python specs/006-quantity-subtopics/checks/build_references.py \
        --experiment <master>/docs/counterfactual-blindness/experiments/grounded-count-harness \
        [--write]

The script rebuilds the crops with `build_board_references` from the same two unedited boards
the experiment uses, compares them with the experiment's `board_references()` and with the
shipped file, and writes the shipped file when `--write` is given.
"""

import argparse
import sys

import numpy as np
from PIL import Image

from intent_harness_quantity.references import (
    SHIPPED_FILE,
    build_board_references,
    load_board_references,
    save_board_references,
)
from intent_harness_tools.counting import cluster


def same(first, second):
    """True when two reference sets have the same kinds, crops and grid, exactly."""
    for board in ("chess", "xiangqi"):
        a = first[board]["references"]
        b = second[board]["references"]
        if len(a) != len(b):
            return False
        for left, right in zip(a, b):
            if left["kind"] != right["kind"] or not np.array_equal(left["feature"], right["feature"]):
                return False
    for key in ("columns", "rows"):
        if list(first["xiangqi"][key]) != list(second["xiangqi"][key]):
            return False
    return first["xiangqi"]["size"] == second["xiangqi"]["size"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    sys.path.insert(0, args.experiment)
    from harness import counting, datasets

    recorded = counting.board_references()
    gold = datasets.load_counting_gold()
    images = {}
    for key in ("chess_pieces", "xiangqi_pieces"):
        row = gold[(gold["sub_topic"] == key) & (gold["condition"] == "original")].iloc[0]
        images[key] = Image.open(datasets.image_file(row["image_path"]))
        print(key, "reference image:", row["image_path"])
    built = build_board_references(images["chess_pieces"], images["xiangqi_pieces"], cluster)

    print("chess crops:", len(built["chess"]["references"]),
          "| xiangqi crops:", len(built["xiangqi"]["references"]))
    print("SDK build equals the experiment's board_references():", same(built, recorded))
    if args.write:
        save_board_references(built)
        print("written:", SHIPPED_FILE)
    shipped = load_board_references()
    print("shipped file equals the experiment's board_references():", same(shipped, recorded))


if __name__ == "__main__":
    main()
