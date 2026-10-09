"""Tests of the option-scoring intent classifier, with a fake language model (no download)."""

import math
import subprocess
import sys

import pytest

from intent_harness import Harness
from intent_harness.types import IntentInfo, Result
from intent_harness_classifiers import (
    DEFAULT_INSTRUCTIONS,
    OptionScoringClassifier,
    build_prompt,
    confidence_from_probabilities,
    softmax,
)
from intent_harness_classifiers import option_scoring


class FakeLanguageModel:
    """Gives each option a fixed log score and records every call."""

    def __init__(self, scores):
        self.scores = scores
        self.calls = []

    def option_log_probabilities(self, prompt, options):
        self.calls.append((prompt, list(options)))
        result = {}
        for option in options:
            result[option] = self.scores.get(option, -50.0)
        return result


class KeyIntent:
    """An intent that returns its own key."""

    required_tools = ()

    def __init__(self, key, description):
        self.key = key
        self.description = description

    def run(self, image, question, tools):
        return Result(value=self.key)


THREE = [
    IntentInfo("quantity", "Questions about the number of objects."),
    IntentInfo("structural", "Questions about shape and size."),
    IntentInfo("other", "Questions that fit none of the others."),
]


def test_options_are_the_given_intents_in_order():
    model = FakeLanguageModel({"structural": -0.1})
    classifier = OptionScoringClassifier(model)
    choice = classifier.classify("Are the lines equal?", THREE)
    assert model.calls[0][1] == ["quantity", "structural", "other"]
    assert choice.key == "structural"
    assert list(choice.probabilities) == ["quantity", "structural", "other"]


def test_a_new_intent_adds_an_option():
    model = FakeLanguageModel({"color": -0.01})
    classifier = OptionScoringClassifier(model)
    four = THREE + [IntentInfo("color", "Questions about colour.")]
    choice = classifier.classify("What colour is it?", four)
    assert model.calls[0][1][-1] == "color"
    assert choice.key == "color"


def test_prompt_shape():
    criteria = {"quantity": "Count things.", "other": "Anything else."}
    prompt = build_prompt("How many legs?", criteria)
    expected = (
        'Text: "How many legs?"\n\n'
        f"Question: {DEFAULT_INSTRUCTIONS}\n\n"
        "Options:\n- quantity: Count things.\n- other: Anything else.\n\n"
        "Answer with the option name only."
    )
    assert prompt == expected


def test_softmax_and_confidence():
    probabilities = softmax({"a": 0.0, "b": math.log(3.0)})
    assert probabilities["a"] == pytest.approx(0.25)
    assert probabilities["b"] == pytest.approx(0.75)
    assert sum(probabilities.values()) == pytest.approx(1.0)
    assert confidence_from_probabilities(probabilities) == pytest.approx(0.5)
    assert confidence_from_probabilities({"a": 0.5, "b": 0.5}) == pytest.approx(0.0)


def test_softmax_with_very_low_scores():
    probabilities = softmax({"a": -1000.0, "b": -1001.0})
    assert sum(probabilities.values()) == pytest.approx(1.0)
    assert probabilities["a"] > probabilities["b"]


def test_one_intent_gives_confidence_one():
    classifier = OptionScoringClassifier(FakeLanguageModel({}))
    choice = classifier.classify("anything", [THREE[0]])
    assert choice.key == "quantity"
    assert choice.probabilities == {"quantity": 1.0}
    assert choice.confidence == 1.0


def test_no_intent_raises():
    classifier = OptionScoringClassifier(FakeLanguageModel({}))
    with pytest.raises(ValueError):
        classifier.classify("anything", [])


def test_register_without_model_raises():
    harness = Harness()
    with pytest.raises(ValueError, match="model"):
        option_scoring.register(harness)


def test_plugin_routes_harness_answer():
    harness = Harness()
    harness.register_intent(KeyIntent("quantity", "Counts."))
    harness.register_intent(KeyIntent("structural", "Shapes."))
    model = FakeLanguageModel({"quantity": -0.2, "structural": -3.0})
    harness.load_classifier("intent_harness_classifiers.option_scoring", language_model=model)
    answer = harness.answer(None, "How many legs?")
    assert answer.intent == "quantity"
    assert answer.value == "quantity"
    assert sum(answer.probabilities.values()) == pytest.approx(1.0)
    assert 0.0 <= answer.confidence <= 1.0


def test_import_does_not_load_torch():
    code = (
        "import sys\n"
        "import intent_harness_classifiers\n"
        "print('torch' in sys.modules, 'transformers' in sys.modules)\n"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    assert result.stdout.strip() == "False False"
