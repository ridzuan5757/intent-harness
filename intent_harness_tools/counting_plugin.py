"""Plugin module: registers the counting image operations by name.

Load it with `harness.load_tools("intent_harness_tools.counting_plugin")`. Each operation is
registered under its function name. This module only calls `harness.register_tool`.
"""

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
from intent_harness_tools.lines import fit_line
from intent_harness_tools.shapes import group_shapes

TOOLS = {
    "luminance": luminance,
    "colour_runs": colour_runs,
    "line_profile": line_profile,
    "cluster": cluster,
    "box_cells": box_cells,
    "template_distance": template_distance,
    "solidity": solidity,
    "radial_peaks": radial_peaks,
    "palette_labels": palette_labels,
    "nearest_template": nearest_template,
    "group_shapes": group_shapes,
    "fit_line": fit_line,
}

TOOL_NAMES = tuple(TOOLS)


def register(harness, **options):
    """Register the counting image operations, and group_shapes and fit_line, under their names.

    A tool that is already registered under the same name (for example by the measurement
    plugin) is not registered again.
    """
    for name, function in TOOLS.items():
        if name in harness.registry.tools:
            continue
        harness.register_tool(function, name=name)
