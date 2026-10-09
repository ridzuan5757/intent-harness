"""User Story 1 and 3 scenarios, and the edge cases of the spec."""

import math

import numpy as np
import pytest
from PIL import Image

from intent_harness_tools import (SUPERSAMPLE, colour_mask, decide, direction_filter, draw_discs,
                                  draw_segments, equivalent_diameter, find_runs, group_shapes,
                                  segment_at_angle)


# ---------------------------------------------------------------- User Story 1

def test_horizontal_stroke_length_at_384():
    size = 384
    length = 0.4 * size
    x0 = (size - length) / 2.0
    image = draw_segments(size, [((x0, size / 2.0), (x0 + length, size / 2.0))])
    segments = find_runs(colour_mask(image, "dark"), "rows", int(0.08 * size))
    assert len(segments) == 1
    assert abs(segments[0]["length"] - length) <= 2.0


def test_two_red_discs_diameters():
    size = 384
    diameter = 0.12 * size
    image = draw_discs(size, [((size * 0.3, size * 0.5), diameter), ((size * 0.7, size * 0.5), diameter)])
    shapes = group_shapes(colour_mask(image, "red"), min_pixels=20)
    assert len(shapes) == 2
    for shape in shapes:
        assert abs(equivalent_diameter(shape) - diameter) <= 1.5


@pytest.mark.parametrize("quantity, tolerance, expected", [
    (0.0, 0.1, "Yes"),
    (0.1, 0.1, "Yes"),
    (-0.1, 0.1, "Yes"),
    (0.11, 0.1, "No"),
    (-0.2, 0.1, "No"),
    (0.0, 0.0, "Yes"),
])
def test_decide(quantity, tolerance, expected):
    assert decide(quantity, tolerance) == expected


# ---------------------------------------------------------------- edge cases

def test_empty_mask_gives_no_shapes_and_no_segments():
    mask = np.zeros((50, 50), dtype=bool)
    assert group_shapes(mask) == []
    assert find_runs(mask, "rows", 5) == []
    assert find_runs(mask, "columns", 5) == []


def test_small_shape_is_dropped():
    mask = np.zeros((50, 50), dtype=bool)
    mask[5:8, 5:8] = True          # 9 pixels
    mask[20:30, 20:30] = True      # 100 pixels
    shapes = group_shapes(mask, min_pixels=20)
    assert len(shapes) == 1
    assert shapes[0]["pixels"] == 100


def test_short_run_is_dropped():
    mask = np.zeros((10, 50), dtype=bool)
    mask[2, 0:4] = True            # 4 px
    mask[6, 10:40] = True          # 30 px
    segments = find_runs(mask, "rows", 10)
    assert len(segments) == 1
    assert segments[0]["length"] == 30


def test_unknown_colour_raises():
    image = Image.new("RGB", (10, 10), "white")
    with pytest.raises(ValueError, match="dark"):
        colour_mask(image, "blue")


def test_unknown_axis_raises():
    mask = np.zeros((10, 10), dtype=bool)
    with pytest.raises(ValueError, match="rows"):
        find_runs(mask, "diagonal", 3)
    with pytest.raises(ValueError, match="columns"):
        direction_filter(mask, "diagonal", 3)


# ---------------------------------------------------------------- User Story 3

def test_draw_segments_size_mode_and_colour():
    image = draw_segments(128, [((20, 64), (108, 64))], width=7, colour=(0, 0, 0))
    assert image.size == (128, 128)
    assert image.mode == "RGB"
    assert image.getpixel((64, 64)) == (0, 0, 0)
    assert image.getpixel((5, 5)) == (255, 255, 255)


def test_draw_discs_colour():
    image = draw_discs(128, [((64, 64), 40)])
    assert image.size == (128, 128)
    assert image.getpixel((64, 64)) == (255, 0, 0)


def test_segment_at_angle_end_points():
    (x0, y0), (x1, y1) = segment_at_angle((100.0, 100.0), 50.0, 30.0)
    assert math.isclose((x0 + x1) / 2.0, 100.0)
    assert math.isclose((y0 + y1) / 2.0, 100.0)
    assert math.isclose(math.hypot(x1 - x0, y1 - y0), 50.0)
    assert y1 < y0                 # rising to the right: image rows grow downward
    assert math.isclose(math.degrees(math.atan2(y0 - y1, x1 - x0)), 30.0)


def test_supersample_is_four():
    assert SUPERSAMPLE == 4
