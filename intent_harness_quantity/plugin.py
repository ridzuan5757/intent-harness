"""Plugin module: registers the quantity intent with its legs pipeline.

Load the tools first:

    harness.load_tools("intent_harness_tools.grounding_dino_plugin",
                       "intent_harness_tools.sam3_plugin")
    harness.load_intents("intent_harness_quantity.plugin")
"""

from intent_harness_quantity.intent import QuantityIntent
from intent_harness_quantity.legs import LegsPipeline


def register(harness, **options):
    harness.register_intent(QuantityIntent([LegsPipeline()]))
