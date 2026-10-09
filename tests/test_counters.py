"""The counting pipelines on drawn figures with a known count, through `Harness.answer`.

The model tools are fakes: `segment_concept` returns the regions a test gives it, so no model is
needed. The selector chooses each counter from the question, as in use.
"""

import numpy as np
from PIL import Image, ImageDraw

from intent_harness import Choice, Harness
from intent_harness_quantity import NO_COUNTER
from intent_harness_quantity.logos import region_crop
from intent_harness_quantity.references import CHESS_SQUARE_COLOURS
from intent_harness_tools.sam3 import keep_smaller_regions, remove_duplicate_regions


class QuantityOnly:
    def classify(self, question, intents):
        return Choice(key="quantity", probabilities={"quantity": 1.0}, confidence=1.0)


class Regions:
    """The regions the fake `segment_concept` returns, by concept."""

    def __init__(self):
        self.by_concept = {}

    def segment_concept(self, image, concept, min_score=0.01):
        return [region for region in self.by_concept.get(concept, []) if region["score"] >= min_score]


def whole_image_box(image, query):
    return [0.0, 0.0, 1.0, 1.0]


def make_harness(regions=None):
    regions = regions or Regions()
    harness = Harness()
    harness.load_tools("intent_harness_tools.counting_plugin")
    harness.register_tool(whole_image_box, name="best_box")
    harness.register_tool(regions.segment_concept, name="segment_concept")
    harness.register_tool(keep_smaller_regions, name="keep_smaller_regions")
    harness.register_tool(remove_duplicate_regions, name="remove_duplicate_regions")
    harness.load_intents("intent_harness_quantity.plugin")
    harness.register_classifier(QuantityOnly())
    return harness


def chess_board(side=48):
    image = Image.new("RGB", (8 * side, 8 * side))
    draw = ImageDraw.Draw(image)
    for row in range(8):
        for column in range(8):
            colour = tuple(int(value) for value in CHESS_SQUARE_COLOURS[(row + column) % 2])
            draw.rectangle([column * side, row * side, (column + 1) * side - 1, (row + 1) * side - 1], fill=colour)
    return image


def line_board(lines, width=400, height=400, background=(220, 179, 92)):
    image = Image.new("RGB", (width, height), background)
    draw = ImageDraw.Draw(image)
    gap = (height - 40) / (lines - 1)
    for index in range(lines):
        y = round(20 + index * gap)
        draw.line([(20, y), (width - 20, y)], fill=(0, 0, 0), width=2)
    return image


def grid_of_boxes(columns, rows, marks):
    """White boxes with black borders; `marks[(column, row)]` draws inside a box."""
    image = Image.new("RGB", (100 * columns + 20, 100 * rows + 20), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    for column in range(columns):
        for row in range(rows):
            left = 10 + column * 100
            top = 10 + row * 100
            draw.rectangle([left, top, left + 90, top + 90], outline=(0, 0, 0), width=4)
            if (column, row) in marks:
                marks[(column, row)](draw, left, top)
    return image


def three_dots(draw, left, top):
    for index in range(3):
        x = left + 20 + index * 25
        draw.ellipse([x, top + 35, x + 14, top + 49], fill=(0, 0, 0))


def four_strokes(draw, left, top):
    for index in range(4):
        x = left + 20 + index * 15
        draw.line([(x, top + 20), (x, top + 70)], fill=(0, 0, 0), width=4)


def test_chess_grid_counts_rows():
    answer = make_harness().answer(chess_board(), "How many rows are there on this board?")
    assert (answer.pipeline, answer.value) == ("chess_grid", 8)
    assert answer.trace[0].tool == "select_counter"


def test_go_grid_counts_lines_and_sudoku_counts_cells():
    harness = make_harness()
    answer = harness.answer(line_board(9), "How many horizontal lines are there on this board?")
    assert (answer.pipeline, answer.value) == ("go_grid", 9)
    answer = harness.answer(line_board(10, background=(255, 255, 255)), "How many rows are there on this puzzle?")
    assert (answer.pipeline, answer.value) == ("sudoku_grid", 9)


def test_dice_counts_circles_and_tally_counts_strokes_in_the_named_cell():
    harness = make_harness()
    image = grid_of_boxes(3, 2, {(1, 0): three_dots, (2, 1): four_strokes})
    assert harness.answer(image, "How many circles are there in cell B1?").value == 3
    assert harness.answer(image, "How many lines are there in cell C2?").value == 4
    assert harness.answer(image, "How many circles are there in cell A1?").value == 0


def test_cell_that_the_grid_does_not_have_gives_none():
    image = grid_of_boxes(2, 2, {})
    answer = make_harness().answer(image, "How many circles are there in cell E5?")
    assert (answer.pipeline, answer.value) == ("dice", None)


def test_flag_stripes_counts_bands_of_the_cloth():
    image = Image.new("RGB", (400, 300), (198, 198, 198))
    draw = ImageDraw.Draw(image)
    colours = [(200, 0, 0), (255, 255, 255), (0, 0, 160), (255, 255, 255), (200, 0, 0)]
    for index, colour in enumerate(colours):
        draw.rectangle([60, 50 + index * 40, 360, 50 + (index + 1) * 40 - 1], fill=colour)
    answer = make_harness().answer(image, "How many stripes are there in this flag?")
    assert (answer.pipeline, answer.value) == ("flag_stripes", 5)


def test_flag_without_cloth_gives_none():
    image = Image.new("RGB", (400, 300), (198, 198, 198))
    answer = make_harness().answer(image, "How many stars are there in this flag?")
    assert (answer.pipeline, answer.value) == ("flag_stars", None)


def full_mask(size, box):
    mask = np.zeros(size, dtype=bool)
    top, bottom, left, right = box
    mask[top:bottom, left:right] = True
    return mask


def test_shoe_logo_counts_slanted_white_stripes_on_the_left_shoe():
    image = Image.new("RGB", (400, 200), (30, 30, 30))
    draw = ImageDraw.Draw(image)
    for index in range(3):
        x = 40 + index * 30
        draw.line([(x, 150), (x + 40, 60)], fill=(250, 250, 250), width=8)
    regions = Regions()
    left_shoe = {"score": 0.9, "box": [0.0, 0.0, 0.5, 1.0], "mask": full_mask((200, 400), (20, 190, 10, 190))}
    right_shoe = {"score": 0.95, "box": [0.5, 0.0, 1.0, 1.0], "mask": full_mask((200, 400), (20, 190, 210, 390))}
    regions.by_concept["shoe"] = [right_shoe, left_shoe]
    answer = make_harness(regions).answer(
        image, "How many visible white stripes are there in the logo on the left shoe?")
    assert (answer.pipeline, answer.value) == ("shoe_logos", 3)


def test_logo_without_a_region_gives_none():
    answer = make_harness().answer(Image.new("RGB", (100, 100)), "How many prongs are there in the logo of this car?")
    assert (answer.pipeline, answer.value) == ("car_logos", None)


def test_region_crop_matches_the_cache_form():
    mask = full_mask((50, 60), (10, 20, 5, 30))
    cropped = region_crop({"score": 0.5, "box": [0, 0, 1, 1], "mask": mask})
    assert cropped["box"] == (10, 20, 5, 30)
    assert cropped["mask"].shape == (10, 25) and cropped["mask"].all()
    assert region_crop({"score": 0.5, "box": [0, 0, 1, 1], "mask": np.zeros((5, 5), dtype=bool)}) is None


def test_question_without_a_counter_gives_pipeline_none():
    answer = make_harness().answer(Image.new("RGB", (10, 10)), "How many clouds are there?")
    assert (answer.intent, answer.pipeline, answer.value) == ("quantity", NO_COUNTER, None)
    assert [step.tool for step in answer.trace] == ["select_counter"]
