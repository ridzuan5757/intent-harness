"""Notebook 06's run: the option-scoring intent classifier on the 388 prompts, for each model.

The classifier is loaded through the SDK (`intent_harness_classifiers.option_scoring`) with ten
description-only intents: the ten recorded intent definitions in data/intent-definitions.json,
in their recorded order. Each prompt goes through the classifier's `classify`, as in
`Harness.answer`. One result file per model: results/01-classifier-<model>.parquet.

    python scripts/run_classifier.py --models all            # the 24 models, smallest first
    python scripts/run_classifier.py --models qwen3-4b --limit 10

A model that fails to load is recorded in results/01-classifier-<model>.failed, and the run
continues with the next model.
"""

import argparse
import json
import time
import traceback

import runs
from intent_harness import Harness
from intent_harness.types import Result


class DescriptionIntent:
    """An intent with a key and a description only. This run never calls it."""

    required_tools = ()

    def __init__(self, key: str, description: str) -> None:
        self.key = key
        self.description = description

    def run(self, image, question, tools):
        return Result(value=None)


def load_models():
    return json.loads((runs.DATA_LISTS / "models.json").read_text())


def run_model(info: dict, manifest, limit: int, device: str) -> None:
    name = runs.run_name(f"01-classifier-{info['model']}", limit)
    run = runs.Run(name, total=len(manifest))
    if run.marker.exists():
        print(f"{name}: already complete", flush=True)
        return
    failed = run.folder / f"{name}.failed"

    harness = Harness()
    definitions = json.loads((runs.DATA_LISTS / "intent-definitions.json").read_text())
    for definition in definitions:
        harness.register_intent(DescriptionIntent(definition["key"], definition["definition"]))
    try:
        harness.load_classifier("intent_harness_classifiers.option_scoring", model=info["hf_id"],
                                device=device, dtype=info["dtype"], kind=info["kind"])
    except Exception:
        failed.write_text(traceback.format_exc())
        print(f"{name}: the model did not load; see {failed.name}", flush=True)
        return
    classifier = harness.registry.classifier
    infos = harness.registry.intent_infos()

    for item in manifest.itertuples():
        if run.done(item.item_id):
            continue
        started = time.perf_counter()
        choice = classifier.classify(item.text, infos)
        run.add({
            "item_id": item.item_id,
            "model": info["model"],
            "gold_intent": item.gold_intent,
            "predicted_intent": choice.key,
            "confidence": choice.confidence,
            "log_scores": json.dumps(classifier.last_log_scores),
            "seconds": round(time.perf_counter() - started, 4),
        })
    run.finish(list(manifest["item_id"]))
    classifier.language_model.unload()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", default="all", help="'all' or a comma-separated list of names")
    parser.add_argument("--limit", type=int, default=0, help="a smoke run on the first N prompts")
    parser.add_argument("--device", default="mps")
    args = parser.parse_args()

    models = load_models()
    if args.models != "all":
        wanted = args.models.split(",")
        chosen = []
        for info in models:
            if info["model"] in wanted:
                chosen.append(info)
        models = chosen
    manifest = runs.load_items("intent-manifest")
    if args.limit:
        manifest = manifest.head(args.limit)
    for info in models:
        started = time.time()
        run_model(info, manifest, args.limit, args.device)
        print(f"{info['model']}: {(time.time() - started) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
