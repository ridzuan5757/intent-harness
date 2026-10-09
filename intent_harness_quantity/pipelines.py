"""The thirteen counting pipelines of the quantity intent, in one list."""

from intent_harness_quantity.boards import (
    ChessGridCounter,
    ChessPiecesCounter,
    LineGridCounter,
    XiangqiPiecesCounter,
)
from intent_harness_quantity.cells import CellCounter
from intent_harness_quantity.flags import FlagStarsCounter, FlagStripesCounter
from intent_harness_quantity.legs import LegsPipeline
from intent_harness_quantity.logos import CarLogoCounter, ShoeLogoCounter

PIPELINE_NAMES = (
    "legs",
    "chess_grid", "sudoku_grid", "xiangqi_grid", "go_grid",
    "chess_pieces", "xiangqi_pieces",
    "flag_stars", "flag_stripes",
    "dice", "tally",
    "car_logos", "shoe_logos",
)


def all_pipelines():
    """A new instance of every counting pipeline, in PIPELINE_NAMES order."""
    return [
        LegsPipeline(),
        ChessGridCounter(), LineGridCounter("sudoku_grid"), LineGridCounter("xiangqi_grid"),
        LineGridCounter("go_grid"),
        ChessPiecesCounter(), XiangqiPiecesCounter(),
        FlagStarsCounter(), FlagStripesCounter(),
        CellCounter("dice"), CellCounter("tally"),
        CarLogoCounter(), ShoeLogoCounter(),
    ]
