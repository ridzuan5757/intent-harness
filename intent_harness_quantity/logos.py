"""Counters for the logo sub-topics: car logos and shoe logos.

The rules and constants are those of the experiment (grounded-count-harness, harness/counting.py,
`count_logo`, spec 004), unchanged. The experiment read SAM 3 regions from a cache made by
`scripts/sam3_logo_masks.py`; here the counter calls the registered tool `segment_concept` with
the same concepts and minimum score, and turns each region into the cache's form: a pixel box
(top, bottom, left, right) around the mask and the mask cropped to that box. Each counter returns
the count, or None when its region is not found.
"""

import numpy as np

from intent_harness_quantity.targets import read_target

MIN_SCORE = 0.05                       # the cache's minimum region score
CAR_CONCEPTS = ("car logo", "emblem")  # the cache's car concepts, in this order
SHOE_CONCEPT = "shoe"                  # the cache's shoe concept used by the counter
CAR_REGION_MIN_SCORE = 0.2
SHOE_REGION_MIN_SCORE = 0.3


def region_crop(region):
    """A `segment_concept` region -> (box, mask crop, score), box = (top, bottom, left, right)
    in pixels around the mask, as the experiment's cache stored it; None for an empty mask."""
    mask = region["mask"]
    rows, cols = np.nonzero(mask)
    if len(rows) == 0:
        return None
    top, bottom = int(rows.min()), int(rows.max()) + 1
    left, right = int(cols.min()), int(cols.max()) + 1
    return {"score": float(region["score"]), "box": (top, bottom, left, right),
            "mask": mask[top:bottom, left:right]}


def concept_regions(image, concept, tools):
    """The regions of one concept in the cache's form, in the model's order."""
    regions = []
    for region in tools["segment_concept"](image, concept, min_score=MIN_SCORE):
        cropped = region_crop(region)
        if cropped is not None:
            regions.append(cropped)
    return regions


def _bright_runs(values, level):
    """Runs of values above `level` along a 1-D profile."""
    above = values > level
    count = 0
    previous = False
    for value in above:
        if value and not previous:
            count += 1
        previous = bool(value)
    return count


def _centre_col(region):
    return (region["box"][2] + region["box"][3]) / 2.0


class CarLogoCounter:
    """The best "car logo" / "emblem" region; star points and prongs from the region's bright
    pixels; overlapping circles from bright runs across the region's centre row (each ring crosses
    it twice)."""

    name = "car_logos"
    required_tools = ("segment_concept", "luminance", "radial_peaks")

    def count(self, image, question, tools):
        rule, target, detail = read_target(question)
        best = None
        for concept in CAR_CONCEPTS:
            for region in concept_regions(image, concept, tools):
                if region["score"] >= CAR_REGION_MIN_SCORE and (best is None or region["score"] > best["score"]):
                    best = region
        if best is None:
            return None
        brightness = tools["luminance"](image)
        top, bottom, left, right = best["box"]
        mask = best["mask"]
        crop = brightness[top:bottom, left:right]
        inside = crop[mask]
        level = float(np.percentile(inside, 70)) if len(inside) else 255.0
        bright = mask & (crop > level)
        if bright.sum() < 10:
            return None
        if target == "overlapping circles":
            middle = crop.shape[0] // 2
            runs = _bright_runs(np.where(mask[middle], crop[middle], 0), level)
            return int(round(runs / 2.0))
        if target == "prongs":
            row = max(0, int(round(0.3 * crop.shape[0])))
            runs = _bright_runs(np.where(mask[row], crop[row], 0), level)
            if runs <= 0:
                return None
            return runs
        rows, cols = np.nonzero(bright)
        centre_row = (crop.shape[0] - 1) / 2.0
        centre_col = (crop.shape[1] - 1) / 2.0
        radius = min(crop.shape[0], crop.shape[1]) / 2.0
        inner = np.hypot(rows - centre_row, cols - centre_col) <= 0.75 * radius
        peaks = tools["radial_peaks"](rows[inner], cols[inner]) if inner.sum() >= 10 else 0
        if peaks <= 0:
            return None
        return peaks


class ShoeLogoCounter:
    """The leftmost "shoe" region; stripes or curves of the asked colour inside it, as separate
    elongated, slanted shapes."""

    name = "shoe_logos"
    required_tools = ("segment_concept", "luminance", "group_shapes", "fit_line")

    def count(self, image, question, tools):
        rule, target, detail = read_target(question)
        shoes = []
        for region in concept_regions(image, SHOE_CONCEPT, tools):
            if region["score"] >= SHOE_REGION_MIN_SCORE:
                shoes.append(region)
        if len(shoes) == 0:
            return None
        brightness = tools["luminance"](image)
        left_shoe = min(shoes, key=_centre_col)
        top, bottom, left, right = left_shoe["box"]
        mask = left_shoe["mask"]
        crop = brightness[top:bottom, left:right]
        colour = detail.split(" ")[0]
        if colour == "black":
            marks = mask & (crop < 60)
        else:
            marks = mask & (crop > 190)
        shapes = tools["group_shapes"](marks, min_pixels=max(6, int(0.002 * mask.sum())))
        slanted = 0
        for shape in shapes:
            line = tools["fit_line"](shape)
            top_s, left_s, bottom_s, right_s = shape["bbox"]
            long_side = max(bottom_s - top_s, right_s - left_s) + 1
            short_side = min(bottom_s - top_s, right_s - left_s) + 1
            if long_side >= 1.5 * short_side and 35 <= abs(line["angle_deg"]) <= 85:
                slanted += 1
        return slanted
