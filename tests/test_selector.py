"""The counter selector: one question per rule, the two image checks, and no match."""

import pytest

from intent_harness_quantity.selector import SELECTOR_RULES, is_tall, select_counter


class Size:
    def __init__(self, width, height):
        self.size = (width, height)


SQUARE = Size(384, 384)
TALL = Size(384, 432)


@pytest.mark.parametrize("question, image, counter", [
    ("How many legs does this animal have?", SQUARE, "legs"),
    ("Count the legs of this animal.", SQUARE, "legs"),
    ("How many legs do this animal have?", SQUARE, "legs"),
    ("How many circles are there in cell C3?", SQUARE, "dice"),
    ("Count the lines in cell E5.", SQUARE, "tally"),
    ("How many chess pieces are there on this board?", SQUARE, "chess_pieces"),
    ("How many King pieces are there on this board?", SQUARE, "chess_pieces"),
    ("Count the Pawn pieces on this board.", SQUARE, "chess_pieces"),
    ("How many xiangqi pieces are there on this board?", TALL, "xiangqi_pieces"),
    ("How many General pieces are there on this board?", TALL, "xiangqi_pieces"),
    ("Count the Cannon pieces on this board.", TALL, "xiangqi_pieces"),
    ("How many Knight pieces are there on this board?", SQUARE, "chess_pieces"),
    ("How many Knight pieces are there on this board?", TALL, "xiangqi_pieces"),
    ("How many horizontal lines are there on this board?", SQUARE, "go_grid"),
    ("Count the vertical lines on this board.", TALL, "xiangqi_grid"),
    ("How many rows are there on this puzzle?", SQUARE, "sudoku_grid"),
    ("Count the columns on this board.", SQUARE, "chess_grid"),
    ("How many prongs are there in the logo of this car?", SQUARE, "car_logos"),
    ("How many points of the star are there on the logo of this car?", SQUARE, "car_logos"),
    ("How many visible white stripes are there in the logo on the left shoe?", SQUARE, "shoe_logos"),
    ("How many stars are there in this flag?", SQUARE, "flag_stars"),
    ("Count the stripes in this flag.", SQUARE, "flag_stripes"),
])
def test_rules_choose_the_counter(question, image, counter):
    assert select_counter(image, question) == counter


def test_no_rule_gives_none():
    assert select_counter(SQUARE, "What colour is the sky?") is None


def test_tall_limit():
    assert is_tall(TALL)
    assert not is_tall(SQUARE)
    assert not is_tall(Size(384, 400))     # 1.04: below the 1.06 limit


def test_rules_are_numbered_in_order():
    numbers = [rule[0] for rule in SELECTOR_RULES]
    assert numbers == list(range(1, len(SELECTOR_RULES) + 1))
