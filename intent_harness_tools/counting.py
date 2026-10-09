"""Image operations for the counting pipelines.

Plain functions with normal arguments and return values, moved unchanged from the experiment
workspace (grounded-count-harness, harness/tools.py, items 9 to 15). They import nothing from
the other packages of this repository.

1. luminance          (H, W) brightness of an image
2. colour_runs        runs of near-constant colour along a pixel line
3. line_profile       the thin grid lines of an image along one axis
4. cluster            group close values; the mean of each group
5. box_cells          the cells of a grid of boxes, named by column letter and row number
6. template_distance  how far a patch is from a reference crop
7. solidity           how much of its convex outline a shape fills
8. radial_peaks       the number of points around a shape's centre
9. palette_labels     each pixel's nearest colour among a few colours found in the image
10. nearest_template  the reference crop nearest to a patch
"""

import numpy as np
from scipy import ndimage


def luminance(image):
    """(H, W) float brightness of a PIL image."""
    rgb = np.asarray(image.convert("RGB")).astype(float)
    return 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]


def colour_runs(pixels, max_step=40, min_length=3):
    """Runs of near-constant colour along a (N, 3) pixel line. A run ends where neighbouring pixels
    differ by more than `max_step` (sum over channels); runs shorter than `min_length` (soft edges)
    are dropped. Each run: start, end, length, colour (mean RGB)."""
    runs = []
    start = 0
    count = len(pixels)
    for index in range(1, count + 1):
        boundary = index == count
        if not boundary:
            step = np.abs(pixels[index].astype(int) - pixels[index - 1].astype(int)).sum()
            boundary = step > max_step
        if boundary:
            if index - start >= min_length:
                runs.append({"start": start, "end": index, "length": index - start,
                             "colour": pixels[start:index].astype(float).mean(axis=0)})
            start = index
    return runs


def line_profile(image, axis, window_fraction=0.04, delta=15, fraction=0.5):
    """The grid lines of an image along `axis` ("rows" = horizontal lines, "columns" = vertical).
    A pixel is a line pixel when it is at least `delta` darker than the median of its window (a
    window of `window_fraction` of the width), so thin lines pass and thick frames do not. A line is
    a group of adjacent rows (or columns) whose line-pixel count reaches `fraction` of the best
    one; groups thicker than twice the median line are dropped (a frame edge, not a line).
    Returns lines (count), kept spans, dropped spans."""
    brightness = luminance(image)
    size = max(5, int(round(window_fraction * image.size[0])) | 1)
    background = ndimage.median_filter(brightness, size=size)
    mask = brightness < background - delta
    coverage = mask.sum(axis=1) if axis == "rows" else mask.sum(axis=0)
    labels, count = ndimage.label(coverage >= fraction * coverage.max())
    spans = []
    for found in ndimage.find_objects(labels):
        spans.append((int(found[0].start), int(found[0].stop - found[0].start)))
    thickness = []
    for start, width in spans:
        thickness.append(width)
    median = float(np.median(thickness)) if thickness else 0.0
    kept = []
    dropped = []
    for start, width in spans:
        if width <= max(2.0 * median, median + 2):
            kept.append((start, width))
        else:
            dropped.append((start, width))
    return {"lines": len(kept), "kept": kept, "dropped": dropped}


def cluster(values, gap):
    """Group sorted values whose neighbours are at most `gap` apart; the mean of each group."""
    ordered = sorted(values)
    groups = [[ordered[0]]]
    for value in ordered[1:]:
        if value - groups[-1][-1] > gap:
            groups.append([value])
        else:
            groups[-1].append(value)
    centres = []
    for group in groups:
        centres.append(float(np.mean(group)))
    return centres


def box_cells(image, light_level=230, min_fraction=0.05):
    """The cells of a grid of boxes: light regions (brightness >= `light_level`) enclosed by box
    borders, not touching the image edge, at least `min_fraction` of the image on each side. Cells
    are named by column letter (left to right) and row number (top to bottom).
    Returns {"cells": {"C3": (top, bottom, left, right), ...}, "n_cols", "n_rows"}."""
    light = luminance(image) >= light_level
    labels, count = ndimage.label(light)
    height, width = light.shape
    boxes = []
    for found in ndimage.find_objects(labels):
        top, bottom = found[0].start, found[0].stop
        left, right = found[1].start, found[1].stop
        if top == 0 or left == 0 or bottom == height or right == width:
            continue
        if bottom - top < min_fraction * height or right - left < min_fraction * width:
            continue
        boxes.append((top, bottom, left, right))
    if not boxes:
        return {"cells": {}, "n_cols": 0, "n_rows": 0}
    heights = []
    column_centres = []
    row_centres = []
    for top, bottom, left, right in boxes:
        heights.append(bottom - top)
        column_centres.append((left + right) / 2.0)
        row_centres.append((top + bottom) / 2.0)
    gap = 0.5 * float(np.median(heights))
    columns = cluster(column_centres, gap)
    rows = cluster(row_centres, gap)
    cells = {}
    for top, bottom, left, right in boxes:
        column = int(np.argmin(np.abs(np.array(columns) - (left + right) / 2.0)))
        row = int(np.argmin(np.abs(np.array(rows) - (top + bottom) / 2.0)))
        cells[f"{chr(ord('A') + column)}{row + 1}"] = (top, bottom, left, right)
    return {"cells": cells, "n_cols": len(columns), "n_rows": len(rows)}


def template_distance(feature, reference):
    """Mean absolute difference between two equal-size grey patches (0 = identical)."""
    return float(np.abs(np.asarray(feature, dtype=float) - np.asarray(reference, dtype=float)).mean())


def solidity(shape):
    """A shape's pixel count divided by the area of its convex outline (1 for a convex shape).
    A shape one pixel wide has no 2-D outline and counts as convex."""
    from scipy.spatial import ConvexHull

    points = np.column_stack([shape["cols"], shape["rows"]]).astype(float)
    if len(points) < 5:
        return 1.0
    try:
        hull = ConvexHull(points)
    except Exception:
        return 1.0
    return min(1.0, shape["pixels"] / max(hull.volume, 1.0))


def radial_peaks(rows, cols, bins=90):
    """How many points stick out around a shape's centre: the furthest pixel in each of `bins`
    angle sectors, smoothed, counted as runs above the midpoint between the nearest and furthest
    sector. 0 for a round shape (less than 15% between them)."""
    rows = np.asarray(rows, dtype=float)
    cols = np.asarray(cols, dtype=float)
    centre_row = rows.mean()
    centre_col = cols.mean()
    angles = np.arctan2(rows - centre_row, cols - centre_col)
    distances = np.hypot(rows - centre_row, cols - centre_col)
    sectors = ((angles + np.pi) / (2 * np.pi) * bins).astype(int) % bins
    profile = np.zeros(bins)
    for sector, distance in zip(sectors, distances):
        if distance > profile[sector]:
            profile[sector] = distance
    for sector in range(bins):
        if profile[sector] == 0:
            profile[sector] = profile[sector - 1]
    kernel = np.array([1.0, 2.0, 3.0, 2.0, 1.0])
    kernel = kernel / kernel.sum()
    padded = np.concatenate([profile[-2:], profile, profile[:2]])
    smooth = np.convolve(padded, kernel, mode="valid")
    low = smooth.min()
    high = smooth.max()
    if high - low < 0.15 * high:
        return 0
    above = smooth > low + 0.5 * (high - low)
    if above.all():
        return 0
    return int(np.sum(above & ~np.roll(above, 1)))


def palette_labels(rgb, k=8, iterations=12):
    """(H, W) index of each pixel's nearest colour among `k` colours found in the (H, W, 3) image by
    k-means (farthest-point start, fixed iterations, deterministic). Soft edge pixels join the
    region they border instead of forming their own colour class."""
    pixels = rgb.reshape(-1, 3).astype(float)
    step = max(1, len(pixels) // 20000)
    sample = pixels[::step]
    centres = [sample[0]]
    for _ in range(1, k):
        distances = np.min(np.stack([((sample - centre) ** 2).sum(axis=1) for centre in centres]), axis=0)
        centres.append(sample[int(np.argmax(distances))])
    centres = np.array(centres)
    for _ in range(iterations):
        nearest = np.argmin(((sample[:, None, :] - centres[None, :, :]) ** 2).sum(axis=2), axis=1)
        for index in range(k):
            members = sample[nearest == index]
            if len(members) > 0:
                centres[index] = members.mean(axis=0)
    labels = np.empty(len(pixels), dtype=int)
    chunk = 200000
    for start in range(0, len(pixels), chunk):
        part = pixels[start:start + chunk]
        labels[start:start + chunk] = np.argmin(((part[:, None, :] - centres[None, :, :]) ** 2).sum(axis=2), axis=1)
    return labels.reshape(rgb.shape[:2])


def nearest_template(feature, references):
    """The reference nearest to `feature` by `template_distance`, as (kind, distance).

    `references` is a list of dicts with "kind" and "feature". On a tie the first one wins.
    """
    best = None
    best_distance = None
    for reference in references:
        distance = template_distance(feature, reference["feature"])
        if best_distance is None or distance < best_distance:
            best = reference
            best_distance = distance
    return best["kind"], best_distance
