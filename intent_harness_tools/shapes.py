"""Shapes: split a mask into connected shapes, and the diameter of a shape."""

import math

import numpy as np
from scipy import ndimage


def group_shapes(mask, min_pixels=20):
    """The 8-connected shapes of a mask with at least `min_pixels` pixels, largest first.
    Each shape: pixels (count), rows and cols (coordinates), bbox, centroid (row, col)."""
    labels, count = ndimage.label(mask, structure=np.ones((3, 3)))
    shapes = []
    for label in range(1, count + 1):
        rows, cols = np.nonzero(labels == label)
        if len(rows) < min_pixels:
            continue
        shapes.append({
            "pixels": int(len(rows)),
            "rows": rows,
            "cols": cols,
            "bbox": (int(rows.min()), int(cols.min()), int(rows.max()), int(cols.max())),
            "centroid": (float(rows.mean()), float(cols.mean())),
        })
    shapes.sort(key=lambda shape: -shape["pixels"])
    return shapes


def equivalent_diameter(shape):
    """The diameter of a disc with the same pixel area as the shape."""
    return math.sqrt(4.0 * shape["pixels"] / math.pi)
