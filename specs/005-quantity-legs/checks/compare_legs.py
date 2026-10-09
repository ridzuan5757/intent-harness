"""Compare the SDK leg counts with the experiment's recorded counts.

    python compare_legs.py --sdk <out>.parquet --recorded <grounded-count-harness>/results/07-full-counts.parquet

Prints the summary of notebook 07 (originals correct, edited correct, clean pairs, edited higher,
same, lower) for both, and the per-image agreement.
"""

import argparse

import pandas as pd


def pair_summary(counts):
    """counts: one row per image with base, pixel, image_type, ground_truth, count."""
    originals = counts[counts["image_type"] == "original"].set_index(["base", "pixel"])
    edited = counts[counts["image_type"] == "edited"].set_index(["base", "pixel"])
    edited = edited.loc[originals.index]
    original_ok = originals["count"] == originals["ground_truth"]
    edited_ok = edited["count"].values == edited["ground_truth"].values
    higher = int((edited["count"].values > originals["count"].values).sum())
    lower = int((edited["count"].values < originals["count"].values).sum())
    return {
        "pairs": len(originals),
        "originals_correct": round(float(original_ok.mean()), 4),
        "edited_correct": round(float(edited_ok.mean()), 4),
        "clean_pairs": int((original_ok.values & edited_ok).sum()),
        "higher": higher,
        "same": len(originals) - higher - lower,
        "lower": lower,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sdk", required=True)
    parser.add_argument("--recorded", required=True)
    args = parser.parse_args()

    sdk = pd.read_parquet(args.sdk)
    recorded = pd.read_parquet(args.recorded)
    recorded = recorded[(recorded["arm"] == "sam3") & (recorded["merge"] == "nms+nested")]
    recorded = recorded[recorded["sample"].isin(sdk["sample"])]

    joined = sdk[["sample", "count"]].merge(
        recorded[["sample", "count", "base", "pixel", "image_type", "ground_truth"]],
        on="sample", suffixes=("_sdk", "_recorded"))
    agree = joined["count_sdk"] == joined["count_recorded"]
    print(f"images compared: {len(joined)} | same count: {int(agree.sum())} ({agree.mean():.4f})")
    differences = joined.loc[~agree, "count_sdk"] - joined.loc[~agree, "count_recorded"]
    print("SDK minus recorded, where they differ:", differences.value_counts().sort_index().to_dict())

    rows = []
    for label, column in [("recorded", "count_recorded"), ("sdk", "count_sdk")]:
        table = joined.rename(columns={column: "count"})
        row = {"source": label}
        row.update(pair_summary(table))
        rows.append(row)
    print(pd.DataFrame(rows).to_string(index=False))
    seconds = sdk["seconds"]
    print(f"seconds per image: mean {seconds.mean():.2f}, total {seconds.sum() / 3600:.2f} h")


if __name__ == "__main__":
    main()
