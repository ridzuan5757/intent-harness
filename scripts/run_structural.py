"""Notebook 02's run: the structural intent on the 396 VLMBias illusion images.

The harness is .env.paper's, with a fixed classifier that chooses `structural`, so the table
measures the illusion naming and the measurement pipelines only. The question is the item's
first VLMBias prompt (the intent does not read it). Result: results/02-structural.parquet.

    python scripts/run_structural.py [--limit N]
"""

import argparse
import time

from PIL import Image

import runs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    items = runs.load_items("illusion-items")
    if args.limit:
        items = items.head(args.limit)
    run = runs.Run(runs.run_name("02-structural", args.limit), total=len(items))
    harness = runs.paper_harness(fixed_intent="structural")
    data = runs.data_dir()

    for item in items.itertuples():
        if run.done(item.item_id):
            continue
        image = Image.open(data / item.image_path)
        started = time.perf_counter()
        answer = harness.answer(image, item.prompt_q1)
        run.add({
            "item_id": item.item_id,
            "gold_illusion": item.gold_illusion,
            "condition": item.condition,
            "pixel": int(item.pixel),
            "edit_size": float(item.edit_size),
            "gold_answer": item.gold_answer,
            "named": answer.pipeline,
            "answer": answer.value,
            "quantity": runs.step_value(answer, "decide", "quantity"),
            "tolerance": runs.step_value(answer, "decide", "tolerance"),
            "correct": answer.value == item.gold_answer,
            "steps": len(answer.trace),
            "seconds": round(time.perf_counter() - started, 4),
        })
    run.finish(list(items["item_id"]))


if __name__ == "__main__":
    main()
