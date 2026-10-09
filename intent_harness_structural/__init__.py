"""The structural intent: answer the VLMBias question for an optical illusion figure.

The pixel rules name the illusion drawn in the image. That illusion's pipeline measures the
figure with the measurement tools, which it gets by name from the harness. The decision uses
the illusion's frozen tolerance. Load it with the module `intent_harness_structural.plugin`.
"""

from intent_harness_structural.illusions import ILLUSION_KEYS, ILLUSIONS, PAPER_KEYS
from intent_harness_structural.intent import MEASUREMENT_TOOLS, PIXEL_RULE_TOOL, StructuralIntent
from intent_harness_structural.pipelines import PIPELINES, Measurement
from intent_harness_structural.pixel_rules import classify_image, pixel_features, rules_hash
from intent_harness_structural.tolerances import TOLERANCES

__all__ = [
    "ILLUSIONS",
    "ILLUSION_KEYS",
    "MEASUREMENT_TOOLS",
    "Measurement",
    "PAPER_KEYS",
    "PIPELINES",
    "PIXEL_RULE_TOOL",
    "StructuralIntent",
    "TOLERANCES",
    "classify_image",
    "pixel_features",
    "rules_hash",
]
