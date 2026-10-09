"""The structural intent: questions about a drawn optical illusion figure."""

from intent_harness.types import Result

from intent_harness_structural.pipelines import PIPELINES
from intent_harness_structural.tolerances import TOLERANCES

PIXEL_RULE_TOOL = "illusion_pixel_rules"

MEASUREMENT_TOOLS = (
    "colour_mask",
    "group_shapes",
    "find_runs",
    "direction_filter",
    "equivalent_diameter",
    "fit_line",
    "point_line_distance",
    "decide",
)

DESCRIPTION = (
    "Questions about the structure of a drawn figure: whether two lines are equal in length, "
    "whether two circles are equal in size, whether two line segments are aligned, or whether "
    "two lines are parallel."
)


class StructuralIntent:
    """Names the illusion with the pixel rules, measures the figure, and decides.

    1. `illusion_pixel_rules` names the illusion drawn in the image, or `none`.
    2. The pipeline of that illusion measures the figure with the measurement tools.
    3. `decide` answers "Yes" when the quantity is inside the illusion's frozen tolerance,
       else "No".

    The value is None when the illusion is `none` or when the pipeline cannot find its shapes.
    The question text is not read: the illusion named from the image fixes the question.
    """

    key = "structural"
    description = DESCRIPTION
    required_tools = (PIXEL_RULE_TOOL,) + MEASUREMENT_TOOLS

    def run(self, image, question, tools):
        illusion = tools[PIXEL_RULE_TOOL](image)
        if illusion not in PIPELINES:
            return Result(value=None, pipeline="none")

        measurement = PIPELINES[illusion](image, tools)
        if not measurement.found:
            return Result(value=None, pipeline=illusion)

        answer = tools["decide"](measurement.quantity, TOLERANCES[illusion])
        return Result(value=answer, pipeline=illusion)
