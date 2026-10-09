"""A small sample per counting sub-topic through `Harness.answer`, against the recorded counts
(SC-002).

Run from the repository root with an environment that has pandas:

    PYTHONPATH=. python specs/006-quantity-subtopics/checks/check_counters.py \
        --experiment <master>/docs/counterfactual-blindness/experiments/grounded-count-harness \
        --data <master>/docs/counterfactual-blindness/findings/week2/dataset/data \
        --sub-topics pixel            # or: logos, or a comma-separated list

The sample per sub-topic: up to 2 items the experiment counted wrong, then items it counted
right, to 5 items (item ids in sorted order). Car logos: 1 wrong and 1 right item for each of
its three targets. The recorded count is the `count` column of
`results/23..27-*.parquet` (-1 = not found, None here). The question is the item's first prompt.
The intent classifier is a fixed one that always chooses `quantity`; the selector chooses the
counter from the question, as in use.
"""

import argparse
import glob
import os

import pandas as pd
from PIL import Image

from intent_harness import Harness
from intent_harness.types import Choice

PIXEL = ["chess_grid", "sudoku_grid", "xiangqi_grid", "go_grid", "chess_pieces", "xiangqi_pieces",
         "flag_stars", "flag_stripes", "dice", "tally"]
LOGOS = ["car_logos", "shoe_logos"]
PER_SUB_TOPIC = 5
WRONG_PER_SUB_TOPIC = 2


class QuantityClassifier:
    """Always chooses the quantity intent."""

    def classify(self, question, intents):
        probabilities = {}
        for info in intents:
            probabilities[info.key] = 1.0 if info.key == "quantity" else 0.0
        return Choice(key="quantity", probabilities=probabilities, confidence=1.0)


def harness():
    h = Harness()
    h.load_tools("intent_harness_tools.counting_plugin",
                 "intent_harness_tools.grounding_dino_plugin",
                 "intent_harness_tools.sam3_plugin")
    h.load_intents("intent_harness_quantity.plugin")
    h.register_classifier(QuantityClassifier())
    return h


def sample(recorded, sub_topic):
    group = recorded[recorded["sub_topic"] == sub_topic].sort_values("item_id")
    if sub_topic == "car_logos":
        # three targets (overlapping circles, prongs, star points): 1 wrong and 1 right of each
        parts = []
        for target, by_target in group.groupby("target"):
            parts.append(by_target[~by_target["correct"]].head(1))
            parts.append(by_target[by_target["correct"]].head(1))
        return pd.concat(parts)
    wrong = group[~group["correct"]].head(WRONG_PER_SUB_TOPIC)
    right = group[group["correct"]].head(PER_SUB_TOPIC - len(wrong))
    return pd.concat([wrong, right])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--sub-topics", default="pixel")
    parser.add_argument("--out", default=os.path.expanduser("~/Documents/workspace/intent-harness-runs/006"))
    args = parser.parse_args()

    if args.sub_topics == "pixel":
        chosen = PIXEL
    elif args.sub_topics == "logos":
        chosen = LOGOS
    else:
        chosen = args.sub_topics.split(",")

    results = os.path.join(args.experiment, "results")
    recorded = pd.concat([pd.read_parquet(path) for path in sorted(glob.glob(os.path.join(results, "2[3-7]-*.parquet")))])
    gold = pd.read_parquet(os.path.join(results, "21-counting-gold.parquet"))
    recorded = recorded.merge(gold[["item_id", "image_path", "prompt"]], on="item_id", how="left")

    h = harness()
    rows = []
    for sub_topic in chosen:
        for _, item in sample(recorded, sub_topic).iterrows():
            image = Image.open(os.path.join(args.data, item["image_path"])).convert("RGB")
            answer = h.answer(image, item["prompt"])
            recorded_count = None if int(item["count"]) == -1 else int(item["count"])
            rows.append({
                "item_id": item["item_id"], "sub_topic": sub_topic, "split": item["split"],
                "recorded_correct": bool(item["correct"]), "recorded_count": recorded_count,
                "pipeline": answer.pipeline, "count": answer.value,
                "same": answer.pipeline == sub_topic and answer.value == recorded_count,
            })
            print(f"{sub_topic:15s} {item['item_id'][:60]:60s} recorded {recorded_count} sdk {answer.value}"
                  f" {'same' if rows[-1]['same'] else 'DIFFERENT'}", flush=True)
    table = pd.DataFrame(rows)
    print()
    print(table.groupby("sub_topic")["same"].agg(["sum", "count"]).to_string())
    print("same count:", int(table["same"].sum()), "of", len(table))
    os.makedirs(args.out, exist_ok=True)
    table.to_parquet(os.path.join(args.out, f"counters-{args.sub_topics.replace(',', '_')}.parquet"))


if __name__ == "__main__":
    main()
