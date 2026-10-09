"""Counters for the board sub-topics: grids and pieces.

The rules and constants are those of the experiment (grounded-count-harness, harness/counting.py,
spec 004), unchanged. Each counter returns the count, or None when its target is not found (the
experiment wrote -1). Image operations are called by name from the tools the intent receives.
"""

import numpy as np

from intent_harness_quantity.references import (
    chess_feature,
    chess_squares,
    load_board_references,
    xiangqi_crop,
)
from intent_harness_quantity.targets import read_target


class ChessGridCounter:
    """Rows or columns of a chess board: colour bands along a line just off the centre. The two
    square colours are the two non-white band colours with the largest total length; neighbouring
    bands of one square colour merge (a piece drawn on a square splits its band)."""

    name = "chess_grid"
    required_tools = ("colour_runs",)

    def count(self, image, question, tools):
        rule, target, detail = read_target(question)
        rgb = np.asarray(image.convert("RGB"))
        height, width = rgb.shape[0], rgb.shape[1]
        if target == "rows":
            line = rgb[:, width // 2 + width // 37]
        elif target == "columns":
            line = rgb[height // 2 + height // 37, :]
        else:
            return None
        runs = tools["colour_runs"](line, min_length=max(3, len(line) // 100))
        if len(runs) == 0:
            return None

        keys = []
        totals = {}
        for run in runs:
            if bool((run["colour"] >= 235).all()):
                keys.append(None)
                continue
            key = tuple(int(value) for value in np.round(run["colour"] / 12))
            keys.append(key)
            totals[key] = totals.get(key, 0) + run["length"]
        ranked = sorted(totals, key=lambda key: -totals[key])
        square_colours = ranked[:2]
        if len(square_colours) != 2:
            return None

        merged = []
        for key in keys:
            if key in square_colours and (len(merged) == 0 or merged[-1] != key):
                merged.append(key)
        if len(merged) == 0:
            return None
        return len(merged)


class LineGridCounter:
    """Lines of a go, sudoku or xiangqi board with the line profile; sudoku rows and columns are
    the lines minus one."""

    required_tools = ("line_profile",)

    def __init__(self, name):
        if name not in ("go_grid", "sudoku_grid", "xiangqi_grid"):
            raise ValueError(f"No line-grid counter for '{name}'.")
        self.name = name

    def count(self, image, question, tools):
        rule, target, detail = read_target(question)
        if target in ("rows", "horizontal lines"):
            axis = "rows"
        elif target in ("columns", "vertical lines"):
            axis = "columns"
        else:
            return None
        found = tools["line_profile"](image, axis)
        if found["lines"] <= 0:
            return None
        if self.name == "sudoku_grid":
            return found["lines"] - 1
        return found["lines"]


def _piece_answer(target, detail, kinds):
    """All pieces, or the pieces of the kind `detail` (as the experiment: any other target counts
    the kind `detail`)."""
    if target == "all pieces":
        return len(kinds)
    found = 0
    for kind in kinds:
        if kind == detail:
            found += 1
    return found


class ChessPiecesCounter:
    """Occupied squares (more than 5% of pixels differ from both square colours); each piece's
    kind is the nearest reference crop."""

    name = "chess_pieces"
    required_tools = ("nearest_template",)

    def __init__(self, references=None):
        self.references = references

    def count(self, image, question, tools):
        rule, target, detail = read_target(question)
        references = self.references or load_board_references()
        rgb = np.asarray(image.convert("RGB"))
        kinds = []
        for row, column, square in chess_squares(rgb):
            feature, share = chess_feature(square)
            if share < 0.05:
                continue
            kind, distance = tools["nearest_template"](feature, references["chess"]["references"])
            kinds.append(kind)
        if len(kinds) == 0:
            return None
        return _piece_answer(target, detail, kinds)


class XiangqiPiecesCounter:
    """Each of the 90 intersections (from the unedited board, scaled to the image) is matched
    against piece and empty-intersection references; the nearest decides empty or which kind."""

    name = "xiangqi_pieces"
    required_tools = ("nearest_template",)

    def __init__(self, references=None):
        self.references = references

    def count(self, image, question, tools):
        rule, target, detail = read_target(question)
        references = self.references or load_board_references()
        rgb = np.asarray(image.convert("RGB"))
        width = rgb.shape[1]
        grid = references["xiangqi"]
        size = grid["size"] * width
        kinds = []
        for row_fraction in grid["rows"]:
            for column_fraction in grid["columns"]:
                feature = xiangqi_crop(rgb, row_fraction * width, column_fraction * width, size)
                kind, distance = tools["nearest_template"](feature, grid["references"])
                if kind != "empty":
                    kinds.append(kind)
        if len(kinds) == 0:
            return None
        return _piece_answer(target, detail, kinds)
