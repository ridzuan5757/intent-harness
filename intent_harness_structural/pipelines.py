"""The six illusion measurement pipelines.

Each pipeline is a fixed sequence of measurement tools. It gets the tools as a mapping from the
harness and calls each one by name; it does not import any tool. The tool sequence and the
arithmetic are moved unchanged from the experiment workspace (`harness/pipelines.py`); only the
tool access changed.

Every pipeline returns a `Measurement`:

    value_a, value_b   the two measured values (top or left first)
    quantity           the compared quantity (relative difference, distance ratio, angle difference)
    found              False when a step did not get the expected shapes; then the values are None
    failed_step        the name of the first step that did not get the expected shapes, else None
"""

from dataclasses import dataclass

LONG_RUN_FRACTION = 0.08      # a straight segment is at least 8% of the image width long
ZOLLNER_FILTER_LENGTH = 41    # px; strokes are 7 px thick at every size


@dataclass(frozen=True)
class Measurement:
    value_a: float | None
    value_b: float | None
    quantity: float | None
    found: bool
    failed_step: str | None = None


def _not_found(step):
    return Measurement(None, None, None, False, step)


def _relative_difference(value_a, value_b):
    return (value_a - value_b) / ((value_a + value_b) / 2.0)


def _two_horizontal_segments(image, tools):
    """Shared by Müller-Lyer and Ponzo: the lengths of the two long horizontal row runs."""
    width = image.size[0]

    mask = tools["colour_mask"](image, "dark")
    if not mask.sum() > 0:
        return _not_found("colour_mask")

    segments = tools["find_runs"](mask, "rows", int(round(LONG_RUN_FRACTION * width)))
    if len(segments) != 2:
        return _not_found("find_runs")

    top_length = segments[0]["length"]
    bottom_length = segments[1]["length"]
    quantity = _relative_difference(top_length, bottom_length)
    return Measurement(top_length, bottom_length, quantity, True)


# ================================================================ Müller-Lyer

def measure_muller_lyer(image, tools):
    """Two horizontal shafts; the fins are slanted, so they form no long row run."""
    return _two_horizontal_segments(image, tools)


# ================================================================ Ponzo

def measure_ponzo(image, tools):
    """Two short horizontal segments between two converging lines. The converging lines are
    steep, so their row runs are short and the segment finder does not return them."""
    return _two_horizontal_segments(image, tools)


# ================================================================ Vertical-Horizontal

def measure_vertical_horizontal(image, tools):
    """One vertical segment standing on one horizontal segment. The vertical run in the
    columns can include the horizontal stroke where the two meet; that overlap is removed."""
    width = image.size[0]
    min_length = int(round(LONG_RUN_FRACTION * width))

    mask = tools["colour_mask"](image, "dark")
    if not mask.sum() > 0:
        return _not_found("colour_mask")

    horizontal = tools["find_runs"](mask, "rows", min_length)
    if len(horizontal) != 1:
        return _not_found("find_runs")

    vertical = tools["find_runs"](mask, "columns", min_length)
    if len(vertical) != 1:
        return _not_found("find_runs")

    h = horizontal[0]
    v = vertical[0]
    # rows covered by the vertical run: v["start"] .. v["end"]; rows of the horizontal stroke:
    # h["first_line"] .. h["last_line"]; subtract their overlap
    overlap_low = max(v["start"], h["first_line"])
    overlap_high = min(v["end"], h["last_line"] + 1)
    overlap = max(0.0, overlap_high - overlap_low)
    vertical_length = v["length"] - overlap
    horizontal_length = h["length"]

    quantity = _relative_difference(vertical_length, horizontal_length)
    return Measurement(vertical_length, horizontal_length, quantity, True)


# ================================================================ Ebbinghaus

def measure_ebbinghaus(image, tools):
    """Two red discs; the black surrounding discs are not in the red mask."""
    mask = tools["colour_mask"](image, "red")
    if not mask.sum() > 0:
        return _not_found("colour_mask")

    shapes = tools["group_shapes"](mask, min_pixels=20)
    if len(shapes) != 2:
        return _not_found("group_shapes")

    shapes = sorted(shapes, key=lambda shape: shape["centroid"][1])          # left first
    left = tools["equivalent_diameter"](shapes[0])
    right = tools["equivalent_diameter"](shapes[1])

    quantity = _relative_difference(left, right)
    return Measurement(left, right, quantity, True)


# ================================================================ Poggendorff

def measure_poggendorff(image, tools):
    """Two diagonal segments on either side of a grey rectangle. The left segment's line is
    extended across the rectangle; the quantity is the distance from the right segment's inner
    end to that line, divided by the rectangle width."""
    grey = tools["colour_mask"](image, "grey")
    rectangles = tools["group_shapes"](grey, min_pixels=100)
    if len(rectangles) < 1:
        return _not_found("colour_mask")
    rectangle = rectangles[0]
    rectangle_width = rectangle["bbox"][3] - rectangle["bbox"][1] + 1

    dark = tools["colour_mask"](image, "dark")
    shapes = tools["group_shapes"](dark, min_pixels=50)
    if len(shapes) != 2:
        return _not_found("group_shapes")

    shapes = sorted(shapes, key=lambda shape: shape["centroid"][1])          # left first
    left_line = tools["fit_line"](shapes[0])
    right_line = tools["fit_line"](shapes[1])

    inner_end = right_line["end_a"]                                  # the right segment's left end
    distance = tools["point_line_distance"](inner_end, left_line)

    quantity = distance / rectangle_width
    return Measurement(left_line["angle_deg"], right_line["angle_deg"], quantity, True)


# ================================================================ Zöllner

def measure_zollner(image, tools):
    """Two long lines crossed by short slanted strokes. A horizontal line filter removes the
    strokes; a line is fitted to each long line; the quantity is the angle difference."""
    mask = tools["colour_mask"](image, "dark")
    if not mask.sum() > 0:
        return _not_found("colour_mask")

    lines_only = tools["direction_filter"](mask, "rows", ZOLLNER_FILTER_LENGTH)
    if not lines_only.sum() > 0:
        return _not_found("direction_filter")

    shapes = tools["group_shapes"](lines_only, min_pixels=int(0.3 * image.size[0]))
    if len(shapes) != 2:
        return _not_found("group_shapes")

    shapes = sorted(shapes, key=lambda shape: shape["centroid"][0])          # top first
    top = tools["fit_line"](shapes[0])
    bottom = tools["fit_line"](shapes[1])

    quantity = top["angle_deg"] - bottom["angle_deg"]
    return Measurement(top["angle_deg"], bottom["angle_deg"], quantity, True)


PIPELINES = {
    "muller_lyer": measure_muller_lyer,
    "ponzo": measure_ponzo,
    "vertical_horizontal": measure_vertical_horizontal,
    "ebbinghaus": measure_ebbinghaus,
    "poggendorff": measure_poggendorff,
    "zollner": measure_zollner,
}
