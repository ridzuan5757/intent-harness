"""Plugin module: registers the counter selector and the quantity intent with its thirteen
counting pipelines.

Load the tools first:

    harness.load_tools("intent_harness_tools.counting_plugin",
                       "intent_harness_tools.grounding_dino_plugin",
                       "intent_harness_tools.sam3_plugin")
    harness.load_intents("intent_harness_quantity.plugin")

The models load at the first call of a model tool, not here.
"""

from intent_harness_quantity.intent import QuantityIntent
from intent_harness_quantity.pipelines import all_pipelines
from intent_harness_quantity.selector import select_counter

SELECTOR_TOOL = "select_counter"


def register(harness, **options):
    """Register the tool `select_counter` and the intent `quantity`."""
    harness.register_tool(select_counter, name=SELECTOR_TOOL)
    harness.register_intent(QuantityIntent(all_pipelines(), selector=SELECTOR_TOOL))
