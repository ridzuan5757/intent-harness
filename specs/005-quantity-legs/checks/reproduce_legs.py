"""Count the legs of the 2,196 VLMBias animal images through Harness.answer.

Runs on a machine with the models in the local cache (the M3). Writes one JSON line per image to
`<out>.jsonl` as it goes, so a second run continues where the first stopped, then writes
`<out>.parquet` with every count.

    python reproduce_legs.py --data-dir <dir with train-animals.parquet> --out <path without suffix>
    python reproduce_legs.py ... --pairs 5          # smoke run: the first 5 pairs only

`--data-dir` is the folder that holds `train-animals.parquet` and the `train-animals/` images.
"""

import argparse
import json
import os
import re
import time

import pandas as pd
from PIL import Image

from intent_harness import Choice, Harness

QUESTION = "How many legs does this animal have?"


class AlwaysQuantity:
    """A classifier that always chooses the quantity intent. This check tests the pipeline only."""

    def classify(self, question, intents):
        return Choice(key="quantity", probabilities={"quantity": 1.0}, confidence=1.0)


def base_id(path):
    """aardvark_0_384.png and aardvark_0_edited_1_384.png -> aardvark_0"""
    file_name = path.split("/")[-1]
    return re.match(r"(.+?)(_edited_\d+)?_\d+\.png", file_name).group(1)


def load_samples(data_dir, pairs):
    samples = pd.read_parquet(os.path.join(data_dir, "train-animals.parquet"))   # (2196, 5)
    samples["base"] = [base_id(path) for path in samples["image_path"]]
    if pairs:
        originals = samples[samples["image_type"] == "original"].index[:pairs]
        keep = []
        for index in originals:
            base = samples.loc[index, "base"]
            pixel = samples.loc[index, "pixel"]
            group = samples[(samples["base"] == base) & (samples["pixel"] == pixel)]
            keep.extend(group.index.tolist())
        samples = samples.loc[sorted(keep)]
    return samples


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--pairs", type=int, default=0)
    args = parser.parse_args()

    samples = load_samples(args.data_dir, args.pairs)
    image_dir = os.path.join(args.data_dir, "train-animals")
    progress_path = args.out + ".jsonl"
    done = {}
    if os.path.exists(progress_path):
        with open(progress_path) as handle:
            for line in handle:
                row = json.loads(line)
                done[row["sample"]] = row
    print(f"images: {len(samples)} | already counted: {len(done)}", flush=True)

    harness = Harness()
    harness.load_tools("intent_harness_tools.grounding_dino_plugin", "intent_harness_tools.sam3_plugin")
    harness.load_intents("intent_harness_quantity.plugin")
    harness.register_classifier(AlwaysQuantity())

    start = time.time()
    counted = 0
    with open(progress_path, "a") as handle:
        for index in samples.index:
            if int(index) in done:
                continue
            image = Image.open(os.path.join(image_dir, samples.loc[index, "image_path"])).convert("RGB")
            tick = time.time()
            answer = harness.answer(image, QUESTION)
            row = {"sample": int(index), "count": int(answer.value), "pipeline": answer.pipeline,
                   "seconds": round(time.time() - tick, 3)}
            handle.write(json.dumps(row) + "\n")
            handle.flush()
            done[int(index)] = row
            counted += 1
            if counted % 100 == 0:
                rate = (time.time() - start) / counted
                left = len(samples) - len(done)
                print(f"{len(done)} of {len(samples)} | {rate:.2f} s per image | about {rate * left / 60:.0f} min left",
                      flush=True)

    rows = [done[int(index)] for index in samples.index]
    counts = pd.DataFrame(rows).merge(samples, left_on="sample", right_index=True)
    counts.to_parquet(args.out + ".parquet", index=False)
    print(f"done | {len(counts)} images | wrote {args.out}.parquet", flush=True)


if __name__ == "__main__":
    main()
