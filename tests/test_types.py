import dataclasses

import pytest

from intent_harness import Answer, Choice, Result, Step


def test_types_are_frozen():
    choice = Choice(key="a", probabilities={"a": 1.0}, confidence=1.0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        choice.key = "b"


def test_result_pipeline_defaults_to_none():
    assert Result(value=4).pipeline is None


def test_step_and_answer_fields():
    step = Step(tool="t", inputs={"x": 1}, output=2)
    answer = Answer(intent="i", pipeline="p", value=2, confidence=0.5,
                    probabilities={"i": 1.0}, trace=(step,))
    assert step.ok and step.error is None
    assert answer.trace[0].output == 2
