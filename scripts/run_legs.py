"""Notebook 03's run: the quantity intent counts legs on the 2,196 animal images (1,098 pairs).

The images are the linear-probing split of VLMBias (`train-animals.parquet`, as in the
experiment). The harness is .env.paper's, with a fixed classifier that chooses `quantity`; the
question is "How many legs does this animal have?", so the selector chooses the legs counter.
The item id is the row index in `train-animals.parquet`. Result: results/03-legs.parquet.

    python scripts/run_legs.py [--limit N]
"""

import argparse
import re
import time

import pandas as pd
from PIL import Image

import runs

QUESTION = "How many legs does this animal have?"


def base_id(path: str) -> str:
    """aardvark_0_384.png and aardvark_0_edited_1_384.png -> aardvark_0"""
    file_name = path.split("/")[-1]
    return re.match(r"(.+?)(_edited_\d+)?_\d+\.png", file_name).group(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    data = runs.data_dir()
    samples = pd.read_parquet(data / "train-animals.parquet")                 # (2196, 5)
    samples["item_id"] = [str(index) for index in samples.index]
    if args.limit:
        samples = samples.head(args.limit)
    run = runs.Run(runs.run_name("03-legs", args.limit), total=len(samples))
    harness = runs.paper_harness(fixed_intent="quantity")

    for index in samples.index:
        item = samples.loc[index]
        if run.done(item["item_id"]):
            continue
        image = Image.open(data / "train-animals" / item["image_path"]).convert("RGB")
        started = time.perf_counter()
        answer = harness.answer(image, QUESTION)
        run.add({
            "item_id": item["item_id"],
            "sample": int(index),
            "name": item["name"],
            "base": base_id(item["image_path"]),
            "pixel": int(item["pixel"]),
            "image_type": item["image_type"],
            "ground_truth": int(item["ground_truth"]),
            "pipeline": answer.pipeline,
            "count": answer.value,
            "seconds": round(time.perf_counter() - started, 3),
        })
    run.finish(list(samples["item_id"]))


if __name__ == "__main__":
    main()
