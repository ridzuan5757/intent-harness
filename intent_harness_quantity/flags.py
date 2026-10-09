"""Counters for the flag sub-topics: stripes and stars.

The rules and constants are those of the experiment (grounded-count-harness, harness/counting.py,
spec 004), unchanged. Each counter returns the count, or None when the flag cloth is not found.
"""

import numpy as np


def flag_cloth(rgb):
    """(top, bottom, left, right) of the flag cloth: the widest run of columns that are mostly not
    the grey background (the pole is a narrow run), then the cloth rows at its fly edge."""
    values = rgb.astype(int)
    grey = ((np.abs(values[:, :, 0] - 198) < 12) & (np.abs(values[:, :, 1] - 198) < 12)
            & (np.abs(values[:, :, 2] - 198) < 12))
    cloth = ~grey
    columns = np.where(cloth.mean(axis=0) > 0.3)[0]
    if len(columns) == 0:
        return None
    runs = []
    start = columns[0]
    for index in range(1, len(columns) + 1):
        if index == len(columns) or columns[index] != columns[index - 1] + 1:
            runs.append((int(start), int(columns[index - 1])))
            if index < len(columns):
                start = columns[index]
    left, right = max(runs, key=lambda run: run[1] - run[0])
    rows = np.where(cloth[:, max(left, right - 5)])[0]
    if len(rows) == 0:
        return None
    return int(rows.min()), int(rows.max()), left, right


class FlagStripesCounter:
    """Colour bands down a column near the fly edge of the cloth; neighbouring bands of one colour
    merge."""

    name = "flag_stripes"
    required_tools = ("colour_runs",)

    def count(self, image, question, tools):
        rgb = np.asarray(image.convert("RGB"))
        box = flag_cloth(rgb)
        if box is None:
            return None
        top, bottom, left, right = box
        column = right - max(3, (right - left) // 30)
        runs = tools["colour_runs"](rgb[top:bottom + 1, column], min_length=max(3, (bottom - top) // 60))
        keys = []
        for run in runs:
            keys.append(tuple(int(value) for value in np.round(run["colour"] / 24)))
        merged = []
        for key in keys:
            if len(merged) == 0 or merged[-1] != key:
                merged.append(key)
        if len(merged) == 0:
            return None
        return len(merged)


class FlagStarsCounter:
    """Stars on the cloth: palette regions not touching the cloth edge, roughly square, at most
    half the cloth; a star when tiny and non-convex, small and non-convex, or measurable with 5-7
    points (4-8 under 14 px) and solidity below 0.85; regions whose centre is inside a kept star's
    box are the same star."""

    name = "flag_stars"
    required_tools = ("palette_labels", "solidity", "radial_peaks")

    def count(self, image, question, tools):
        from scipy import ndimage

        rgb = np.asarray(image.convert("RGB"))
        box = flag_cloth(rgb)
        if box is None:
            return None
        top, bottom, left, right = box
        cloth = rgb[top:bottom + 1, left:right + 1]
        height, width = cloth.shape[0], cloth.shape[1]
        labels = tools["palette_labels"](cloth, k=8)

        candidates = []
        for value in np.unique(labels):
            regions, count = ndimage.label(labels == value)
            for found, region in zip(ndimage.find_objects(regions), range(1, count + 1)):
                region_top, region_bottom = found[0].start, found[0].stop
                region_left, region_right = found[1].start, found[1].stop
                if region_top <= 1 or region_left <= 1 or region_bottom >= height - 1 or region_right >= width - 1:
                    continue
                tall = region_bottom - region_top
                wide = region_right - region_left
                if tall < 3 or wide < 3 or tall > 0.5 * height or wide > 0.5 * width:
                    continue
                if not (0.6 <= tall / wide <= 1.6):
                    continue
                rows, cols = np.nonzero(regions[found] == region)
                if len(rows) < 6:
                    continue
                shape = {"rows": rows, "cols": cols, "pixels": len(rows)}
                solidity = tools["solidity"](shape)
                longest = max(tall, wide)
                if longest < 0.015 * width:
                    is_star = 0.3 <= solidity < 0.85
                elif longest < 0.025 * width:
                    is_star = 0.3 <= solidity < 0.9
                elif longest < 14:
                    peaks = tools["radial_peaks"](rows, cols)
                    is_star = 4 <= peaks <= 8 and solidity < 0.9
                else:
                    peaks = tools["radial_peaks"](rows, cols)
                    is_star = 5 <= peaks <= 7 and solidity < 0.85
                if is_star:
                    candidates.append((region_top, region_bottom, region_left, region_right))

        candidates.sort(key=lambda box: -(box[1] - box[0]) * (box[3] - box[2]))
        kept = []
        for candidate in candidates:
            centre_row = (candidate[0] + candidate[1]) / 2.0
            centre_col = (candidate[2] + candidate[3]) / 2.0
            inside = False
            for star in kept:
                if star[0] - 2 <= centre_row <= star[1] + 2 and star[2] - 2 <= centre_col <= star[3] + 2:
                    inside = True
            if not inside:
                kept.append(candidate)
        if len(kept) == 0:
            return None
        return len(kept)
