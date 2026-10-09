"""The quantity intent: questions that ask how many of something an image shows.

The intent holds counting pipelines by name. This version has one pipeline, `legs`. The count is
computed in code from the regions the localizer tools return; no language model writes it.
"""

from intent_harness_quantity.intent import QuantityIntent
from intent_harness_quantity.legs import LegsPipeline

__all__ = ["LegsPipeline", "QuantityIntent"]
