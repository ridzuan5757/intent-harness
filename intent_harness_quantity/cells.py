"""Counters for the patterned-grid sub-topics: dice and tally.

The rules and constants are those of the experiment (grounded-count-harness, harness/counting.py,
spec 004), unchanged. Each counter returns the count, or None when the grid or the named cell is
not found.
"""

from intent_harness_quantity.targets import read_target


class CellCounter:
    """Find the cell named in the question with box_cells; inside it, count dark shapes: circles
    only (solidity at least 0.85) for dice, every shape for tally."""

    required_tools = ("box_cells", "luminance", "group_shapes", "solidity")

    def __init__(self, name):
        if name not in ("dice", "tally"):
            raise ValueError(f"No cell counter for '{name}'.")
        self.name = name

    def count(self, image, question, tools):
        rule, target, cell = read_target(question)
        found = tools["box_cells"](image)
        complete = len(found["cells"]) == found["n_cols"] * found["n_rows"] and len(found["cells"]) > 0
        if not complete:
            return None
        box = found["cells"].get(cell)
        if box is None:
            return None
        top, bottom, left, right = box
        ink = tools["luminance"](image)[top:bottom, left:right] < 128
        shapes = tools["group_shapes"](ink, min_pixels=5)
        if self.name == "tally":
            return len(shapes)
        circles = 0
        for shape in shapes:
            if round(tools["solidity"](shape), 3) >= 0.85:
                circles += 1
        return circles
