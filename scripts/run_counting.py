"""Notebook 04's run: the quantity intent on the 795 VLMBias counting items (192 development,
603 evaluation) of the twelve sub-topics.

The harness is .env.paper's, with a fixed classifier that chooses `quantity`. The question is the
item's VLMBias prompt, so the selector chooses the counter from the question, as in use. The
selector's choice is read from the trace. Result: results/04-counting.parquet.

    python scripts/run_counting.py [--limit N] [--sub-topics a,b]
"""

import argparse
import time

from PIL import Image

import runs


def selected(answer):
    """The counter that the selector chose, from the trace."""
    for step in answer.trace:
        if step.tool == "select_counter":
            return step.output
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--sub-topics", default="", help="a smoke run on these sub-topics only")
    args = parser.parse_args()

    items = runs.load_items("counting-items")
    name = "04-counting"
    if args.sub_topics:
        items = items[items["sub_topic"].isin(args.sub_topics.split(","))]
        name = f"04-counting-{args.sub_topics.replace(',', '_')}"
    if args.limit:
        items = items.groupby("sub_topic").head(args.limit)
    run = runs.Run(runs.run_name(name, args.limit), total=len(items))
    harness = runs.paper_harness(fixed_intent="quantity")
    data = runs.data_dir()

    for item in items.itertuples():
        if run.done(item.item_id):
            continue
        image = Image.open(data / item.image_path).convert("RGB")
        started = time.perf_counter()
        answer = harness.answer(image, item.prompt)
        run.add({
            "item_id": item.item_id,
            "sub_topic": item.sub_topic,
            "split": item.split,
            "target": item.target,
            "gold_count": int(item.gold_count),
            "familiar_count": int(item.familiar_count),
            "selected": selected(answer),
            "pipeline": answer.pipeline,
            "count": answer.value,
            "correct": answer.value == int(item.gold_count),
            "seconds": round(time.perf_counter() - started, 3),
        })
    run.finish(list(items["item_id"]))


if __name__ == "__main__":
    main()
