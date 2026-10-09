"""The counting image operations on arrays and drawn figures with a known answer."""

import numpy as np
from PIL import Image, ImageDraw

from intent_harness_tools.counting import (
    box_cells,
    cluster,
    colour_runs,
    line_profile,
    luminance,
    nearest_template,
    palette_labels,
    radial_peaks,
    solidity,
    template_distance,
)
from intent_harness_tools.shapes import group_shapes


def test_luminance_of_white_and_black():
    image = Image.new("RGB", (4, 2), (255, 255, 255))
    image.putpixel((0, 0), (0, 0, 0))
    values = luminance(image)
    assert values.shape == (2, 4)
    assert values[0, 0] == 0
    assert abs(values[1, 3] - 255) < 1e-9


def test_colour_runs_finds_bands_and_drops_short_runs():
    line = np.array([[255, 0, 0]] * 10 + [[0, 0, 255]] * 2 + [[0, 255, 0]] * 10, dtype=np.uint8)
    runs = colour_runs(line, min_length=3)
    assert [run["length"] for run in runs] == [10, 10]
    assert list(runs[0]["colour"]) == [255, 0, 0]


def test_line_profile_counts_thin_lines():
    image = Image.new("RGB", (200, 200), (230, 180, 100))
    draw = ImageDraw.Draw(image)
    for index in range(7):
        y = 20 + index * 25
        draw.line([(10, y), (190, y)], fill=(0, 0, 0), width=2)
    assert line_profile(image, "rows")["lines"] == 7


def test_cluster_groups_close_values():
    assert cluster([1.0, 1.5, 10.0, 10.4, 30.0], 2.0) == [1.25, 10.2, 30.0]


def test_box_cells_names_cells_by_column_and_row():
    image = Image.new("RGB", (300, 200), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    for column in range(3):
        for row in range(2):
            left = 10 + column * 95
            top = 10 + row * 92
            draw.rectangle([left, top, left + 85, top + 82], outline=(0, 0, 0), width=3)
    found = box_cells(image)
    assert (found["n_cols"], found["n_rows"]) == (3, 2)
    assert sorted(found["cells"]) == ["A1", "A2", "B1", "B2", "C1", "C2"]


def test_template_distance_and_nearest():
    a = np.zeros((4, 4))
    b = np.full((4, 4), 10.0)
    assert template_distance(a, a) == 0
    assert template_distance(a, b) == 10
    references = [{"kind": "dark", "feature": a}, {"kind": "light", "feature": b}]
    assert nearest_template(np.full((4, 4), 8.0), references) == ("light", 2.0)


def test_solidity_of_a_square_and_an_l_shape():
    square = np.zeros((30, 30), dtype=bool)
    square[5:25, 5:25] = True
    shape = group_shapes(square)[0]
    assert solidity(shape) > 0.95
    corner = np.zeros((30, 30), dtype=bool)
    corner[5:25, 5:10] = True
    corner[20:25, 5:25] = True
    assert solidity(group_shapes(corner)[0]) < 0.75     # far from convex


def star_mask(points, size=101, outer=45, inner=18):
    image = Image.new("L", (size, size), 0)
    corners = []
    for index in range(2 * points):
        radius = outer if index % 2 == 0 else inner
        angle = np.pi * index / points - np.pi / 2
        corners.append((50 + radius * np.cos(angle), 50 + radius * np.sin(angle)))
    ImageDraw.Draw(image).polygon(corners, fill=255)
    return np.asarray(image) > 0


def test_radial_peaks_counts_star_points_and_zero_for_a_disc():
    rows, cols = np.nonzero(star_mask(5))
    assert radial_peaks(rows, cols) == 5
    disc = np.zeros((101, 101), dtype=bool)
    yy, xx = np.mgrid[0:101, 0:101]
    disc[(yy - 50) ** 2 + (xx - 50) ** 2 <= 40 ** 2] = True
    rows, cols = np.nonzero(disc)
    assert radial_peaks(rows, cols) == 0


def test_palette_labels_is_deterministic_and_separates_colours():
    rgb = np.zeros((20, 20, 3), dtype=np.uint8)
    rgb[:, 10:] = (255, 0, 0)
    first = palette_labels(rgb, k=2)
    second = palette_labels(rgb, k=2)
    assert np.array_equal(first, second)
    assert first[0, 0] != first[0, 19]
