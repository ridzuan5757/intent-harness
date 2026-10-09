"""The region helpers of the SAM 3 tools, on masks drawn in the test."""

import numpy as np

from intent_harness_tools.sam3 import (
    keep_smaller_regions,
    mask_to_box,
    remove_duplicate_regions,
    small_mask,
)

SIZE = 256


def rectangle(row0, col0, row1, col1, size=SIZE):
    mask = np.zeros((size, size), dtype=bool)
    mask[row0:row1, col0:col1] = True
    return mask


def region(mask, score):
    return {"box": mask_to_box(mask), "score": score, "mask": mask}


def test_mask_to_box_uses_fractions_and_exclusive_end():
    box = mask_to_box(rectangle(64, 32, 128, 96))
    assert box == [32 / SIZE, 64 / SIZE, 96 / SIZE, 128 / SIZE]


def test_mask_to_box_of_empty_mask_is_none():
    assert mask_to_box(np.zeros((8, 8), dtype=bool)) is None


def test_small_mask_long_side():
    reduced = small_mask(np.ones((300, 600), dtype=bool))
    assert reduced.shape == (64, 128)


def test_keep_smaller_regions_applies_size_rule_and_sorts():
    animal = [0.0, 0.0, 1.0, 1.0]
    big = region(rectangle(0, 0, 200, 200), 0.9)          # 0.61 of the image: too big
    leg_a = region(rectangle(10, 10, 60, 30), 0.5)
    leg_b = region(rectangle(100, 100, 150, 120), 0.8)
    kept = keep_smaller_regions([big, leg_a, leg_b], animal, fraction=0.5)
    assert [r["score"] for r in kept] == [0.8, 0.5]


def test_keep_smaller_regions_limit():
    animal = [0.0, 0.0, 1.0, 1.0]
    regions = [region(rectangle(i, i, i + 4, i + 4), 0.1 + i / 1000) for i in range(0, 200)]
    kept = keep_smaller_regions(regions, animal, max_regions=150)
    assert len(kept) == 150
    assert kept[0]["score"] == max(r["score"] for r in regions)


def test_duplicates_by_iou():
    first = region(rectangle(0, 0, 100, 40), 0.9)
    shifted = region(rectangle(5, 0, 105, 40), 0.8)        # IoU about 0.9
    other = region(rectangle(150, 150, 250, 190), 0.7)
    kept = remove_duplicate_regions([first, shifted, other], threshold=0.48)
    assert [r["score"] for r in kept] == [0.9, 0.7]


def test_nested_rule_drops_a_region_inside_a_kept_one():
    outer = region(rectangle(0, 0, 200, 60), 0.9)
    inner = region(rectangle(10, 10, 60, 50), 0.8)         # fully inside, IoU below 0.5
    kept_nested = remove_duplicate_regions([outer, inner], threshold=0.48, nested=True)
    kept_plain = remove_duplicate_regions([outer, inner], threshold=0.48, nested=False)
    assert len(kept_nested) == 1
    assert len(kept_plain) == 2


def test_threshold_stops_the_walk():
    a = region(rectangle(0, 0, 40, 40), 0.9)
    b = region(rectangle(100, 100, 140, 140), 0.47)
    c = region(rectangle(200, 200, 240, 240), 0.9)         # after a low score: not reached
    kept = remove_duplicate_regions([a, b, c], threshold=0.48)
    assert len(kept) == 1


def test_no_regions_counts_zero():
    assert remove_duplicate_regions([], threshold=0.48) == []
