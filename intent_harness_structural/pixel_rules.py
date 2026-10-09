"""The illusion classifier by pixel rules.

Seven pixel features and seven ordered rules, written from the class descriptions and frozen
(`rules_hash`) before any benchmark image was scored. The first rule whose test holds gives the
class. Moved unchanged from the experiment workspace (`harness/classifiers.py`,
`PixelRuleClassifier`). On the 396 VLMBias illusion images the rules name every image
correctly.
"""

import hashlib
import json

import numpy as np
from scipy import ndimage

PIXEL_THRESHOLDS = {
    "red": {"r_min": 180, "g_max": 90, "b_max": 90},
    "grey": {"centre": 128, "spread": 12, "channel_gap": 4},
    "dark": {"max": 100},
    "long_run_fraction": 0.08,          # of the width (rows) or the height (columns)
    "component_min_fraction": 0.00005,  # of the pixel count, floor 10 pixels
    "component_min_floor": 10,
}

# Ordered. The first rule whose test holds gives the class.
PIXEL_RULES = [
    {"order": 1, "key": "ebbinghaus", "test": "red_fraction > 0.001"},
    {"order": 2, "key": "poggendorff", "test": "grey_fraction > 0.02"},
    {"order": 3, "key": "vertical_horizontal",
     "test": "vertical_lines >= 1 and horizontal_lines >= 1 and diagonal_fraction < 0.10"},
    {"order": 4, "key": "zollner", "test": "horizontal_lines >= 1 and diagonal_components >= 20"},
    {"order": 5, "key": "ponzo", "test": "horizontal_lines >= 2 and diagonal_component_height >= 0.60"},
    {"order": 6, "key": "muller_lyer", "test": "horizontal_lines >= 2"},
    {"order": 7, "key": "none", "test": "otherwise"},
]

FEATURE_NAMES = ["red_fraction", "grey_fraction", "horizontal_lines", "vertical_lines", "diagonal_fraction",
                 "diagonal_components", "diagonal_component_height"]


def rules_hash():
    """SHA-256 of the rule list and the thresholds: the record that the rules were frozen."""
    text = json.dumps({"rules": PIXEL_RULES, "thresholds": PIXEL_THRESHOLDS}, sort_keys=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _long_runs_along_rows(mask, min_length):
    """True where a pixel lies in a run of True pixels, inside its row, of at least
    `min_length` pixels. mask: (H, W) bool."""
    height, width = mask.shape
    padded = np.zeros((height, width + 2), dtype=np.int8)
    padded[:, 1:-1] = mask
    changes = np.diff(padded, axis=1)              # +1 where a run starts, -1 after it ends
    result = np.zeros((height, width), dtype=bool)
    for row in range(height):
        starts = np.where(changes[row] == 1)[0]
        ends = np.where(changes[row] == -1)[0]
        for start, end in zip(starts, ends):
            if end - start >= min_length:
                result[row, start:end] = True
    return result


def _count_groups(flags):
    """How many groups of adjacent True values a 1-D boolean array holds."""
    labels, count = ndimage.label(flags.astype(np.int8))
    return int(count)


def pixel_features(image):
    """The seven pixel features for one PIL image."""
    rgb = np.asarray(image.convert("RGB")).astype(np.int16)     # (H, W, 3)
    height, width = rgb.shape[0], rgb.shape[1]
    red_channel = rgb[:, :, 0]
    green_channel = rgb[:, :, 1]
    blue_channel = rgb[:, :, 2]

    red_rule = PIXEL_THRESHOLDS["red"]
    red = (red_channel > red_rule["r_min"]) & (green_channel < red_rule["g_max"]) & (blue_channel < red_rule["b_max"])
    grey_rule = PIXEL_THRESHOLDS["grey"]
    grey = ((np.abs(red_channel - grey_rule["centre"]) < grey_rule["spread"])
            & (np.abs(red_channel - green_channel) < grey_rule["channel_gap"])
            & (np.abs(green_channel - blue_channel) < grey_rule["channel_gap"]))
    dark_max = PIXEL_THRESHOLDS["dark"]["max"]
    dark = (red_channel < dark_max) & (green_channel < dark_max) & (blue_channel < dark_max)

    min_horizontal = int(round(PIXEL_THRESHOLDS["long_run_fraction"] * width))
    min_vertical = int(round(PIXEL_THRESHOLDS["long_run_fraction"] * height))
    in_horizontal_run = _long_runs_along_rows(dark, min_horizontal)           # (H, W)
    in_vertical_run = _long_runs_along_rows(dark.T, min_vertical).T           # (H, W)
    horizontal_lines = _count_groups(in_horizontal_run.any(axis=1))           # groups of rows
    vertical_lines = _count_groups(in_vertical_run.any(axis=0))               # groups of columns

    diagonal = dark & ~in_horizontal_run & ~in_vertical_run
    n_dark = int(dark.sum())
    diagonal_fraction = float(diagonal.sum()) / n_dark if n_dark > 0 else 0.0

    labels, n_components = ndimage.label(diagonal, structure=np.ones((3, 3)))
    min_pixels = max(PIXEL_THRESHOLDS["component_min_floor"],
                     int(round(PIXEL_THRESHOLDS["component_min_fraction"] * height * width)))
    kept_components = 0
    tallest = 0
    for label in range(1, n_components + 1):
        component = labels == label
        if int(component.sum()) < min_pixels:
            continue
        kept_components += 1
        rows_present = np.where(component.any(axis=1))[0]
        tallest = max(tallest, int(rows_present.max() - rows_present.min() + 1))

    return {
        "red_fraction": float(red.mean()),
        "grey_fraction": float(grey.mean()),
        "horizontal_lines": horizontal_lines,
        "vertical_lines": vertical_lines,
        "diagonal_fraction": diagonal_fraction,
        "diagonal_components": kept_components,
        "diagonal_component_height": tallest / height,
    }


def matched_rules(features):
    """The keys of every rule whose test holds, in rule order. The first is the class."""
    matched = []
    if features["red_fraction"] > 0.001:
        matched.append("ebbinghaus")
    if features["grey_fraction"] > 0.02:
        matched.append("poggendorff")
    if features["vertical_lines"] >= 1 and features["horizontal_lines"] >= 1 and features["diagonal_fraction"] < 0.10:
        matched.append("vertical_horizontal")
    if features["horizontal_lines"] >= 1 and features["diagonal_components"] >= 20:
        matched.append("zollner")
    if features["horizontal_lines"] >= 2 and features["diagonal_component_height"] >= 0.60:
        matched.append("ponzo")
    if features["horizontal_lines"] >= 2:
        matched.append("muller_lyer")
    matched.append("none")
    return matched


def classify_image(image):
    """The illusion key for one PIL image: the first rule that holds."""
    return matched_rules(pixel_features(image))[0]
