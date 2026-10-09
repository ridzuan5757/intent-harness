"""Intent classifiers that plug into the harness.

`option_scoring` scores each loaded intent key as a language model's reply. Importing this
package does not import torch or transformers.
"""

from intent_harness_classifiers.option_scoring import OptionScoringClassifier
from intent_harness_classifiers.scoring import (
    DEFAULT_INSTRUCTIONS,
    build_prompt,
    confidence_from_probabilities,
    softmax,
)

__all__ = [
    "DEFAULT_INSTRUCTIONS",
    "OptionScoringClassifier",
    "build_prompt",
    "confidence_from_probabilities",
    "softmax",
]
