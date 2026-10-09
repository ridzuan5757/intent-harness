"""Lines: the straight line through a shape, and the distance from a point to it."""

import math

import numpy as np


def fit_line(shape):
    """The principal axis of the shape's pixels. Angle in degrees, measured from the image's
    horizontal axis, positive when the line rises to the right (image rows grow downward).
    end_a and end_b are the extreme pixels along the axis, as (row, col), end_a the left one."""
    points = np.column_stack([shape["cols"], shape["rows"]]).astype(float)   # (N, 2) as (x, y)
    centre = points.mean(axis=0)
    centred = points - centre
    _, _, vectors = np.linalg.svd(centred, full_matrices=False)
    direction = vectors[0]                                                    # unit (dx, dy)
    if direction[0] < 0:
        direction = -direction
    projections = centred @ direction
    low = centre + projections.min() * direction
    high = centre + projections.max() * direction
    angle = math.degrees(math.atan2(-direction[1], direction[0]))           # y axis points down
    return {
        "centre": (float(centre[1]), float(centre[0])),
        "direction": (float(direction[0]), float(direction[1])),
        "angle_deg": float(angle),
        "end_a": (float(low[1]), float(low[0])),
        "end_b": (float(high[1]), float(high[0])),
    }


def point_line_distance(point, line):
    """Signed perpendicular distance from a (row, col) point to the line; positive when the
    point lies below the line in the image."""
    centre_row, centre_col = line["centre"]
    dx, dy = line["direction"]
    offset_x = point[1] - centre_col
    offset_y = point[0] - centre_row
    return float(offset_y * dx - offset_x * dy)
