"""Check that the moved classifier keeps the recorded number (spec 003, SC-002).

Runs the option-scoring classifier through the SDK path on the 388-item intent manifest:
ten description-only intents with the ten recorded definitions, loaded in the recorded order,
then `classify` for each prompt. It compares each choice and the log scores with the recorded
result file of the experiment workspace.

Inputs (not in this repository):
  --intents   the experiment's harness/intents.py (the ten keys and definitions, in order)
  --manifest  the experiment's results/manifest.parquet
  --recorded  the experiment's results/04-choice-qwen3-4b-full.parquet
  --out       where to write the per-item results (a parquet file)

Example (on the M3):
  python reproduce_qwen3_4b.py --intents intents.py --manifest manifest.parquet \
      --recorded 04-choice-qwen3-4b-full.parquet --out sdk-qwen3-4b.parquet --limit 10
"""

import argparse
import importlib.util
import json
import time

import pandas as pd

from intent_harness import Harness
from intent_harness.types import Result


class DescriptionIntent:
    """An intent with a key and a description only. The check never runs it."""

    required_tools = ()

    def __init__(self, key, description):
        self.key = key
        self.description = description

    def run(self, image, question, tools):
        return Result(value=None)


def load_definitions(path):
    spec = importlib.util.spec_from_file_location("recorded_intents", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    pairs = []
    for intent in module.INTENTS:
        pairs.append((intent["key"], intent["definition"]))
    return pairs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--intents", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--recorded", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--model", default="Qwen/Qwen3-4B")
    parser.add_argument("--device", default="mps")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    harness = Harness()
    for key, definition in load_definitions(args.intents):
        harness.register_intent(DescriptionIntent(key, definition))
    harness.load_classifier("intent_harness_classifiers.option_scoring", model=args.model, device=args.device)
    classifier = harness.registry.classifier
    infos = harness.registry.intent_infos()

    manifest = pd.read_parquet(args.manifest)
    if args.limit:
        manifest = manifest.head(args.limit)

    rows = []
    for item in manifest.itertuples():
        started = time.perf_counter()
        choice = classifier.classify(item.text, infos)
        rows.append({
            "item_id": item.item_id,
            "gold_intent": item.gold_intent,
            "predicted_intent": choice.key,
            "confidence": choice.confidence,
            "log_scores": json.dumps(classifier.last_log_scores),
            "seconds": time.perf_counter() - started,
        })
    sdk = pd.DataFrame(rows)
    sdk.to_parquet(args.out)

    recorded = pd.read_parquet(args.recorded)[["item_id", "predicted_intent", "raw"]]
    recorded = recorded.rename(columns={"predicted_intent": "recorded_intent", "raw": "recorded_raw"})
    both = sdk.merge(recorded, on="item_id", how="left")

    largest_gap = 0.0
    for row in both.itertuples():
        mine = json.loads(row.log_scores)
        theirs = json.loads(row.recorded_raw)
        for key in mine:
            largest_gap = max(largest_gap, abs(mine[key] - theirs[key]))

    correct = int((both.predicted_intent == both.gold_intent).sum())
    same = int((both.predicted_intent == both.recorded_intent).sum())
    recorded_correct = int((both.recorded_intent == both.gold_intent).sum())
    print(f"items: {len(both)}")
    print(f"accuracy through the SDK: {correct}/{len(both)} = {correct / len(both):.3f}")
    print(f"recorded accuracy on the same items: {recorded_correct}/{len(both)} = {recorded_correct / len(both):.3f}")
    print(f"same choice as the recorded file: {same}/{len(both)}")
    print(f"largest log-score difference (recorded scores are rounded to 4 decimals): {largest_gap:.4f}")


if __name__ == "__main__":
    main()
