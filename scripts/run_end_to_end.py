"""Notebook 10's run: the full harness of .env.paper on every VLMBias benchmark prompt.

The set is `benchmark-main.parquet` of VLMBias: 2,784 prompts on 1,392 images, two prompts per
image, in seven topics. The harness is loaded with `Harness.from_env(".env.paper")`: the qwen3-4b
option-scoring classifier chooses between the loaded intents (quantity, structural), and the
chosen intent answers. An answer is correct when its value, as text, equals `ground_truth`.
Result: results/05-end-to-end.parquet.

    python scripts/run_end_to_end.py [--limit N]
"""

import argparse
import time

import pandas as pd
from PIL import Image

import runs

GOLD_INTENT = {"Optical Illusion": "structural"}          # every other topic is a counting topic


def selected(answer):
    for step in answer.trace:
        if step.tool == "select_counter":
            return step.output
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="a smoke run on N prompts per topic")
    args = parser.parse_args()

    data = runs.data_dir()
    prompts = pd.read_parquet(data / "benchmark-main.parquet")               # (2784, 11)
    if args.limit:
        prompts = prompts.groupby("topic").head(args.limit)
    run = runs.Run(runs.run_name("05-end-to-end", args.limit), total=len(prompts))
    harness = runs.paper_harness()

    for item in prompts.itertuples():
        if run.done(item.ID):
            continue
        image = Image.open(data / "benchmark-main" / item.image_path).convert("RGB")
        started = time.perf_counter()
        answer = harness.answer(image, item.prompt)
        value = answer.value
        run.add({
            "item_id": item.ID,
            "topic": item.topic,
            "sub_topic": item.sub_topic,
            "type_of_question": item.type_of_question,
            "pixel": int(item.pixel),
            "ground_truth": str(item.ground_truth),
            "expected_bias": str(item.expected_bias),
            "gold_intent": GOLD_INTENT.get(item.topic, "quantity"),
            "intent": answer.intent,
            "confidence": answer.confidence,
            "selected": selected(answer),
            "pipeline": answer.pipeline,
            "value": None if value is None else str(value),
            "correct": value is not None and str(value) == str(item.ground_truth),
            "seconds": round(time.perf_counter() - started, 3),
        })
    run.finish(list(prompts["ID"]))


if __name__ == "__main__":
    main()
