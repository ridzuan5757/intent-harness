"""The drawn-shape checks of the experiment's notebook 13 (sections 3 to 8).

Each check draws a shape with a known answer, measures it with one tool, and compares the error
with a limit that was set before the checks ran. The cases, sizes, limits and order are the
same as in notebook 13: 116 checks, all inside their limits.
"""

import math

import pytest
from PIL import Image

from intent_harness_tools import (colour_mask, decide, direction_filter, draw_discs, draw_segments,
                                  equivalent_diameter, find_runs, fit_line, group_shapes,
                                  point_line_distance, segment_at_angle)

LIMITS = {
    "length_px": 2.0,
    "diameter_px": 1.5,
    "angle_deg": 0.3,
    "distance_px": 1.5,
}
SIZES = [384, 768, 1152]
STROKE = 7
ZOLLNER_FILTER_LENGTH = 41      # px; the Zollner pipeline's filter length in the experiment

# The largest absolute error per tool in notebook 13 (section 9), to six decimals.
NOTEBOOK_13_LARGEST_ERROR = {
    "colour_mask": 0.0,
    "decide": 0.0,
    "direction_filter": 0.115641,
    "equivalent_diameter": 0.169844,
    "find_runs": 0.8,
    "fit_line": 0.056093,
    "group_shapes": 0.0,
    "point_line_distance": 0.164823,
}
NOTEBOOK_13_CHECKS_PER_TOOL = {
    "colour_mask": 12,
    "decide": 5,
    "direction_filter": 18,
    "equivalent_diameter": 9,
    "find_runs": 27,
    "fit_line": 21,
    "group_shapes": 12,
    "point_line_distance": 12,
}


def _check(tool, case, pixel, known, measured, limit):
    error = float(measured) - float(known)
    return {"tool": tool, "case": case, "pixel": pixel, "known": float(known),
            "measured": float(measured), "error": error, "limit": float(limit)}


def _segment_lengths():
    checks = []
    for size in SIZES:
        for fraction in [0.2, 0.4, 0.6]:
            length = fraction * size
            x0 = (size - length) / 2.0
            middle = size / 2.0

            horizontal = draw_segments(size, [((x0, middle), (x0 + length, middle))], width=STROKE)
            found = find_runs(colour_mask(horizontal, "dark"), "rows", int(0.08 * size))
            checks.append(_check("find_runs", f"horizontal {fraction:.1f}W", size, length,
                                 found[0]["length"], LIMITS["length_px"]))

            vertical = draw_segments(size, [((middle, x0), (middle, x0 + length))], width=STROKE)
            found = find_runs(colour_mask(vertical, "dark"), "columns", int(0.08 * size))
            checks.append(_check("find_runs", f"vertical {fraction:.1f}W", size, length,
                                 found[0]["length"], LIMITS["length_px"]))

            thickness = found[0]["thickness"]
            checks.append(_check("find_runs", f"stroke thickness {fraction:.1f}W", size, STROKE,
                                 thickness, 1.0))
    return checks


def _disc_diameters():
    checks = []
    for size in SIZES:
        for fraction in [0.08, 0.12, 0.2]:
            diameter = fraction * size
            image = draw_discs(size, [((size * 0.3, size * 0.5), diameter),
                                      ((size * 0.7, size * 0.5), diameter)])
            shapes = group_shapes(colour_mask(image, "red"), min_pixels=20)
            checks.append(_check("group_shapes", f"2 discs {fraction:.2f}W", size, 2, len(shapes), 0))
            checks.append(_check("equivalent_diameter", f"disc {fraction:.2f}W", size, diameter,
                                 equivalent_diameter(shapes[0]), LIMITS["diameter_px"]))
        many = []
        for index in range(6):
            many.append(((size * (0.12 + 0.15 * index), size * 0.5), size * 0.06))
        shapes = group_shapes(colour_mask(draw_discs(size, many), "red"), min_pixels=20)
        checks.append(_check("group_shapes", "6 discs", size, 6, len(shapes), 0))
    return checks


def _line_angles():
    checks = []
    for size in SIZES:
        for angle in [-10, 0, 2, 3, 30, 45, 60]:
            segment = segment_at_angle((size / 2.0, size / 2.0), 0.5 * size, angle)
            image = draw_segments(size, [segment], width=STROKE)
            shapes = group_shapes(colour_mask(image, "dark"), min_pixels=20)
            line = fit_line(shapes[0])
            checks.append(_check("fit_line", f"angle {angle:+d} deg", size, angle,
                                 line["angle_deg"], LIMITS["angle_deg"]))
    return checks


def _point_line_distances():
    """Two segments on one line at 30 degrees; the right one is moved across the line by a known
    offset. The distance from its inner end to the left segment's line must equal the offset."""
    checks = []
    for size in SIZES:
        for offset in [0.0, 5.0, 10.0, 20.0]:
            angle = 30.0
            length = 0.25 * size
            dx = math.cos(math.radians(angle))
            dy = -math.sin(math.radians(angle))
            normal_x = -dy
            normal_y = dx
            left_centre = (size * 0.3, size * 0.6)
            right_centre = (left_centre[0] + 0.4 * size * dx + offset * normal_x,
                            left_centre[1] + 0.4 * size * dy + offset * normal_y)
            left = segment_at_angle(left_centre, length, angle)
            right = segment_at_angle(right_centre, length, angle)
            image = draw_segments(size, [left, right], width=STROKE)
            shapes = group_shapes(colour_mask(image, "dark"), min_pixels=20)
            if shapes[0]["centroid"][1] > shapes[1]["centroid"][1]:     # put the left shape first
                shapes = [shapes[1], shapes[0]]
            left_line = fit_line(shapes[0])
            right_line = fit_line(shapes[1])
            distance = point_line_distance(right_line["end_a"], left_line)
            checks.append(_check("point_line_distance", f"offset {offset:.0f} px", size, offset,
                                 distance, LIMITS["distance_px"]))
    return checks


def _direction_filter():
    """A long line tilted by a known angle, crossed by short strokes at 45 degrees, as in a
    Zollner figure. After the filter, one shape must remain, at the tilt angle."""
    checks = []
    for size in SIZES:
        for tilt in [0.0, 2.0, 3.0]:
            strokes = [segment_at_angle((size / 2.0, size / 2.0), 0.9 * size, tilt)]
            for index in range(8):
                x = size * (0.1 + 0.1 * index)
                y = size / 2.0 - math.tan(math.radians(tilt)) * (x - size / 2.0)
                strokes.append(segment_at_angle((x, y), 0.15 * size, 45.0))
            image = draw_segments(size, strokes, width=STROKE)
            kept = direction_filter(colour_mask(image, "dark"), "rows", ZOLLNER_FILTER_LENGTH)
            shapes = group_shapes(kept, min_pixels=int(0.3 * size))
            checks.append(_check("direction_filter", f"shapes left, tilt {tilt:.0f}", size, 1,
                                 len(shapes), 0))
            checks.append(_check("direction_filter", f"angle after filter, tilt {tilt:.0f}", size,
                                 tilt, fit_line(shapes[0])["angle_deg"], LIMITS["angle_deg"]))
    return checks


def _colour_masks_and_decisions():
    checks = []
    blocks = [("dark", (0, 0, 0)), ("red", (255, 0, 0)), ("grey", (128, 128, 128))]
    for colour, rgb in blocks:
        image = Image.new("RGB", (100, 100), "white")
        image.paste(rgb, (25, 25, 75, 75))
        mask = colour_mask(image, colour)
        checks.append(_check("colour_mask", f"{colour} block, inside", 100, 2500,
                             int(mask[25:75, 25:75].sum()), 0))
        checks.append(_check("colour_mask", f"{colour} block, outside", 100, 0,
                             int(mask.sum() - mask[25:75, 25:75].sum()), 0))
        for other, _ in blocks:
            if other != colour:
                checks.append(_check("colour_mask", f"{colour} block under the {other} mask", 100,
                                     0, int(colour_mask(image, other).sum()), 0))

    decisions = [(0.0, 0.1, "Yes"), (0.1, 0.1, "Yes"), (-0.1, 0.1, "Yes"), (0.11, 0.1, "No"),
                 (-0.2, 0.1, "No")]
    for quantity, tolerance, expected in decisions:
        got = decide(quantity, tolerance)
        matched = 1
        if got != expected:
            matched = 0
        checks.append(_check("decide", f"{quantity:+.2f} vs {tolerance}", 0, 1, matched, 0))
    return checks


def build_checks():
    """All drawn-shape checks, in the order of notebook 13."""
    checks = []
    checks.extend(_segment_lengths())
    checks.extend(_disc_diameters())
    checks.extend(_line_angles())
    checks.extend(_point_line_distances())
    checks.extend(_direction_filter())
    checks.extend(_colour_masks_and_decisions())
    return checks


CHECKS = build_checks()


def _check_id(check):
    return f"{check['tool']}|{check['case']}|{check['pixel']}"


@pytest.mark.parametrize("check", CHECKS, ids=[_check_id(check) for check in CHECKS])
def test_drawn_shape_check_inside_limit(check):
    assert abs(check["error"]) <= check["limit"], check


def test_check_count_matches_notebook_13():
    per_tool = {}
    for check in CHECKS:
        per_tool[check["tool"]] = per_tool.get(check["tool"], 0) + 1
    assert len(CHECKS) == 116
    assert per_tool == NOTEBOOK_13_CHECKS_PER_TOOL


def test_largest_error_per_tool_matches_notebook_13():
    largest = {}
    for check in CHECKS:
        error = abs(check["error"])
        if error > largest.get(check["tool"], 0.0):
            largest[check["tool"]] = error
        else:
            largest.setdefault(check["tool"], 0.0)
    rounded = {}
    for tool, error in largest.items():
        rounded[tool] = round(error, 6)
    assert rounded == NOTEBOOK_13_LARGEST_ERROR
