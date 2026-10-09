"""Plugin module: registers the SAM 3 tools by name.

Load it with `harness.load_tools("intent_harness_tools.sam3_plugin")`. The model loads at the
first call, not at registration.
"""

from intent_harness_tools.sam3 import keep_smaller_regions, remove_duplicate_regions, segment_concept

TOOL_NAMES = ("segment_concept", "keep_smaller_regions", "remove_duplicate_regions")


def register(harness, **options):
    harness.register_tool(segment_concept, name="segment_concept")
    harness.register_tool(keep_smaller_regions, name="keep_smaller_regions")
    harness.register_tool(remove_duplicate_regions, name="remove_duplicate_regions")
