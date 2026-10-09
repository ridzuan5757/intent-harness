"""Plugin module: registers the GroundingDINO box tool by name.

Load it with `harness.load_tools("intent_harness_tools.grounding_dino_plugin")`. The model loads
at the first call, not at registration.
"""

from intent_harness_tools.grounding_dino import best_box

TOOL_NAMES = ("best_box",)


def register(harness, **options):
    harness.register_tool(best_box, name="best_box")
