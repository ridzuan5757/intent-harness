"""Straight segments along rows or columns, and the stroke-direction filter."""

import numpy as np
from scipy import ndimage


def _row_runs(row_values, min_length):
    """(start, end) of runs of True at least `min_length` long; end is exclusive."""
    padded = np.concatenate([[0], row_values.astype(np.int8), [0]])
    changes = np.diff(padded)
    starts = np.where(changes == 1)[0]
    ends = np.where(changes == -1)[0]
    runs = []
    for start, end in zip(starts, ends):
        if end - start >= min_length:
            runs.append((int(start), int(end)))
    return runs


def find_runs(mask, axis, min_length):
    """Long straight runs of a mask along `axis` ("rows" = horizontal, "columns" = vertical),
    merged into segments. Runs in adjacent lines that overlap belong to one segment.

    Each segment: position (mean line index), first and last line, thickness (lines spanned),
    start and end (median run start and end), length (median run length)."""
    if axis == "columns":
        working = mask.T
    elif axis == "rows":
        working = mask
    else:
        raise ValueError("axis must be 'rows' or 'columns'")

    segments = []          # each: {"lines": [...], "starts": [...], "ends": [...]}
    open_segments = []     # segments that had a run in the previous line
    for line_index in range(working.shape[0]):
        runs = _row_runs(working[line_index], min_length)
        still_open = []
        for start, end in runs:
            joined = None
            for segment in open_segments:
                last_start = segment["starts"][-1]
                last_end = segment["ends"][-1]
                if start < last_end and end > last_start:      # the runs overlap
                    joined = segment
                    break
            if joined is None:
                joined = {"lines": [], "starts": [], "ends": []}
                segments.append(joined)
            joined["lines"].append(line_index)
            joined["starts"].append(start)
            joined["ends"].append(end)
            still_open.append(joined)
        open_segments = still_open

    result = []
    for segment in segments:
        lengths = np.array(segment["ends"]) - np.array(segment["starts"])
        result.append({
            "axis": axis,
            "position": float(np.mean(segment["lines"])),
            "first_line": int(min(segment["lines"])),
            "last_line": int(max(segment["lines"])),
            "thickness": int(max(segment["lines"]) - min(segment["lines"]) + 1),
            "start": float(np.median(segment["starts"])),
            "end": float(np.median(segment["ends"])),
            "length": float(np.median(lengths)),
        })
    result.sort(key=lambda segment: segment["position"])
    return result


def direction_filter(mask, axis, length):
    """Keep only the parts of the mask that contain a straight `length`-pixel line along
    `axis` (binary opening with a line element); slanted strokes are removed."""
    if axis == "rows":
        element = np.ones((1, length), dtype=bool)
    elif axis == "columns":
        element = np.ones((length, 1), dtype=bool)
    else:
        raise ValueError("axis must be 'rows' or 'columns'")
    return ndimage.binary_opening(mask, structure=element)
