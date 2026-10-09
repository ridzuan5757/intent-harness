"""The quantity intent: questions that ask how many of something an image shows.

The intent holds thirteen counting pipelines by name: `legs` and the twelve VLMBias counting
sub-topics. The registered tool `select_counter` chooses one from the question. The count is
computed in code from the image; no language model writes it.
"""

from intent_harness_quantity.intent import NO_COUNTER, QuantityIntent
from intent_harness_quantity.legs import LegsPipeline
from intent_harness_quantity.pipelines import PIPELINE_NAMES, all_pipelines
from intent_harness_quantity.selector import select_counter

__all__ = ["NO_COUNTER", "PIPELINE_NAMES", "LegsPipeline", "QuantityIntent", "all_pipelines",
           "select_counter"]
