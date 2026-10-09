"""Measurement tools for drawn figures.

Plain functions with normal arguments and return values. The package does not import any other
package of this repository: it knows nothing about tool names, traces, registration or intents.

The eight measurement tools:

1. colour_mask          the pixels that are dark, red or grey
2. group_shapes         split a mask into separate shapes, largest first
3. find_runs            long horizontal or vertical runs of a mask, merged into segments
4. direction_filter     keep only strokes along one direction
5. equivalent_diameter  the diameter of a disc with the same area as a shape
6. fit_line             the straight line through a shape: centre, direction, angle, end points
7. point_line_distance  the distance from a point to an extended line
8. decide               "Yes" when a quantity is inside a tolerance, else "No"

The drawing helpers make test shapes with a known answer: draw_segments, draw_discs and
segment_at_angle.
"""

from intent_harness_tools.decision import decide
from intent_harness_tools.drawing import SUPERSAMPLE, draw_discs, draw_segments, segment_at_angle
from intent_harness_tools.lines import fit_line, point_line_distance
from intent_harness_tools.masks import COLOUR_RULES, colour_mask
from intent_harness_tools.segments import direction_filter, find_runs
from intent_harness_tools.shapes import equivalent_diameter, group_shapes

__all__ = [
    "COLOUR_RULES",
    "SUPERSAMPLE",
    "colour_mask",
    "decide",
    "direction_filter",
    "draw_discs",
    "draw_segments",
    "equivalent_diameter",
    "find_runs",
    "fit_line",
    "group_shapes",
    "point_line_distance",
    "segment_at_angle",
]
