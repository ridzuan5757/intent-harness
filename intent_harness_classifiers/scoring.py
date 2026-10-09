"""Pure functions of option scoring: the prompt, the probabilities and the confidence.

The prompt shape follows the TypeSafe Choice primitive: the text to classify, the
instructions, the options with their descriptions, and a one-line reply rule.
"""

import math
from collections.abc import Mapping

DEFAULT_INSTRUCTIONS = "Which visual pattern is this question or description about?"


def build_prompt(text: str, criteria: Mapping[str, str], instructions: str = DEFAULT_INSTRUCTIONS) -> str:
    """The prompt for one text. `criteria` maps each option key to its description.

    The text is labelled "Text", not "State": "state" can be one of the options, and the label
    "State:" moved the model toward that option in the experiment.
    """
    lines = [f"Text: \"{text}\"", "", f"Question: {instructions}", "", "Options:"]
    for option in criteria:
        lines.append(f"- {option}: {criteria[option]}")
    lines.append("")
    lines.append("Answer with the option name only.")
    return "\n".join(lines)


def softmax(log_scores: Mapping[str, float]) -> dict[str, float]:
    """Turn {option: log score} into {option: probability}. The highest score is subtracted
    first, so that large negative scores do not underflow."""
    highest = max(log_scores.values())
    weights = {}
    total = 0.0
    for option, value in log_scores.items():
        weights[option] = math.exp(value - highest)
        total += weights[option]
    probabilities = {}
    for option in log_scores:
        probabilities[option] = weights[option] / total
    return probabilities


def confidence_from_probabilities(probabilities: Mapping[str, float]) -> float:
    """(K * max - 1) / (K - 1): 1.0 when all probability is on one option, 0.0 when it is
    spread evenly. With one option the confidence is 1.0."""
    values = list(probabilities.values())
    k = len(values)
    if k < 2:
        return 1.0
    return (k * max(values) - 1.0) / (k - 1.0)
