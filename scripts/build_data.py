"""Build the item lists in data/ from the experiment workspace's files (run once).

The item lists record which items the paper uses, their questions and their gold answers. The
images are not copied: each image path is relative to INTENT_HARNESS_DATA_DIR.

    python scripts/build_data.py --experiment <master>/docs/counterfactual-blindness/experiments/grounded-count-harness

Sources (in the experiment workspace):
- harness/intents.py                  the ten intent definitions, in their recorded order
- results/manifest.parquet            the 388 intent prompts with the gold intent
- harness/registry.py                 the models; llava-ov-72b is left out (user decision 2026-10-09)
- results/illusion-manifest.parquet   the 396 illusion images
- results/12-gold.parquet             their gold answers and the two VLMBias prompts
- results/21-counting-gold.parquet    the 795 counting items with prompt and gold count
"""

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
LEFT_OUT_MODELS = ("llava-ov-72b",)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", required=True)
    args = parser.parse_args()
    experiment = Path(args.experiment)
    results = experiment / "results"
    out = ROOT / "data"
    out.mkdir(exist_ok=True)

    # the ten intent definitions, in order
    intents = load_module(experiment / "harness" / "intents.py", "recorded_intents")
    definitions = []
    for intent in intents.INTENTS:
        definitions.append({"key": intent["key"], "definition": intent["definition"]})
    (out / "intent-definitions.json").write_text(json.dumps(definitions, indent=2) + "\n")

    # the 388 intent prompts
    manifest = pd.read_parquet(results / "manifest.parquet")
    manifest = manifest[["item_id", "text", "source", "gold_intent", "disputed"]]
    manifest.to_parquet(out / "intent-manifest.parquet", index=False)

    # the 24 models (registry.py imports pandas only; it needs no model)
    sys.path.insert(0, str(experiment))
    registry = load_module(experiment / "harness" / "registry.py", "recorded_registry")
    models = []
    for name in registry.models_by_size():
        if name in LEFT_OUT_MODELS:
            continue
        info = registry.MODEL_REGISTRY[name]
        models.append({"model": name, "hf_id": info["hf_id"], "kind": info["kind"],
                       "dtype": info["dtype"], "size_gb": info["size_gb"]})
    (out / "models.json").write_text(json.dumps(models, indent=2) + "\n")

    # the 396 illusion images with their gold answer and prompts
    illusions = pd.read_parquet(results / "illusion-manifest.parquet")
    gold = pd.read_parquet(results / "12-gold.parquet")
    illusions = illusions[["item_id", "image_path", "gold_illusion", "condition", "instance",
                           "pixel", "edit_size"]].merge(
        gold[["item_id", "prompt_q1", "prompt_q2", "gold_answer"]], on="item_id", how="left")
    illusions.to_parquet(out / "illusion-items.parquet", index=False)

    # the 795 counting items
    counting = pd.read_parquet(results / "21-counting-gold.parquet")
    counting = counting[["item_id", "sub_topic", "split", "condition", "image_path", "figure",
                         "pixel", "target", "target_detail", "prompt", "gold_count",
                         "familiar_count"]]
    counting.to_parquet(out / "counting-items.parquet", index=False)

    print(f"intent definitions: {len(definitions)}")
    print(f"intent prompts: {len(manifest)}")
    print(f"models: {len(models)}")
    print(f"illusion images: {len(illusions)}")
    print(f"counting items: {len(counting)}")


if __name__ == "__main__":
    main()
