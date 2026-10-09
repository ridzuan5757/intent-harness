"""The option-scoring intent classifier and its plugin entry point.

The classifier asks a language model how likely each loaded intent key is as its reply, turns
the scores into probabilities and chooses the most probable key. It has no label list of its
own: the options are the intents that the harness passes to `classify`.

Load it in code:

    harness.load_classifier("intent_harness_classifiers.option_scoring", model="Qwen/Qwen3-4B")

or from a .env file with INTENT_HARNESS_CLASSIFIER and INTENT_HARNESS_CLASSIFIER_MODEL.
"""

from collections.abc import Sequence
from typing import Any, Protocol

from intent_harness.types import Choice, IntentInfo
from intent_harness_classifiers.scoring import (
    DEFAULT_INSTRUCTIONS,
    build_prompt,
    confidence_from_probabilities,
    softmax,
)


class ScoresOptions(Protocol):
    """What the classifier needs from a language model."""

    def option_log_probabilities(self, prompt: str, options: Sequence[str]) -> dict[str, float]: ...


class OptionScoringClassifier:
    """Chooses among the given intents by option scoring. Nothing is generated or parsed."""

    def __init__(self, language_model: ScoresOptions, instructions: str = DEFAULT_INSTRUCTIONS) -> None:
        self.language_model = language_model
        self.instructions = instructions
        self.last_log_scores: dict[str, float] = {}

    def classify(self, question: str, intents: Sequence[IntentInfo]) -> Choice:
        criteria = {}
        for intent in intents:
            criteria[intent.key] = intent.description
        options = list(criteria)
        if not options:
            raise ValueError("No intent to choose from.")

        prompt = build_prompt(question, criteria, self.instructions)
        log_scores = self.language_model.option_log_probabilities(prompt, options)
        self.last_log_scores = dict(log_scores)
        probabilities = softmax(log_scores)
        best = max(probabilities, key=probabilities.get)
        return Choice(key=best, probabilities=probabilities,
                      confidence=confidence_from_probabilities(probabilities))


def register(harness: Any, model: str | None = None, language_model: ScoresOptions | None = None,
             device: str = "mps", dtype: str = "bfloat16",
             instructions: str = DEFAULT_INSTRUCTIONS) -> OptionScoringClassifier:
    """Set the option-scoring classifier on `harness`.

    Give `model` (a HuggingFace id or a local path in the local cache) to load a causal
    language model, or `language_model` (any object with `option_log_probabilities`).
    """
    if language_model is None:
        if not model:
            raise ValueError(
                "The option-scoring classifier needs the option 'model' "
                "(for example model='Qwen/Qwen3-4B'), or 'language_model'."
            )
        from intent_harness_classifiers.language_model import LanguageModel

        language_model = LanguageModel(model, device=device, dtype=dtype)
    classifier = OptionScoringClassifier(language_model, instructions=instructions)
    harness.register_classifier(classifier)
    return classifier
