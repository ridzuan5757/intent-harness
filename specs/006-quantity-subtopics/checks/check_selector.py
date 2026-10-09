"""The counter selector on every VLMBias counting prompt, against the gold sub-topic (SC-001).

Run from the repository root with an environment that has pandas:

    PYTHONPATH=. python specs/006-quantity-subtopics/checks/check_selector.py \
        --data <master>/docs/counterfactual-blindness/findings/week2/dataset/data

Every prompt of `benchmark-main.parquet` and `benchmark-original.parquet` is used, except the
illusion prompts and the identification prompts ("What ... is this?"). The gold sub-topic is the
benchmark's own sub-topic, mapped to the counter names (animal prompts: `legs`). The selector
gets the prompt and the prompt's image (it reads only the image size).
"""

import argparse
import os

import pandas as pd
from PIL import Image

from intent_harness_quantity.selector import select_counter

MAIN_SUB_TOPICS = {
    "Animal Add Legs": "legs", "Chess Pieces": "chess_pieces", "Xiangqi Pieces": "xiangqi_pieces",
    "Flags 2D Stars": "flag_stars", "Flags 2D Stripes": "flag_stripes", "Chess Grid": "chess_grid",
    "Go Grid": "go_grid", "Sudoku Grid": "sudoku_grid", "Xiangqi Grid": "xiangqi_grid",
    "Car Logos": "car_logos", "Shoe Logos": "shoe_logos", "Dice Pattern": "dice",
    "Tally Pattern": "tally",
}


def original_gold(sub_topic, prompt):
    if sub_topic in MAIN_SUB_TOPICS:
        return MAIN_SUB_TOPICS[sub_topic]
    if sub_topic == "animal":
        return "legs"
    if sub_topic == "flags":
        return "flag_stars" if "stars" in prompt else "flag_stripes"
    if sub_topic == "cars":
        return "car_logos"
    if sub_topic == "shoes":
        return "shoe_logos"
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--out", default=os.path.expanduser("~/Documents/workspace/intent-harness-runs/006"))
    args = parser.parse_args()

    rows = []
    sizes = {}
    for file_name, split_dir in [("benchmark-main.parquet", "benchmark-main"),
                                 ("benchmark-original.parquet", "benchmark-original")]:
        table = pd.read_parquet(os.path.join(args.data, file_name),
                                columns=["topic", "sub_topic", "prompt", "image_path"])
        for index in range(len(table)):
            topic = table.loc[index, "topic"]
            prompt = table.loc[index, "prompt"]
            if topic == "Optical Illusion" or prompt.startswith("What "):
                continue
            if split_dir == "benchmark-main":
                gold = MAIN_SUB_TOPICS.get(table.loc[index, "sub_topic"])
            else:
                gold = original_gold(table.loc[index, "sub_topic"], prompt)
            path = os.path.join(args.data, split_dir, table.loc[index, "image_path"])
            if path not in sizes:
                with Image.open(path) as image:
                    sizes[path] = image.size
            rows.append({"split": split_dir, "gold": gold, "prompt": prompt, "path": path})

    class Size:
        def __init__(self, size):
            self.size = size

    for row in rows:
        row["chosen"] = select_counter(Size(sizes[row["path"]]), row["prompt"])
        row["right"] = row["chosen"] == row["gold"]
    table = pd.DataFrame(rows)
    print("prompts:", len(table), "| images:", len(sizes))
    print("selector right:", int(table["right"].sum()), "of", len(table),
          f"({table['right'].mean():.4f})")
    summary = table.groupby(["gold"])["right"].agg(["sum", "count"])
    print(summary.to_string())
    wrong = table[~table["right"]]
    if len(wrong):
        print(wrong[["split", "gold", "chosen", "prompt"]].drop_duplicates().to_string())
    os.makedirs(args.out, exist_ok=True)
    table.to_parquet(os.path.join(args.out, "selector.parquet"))


if __name__ == "__main__":
    main()
