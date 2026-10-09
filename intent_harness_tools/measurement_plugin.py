"""Plugin module: registers the eight measurement tools in a harness.

Load it with `harness.load_tools("intent_harness_tools.measurement_plugin")`. Each tool is
registered under its function name. The harness wraps each function, so every call inside
`Harness.answer` is recorded as one trace step.

This module only calls `harness.register_tool`. It does not import the core.
"""

from intent_harness_tools.decision import decide
from intent_harness_tools.lines import fit_line, point_line_distance
from intent_harness_tools.masks import colour_mask
from intent_harness_tools.segments import direction_filter, find_runs
from intent_harness_tools.shapes import equivalent_diameter, group_shapes

TOOLS = {
    "colour_mask": colour_mask,
    "group_shapes": group_shapes,
    "find_runs": find_runs,
    "direction_filter": direction_filter,
    "equivalent_diameter": equivalent_diameter,
    "fit_line": fit_line,
    "point_line_distance": point_line_distance,
    "decide": decide,
}

TOOL_NAMES = tuple(TOOLS)


def register(harness, **options):
    """Register the eight measurement tools under their function names."""
    for name, function in TOOLS.items():
        harness.register_tool(function, name=name)
