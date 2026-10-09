"""Plugin module: registers the illusion pixel-rule tool and the structural intent.

Load the measurement tools first:

    harness.load_tools("intent_harness_tools.measurement_plugin")
    harness.load_intents("intent_harness_structural.plugin")
"""

from intent_harness_structural.intent import PIXEL_RULE_TOOL, StructuralIntent
from intent_harness_structural.pixel_rules import classify_image


def register(harness, **options):
    """Register the tool `illusion_pixel_rules` and the intent `structural`."""
    harness.register_tool(classify_image, name=PIXEL_RULE_TOOL)
    harness.register_intent(StructuralIntent())
